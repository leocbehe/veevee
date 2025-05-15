import streamlit as st
import requests
from datetime import datetime

def landing_page():
    # Initialize session state variables
    if "show_chatbot_form" not in st.session_state:
        st.session_state.show_chatbot_form = False
    if "new_chatbot_name" not in st.session_state:
        st.session_state.new_chatbot_name = ""
    if "new_chatbot_description" not in st.session_state:
        st.session_state.new_chatbot_description = ""
    if "new_chatbot_model_path" not in st.session_state:
        st.session_state.new_chatbot_model_path = ""

    def open_chatbot_form():
        st.session_state.show_chatbot_form = True

    def close_chatbot_form():
        st.session_state.show_chatbot_form = False

    def open_profile_page():
        st.session_state.current_page = "profile_page"

    def create_chatbot():
        try:
            print(f"Creating chatbot with name: {st.session_state.new_chatbot_name}")
            print(f"datetime: {datetime.now().isoformat()}")
            response = requests.post(
                "http://localhost:8000/chatbots/",
                json={
                    "chatbot_name": st.session_state.new_chatbot_name,
                    "description": st.session_state.new_chatbot_description,
                    "model_path": st.session_state.new_chatbot_model_path,
                    "configuration": st.session_state.new_chatbot_config,
                    "created_at": datetime.now().isoformat(),
                    "owner_id": st.session_state.user_id
                },
                headers={"Authorization": f"Bearer {st.session_state.access_token}"},
            )
            if response.status_code == 200:
                st.success("Chatbot created successfully!")
            else:
                st.error(f"Failed to create chatbot: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Error connecting to the chatbot service: {str(e)}")
        finally:
            close_chatbot_form()

    # Button to open the chatbot form, placed above "Your Chatbots"

    st.markdown(f"<h3 style='text-align: center;'>Your Chatbots</h2>", unsafe_allow_html=True)

    # Chatbot form (modal)
    if st.session_state.show_chatbot_form:
        for k in ["stream", "temperature", "inference_provider"]:
            st.session_state.new_chatbot_config[k] = None
        with st.sidebar.container():
            st.sidebar.header("Create New Chatbot")
            st.session_state.new_chatbot_name = st.sidebar.text_input("Chatbot Name:", value=st.session_state.new_chatbot_name)
            st.session_state.new_chatbot_description = st.sidebar.text_input("Chatbot Description:", value=st.session_state.new_chatbot_description)
            st.session_state.new_chatbot_model_path = st.sidebar.text_input("Chatbot Model Path:", value=st.session_state.new_chatbot_model_path)
            st.session_state.new_chatbot_config["stream"] = st.sidebar.checkbox("Stream Responses", value=st.session_state.new_chatbot_config["stream"])
            st.session_state.new_chatbot_config["temperature"] = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=st.session_state.new_chatbot_config["temperature"], step=0.1)
            st.session_state.new_chatbot_config["inference_provider"] = st.sidebar.selectbox("Inference Provider", ["ollama", "huggingface"], index=st.session_state.new_chatbot_config["inference_provider"])

            col1, col2 = st.sidebar.columns(2)
            with col1:
                st.sidebar.button("Save", on_click=create_chatbot)
            with col2:
                st.sidebar.button("Cancel", on_click=close_chatbot_form)

    # Retrieve chatbots from the database and display them
    try:
        response = requests.get(
            "http://localhost:8000/chatbots/",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        if response.status_code == 200:
            chatbots = response.json()
            if chatbots:
                for chatbot in chatbots:
                    st.markdown("<hr style='margin-top: 0.5em;'>", unsafe_allow_html=True)
                    col1, col2, col3 = st.columns([0.7, 0.15, 0.15])
                    with col1:
                        st.write(f"- {chatbot['chatbot_name']}")
                    with col2:
                        if st.button(f"Select", key=f"select_{chatbot['chatbot_id']}", use_container_width=True):
                            st.session_state.chatbot_id = chatbot['chatbot_id']
                            st.session_state.chatbot_name = chatbot['chatbot_name']
                            st.session_state.chatbot_description = chatbot['description']
                            st.session_state.chatbot_model_path = chatbot['model_path']
                            if 'configuration' in chatbot:
                                st.session_state.chatbot_config = chatbot['configuration']
                            else:
                                st.session_state.chatbot_config = {}
                            st.session_state.current_page = "chatbot_page"
                            st.rerun()
                    with col3:
                        if st.button(f"Delete", key=f"delete_{chatbot['chatbot_id']}", use_container_width=True):
                            response = requests.delete(
                                f"http://localhost:8000/chatbots/{chatbot['chatbot_id']}",
                                headers={"Authorization": f"Bearer {st.session_state.access_token}"}
                            )
                            if response.status_code == 200:
                                st.success(f"Chatbot '{chatbot['chatbot_name']}' deleted successfully!")
                                st.rerun()
                            else:
                                st.error(f"Failed to delete chatbot: {response.status_code} - {response.text}")
                st.markdown("<hr style='margin-top: 0.5em;'>", unsafe_allow_html=True)
            else:
                st.write("There's nobody here...")
        else:
            st.error(f"Failed to retrieve chatbots: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Error connecting to the chatbot service: {str(e)}")

    c1, c2, c3 = st.columns([1, 3, 1])
    with c1:
        st.button("Edit Profile", on_click=open_profile_page, use_container_width=True)
    with c3:
        st.button("New Chatbot", on_click=open_chatbot_form, use_container_width=True)
