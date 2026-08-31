import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def train():
    df = pd.read_csv("data/raw/liver_disease.csv")
    X = df.drop(columns=['Dataset'])
    y = df['Dataset'].apply(lambda v: 1 if v == 1 else 0) # binary 0/1
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    try:
        import xgboost as xgb
        model = xgb.XGBClassifier(eval_metric='logloss', random_state=42)
    except ImportError:
        model = GradientBoostingClassifier(random_state=42)

    model.fit(X_train, y_train)

    accuracy = accuracy_score(y_test, model.predict(X_test))
    print(f"Liver Model Accuracy: {accuracy:.4f}")

    joblib.dump(model, "models/saved_models/liver_xgb.joblib")
    print("Model saved to models/saved_models/liver_xgb.joblib")

if __name__ == "__main__":
    train()
