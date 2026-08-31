"""
Evaluation script for trained disease models.
Computes ROC-AUC, F1, Accuracy, Sensitivity, and Specificity.
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score, confusion_matrix
from models.disease_configs import DISEASES

def evaluate_model(disease_key: str):
    spec = DISEASES.get(disease_key)
    if not spec:
        raise ValueError(f"Unknown disease key: {disease_key}")

    if not spec.model_path.exists():
        raise FileNotFoundError(f"Model file not found: {spec.model_path}")
    if not spec.raw_csv.exists():
        raise FileNotFoundError(f"Raw data file not found: {spec.raw_csv}")

    model = joblib.load(spec.model_path)
    df = pd.read_csv(spec.raw_csv)
    X = df[spec.all_features]
    y = df[spec.target]

    y_pred = model.predict(X)
    y_prob = model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else y_pred

    acc = accuracy_score(y, y_pred)
    f1 = f1_score(y, y_pred)
    auc = roc_auc_score(y, y_prob)

    tn, fp, fn, tp = confusion_matrix(y, y_pred).ravel()
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0

    return {
        "disease": spec.display_name,
        "accuracy": acc,
        "f1_score": f1,
        "roc_auc": auc,
        "sensitivity": sensitivity,
        "specificity": specificity
    }

def evaluate_all():
    results = []
    for key in DISEASES:
        res = evaluate_model(key)
        results.append(res)
        print(f"[{res['disease']}] Acc: {res['accuracy']:.3f} | F1: {res['f1_score']:.3f} | AUC: {res['roc_auc']:.3f}")
    return pd.DataFrame(results)

if __name__ == "__main__":
    evaluate_all()
