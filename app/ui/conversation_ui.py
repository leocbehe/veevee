import streamlit as st
import requests
import datetime
import uuid
import pprint
from huggingface_hub import ChatCompletionOutput
from typing import List
from ..llm import LLMService
from ..config import settings

def conversation_page():
    if st.sidebar.button("Back to Chatbot Page"):
        st.session_state.current_page = "chatbot_page"
        st.rerun()
    st.sidebar.write(f"Chatting with {st.session_state.chatbot_name}")
    if st.session_state.conversation_description:
        st.sidebar.write(f"Topic: {st.session_state.conversation_description}")
    
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
        if message['role'] == 'user':
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
            "conversation_id": st.session_state.conversation_id,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        # Generate chatbot response
        print(f"Generating response for user input: {user_input}")
        response_text = generate_response(st.session_state.conversation_messages)

        if not response_text:
            st.error("Failed to generate response from the chatbot.")
            return None
        
        # Add chatbot response to conversation history
        st.session_state.conversation_messages.append({
            "role": "assistant", 
            "message_text": response_text,
            "conversation_id": st.session_state.conversation_id,
            "timestamp": datetime.datetime.now().isoformat()
        })

        # update messages on the backend
        update_messages_backend(st.session_state.conversation_id, st.session_state.conversation_messages)
        
        # Rerun to refresh the page and show new messages
        st.rerun()

def generate_response(conversation_history):
    # Initialize the LLM service    
    service = LLMService(inference_provider="ollama")
    # huggingface is expecting a list with only "role" and "content" keys, so we need to remove the "conversation_id" and "timestamp" keys
    formatted_conversation_history = [
        {
            "role": message["role"],
            "content": message["message_text"]
        }
        for message in conversation_history
    ]

    response_generator = service.generate(formatted_conversation_history, stream=True)

    full_response = ""
    response_placeholder = st.empty() 

    if service.inference_provider == "ollama":
        for chunk in response_generator:
            full_response += chunk.message.content
            response_placeholder.markdown(full_response + "▌")  # Display the updated response with a cursor
        response_placeholder.markdown(full_response)  # Final response without cursor
        return full_response
    else:
        for chunk in response_generator:
            full_response += chunk.choices[0].delta.content if chunk.choices[0].delta.content else ""
            response_placeholder.markdown(full_response + "▌")  # Display the updated response with a cursor
        response_placeholder.markdown(full_response)  # Final response without cursor
        return full_response


    # response_text = response.choices[0].message.content if service.inference_provider == "huggingface" else response.message.content
    # return response_text


def create_conversation():
    st.session_state.conversation_id = str(uuid.uuid4())
    try:
        print(f"Creating conversation with ID: {st.session_state.conversation_id}")
        response = requests.post(
            f"http://localhost:8000/conversations/",
            json={
                "user_id": st.session_state.user_id,
                "conversation_id": st.session_state.conversation_id,
                "chatbot_id": st.session_state.chatbot_id,
                "description": st.session_state.new_conversation_description if st.session_state.new_conversation_description else "New Conversation",
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
            print(f"Failed to create conversation: {response.status_code} - {response.message_text}")
            pprint.pprint(st.session_state)
    except Exception as e:
        st.error(f"Error connecting to the chatbot service: {str(e)}")
        return None
    return st.session_state.conversation_id

def update_messages_backend(conversation_id, messages):
    pprint.pprint(messages)
    try:
        response = requests.put(
            f"http://localhost:8000/conversations/",
            json={
                "conversation_id": conversation_id,
                "messages": messages,
                "last_modified": datetime.datetime.now().isoformat()
            },
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        if not response.status_code == 200:
            st.error(f"Failed to update messages: {response.status_code} - {response.message_text}")
    except Exception as e:
        st.error(f"Error connecting to the chatbot service: {str(e)}")