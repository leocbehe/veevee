import streamlit as st
import requests
from datetime import datetime
import uuid

def fetch_chatbot_data(chatbot_id, access_token):
    """
    Fetch chatbot data from the API.
    
    Args:
        chatbot_id: ID of the chatbot to fetch
        access_token: Authorization token
        
    Returns:
        dict: Chatbot data or None if error
    """
    try:
        response = requests.get(
            f"http://localhost:8000/chatbots/{chatbot_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code != 200:
            print(f"No associated chatbot found; chatbot creation may not have executed properly. \
                  {response.status_code} - {response.text}")
            return None
            
        return response.json()
    except Exception as e:
        st.error(f"Error connecting to the chatbot service: {str(e)}")
        return None

def display_chatbot_info(chatbot_data):
    """
    Display non-editable chatbot information.
    
    Args:
        chatbot_data: Dictionary containing chatbot information
    """
    # Center the main title
    st.markdown("<h1 style='text-align: center;'>Chatbot Details</h1>", unsafe_allow_html=True)
    
    # Use full width for the subheaders with center-justified text
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h3 style='text-align: center;'>Chatbot ID</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>{chatbot_data.get('chatbot_id', 'N/A')}</p>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align: center;'>Owner ID</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>{chatbot_data.get('owner_id', 'N/A')}</p>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<h3 style='text-align: center;'>Created At</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>{chatbot_data.get('created_at', 'N/A')}</p>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align: center;'>Status</h3>", unsafe_allow_html=True)
        status = "Active" if chatbot_data.get("is_active", False) else "Inactive"
        st.markdown(f"<p style='text-align: center;'>{status}</p>", unsafe_allow_html=True)

def render_edit_form(chatbot_data):
    """
    Render the editable form for chatbot configuration.
    
    Args:
        chatbot_data: Dictionary containing current chatbot data
        
    Returns:
        tuple: (back_button, submit_button, form_data)
    """
    st.subheader("Editable Information")
    
    with st.form(key="edit_chatbot_form"):
        chatbot_name = st.text_input("Chatbot Name", 
                                   value=chatbot_data.get("chatbot_name", ""),
                                   help="The personalized chatbot name. Has no effect on the model.")
        description = st.text_area("Description", 
                                 value=chatbot_data.get("description", ""),
                                 help="A description of the chatbot. Has no effect on the model.")
        model_name = st.text_input("Model Name", 
                                 value=chatbot_data.get("model_name", ""),
                                 help="Can be an ollama model name or a Hugging Face model name. Must be a valid model name for the specified inference provider.")
        
        # Configuration section
        st.subheader("Configuration (JSON)")
        inference_providers = ["ollama", "huggingface"]
        current_provider = chatbot_data.get("configuration", {}).get("inference_provider", "ollama")
        provider_index = 0 if current_provider == "ollama" else 1
        
        inference_provider = st.selectbox("Inference Provider", 
                    options=inference_providers,
                    index=provider_index,
                    help="The service or framework used for inference such as ollama or huggingface; i.e. where the model is \
                        actually being run")
        inference_url = st.text_input("Inference URL", 
                                    value=chatbot_data.get("configuration", {}).get("inference_url", ""),
                                    help="URL for the inference API endpoint")
        max_response_tokens = st.number_input("Max Response Tokens", min_value=1, max_value=50000, step=1, value=chatbot_data.get("configuration", {}).get("max_response_tokens", 1000), 
                                     help="The maximum number of tokens that the model can produce in a single response.")
        temperature = st.slider("Temperature", 
                               min_value=0.0, max_value=2.0, step=0.1, 
                               value=chatbot_data.get("configuration", {}).get("temperature", 0.7))
        stream = st.checkbox("Stream Responses", 
                           value=chatbot_data.get("configuration", {}).get("stream", True),
                           help="Whether to stream responses from the model or wait until the entire response is generated.")
        system_context_allowed = st.checkbox("System Context Allowed", value=chatbot_data.get("configuration", {}).get("system_context_allowed", False),
                                             help="""Only enable this if the model being used supports the "system" role in its prompt format. If enabled, any additional context 
                                             retrieved from the chatbot's knowledge base will be added to a "system" message at the beginning of the conversation. Otherwise, the context
                                             will just be added as an additional user message. Providing the context as a system message is generally more effective, as the system role
                                             is specifically designed to provide background context and behavioral instructions to the model.""")
        
        is_active = st.checkbox("Active", value=chatbot_data.get("is_active", True))
        
        # Form buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            back_button = st.form_submit_button("Back to Chatbots", use_container_width=True)

        with col3:    
            submit_button = st.form_submit_button(label="Save Changes", use_container_width=True)
    
    # Return form data
    form_data = {
        "chatbot_name": chatbot_name,
        "description": description,
        "model_name": model_name,
        "configuration": {
            "inference_provider": inference_provider,
            "inference_url": inference_url,
            "temperature": temperature,
            "stream": stream,
            "max_response_tokens": max_response_tokens,
            "system_context_allowed": system_context_allowed,
        },
        "is_active": is_active
    }
    
    return back_button, submit_button, form_data

def update_chatbot(chatbot_id, access_token, update_data):
    """
    Send PATCH request to update chatbot.
    
    Args:
        chatbot_id: ID of the chatbot to update
        access_token: Authorization token
        update_data: Dictionary containing update data
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print("SENDING UPDATE REQUEST")
        print(f"chatbot name: {update_data.get('chatbot_name')}")
        
        response = requests.patch(
            f"http://localhost:8000/chatbots/{chatbot_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code == 200:
            st.success("Chatbot updated successfully!")
            print("Chatbot updated successfully!")
            return True
        else:
            st.error(f"Failed to update chatbot: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"Error updating chatbot: {str(e)}")
        return False

def refresh_cached_data(chatbot_id, access_token, cache_key):
    """
    Refresh cached chatbot data after successful update.
    
    Args:
        chatbot_id: ID of the chatbot
        access_token: Authorization token
        cache_key: Session state cache key
    """
    try:
        refresh_response = requests.get(
            f"http://localhost:8000/chatbots/{chatbot_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if refresh_response.status_code == 200:
            st.session_state[cache_key] = refresh_response.json()
            st.rerun()
    except Exception as e:
        print(f"Error refreshing data after update: {str(e)}")

def handle_navigation_back(cache_key):
    """
    Handle navigation back to chatbots list.
    
    Args:
        cache_key: Session state cache key to clear
    """
    if cache_key in st.session_state:
        del st.session_state[cache_key]
    st.session_state.current_page = "landing_page"
    st.rerun()

def chatbot_edit_page():
    """
    Main function for the chatbot edit page.
    Orchestrates the entire page flow.
    """
    # Check if chatbot_id exists in session state
    if "chatbot_id" not in st.session_state:
        st.error("No chatbot selected for editing")
        if st.button("Return to Chatbots"):
            st.session_state.current_page = "landing_page"
            st.rerun()
        return
    
    # Set up caching
    cache_key = f"chatbot_data_{st.session_state.chatbot_id}"
    
    # Fetch chatbot data if not cached
    if cache_key not in st.session_state:
        chatbot_data = fetch_chatbot_data(st.session_state.chatbot_id, st.session_state.access_token)
        if chatbot_data is None:
            if st.button("Return to Chatbots"):
                st.session_state.current_page = "landing_page"
                st.rerun()
            return
        st.session_state[cache_key] = chatbot_data
    
    chatbot_data = st.session_state[cache_key]
    
    # Display chatbot information
    display_chatbot_info(chatbot_data)
    
    # Render edit form
    back_button, submit_button, form_data = render_edit_form(chatbot_data)
    
    # Handle form submissions
    if back_button:
        handle_navigation_back(cache_key)
    
    if submit_button:
        print("SUBMIT BUTTON PRESSED")
        
        # Prepare update data (exclude is_active from the update for now)
        update_data = {
            "chatbot_name": form_data["chatbot_name"],
            "description": form_data["description"],
            "model_name": form_data["model_name"],
            "configuration": form_data["configuration"],
        }
        
        # Update chatbot
        success = update_chatbot(st.session_state.chatbot_id, st.session_state.access_token, update_data)
        
        # Refresh data if successful
        if success:
            refresh_cached_data(st.session_state.chatbot_id, st.session_state.access_token, cache_key)