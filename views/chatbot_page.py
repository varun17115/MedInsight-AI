import streamlit as st
from database.db_manager import DatabaseManager
from src.chatbot.chat_manager import ChatManager
from src.chatbot.gemini_client import GeminiClient

def render():
    st.title("Clinical Assistant")
    st.write("Talk to the MedInsight AI Assistant about your reports.")

    user = st.session_state.get('user')
    if not user:
        st.error("Please login first.")
        return

    db = DatabaseManager()
    reports = db.get_user_reports(user['id'])

    if not reports:
        st.info("Upload a medical report first to give the assistant context.")
        return

    report_options = {r['id']: f"{r['report_title']} ({r['upload_timestamp'][:10]})" for r in reports}
    active_report_id = st.session_state.get('active_report_id')
    default_index = 0
    if active_report_id and active_report_id in report_options:
        default_index = list(report_options.keys()).index(active_report_id)

    selected_report_id = st.selectbox("Select Context Report", options=list(report_options.keys()),
                                      format_func=lambda x: report_options[x], index=default_index)

    if not selected_report_id:
        return

    # Keep a reference to the active report in session
    if 'chatbot_report_id' not in st.session_state or st.session_state['chatbot_report_id'] != selected_report_id:
        st.session_state['chatbot_report_id'] = selected_report_id
        # Initialize or reload chat history
        st.session_state.chat_history = db.get_chat_history(user['id'], report_id=selected_report_id)

    # Convert DB history to streamlit chat format
    messages = st.session_state.get('chat_history', [])

    # Display chat history
    for msg in messages:
        role = msg.get('role', 'user')
        st.chat_message(role).write(msg['message'])

    prompt = st.chat_input("Ask about your report (e.g., 'What does my high glucose mean?')")

    if prompt:
        # Show user message
        st.chat_message("user").write(prompt)

        # Build context
        with st.spinner("Thinking..."):
            client = GeminiClient()
            chat_manager = ChatManager(client, db)
            response = chat_manager.handle_message(user['id'], selected_report_id, prompt)

        st.chat_message("assistant").write(response)

        # Update local session state history
        st.session_state.chat_history = db.get_chat_history(user['id'], report_id=selected_report_id)
