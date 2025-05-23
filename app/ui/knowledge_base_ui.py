import streamlit as st
import os
import datetime
import requests
import uuid
from ..rag_utils import delete_cache
from ..config import settings


def cache_file(upload_file):
    # set temp dir and file path
    temp_dir = os.path.join(settings.app_dir, "tmp")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    file_path = os.path.join(temp_dir, upload_file["file_name"])

    # save file to temp dir
    print(f"saving cache file to {file_path}")
    with open(file_path, "wb") as f:
        f.write(upload_file["file_buffer"])

    return os.path.abspath(file_path)


def get_knowledge_base_documents(chatbot_id):
    response = requests.get(
        f"http://localhost:8000/documents/by_chatbot/{chatbot_id}",
        headers={"Authorization": f"Bearer {st.session_state.access_token}"},
    )
    if response.status_code == 200:
        return response.json()
    else:
        st.error(
            f"failed to retrieve knowledge base documents for chatbot {chatbot_id}: {response.status_code}"
        )
        return []


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

    # uploaded_documents is the list of documents that have previously been uploaded
    # to the chatbot's knowledge base. new_documents is the list of documents that
    # have been queued for upload during this session. After the user clicks the "Upload"
    # button, new_documents is cleared and uploaded_documents is updated.
    if "new_documents" not in st.session_state:
        st.session_state.new_documents = []

    # File uploader
    new_documents = st.file_uploader("Upload documents", accept_multiple_files=True)

    if new_documents:
        for new_document in new_documents:
            # Check if the file has already been uploaded
            if new_document.name not in [
                f["file_name"] for f in st.session_state.new_documents
            ]:

                print(f"appending document to new documents: {new_document}")
                # Add the file to the session state
                st.session_state.new_documents.append(
                    {
                        "file_name": new_document.name,
                        "created_at": datetime.datetime.now().isoformat(),
                        "context": "",  # Initialize context
                        "file_buffer": new_document.getbuffer(),
                    }
                )

    # Display list of uploaded documents
    if "uploaded_documents" not in st.session_state:
        st.session_state.uploaded_documents = get_knowledge_base_documents(
            st.session_state.chatbot_id
        )
    # sort the uploaded documents by file name
    st.session_state.uploaded_documents.sort(key=lambda x: x["file_name"])

    with st.container():
        for file_data in st.session_state.uploaded_documents:
            col1, col2, col3, col4 = st.columns([4, 2, 2, 1])
            with col1:
                st.write(f"- {file_data['file_name']}")
            with col2:
                st.write(f"Uploaded: {file_data['created_at']}")
            with col3:
                if st.button("Edit Context", key=file_data["file_name"]):
                    st.session_state.document_id = file_data["document_id"]
                    st.session_state.current_page = "context_edit_page"
                    st.rerun()
            with col4:
                if st.button(
                    "❌",
                    key=file_data["file_name"] + "_delete",
                    use_container_width=True,
                ):
                    response = requests.delete(
                        f"http://localhost:8000/documents/{file_data['document_id']}",
                        headers={
                            "Authorization": f"Bearer {st.session_state.access_token}"
                        },
                    )
                    if response.status_code == 204:
                        st.success(f"Document '{file_data['file_name']}' deleted.")
                        st.session_state.uploaded_documents.remove(file_data)
                        st.rerun()
                    else:
                        st.error(
                            f"Failed to delete document '{file_data['file_name']}'."
                        )

    col1, col2, _ = st.columns([2, 1, 4])
    with col1:
        if st.button("Back to Chatbot Page", use_container_width=True):
            del st.session_state.uploaded_documents
            st.session_state.current_page = "chatbot_page"
            st.rerun()
    with col2:
        if st.button("Save"):
            delete_cache()
            for document in st.session_state.new_documents:
                print(f"in new documents: {document}")
                if document["file_name"] in [ d["file_name"] for d in st.session_state.uploaded_documents ]:
                    print(f"skipping {document['file_name']} because it already exists")
                    continue
                abs_file_path = cache_file(document)
            for document in st.session_state.new_documents:
                json_params = {
                    "document_id": str(uuid.uuid4()),
                    "chatbot_id": st.session_state.chatbot_id,
                    "file_name": document["file_name"],
                    "context": document["context"],
                    "file_path": abs_file_path,
                    "created_at": document["created_at"],
                }

                print(f"calling create document with {json_params}")
                requests.post(
                    "http://localhost:8000/documents/",
                    json=json_params,
                    headers={
                        "Authorization": f"Bearer {st.session_state.access_token}"
                    },
                )
            del st.session_state.uploaded_documents
            st.rerun()
