
import pandas as pd
import numpy as np
import os

def generate_diabetes_data():
    n_samples = 500
    data = {
        'Pregnancies': np.random.randint(0, 15, n_samples),
        'Glucose': np.random.normal(120, 30, n_samples),
        'BloodPressure': np.random.normal(70, 10, n_samples),
        'SkinThickness': np.random.normal(20, 10, n_samples),
        'Insulin': np.random.normal(80, 50, n_samples),
        'BMI': np.random.normal(30, 7, n_samples),
        'DiabetesPedigreeFunction': np.random.normal(0.5, 0.2, n_samples),
        'Age': np.random.randint(20, 80, n_samples),
        'Outcome': np.random.randint(0, 2, n_samples)
    }
    df = pd.DataFrame(data)
    df.to_csv("data/raw/diabetes.csv", index=False)

def generate_heart_data():
    n_samples = 500
    data = {
        'Age': np.random.randint(30, 80, n_samples),
        'Sex': np.random.randint(0, 2, n_samples),
        'ChestPainType': np.random.randint(0, 4, n_samples),
        'RestingBP': np.random.normal(130, 20, n_samples),
        'Cholesterol': np.random.normal(240, 50, n_samples),
        'FastingBS': np.random.randint(0, 2, n_samples),
        'MaxHR': np.random.normal(150, 20, n_samples),
        'HeartDisease': np.random.randint(0, 2, n_samples)
    }
    df = pd.DataFrame(data)
    df.to_csv("data/raw/heart_data.csv", index=False)

def generate_kidney_data():
    # Simplied from ckd.csv
    n_samples = 500
    data = {
        'age': np.random.normal(50, 15, n_samples),
        'bp': np.random.normal(80, 10, n_samples),
        'sg': np.random.uniform(1.005, 1.025, n_samples),
        'al': np.random.randint(0, 5, n_samples),
        'bgr': np.random.normal(150, 50, n_samples),
        'bu': np.random.normal(50, 20, n_samples),
        'sc': np.random.normal(1.5, 0.5, n_samples),
        'hemo': np.random.normal(12, 2, n_samples),
        'classification': np.random.randint(0, 2, n_samples)
    }
    df = pd.DataFrame(data)
    df.to_csv("data/raw/ckd.csv", index=False)

def generate_liver_data():
    n_samples = 500
    data = {
        'Age': np.random.randint(20, 80, n_samples),
        'TotalBilirubin': np.random.normal(1, 0.5, n_samples),
        'DirectBilirubin': np.random.normal(0.5, 0.2, n_samples),
        'AlkalinePhosphotase': np.random.normal(200, 50, n_samples),
        'AlamineAminotransferase': np.random.normal(40, 20, n_samples),
        'AspartateAminotransferase': np.random.normal(40, 20, n_samples),
        'TotalProtiens': np.random.normal(7, 1, n_samples),
        'Albumin': np.random.normal(3.5, 0.5, n_samples),
        'Dataset': np.random.randint(1, 3, n_samples)
    }
    df = pd.DataFrame(data)
    df.to_csv("data/raw/liver_disease.csv", index=False)

if __name__ == "__main__":
    generate_diabetes_data()
    generate_heart_data()
    generate_kidney_data()
    generate_liver_data()
    print("Mock datasets generated in data/raw/")
