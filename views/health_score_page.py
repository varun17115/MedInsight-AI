import streamlit as st
import json
from database.db_manager import DatabaseManager

def render():
    st.title("Health Score Overview")

    user = st.session_state.get('user')
    if not user:
        st.error("Please login first.")
        return

    db = DatabaseManager()

    # Get all reports to allow selection
    reports = db.get_user_reports(user['id'])

    if not reports:
        st.info("No reports found. Please upload a report first.")
        return

    # Select report
    report_options = {r['id']: f"{r['report_title']} ({r['upload_timestamp'][:10]})" for r in reports}

    active_report_id = st.session_state.get('active_report_id')
    default_index = 0
    if active_report_id and active_report_id in report_options:
        default_index = list(report_options.keys()).index(active_report_id)

    selected_report_id = st.selectbox("Select Report to View", options=list(report_options.keys()),
                                      format_func=lambda x: report_options[x], index=default_index)

    if selected_report_id:
        st.session_state['active_report_id'] = selected_report_id
        health_score_row = db.get_report_health_score(selected_report_id)

        if not health_score_row:
            st.warning("No health score computed for this report.")
            return

        score = health_score_row['overall_score']
        grade = health_score_row['score_grade']

        st.write(f"### Overall Health Score: {score:.1f} / 100")

        color = "green"
        if grade in ["Fair", "Poor"]:
            color = "orange"
        elif grade == "Critical":
            color = "red"

        st.markdown(f"<h2 style='color: {color};'>{grade}</h2>", unsafe_allow_html=True)

        try:
            breakdown = json.loads(health_score_row['score_breakdown_json']) if health_score_row.get('score_breakdown_json') else {}
        except:
            breakdown = {}

        if breakdown:
            st.subheader("Category Breakdown")
            for cat, penalty in breakdown.items():
                st.write(f"**{cat}**: Needs attention (Penalty applied: {penalty})")
        else:
            st.write("All categories are relatively healthy or not enough data to break down.")

        st.markdown("---")
        st.subheader("Key Recommendations")
        recs = db.get_report_recommendations(selected_report_id)
        if recs:
            for rec in recs:
                st.markdown(f"**{rec['title']}** ({rec['priority']} Priority)")
                try:
                    desc_data = json.loads(rec['description'])
                    for p in desc_data.get('diet', []):
                        st.markdown(f"- 🍎 {p}")
                    for p in desc_data.get('lifestyle', []):
                        st.markdown(f"- 🏃 {p}")
                    if desc_data.get('consult'):
                        st.markdown(f"- 👩‍⚕️ **Consult:** {desc_data['consult']}")
                except:
                    st.write(rec['description'])
        else:
            st.info("No specific critical recommendations generated.")
