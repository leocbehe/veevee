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

    def open_new_conversation():
        st.session_state.conversation_id = create_conversation()
        st.session_state.current_page = "conversation_page"

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

    h1, h2, h3 = st.columns([0.3, 0.4, 0.3])
    with h1:
        if st.button("⬅️ Back", use_container_width=True):
            st.session_state.current_page = "landing_page"
            st.rerun()
    with h2:
        st.button("New Conversation", on_click=open_new_conversation, use_container_width=True)
    with h3:
        if st.button("Knowledge Base", use_container_width=True):
            st.session_state.current_page = "knowledge_base_page"
            st.rerun()

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

    # display all conversations for this chatbot 
    try:
        response = requests.get(
            f"http://localhost:8000/conversations/by_chatbot/{st.session_state.chatbot_id}",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        if response.status_code == 200:
            conversations = response.json()
            if conversations:
                for conversation in conversations:
                    st.divider()
                    c1,c2,c3,c4 = st.columns([0.2, 0.3, 0.3, 0.2], border=False)
                    with c1:
                        st.html(f"<div style='text-align: center;'>{conversation['description']}</div>")
                    with c2:
                        st.html(f"<div style='text-align: center;'>Created {format_start_time(conversation['start_time'])}</div>")
                    with c3:
                        if st.button("Select", key=f"select_{conversation['conversation_id']}", use_container_width=True):
                            st.session_state.conversation_id = conversation['conversation_id']
                            st.session_state.conversation_description = conversation['description']
                            st.session_state.conversation_start_time = conversation['start_time']
                            st.session_state.current_page = "conversation_page"
                            st.rerun()
                    with c4:
                        if st.button("Delete", key=f"delete_{conversation['conversation_id']}", use_container_width=True):
                            response = requests.delete(
                                f"http://localhost:8000/conversations/{conversation['conversation_id']}",
                                headers={"Authorization": f"Bearer {st.session_state.access_token}"}
                            )
                            if response.status_code == 200:
                                st.success(f"Conversation {conversation['conversation_id']} deleted successfully.")
                            else:
                                st.write(f"Error deleting conversation {conversation['conversation_id']}: {response.status_code}")
                            st.rerun()
            else:
                st.write("<div style='text-align:center;'>No conversations yet...</div>", unsafe_allow_html=True)


    except Exception as e:
        st.error(f"Error connecting to the chatbot service: {str(e)}")
        print("session state:")
        pprint.pprint(st.session_state)

    st.session_state.page_load = False