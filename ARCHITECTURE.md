# MedInsight AI — System Architecture & Project Blueprint

**Project:** MedInsight AI: Intelligent Medical Report Analysis, Multi-Disease Risk Prediction, Health Scoring, Explainable AI & Medical Chatbot Platform

**Approach:** Merge & extend two existing codebases (Healthcare Prediction Platform + MediAssist AI) — reuse all working components, build new layers on top.

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER (Streamlit UI)                     │
│                                                                         │
│  ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌───────────┐ ┌────────────┐  │
│  │  Login/   │ │  Upload  │ │ Prediction│ │  Health   │ │  Analytics │  │
│  │ Register  │ │  Report  │ │  Results  │ │   Score   │ │  & Trends  │  │
│  └──────────┘ └──────────┘ └───────────┘ └───────────┘ └────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌───────────┐ ┌────────────┐  │
│  │  Chatbot │ │  Report  │ │  Doctor   │ │  Profile  │ │  History   │  │
│  │   (RAG)  │ │ Compare  │ │  Summary  │ │ & Settings│ │  & Reports │  │
│  └──────────┘ └──────────┘ └───────────┘ └───────────┘ └────────────┘  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────┐
│                   DOCUMENT PROCESSING ENGINE                            │
│                                                                         │
│  ┌─────────────────────┐    ┌─────────────────────┐                     │
│  │   Digital PDF Path  │    │  Scanned/Image Path  │                    │
│  │  ┌───────────────┐  │    │  ┌───────────────┐   │                    │
│  │  │   PyMuPDF      │  │    │  │  OpenCV Preproc│   │                    │
│  │  │  (text extract)│  │    │  │  (deskew/CLAHE)│   │                    │
│  │  └───────┬───────┘  │    │  └───────┬───────┘   │                    │
│  │  ┌───────▼───────┐  │    │  ┌───────▼───────┐   │                    │
│  │  │  pdfplumber   │  │    │  │   EasyOCR      │   │                    │
│  │  │ (table extract)│  │    │  │  (text recog)  │   │                    │
│  │  └───────────────┘  │    │  └───────────────┘   │                    │
│  └──────────┬──────────┘    └──────────┬───────────┘                    │
│             └──────────────┬───────────┘                                │
│                            ▼                                            │
│  ┌─────────────────────────────────────────────┐                        │
│  │     Medical Parameter Extraction Engine       │                      │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────┐  │                      │
│  │  │  Regex   │ │  Fuzzy   │ │  Canonical   │  │                      │
│  │  │ Patterns │ │ Matching │ │   Mapper     │  │                      │
│  │  └──────────┘ └──────────┘ └──────────────┘  │                      │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────┐  │                      │
│  │  │  Unit    │ │ Reference│ │  Anomaly     │  │                      │
│  │  │Normalizer│ │  Ranges  │ │  Detector    │  │                      │
│  │  └──────────┘ └──────────┘ └──────────────┘  │                      │
│  └─────────────────────┬───────────────────────┘                        │
└────────────────────────┼────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────────────┐
│                 ML & PREDICTIVE ANALYTICS ENGINE                        │
│                                                                         │
│  Disease Models (8):                                                    │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                      │
│  │Diabetes │ │  Heart   │ │ Kidney  │ │  Liver  │                      │
│  │ XGBoost │ │   RF     │ │ XGBoost │ │ XGBoost │                      │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘                      │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                      │
│  │ Stroke  │ │ Anemia  │ │ Thyroid │ │ Breast  │                      │
│  │   RF    │ │ XGBoost │ │ XGBoost │ │ XGBoost │                      │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘                      │
│                                                                         │
│  ┌───────────────┐  ┌────────────────┐  ┌────────────────┐              │
│  │ SHAP Explainer│  │ Health Score   │  │ Model Registry │              │
│  │ (TreeSHAP /   │  │ Engine (0-100) │  │ (lazy load +   │              │
│  │  KernelSHAP)  │  │                │  │  caching)      │              │
│  └───────────────┘  └────────────────┘  └────────────────┘              │
└────────────────────────┬────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────────────┐
│            CLINICAL DECISION SUPPORT & CHATBOT                          │
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │  Recommendation  │  │  Report Compare  │  │  AI Chatbot      │      │
│  │  Engine (Rules)  │  │  Engine           │  │  (Gemini + RAG)  │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
│  ┌──────────────────┐  ┌──────────────────┐                             │
│  │  Doctor Summary  │  │  PDF Report      │                             │
│  │  Generator       │  │  (ReportLab)     │                             │
│  └──────────────────┘  └──────────────────┘                             │
└────────────────────────┬────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────────────┐
│                   PERSISTENCE LAYER (SQLite)                            │
│                                                                         │
│  ┌────────┐ ┌────────┐ ┌──────────────┐ ┌─────────────┐               │
│  │ users  │ │reports │ │  medical_    │ │ predictions │               │
│  │        │ │        │ │  parameters  │ │             │               │
│  └────────┘ └────────┘ └──────────────┘ └─────────────┘               │
│  ┌──────────────┐ ┌────────────────┐ ┌──────────────┐                  │
│  │ health_scores│ │recommendations │ │ chat_history │                  │
│  └──────────────┘ └────────────────┘ └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Complete Folder Structure

```
MedicalReportAnalyzer/
│
├── .streamlit/
│   └── config.toml                          # Streamlit theme config
│
├── assets/
│   ├── css/
│   │   └── style.css                        # Glassmorphism + modern healthcare CSS
│   ├── images/
│   │   ├── logo.png                         # App logo
│   │   └── default_avatar.png               # Profile placeholder
│   └── sample_reports/                      # Test medical reports
│       ├── sample_cbc_scan.png
│       ├── sample_lipid_digital.pdf
│       └── sample_metabolic_scan.pdf
│
├── data/
│   ├── raw/                                 # Training datasets (UCI/Kaggle + existing)
│   │   ├── diabetes.csv                     # [FROM: Healthcare synthetic + MediAssist]
│   │   ├── heart_statlog.csv                # [FROM: Healthcare synthetic]
│   │   ├── kidney_disease.csv               # [FROM: Healthcare synthetic + MediAssist]
│   │   ├── liver_patient.csv                # [FROM: Healthcare synthetic]
│   │   ├── stroke.csv                       # [FROM: Healthcare synthetic]
│   │   ├── anemia.csv                       # [FROM: MediAssist]
│   │   ├── thyroid.csv                      # [NEW: source from UCI/Kaggle]
│   │   └── breast_cancer.csv                # [NEW: sklearn.datasets]
│   ├── processed/                           # Feature-engineered datasets
│   └── reference_ranges.json                # [NEW] Clinical reference ranges + canonical mappings
│
├── database/
│   ├── __init__.py
│   ├── connection.py                        # [NEW] Thread-safe SQLite connection manager
│   ├── schema.sql                           # [NEW] DDL for all 7 tables
│   └── db_manager.py                        # [NEW] Repository-pattern CRUD operations
│
├── models/
│   ├── saved_models/                        # Serialized model pipelines (.joblib)
│   │   ├── diabetes_model.joblib            # [FROM: Healthcare training.py output]
│   │   ├── heart_model.joblib               # [FROM: Healthcare training.py output]
│   │   ├── kidney_model.joblib              # [FROM: Healthcare training.py output]
│   │   ├── liver_model.joblib               # [FROM: Healthcare training.py output]
│   │   ├── stroke_model.joblib              # [FROM: Healthcare training.py output]
│   │   ├── anemia_model.joblib              # [NEW: train from MediAssist XGBoost notebook]
│   │   ├── thyroid_model.joblib             # [NEW: train]
│   │   └── breast_cancer_model.joblib       # [NEW: train]
│   ├── training/
│   │   ├── __init__.py
│   │   ├── train_pipeline.py               # [FROM: Healthcare training.py — extended for 8 diseases]
│   │   ├── data_generation.py              # [FROM: Healthcare data_generation.py — keep all 5 generators]
│   │   └── evaluate.py                     # [NEW] Unified evaluation (AUC-ROC, F1, confusion matrix)
│   └── disease_configs.py                   # [FROM: Healthcare config.py — add anemia/thyroid/breast cancer specs]
│
├── src/
│   ├── __init__.py
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── authenticator.py                # [NEW] bcrypt password hashing + session management
│   │   └── validators.py                   # [NEW] Email/password policy validators
│   │
│   ├── ocr/
│   │   ├── __init__.py
│   │   ├── preprocessor.py                 # [NEW] OpenCV: deskew, CLAHE, threshold, denoise
│   │   ├── text_extractor.py               # [NEW] PyMuPDF + pdfplumber for digital PDFs
│   │   └── ocr_engine.py                   # [NEW] EasyOCR wrapper for scanned docs/images
│   │
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── regex_patterns.py               # [FROM: MediAssist ocr_module.py patterns — expanded]
│   │   ├── fuzzy_matcher.py                # [NEW] Fuzzy matching for parameter names
│   │   ├── canonical_mapper.py             # [NEW] Alias→canonical mapping (FBS→glucose_fasting)
│   │   ├── unit_normalizer.py              # [NEW] Unit conversion (mmol/L↔mg/dL, etc.)
│   │   └── anomaly_detector.py             # [FROM: MediAssist disease_predictor.py severity logic — expanded]
│   │
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── predictor.py                    # [FROM: Healthcare prediction.py — ModelRegistry + DiseaseModel]
│   │   ├── shap_explainer.py               # [FROM: Healthcare explainability.py — as-is]
│   │   └── health_score.py                 # [NEW] Composite 0-100 health scoring engine
│   │
│   ├── recommender/
│   │   ├── __init__.py
│   │   ├── rule_engine.py                  # [FROM: Healthcare recommendations.py — extended for 8 diseases]
│   │   └── knowledge_base.py               # [NEW] Evidence-based recommendation templates
│   │
│   ├── chatbot/
│   │   ├── __init__.py
│   │   ├── gemini_client.py                # [FROM: MediAssist chatbot.py — refactored, no hardcoded keys]
│   │   ├── context_builder.py              # [NEW] RAG context from patient data
│   │   └── chat_manager.py                 # [NEW] Conversation history + SQLite persistence
│   │
│   ├── comparison/
│   │   ├── __init__.py
│   │   └── report_comparator.py            # [NEW] Compare current vs previous report
│   │
│   └── reporting/
│       ├── __init__.py
│       ├── pdf_generator.py                # [FROM: Healthcare pdf_report.py — extended]
│       └── doctor_summary.py               # [NEW] Clinical summary generator for physicians
│
├── views/
│   ├── __init__.py
│   ├── login_page.py                       # [NEW] Login + Register UI
│   ├── dashboard_page.py                   # [FROM: Healthcare dashboard/app.py — redesigned]
│   ├── upload_page.py                      # [NEW] Upload report + extraction preview + parameter editor
│   ├── prediction_page.py                  # [FROM: Healthcare common.py — redesigned]
│   ├── health_score_page.py                # [NEW] Composite score + radar chart + sub-scores
│   ├── analytics_page.py                   # [NEW] Historical trends (Plotly time-series)
│   ├── chatbot_page.py                     # [FROM: MediAssist app.py chat section — redesigned]
│   ├── comparison_page.py                  # [NEW] Side-by-side report comparison
│   ├── profile_page.py                     # [NEW] User demographics + settings
│   ├── history_page.py                     # [NEW] Past reports list + doctor summary view
│   └── components/
│       ├── __init__.py
│       ├── sidebar.py                      # [NEW] Navigation sidebar with user info
│       ├── metric_cards.py                 # [FROM: Healthcare theme.py — adapted]
│       └── charts.py                       # [NEW] Reusable Plotly chart components
│
├── tests/
│   ├── __init__.py
│   ├── test_auth.py                        # [NEW]
│   ├── test_ocr.py                         # [NEW]
│   ├── test_parser.py                      # [NEW]
│   ├── test_models.py                      # [FROM: Healthcare test_prediction.py — extended]
│   ├── test_db.py                          # [NEW]
│   ├── test_recommendations.py             # [FROM: Healthcare test_recommendations.py]
│   ├── test_health_score.py                # [NEW]
│   └── test_chatbot.py                     # [NEW]
│
├── app.py                                  # Main Streamlit entrypoint + page routing
├── requirements.txt                        # All dependencies (merged + new)
├── .env.example                            # API keys placeholder (GEMINI_API_KEY)
├── README.md                               # Project documentation
├── ARCHITECTURE.md                         # This file
└── run.bat                                 # Quick launch script
```

### Source Mapping Legend

| Tag | Meaning |
|-----|---------|
| `[FROM: Healthcare ...]` | Reused from Healthcare Prediction Platform (modify/extend as needed) |
| `[FROM: MediAssist ...]` | Reused from MediAssist AI (extract, refactor, integrate) |
| `[NEW]` | Built from scratch |

---

## 3. Database Schema

```sql
-- ============================================================
-- MedInsight AI — SQLite Schema
-- ============================================================

-- 1. Users
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    age INTEGER,
    gender VARCHAR(10) CHECK(gender IN ('Male', 'Female', 'Other')),
    blood_group VARCHAR(5),
    height_cm REAL,
    weight_kg REAL,
    medical_conditions TEXT,              -- JSON array of pre-existing conditions
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Medical Reports
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    report_title VARCHAR(150),
    report_type VARCHAR(50) DEFAULT 'General',
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size_kb REAL,
    raw_extracted_text TEXT,
    extraction_method VARCHAR(20),        -- 'pymupdf', 'pdfplumber', 'easyocr', 'manual'
    ocr_confidence REAL,
    report_date DATE,
    upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Processed',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Extracted Medical Parameters
CREATE TABLE IF NOT EXISTS medical_parameters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    parameter_name VARCHAR(100) NOT NULL,
    canonical_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),                 -- Hematology, Renal, Hepatic, Lipid, Metabolic, Thyroid
    measured_value REAL NOT NULL,
    unit VARCHAR(30) NOT NULL,
    normalized_value REAL,                -- Value converted to standard unit
    normalized_unit VARCHAR(30),
    reference_low REAL,
    reference_high REAL,
    flag VARCHAR(20) NOT NULL,            -- LOW, NORMAL, HIGH, CRITICAL
    confidence_score REAL DEFAULT 1.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE
);

-- 4. Disease Predictions
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    disease_type VARCHAR(50) NOT NULL,    -- All 8 diseases
    risk_probability REAL NOT NULL,
    risk_level VARCHAR(20) NOT NULL,      -- Low, Moderate, High, Critical
    model_name VARCHAR(50) NOT NULL,
    model_version VARCHAR(20) DEFAULT '1.0',
    shap_values_json TEXT,                -- JSON: top contributing features + SHAP values
    input_features_json TEXT,             -- JSON: feature values used for prediction
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE
);

-- 5. Composite Health Scores
CREATE TABLE IF NOT EXISTS health_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER UNIQUE NOT NULL,
    overall_score REAL NOT NULL,           -- 0-100
    metabolic_score REAL,
    cardiac_score REAL,
    renal_score REAL,
    hepatic_score REAL,
    hematologic_score REAL,
    score_grade VARCHAR(15) NOT NULL,     -- Excellent, Good, Fair, Poor, Critical
    score_breakdown_json TEXT,            -- JSON: per-parameter contribution
    calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE
);

-- 6. Recommendations
CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    category VARCHAR(50) NOT NULL,        -- Diet, Exercise, Lifestyle, Medical Consultation, Medication
    priority VARCHAR(20) NOT NULL,        -- High, Medium, Low
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    target_condition VARCHAR(50),         -- Which disease/risk this addresses
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE
);

-- 7. Chat History
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    report_id INTEGER,                    -- NULL for general queries
    role VARCHAR(10) NOT NULL,            -- 'user' or 'assistant'
    message TEXT NOT NULL,
    context_summary TEXT,                 -- What patient data was in context
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE SET NULL
);

-- Indices
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_reports_user_id ON reports(user_id);
CREATE INDEX IF NOT EXISTS idx_params_report_id ON medical_parameters(report_id);
CREATE INDEX IF NOT EXISTS idx_params_canonical ON medical_parameters(canonical_name);
CREATE INDEX IF NOT EXISTS idx_predictions_report_id ON predictions(report_id);
CREATE INDEX IF NOT EXISTS idx_predictions_disease ON predictions(disease_type);
CREATE INDEX IF NOT EXISTS idx_health_scores_report_id ON health_scores(report_id);
CREATE INDEX IF NOT EXISTS idx_chat_user_id ON chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_report_id ON chat_history(report_id);
```

---

## 4. Development Roadmap & Implementation Order

### Phase 1: Foundation (Days 1-3)
```
Step 1.1  Scaffold project folder structure
Step 1.2  Merge requirements.txt from both projects + new deps
Step 1.3  Create .streamlit/config.toml
Step 1.4  Create database/schema.sql
Step 1.5  Build database/connection.py (thread-safe SQLite manager)
Step 1.6  Build database/db_manager.py (CRUD for all 7 tables)
Step 1.7  Write tests/test_db.py
```

### Phase 2: Authentication (Days 4-5)
```
Step 2.1  Build src/auth/validators.py (email, password policy)
Step 2.2  Build src/auth/authenticator.py (bcrypt hash, login, register, sessions)
Step 2.3  Build views/login_page.py (login + register UI)
Step 2.4  Write tests/test_auth.py
```

### Phase 3: OCR & Document Processing (Days 6-10)
```
Step 3.1  Build src/ocr/preprocessor.py (OpenCV pipeline)
Step 3.2  Build src/ocr/text_extractor.py (PyMuPDF + pdfplumber)
Step 3.3  Build src/ocr/ocr_engine.py (EasyOCR wrapper)
Step 3.4  Build data/reference_ranges.json
Step 3.5  Build src/parser/regex_patterns.py (extract from MediAssist + expand)
Step 3.6  Build src/parser/fuzzy_matcher.py
Step 3.7  Build src/parser/canonical_mapper.py
Step 3.8  Build src/parser/unit_normalizer.py
Step 3.9  Build src/parser/anomaly_detector.py (extract from MediAssist + expand)
Step 3.10 Write tests/test_ocr.py + tests/test_parser.py
```

### Phase 4: ML Models & Prediction (Days 11-16)
```
Step 4.1  Port Healthcare config.py → models/disease_configs.py (add 3 new diseases)
Step 4.2  Port Healthcare training.py → models/training/train_pipeline.py
Step 4.3  Port Healthcare data_generation.py → models/training/data_generation.py
Step 4.4  Train all 8 models, serialize to models/saved_models/
Step 4.5  Port Healthcare prediction.py → src/ml/predictor.py
Step 4.6  Port Healthcare explainability.py → src/ml/shap_explainer.py
Step 4.7  Build src/ml/health_score.py (composite scoring engine)
Step 4.8  Build models/training/evaluate.py
Step 4.9  Write tests/test_models.py + tests/test_health_score.py
```

### Phase 5: Recommendations & Reporting (Days 17-20)
```
Step 5.1  Port Healthcare recommendations.py → src/recommender/rule_engine.py (add 3 diseases)
Step 5.2  Build src/recommender/knowledge_base.py
Step 5.3  Port Healthcare pdf_report.py → src/reporting/pdf_generator.py (extend)
Step 5.4  Build src/reporting/doctor_summary.py
Step 5.5  Build src/comparison/report_comparator.py
```

### Phase 6: AI Chatbot (Days 21-23)
```
Step 6.1  Refactor MediAssist chatbot.py → src/chatbot/gemini_client.py
Step 6.2  Build src/chatbot/context_builder.py (RAG context assembly)
Step 6.3  Build src/chatbot/chat_manager.py (conversation history + SQLite)
Step 6.4  Write tests/test_chatbot.py
```

### Phase 7: Streamlit UI (Days 24-30)
```
Step 7.1  Build assets/css/style.css (glassmorphism theme)
Step 7.2  Build views/components/sidebar.py
Step 7.3  Build views/components/metric_cards.py (port from Healthcare theme.py)
Step 7.4  Build views/components/charts.py
Step 7.5  Build views/dashboard_page.py
Step 7.6  Build views/upload_page.py
Step 7.7  Build views/prediction_page.py
Step 7.8  Build views/health_score_page.py
Step 7.9  Build views/analytics_page.py (historical trends + Plotly)
Step 7.10 Build views/chatbot_page.py
Step 7.11 Build views/comparison_page.py
Step 7.12 Build views/profile_page.py
Step 7.13 Build views/history_page.py
Step 7.14 Build app.py (main entrypoint + page router)
```

### Phase 8: Integration & Polish (Days 31-35)
```
Step 8.1  End-to-end integration testing
Step 8.2  Sample report testing (CBC, LFT, KFT, Lipid)
Step 8.3  Edge case handling (missing values, partial OCR, empty reports)
Step 8.4  UI polish, responsive layout, error states
Step 8.5  README.md + deployment guide
Step 8.6  run.bat quick launcher
```

---

## 5. Component Reuse Map

### From Healthcare Prediction Platform
| Source File | Target Location | Changes |
|---|---|---|
| `src/config.py` | `models/disease_configs.py` | Add anemia, thyroid, breast cancer DiseaseSpec |
| `src/training.py` | `models/training/train_pipeline.py` | Add XGBoost option, train 8 models |
| `src/data_generation.py` | `models/training/data_generation.py` | Keep all 5 generators as-is |
| `src/prediction.py` | `src/ml/predictor.py` | Extend ModelRegistry for 8 diseases |
| `src/explainability.py` | `src/ml/shap_explainer.py` | Minimal changes — works generically |
| `src/recommendations.py` | `src/recommender/rule_engine.py` | Add rules for anemia, thyroid, breast cancer |
| `src/pdf_report.py` | `src/reporting/pdf_generator.py` | Add health score section, more parameters |
| `dashboard/theme.py` | `views/components/metric_cards.py` | Extract card rendering logic |
| `dashboard/common.py` | `views/prediction_page.py` | Redesign with new UI, keep predict→SHAP→recs flow |
| `tests/*` | `tests/` | Port applicable tests |

### From MediAssist AI
| Source File | Target Location | Changes |
|---|---|---|
| `ocr_module.py` (regex patterns) | `src/parser/regex_patterns.py` | Extract 14 patterns, expand to 15+ |
| `ocr_module.py` (valid ranges) | `data/reference_ranges.json` | Convert dict to structured JSON |
| `disease_predictor.py` (severity) | `src/parser/anomaly_detector.py` | Extract severity logic, generalize |
| `chatbot.py` | `src/chatbot/gemini_client.py` | Remove hardcoded key, add env config |
| `Datasets/*.csv` | `data/raw/` | Merge with Healthcare datasets |

---

## 6. Key Dependencies (requirements.txt)

```
# Core
streamlit>=1.28.0
python-dotenv>=1.0.0

# Database
# (sqlite3 is stdlib — no external dep)

# Auth
bcrypt>=4.1.0

# OCR & Document Processing
PyMuPDF>=1.23.0
pdfplumber>=0.10.0
easyocr>=1.7.0
opencv-python>=4.8.0

# ML & Data
scikit-learn>=1.3.0
xgboost>=2.0.0
lightgbm>=4.1.0
shap>=0.43.0
pandas>=2.1.0
numpy>=1.24.0
joblib>=1.3.0

# Fuzzy Matching
rapidfuzz>=3.5.0

# Visualization
plotly>=5.18.0
matplotlib>=3.8.0

# PDF Generation
reportlab>=4.0.0

# Chatbot
google-generativeai>=0.3.0

# Image Processing
Pillow>=10.0.0

# Utilities
openpyxl>=3.1.0
```
