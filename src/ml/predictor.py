import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import logging

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from models.disease_configs import DISEASES

class DiseasePredictor:
    def __init__(self, model_dir="models/saved_models"):
        self.model_dir = model_dir
        self.models = {}
        self._load_models()

    def _load_models(self):
        """Load all models defined in disease_configs."""
        for key, spec in DISEASES.items():
            if spec.model_path.exists():
                try:
                    self.models[key] = joblib.load(spec.model_path)
                except Exception as e:
                    logger.warning(f"Failed to load model for {key}: {e}")
            else:
                logger.warning(f"Model file not found for {key} at {spec.model_path}")

    def _extract_features_for_model(self, model, profile: dict) -> pd.DataFrame:
        """
        Dynamically extracts and constructs the feature row matching the exact
        feature names and order expected by the trained model (via feature_names_in_).
        """
        # Determine exact expected features
        if hasattr(model, "feature_names_in_"):
            expected_features = list(model.feature_names_in_)
        elif hasattr(model, "get_booster"):
            try:
                expected_features = model.get_booster().feature_names
            except Exception:
                expected_features = []
        else:
            expected_features = []

        row = {}
        age_val = float(profile.get('age', 45))
        gender_val = str(profile.get('gender', 'Male')).lower()
        is_male = 1 if ('m' in gender_val and 'f' not in gender_val) else 0

        for feat in expected_features:
            fl = feat.lower()
            val = None

            # Exact or partial key matches
            if feat in profile:
                val = profile[feat]
            elif fl in profile:
                val = profile[fl]
            elif fl in ['age']:
                val = age_val
            elif fl in ['sex', 'gender']:
                val = is_male
            elif fl in ['glucose', 'avg_glucose_level', 'avgglucoselevel', 'bgr']:
                val = profile.get('glucose_fasting', profile.get('glucose_random', 105.0))
            elif fl in ['bloodpressure', 'blood_pressure', 'bp', 'restingbp']:
                val = profile.get('blood_pressure', 120.0)
            elif fl in ['bmi']:
                val = profile.get('bmi', 24.5)
            elif fl in ['cholesterol', 'chol']:
                val = profile.get('cholesterol_total', 190.0)
            elif fl in ['hemoglobin', 'hemo']:
                val = profile.get('hemoglobin', 14.5 if is_male else 13.0)
            elif fl in ['creatinine', 'sc']:
                val = profile.get('creatinine', 0.95)
            elif fl in ['bu', 'blood_urea', 'blood_urea_nitrogen']:
                val = profile.get('blood_urea_nitrogen', profile.get('blood_urea', 20.0))
            elif fl in ['total_bilirubin', 'totalbilirubin']:
                val = profile.get('total_bilirubin', 0.8)
            elif fl in ['direct_bilirubin', 'directbilirubin']:
                val = profile.get('direct_bilirubin', 0.2)
            elif fl in ['alkaline_phosphotase', 'alkalinephosphotase']:
                val = profile.get('alkaline_phosphatase', 85.0)
            elif fl in ['alamine_aminotransferase', 'alamineaminotransferase']:
                val = profile.get('alt_sgpt', 28.0)
            elif fl in ['aspartate_aminotransferase', 'aspartateaminotransferase']:
                val = profile.get('ast_sgot', 26.0)
            elif fl in ['total_proteins', 'totalprotiens']:
                val = profile.get('total_proteins', 7.2)
            elif fl in ['albumin', 'al']:
                val = profile.get('albumin', 4.2)
            elif fl in ['rbc_count']:
                val = profile.get('rbc_count', 4.8)
            elif fl in ['mcv']:
                val = profile.get('mcv', 88.0)
            elif fl in ['mch']:
                val = profile.get('mch', 29.5)
            elif fl in ['iron']:
                val = profile.get('iron', 95.0)
            elif fl in ['tsh']:
                val = profile.get('tsh', 2.1)
            elif fl in ['ft3']:
                val = profile.get('ft3', 3.1)
            elif fl in ['ft4']:
                val = profile.get('ft4', 1.2)
            elif fl in ['hypertension']:
                val = 1 if profile.get('blood_pressure', 120.0) >= 140 else 0
            elif fl in ['heartdisease']:
                val = 0
            elif fl in ['fastingbs', 'fasting_blood_sugar_high']:
                val = 1 if profile.get('glucose_fasting', 100) > 120 else 0
            elif fl in ['maxhr', 'max_heart_rate']:
                val = 150.0
            elif fl in ['chestpaintype']:
                val = 0
            elif fl in ['sg']:
                val = 1.020
            elif fl in ['pregnancies', 'skinthickness', 'insulin', 'diabetespedigreefunction']:
                val = 0.0
            elif fl in ['brca_mutation', 'familyhistory']:
                val = 0
            elif fl in ['estrogenlevel']:
                val = 50.0

            if val is None:
                val = 0.0

            row[feat] = float(val)

        return pd.DataFrame([row])

    def _predict_disease(self, key: str, profile: dict) -> float:
        """Generic predictor using disease spec."""
        if key not in self.models:
            return 0.0

        model = self.models[key]
        features_df = self._extract_features_for_model(model, profile)

        try:
            if hasattr(model, "predict_proba"):
                prob = model.predict_proba(features_df)[0][1]
            else:
                prob = model.predict(features_df)[0]
            return float(prob)
        except Exception as e:
            logger.error(f"Prediction failed for {key}: {e}")
            return 0.0

    def predict_all(self, profile: dict) -> dict:
        """Predict probabilities for all supported diseases."""
        results = {}
        for key, spec in DISEASES.items():
            results[spec.display_name] = self._predict_disease(key, profile)
        return results
