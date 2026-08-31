import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def train():
    df = pd.read_csv("data/raw/heart_data.csv")
    X = df.drop(columns=['HeartDisease'])
    y = df['HeartDisease']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    accuracy = accuracy_score(y_test, model.predict(X_test))
    print(f"Heart Model Accuracy: {accuracy:.4f}")

    joblib.dump(model, "models/saved_models/heart_rf.joblib")
    print("Model saved to models/saved_models/heart_rf.joblib")

if __name__ == "__main__":
    train()
