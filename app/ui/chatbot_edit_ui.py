import streamlit as st
import requests
from datetime import datetime
import uuid

def chatbot_edit_page():
    """
    Streamlit page for editing chatbot details.
    Allows users to modify chatbot properties and save changes.
    """
    # Check if chatbot_id exists in session state
    if "chatbot_id" not in st.session_state:
        st.error("No chatbot selected for editing")
        if st.button("Return to Chatbots"):
            st.session_state.current_page = "landing_page"
            st.rerun()
        return
    
    # Fetch current chatbot data
    try:
        response = requests.get(
            f"http://localhost:8000/chatbots/{st.session_state.chatbot_id}",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        
        if response.status_code != 200:
            print(f"No associated chatbot found; chatbot creation may not have executed properly. \
                  {response.status_code} - {response.text}")
            if st.button("Return to Chatbots"):
                st.session_state.current_page = "landing_page"
                st.rerun()
            return
            
        chatbot_data = response.json()
    except Exception as e:
        st.error(f"Error connecting to the chatbot service: {str(e)}")
        if st.button("Return to Chatbots"):
            st.session_state.current_page = "landing_page"
            st.rerun()
        return
    
    # Page header
    st.title("Chatbot Details")
    
    # Display non-editable fields
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Chatbot ID")
        st.text(chatbot_data.get("chatbot_id", "N/A"))
        
        st.subheader("Owner ID")
        st.text(chatbot_data.get("owner_id", "N/A"))
    
    with col2:
        st.subheader("Created At")
        st.text(chatbot_data.get("created_at", "N/A"))
        
        st.subheader("Status")
        status = "Active" if chatbot_data.get("is_active", False) else "Inactive"
        st.text(status)
    
    # Editable fields
    st.subheader("Editable Information")
    
    # Initialize session state for form values if not already present
    st.session_state.edit_chatbot_name = chatbot_data.get("chatbot_name", "")
    st.session_state.edit_description = chatbot_data.get("description", "")
    st.session_state.edit_model_name = chatbot_data.get("model_name", "")
    st.session_state.edit_configuration = chatbot_data.get("configuration", {})
    st.session_state.edit_is_active = chatbot_data.get("is_active", True)
    st.session_state.edit_inference_provider = chatbot_data.get("configuration", {}).get("inference_provider", "")
    st.session_state.edit_inference_url = chatbot_data.get("configuration", {}).get("inference_url", "")
    st.session_state.temperature = chatbot_data.get("configuration", {}).get("temperature", 0.7)
    st.session_state.stream = chatbot_data.get("configuration", {}).get("stream", True)
    
    # Form for editing chatbot
    with st.form(key="edit_chatbot_form"):
        st.text_input("Chatbot Name", key="edit_chatbot_name", help="The personalized chatbot name. Has no effect on the model.")
        st.text_area("Description", key="edit_description", help="A description of the chatbot. Has no effect on the model.")
        st.text_input("Model Name", key="edit_model_name", 
                     help="Can be an ollama model name or a Hugging Face model name. Must be a valid model name for the specified inference provider.")
        
        # Configuration as JSON - more advanced UI could be implemented
        st.subheader("Configuration (JSON)")
        inference_providers = ["ollama", "huggingface"]
        st.selectbox("Inference Provider", 
                    options=inference_providers,
                    index=0,
                    key="edit_inference_provider", 
                    help="The service or framework used for inference such as ollama or huggingface; i.e. where the model is \
                        actually being run")
        st.text_input("Inference URL", key="edit_inference_url",
                     help="URL for the inference API endpoint")
        st.slider("Temperature", min_value=0.0, max_value=1.0, step=0.1, key="temperature")
        st.checkbox("Stream Responses", key="stream", help="Whether to stream responses from the model or wait until the entire response is generated.")
        
        st.checkbox("Active", key="edit_is_active")
        
        # Active status toggle

        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            # Button to return to chatbot list
            if st.form_submit_button("Back to Chatbots", use_container_width=True):
                st.session_state.current_page = "landing_page"
                st.rerun()

        with col3:    
            # Submit button
            submit_button = st.form_submit_button(label="Save Changes", use_container_width=True)    

            if submit_button:
                try:
                    # Parse configuration from string to dict
                    config_dict = {
                        "inference_provider": st.session_state.edit_inference_provider,
                        "inference_url": st.session_state.edit_inference_url,
                        "temperature": st.session_state.temperature,
                        "stream": st.session_state.stream,
                    }
                    
                    # Prepare update data
                    update_data = {
                        "chatbot_name": st.session_state.edit_chatbot_name,
                        "description": st.session_state.edit_description,
                        "model_name": st.session_state.edit_model_name,
                        "configuration": config_dict,
                    }
                    
                    # Send update request
                    response = requests.patch(
                        f"http://localhost:8000/chatbots/{st.session_state.chatbot_id}",
                        json=update_data,
                        headers={"Authorization": f"Bearer {st.session_state.access_token}"}
                    )
                    
                    if response.status_code == 200:
                        print("Chatbot updated successfully!")
                    else:
                        st.error(f"Failed to update chatbot: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Error updating chatbot: {str(e)}")