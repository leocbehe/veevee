import streamlit as st
import requests
import uuid
import pprint
import datetime
from .conversation_ui import create_conversation

def chatbot_page():
    # Initialize session state variables
    if "conversation_description" not in st.session_state:
        st.session_state.conversation_description = ""
    
    # Initialize conversations list if not already loaded
    if "conversations" not in st.session_state:
        st.session_state.conversations = None
        st.session_state.conversations_loaded = False

    def open_new_conversation():
        st.session_state.conversation_id = create_conversation()
        st.session_state.conversations_loaded = False  # Reset when navigating away
        st.session_state.current_page = "conversation_page"

    def navigate_back():
        st.session_state.conversations_loaded = False  # Reset when navigating away
        st.session_state.current_page = "landing_page"

    def navigate_to_knowledge_base():
        st.session_state.conversations_loaded = False  # Reset when navigating away
        st.session_state.current_page = "knowledge_base_page"

    def format_start_time(start_time_str):
        """Format the start time to a readable format: Month Day, Time"""
        try:
            # Parse the datetime string
            dt = datetime.datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            # Format as "Jan 15, 2:30 PM"
            return dt.strftime("%b %d, %I:%M %p")
        except:
            # If parsing fails, return the original string
            return start_time_str

    def delete_conversation(conversation_id):
        """Delete a conversation and update the local state"""
        try:
            response = requests.delete(
                f"http://localhost:8000/conversations/{conversation_id}",
                headers={"Authorization": f"Bearer {st.session_state.access_token}"}
            )
            if response.status_code == 200:
                # Remove the conversation from the local state instead of refetching
                st.session_state.conversations = [
                    conv for conv in st.session_state.conversations 
                    if conv['conversation_id'] != conversation_id
                ]
            else:
                st.error(f"Error deleting conversation {conversation_id}: {response.status_code}")
        except Exception as e:
            st.error(f"Error deleting conversation: {str(e)}")

    def select_conversation(conversation):
        st.session_state.conversation_id = conversation['conversation_id']
        st.session_state.conversation_description = conversation['description']
        st.session_state.conversation_start_time = conversation['start_time']
        st.session_state.conversations_loaded = False  # Reset when navigating away
        st.session_state.current_page = "conversation_page"

    h1, h2, h3 = st.columns([0.3, 0.4, 0.3])
    with h1:
        st.button("⬅️ Back", on_click=navigate_back, use_container_width=True)
    with h2:
        st.button("New Conversation", on_click=open_new_conversation, use_container_width=True)
    with h3:
        st.button("Knowledge Base", on_click=navigate_to_knowledge_base, use_container_width=True)

    st.html(f"""
    <div style='text-align:center;font-size:32px;font-weight:bold;margin-bottom:0px;'>{st.session_state.chatbot_name}</div>
    <div style='text-align:center;font-size:16px;font-family:Consolas;margin-top:0px;'>Model Name: {st.session_state.chatbot_model_name}</div>
    <div style='text-align:center;font-size:16px;font-family:Consolas;margin-top:0px;'>Provider: {st.session_state.chatbot_config['inference_provider']}</div>
    <hr style='margin-top:16px;'>
    """)
    st.html("<div style='text-align: center; font-size: 24px; font-weight: bold;'>Description</div>")
    st.html(f"<div style='text-align:center;font-size:16px;margin-top:0px;'>{st.session_state.chatbot_description}</div>")
    st.html("<hr>")
    st.html("<div style='text-align: center; font-size: 24px; font-weight: bold;'>Conversations</div>")

    # Only fetch conversations if they haven't been loaded yet
    if not st.session_state.conversations_loaded:
        try:
            response = requests.get(
                f"http://localhost:8000/conversations/by_chatbot/{st.session_state.chatbot_id}",
                headers={"Authorization": f"Bearer {st.session_state.access_token}"}
            )
            if response.status_code == 200:
                st.session_state.conversations = response.json()
                st.session_state.conversations_loaded = True
            else:
                st.error(f"Error fetching conversations: {response.status_code}")
                st.session_state.conversations = []
        except Exception as e:
            st.error(f"Error connecting to the chatbot service: {str(e)}")
            st.session_state.conversations = []

    # Display conversations
    if st.session_state.conversations:
        for conversation in st.session_state.conversations:
            st.divider()
            c1,c2,c3,c4 = st.columns([0.2, 0.3, 0.3, 0.2], border=False)
            with c1:
                st.html(f"<div style='text-align: center;'>{conversation['description']}</div>")
            with c2:
                st.html(f"<div style='text-align: center;'>Created {format_start_time(conversation['start_time'])}</div>")
            with c3:
                if st.button("Select", key=f"select_{conversation['conversation_id']}", use_container_width=True):
                    select_conversation(conversation)
            with c4:
                if st.button("Delete", key=f"delete_{conversation['conversation_id']}", use_container_width=True):
                    with st.spinner("Deleting conversation..."):
                        delete_conversation(conversation['conversation_id'])
                    st.rerun()
    else:
        st.write("<div style='text-align:center;'>No conversations yet...</div>", unsafe_allow_html=True)

    st.session_state.page_load = False