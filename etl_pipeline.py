import pandas as pd
import numpy as np
import os
from datetime import datetime

# Setup directories
DATA_DIR = 'data'
DWH_DIR = 'dwh'
if not os.path.exists(DWH_DIR):
    os.makedirs(DWH_DIR)

def run_etl():
    print("Starting ETL process...")

    # 1. Extraction
    print("Extracting data...")
    customer_info = pd.read_csv(os.path.join(DATA_DIR, 'customer_info.csv'))
    usage_data = pd.read_csv(os.path.join(DATA_DIR, 'usage_data.csv'))
    churn_labels = pd.read_csv(os.path.join(DATA_DIR, 'churn_labels.csv'))

    # 2. Transformation & Cleaning
    print("Cleaning and Transforming data...")

    # Clean customer_info
    # Impute missing Age with median
    customer_info['Age'] = customer_info['Age'].fillna(customer_info['Age'].median())

    # Correct negative MonthlyCharges
    customer_info.loc[customer_info['MonthlyCharges'] < 0, 'MonthlyCharges'] = customer_info['MonthlyCharges'].median()

    # Enrich: Assign Operators (Orange / MTN)
    np.random.seed(42) # For reproducibility
    operators = ['Orange', 'MTN']
    customer_info['Operator'] = np.random.choice(operators, size=len(customer_info))

    # Enrich: Map generic regions to Cameroon regions
    # We'll use a mapping or random assignment to specific Cameroon regions
    cameroon_regions = {
        'Urban': ['Littoral', 'Centre'],
        'Suburban': ['Ouest', 'Sud-Ouest', 'Nord-Ouest'],
        'Rural': ['Nord', 'Extrême-Nord', 'Adamaoua', 'Est', 'Sud']
    }

    def map_cameroon_region(row):
        choices = cameroon_regions.get(row['Region'], ['Centre'])
        return np.random.choice(choices)

    customer_info['CameroonRegion'] = customer_info.apply(map_cameroon_region, axis=1)

    # 3. Create Dimensions
    print("Creating Dimensions...")

    # dim_customer
    dim_customer = customer_info[['CustomerID', 'Age', 'Gender', 'ContractType', 'SignupDate']].drop_duplicates(subset=['CustomerID'])

    # dim_operator
    dim_operator = pd.DataFrame({
        'OperatorID': [1, 2],
        'OperatorName': ['Orange', 'MTN']
    })

    # Add OperatorID to customer_info for joining
    op_map = {'Orange': 1, 'MTN': 2}
    customer_info['OperatorID'] = customer_info['Operator'].map(op_map)

    # dim_location
    unique_locations = customer_info[['CameroonRegion', 'Region']].drop_duplicates().reset_index(drop=True)
    unique_locations['LocationID'] = unique_locations.index + 1
    dim_location = unique_locations.rename(columns={'CameroonRegion': 'RegionName', 'Region': 'AreaType'})

    # Join LocationID back to customer_info
    customer_info = customer_info.merge(unique_locations, on=['CameroonRegion', 'Region'])

    # dim_date
    usage_dates = pd.to_datetime(usage_data['Month']).unique()
    dim_date = pd.DataFrame({'FullDate': usage_dates})
    dim_date['DateKey'] = dim_date['FullDate'].dt.strftime('%Y%m%d').astype(int)
    dim_date['Day'] = dim_date['FullDate'].dt.day
    dim_date['Month'] = dim_date['FullDate'].dt.month
    dim_date['MonthName'] = dim_date['FullDate'].dt.month_name()
    dim_date['Quarter'] = dim_date['FullDate'].dt.quarter
    dim_date['Year'] = dim_date['FullDate'].dt.year

    # 4. Create Fact Table
    print("Creating Fact Table...")

    # Merge usage with customer info and churn
    fact_usage = usage_data.merge(customer_info[['CustomerID', 'OperatorID', 'LocationID', 'MonthlyCharges']], on='CustomerID', how='left')
    fact_usage = fact_usage.merge(churn_labels, on='CustomerID', how='left')

    # Convert Month to DateKey
    fact_usage['Month'] = pd.to_datetime(fact_usage['Month'])
    fact_usage['DateKey'] = fact_usage['Month'].dt.strftime('%Y%m%d').astype(float) # float because of potential NaNs if dates don't match, will convert to int after handling

    # Fill missing values if any
    fact_usage['Churn'] = fact_usage['Churn'].fillna(0).astype(int)

    # Select columns for fact table
    fact_usage = fact_usage[[
        'DateKey', 'CustomerID', 'LocationID', 'OperatorID',
        'CallMinutes', 'DataUsageGB', 'SMSCount', 'Complaints',
        'MonthlyCharges', 'Churn'
    ]]

    # Ensure DateKey is int
    fact_usage['DateKey'] = fact_usage['DateKey'].astype(int)

    # 5. Load (Export to CSV)
    print("Exporting to CSV...")
    dim_customer.to_csv(os.path.join(DWH_DIR, 'dim_customer.csv'), index=False)
    dim_operator.to_csv(os.path.join(DWH_DIR, 'dim_operator.csv'), index=False)
    dim_location.to_csv(os.path.join(DWH_DIR, 'dim_location.csv'), index=False)
    dim_date.to_csv(os.path.join(DWH_DIR, 'dim_date.csv'), index=False)
    fact_usage.to_csv(os.path.join(DWH_DIR, 'fact_usage.csv'), index=False)

    print(f"ETL completed successfully! Files are in the '{DWH_DIR}' directory.")

if __name__ == "__main__":
    run_etl()
