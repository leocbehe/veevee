import streamlit as st
import requests

def landing_page():
    # Initialize session state variables
    if "show_chatbot_form" not in st.session_state:
        st.session_state.show_chatbot_form = False
    if "chatbot_name_input" not in st.session_state:
        st.session_state.chatbot_name_input = ""
    if "chatbot_description_input" not in st.session_state:
        st.session_state.chatbot_description_input = ""
    if "chatbot_model_path_input" not in st.session_state:
        st.session_state.chatbot_model_path_input = ""

    def open_chatbot_form():
        st.session_state.show_chatbot_form = True

    def close_chatbot_form():
        st.session_state.show_chatbot_form = False

    def create_chatbot():
        try:
            response = requests.post(
                "http://localhost:8000/chatbots/",
                json={
                    "chatbot_name": st.session_state.chatbot_name_input,
                    "description": st.session_state.chatbot_description_input,
                    "model_path": st.session_state.chatbot_model_path_input,
                    "owner_id": st.session_state.user_id,
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
            st.rerun()

    # Button to open the chatbot form, placed above "Your Chatbots"
    st.button("Create Chatbot", on_click=open_chatbot_form)

    st.subheader("Your Chatbots:")

    # Chatbot form (modal)
    if st.session_state.show_chatbot_form:
        with st.sidebar.container():
            st.sidebar.subheader("Create New Chatbot")
            st.session_state.chatbot_name_input = st.sidebar.text_input("Chatbot Name:", value=st.session_state.chatbot_name_input)
            st.session_state.chatbot_description_input = st.sidebar.text_input("Chatbot Description:", value=st.session_state.chatbot_description_input)
            st.session_state.chatbot_model_path_input = st.sidebar.text_input("Chatbot Model Path:", value=st.session_state.chatbot_model_path_input)

            col1, col2 = st.sidebar.columns(2)
            with col1:
                if st.sidebar.button("Save", on_click=create_chatbot):
                    pass
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
                    col1, col2 = st.columns([0.8, 0.2])
                    with col1:
                        st.write(f"- {chatbot['chatbot_name']}")
                    with col2:
                        if st.button(f"Select {chatbot['chatbot_name']}", key=f"select_{chatbot['chatbot_id']}"):
                            st.session_state.chatbot_id = chatbot['chatbot_id']
                            st.session_state.chatbot_name = chatbot['chatbot_name']
                            st.session_state.chatbot_description = chatbot['description']
                            st.session_state.chatbot_model_path = chatbot['model_path']
                            st.session_state.current_page = "chatbot_page"
                            st.rerun()
            else:
                st.write("There's nobody here...")
        else:
            st.error(f"Failed to retrieve chatbots: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Error connecting to the chatbot service: {str(e)}")
