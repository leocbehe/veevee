import streamlit as st
import requests
import datetime
from datetime import timezone

def profile_page():
    """
    Streamlit UI for user profile management.
    Displays user information in editable fields and allows users to update their profile.
    """
    st.header("Your Profile")

    # Initialize form state if not already in session
    if "profile_form_data" not in st.session_state:
        # Fetch current user data
        try:
            response = requests.get(
                f"http://localhost:8000/users/{st.session_state.user_id}",
                headers={"Authorization": f"Bearer {st.session_state.access_token}"}
            )
            if response.status_code == 200:
                user_data = response.json()
                st.session_state.profile_form_data = {
                    "username": user_data.get("username", ""),
                    "email": user_data.get("email", ""),
                    "firstname": user_data.get("firstname", ""),
                    "lastname": user_data.get("lastname", ""),
                    "user_id": user_data.get("user_id", ""),
                    "is_active": user_data.get("is_active", True),
                    "role": user_data.get("role", ""),
                    "created_at": user_data.get("created_at", "")
                }
            else:
                st.error(f"Failed to fetch user data: {response.status_code} - {response.text}")
                return
        except Exception as e:
            st.error(f"Error connecting to the user service: {str(e)}")
            return

    with st.form("profile_form"):
        # Display user information in editable fields
        st.text_input("Username", value=st.session_state.profile_form_data["username"], key="edit_username")
        st.text_input("Email", value=st.session_state.profile_form_data["email"], key="edit_email")
        st.text_input("First Name", value=st.session_state.profile_form_data["firstname"], key="edit_firstname")
        st.text_input("Last Name", value=st.session_state.profile_form_data["lastname"], key="edit_lastname")
        
        # Optional: Add password change fields
        st.subheader("Change Password")
        new_password = st.text_input("New Password", type="password", key="edit_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        
        # Display non-editable fields
        st.subheader("Account Information")
        st.info(f"User ID: {st.session_state.profile_form_data['user_id']}")
        st.info(f"Account Status: {'Active' if st.session_state.profile_form_data['is_active'] else 'Inactive'}")
        st.info(f"Role: {st.session_state.profile_form_data['role']}")
        st.info(f"Created At: {st.session_state.profile_form_data['created_at']}")
        
        # Form buttons
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            submit_button = st.form_submit_button("Save Changes", use_container_width=True)
        with col3:
            cancel_button = st.form_submit_button("Cancel", use_container_width=True)
    
    # Handle form submission
    if submit_button:
        # Validate password if provided
        if new_password and new_password != confirm_password:
            st.error("Passwords do not match!")
            return
        
        # Prepare update data
        update_data = {
            "username": st.session_state.edit_username,
            "email": st.session_state.edit_email,
            "firstname": st.session_state.edit_firstname,
            "lastname": st.session_state.edit_lastname
        }
        
        # Add password if provided
        if new_password:
            update_data["password"] = new_password
        
        try:
            response = requests.put(
                f"http://localhost:8000/users/{st.session_state.user_id}",
                json=update_data,
                headers={"Authorization": f"Bearer {st.session_state.access_token}"}
            )
            
            if response.status_code == 200:
                st.success("Profile updated successfully!")
                # Update session state with new data
                st.session_state.profile_form_data.update({
                    "username": st.session_state.edit_username,
                    "email": st.session_state.edit_email,
                    "firstname": st.session_state.edit_firstname,
                    "lastname": st.session_state.edit_lastname
                })
                # Navigate back to landing page
                st.session_state.current_page = "landing_page"
                st.rerun()
            else:
                st.error(f"Failed to update profile: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Error connecting to the user service: {str(e)}")
    
    # Handle cancel button
    if cancel_button:
        st.session_state.current_page = "landing_page"
        st.rerun()