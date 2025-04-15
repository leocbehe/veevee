import streamlit as st
import requests
import uuid
import pprint
import datetime
from .conversation_ui import create_conversation

def chatbot_page():
    # Initialize session state variables
    if "show_conversation_form" not in st.session_state:
        st.session_state.show_conversation_form = False
    if "new_conv_desc" not in st.session_state:
        st.session_state.new_conv_desc = ""

    def open_conversation_form():
        st.session_state.show_conversation_form = True

    def close_conversation_form():
        st.session_state.show_conversation_form = False

    def create_new_conversation():
        st.session_state.conversation_description = st.session_state.new_conv_desc
        create_conversation()
        print(f"Conversation ID: {st.session_state.conversation_id}")
        st.session_state.current_page = "conversation_page"
        close_conversation_form()

    h1, h2, h3 = st.columns([0.3, 0.3, 0.4])
    with h1:
        if st.button("Back to Landing Page"):
            st.session_state.current_page = "landing_page"
            st.rerun()
    with h2:
        st.button("New Conversation", on_click=open_conversation_form)

    # Conversation form (modal)
    if st.session_state.show_conversation_form:
        with st.sidebar.container():
            st.sidebar.subheader("Create New Conversation")
            st.session_state.new_conv_desc = st.sidebar.text_input("New Conversation Description", key="new_conversation_description", value=st.session_state.new_conv_desc)

            col1, col2 = st.sidebar.columns(2)
            with col1:
                if st.sidebar.button("Save", on_click=create_new_conversation):
                    pass
            with col2:
                st.sidebar.button("Cancel", on_click=close_conversation_form)
    with h3:
        pass

    st.write(f"**Chatbot Name:** {st.session_state.chatbot_name}")
    st.write(f"**Chatbot Description:** {st.session_state.chatbot_description}")
    st.write(f"**Chatbot Model Path:** {st.session_state.chatbot_model_path}")
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
                            print(f"delete command: http://localhost:8000/conversations/{conversation['conversation_id']}"),
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