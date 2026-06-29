# Data Warehouse Telecom Cameroon (Orange & MTN)

Ce projet implémente un Data Warehouse en architecture en étoile (Star Schema) pour analyser la consommation des clients télécoms au Cameroun.

## Architecture du Data Warehouse

Le Data Warehouse est composé d'une table de faits centrale et de plusieurs tables de dimensions :

- **fact_usage** : Contient les mesures de consommation associées à un service, ainsi que les plaintes, les charges mensuelles et le statut de churn.
- **dim_customer** : Informations démographiques sur les clients (Âge, Genre, Type de contrat).
- **dim_date** : Hiérarchie temporelle pour l'analyse (Jour, Mois, Trimestre, Année).
- **dim_location** : Localisation géographique enrichie avec les régions du Cameroun (Littoral, Centre, Ouest, etc.).
- **dim_operator** : Identification de l'opérateur (Orange Cameroun, MTN Cameroon).
- **dim_service** : Types de services consommés (Appels, Data, SMS).

## Processus ETL

Le script `etl_pipeline.py` automatise le processus :
1. **Extraction** : Lecture des données brutes depuis le dossier `data/`.
2. **Nettoyage** : Gestion des valeurs manquantes (âge) et correction des anomalies (charges négatives).
3. **Enrichissement** :
    - Assignation aléatoire des opérateurs (Orange/MTN).
    - Mapping des types de zones vers des régions réelles du Cameroun.
4. **Transformation** :
    - Structuration des données selon le modèle en étoile.
    - Pivotage des mesures de consommation pour une analyse granulaire par service.
5. **Chargement** : Exportation des fichiers CSV prêts à l'emploi dans le dossier `dwh/`.

## Guide de Test et de Validation

Pour garantir que le Data Warehouse est correctement construit et que les données sont fiables, suivez ces étapes :

### 1. Installation des dépendances
Assurez-vous d'avoir Python et la bibliothèque `pandas` installés :
```bash
pip install pandas
```

### 2. Exécution du pipeline ETL
Lancez la transformation des données brutes en modèle en étoile :
```bash
python3 etl_pipeline.py
```
Vérifiez que le dossier `dwh/` a bien été créé et contient les 6 fichiers CSV.

### 3. Lancement des tests de qualité
Exécutez le script de validation pour vérifier l'intégrité des données (clés uniques, pas de valeurs nulles, intégrité référentielle) :
```bash
python3 validate_dwh.py
```
Si tout est correct, vous verrez le message : `ALL QUALITY CHECKS PASSED!`.

## Visualisation avec Power BI

Pour visualiser l'évolution de la consommation :
1. Ouvrez Power BI Desktop.
2. Cliquez sur **Obtenir des données** > **Texte/CSV**.
3. Importez les fichiers de `dwh/` un par un.
4. Allez dans la vue **Modèle** pour vérifier que `fact_usage` est relié aux dimensions par les IDs correspondants.
5. Créez vos graphiques (ex: Consommation par Service et par Région, Taux de Churn par Opérateur, etc.).
