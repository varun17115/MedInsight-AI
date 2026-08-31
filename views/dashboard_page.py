import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.db_manager import DatabaseManager

def render():
    user = st.session_state.get('user')
    if not user:
        st.error("Please login first.")
        return

    db = DatabaseManager()
    reports = db.get_user_reports(user['id'])

    # 1. Vibrant Hero Banner
    st.markdown(
        f"""
        <div class="vibrant-hero">
            <h1>Clinical Intelligence Dashboard</h1>
            <p>Welcome back, <strong>{user.get('full_name', 'Patient')}</strong>. Here is your real-time multi-organ health trajectory, biomarker anomaly tracking, and AI disease risk stratification.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not reports:
        st.markdown(
            """
            <div class="glass-box" style="text-align: center; padding: 50px 20px;">
                <img src="https://img.icons8.com/fluency/96/medical-history.png" width="90" style="margin-bottom: 16px;"/>
                <h2 style="margin-bottom: 8px;">No Medical Reports Analyzed Yet</h2>
                <p style="color: #64748b; max-width: 540px; margin: 0 auto 24px auto; font-size: 1rem;">
                    Upload a clinical lab report (CBC, Lipid Panel, Metabolic, Thyroid, Liver, or Kidney test) to instantly activate multi-disease risk prediction, SHAP explanations, and personalized health recommendations.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("📤 Upload Medical Report Now", type="primary"):
            st.session_state['current_page'] = "Upload Report"
            st.rerun()
        return

    latest_report = reports[0]
    report_id = latest_report['id']
    params = db.get_report_parameters(report_id)
    preds = db.get_report_predictions(report_id)
    health_score_row = db.get_report_health_score(report_id)
    recs = db.get_report_recommendations(report_id)

    # Key Metrics Bar
    score_val = health_score_row['overall_score'] if health_score_row else 100.0
    score_grade = health_score_row['score_grade'] if health_score_row else "Good"
    anomalies = [p for p in params if p.get('flag') in ['HIGH', 'LOW', 'CRITICAL']]
    high_risks = [p for p in preds if p.get('risk_probability', 0) > 0.5]

    score_class = "success" if score_val >= 75 else "warning" if score_val >= 50 else "danger"

    st.markdown(
        f"""
        <div class="metric-grid-4">
            <div class="vibrant-metric-card {score_class}">
                <span class="vibrant-metric-label">Composite Health Score</span>
                <span class="vibrant-metric-num" style="color: {'#10b981' if score_val >= 75 else '#f59e0b' if score_val >= 50 else '#ef4444'};">
                    {score_val:.1f} <span style="font-size: 1.1rem; color: #94a3b8; font-weight: 500;">/ 100</span>
                </span>
                <span class="vibrant-metric-hint">Status: <strong>{score_grade}</strong></span>
            </div>
            <div class="vibrant-metric-card {'danger' if anomalies else 'success'}">
                <span class="vibrant-metric-label">Biomarker Anomalies</span>
                <span class="vibrant-metric-num" style="color: {'#ef4444' if anomalies else '#10b981'};">{len(anomalies)}</span>
                <span class="vibrant-metric-hint">Out of <strong>{len(params)}</strong> measured tests</span>
            </div>
            <div class="vibrant-metric-card {'danger' if high_risks else 'success'}">
                <span class="vibrant-metric-label">Elevated Risks</span>
                <span class="vibrant-metric-num" style="color: {'#ef4444' if high_risks else '#10b981'};">{len(high_risks)}</span>
                <span class="vibrant-metric-hint">Across <strong>8</strong> disease models</span>
            </div>
            <div class="vibrant-metric-card purple">
                <span class="vibrant-metric-label">Report Archive</span>
                <span class="vibrant-metric-num" style="color: #7c3aed;">{len(reports)}</span>
                <span class="vibrant-metric-hint">Latest: <strong>{latest_report['upload_timestamp'][:10]}</strong></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown(
            """
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                <h3 style="margin: 0; font-size: 1.25rem;">🔬 Extracted Biomarkers & Anomalies</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        if params:
            df_params = []
            for p in params:
                flag = p.get('flag', 'NORMAL')
                ref = f"{p.get('reference_low', '')} - {p.get('reference_high', '')}" if p.get('reference_low') is not None else "Standard"
                df_params.append({
                    "Biomarker": p.get('parameter_name'),
                    "Category": p.get('category'),
                    "Measured Value": f"{p.get('measured_value')} {p.get('unit', '')}",
                    "Reference Range": ref,
                    "Clinical Flag": f"🚨 {flag}" if flag in ['HIGH', 'CRITICAL'] else f"⚠️ {flag}" if flag == 'LOW' else f"✅ {flag}"
                })
            st.dataframe(df_params, use_container_width=True, height=290)
        else:
            st.info("No parameters extracted for the latest report.")

    with col2:
        st.markdown(
            """
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                <h3 style="margin: 0; font-size: 1.25rem;">⚠️ Multi-Organ Risk Spectrum</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        if preds:
            disease_names = [p['disease_type'] for p in preds]
            risk_values = [p['risk_probability'] * 100 for p in preds]
            
            # Vibrant color palette for charts
            colors = [
                '#ef4444' if v >= 70 else '#f59e0b' if v >= 40 else '#10b981'
                for v in risk_values
            ]

            fig = go.Figure(go.Bar(
                x=risk_values,
                y=disease_names,
                orientation='h',
                marker=dict(
                    color=colors,
                    line=dict(width=0),
                    cornerradius=6
                ),
                text=[f"{v:.1f}%" for v in risk_values],
                textposition='inside',
                textfont=dict(color='white', family='Plus Jakarta Sans', size=11),
                insidetextanchor='end'
            ))
            fig.update_layout(
                margin=dict(l=10, r=10, t=5, b=10),
                height=290,
                xaxis=dict(range=[0, 100], title=None, showgrid=True, gridcolor="#f1f5f9"),
                yaxis=dict(autorange="reversed"),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)

    # Recommendations Section
    if recs:
        st.markdown("---")
        st.markdown(
            """
            <div style="margin-bottom: 16px;">
                <h3 style="margin: 0; font-size: 1.3rem;">💡 Personalized Evidence-Based Action Plan</h3>
                <p style="margin: 4px 0 0 0; color: #64748b; font-size: 0.95rem;">Curated dietary, lifestyle, and specialist consultation advice generated specifically for your biomarker anomalies.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        r_cols = st.columns(min(3, len(recs)))
        for i, rec in enumerate(recs[:3]):
            with r_cols[i]:
                p_level = rec.get('priority', 'Medium')
                st.markdown(
                    f"""
                    <div class="glass-box" style="height: 100%; border-top: 4px solid {'#ef4444' if p_level == 'High' else '#f59e0b' if p_level == 'Medium' else '#3b82f6'};">
                        <span class="pill-badge {'danger' if p_level == 'High' else 'warning'}">{p_level} Priority</span>
                        <h4 style="margin: 12px 0 8px 0; font-size: 1.1rem; color: #0f172a;">{rec.get('title')}</h4>
                        <p style="font-size: 0.9rem; color: #64748b; margin: 0;">Target: <strong>{rec.get('target_condition', 'General')}</strong></p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
