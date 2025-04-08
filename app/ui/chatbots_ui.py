import streamlit as st
import requests
import uuid
import datetime
from .conversation import create_conversation

def chatbot_page():
    h1, h2, h3 = st.columns([0.3, 0.4, 0.3])
    with h1:
        if st.button("Back to Landing Page"):
            st.session_state.current_page = "landing_page"
            st.rerun()
    with h2:
        if st.button("New Conversation"):
            st.session_state.conversation_id = create_conversation()
            st.session_state.current_page = "conversation_page"
            st.rerun()
    with h3:
        pass
    st.write(f"**Chatbot Name:** {st.session_state.chatbot_name}")
    st.write(f"**Chatbot Description:** {st.session_state.chatbot_description}")
    st.write(f"**Chatbot Model Path:** {st.session_state.chatbot_model_path}")

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
                a1,a2,a3,a4 = st.columns([0.25, 0.25, 0.25, 0.25], border=True)
                with a1:
                    st.write("Conversation ID")
                with a2:
                    st.write("Description")
                with a3:
                    st.write("Start Time")
                with a4:
                    st.write("Select")
                for conversation in conversations:
                    c1,c2,c3,c4 = st.columns([0.25, 0.25, 0.25, 0.25], border=True)
                    with c1:
                        st.write("..."+str(conversation['conversation_id'])[-8:])
                    with c2:
                        st.write(conversation['description'])
                    with c3:
                        st.write(conversation['start_time'])
                    with c4:
                        if st.button("Select", key=conversation['conversation_id']):
                            st.session_state.conversation_id = "..."+str(conversation['conversation_id'])[-8:]
                            st.session_state.conversation_description = conversation['description']
                            st.session_state.current_page = "conversation_page"
                            st.rerun()

                st.subheader("Conversations:")

    except Exception as e:
        st.error(f"Error connecting to the chatbot service: {str(e)}")

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