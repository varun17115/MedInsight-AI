"""
Data generation module for synthetic datasets across all supported diseases.
"""
import os
import pandas as pd
import numpy as np

def generate_all_datasets(output_dir="data/raw"):
    os.makedirs(output_dir, exist_ok=True)
    np.random.seed(42)
    n = 1000

    # 1. Diabetes
    df_dia = pd.DataFrame({
        'pregnancies': np.random.randint(0, 10, n),
        'glucose': np.random.normal(120, 30, n).clip(60, 250),
        'blood_pressure': np.random.normal(80, 15, n).clip(50, 140),
        'skin_thickness': np.random.normal(20, 10, n).clip(5, 60),
        'insulin': np.random.normal(80, 50, n).clip(10, 300),
        'bmi': np.random.normal(28, 6, n).clip(15, 50),
        'diabetes_pedigree': np.random.uniform(0.1, 1.5, n),
        'age': np.random.randint(20, 80, n),
    })
    df_dia['Outcome'] = ((df_dia['glucose'] > 140) | (df_dia['bmi'] > 32)).astype(int)
    df_dia.to_csv(f"{output_dir}/diabetes.csv", index=False)

    # 2. Heart Disease
    df_heart = pd.DataFrame({
        'age': np.random.randint(30, 80, n),
        'sex': np.random.binomial(1, 0.6, n),
        'chest_pain_type': np.random.randint(0, 4, n),
        'resting_bp': np.random.normal(130, 20, n).clip(90, 200),
        'cholesterol': np.random.normal(240, 50, n).clip(120, 400),
        'fasting_blood_sugar_high': np.random.binomial(1, 0.2, n),
        'resting_ecg_abnormal': np.random.randint(0, 3, n),
        'max_heart_rate': np.random.normal(150, 25, n).clip(70, 210),
        'exercise_angina': np.random.binomial(1, 0.3, n),
        'oldpeak': np.random.exponential(1.0, n).clip(0, 6),
        'st_slope': np.random.randint(0, 3, n),
        'num_major_vessels': np.random.randint(0, 4, n),
        'thalassemia': np.random.randint(0, 3, n)
    })
    df_heart['target'] = ((df_heart['cholesterol'] > 260) | (df_heart['oldpeak'] > 2.0)).astype(int)
    df_heart.to_csv(f"{output_dir}/heart_disease.csv", index=False)

    # 3. Stroke
    df_stroke = pd.DataFrame({
        'Age': np.random.uniform(20, 90, n),
        'Hypertension': np.random.binomial(1, 0.3, n),
        'HeartDisease': np.random.binomial(1, 0.2, n),
        'AvgGlucoseLevel': np.random.normal(120, 40, n),
        'BMI': np.random.normal(28, 5, n)
    })
    df_stroke['Stroke'] = (((df_stroke['Age'] > 60) & (df_stroke['Hypertension'] == 1)) | (df_stroke['AvgGlucoseLevel'] > 180)).astype(int)
    df_stroke.to_csv(f"{output_dir}/stroke.csv", index=False)

    # 4. Kidney
    df_ckd = pd.DataFrame({
        'age': np.random.randint(20, 80, n),
        'blood_pressure': np.random.normal(80, 15, n),
        'blood_glucose_random': np.random.normal(130, 40, n),
        'blood_urea': np.random.normal(45, 20, n),
        'serum_creatinine': np.random.normal(1.2, 0.8, n),
        'sodium': np.random.normal(138, 5, n),
        'potassium': np.random.normal(4.3, 0.6, n),
        'hemoglobin': np.random.normal(13, 2, n),
        'packed_cell_volume': np.random.normal(40, 6, n),
        'white_blood_cell_count': np.random.normal(8000, 2000, n),
        'albumin': np.random.randint(0, 5, n),
        'hypertension': np.random.binomial(1, 0.3, n),
        'diabetes_mellitus': np.random.binomial(1, 0.25, n),
        'appetite_poor': np.random.binomial(1, 0.15, n),
        'anemia': np.random.binomial(1, 0.2, n)
    })
    df_ckd['Disease'] = ((df_ckd['serum_creatinine'] > 1.5) | (df_ckd['blood_urea'] > 60)).astype(int)
    df_ckd.to_csv(f"{output_dir}/kidney_disease.csv", index=False)

    # 5. Liver
    df_liver = pd.DataFrame({
        'age': np.random.randint(18, 80, n),
        'gender': np.random.binomial(1, 0.6, n),
        'total_bilirubin': np.random.lognormal(0.2, 0.6, n),
        'direct_bilirubin': np.random.lognormal(-0.5, 0.6, n),
        'alkaline_phosphotase': np.random.normal(200, 80, n).clip(50, 600),
        'alamine_aminotransferase': np.random.normal(40, 30, n).clip(10, 250),
        'aspartate_aminotransferase': np.random.normal(45, 35, n).clip(10, 250),
        'total_proteins': np.random.normal(6.5, 1.0, n),
        'albumin': np.random.normal(3.5, 0.6, n),
        'albumin_globulin_ratio': np.random.normal(1.0, 0.3, n)
    })
    df_liver['Disease'] = ((df_liver['total_bilirubin'] > 2.0) | (df_liver['alamine_aminotransferase'] > 80)).astype(int)
    df_liver.to_csv(f"{output_dir}/liver_disease.csv", index=False)

    # 6. Anemia
    df_anemia = pd.DataFrame({
        'Hemoglobin': np.random.normal(13, 2.5, n),
        'RBC_Count': np.random.normal(4.5, 0.8, n),
        'MCV': np.random.normal(85, 10, n),
        'MCH': np.random.normal(29, 3, n),
        'Iron': np.random.normal(100, 35, n)
    })
    df_anemia['Disease'] = ((df_anemia['Hemoglobin'] < 11.5) | (df_anemia['Iron'] < 50)).astype(int)
    df_anemia.to_csv(f"{output_dir}/anemia.csv", index=False)

    # 7. Thyroid
    df_thyroid = pd.DataFrame({
        'TSH': np.random.lognormal(0.6, 0.9, n),
        'FT3': np.random.normal(3.2, 0.6, n),
        'FT4': np.random.normal(1.2, 0.4, n),
        'Age': np.random.randint(18, 85, n),
        'Sex': np.random.binomial(1, 0.5, n)
    })
    df_thyroid['Disease'] = ((df_thyroid['TSH'] > 5.0) | (df_thyroid['TSH'] < 0.3)).astype(int)
    df_thyroid.to_csv(f"{output_dir}/thyroid.csv", index=False)

    # 8. Breast Cancer
    df_bc = pd.DataFrame({
        'Age': np.random.randint(25, 80, n),
        'BRCA_Mutation': np.random.binomial(1, 0.08, n),
        'FamilyHistory': np.random.binomial(1, 0.15, n),
        'EstrogenLevel': np.random.normal(110, 45, n)
    })
    df_bc['Disease'] = ((df_bc['BRCA_Mutation'] == 1) | ((df_bc['Age'] > 55) & (df_bc['FamilyHistory'] == 1))).astype(int)
    df_bc.to_csv(f"{output_dir}/breast_cancer.csv", index=False)

if __name__ == "__main__":
    generate_all_datasets()
