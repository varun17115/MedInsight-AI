import streamlit as st
import pandas as pd
from database.db_manager import DatabaseManager
from src.reporting.doctor_summary import DoctorSummaryGenerator

def render():
    st.title("Patient History")

    user = st.session_state.get('user')
    if not user:
        st.error("Please login first.")
        return

    db = DatabaseManager()

    if 'delete_report' in st.session_state:
        db.delete_report(st.session_state.delete_report)
        st.success("Report deleted.")
        del st.session_state.delete_report
        st.rerun()

    reports = db.get_user_reports(user['id'])

    if not reports:
        st.info("No reports found in history.")
        return

    df = pd.DataFrame(reports)
    # Reformat for display
    display_df = df[['report_title', 'report_date', 'upload_timestamp']].copy()
    display_df.columns = ['Title', 'Report Date', 'Uploaded At']

    st.table(display_df)

    st.subheader("Actions")
    report_options = {r['id']: f"{r['report_title']} ({r['upload_timestamp'][:10]})" for r in reports}
    action_report_id = st.selectbox("Select Report", options=list(report_options.keys()), format_func=lambda x: report_options[x])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("View Details"):
            st.session_state['active_report_id'] = action_report_id
            st.info("Report set as active. Visit Health Score or Prediction pages to view details.")

    with col2:
        if st.button("Delete Report"):
            st.session_state.delete_report = action_report_id
            st.rerun()

    st.subheader("Physician Summary")
    if st.button("Generate Doctor Summary"):
        # Gather data
        params = db.get_report_parameters(action_report_id)
        preds = db.get_report_predictions(action_report_id)

        generator = DoctorSummaryGenerator()
        summary = generator.generate_summary(user, params, preds)
        st.text_area("Physician Summary", summary, height=300)
