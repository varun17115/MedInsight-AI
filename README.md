# MedInsight AI — Intelligent Medical Report Analysis Platform

MedInsight AI is an advanced medical report analysis, multi-disease risk prediction, health scoring, explainable AI, and medical chatbot platform built with Streamlit, OpenCV, EasyOCR, Scikit-Learn, XGBoost, SHAP, and Google Gemini.

## Features

- **Document Processing Engine**:
  - Multi-engine text and table extraction using PyMuPDF, pdfplumber, and EasyOCR with OpenCV pre-processing (deskew, CLAHE contrast enhancement, adaptive thresholding, denoising).
  - Parameter extraction with regex patterns, fuzzy matching, alias canonical mapping, and clinical unit normalization.
  - Anomaly detection against reference ranges with low/normal/high/critical severity flags.

- **Machine Learning & Risk Prediction**:
  - Multi-disease predictive analytics covering 8 conditions: Diabetes, Heart Disease, Chronic Kidney Disease, Liver Disease, Stroke Risk, Anemia, Thyroid Dysfunction, and Breast Cancer Risk.
  - Explainable AI with SHAP (TreeSHAP & KernelSHAP) showing positive/negative feature contributions.
  - Composite Health Score (0–100) combining Metabolic, Cardiac, Renal, Hepatic, and Hematologic sub-scores.

- **Clinical Decision Support & Chatbot**:
  - Evidence-based actionable recommendations categorized by Diet, Exercise, Lifestyle, and Medical Consultation.
  - Side-by-side longitudinal report comparator with trend tracking.
  - Interactive AI medical assistant powered by Google Gemini with patient-context RAG.
  - Comprehensive clinical summary and downloadable PDF reports.

## Installation & Setup

1. **Clone and Navigate**:
   ```bash
   cd MedicalReportAnalyzer
   ```

2. **Create and Activate Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Copy `.env.example` to `.env` and provide your Google Gemini API key:
   ```bash
   cp .env.example .env
   ```

5. **Run the Application**:
   ```bash
   streamlit run app.py
   # Or on Windows:
   run.bat
   ```

## Project Structure
Refer to `ARCHITECTURE.md` for the complete system architecture, database schema, and module documentation.
