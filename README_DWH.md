# Data Warehouse Telecom Cameroon (Orange & MTN) - Version IA

Ce projet implémente un Data Warehouse complet (Star Schema) couplé à un moteur d'IA pour l'analyse de la consommation télécom au Cameroun.

## Architecture du Data Warehouse

- **fact_usage** : Table centrale de faits (mesures de consommation par service).
- **dim_customer** : Profils clients.
- **dim_operator** : Orange vs MTN.
- **dim_location** : Régions du Cameroun.
- **dim_service** : Appels, Data, SMS.
- **dim_date** : Temps.

## Composant IA : Conseiller Décisionnel

Le système inclut un modèle d'IA (Random Forest) qui :
1. **Prédit le risque de Churn** : Identifie les clients susceptibles de quitter l'opérateur.
2. **Fournit des conseils** : Propose des actions concrètes (promotions, appels SAV) basées sur les tendances.

## Workflow de Mise en Place & Observation

Suivez ces étapes pour observer le fonctionnement complet du projet :

### 1. Préparation et ETL
Transforme les données brutes en Data Warehouse structuré.
```bash
python3 etl_pipeline.py
```
**Observation :** Vérifiez l'apparition des fichiers structurés dans le dossier `dwh/`.

### 2. Validation de l'Intégrité
Vérifie que les données du DWH sont prêtes pour l'analyse et l'IA.
```bash
python3 validate_dwh.py
```
**Observation :** Le script doit afficher `ALL QUALITY CHECKS PASSED!`.

### 3. Entraînement de l'IA
Crée le modèle prédictif basé sur les données du DWH.
```bash
python3 ai_model.py
```
**Observation :** Un dossier `models/` est créé contenant le fichier `churn_model.pkl`.

### 4. Conseil Décisionnel
Génère les recommandations pour les décideurs.
```bash
python3 ai_advisor.py
```
**Observation :** Vous verrez une console s'afficher avec les **Alertes Churn** et des **Conseils Stratégiques** personnalisés (ex: "Offrir un bonus de fidélité").

## Visualisation Power BI
Importez les fichiers du dossier `dwh/` dans Power BI pour observer l'évolution graphique des indicateurs (KPIs) mis en avant par l'IA.
