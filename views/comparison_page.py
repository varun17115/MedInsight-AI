import streamlit as st
import pandas as pd
from database.db_manager import DatabaseManager
from src.comparison.report_comparator import ReportComparator

def render():
    st.title("Report Comparison")
    st.write("Compare two medical reports to observe trends and changes.")

    user = st.session_state.get('user')
    if not user:
        st.error("Please login first.")
        return

    db = DatabaseManager()
    reports = db.get_user_reports(user['id'])

    if len(reports) < 2:
        st.info("You need at least two reports to use the comparison feature.")
        return

    report_options = {r['id']: f"{r['report_title']} ({r['upload_timestamp'][:10]})" for r in reports}

    col1, col2 = st.columns(2)
    with col1:
        old_report_id = st.selectbox("Select Older Report", options=list(report_options.keys()), format_func=lambda x: report_options[x], index=len(reports)-1)
    with col2:
        new_report_id = st.selectbox("Select Newer Report", options=list(report_options.keys()), format_func=lambda x: report_options[x], index=0)

    if old_report_id and new_report_id:
        if old_report_id == new_report_id:
            st.warning("Please select two different reports to compare.")
            return

        old_params = db.get_report_parameters(old_report_id)
        new_params = db.get_report_parameters(new_report_id)

        st.subheader("Parameter Trends")
        results = ReportComparator.compare_parameters(old_params, new_params)

        if not results:
            st.write("No matching parameters found to compare.")
            return

        df = pd.DataFrame(results)
        # Apply color styling
        def style_trend(val):
            color = 'green' if val == 'Improved' else 'red' if val == 'Worsened' else 'orange' if val == 'Stable' else 'gray'
            return f'color: {color}'

        # We need to map dataframe column headers
        df.rename(columns={
            "parameter": "Biomarker",
            "old_value": "Old Value",
            "new_value": "New Value",
            "unit": "Unit",
            "trend": "Trend",
            "color": "Color" # We can drop this or use it for style
        }, inplace=True)

        if 'Color' in df.columns:
            # Create a clean df for display
            display_df = df.drop(columns=['Color'])
            st.dataframe(display_df, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)
