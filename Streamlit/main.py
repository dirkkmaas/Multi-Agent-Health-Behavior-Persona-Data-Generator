import streamlit as st
import requests
import json
from collections import deque
import os
from datetime import datetime
import subprocess
import docker
import time

st.set_page_config(page_title="Health Behavior Persona Data Generator", layout="centered")

    
def start_hb_agent(username, openai_key, port):
    client = docker.from_env() # load /create docker containers trough python
    container_name = f"hb_agent_{username}" # name container
    try:
        container = client.containers.get(container_name)
        container.reload()  # Refresh container's status info
        if container.status != 'running':
            st.session_state.agent_logs = []  # Clear previous logs
            with st.spinner(f"Starting agent network for {username}..."):
                container.start() # start container
                st.session_state.agent_logs.append(f"Loading {container_name}...")
                log_placeholder = st.empty() # log placeholder
                # Wait for the application to start
                log_stream = container.logs(stream=True, follow=True) # container logs to check for errors
                for line in log_stream: # stream logs
                    decoded_line = line.decode('utf-8').strip()
                    st.session_state.agent_logs.append(decoded_line)
                    log_placeholder.text_area("Agent Logs", value="\n".join(st.session_state.agent_logs), height=300) 
                    if "Application startup complete." in decoded_line:
                        st.success("Agent started successfully!")
                        time.sleep(2)
                        break
                else:
                    st.error("Agent failed to start. Please check the logs for more details.")
                    return None, None
        else:
            st.info(f"Agent network for {username} is already running.")

        st.session_state.hb_agent_container_name = container_name
        return container_name, port # return port for later

    except docker.errors.NotFound:
        st.session_state.agent_logs = []  # Clear previous logs
        with st.spinner(f"Creating and starting agent network for {username}..."):
            try:
                container = client.containers.run(
                    "hb_agent_image:latest",
                    name=container_name,
                    detach=True,
                    environment={"OPENAI_API_KEY": openai_key, "USERNAME": username},
                    ports={'5000/tcp': port},
                    network="app_network",  # use fixed network name, not folder-prefixed
                    volumes={'chroma_data': {'bind': '/chroma_db', 'mode': 'rw'}}  # use fixed volume name
                ) # create a new container with its name, OpenAI key, username and user specific port
                st.session_state.hb_agent_container_name = container_name

                log_placeholder = st.empty()
                log_stream = container.logs(stream=True, follow=True) # stream the logs
                for line in log_stream:
                    decoded_line = line.decode('utf-8').strip()
                    st.session_state.agent_logs.append(decoded_line)
                    log_placeholder.text_area("Agent Logs", value="\n".join(st.session_state.agent_logs), height=300)
                    if "Application startup complete." in decoded_line:
                        st.success("Agent started successfully!")
                        time.sleep(1)
                        break
                else:
                    st.error("Agent failed to start. Please check the logs for more details.")
                    return None, None

                return container_name, port # return container_name and port to use for prompts
            except docker.errors.APIError as e:
                st.error(f"Failed to start {container_name}: {e}")
                return None, None

def stop_hb_agent(container_name):
    """Stops the current running container which is used by the user.
    Afterwards clears all the information stored in the streamlit application"""
    client = docker.from_env() # get docker
    try:
        container = client.containers.get(container_name)
        container.stop()   # stop container
        print(f"{container_name} stopped.")
    except docker.errors.NotFound:
        print(f"Container {container_name} not found.")
    except docker.errors.APIError as e:
        print(f"Error stopping {container_name}: {e}")
    finally:
        for key in ['logged_in', 'hb_agent_started', 'agent_logs', 'username',
                    'openai_key', 'user_port', 'hb_agent_container_name', 'history']:
            if key in st.session_state:
                del st.session_state[key] # reset everything stored in streamlit
        st.session_state.page = "login" # back to login
        st.rerun() # rerun

def login_screen():
    """Instagets login screen where user should provide username and password,
    if not registered user can go to register screen by button"""
    st.title("Login") 
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_btn"):
        if not username or not password:
            st.error("Please enter username and password.") # ensure both are entered
        else:
            response = requests.post("http://fastapi_app:8000/verify-user", json={
                "username": username,
                "password": password
            }) # check password in database postgresql
            if response.status_code == 200 and response.json().get("verified"):
                st.session_state.logged_in = True
                st.session_state.username = username  # Set username in session state
                # Retrieve additional info (OpenAI key and port)
                info_response = requests.get(f"http://fastapi_app:8000/get-user-info/{username}")
                if info_response.status_code == 200:
                    user_info = info_response.json()
                    openai_key = user_info.get("openai_key")
                    user_port = user_info.get("port")
                    if not openai_key or not user_port:
                        st.error("Missing OpenAI key or port info from server.")
                    else:
                        st.session_state.openai_key = openai_key
                        st.session_state.user_port = user_port
                        st.session_state.page = "agent_startup" # go to start up page with starting logs
                        st.rerun()
                else:
                    st.error("Error retrieving user info from server.") 
            else:
                st.error("Invalid username or password.")

    if st.button("Go to Register", key="go_to_register"): # go to register screen
        st.session_state.page = "register"
        st.rerun()

def register_screen():
    """This function creates the register screen, here users should supply their unique username, password
    and openAI key. After registration the user is directed to the login screen"""
    st.title("Register")
    username = st.text_input("Username", key="register_username")
    password = st.text_input("Password", type="password", key="register_password")
    openai_key_input = st.text_input("OpenAI Key", type="password", key="register_openai_key")

    if st.button("Register", key="register_btn"):
        if username and password and openai_key_input:
            response = requests.post("http://fastapi_app:8000/add-user", json={
                "username": username,
                "password": password,
                "openai_key": openai_key_input
            })
            if response.status_code == 200:
                st.success("User registered successfully! Please log in.") # succesfull login message
                st.session_state.page = "login"  # Redirect back to the login screen.
                time.sleep(1)  
                st.rerun()
            else:
                st.error(f"Error registering user: {response.text}") # error with adding user
        else:
            st.error("Please fill in all fields for registration.") # not all information

    if st.button("Back to Login", key="back_to_login"): # go back to login if entered accidentally 
        st.session_state.page = "login"
        st.rerun()

def agent_startup_screen():
    """Screen showing the starting procedure of the agent, used to show error messsage such as 
    no credentials on OpenAI key"""
    st.title("Starting Agent Network...")
    username = st.session_state.get("username")
    openai_key = st.session_state.get("openai_key")
    user_port = st.session_state.get("user_port")
    container_name, port = start_hb_agent(username, openai_key, user_port)
    if container_name is None: # if failed to start
        st.error("Failed to start agent. Please check logs or restart the login procedure.")
        if st.button("Restart login procedure"): # option to go back to login
            st.session_state.hb_agent_started = False
            st.session_state.agent_logs = []
            st.session_state.page = "login"
            st.rerun()
    else:
        st.session_state.hb_agent_started = True
        st.session_state.page = "main"  # This will trigger the chatbot interface (else)
        st.rerun()

# initialization statements
if 'page' not in st.session_state:
    st.session_state.page = "login"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'hb_agent_started' not in st.session_state:
    st.session_state.hb_agent_started = False
if 'agent_logs' not in st.session_state:
    st.session_state.agent_logs = []

# logic for moving trough screens
if st.session_state.page == "login":
    login_screen()
elif st.session_state.page == "register":
    register_screen()
elif st.session_state.page == "agent_startup":
    agent_startup_screen()
else:
    st.title("Behavior Change Data Generator")  # Show the main application title

    with st.sidebar:
        st.header("Memory Management") # all memory management components
        
        # Semantic Memory Management Section
        st.subheader("Semantic Memory Management")
        expert_selection = st.selectbox(
            "Select Expert",
            ["environmental_expert", "event_expert", "analytical_expert"],
            format_func=lambda x: x.replace("_", " ").title()
        ) # select one of the experts to update the memory
        
        uploaded_files = st.file_uploader(
            "Upload PDFs for Semantic Memory",
            type=['pdf'],
            accept_multiple_files=True
        ) # uploaded pdfs for embedding
        
        if uploaded_files:
            if 'processing_pdfs' not in st.session_state: # instigate variable
                st.session_state.processing_pdfs = False 
            if not st.session_state.processing_pdfs:
                if st.button("Process PDFs", type="primary"): # create button to start the pdf process
                    try:
                        st.session_state.processing_pdfs = True # set true
                        with st.spinner("Processing PDFs..."):
                            temp_dir = "temp_uploads"
                            os.makedirs(temp_dir, exist_ok=True) # make temporary directory
                            for uploaded_file in uploaded_files:
                                file_path = os.path.join(temp_dir, uploaded_file.name)
                                with open(file_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer()) # write a files to a temproary storage
                            files = [("files", open(os.path.join(temp_dir, f), "rb")) for f in os.listdir(temp_dir)] # write files in tuple for request
                            response = requests.post(
                                f"http://fastapi_app:8000/process-pdf/{expert_selection}",
                                files=files,
                                headers={"X-User-Port": str(st.session_state.user_port)}
                            ) # use userport for specific user container
                            for file in os.listdir(temp_dir):
                                os.remove(os.path.join(temp_dir, file)) # remove files
                            os.rmdir(temp_dir) # remove directory
                            if response.status_code == 200:
                                st.success("PDFs processed successfully!")
                            else:
                                st.error(f"Error processing PDFs: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                    finally:
                        st.session_state.processing_pdfs = False
            else:
                st.info("PDF processing is currently running. Please wait...")

        st.subheader("Episodic Memory Management") # for episodic memory
        if st.button("Update Memory", type="primary"):
            # Check if there's any conversation history first
            if not st.session_state.history: # to ensure that the agents have conversation memory
                st.error("No conversation history found!")
                st.warning("Please interact with the agent first before updating memory.")
            else:    
                try:
                    with st.spinner("Updating memory..."):
                        response = requests.post(
                            "http://fastapi_app:8000/update-memory",
                            headers={"X-User-Port": str(st.session_state.user_port)}
                        ) # post to specific user port (using user name for fastapi)
                        if response.status_code == 200:
                            response_data = response.json()
                            if response_data.get("status") == "warning":
                                st.warning(response_data.get("message", "Please interact with the agent first before updating memory."))
                            else: 
                                st.success(response_data.get("message", "Memory updated successfully!"))
                                st.session_state.last_memory_update = response_data.get("timestamp")
                                # Clear conversation history after successful update
                                st.session_state.history = []
                                st.session_state.tool_placeholders = {} # clear tool placeholders
                                st.rerun()  # Rerun 
                        else:
                            st.error(f"Failed to update memory: {response.text}")
                except Exception as e:
                    st.error(f"Error updating memory: {str(e)}")
            
            if st.session_state.last_memory_update:
                st.info(f"Last memory update: {st.session_state.last_memory_update}")

        st.header("Generated Data Output")
        with st.expander("Show Generated Data Output", expanded=False):
            # Add a refresh button to re-run the code when the expander is open to ensure that it can be updated after data generation
            if st.button("Refresh Data", key="refresh_data_button"):
                st.rerun()
            username = st.session_state.get("username")
            # Use FastAPI endpoints to fetch data
            response = requests.get(f"http://fastapi_app:8000/get-generated-data/{username}") # get each user-specifics runs
            if response.status_code == 200:
                data = response.json()
                runs = data.get("runs", []) # list of runs
                if runs:
                    run_names = [run["run"] for run in runs]
                    selected_run = st.selectbox("Select a data generation run:", run_names, key="data_run_select") # create selection window for run names
                    if selected_run: 
                        st.write(f"Run: {selected_run}") # show selected run
                        zip_url = f"http://fastapi_app:8000/download-run-zip/{username}/{selected_run}"
                        zip_response = requests.get(zip_url)
                        if zip_response.status_code == 200:
                            st.download_button(
                                label=f"Download {selected_run} as ZIP",
                                data=zip_response.content,
                                file_name=f"{selected_run}.zip",
                                mime="application/zip"
                            ) # download selected run
                        else:
                            st.warning(f"Could not fetch ZIP for {selected_run}.")
                else:
                    st.info("No data generation runs found.")
            else:
                st.warning("Could not fetch generated data from FastAPI.")
        if st.button("Logout"):
            if 'hb_agent_container_name' in st.session_state:
                stop_hb_agent(st.session_state.hb_agent_container_name)  # Shut down the hb_agent
            st.session_state.logged_in = False  # Reset login status
            st.session_state.hb_agent_started = False  # Reset the agent startup status
            st.session_state.history = []  # Clear message history
            st.success("Logged out successfully!")
            st.rerun()  # Rerun the app to show the login form

    # Initialize session state for chat history and tool messages.
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'tool_placeholders' not in st.session_state:
        st.session_state.tool_placeholders = {}
    if 'last_memory_update' not in st.session_state:
        st.session_state.last_memory_update = None

    for msg in st.session_state.history:  # logs history and ensures that it is printed
        role = "user" if msg['sender'] == "user" else "assistant"
        with st.chat_message(role):
            st.markdown(msg['message'])
            if msg['sender'] == "assistant" and "expander" in msg and msg["expander"]: # ensure that expander is kept
                with st.expander("Message prompt"):
                    st.markdown(msg["expander"])

    user_input = st.chat_input("Enter message")  # chat entry

    def stream_response(prompt):
        """
        Logic to stream the different tool responses, tool calls and final agent response to the chatbox
        """
        agent_text = "**[Supervisor]:**\n"  # Accumulated agent text
        word_threshold = 1  # Token count threshold for ignoring tool messages for langgraph 
        agent_placeholder = st.chat_message("assistant").empty() # placeholder
        inside_tool_calls = False

        with requests.post(
            "http://fastapi_app:8000/ask",
            headers={"Content-Type": "application/json",
            "X-User-Port": str(st.session_state.user_port) 
            },
            data=json.dumps({"prompt": prompt}),
            stream=True
        ) as response:  # stream the response from the fastAPI 
            if response.status_code != 200:
                st.error(f"Server error: {response.status_code}")
                return "Error: Could not get response."

            # Process the streamed response line by line.
            for line in response.iter_lines(decode_unicode=True):
                try:
                    data = json.loads(line)  # load the parsed json line
                except json.JSONDecodeError:
                    continue

                content = data.get("content", "")  # use the data structure to get the message content
                node = data.get("langgraph_node", "")  # tool or agent entry
                additional_kwargs = data.get("additional_kwargs", {})  # tool call
                message_id = data.get("id", "")  # Unique ID for tool message chunks

                # if agent message with tool call
                if node == "agent":
                    if "tool_calls" in additional_kwargs:
                        for tool_call in additional_kwargs["tool_calls"]:  # if a tool call is entered
                            function = tool_call.get("function", {}) # is the query
                            tool_name = function.get("name")
                            if tool_name:
                                agent_text += f"\n**[Expert Query: {tool_name}]**\n"  # tool name is parsed once
                            agent_text += function.get("arguments", "")  # query
                            inside_tool_calls = True 
                    if inside_tool_calls and not ("tool_calls" in additional_kwargs):  # logic to end tool calls with a ---
                        agent_text += "\n\n---\n\n" 
                        inside_tool_calls = False
                    agent_text += content # place in the supervisor window
                    agent_placeholder.markdown(agent_text + "\n\n")
                # if tools message
                elif node == "tools": 
                    chunk_too_long = len(content.split()) > word_threshold  # if chunk is longer than one (means the prompt to the expert is parsed)
                    if chunk_too_long:  # logic to showcase the expert prompt with  episodic an semantic memory entries in the expert messages
                        try: 
                            content = json.loads(content)  # load the json content (for the prompt)
                            prompt = content.get("prompt", {})  # prompt
                            prompt_id = prompt.get("message_id")  # id (same as the corresponding streamed message id)
                            expert_prompt = prompt.get("expert_prompt")  # get the expert prompt from the parsed prompt. Because of nested dictionaires
                            content = expert_prompt  
                            message_id = prompt_id
                        except Exception as e:
                            print(f"Error parsing prompt from long tool message: {e}")
                            continue

                    if message_id not in st.session_state.tool_placeholders:  # if new message_id
                        header = f"**[Expert:]**\n"  # can add message_id in the tool description
                        placeholder = st.chat_message("assistant").empty()  # create an empty message
                        expander = st.expander("Message prompt")  # initialize the expander for the message prompt
                        st.session_state.tool_placeholders[message_id] = {
                            "placeholder": placeholder,
                            "text": header,
                            "expander": expander,
                            "expander_text": ""
                        }  # create a message to stream the new message id
                    if message_id in st.session_state.tool_placeholders:  # if message_id already initialized
                        tool_entry = st.session_state.tool_placeholders[message_id]  # get the corresponding message
                        tool_placeholder = tool_entry["placeholder"]
                        tool_text = tool_entry["text"]
                        expander = tool_entry["expander"]
                        if chunk_too_long:  # if prompt to expert
                            tool_entry["expander_text"] += content  # Store content for history
                            with st.session_state.tool_placeholders[message_id]["expander"]:
                                expander.markdown(content) # mark the expert information
                        else:    
                            tool_text += content
                            st.session_state.tool_placeholders[message_id]["text"] = tool_text
                            tool_placeholder.markdown(tool_text)  # stream the normal messages in the correct entry

            for msg_id, tool_entry in st.session_state.tool_placeholders.items():
                final_tool_msg = tool_entry["text"].strip()  # clean up the message
                tool_entry["placeholder"].markdown(final_tool_msg)  # add the full message
                st.session_state.history.append({
                    "sender": "assistant",
                    "message": final_tool_msg,
                    "expander": tool_entry["expander_text"]  
                })  # update the state of the Streamlit to add to history            
            st.session_state.tool_placeholders.clear()  # clean up placeholders

            final_agent_text = agent_text.strip() 
            return final_agent_text # return supervisor message

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.history.append({"sender": "user", "message": user_input}) # add user message
        assistant_response = stream_response(user_input) # use stream logic for response generation
        st.session_state.history.append({"sender": "assistant", "message": assistant_response}) # append supervisor response