import streamlit as st
import datetime
import requests
from jose import jwt

# DECLARATIONS --------------------------------------------------------------------------------------------

# Define the landing page function
def landing_page():
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
                    st.write(f"- {chatbot['chatbot_name']}")
            else:
                st.write("There's nobody here...")
        else:
            st.error(f"Failed to retrieve chatbots: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Error connecting to the chatbot service: {str(e)}")
    
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
            
            st.success(f"Welcome, {username}!")

            st.rerun() # Rerun to show the landing page
        else:
            st.error("Invalid username or password")
    except Exception as e:
        st.error(f"Error connecting to authentication service: {str(e)}")

# RUNS AT START --------------------------------------------------------------------------------------------



# CONDITIONAL RENDERING --------------------------------------------------------------------------------------------

if 'access_token' in st.session_state and st.session_state.access_token and is_token_valid():
    st.title(f"VeeVee UI - Welcome, {st.session_state.username}!")
    landing_page()
else:
    st.title("VeeVee UI")
    st.warning("Warning: Refreshing the page will log you out!")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        if submit_button:
            login()