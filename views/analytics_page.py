import streamlit as st
import pandas as pd
import plotly.express as px
from database.db_manager import DatabaseManager

def render():
    st.title("Analytics & Trends")
    st.write("Track your health biomarkers over time.")

    user = st.session_state.get('user')
    if not user:
        st.error("Please login first.")
        return

    db = DatabaseManager()
    parameters = db.get_all_user_parameter_names(user['id'])

    if not parameters:
        st.info("No parameter data found.")
        return

    selected_param = st.selectbox("Select Parameter to Analyze", options=parameters)

    if selected_param:
        history = db.get_parameter_history(user['id'], selected_param)

        if not history:
            st.write("No historical data available for this parameter.")
            return

        df = pd.DataFrame(history)
        # Ensure we have date values
        df['upload_timestamp'] = pd.to_datetime(df['upload_timestamp'])

        if len(df) == 1:
            st.info("Only one data point available. Upload more reports to see trends.")

        # Plot line chart
        fig = px.line(df, x="upload_timestamp", y="measured_value", markers=True,
                      title=f"{selected_param.title()} Trend Over Time",
                      labels={"upload_timestamp": "Date", "measured_value": f"Value ({df['unit'].iloc[0]})" if not df.empty else "Value"},
                      hover_data=["report_title", "flag"])

        # Add reference lines if available
        if not df.empty and pd.notnull(df['reference_low'].iloc[0]) and pd.notnull(df['reference_high'].iloc[0]):
            ref_low = df['reference_low'].iloc[0]
            ref_high = df['reference_high'].iloc[0]
            fig.add_hline(y=ref_low, line_dash="dash", line_color="green", annotation_text="Low Normal")
            fig.add_hline(y=ref_high, line_dash="dash", line_color="red", annotation_text="High Normal")

        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Health Score Trend")
        score_history = db.get_health_score_history(user['id'])
        if score_history:
            sdf = pd.DataFrame(score_history)
            sdf['upload_timestamp'] = pd.to_datetime(sdf['upload_timestamp'])
            fig_score = px.line(sdf, x="upload_timestamp", y="overall_score", markers=True,
                                title="Overall Health Score Over Time",
                                labels={"upload_timestamp": "Date", "overall_score": "Health Score"})
            fig_score.update_layout(height=400)
            st.plotly_chart(fig_score, use_container_width=True)
