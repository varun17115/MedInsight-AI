import os
import streamlit as st
import tempfile
import plotly.graph_objects as go
from database.db_manager import DatabaseManager
from src.parser.parser import MedicalReportParser
from src.ml.predictor import DiseasePredictor
from src.ml.health_score import HealthScoreCalculator
from src.recommender.rule_engine import RecommendationEngine
from src.ocr.text_extractor import TextExtractor
from src.ocr.ocr_engine import OCREngine

def render():
    st.markdown(
        """
        <div class="vibrant-hero">
            <h1>Upload & Intelligent Analysis</h1>
            <p>Upload multi-format clinical reports (PDF, scanned images) for automated parameter extraction, OCR text parsing, multi-organ anomaly detection, and real-time AI disease prediction.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    user = st.session_state.get('user')
    if not user:
        st.error("Please login first.")
        return

    gender = user.get("gender", "Male")
    db = DatabaseManager()

    st.markdown(
        """
        <div class="glass-box">
            <h3 style="margin-bottom: 8px;">Upload Medical Document</h3>
            <p style="color: #64748b; margin-bottom: 20px;">Supported Formats: PDF (Digital / Scanned), PNG, JPG, JPEG</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_up, col_info = st.columns([3, 2])

    with col_up:
        uploaded_file = st.file_uploader("Choose file", type=['pdf', 'png', 'jpg', 'jpeg'], label_visibility="collapsed")
        report_title = st.text_input("Report Title (Optional)", value="Comprehensive Medical Test")

    with col_info:
        st.info("💡 **Tip:** Our multimodal engine automatically parses tabular CBC tests, renal/liver biochemistry panels, lipid profiles, and metabolic panels.")

    if st.button("🚀 Analyze Medical Report", type="primary") and uploaded_file:
        with st.spinner("Processing medical report with multimodal OCR, extraction & ML engines..."):
            # 1. Save uploaded file to temp path
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            file_size_kb = os.path.getsize(file_path) / 1024.0
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()

            raw_text = ""
            tables = []

            # 2. Extract Text & Tables
            if file_ext == '.pdf':
                extractor = TextExtractor()
                raw_text = extractor.extract_text_pymupdf(file_path)
                tables = extractor.extract_tables_pdfplumber(file_path)
            else:
                ocr = OCREngine()
                ocr_res = ocr.process_document(file_path)
                raw_text = ocr_res.get("text", "")

            # 3. Parse Parameters
            parser = MedicalReportParser()
            parameters = parser.parse_text(raw_text, gender=gender, tables=tables)

            # 4. Predict Disease Risks
            profile = {p['canonical_name']: p['measured_value'] for p in parameters if p.get('canonical_name')}
            profile['age'] = user.get('age', 40)
            profile['gender'] = gender

            predictor = DiseasePredictor()
            risks = predictor.predict_all(profile)

            # 5. Calculate Health Score
            scorer = HealthScoreCalculator()
            health_score = scorer.calculate_score(parameters, disease_risks=risks)

            # 6. Generate Recommendations
            recommender = RecommendationEngine()
            recs = recommender.generate_recommendations(parameters, disease_risks=risks)

            # 7. Save to Database
            report_id = db.save_full_analysis(
                user_id=user['id'],
                report_title=report_title or uploaded_file.name,
                file_name=uploaded_file.name,
                file_path=file_path,
                raw_text=raw_text,
                parameters=parameters,
                predictions=risks,
                health_score=health_score,
                recommendations=recs
            )

            st.session_state['active_report_id'] = report_id
            st.session_state['last_analysis'] = {
                "report_id": report_id,
                "parameters": parameters,
                "risks": risks,
                "health_score": health_score,
                "recommendations": recs
            }

            st.success(f"✅ Report Analyzed and Saved Successfully! (Report ID: {report_id})")

    # Render results either from fresh run or stored in session
    analysis = st.session_state.get('last_analysis')
    if analysis:
        st.markdown("---")
        st.markdown(
            """
            <div style="margin-bottom: 20px;">
                <h2 style="font-size: 1.6rem; color: #0f172a; margin: 0;">📊 Clinical Analysis & Risk Summary</h2>
                <p style="color: #64748b; margin: 4px 0 0 0;">Review extracted parameters, multi-disease predictions, and recommendations below.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Top Metric Cards
        score_val = analysis['health_score']['overall_score']
        score_grade = analysis['health_score']['rating']
        anomalies_cnt = analysis['health_score']['anomalies_count']

        st.markdown(
            f"""
            <div class="metric-grid-4">
                <div class="vibrant-metric-card purple">
                    <span class="vibrant-metric-label">Parameters Extracted</span>
                    <span class="vibrant-metric-num" style="color: #7c3aed;">{len(analysis['parameters'])}</span>
                    <span class="vibrant-metric-hint">Biomarkers parsed</span>
                </div>
                <div class="vibrant-metric-card {'danger' if anomalies_cnt else 'success'}">
                    <span class="vibrant-metric-label">Detected Anomalies</span>
                    <span class="vibrant-metric-num" style="color: {'#ef4444' if anomalies_cnt else '#10b981'};">{anomalies_cnt}</span>
                    <span class="vibrant-metric-hint">Out-of-range flags</span>
                </div>
                <div class="vibrant-metric-card {'success' if score_val >= 75 else 'warning' if score_val >= 50 else 'danger'}">
                    <span class="vibrant-metric-label">Composite Health Score</span>
                    <span class="vibrant-metric-num" style="color: {'#10b981' if score_val >= 75 else '#f59e0b' if score_val >= 50 else '#ef4444'};">
                        {score_val:.1f} <span style="font-size: 1rem; color: #94a3b8;">/ 100</span>
                    </span>
                    <span class="vibrant-metric-hint">Status: <strong>{score_grade}</strong></span>
                </div>
                <div class="vibrant-metric-card success">
                    <span class="vibrant-metric-label">OCR & ML Pipeline</span>
                    <span class="vibrant-metric-num" style="color: #10b981;">Active</span>
                    <span class="vibrant-metric-hint">8 disease models ready</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Tabbed detailed views
        tab_params, tab_risks, tab_recs = st.tabs(["🔬 Extracted Biomarkers", "⚠️ AI Disease Predictions", "💡 Clinical Action Plan"])

        with tab_params:
            if analysis['parameters']:
                display_params = []
                for p in analysis['parameters']:
                    flag = p.get('flag', 'NORMAL')
                    ref = f"{p['reference_low']} - {p['reference_high']}" if p.get('reference_low') is not None else "Standard"
                    display_params.append({
                        "Biomarker": p['parameter_name'],
                        "Category": p['category'],
                        "Measured Value": f"{p['measured_value']} {p['unit']}",
                        "Reference Range": ref,
                        "Clinical Flag": f"🚨 {flag}" if flag in ['HIGH', 'CRITICAL'] else f"⚠️ {flag}" if flag == 'LOW' else f"✅ {flag}"
                    })
                st.dataframe(display_params, use_container_width=True)
            else:
                st.warning("No structured biomarkers could be recognized from the document.")

        with tab_risks:
            risk_cols = st.columns(4)
            for i, (disease, prob) in enumerate(analysis['risks'].items()):
                with risk_cols[i % 4]:
                    risk_pct = prob * 100
                    st.markdown(
                        f"""
                        <div class="vibrant-metric-card {'danger' if risk_pct >= 70 else 'warning' if risk_pct >= 40 else 'success'}" style="margin-bottom: 12px;">
                            <span class="vibrant-metric-label">{disease}</span>
                            <span class="vibrant-metric-num" style="font-size: 1.8rem; color: {'#ef4444' if risk_pct >= 70 else '#f59e0b' if risk_pct >= 40 else '#10b981'};">
                                {risk_pct:.1f}%
                            </span>
                            <span class="vibrant-metric-hint">Risk: <strong>{'High' if risk_pct >= 70 else 'Moderate' if risk_pct >= 40 else 'Low'}</strong></span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    st.progress(min(1.0, max(0.0, prob)))

        with tab_recs:
            if analysis['recommendations']:
                for rec in analysis['recommendations']:
                    with st.expander(f"📌 {rec.get('title', 'Recommendation')} ({rec.get('flag', 'Alert')})", expanded=True):
                        if rec.get('diet'):
                            st.markdown("**🥗 Dietary Advice:**")
                            for d in rec['diet']:
                                st.markdown(f"- {d}")
                        if rec.get('lifestyle'):
                            st.markdown("**🏃 Lifestyle & Physical Activity:**")
                            for l in rec['lifestyle']:
                                st.markdown(f"- {l}")
                        if rec.get('consult'):
                            st.markdown(f"**👨‍⚕️ Specialist Consultation:** {rec['consult']}")
            else:
                st.success("All analyzed parameters are within normal physiological bounds. Maintain a healthy lifestyle!")
