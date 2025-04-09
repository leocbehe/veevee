import streamlit as st
import requests
import datetime
import uuid
import pprint

def conversation_page():
    if st.sidebar.button("Back to Chatbot Page"):
        st.session_state.current_page = "chatbot_page"
        st.rerun()
    st.sidebar.write(f"Chatting with {st.session_state.chatbot_name}")
    if st.session_state.conversation_description:
        st.sidebar.write(f"Topic: {st.session_state.conversation_description}")
    
    # Main conversation dialogue box
    st.title(f"Conversation with {st.session_state.chatbot_name}")
    
    # Initialize conversation history in session state if not exists
    if 'conversation_messages' not in st.session_state:
        st.session_state.conversation_messages = []

    try:
        response = requests.get(
            f"http://localhost:8000/conversations/{st.session_state.conversation_id}",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        if response.status_code == 200:
            conversation_data = response.json()
            st.session_state.conversation_messages = conversation_data['messages']
        else:
            st.write(f"Error fetching conversation data: {response.status_code}")
    except Exception as e:
        st.write(f"Error fetching conversation data: {e}")
    
    # Display conversation history
    for message in st.session_state.conversation_messages:
        if message['sender'] == 'user':
            st.chat_message("user").write(message['message_text'])
        else:
            st.chat_message("assistant").write(message['message_text'])
    
    # Input for new message
    user_input = st.chat_input("Type your message...")
    
    if user_input:
        # update messages on the frontend
        st.session_state.conversation_messages.append({
            "role": "user", 
            "message_text": user_input,
        })
        
        # TODO: Implement actual API call to get chatbot response
        # For now, using a placeholder response
        chatbot_response = f"Response to: {user_input}"
        
        # Add chatbot response to conversation history
        st.session_state.conversation_messages.append({
            "role": "assistant", 
            "message_text": chatbot_response,
        })

        # update messages on the backend
        update_messages_backend(st.session_state.conversation_id, st.session_state.conversation_messages)
        
        # Rerun to refresh the page and show new messages
        st.rerun()
    

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
            st.error(f"Failed to create conversation: {response.status_code} - {response.message_text}")
    except Exception as e:
        st.error(f"Error connecting to the chatbot service: {str(e)}")
        return None
    return st.session_state.conversation_id

def update_messages_backend(conversation_id, messages):
    print("Updating messages...")
    pprint.pprint(messages)
    try:
        response = requests.put(
            f"http://localhost:8000/conversations/",
            json={
                "conversation_id": conversation_id,
                "messages": messages
            },
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        if response.status_code == 200:
            st.success("Messages updated successfully!")
        else:
            st.error(f"Failed to update messages: {response.status_code} - {response.message_text}")
    except Exception as e:
        st.error(f"Error connecting to the chatbot service: {str(e)}")