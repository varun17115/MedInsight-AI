"""
Central disease configuration for MedInsight AI platform.
Defines schemas, features, targets, and model mapping for 8 disease categories.
"""
from dataclasses import dataclass, field
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = ROOT_DIR / "data" / "raw"
DATA_PROCESSED_DIR = ROOT_DIR / "data" / "processed"
MODELS_DIR = ROOT_DIR / "models" / "saved_models"

@dataclass(frozen=True)
class DiseaseSpec:
    key: str
    display_name: str
    target: str
    numeric_features: list[str]
    categorical_features: list[str] = field(default_factory=list)
    positive_label: int = 1

    @property
    def all_features(self) -> list[str]:
        return self.numeric_features + self.categorical_features

    @property
    def raw_csv(self) -> Path:
        return DATA_RAW_DIR / f"{self.key}.csv"

    @property
    def model_path(self) -> Path:
        # Match actual saved model filenames with algorithm suffix
        algo_map = {
            "diabetes": "diabetes_xgb.joblib",
            "heart_disease": "heart_rf.joblib",
            "kidney_disease": "kidney_xgb.joblib",
            "liver_disease": "liver_xgb.joblib",
            "stroke": "stroke_xgb.joblib",
            "anemia": "anemia_xgb.joblib",
            "thyroid": "thyroid_rf.joblib",
            "breast_cancer": "breastcancer_rf.joblib"
        }
        filename = algo_map.get(self.key, f"{self.key}_model.joblib")
        return MODELS_DIR / filename


DISEASES: dict[str, DiseaseSpec] = {
    "diabetes": DiseaseSpec(
        key="diabetes",
        display_name="Diabetes",
        target="Outcome",
        numeric_features=[
            "pregnancies", "glucose", "blood_pressure", "skin_thickness",
            "insulin", "bmi", "diabetes_pedigree", "age",
        ],
    ),
    "heart_disease": DiseaseSpec(
        key="heart_disease",
        display_name="Heart Disease",
        target="target",
        numeric_features=[
            "age", "resting_bp", "cholesterol", "max_heart_rate",
            "oldpeak", "num_major_vessels",
        ],
        categorical_features=[
            "sex", "chest_pain_type", "fasting_blood_sugar_high",
            "resting_ecg_abnormal", "exercise_angina", "st_slope", "thalassemia",
        ],
    ),
    "stroke": DiseaseSpec(
        key="stroke",
        display_name="Stroke",
        target="Stroke",
        numeric_features=["Age", "AvgGlucoseLevel", "BMI"],
        categorical_features=["Hypertension", "HeartDisease"],
    ),
    "liver_disease": DiseaseSpec(
        key="liver_disease",
        display_name="Liver Disease",
        target="Disease",
        numeric_features=[
            "age", "total_bilirubin", "direct_bilirubin",
            "alkaline_phosphotase", "alamine_aminotransferase",
            "aspartate_aminotransferase", "total_proteins",
            "albumin", "albumin_globulin_ratio",
        ],
        categorical_features=["gender"],
    ),
    "kidney_disease": DiseaseSpec(
        key="kidney_disease",
        display_name="Chronic Kidney Disease",
        target="Disease",
        numeric_features=[
            "age", "blood_pressure", "blood_glucose_random", "blood_urea",
            "serum_creatinine", "sodium", "potassium", "hemoglobin",
            "packed_cell_volume", "white_blood_cell_count", "albumin",
        ],
        categorical_features=["hypertension", "diabetes_mellitus", "appetite_poor", "anemia"],
    ),
    "anemia": DiseaseSpec(
        key="anemia",
        display_name="Anemia",
        target="Disease",
        numeric_features=["Hemoglobin", "RBC_Count", "MCV", "MCH", "Iron"],
    ),
    "thyroid": DiseaseSpec(
        key="thyroid",
        display_name="Thyroid Dysfunction",
        target="Disease",
        numeric_features=["TSH", "FT3", "FT4", "Age"],
        categorical_features=["Sex"],
    ),
    "breast_cancer": DiseaseSpec(
        key="breast_cancer",
        display_name="Breast Cancer Risk",
        target="Disease",
        numeric_features=["Age", "EstrogenLevel"],
        categorical_features=["BRCA_Mutation", "FamilyHistory"],
    ),
}
