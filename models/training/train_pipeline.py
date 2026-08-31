"""
Training pipeline for all 8 medical disease prediction models.
"""
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import roc_auc_score, f1_score
from models.disease_configs import DISEASES, DiseaseSpec

try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

def train_single_model(spec: DiseaseSpec, model_type="auto"):
    os.makedirs(spec.model_path.parent, exist_ok=True)
    if not spec.raw_csv.exists():
        raise FileNotFoundError(f"Training dataset not found: {spec.raw_csv}")

    df = pd.read_csv(spec.raw_csv)
    X = df[spec.all_features]
    y = df[spec.target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    if model_type == "xgb" or (model_type == "auto" and HAS_XGB and spec.key in ["diabetes", "kidney_disease", "liver_disease", "anemia", "stroke"]):
        model = xgb.XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.08, eval_metric='logloss', random_state=42)
    else:
        model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)

    model.fit(X_train, y_train)

    y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else model.predict(X_test)
    y_pred = model.predict(X_test)

    auc = roc_auc_score(y_test, y_pred_proba)
    f1 = f1_score(y_test, y_pred)
    print(f"[{spec.display_name}] AUC-ROC: {auc:.4f} | F1: {f1:.4f}")

    joblib.dump(model, spec.model_path)
    return model

def train_all():
    print("Starting MedInsight AI 8-Disease Model Training Pipeline...")
    for key, spec in DISEASES.items():
        train_single_model(spec)
    print("All models trained and saved to models/saved_models/")

if __name__ == "__main__":
    train_all()
