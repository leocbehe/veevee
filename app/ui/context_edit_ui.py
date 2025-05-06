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
                col1, col2 = st.columns([5, 1])  # Adjust column widths as needed

                with col1:
                    context_key = f"context_{document['document_id']}"
                    if context_key not in st.session_state:
                        st.session_state[context_key] = (
                            document["context"] or ""
                        )  # Initialize with existing context

                    st.session_state[context_key] = st.text_area(
                        "Context:",
                        value=st.session_state[context_key],
                        height=200,
                        key=f"context_area_{document['document_id']}",
                        label_visibility="collapsed",
                    )

                with col2:
                    if st.button(
                        "Update Context", key=f"update_{document['document_id']}"
                    ):
                        new_context = st.session_state[context_key]
                        update_context(document["document_id"], new_context)
                    if st.button("Get Summary", key=f"summary_{document_id}"):
                        st.session_state.summary_generator = summarize_document(
                            document_id, document["raw_text"]
                        )
                        st.session_state.show_summary = True
                        st.rerun()

        elif response.status_code == 404:
            st.info("Document not found.")
        else:
            st.error(
                f"Failed to retrieve document: {response.status_code} - {response.text}"
            )

    except Exception as e:
        st.error(f"Error connecting to the document service: {str(e)}")

    if st.button("Back to Knowledge Base"):
        st.session_state.current_page = "knowledge_base_page"
        st.session_state.document_id = None
        st.rerun()

    if st.session_state.get("show_summary", False):
        render_popup_summary(st.session_state.summary_generator)


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
    summary_service = LLMService("gemma3:12b")
    order = """ Please summarize the following text in 300 words or less:\n\n"""

    response_generator = summary_service.generate(
        [
            {
            "role": "user",
            "content": order
            },
            {
            "role": "user",
            "content": raw_text
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
