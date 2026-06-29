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
    customer_info['Age'] = customer_info['Age'].fillna(customer_info['Age'].median())
    customer_info.loc[customer_info['MonthlyCharges'] < 0, 'MonthlyCharges'] = customer_info['MonthlyCharges'].median()

    # Enrich: Assign Operators (Orange / MTN)
    np.random.seed(42)
    operators = ['Orange', 'MTN']
    customer_info['Operator'] = np.random.choice(operators, size=len(customer_info))

    # Enrich: Map generic regions to Cameroon regions
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

    # dim_service
    dim_service = pd.DataFrame({
        'ServiceID': [1, 2, 3],
        'ServiceName': ['Appels', 'Data', 'SMS'],
        'Unit': ['Minutes', 'GB', 'Unités']
    })

    # dim_location
    unique_locations = customer_info[['CameroonRegion', 'Region']].drop_duplicates().reset_index(drop=True)
    unique_locations['LocationID'] = unique_locations.index + 1
    dim_location = unique_locations.rename(columns={'CameroonRegion': 'RegionName', 'Region': 'AreaType'})

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
    print("Creating Fact Table (Pivoted by Service)...")

    # Join customer_info with unique_locations to get LocationID
    customer_info_with_loc = customer_info.merge(unique_locations, on=['CameroonRegion', 'Region'])

    # Map OperatorID
    op_map = {'Orange': 1, 'MTN': 2}
    customer_info_with_loc['OperatorID'] = customer_info_with_loc['Operator'].map(op_map)

    customer_ids_meta = customer_info_with_loc[['CustomerID', 'OperatorID', 'LocationID', 'MonthlyCharges']]

    # Join usage with customer info meta and churn
    temp_fact = usage_data.merge(customer_ids_meta, on='CustomerID', how='left')
    temp_fact = temp_fact.merge(churn_labels, on='CustomerID', how='left')

    # Convert Month to DateKey
    temp_fact['Month'] = pd.to_datetime(temp_fact['Month'])
    temp_fact['DateKey'] = temp_fact['Month'].dt.strftime('%Y%m%d').astype(int)
    temp_fact['Churn'] = temp_fact['Churn'].fillna(0).astype(int)

    # Melt (Pivot) usage metrics into long format
    id_vars = ['DateKey', 'CustomerID', 'LocationID', 'OperatorID', 'MonthlyCharges', 'Complaints', 'Churn']

    fact_usage = temp_fact.melt(
        id_vars=id_vars,
        value_vars=['CallMinutes', 'DataUsageGB', 'SMSCount'],
        var_name='ServiceNameRaw',
        value_name='UsageValue'
    )

    # Map ServiceNameRaw to ServiceID
    service_map = {'CallMinutes': 1, 'DataUsageGB': 2, 'SMSCount': 3}
    fact_usage['ServiceID'] = fact_usage['ServiceNameRaw'].map(service_map)

    # Final column selection
    fact_usage = fact_usage[[
        'DateKey', 'CustomerID', 'LocationID', 'OperatorID', 'ServiceID',
        'UsageValue', 'MonthlyCharges', 'Complaints', 'Churn'
    ]]

    # 5. Load (Export to CSV)
    print("Exporting to CSV...")
    dim_customer.to_csv(os.path.join(DWH_DIR, 'dim_customer.csv'), index=False)
    dim_operator.to_csv(os.path.join(DWH_DIR, 'dim_operator.csv'), index=False)
    dim_service.to_csv(os.path.join(DWH_DIR, 'dim_service.csv'), index=False)
    dim_location.to_csv(os.path.join(DWH_DIR, 'dim_location.csv'), index=False)
    dim_date.to_csv(os.path.join(DWH_DIR, 'dim_date.csv'), index=False)
    fact_usage.to_csv(os.path.join(DWH_DIR, 'fact_usage.csv'), index=False)

    print(f"ETL completed successfully! Files are in the '{DWH_DIR}' directory.")

if __name__ == "__main__":
    run_etl()
