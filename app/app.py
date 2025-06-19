import logging
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from pydantic import BaseModel
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
import httpx
import traceback
import os
import shutil
from typing import List
from datetime import datetime
from database.database import add_user, verify_user, create_table, create_connection, get_user_info 
import zipfile
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.error")

app = FastAPI()
create_table() # user credentials


class UserCredentials(BaseModel):
    """for user credential storage ensures that it is in correct shape (username, password)"""
    username: str
    password: str

class UserRegistration(UserCredentials):
    """For user registration, ensure shape (open API key)"""
    openai_key: str


class QueryRequest(BaseModel):
    """For query type check from streamlit to agent network (query)"""
    query: str

@app.post("/ask")
async def ask(request: Request):
    """Prompt to the specific agent network of each user"""
    user_port = request.headers.get("X-User-Port")  # get the user port
    if not user_port:
        raise HTTPException(status_code=400, detail="User port not provided") 

    body = await request.json() # get json
    prompt = body.get("prompt")
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    query_request = {"query": prompt}
    agent_url = f"http://host.docker.internal:{user_port}/supervisor/ask" # specific container

    try:
        async def stream_response():
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("POST", agent_url, json=query_request) as response:
                    if response.status_code != 200:
                        raise HTTPException(
                            status_code=response.status_code,
                            detail="Error from supervisor service"
                        )
                    async for chunk in response.aiter_text(): # stream the response in chunks (type-writer)
                        if chunk:
                            yield chunk
    
        return StreamingResponse(stream_response(), media_type="application/json")
    
    except Exception as e:
        logger.error(f"Streaming failed: {e}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Streaming failed: {str(e)}")



@app.post("/update-memory")
async def update_memory(request: Request):
    user_port = request.headers.get("X-User-Port") # specific user port to route to correct agent
    if not user_port:
        raise HTTPException(status_code=400, detail="User port not provided")
    try:
        async with httpx.AsyncClient(timeout=120.0) as client: # long timeout due to multiple experts/supervisor who have to reflect
            response = await client.post(f"http://host.docker.internal:{user_port}/supervisor/update-memory")
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Error from supervisor service during memory update"
                )
            
            # Parse the response from HB_Agent
            response_data = response.json()
            if "warning" in response_data.get("message", "").lower(): # if no interaction available
                return JSONResponse(
                    content={
                        "status": "warning",
                        "message": "Please interact with the agent first before updating memory",
                        "timestamp": datetime.now().isoformat()
                    }
                )
            
            return JSONResponse(
                content={
                    "status": "success",
                    "message": "Memory updated successfully",
                    "timestamp": datetime.now().isoformat()
                }
            ) # otherwise succesfull
    except Exception as e:
        logger.error(f"Memory update failed: {e}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Memory update failed: {str(e)}")

@app.post("/process-pdf/{expert_name}")
async def process_pdf(expert_name: str, request: Request, files: List[UploadFile] = File(...)):
    user_port = request.headers.get("X-User-Port")
    if not user_port:
        raise HTTPException(status_code=400, detail="User port not provided")
    print(f"this is the user port {user_port}") 
    try:
        temp_dir = "temp_pdfs"
        os.makedirs(temp_dir, exist_ok=True) # temporary storage for pdfs
        # Save uploaded files
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
        
        async with httpx.AsyncClient(timeout=300.0) as client: # long time-out due to multiple pdfs (scenario)
            response = await client.post(
                f"http://host.docker.internal:{user_port}/process-pdf/{expert_name}",
                files=[("files", open(os.path.join(temp_dir, f), "rb")) for f in os.listdir(temp_dir)] # creates list of tuples, for each pdf file one entry
            )     # Forward to HB_Agent for processing

            
            # Clean up temporary directory
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Error from HB_Agent service during PDF processing"
                )
            
            return JSONResponse(content={"status": "success", "message": "PDFs processed successfully"}) # reponse after succesful RAG
            
    except Exception as e:
        logger.error(f"PDF processing failed: {e}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}") # failure

@app.post("/add-user")
async def add_user_endpoint(user: UserRegistration): # add user to the database 
    try:
        add_user(user.username, user.password, user.openai_key) # add the user credentials if not already existing username
        return {"status": "success", "message": "User added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) # error message handled in streamlit

@app.post("/verify-user")
async def verify_user_endpoint(user: UserCredentials):
    try:
        is_verified = verify_user(user.username, user.password) # verify user name and password in database
        return {"status": "success", "verified": is_verified}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-user-info/{username}")
def get_user_info_endpoint(username: str):
    try:
        user_info = get_user_info(username) # get user port and openAI key to deploy the hb agent
        if user_info is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user_info
    except Exception as e:
        logger.error(f"Error in get_user_info_endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/get-generated-data/{username}")
def get_generated_data(username: str):
    output_base = f"/chroma_db/output_pipeline/{username}" # specific output for each user
    if not os.path.exists(output_base):
        return {"runs": []} # no runs yet
    runs = sorted([d for d in os.listdir(output_base) if os.path.isdir(os.path.join(output_base, d))]) # creat list of the outputs
    data = []
    for run in runs:
        run_folder = os.path.join(output_base, run)
        # Only include files, not directories
        files = [f for f in os.listdir(run_folder) if os.path.isfile(os.path.join(run_folder, f))] # create a list of all the runs in the user output
        data.append({"run": run, "files": files}) 
    return {"runs": data} # showcase the runs

@app.get("/download-run-zip/{username}/{run}")
def download_run_zip(username: str, run: str): # zip the file and make it available for download
    folder_path = os.path.join("/chroma_db/output_pipeline", username, run) 
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        raise HTTPException(status_code=404, detail=f"Folder at path {folder_path} not found or is not a directory.")
    # Create a zip in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
    zip_buffer.seek(0)
    return StreamingResponse(zip_buffer, media_type="application/zip", headers={"Content-Disposition": f"attachment; filename={run}.zip"}) # return the specified zip file