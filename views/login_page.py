import streamlit as st
from src.auth.authenticator import Authenticator
from database.db_manager import DatabaseManager

def render_login_page():
    st.title("Welcome to MedInsight AI")
    st.write("Intelligent Medical Report Analysis & Disease Risk Prediction Platform.")

    # Initialize DB and Authenticator
    db = DatabaseManager()
    auth = Authenticator(db)

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            credential = st.text_input("Username or Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                if not credential or not password:
                    st.error("Please fill in both fields.")
                else:
                    success, msg, user = auth.login_user(credential, password)
                    if success:
                        st.success(msg)
                        st.session_state['user'] = user
                        st.session_state['logged_in'] = True
                        st.rerun()
                    else:
                        st.error(msg)

    with tab2:
        st.subheader("Create a New Account")
        with st.form("register_form"):
            reg_username = st.text_input("Username*")
            reg_email = st.text_input("Email*")
            reg_fullname = st.text_input("Full Name*")
            reg_password = st.text_input("Password*", type="password")
            reg_confirm_password = st.text_input("Confirm Password*", type="password")

            c1, c2 = st.columns(2)
            reg_age = c1.number_input("Age (Optional)", min_value=1, max_value=120, value=None)
            reg_gender = c2.selectbox("Gender (Optional)", ["Male", "Female", "Other", None])

            reg_submitted = st.form_submit_button("Register")

            if reg_submitted:
                if not reg_username or not reg_email or not reg_fullname or not reg_password:
                    st.error("Please fill in all mandatory fields (*).")
                elif reg_password != reg_confirm_password:
                    st.error("Passwords do not match!")
                else:
                    success, msg = auth.register_user(
                        username=reg_username,
                        email=reg_email,
                        password=reg_password,
                        full_name=reg_fullname,
                        age=int(reg_age) if reg_age else None,
                        gender=reg_gender if reg_gender else None
                    )
                    if success:
                        st.success("Registration successful! Please login from the Login tab.")
                    else:
                        st.error(msg)
