import streamlit as st
from database.db_manager import DatabaseManager
from src.auth.authenticator import hash_password

def render():
    st.title("My Profile")

    user = st.session_state.get('user')
    if not user:
        st.error("Please login first.")
        return

    db = DatabaseManager()

    with st.expander("Update Profile", expanded=True):
        with st.form("profile_form"):
            full_name = st.text_input("Full Name", value=user.get('full_name', ''))
            age = st.number_input("Age", min_value=0, max_value=120, value=user.get('age', 40))
            gender = st.selectbox("Gender", options=['Male', 'Female', 'Other'], index=['Male', 'Female', 'Other'].index(user.get('gender', 'Male')))
            blood_group = st.text_input("Blood Group", value=user.get('blood_group', ''))
            height = st.number_input("Height (cm)", value=user.get('height_cm', 0.0))
            weight = st.number_input("Weight (kg)", value=user.get('weight_kg', 0.0))
            cond = st.text_area("Medical Conditions", value=user.get('medical_conditions', ''))

            if st.form_submit_button("Save Changes"):
                db.update_user_profile(user['id'], full_name, age, gender, blood_group, height, weight, cond)
                # Refresh session user
                st.session_state['user'] = db.get_user_by_credential(user['username'])
                st.success("Profile updated.")

    with st.expander("Change Password"):
        with st.form("password_form"):
            new_pass = st.text_input("New Password", type="password")
            confirm_pass = st.text_input("Confirm New Password", type="password")

            if st.form_submit_button("Update Password"):
                if new_pass != confirm_pass:
                    st.error("Passwords do not match.")
                elif len(new_pass) < 8:
                    st.error("Password too short.")
                else:
                    db.update_user_password(user['id'], hash_password(new_pass))
                    st.success("Password updated.")
