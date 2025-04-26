import streamlit as st
import os
import datetime
import requests
import uuid
from ..config import settings


def cache_file(upload_file):
    temp_dir = os.path.join(settings.app_dir, "tmp")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    file_path = os.path.join(temp_dir, upload_file["file_name"])
    with open(file_path, "wb") as f:
        f.write(upload_file["file_buffer"])
    return os.path.abspath(file_path)


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
            if uploaded_file.name not in [
                f["file_name"] for f in st.session_state.uploaded_files
            ]:

                # Add the file to the session state
                st.session_state.uploaded_files.append(
                    {
                        "file_name": uploaded_file.name,
                        "created_at": datetime.datetime.now().isoformat(),
                        "context": "",  # Initialize context
                        "file_buffer": uploaded_file.getbuffer(),
                    }
                )
                st.success(f"File '{uploaded_file.name}' uploaded successfully!")
            else:
                st.warning(f"File '{uploaded_file.name}' already uploaded.")

    # Display list of uploaded documents
    if st.session_state.uploaded_files:
        st.subheader("Uploaded Documents")
        for file_data in st.session_state.uploaded_files:
            col1, col2, col3, col4 = st.columns([4, 2, 2, 1])
            with col1:
                st.write(f"- {file_data['file_name']}")
            with col2:
                st.write(f"Uploaded: {file_data['created_at']}")
            with col3:
                if st.button("Edit Context", key=file_data["file_name"]):
                    st.session_state.selected_file = file_data["file_name"]
                    st.session_state.current_page = "context_edit_page"
                    st.rerun()
            with col4:
                if st.button(
                    "❌",
                    key=file_data["file_name"] + "_delete",
                    use_container_width=True,
                ):
                    st.session_state.uploaded_files.remove(file_data)
                    st.rerun()

    col1, col2, _ = st.columns([2, 1, 4])
    with col1:
        if st.button("Back to Chatbot Page", use_container_width=True):
            st.session_state.current_page = "chatbot_page"
            st.rerun()
    with col2:
        if st.button("Save"):
            for document in st.session_state.uploaded_files:
                abs_file_path = cache_file(document)
                json_params = {
                    "document_id": str(uuid.uuid4()),
                    "chatbot_id": st.session_state.chatbot_id,
                    "file_name": document["file_name"],
                    "context": document["context"],
                    "file_path": abs_file_path,
                    "created_at": document["created_at"],
                }
                print(f"JSON Params: {json_params}")
                requests.post(
                    "http://localhost:8000/documents/",
                    json=json_params,
                    headers={
                        "Authorization": f"Bearer {st.session_state.access_token}"
                    },
                )
