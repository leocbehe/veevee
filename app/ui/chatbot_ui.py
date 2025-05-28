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

    h1, h2, h3 = st.columns([0.3, 0.4, 0.3])
    with h1:
        if st.button("Back", use_container_width=True):
            st.session_state.current_page = "landing_page"
            st.rerun()
    with h2:
        st.button("New Conversation", on_click=open_new_conversation, use_container_width=True)
    with h3:
        if st.button("Knowledge Base", use_container_width=True):
            st.session_state.current_page = "knowledge_base_page"
            st.rerun()

    st.write(f"**Chatbot Name:** {st.session_state.chatbot_name}")
    st.write(f"**Chatbot Model Name:** {st.session_state.chatbot_model_name}")
    st.write(f"**Chatbot Description:** {st.session_state.chatbot_description}")
    st.subheader("Conversations:")

    # display all conversations for this chatbot 
    try:
        response = requests.get(
            f"http://localhost:8000/conversations/by_chatbot/{st.session_state.chatbot_id}",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        print(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            conversations = response.json()
            if conversations:
                a1,a2,a3,a4,a5 = st.columns([0.2, 0.2, 0.2, 0.2, 0.2], border=True)
                with a1:
                    st.write("Conversation ID")
                with a2:
                    st.write("Description")
                with a3:
                    st.write("Start Time")
                with a4:
                    st.write("Select")
                with a5:
                    st.write("Delete")
                for conversation in conversations:
                    c1,c2,c3,c4,c5 = st.columns([0.2, 0.2, 0.2, 0.2, 0.2], border=True)
                    with c1:
                        st.write("..."+str(conversation['conversation_id'])[-8:])
                    with c2:
                        st.write(conversation['description'])
                    with c3:
                        st.write(conversation['start_time'])
                    with c4:
                        if st.button("Select", key=f"select_{conversation['conversation_id']}"):
                            st.session_state.conversation_id = conversation['conversation_id']
                            st.session_state.conversation_description = conversation['description']
                            st.session_state.current_page = "conversation_page"
                            st.rerun()
                    with c5:
                        if st.button("Delete", key=f"delete_{conversation['conversation_id']}"):
                            response = requests.delete(
                                f"http://localhost:8000/conversations/{conversation['conversation_id']}",
                                headers={"Authorization": f"Bearer {st.session_state.access_token}"}
                            )
                            if response.status_code == 200:
                                st.success(f"Conversation {conversation['conversation_id']} deleted successfully.")
                            else:
                                st.write(f"Error deleting conversation {conversation['conversation_id']}: {response.status_code}")
                                st.write(response.status_code)
                            st.rerun()


    except Exception as e:
        st.error(f"Error connecting to the chatbot service: {str(e)}")
        print("session state:")
        pprint.pprint(st.session_state)