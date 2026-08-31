import streamlit as st
from database.db_manager import DatabaseManager
from src.chatbot.chat_manager import ChatManager
from src.chatbot.gemini_client import GeminiClient

def render():
    st.markdown(
        """
        <div class="vibrant-hero">
            <h1>Intelligent Clinical Chatbot & Medical Co-Pilot 💬</h1>
            <p>Interactive Retrieval-Augmented Generation (RAG) assistant powered by Google Gemini. Ask questions about your lab test parameters, abnormal biomarkers, organ health status, or disease risk prevention.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    user = st.session_state.get('user')
    if not user:
        st.error("Please login first.")
        return

    db = DatabaseManager()
    reports = db.get_user_reports(user['id'])

    if not reports:
        st.markdown(
            """
            <div class="glass-box" style="text-align: center; padding: 40px 20px;">
                <img src="https://img.icons8.com/fluency/96/chat--v1.png" width="70" style="margin-bottom: 12px;"/>
                <h3>No Medical Reports Found for Analysis</h3>
                <p style="color: #64748b; max-width: 500px; margin: 0 auto 20px auto;">Upload your medical report first to give the clinical chatbot full RAG context regarding your laboratory test values and disease predictions.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("📤 Upload Report Now", type="primary"):
            st.session_state['current_page'] = "Upload Report"
            st.rerun()
        return

    # Select report for RAG context
    report_options = {r['id']: f"📄 {r['report_title']} ({r['upload_timestamp'][:10]})" for r in reports}
    active_report_id = st.session_state.get('active_report_id')
    default_index = 0
    if active_report_id and active_report_id in report_options:
        default_index = list(report_options.keys()).index(active_report_id)

    c1, c2 = st.columns([3, 1])
    with c1:
        selected_report_id = st.selectbox(
            "Active Clinical Context Report",
            options=list(report_options.keys()),
            format_func=lambda x: report_options[x],
            index=default_index
        )
    with c2:
        if st.button("🧹 Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

    if not selected_report_id:
        return

    # Reload chat history when changing report
    if 'chatbot_report_id' not in st.session_state or st.session_state['chatbot_report_id'] != selected_report_id:
        st.session_state['chatbot_report_id'] = selected_report_id
        st.session_state.chat_history = db.get_chat_history(user['id'], report_id=selected_report_id)

    # Context Summary Badge
    params = db.get_report_parameters(selected_report_id)
    anomalies = [p for p in params if p.get('flag') in ['HIGH', 'LOW', 'CRITICAL']]
    
    st.markdown(
        f"""
        <div style="background: white; border-radius: 12px; padding: 12px 18px; border: 1px solid #e2e8f0; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between;">
            <div>
                <span style="font-size: 0.85rem; color: #64748b; font-weight: 600;">GROUND-TRUTH RAG CONTEXT:</span>
                <span style="margin-left: 8px; font-weight: 700; color: #0f172a;">{len(params)} Biomarkers Loaded</span>
                <span style="margin-left: 8px; color: {'#ef4444' if anomalies else '#10b981'}; font-weight: 600;">({len(anomalies)} Anomalies Detected)</span>
            </div>
            <span style="font-size: 0.8rem; background: #ecfdf5; color: #065f46; padding: 4px 10px; border-radius: 9999px; font-weight: 700; border: 1px solid #a7f3d0;">
                ● AI Real-time Assistant Ready
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Display conversation messages
    messages = st.session_state.get('chat_history', [])
    for msg in messages:
        role = msg.get('role', 'user')
        avatar = "👤" if role == "user" else "🩺"
        with st.chat_message(role, avatar=avatar):
            st.markdown(msg['message'])

    # Suggested Prompts Chips
    if not messages:
        st.markdown("**Suggested questions for this report:**")
        s_cols = st.columns(3)
        with s_cols[0]:
            if st.button("🔍 Explain all abnormal parameters"):
                prompt = "Please give me a complete summary and breakdown of all abnormal (out of range) parameters in my report."
                st.session_state['pending_prompt'] = prompt
                st.rerun()
        with s_cols[1]:
            if st.button("🥗 Diet & Exercise Plan"):
                prompt = "What specific dietary and lifestyle changes should I make based on this report's results?"
                st.session_state['pending_prompt'] = prompt
                st.rerun()
        with s_cols[2]:
            if st.button("⚠️ Which doctor should I consult?"):
                prompt = "Based on my lab results and disease risk predictions, what medical specialists should I see?"
                st.session_state['pending_prompt'] = prompt
                st.rerun()

    # Chat Input
    prompt = st.chat_input("Ask any question about your medical report (e.g. 'Why is my MCV low?')")

    if 'pending_prompt' in st.session_state and st.session_state['pending_prompt']:
        prompt = st.session_state['pending_prompt']
        st.session_state['pending_prompt'] = None

    if prompt:
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🩺"):
            with st.spinner("Analyzing report data with MedInsight RAG engine..."):
                client = GeminiClient()
                chat_manager = ChatManager(client, db)
                response = chat_manager.handle_message(user['id'], selected_report_id, prompt)
                st.markdown(response)

        st.session_state.chat_history = db.get_chat_history(user['id'], report_id=selected_report_id)
        st.rerun()
