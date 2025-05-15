import streamlit as st
import numpy as np
import requests
import datetime
import uuid
import pprint
from sklearn.metrics.pairwise import cosine_similarity
from ..llm import LLMService
from ..rag_utils import text_to_embedding

def conversation_page():

    c1, c2, c3 = st.columns([1, 5, 1])
    with c1:
        if st.button("⬅️"):
            st.session_state.current_page = "chatbot_page"
            st.rerun()
    with c2:
        st.markdown(f"<h3 style='text-align: center;'>chatting with {st.session_state.chatbot_name}</h1>", unsafe_allow_html=True)    
    
    
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
    
    # main entry point for inference
    if user_input:
        handle_user_input(user_input)
        

def handle_user_input(user_input):
    """The main function to handle user input and generate chatbot responses."""
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

def add_knowledge_base_context(user_prompt_text):
    """Adds context from the knowledge base based on the user's prompt.
    This is done by checking the similarity of the user's question with the chunk embeddings
    in the knowledge base table, then adding any chunks that have relevant embeddings by 
    integrating the chunk text into the prompt."""
 
    chunks = None
    try:
        # get document ids for the current chatbot
        response = requests.get(
            f"http://localhost:8000/documents/by_chatbot/{st.session_state.chatbot_id}",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        document_ids = [d['document_id'] for d in response.json()]

        # get the document chunks associated with the document ids
        response = requests.post(
            f"http://localhost:8000/documents/document_chunks/",
            json=document_ids,
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )

        if response.status_code == 200:
            chunks = response.json()
        else:
            st.write(f"unexpected response while fetching chunks from the knowledge base: {response.status_code}")

    except Exception as e:
        st.error(f"Error connecting to FastAPI route: {e}")

    if not chunks:
        st.write("No chunks found in the knowledge base.")
        return None

    # generate embedding from user prompt
    user_prompt_embedding = text_to_embedding(user_prompt_text).reshape(1, -1)
    # sort the chunks by similarity to the user prompt
    chunks = sorted(chunks, key=lambda x: cosine_similarity(np.array(x['chunk_embedding']).reshape(1, -1), user_prompt_embedding)[0][0], reverse=True)
    for chunk in chunks:
        cos_sim = cosine_similarity(np.array(chunk['chunk_embedding']).reshape(1, -1), user_prompt_embedding)[0][0]
        print(f"cos_sim: {cos_sim}")

    print(f"text of top 5 chunks: {[chunk['chunk_text'] for chunk in chunks[:5]]}")
    context_text = [chunk['chunk_text'] for chunk in chunks[:5]]
    context_message = "Please use the following text as needed in our conversation: \n\n" + "\n\n".join(context_text)

    return context_message



def generate_response(conversation_history):
    # Initialize the LLM service    
    service = LLMService(inference_provider="ollama")
    service.stream = True

    context_message = add_knowledge_base_context(conversation_history)

    # huggingface is expecting a list with only "role" and "content" keys, so we need to remove the "conversation_id" and "timestamp" keys
    formatted_conversation_history = [
        {
            "role": message["role"],
            "content": message["message_text"]
        }
        for message in conversation_history
    ]
    user_prompt = formatted_conversation_history.pop(-1)
    formatted_conversation_history.append({"role": "user", "content": context_message})
    formatted_conversation_history.append(user_prompt)

    response_generator = service.generate(formatted_conversation_history)

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


def create_conversation():
    st.session_state.conversation_id = str(uuid.uuid4())
    try:
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
            print("Conversation created successfully")
        else:
            print(f"Failed to create conversation: {response.status_code} - {response.message_text}")
            pprint.pprint(st.session_state)
    except Exception as e:
        st.error(f"Error connecting to the chatbot service: {str(e)}")
        return None
    return st.session_state.conversation_id

def update_messages_backend(conversation_id, messages):
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