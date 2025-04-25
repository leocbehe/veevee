import streamlit as st
import os
import datetime
import requests
import uuid

def knowledge_base_page():
    """
    Streamlit UI for managing knowledge base documents.
    Allows users to upload documents, view a list of uploaded documents,
    and potentially edit context for each document (feature not fully implemented).
    Context refers to the information that is used to integrate the document into the
    chatbot's background knowledge. For example, if a document is written as a list
    of geography facts, the context could be a system prompt that says "You refer to 
    the following facts as necessary when answering questions about geography." This 
    context statement is then prepended to the text of the document itself, and the
    whole thing is set as the chatbot's system prompt.
    """

    st.header("Manage Knowledge Base")

    # Initialize session state for uploaded files if it doesn't exist
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

    # File uploader
    uploaded_files = st.file_uploader("Upload documents", accept_multiple_files=True)

    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Check if the file has already been uploaded
            if uploaded_file.name not in [f["file_name"] for f in st.session_state.uploaded_files]:
                # Save the file to a temporary directory (optional)
                # temp_dir = "temp_files"
                # if not os.path.exists(temp_dir):
                #     os.makedirs(temp_dir)
                # file_path = os.path.join(temp_dir, uploaded_file.name)
                # with open(file_path, "wb") as f:
                #     f.write(uploaded_file.getbuffer())

                # Add the file to the session state
                st.session_state.uploaded_files.append({
                    "file_name": uploaded_file.name,
                    "file_content": uploaded_file.read(),  # Store file content in memory
                    "upload_date": datetime.datetime.now().isoformat(),
                    # "file_path": file_path,  # Store the file path
                    "context": {}  # Initialize context
                })
                st.success(f"File '{uploaded_file.name}' uploaded successfully!")
            else:
                st.warning(f"File '{uploaded_file.name}' already uploaded.")

    # Display list of uploaded documents
    if st.session_state.uploaded_files:
        st.subheader("Uploaded Documents")
        for file_data in st.session_state.uploaded_files:
            col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
            with col1:
                st.write(f"- {file_data['file_name']}")
            with col2:
                st.write(f"Uploaded: {file_data['upload_date']}")
            with col3:
                if st.button("Edit Context", key=file_data['file_name']):
                    st.session_state.selected_file = file_data['file_name']
                    st.session_state.current_page = "context_edit_page"
                    st.rerun()

    col1, col2, _ = st.columns([2,1,4])
    with col1:
        if st.button("Back to Chatbot Page", use_container_width=True):
            st.session_state.current_page = "chatbot_page"
            st.rerun()
    with col2:
        if st.button("Save"):
            # TODO: Implement save functionality
            pass