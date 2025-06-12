import streamlit as st
import requests
import uuid
from ..llm import LLMService


def context_edit_page():
    """
    Displays a single knowledge base document based on the selected_document ID,
    allowing users to view and modify the context of the document.
    """

    if "chatbot_id" not in st.session_state:
        st.error("No chatbot selected. Please return to the chatbot page.")
        return

    if "document_id" not in st.session_state:
        st.error(
            "No document selected. Please select a document from the knowledge base page."
        )
        return

    document_id = st.session_state.document_id

    try:
        response = requests.get(
            f"http://localhost:8000/documents/{document_id}",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"},
        )

        if response.status_code == 200:
            document = response.json()

            st.header(f"Edit Context: {document['file_name']}")

            st.divider()

            with st.container():
                text_preview_key = f"text_preview_{document['document_id']}"
                context_key = f"context_{document['document_id']}"
                if text_preview_key not in st.session_state:
                    st.session_state[text_preview_key] = (
                        document["raw_text"][:5000]+"... " or ""
                    )  # Initialize with existing text preview
                if context_key not in st.session_state:
                    st.session_state[context_key] = (
                        document["context"] or ""
                    )  # Initialize with existing context

                st.text_area(
                    "Context:",
                    value=st.session_state[context_key],
                    height=100,
                    key=f"context_area_{document['document_id']}",
                    label_visibility="visible"
                )

                col1, col2 = st.columns([1, 2])
                with col1:
                    if st.button("Update Context", key=f"update_{document['document_id']}", use_container_width=True):
                        new_context = st.session_state[context_key]
                        update_context(document["document_id"], new_context)
                with col2:
                    if st.button("⬅️ Back to Knowledge Base", use_container_width=True):
                        st.session_state.current_page = "knowledge_base_page"
                        st.session_state.document_id = None
                        st.rerun()

        elif response.status_code == 404:
            st.info("Document not found.")
        else:
            st.error(
                f"Failed to retrieve document: {response.status_code} - {response.text}"
            )

    except Exception as e:
        st.error(f"Error connecting to the document service: {str(e)}")

    # if st.session_state.get("show_summary", False):
    #     render_popup_summary(st.session_state.summary_generator)

    

    st.session_state.page_load = False


def update_context(document_id: uuid.UUID, new_context: str):
    """
    Updates the context of a knowledge base document.
    """
    try:
        response = requests.put(
            f"http://localhost:8000/documents/{document_id}",
            json={
                "context": new_context
            },
            headers={"Authorization": f"Bearer {st.session_state.access_token}"},
        )

        if response.status_code == 200:
            st.success("Context updated")
        else:
            st.error(
                f"Failed to update context: {response.status_code} - {response.text}"
            )

    except Exception as e:
        st.error(f"Error updating the document service: {str(e)}")


def summarize_document(document_id: uuid.UUID, raw_text: str):
    summary_service = LLMService(
        st.session_state.chatbot_model_name, 
        inference_provider=st.session_state.chatbot_config['inference_provider'],
        inference_url=st.session_state.chatbot_config['inference_url'],
        max_response_tokens=1000)
    order = """ Please summarize the following text:\n\n"""

    response_generator = summary_service.generate(
        [
            {
            "role": "user",
            "content": order
            },
            {
            "role": "user",
            "content": ( raw_text if len(raw_text) < 5000 else raw_text[:5000] + "...") 
            }
        ]
    )

    return response_generator


def render_popup_summary(summary_generator):
    with st.container(border=True):
        st.subheader("Summary")
        summary_placeholder = st.empty()
        full_summary = ""
        for chunk in summary_generator:
            full_summary += chunk.message.content
            summary_placeholder.markdown(full_summary + "▌")
        summary_placeholder.markdown(full_summary)
