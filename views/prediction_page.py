import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from database.db_manager import DatabaseManager

def plot_gauge(title, value):
    val_pct = value * 100
    bar_color = "#ef4444" if val_pct >= 70 else "#f59e0b" if val_pct >= 40 else "#10b981"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val_pct,
        number={'suffix': "%", 'font': {'size': 26, 'family': 'Outfit, sans-serif'}},
        title={'text': f"<b>{title}</b>", 'font': {'size': 16, 'family': 'Outfit, sans-serif'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94a3b8"},
            'bar': {'color': bar_color, 'thickness': 0.3},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e2e8f0",
            'steps': [
                {'range': [0, 40], 'color': "#ecfdf5"},
                {'range': [40, 70], 'color': "#fffbeb"},
                {'range': [70, 100], 'color': "#fef2f2"}
            ],
            'threshold': {
                'line': {'color': "#dc2626", 'width': 3},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    fig.update_layout(height=230, margin=dict(l=15, r=15, t=40, b=15))
    return fig

def render():
    st.markdown(
        """
        <div class="hero-banner">
            <h1>Multi-Disease AI Risk Stratification ⚠️</h1>
            <p>Predictive risk scoring powered by 8 specialized Machine Learning models (XGBoost, Random Forest) trained on clinical datasets with physiological risk thresholding.</p>
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
        st.info("No reports found. Please upload a medical lab report first.")
        return

    # Select report
    report_options = {r['id']: f"📄 {r['report_title']} — {r['upload_timestamp'][:10]}" for r in reports}
    active_report_id = st.session_state.get('active_report_id')
    default_index = 0
    if active_report_id and active_report_id in report_options:
        default_index = list(report_options.keys()).index(active_report_id)

    selected_report_id = st.selectbox("Select Report to Inspect Risk Projections", options=list(report_options.keys()),
                                      format_func=lambda x: report_options[x], index=default_index)

    if selected_report_id:
        st.session_state['active_report_id'] = selected_report_id
        predictions = db.get_report_predictions(selected_report_id)

        if not predictions:
            st.warning("No predictions found for this report.")
            return

        # Overall summary metric
        high_risk_count = sum(1 for p in predictions if p['risk_probability'] >= 0.7)
        mod_risk_count = sum(1 for p in predictions if 0.4 <= p['risk_probability'] < 0.7)
        low_risk_count = sum(1 for p in predictions if p['risk_probability'] < 0.4)

        st.markdown(
            f"""
            <div class="metric-container">
                <div class="metric-card-modern danger">
                    <span class="metric-title">Critical / High Risks</span>
                    <span class="metric-value">{high_risk_count}</span>
                    <span class="metric-sub">Requires immediate medical review</span>
                </div>
                <div class="metric-card-modern warning">
                    <span class="metric-title">Moderate Watchlist</span>
                    <span class="metric-value">{mod_risk_count}</span>
                    <span class="metric-sub">Lifestyle intervention recommended</span>
                </div>
                <div class="metric-card-modern success">
                    <span class="metric-title">Low Risk / Optimal</span>
                    <span class="metric-value">{low_risk_count}</span>
                    <span class="metric-sub">Organ indicators within safety limits</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.subheader("Organ & System Risk Spectrum Gauges")
        cols = st.columns(4)
        for i, pred in enumerate(predictions):
            disease = pred['disease_type']
            risk_prob = pred['risk_probability']
            risk_level = pred['risk_level']

            with cols[i % 4]:
                st.plotly_chart(plot_gauge(disease, risk_prob), use_container_width=True)
                if risk_level in ["Critical", "High"]:
                    st.markdown(f"<div style='text-align:center;'><span class='badge-pill danger'>🚨 {risk_level} ({risk_prob*100:.1f}%)</span></div>", unsafe_allow_html=True)
                elif risk_level == "Moderate":
                    st.markdown(f"<div style='text-align:center;'><span class='badge-pill warning'>⚠️ {risk_level} ({risk_prob*100:.1f}%)</span></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align:center;'><span class='badge-pill normal'>✅ {risk_level} ({risk_prob*100:.1f}%)</span></div>", unsafe_allow_html=True)
                st.write("")
