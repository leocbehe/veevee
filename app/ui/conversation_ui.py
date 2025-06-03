import streamlit as st
import numpy as np
import requests
import datetime
import uuid
from ..config import settings
from ..schemas import DocumentChunk
import pprint
from sklearn.metrics.pairwise import cosine_similarity
from ..llm import LLMService
from ..rag_utils import text_to_embedding, get_embedded_chunks

def create_sidebar():
    """
    Creates a sidebar with navigation controls and recent message history.
    """
    with st.sidebar:
        st.markdown("### Navigation")
        if st.button("⬅️ Back to Chatbot", use_container_width=True):
            st.session_state.current_page = "chatbot_page"
            st.session_state.conversation_messages = []
            st.rerun()
        
        st.divider()
        
        # Add remember conversation toggle
        if 'conversation_messages' in st.session_state and st.session_state.conversation_messages:
            # Initialize the remembered state if not exists
            if 'remember_conversation' not in st.session_state:
                st.session_state.remember_conversation = False
            
            remembered = st.checkbox(
                "💾 Remember this conversation", 
                value=st.session_state.remember_conversation,
                help="Toggle to remember/forget this conversation"
            )
            
            # Update session state if checkbox value changed
            if remembered != st.session_state.remember_conversation:
                st.session_state.remember_conversation = remembered
        
        st.divider()
        
        # Optional: Add some conversation info in the sidebar
        if 'chatbot_name' in st.session_state:
            st.markdown(f"**Chatbot:** {st.session_state.chatbot_name}")
        
        if 'conversation_messages' in st.session_state:
            message_count = len(st.session_state.conversation_messages)
            st.markdown(f"**Messages:** {message_count}")
            
            # Show recent message history
            if message_count > 0:
                st.markdown("**Recent Messages:**")
                # Get the last 10 messages
                recent_messages = st.session_state.conversation_messages[-10:]
                
                for i, message in enumerate(recent_messages):
                    # Truncate message to first 20 characters
                    truncated_text = message['message_text'][:20] + "..." if len(message['message_text']) > 20 else message['message_text']
                    
                    # Use different styling for user vs assistant
                    if message['role'] == 'user':
                        st.markdown(f"🙋 {truncated_text}")
                    elif message['role'] == 'assistant':
                        st.markdown(f"🤖 {truncated_text}")
                    elif message['role'] == 'system':
                        st.markdown(f"💿 {truncated_text}")

def store_conversation_in_knowledge_base(conversation_id, conversation_messages):
    """
    Convert the conversation into a knowledge base item that can be retrieved for context.
    """
    conversation_document_id = uuid.uuid5(uuid.NAMESPACE_URL, conversation_id)
    for message in conversation_messages:
        if message['role'] == 'user':
            chunk_metadata = {
                "context": "The following is a statement made by the user during a conversation with you, the assistant: ",
            }
        elif message['role'] == 'assistant':
            chunk_metadata = {
                "context": "The following is a statement made by you, the assistant, during a conversation with the user: ",
            }
        elif message['role'] == 'system':
            chunk_metadata = {
                "context": "The following is information that you should incorporate as part of your background knowledge only if it is relevant to the conversation: ",
            }
        embedded_chunks = get_embedded_chunks(message['message_text'], conversation_document_id, chunk_metadata)

    # combine the messages into a single raw text string
    conversation_text = "\n\n".join([message['role']+": "+message['message_text'] for message in conversation_messages])
    
    # retrieve all documents associated with this chatbot ID to see if the conversation has already been stored
    conversation_document_exists = False
    try:
        response = requests.get(
            f"http://localhost:8000/documents/by_chatbot/{st.session_state.chatbot_id}",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )        
        response.raise_for_status()
        documents = response.json()
        for document in documents:
            if document['document_id'] == conversation_document_id:
                conversation_document_exists = True
    except Exception as e:
        print(f"Error fetching documents by chatbot ID: {e}")
        return
    
    
    # if the conversation has not been stored, create a knowledgebasedocument using the conversation data
    if not conversation_document_exists:
        try:
            response = requests.post(
                f"http://localhost:8000/documents",
                headers={"Authorization": f"Bearer {st.session_state.access_token}"},
                json={
                    "document_id": str(conversation_document_id),
                    "chatbot_id": st.session_state.chatbot_id,
                    "file_name": f"conversation_{conversation_id[-6:]}",
                    "context": st.session_state.conversation_description,
                    "created_at": st.session_state.conversation_start_time,
                    "raw_text": conversation_text,
                    "chunks": embedded_chunks,
                }
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Error storing conversation in knowledge base: {e}")

    # if the conversation has been stored, update the knowledgebasedocument with the new conversation data
    else:
        try:
            response = requests.put(
                f"http://localhost:8000/documents/{conversation_document_id}",
                headers={"Authorization": f"Bearer {st.session_state.access_token}"},
                json={
                    "document_id": conversation_document_id,
                    "chatbot_id": st.session_state.chatbot_id,
                    "file_name": f"conversation_{conversation_id[-6:]}",
                    "context": st.session_state.conversation_description,
                    "created_at": st.session_state.conversation_start_time,
                    "raw_text": conversation_text,
                    "chunks": embedded_chunks,
                }
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Error updating conversation in knowledge base: {e}")

def retrieve_conversation_messages(conversation_id):
    try:
        response = requests.get(
            f"http://localhost:8000/conversations/{st.session_state.conversation_id}",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        if response.status_code == 200:
            conversation_data = response.json()
            st.session_state.conversation_messages = conversation_data['messages']
            # Initialize the remembered state from backend data
            st.session_state.remember_conversation = conversation_data.get('is_remembered', False)
        else:
            st.write(f"Error fetching conversation data: {response.status_code}")
    except Exception as e:
        st.write(f"Error fetching conversation data: {e}")

def conversation_page():
    # Retrieve conversation messages
    retrieve_conversation_messages(st.session_state.conversation_id)

    # Create the sidebar
    create_sidebar()
    
    # Simple header without sticky positioning
    st.markdown(f"<h2 style='text-align: center;'>Chatting with {st.session_state.chatbot_name}</h2>", unsafe_allow_html=True)
    st.divider()
        
    # Display conversation history
    for message in st.session_state.conversation_messages:
        if message['role'] == 'user':
            st.chat_message("user").write(message['message_text'])
        elif message['role'] == 'assistant':
            st.chat_message("assistant").write(message['message_text'])
        elif message['role'] == 'system':
            st.chat_message("system").write(message['message_text'])
    
    # Input for new message
    user_input = st.chat_input("Type your message...")

    
    # main entry point for inference
    if user_input:
        handle_user_input(user_input)

    st.session_state.page_load = False

def generate_knowledge_base_context(user_prompt_text):
    """Generates context from the knowledge base based on the user's prompt.
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
        print("No chunks found in the knowledge base.")
        return None

    # generate embedding from user prompt
    user_prompt_embedding = text_to_embedding(user_prompt_text['content']).reshape(1, -1)
    # sort the chunks by similarity to the user prompt
    chunks = sorted(chunks, key=lambda x: cosine_similarity(np.array(x['chunk_embedding']).reshape(1, -1), user_prompt_embedding)[0][0], reverse=True)

    context_text = []
    # look through top N chunks most similar to the user prompt. if the cosine similarity is > 0.4, add the chunk to the context.
    for chunk in chunks[:settings.num_context_chunks]:
        print(f"> ANALYZING CHUNK: {chunk['chunk_text']}")
        similarity = cosine_similarity(np.array(chunk['chunk_embedding']).reshape(1, -1), user_prompt_embedding)[0][0]
        print(f" > SIMILARITY: {similarity}")
        if similarity > 0.4:
            print("> Adding chunk to context...")
            context_text.append(chunk['chunk_text'])
        else:
            print("> Skipping chunk...")

    context_message = "\n\n".join(context_text)

    return context_message

def add_context_to_conversation(conversation_history, context_message, use_system_role=False):
    """Adds the specified context message to the conversation history based on the model's formatting requirements."""
    if use_system_role:
        # create a system message that includes the given context message and explains to the system that it should use the context as necessary
        full_system_prompt = f"You are a helpful assistant. When responding to the user, you should refer to the following context as necessary to help you answer the user's question. \
            START OF CONTEXT:\n\n{context_message}\n\nEND OF CONTEXT.\n\nIf the context is not necessary to answer the user's question, you should ignore the context. If the context is necessary, \
            incorporate it into your response in a clear and natural way while still using your own words. In all cases, do not explicitly state that you are using the context."
        # prepend the system message to the conversation history
        conversation_history.insert(0, {"role": "system", "content": full_system_prompt})
    else:
        # create a user message that includes the given context message
        full_context_prompt = f"Please respond to my next message by referring to this context. START OF CONTEXT:\n\n{context_message}\n\nEND OF CONTEXT\n\nNow, please respond to my \
            next message by using that context as necessary. If the context is not necessary, you should ignore the context and answer as normal. Either way, respond without explicitly \
            mentioning the context."
        # Add the context message as a user message
        conversation_history.append({"role": "user", "content": full_context_prompt})


def generate_response(conversation_history):
    # Initialize the LLM service
    service = LLMService(model_name=st.session_state.chatbot_model_name, **st.session_state.chatbot_config)

    # huggingface is expecting a list with only "role" and "content" keys, so we need to remove the "conversation_id" and "timestamp" keys
    formatted_conversation_history = [
        {
            "role": message["role"],
            "content": message["message_text"]
        }
        for message in conversation_history
    ]

    # remove the user prompt from the conversation history and use it to generate the context message.
    # then add the context message and the user prompt back into the conversation history (in that order)
    user_prompt = formatted_conversation_history.pop(-1)

    context_message = generate_knowledge_base_context(user_prompt)
    if context_message:
        add_context_to_conversation(formatted_conversation_history, context_message, use_system_role=service.system_context_allowed)
    elif service.system_context_allowed:
        formatted_conversation_history.insert(0, {"role": "system", "content": "You are a helpful assistant."})
    formatted_conversation_history.append(user_prompt)

    response_generator = service.generate(formatted_conversation_history)
    if not response_generator:
        print("Failed to initialize the LLM service properly. Please check your configuration.")
        return None
    else:
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
                # print(chunk.choices[0].delta.content)
                full_response += chunk.choices[0].delta.content if chunk.choices[0].delta.content else ""
                response_placeholder.markdown(full_response + "▌")  # Display the updated response with a cursor
            response_placeholder.markdown(full_response)  # Final response without cursor
            return full_response


def create_conversation():
    st.session_state.conversation_id = str(uuid.uuid4())
    st.session_state.conversation_start_time = datetime.datetime.now().isoformat()
    st.session_state.last_modified = datetime.datetime.now().isoformat()
    try:
        response = requests.post(
            f"http://localhost:8000/conversations/",
            json={
                "user_id": st.session_state.user_id,
                "conversation_id": st.session_state.conversation_id,
                "chatbot_id": st.session_state.chatbot_id,
                "description": "New Conversation",
                "start_time": st.session_state.conversation_start_time,
                "last_modified": st.session_state.last_modified,
                "is_active": True,
                "is_remembered": False,
            },
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        if response.status_code == 200:
            print("Conversation created successfully")
        else:
            print(f"Failed to create conversation: {response.status_code} - {response.message_text}")
    except Exception as e:
        st.error(f"Error connecting to the chatbot service: {str(e)}")
        return None
    return st.session_state.conversation_id

def update_messages_backend(conversation_id, messages):
    # Get the remembered state, defaulting to False if not set
    is_remembered = st.session_state.get('remember_conversation', False)
    
    try:
        response = requests.put(
            f"http://localhost:8000/conversations/",
            json={
                "conversation_id": conversation_id,
                "messages": messages,
                "last_modified": datetime.datetime.now().isoformat(),
                "description": st.session_state.conversation_description if st.session_state.conversation_description else "New Conversation",
                "is_remembered": is_remembered,
            },
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        if not response.status_code == 200:
            st.error(f"Failed to update messages: {response.status_code} - {response.message_text}")
    except Exception as e:
        st.error(f"Error connecting to the chatbot service: {str(e)}")

def handle_user_input(user_input):
    """All the logic for the chatbot response should be in this function. The end of this function should mark the point of the 
    application returning to a standby state."""
    if not st.session_state.conversation_messages:
        st.session_state.conversation_description = user_input[:30]+"..." if len(user_input) > 30 else user_input
    st.chat_message("user").write(user_input)
    st.session_state.conversation_messages.append({
        "role": "user", 
        "message_text": user_input,
        "conversation_id": st.session_state.conversation_id,
        "timestamp": datetime.datetime.now().isoformat()
    })

    with st.spinner("Generating response..."):
        # Generate chatbot response
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
        # store the conversation in the knowledge base if the feature is enabled
        if st.session_state.remember_conversation:
            store_conversation_in_knowledge_base(st.session_state.conversation_id, st.session_state.conversation_messages)
        # Rerun to refresh the page and show new messages
        st.rerun()
