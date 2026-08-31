import os
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split

os.makedirs("models/saved_models", exist_ok=True)
os.makedirs("data/raw", exist_ok=True)

def generate_and_train_stroke():
    # Stroke Features: 'Age', 'Hypertension', 'HeartDisease', 'AvgGlucoseLevel', 'BMI'
    np.random.seed(42)
    n = 1000
    age = np.random.uniform(20, 90, n)
    ht = np.random.binomial(1, age/100 * 0.5)
    hd = np.random.binomial(1, age/100 * 0.3)
    gl = np.random.normal(120, 40, n)
    bmi = np.random.normal(28, 5, n)

    # Target
    risk = (age/100) * 0.4 + (ht * 0.2) + (hd * 0.2) + (gl > 150)*0.1 + (bmi > 30)*0.1
    stroke = np.random.binomial(1, risk)

    df = pd.DataFrame({'Age': age, 'Hypertension': ht, 'HeartDisease': hd, 'AvgGlucoseLevel': gl, 'BMI': bmi, 'Stroke': stroke})
    df.to_csv("data/raw/stroke_data.csv", index=False)

    X = df.drop(columns=['Stroke'])
    y = df['Stroke']

    try:
        import xgboost as xgb
        model = xgb.XGBClassifier(eval_metric='logloss', random_state=42)
    except:
        model = GradientBoostingClassifier(random_state=42)

    model.fit(X, y)
    joblib.dump(model, "models/saved_models/stroke_xgb.joblib")
    print("Saved Stroke model")

def generate_and_train_thyroid():
    # Thyroid Features: 'TSH', 'FT3', 'FT4', 'Age', 'Sex' (1=Male, 0=Female)
    np.random.seed(42)
    n = 1000
    tsh = np.random.lognormal(mean=0.5, sigma=0.8, size=n)
    ft3 = np.random.normal(3.5, 0.5, n)
    ft4 = np.random.normal(1.2, 0.3, n)
    age = np.random.uniform(20, 80, n)
    sex = np.random.binomial(1, 0.5, n)

    # Target (Hypo or hyper - simplistic risk)
    risk = ((tsh > 4.0) | (tsh < 0.4)) * 0.6 + (ft4 < 0.8) * 0.3 + (ft4 > 1.8) * 0.3
    risk = np.clip(risk + np.random.uniform(-0.1, 0.1, n), 0, 1)
    disease = np.random.binomial(1, risk)

    df = pd.DataFrame({'TSH': tsh, 'FT3': ft3, 'FT4': ft4, 'Age': age, 'Sex': sex, 'Disease': disease})
    df.to_csv("data/raw/thyroid_data.csv", index=False)

    X = df.drop(columns=['Disease'])
    y = df['Disease']

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    joblib.dump(model, "models/saved_models/thyroid_rf.joblib")
    print("Saved Thyroid model")

def generate_and_train_anemia():
    # Anemia Features: 'Hemoglobin', 'RBC_Count', 'MCV', 'MCH', 'Iron'
    np.random.seed(42)
    n = 1000
    hb = np.random.normal(13, 2, n)
    rbc = np.random.normal(4.5, 0.8, n)
    mcv = np.random.normal(85, 10, n)
    mch = np.random.normal(29, 3, n)
    iron = np.random.normal(100, 30, n)

    # Target
    risk = (hb < 12) * 0.5 + (rbc < 4.0) * 0.2 + (iron < 60) * 0.3
    risk = np.clip(risk + np.random.uniform(0, 0.1, n), 0, 1)
    disease = np.random.binomial(1, risk)

    df = pd.DataFrame({'Hemoglobin': hb, 'RBC_Count': rbc, 'MCV': mcv, 'MCH': mch, 'Iron': iron, 'Disease': disease})
    df.to_csv("data/raw/anemia_data.csv", index=False)

    X = df.drop(columns=['Disease'])
    y = df['Disease']

    try:
        import xgboost as xgb
        model = xgb.XGBClassifier(eval_metric='logloss', random_state=42)
    except:
        model = GradientBoostingClassifier(random_state=42)

    model.fit(X, y)
    joblib.dump(model, "models/saved_models/anemia_xgb.joblib")
    print("Saved Anemia model")

def generate_and_train_breast_cancer():
    # Breast Cancer (Synthetic clinical params): 'Age', 'BRCA_Mutation', 'FamilyHistory', 'EstrogenLevel'
    np.random.seed(42)
    n = 1000
    age = np.random.uniform(30, 80, n)
    brca = np.random.binomial(1, 0.05, n) # rare
    fh = np.random.binomial(1, 0.1, n)
    est = np.random.normal(100, 40, n)

    risk = (age/100) * 0.2 + (brca) * 0.6 + (fh) * 0.2 + (est > 150)*0.1
    risk = np.clip(risk, 0, 1)
    disease = np.random.binomial(1, risk)

    df = pd.DataFrame({'Age': age, 'BRCA_Mutation': brca, 'FamilyHistory': fh, 'EstrogenLevel': est, 'Disease': disease})
    df.to_csv("data/raw/breastcancer_data.csv", index=False)

    X = df.drop(columns=['Disease'])
    y = df['Disease']

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    joblib.dump(model, "models/saved_models/breastcancer_rf.joblib")
    print("Saved Breast Cancer model")

if __name__ == "__main__":
    generate_and_train_stroke()
    generate_and_train_thyroid()
    generate_and_train_anemia()
    generate_and_train_breast_cancer()
