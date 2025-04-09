import streamlit as st
import datetime
import requests
import uuid
from jose import jwt
import pandas as pd
import app.ui.chatbots_ui as chatbots_ui
import app.ui.conversation_ui as conversation_ui
import app.ui.landing_ui as landing_ui


# DECLARATIONS --------------------------------------------------------------------------------------------
    
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
    if "chatbot_name" not in st.session_state:
        st.session_state.chatbot_name = None
    if "chatbot_description" not in st.session_state:
        st.session_state.chatbot_description = None
    if "chatbot_model_path" not in st.session_state:
        st.session_state.chatbot_model_path = None
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    if "conversation_description" not in st.session_state:
        st.session_state.conversation_description = None
    if "conversation_messages" not in st.session_state:
        st.session_state.conversation_messages = []
    if "current_page" not in st.session_state:
        st.session_state.current_page = "landing_page"

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
    if st.session_state.current_page == "landing_page":
        st.title(f"VeeVee UI - Welcome, {st.session_state.username}!")
        landing_ui.landing_page()
    elif st.session_state.current_page == "chatbot_page":
        st.title(f"VeeVee UI - Chatbot: {st.session_state.chatbot_name}")
        chatbots_ui.chatbot_page()
    elif st.session_state.current_page == "conversation_page":
        st.title(f"VeeVee UI - Conversation: {st.session_state.conversation_id}")
        conversation_ui.conversation_page()
else:
    st.title("VeeVee UI")
    st.warning("Warning: Refreshing the page will log you out!")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        if submit_button:
            login()