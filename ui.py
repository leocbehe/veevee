import streamlit as st
import datetime
import requests
from jose import jwt
import app.ui.chatbot_ui as chatbot_ui
import app.ui.conversation_ui as conversation_ui
import app.ui.landing_ui as landing_ui
import app.ui.knowledge_base_ui as knowledge_base_ui
import app.ui.context_edit_ui as context_edit_ui
import app.ui.profile_ui as profile_ui
import app.ui.chatbot_edit_ui as chatbot_edit_ui


# DECLARATIONS --------------------------------------------------------------------------------------------
    
# Function to check if token is valid
def is_token_valid():
    if not st.session_state.access_token or not st.session_state.token_expiry:
        return False
    return datetime.datetime.now().timestamp() < st.session_state.token_expiry

def initialize_session_state():
    keys = [
        "access_token",
        "token_expiry",
        "username",
        "user_id",
        "chatbot_id",
        "chatbot_name",
        "chatbot_description",
        "chatbot_model_name",
        "conversation_id",
        "conversation_description",
        "new_conversation_description",
        "document_id",
    ]
    for key in keys:
        if key not in st.session_state:
            st.session_state[key] = None

    if "current_page" not in st.session_state:
        st.session_state.current_page = "landing_page"

    if "conversation_messages" not in st.session_state:
        st.session_state.conversation_messages = []

    if "chatbot_config" not in st.session_state:
        st.session_state.chatbot_config = {}

    if "new_chatbot_config" not in st.session_state:
        st.session_state.new_chatbot_config = {}

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

def create_user():
    try:
        response = requests.post(
            "http://localhost:8000/users/",
            json={
                "username": username,
                "password": password,
            },
            headers={"Content-Type": "application/json"}
        )
        print(f"response: {response}")
        if response.status_code == 200:
            print("User created successfully! Logging you in...")
            login()
        else:
            st.error(f"Failed to create user: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Error connecting to user creation service: {str(e)}")

# RUNS AT START --------------------------------------------------------------------------------------------

initialize_session_state()

# CONDITIONAL RENDERING --------------------------------------------------------------------------------------------

if 'access_token' in st.session_state and st.session_state.access_token and is_token_valid():
    # st.markdown("<h1 style='text-align: center;'>VeeVee UI</h1>", unsafe_allow_html=True)
    if st.session_state.current_page == "landing_page":
        landing_ui.landing_page()
    elif st.session_state.current_page == "chatbot_page":
        chatbot_ui.chatbot_page()
    elif st.session_state.current_page == "conversation_page":
        conversation_ui.conversation_page()
    elif st.session_state.current_page == "knowledge_base_page":
        knowledge_base_ui.knowledge_base_page()
    elif st.session_state.current_page == "context_edit_page":
        context_edit_ui.context_edit_page()
    elif st.session_state.current_page == "profile_page":
        profile_ui.profile_page()
    elif st.session_state.current_page == "chatbot_edit_page":
        chatbot_edit_ui.chatbot_edit_page()
else:
    st.markdown("<h1 style='text-align: center;'>VeeVee UI</h1>", unsafe_allow_html=True)
    st.warning("Warning: Refreshing the page will log you out!")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        button1, button2, _ = st.columns([0.12, 0.18, 0.7], border=False)
        with button1:
            submit_button = st.form_submit_button("Login")
            if submit_button:
                login()
        with button2:
            create_user_button = st.form_submit_button("Create User")
            if create_user_button:
                create_user()
        