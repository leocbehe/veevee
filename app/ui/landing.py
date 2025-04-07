import streamlit as st
import requests
from .chatbots import create_chatbot

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