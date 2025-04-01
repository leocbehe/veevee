import streamlit as st
import datetime
import requests
import uuid
from jose import jwt

# DECLARATIONS --------------------------------------------------------------------------------------------

# Define the landing page function
def landing_page():

    # Initialize chatbot name and description in session state if they don't exist
    if "chatbot_name_input" not in st.session_state:
        st.session_state.chatbot_name_input = ""
    if "chatbot_description_input" not in st.session_state:
        st.session_state.chatbot_description_input = ""
    if "chatbot_model_path_input" not in st.session_state:
        st.session_state.chatbot_model_path_input = ""

    # Render the input fields in the sidebar, regardless of button press
    st.session_state.chatbot_name_input = st.sidebar.text_input("Chatbot Name:", value=st.session_state.chatbot_name_input)
    st.session_state.chatbot_description_input = st.sidebar.text_input("Chatbot Description:", value=st.session_state.chatbot_description_input)
    st.session_state.chatbot_model_path_input = st.sidebar.text_input("Chatbot Model Path:", value=st.session_state.chatbot_model_path_input)

    if st.sidebar.button("Create Chatbot"):
        create_chatbot()

    # Retrieve chatbots from the database
    try:
        response = requests.get(
            "http://localhost:8000/chatbots/",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        if response.status_code == 200:
            chatbots = response.json()
            st.subheader("Your Chatbots:")
            if chatbots:
                for chatbot in chatbots:
                    col1, col2 = st.columns([0.8, 0.2])
                    with col1:
                        st.write(f"- {chatbot['chatbot_name']}")
                    with col2:
                        if st.button(f"Select {chatbot['chatbot_name']}", key=f"select_{chatbot['chatbot_id']}"):
                            st.session_state.chatbot_id = chatbot['chatbot_id']
                            st.session_state.chatbot_name = chatbot['chatbot_name']
                            st.session_state.chatbot_description = chatbot['description']
                            st.session_state.chatbot_model_path = chatbot['model_path']
                            st.session_state.current_page = "chatbot_page"
                            st.rerun()


            else:
                st.write("There's nobody here...")
        else:
            st.error(f"Failed to retrieve chatbots: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Error connecting to the chatbot service: {str(e)}")

def chatbot_page():
    st.write(f"**Chatbot Name:** {st.session_state.chatbot_name}")
    st.write(f"**Chatbot Description:** {st.session_state.chatbot_description}")
    st.write(f"**Chatbot Model Path:** {st.session_state.chatbot_model_path}")
    
# Function to check if token is valid
def is_token_valid():
    if not st.session_state.access_token or not st.session_state.token_expiry:
        return False
    return datetime.datetime.now().timestamp() < st.session_state.token_expiry

def initialize_session_state():
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "token_expiry" not in st.session_state:
        st.session_state.token_expiry = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "chatbot_id" not in st.session_state:
        st.session_state.chatbot_id = None
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    if "chatbot_name" not in st.session_state:
        st.session_state.chatbot_name = None
    if "chatbot_description" not in st.session_state:
        st.session_state.chatbot_description = None
    if "chatbot_model_path" not in st.session_state:
        st.session_state.chatbot_model_path = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "landing"

def create_chatbot():
    try:
        response = requests.post(
            "http://localhost:8000/chatbots/",
            json={
                "chatbot_id": str(uuid.uuid4()),
                "owner_id": st.session_state.user_id,
                "chatbot_name": st.session_state.chatbot_name_input,
                "description": st.session_state.chatbot_description_input,
                "model_path": st.session_state.chatbot_model_path_input,
                "created_at": datetime.datetime.now().isoformat(),
                "is_active": True
            },
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        if response.status_code == 200:
            st.success("Chatbot created successfully!")
        else:
            st.error(f"Failed to create chatbot: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Error connecting to the chatbot service: {str(e)}")

def login():
    try:
        response = requests.post(
            "http://localhost:8000/auth/token", 
            data={
                "username": username,
                "password": password
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            from app.dependencies import SECRET_KEY
            token_data = response.json()
            st.session_state.access_token = token_data.get("access_token")            
            decoded_token = jwt.decode(st.session_state.access_token, SECRET_KEY, options={"verify_signature": False})
            st.session_state.token_expiry = decoded_token.get("expires_at")
            st.session_state.username = decoded_token.get("username")
            st.session_state.user_id = decoded_token.get("sub")
            
            st.success(f"Welcome, {username}!")

            st.rerun() 
        else:
            st.error("Invalid username or password")
    except Exception as e:
        st.error(f"Error connecting to authentication service: {str(e)}")

# RUNS AT START --------------------------------------------------------------------------------------------

initialize_session_state()

# CONDITIONAL RENDERING --------------------------------------------------------------------------------------------

if 'access_token' in st.session_state and st.session_state.access_token and is_token_valid():
    if st.session_state.current_page == "landing":
        st.title(f"VeeVee UI - Welcome, {st.session_state.username}!")
        landing_page()
    elif st.session_state.current_page == "chatbot_page":
        st.title(f"VeeVee UI - Chatbot: {st.session_state.chatbot_name}")
        chatbot_page()
else:
    st.title("VeeVee UI")
    st.warning("Warning: Refreshing the page will log you out!")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        if submit_button:
            login()