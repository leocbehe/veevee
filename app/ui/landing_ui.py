import streamlit as st
import requests
from datetime import datetime
import uuid

def logout():
    # Clear session state
    st.session_state.clear()

def landing_page():
    # Initialize session state variables
    if "show_chatbot_form" not in st.session_state:
        st.session_state.show_chatbot_form = False
    if "new_chatbot_name" not in st.session_state:
        st.session_state.new_chatbot_name = ""
    if "new_chatbot_description" not in st.session_state:
        st.session_state.new_chatbot_description = ""
    if "new_chatbot_model_name" not in st.session_state:
        st.session_state.new_chatbot_model_name = ""

    def create_new_chatbot():
        chatbot_id = str(uuid.uuid4())
        chatbot_name = ""
        chatbot_description = ""
        chatbot_model_name = ""
        chatbot_owner_id = st.session_state.user_id
        chatbot_created_at = datetime.now().isoformat()
        chatbot_configuration = {}
        try:
            response = requests.post(
                "http://localhost:8000/chatbots/",
                json={
                    "chatbot_id": chatbot_id,
                    "chatbot_name": chatbot_name,
                    "description": chatbot_description,
                    "model_name": chatbot_model_name,
                    "owner_id": chatbot_owner_id,
                    "created_at": chatbot_created_at,
                    "configuration": chatbot_configuration,
                },
                headers={"Authorization": f"Bearer {st.session_state.access_token}"},
            )
            if response.status_code == 200:
                st.session_state.chatbot_id = chatbot_id
                st.session_state.current_page = "chatbot_edit_page"
            else:
                st.error(f"Failed to create chatbot: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Error connecting to the chatbot service: {str(e)}")       
            response = requests.delete(
                "http://localhost:8000/chatbots/{chatbot_id}",
                headers={"Authorization": f"Bearer {st.session_state.access_token}"},
            )
            if response.status_code != 200:
                print(f"Failed to delete chatbot: {response.status_code} - {response.text}")


    def open_profile_page():
        st.session_state.current_page = "profile_page"

    # Button to open the chatbot form, placed above "Your Chatbots"

    st.markdown(f"<h3 style='text-align: center;'>Your Chatbots</h2>", unsafe_allow_html=True)

    # Retrieve chatbots from the database and display them
    try:
        response = requests.get(
            "http://localhost:8000/chatbots/",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        if response.status_code == 200:
            chatbots = response.json()
            if chatbots:
                for chatbot in chatbots:
                    st.markdown("<hr style='margin-top: 0.5em;'>", unsafe_allow_html=True)
                    col1, col2, col3, col4 = st.columns([0.55, 0.15, 0.15, 0.15])
                    with col1:
                        st.write(f"- {chatbot['chatbot_name']}")
                    with col2:
                        if st.button(f"Select", key=f"select_{chatbot['chatbot_id']}", use_container_width=True):
                            st.session_state.chatbot_id = chatbot['chatbot_id']
                            st.session_state.chatbot_name = chatbot['chatbot_name']
                            st.session_state.chatbot_description = chatbot['description']
                            st.session_state.chatbot_model_name = chatbot['model_name']
                            st.session_state.chatbot_config = {} if not 'configuration' in chatbot else chatbot['configuration']
                            st.session_state.current_page = "chatbot_page"
                            st.rerun()
                    with col3:
                        if st.button(f"Edit", key=f"edit_{chatbot['chatbot_id']}", use_container_width=True):
                            st.session_state.chatbot_id = chatbot['chatbot_id']
                            st.session_state.chatbot_name = chatbot['chatbot_name']
                            st.session_state.chatbot_description = chatbot['description']
                            st.session_state.chatbot_model_name = chatbot['model_name']
                            st.session_state.chatbot_config = {} if not 'configuration' in chatbot else chatbot['configuration']
                            st.session_state.current_page = "chatbot_edit_page"
                            st.rerun()
                    with col4:
                        if st.button(f"Delete", key=f"delete_{chatbot['chatbot_id']}", use_container_width=True):
                            response = requests.delete(
                                f"http://localhost:8000/chatbots/{chatbot['chatbot_id']}",
                                headers={"Authorization": f"Bearer {st.session_state.access_token}"}
                            )
                            if response.status_code == 200:
                                st.success(f"Chatbot '{chatbot['chatbot_name']}' deleted successfully!")
                                st.rerun()
                            else:
                                st.error(f"Failed to delete chatbot: {response.status_code} - {response.text}")
                st.markdown("<hr style='margin-top: 0.5em;'>", unsafe_allow_html=True)
            else:
                st.write("There's nobody here...")
        else:
            st.error(f"Failed to retrieve chatbots: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Error connecting to the chatbot service: {str(e)}")

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.button("Edit Profile", on_click=open_profile_page, use_container_width=True)
    with c2:
        st.button("New Chatbot", on_click=create_new_chatbot, use_container_width=True)
    with c3:
        st.button("Logout", on_click=logout, use_container_width=True)

    st.session_state.page_load = False
