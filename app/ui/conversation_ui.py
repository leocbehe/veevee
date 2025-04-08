import streamlit as st
import requests
import datetime
import uuid

def conversation_page():
    st.write(f"Chatting with {st.session_state.chatbot_name}")
    if st.session_state.conversation_description:
        st.write(f"Topic: {st.session_state.conversation_description}")
    h1, h2 = st.columns([0.5, 0.5])
    with h1:
        if st.button("Back to Chatbot Page"):
            st.session_state.current_page = "chatbot_page"
            st.rerun()
    with h2:
        if st.button("placeholder"):
            pass

def create_conversation():
    st.session_state.conversation_id = str(uuid.uuid4())
    try:
        response = requests.post(
            f"http://localhost:8000/conversations/{st.session_state.conversation_id}",
            json={
                "user_id": st.session_state.user_id,
                "conversation_id": st.session_state.conversation_id,
                "chatbot_id": st.session_state.chatbot_id,
                "description": st.session_state.conversation_description_input,
                "start_time": datetime.datetime.now().isoformat(),
                "last_modified": datetime.datetime.now().isoformat(),
                "is_active": True
            },
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        if response.status_code == 200:
            st.success("Conversation created successfully!")
        else:
            st.error(f"Failed to create conversation: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Error connecting to the chatbot service: {str(e)}")
        return None
    return st.session_state.conversation_id