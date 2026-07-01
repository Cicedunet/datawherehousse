import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

DWH_DIR = 'dwh'
MODEL_DIR = 'models'

def train():
    print("AI Model: Entraînement en cours...")
    if not os.path.exists(MODEL_DIR): os.makedirs(MODEL_DIR)

    fact = pd.read_csv(os.path.join(DWH_DIR, 'fact_usage.csv'))
    cust = pd.read_csv(os.path.join(DWH_DIR, 'dim_customer.csv'))

    # Agrégation simplifiée pour le modèle
    df = fact.groupby('CustomerID').agg({
        'UsageValue': 'mean',
        'MonthlyCharges': 'mean',
        'Complaints': 'sum',
        'Churn': 'max'
    }).reset_index().merge(cust, on='CustomerID')

    df['Gender'] = df['Gender'].map({'Male': 0, 'Female': 1})
    df['ContractType'] = df['ContractType'].map({'Monthly': 0, 'Prepaid': 1, 'Yearly': 2})

    features = ['UsageValue', 'MonthlyCharges', 'Complaints', 'Age', 'Gender', 'ContractType']
    X = df[features]
    y = df['Churn']

    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y)

    joblib.dump(model, os.path.join(MODEL_DIR, 'churn_model.pkl'))
    joblib.dump(features, os.path.join(MODEL_DIR, 'feature_names.pkl'))
    print("AI Model: Modèle sauvegardé avec succès.")

if __name__ == "__main__":
    train()
