import pandas as pd
import os

DWH_DIR = 'dwh'

def check_nulls(df, name):
    null_counts = df.isnull().sum().sum()
    if null_counts > 0:
        print(f"FAILED: {name} contains {null_counts} null values.")
        return False
    print(f"PASSED: {name} has no null values.")
    return True

def check_uniqueness(df, column, name):
    if df[column].duplicated().any():
        print(f"FAILED: {name} has duplicate values in {column}.")
        return False
    print(f"PASSED: {name} has unique {column}.")
    return True

def check_referential_integrity(fact, dim, join_col, name):
    missing = fact[~fact[join_col].isin(dim[join_col])]
    if len(missing) > 0:
        print(f"FAILED: Referential integrity between fact and {name} on {join_col}. {len(missing)} orphaned rows.")
        return False
    print(f"PASSED: Referential integrity between fact and {name}.")
    return True

def run_checks():
    print("Running Data Quality Checks...")

    dim_customer = pd.read_csv(os.path.join(DWH_DIR, 'dim_customer.csv'))
    dim_date = pd.read_csv(os.path.join(DWH_DIR, 'dim_date.csv'))
    dim_location = pd.read_csv(os.path.join(DWH_DIR, 'dim_location.csv'))
    dim_operator = pd.read_csv(os.path.join(DWH_DIR, 'dim_operator.csv'))
    fact_usage = pd.read_csv(os.path.join(DWH_DIR, 'fact_usage.csv'))

    results = []
    results.append(check_nulls(dim_customer, "dim_customer"))
    results.append(check_nulls(dim_date, "dim_date"))
    results.append(check_nulls(dim_location, "dim_location"))
    results.append(check_nulls(dim_operator, "dim_operator"))
    results.append(check_nulls(fact_usage, "fact_usage"))

    results.append(check_uniqueness(dim_customer, "CustomerID", "dim_customer"))
    results.append(check_uniqueness(dim_date, "DateKey", "dim_date"))
    results.append(check_uniqueness(dim_location, "LocationID", "dim_location"))
    results.append(check_uniqueness(dim_operator, "OperatorID", "dim_operator"))

    results.append(check_referential_integrity(fact_usage, dim_customer, "CustomerID", "dim_customer"))
    results.append(check_referential_integrity(fact_usage, dim_date, "DateKey", "dim_date"))
    results.append(check_referential_integrity(fact_usage, dim_location, "LocationID", "dim_location"))
    results.append(check_referential_integrity(fact_usage, dim_operator, "OperatorID", "dim_operator"))

    if all(results):
        print("\nALL QUALITY CHECKS PASSED!")
    else:
        print("\nSOME QUALITY CHECKS FAILED!")

if __name__ == "__main__":
    run_checks()
