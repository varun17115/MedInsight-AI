import shap
import pandas as pd
import joblib
import os

class SHAPExplainer:
    def __init__(self, model_dir="models/saved_models", data_dir="data/raw"):
        self.model_dir = model_dir
        self.data_dir = data_dir
        self.models = {}
        self.explainers = {}
        self.data_snapshots = {
            'diabetes': 'diabetes.csv',
            'heart': 'heart_data.csv',
            'kidney': 'ckd.csv',
            'liver': 'liver_disease.csv'
        }
        self._load_models_and_explainers()

    def _load_models_and_explainers(self):
        for name, filename in self.data_snapshots.items():
            model_path = f"{self.model_dir}/{self._get_model_filename(name)}"
            data_path = f"{self.data_dir}/{filename}"

            if os.path.exists(model_path) and os.path.exists(data_path):
                try:
                    self.models[name] = joblib.load(model_path)
                    # Load a subset of data for background distribution
                    df = pd.read_csv(data_path)
                    # Drop label column
                    drop_col = 'Outcome' if name == 'diabetes' else \
                               'HeartDisease' if name == 'heart' else \
                               'classification' if name == 'kidney' else 'Dataset'
                    X = df.drop(columns=[drop_col])
                    self.explainers[name] = shap.TreeExplainer(self.models[name])
                    self.data_snapshots[name] = X.sample(min(100, len(X)))
                except Exception:
                    pass

    def _get_model_filename(self, name):
        return f"{name}_xgb.joblib" if name != 'heart' else "heart_rf.joblib"

    def explain(self, model_name, features_df):
        if model_name not in self.explainers:
            return None
        shap_values = self.explainers[model_name].shap_values(features_df)
        return shap_values
