from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from langgraph.prebuilt import create_react_agent
from agents import AgentBuilder, OpenAIAgent
from langchain_core.messages import SystemMessage,  HumanMessage, AIMessage,ToolMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from config import OPENAI_API_KEY
import uvicorn
from pydantic import BaseModel
import json
import os 
from datetime import datetime
from fastapi.responses import JSONResponse
import shutil
from typing import List
from memory import PDFProcessor,ChromaMemory
import logging
from event_data_generation.run_full_pipeline_modular import run_pipeline_from_vars

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()
def load_prompt_from_file(file_path: str):
    """Loads the contents of a text file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    with open(file_path, 'r') as file:
        return file.read().strip()

def create_supervisor(username):
    """Creates a multi-agent architecture with supervisor architecture, initializes three different 
    experts. An event, analytical and environemental expert for the definition of health behavior
    personas. These variables are subsequently used by the supervisor to start data generation based
    on a SMT-solver."""

    # Ensure the marker directory exists inside the persisted Chroma volume
    os.makedirs("/chroma_db/markers", exist_ok=True)

    # Define user-specific marker path
    marker_file = f"/chroma_db/markers/semantic_initialized_{username}.txt"

    environmental_expert = AgentBuilder(
        system_prompt_file="Set_up/Templates/SM_environmental_agent.txt",
        episodic_prompt_file="Set_up/Templates/Episodic_prompt.txt",
        semantic_prompt_file="Set_up/Templates/Semantic_prompt.txt",
        reflection_prompt_file="Set_up/Templates/Reflection_prompt.txt",
        episodic_collection=f"environmental_expert_eps_{username}",  
        semantic_collection=f"environmental_expert_sem_{username}",  
        episodic_number=3, semantic_number=3,
        agent=OpenAIAgent(), agent_name="environmental_expert"
    )

    event_expert = AgentBuilder(
        system_prompt_file="Set_up/Templates/SM_event_agent.txt",
        episodic_prompt_file="Set_up/Templates/Episodic_prompt.txt",
        semantic_prompt_file="Set_up/Templates/Semantic_prompt.txt",
        reflection_prompt_file="Set_up/Templates/Reflection_prompt.txt",
        episodic_collection=f"event_expert_eps_{username}",  
        semantic_collection=f"event_expert_sem_{username}",  
        episodic_number=3, semantic_number=3,
        agent=OpenAIAgent(), agent_name="event_expert"
    )

    analytical_expert = AgentBuilder(
        system_prompt_file="Set_up/Templates/SM_analyst_agent.txt",
        episodic_prompt_file="Set_up/Templates/Episodic_prompt.txt",
        semantic_prompt_file="Set_up/Templates/Semantic_prompt.txt",
        reflection_prompt_file="Set_up/Templates/Reflection_prompt.txt",
        episodic_collection=f"analytical_expert_eps_{username}",  
        semantic_collection=f"analytical_expert_sem_{username}",  
        episodic_number=3, semantic_number=3,
        agent=OpenAIAgent(), agent_name="analytical_expert"
    )

    # Check if the general knowledge has already been copied
    if not os.path.exists(marker_file):
        memory = ChromaMemory()

        # Copy general knowledge entries for each agent. Ensure that you use the correct collection name, and store in Data folder. 
        for collection_type, general_name, user_collection in [
            ("environmental", "general_environmental", f"environmental_expert_sem_{username}"),
            ("event", "general_event", f"event_expert_sem_{username}"),
            ("analytical", "general_analytical", f"analytical_expert_sem_{username}")
        ]:
            try:
                entries = memory.search(query="*", collection_name=general_name, top_k=1000)
                if entries is None:
                    entries = []
            except Exception:
                entries = []  # If collection does not exist or is empty, just skip
            for entry in entries:
                memory.add_entry(entry, collection_name=user_collection) # add the general knowledge from the semantic memories to each user memory
        # Create the persistent marker file
        with open(marker_file, "w") as f:
            f.write("Initialized")
            logging.info("Initialized the semantic memories")  # Log message for Docker container
    logging.info("Semantic memories already initialized")  # Log message for Docker container


    @tool
    def environmental_expert_tool(query: str):
        """Use this tool to extract and structure environmental constants for simulation participants, 
        such as persona features (e.g., age group, gender distribution, education level), sample size, 
        start date, simulation horizon, and available day parts."""
        return f"{environmental_expert.run(query)}"

    @tool
    def event_expert_tool(query: str):
        """Use this tool to define and structure behavioral events for the simulation, including event metadata, characteristics, 
        constraints, and temporal patterns. Use this when event-related details are needed or incomplete."""
        return f"{event_expert.run(query)}"

    @tool
    def analytical_expert_tool(query: str):
        """Use this tool to analyze temporal relationships between events. It returns logical constraints and dependencies
        between events in Linear Temporal Logic (LTL) format."""
        return f"{analytical_expert.run(query)}"

    @tool
    def run_data_generation(constant_persona_features: dict, eventironmental_data: list, ltl_expressions: list):
        """
        This function runs the full event data generation and visualization pipeline using expert-defined templates. It requires three mandatory inputs:
        constant_persona_features (dict): Static persona attributes.
        eventironmental_data (list): Environmental/event-related data records.
        ltl_expressions (list): LTL rules for temporal event logic.
        """
        return run_pipeline_from_vars(
            constant_persona_features,
            eventironmental_data,
            ltl_expressions)
    # Instigate llm for supervisor
    llm = ChatOpenAI(streaming=True, api_key=OPENAI_API_KEY, model="gpt-4.1", temperature=0.2)  
    # Create tools mapping to create connection between supervisor and experts
    tools = [environmental_expert_tool, event_expert_tool, analytical_expert_tool, run_data_generation]
    # expert prompt supervisor
    system_prompt = (load_prompt_from_file("Set_up/Templates/Supervisor_template.txt"))
    # Implemented ReAct agent from langgraph
    supervisor = create_react_agent(llm, tools, prompt=system_prompt)
    # tools seperately called to ensure that they can be used for the exit protocol. 
    supervisor.environmental_expert=environmental_expert
    supervisor.event_expert=event_expert
    supervisor.analytical_expert=analytical_expert

    # Supervisor episodic memory collection name
    supervisor_episodic_collection = f"supervisor_eps_{username}"
    supervisor_semantic_collection = f"supervisor_sem_{username}"
    # Initialize supervisor episodic memory handler from COALA paper
    from core.conversation_handler import ConversationHandler
    from core.prompt_manager import PromptManager
    supervisor_prompt_manager = PromptManager( system_prompt_file="Set_up/Templates/System_message.txt",
        episodic_prompt_file="Set_up/Templates/Episodic_prompt.txt",
        semantic_prompt_file="Set_up/Templates/Semantic_prompt.txt",
        reflection_prompt_file="Set_up/Templates/Reflection_prompt.txt"
    )
    supervisor_memory_handler = ConversationHandler(
        prompt_manager=supervisor_prompt_manager,
        agent=OpenAIAgent(),  
        collection_episodic=supervisor_episodic_collection,
        collection_semantic=supervisor_semantic_collection,
        top_k_episodic=3,
        top_k_semantic=3,
        name="supervisor"
    )
    supervisor.memory_handler = supervisor_memory_handler
    return supervisor

def format_conversation(messages):
    """"Create conversation summary to use in prompt """
    conversation = []
    for message in messages:
        if message['role'] in ['assistant', 'user']:
            conversation.append(f"{message['role'].capitalize()}: {message['content']}")
    return "\n".join(conversation)



@app.on_event("startup")  # initialize supervisor once on start-up to ensure that the message history is kept for the tools (episodic)
def startup_event(): 
    global supervisor, conversation_history
    conversation_history = []  # global conversation history
    username = os.getenv("USERNAME", "default_user")  # Get the username from the environment variable
    supervisor = create_supervisor(username)  # Pass the username to create_supervisor
    print("Supervisor initialized")

class QueryRequest(BaseModel):
    query: str


@app.post("/supervisor/ask")
async def ask_supervisor(query: QueryRequest):
    global supervisor, conversation_history
    try:
        formatted_history = format_conversation(conversation_history) # without system message
        # Get relevant episodic memory chunks for this query
        episodic_prompt = supervisor.memory_handler.prompt_manager.get_episodic_prompt(
            query.query,
            supervisor.memory_handler.collection_episodic,
            supervisor.memory_handler.top_k_episodic
        )
        conversation_history.append({"role": "user", "content": query.query}) # append user message for future
        conversation_history_prompt = (
            "You are a helpful supervisor who manages expert agents.\n\n"
            f"This is the episodic memory that can be linked to the current user question:\n{episodic_prompt}\n\n"
            f"This is the conversation history:\n{formatted_history}\n\n"
            f"This is the current user question:\n{query.query}"
            
        )
        final_prompt = {"messages": [("user", conversation_history_prompt)]} # final prompt combined all the information

        async def stream_openai(query_input):
            assistant_response = ""
            async for item in supervisor.astream(query_input, stream_mode="messages"): # get typewrite stream
                message_chunk, metadata = item # items that are streamed
                content = message_chunk.content or ""
                if len(content.strip()) <= 100: # tool messages are streamed and returned as one final message, stop those to ensure that they are not entered twice
                    assistant_response += content # add to assistant_response
                yield json.dumps({
                    "content": content,
                    "langgraph_node": metadata.get("langgraph_node"),
                    "additional_kwargs": message_chunk.additional_kwargs,
                    "response_metadata": message_chunk.response_metadata,
                    "id": message_chunk.id
                }) + "\n"
            conversation_history.append({
                "role": "assistant",
                "content": assistant_response
            }) # add the reponse of the agent to the conversation history
        return StreamingResponse(stream_openai(final_prompt), media_type="application/json")
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error occurred: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )

@app.post("/supervisor/update-memory")
async def update_memory():
    global supervisor, conversation_history
    try:
        # Trigger memory update for all experts
        prompt = "exit"  # Using the existing exit protocol for memory updates
        supervisor.environmental_expert.run(prompt) # all initialized in create supervisor
        supervisor.event_expert.run(prompt)
        supervisor.analytical_expert.run(prompt)
        # Update supervisor episodic memory as well
        if conversation_history:
            supervisor.memory_handler.messages.extend(conversation_history)
            supervisor.memory_handler.run_conversation(prompt)
            conversation_history.clear()
        return JSONResponse(
            content={
                "status": "success",
                "message": "Memory updated successfully",
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Memory update failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )

@app.post("/process-pdf/{expert_name}")
async def process_pdf(expert_name: str, files: List[UploadFile] = File(...)):
    try:
        username = os.getenv("USERNAME", "default_user")  # Get the username from the environment variable
        # Map expert names to their semantic collection names
        collection_mapping = {
            "environmental_expert": f"environmental_expert_sem_{username}",
            "event_expert": f"event_expert_sem_{username}",
            "analytical_expert": f"analytical_expert_sem_{username}"
        }
        if expert_name not in collection_mapping: # for future use if someone changes experts but forgets to adjust here
            raise HTTPException(status_code=400, detail=f"Invalid expert name. Must be one of: {list(collection_mapping.keys())}")
        
        semantic_collection = collection_mapping[expert_name] # get user specific collection
        pdf_dir = os.path.join("Set_up", "Semantic_memory", expert_name) # Make pdf dir for temporary storage
        os.makedirs(pdf_dir, exist_ok=True)
        for file in files:         # Save uploaded files
            file_path = os.path.join(pdf_dir, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
        pdf_processor = PDFProcessor(pdf_dir, semantic_collection) # process all the pdfs in the directory
        pdf_processor.process_pdf_to_chunks()
        for file in os.listdir(pdf_dir):
            os.remove(os.path.join(pdf_dir, file)) # clean up the directory afterwards
        os.rmdir(pdf_dir) # remove directory
        return JSONResponse(
            content={
                "status": "success",
                "message": f"PDFs processed and added to {semantic_collection} successfully",
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")

