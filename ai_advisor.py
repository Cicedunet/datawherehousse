import pandas as pd
import joblib
import os

DWH_DIR = 'dwh'
MODEL_DIR = 'models'

def advise():
    print("AI Advisor: Analyse des données pour recommandations...")
    model_path = os.path.join(MODEL_DIR, 'churn_model.pkl')
    if not os.path.exists(model_path):
        print("Erreur: Modèle non trouvé.")
        return

    model = joblib.load(model_path)
    features = joblib.load(os.path.join(MODEL_DIR, 'feature_names.pkl'))

    fact = pd.read_csv(os.path.join(DWH_DIR, 'fact_usage.csv'))
    cust = pd.read_csv(os.path.join(DWH_DIR, 'dim_customer.csv'))

    # Dernières données connues
    latest = fact[fact['DateKey'] == fact['DateKey'].max()].groupby('CustomerID').agg({
        'UsageValue': 'mean',
        'MonthlyCharges': 'mean',
        'Complaints': 'sum'
    }).reset_index().merge(cust, on='CustomerID')

    latest['Gender'] = latest['Gender'].map({'Male': 0, 'Female': 1})
    latest['ContractType'] = latest['ContractType'].map({'Monthly': 0, 'Prepaid': 1, 'Yearly': 2})

    latest['Risk'] = model.predict_proba(latest[features])[:, 1]

    print("\n" + "="*40)
    print("   CONSEILLER DÉCISIONNEL TÉLÉCOM IA")
    print("="*40)

    print("\n[ALERTES CHURN - RÉTENTION]")
    for _, r in latest.sort_values('Risk', ascending=False).head(3).iterrows():
        print(f"- Client {r['CustomerID']} : Risque {r['Risk']:.1%}")
        print(f"  Action : Offrir un bonus de fidélité ou appeler pour enquête de satisfaction.")

    print("\n[CONSEIL STRATÉGIQUE]")
    avg_risk = latest['Risk'].mean()
    if avg_risk > 0.15:
        print(f"Risque moyen élevé ({avg_risk:.1%}). Lancer une campagne nationale Orange/MTN.")
    else:
        print(f"Stabilité détectée ({avg_risk:.1%}). Focus sur l'acquisition.")
    print("="*40)

if __name__ == "__main__":
    advise()
