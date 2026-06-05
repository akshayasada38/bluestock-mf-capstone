"""
data_ingestion.py
Day 1 - Task 3: Load all 10 CSV datasets, inspect structure, note anomalies.
"""

import os
import pandas as pd
import numpy as np

RAW_DATA_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw")
PROCESSED_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "processed")
SEP = "=" * 70

CSV_FILES = [
    "01_fund_master.csv",
    "02_nav_history.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv",
]


def load_and_inspect(filepath: str) -> pd.DataFrame | None:
    filename = os.path.basename(filepath)
    print(f"\n{SEP}\n  FILE: {filename}\n{SEP}")

    if not os.path.exists(filepath):
        print(f"  [WARNING] Not found: {filepath}")
        return None

    df = pd.read_csv(filepath)

    # Shape
    print(f"\n📐 Shape      : {df.shape[0]:,} rows × {df.shape[1]} columns")

    # dtypes
    print(f"\n📋 Data Types :\n{df.dtypes.to_string()}")

    # Head
    print(f"\n👀 First 5 Rows:\n{df.head().to_string()}")

    # Anomalies
    print(f"\n🔍 Anomaly Check:")
    anomalies = []

    null_cols = df.isnull().sum()
    null_cols = null_cols[null_cols > 0]
    if not null_cols.empty:
        for col, cnt in null_cols.items():
            pct = round(cnt / len(df) * 100, 2)
            anomalies.append(f"  ⚠️  '{col}': {cnt} nulls ({pct}%)")
    else:
        print("  ✅ No missing values.")

    dups = df.duplicated().sum()
    if dups:
        anomalies.append(f"  ⚠️  {dups} duplicate rows.")
    else:
        print("  ✅ No duplicate rows.")

    for col in df.select_dtypes(include=[np.number]).columns:
        neg = (df[col] < 0).sum()
        if neg:
            anomalies.append(f"  ⚠️  '{col}': {neg} negative values.")

    for col in df.columns:
        if df[col].nunique() == 1:
            anomalies.append(f"  ⚠️  '{col}': only 1 unique value.")

    for a in anomalies:
        print(a)

    return df


def run_ingestion():
    print(f"\n{SEP}\n  MUTUAL FUND DATA INGESTION — DAY 1\n{SEP}")
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    dataframes = {}
    loaded = skipped = 0

    for filename in CSV_FILES:
        filepath = os.path.join(RAW_DATA_DIR, filename)
        df = load_and_inspect(filepath)
        if df is not None:
            key = filename.replace(".csv", "")
            dataframes[key] = df
            out = os.path.join(PROCESSED_DIR, filename.replace(".csv", "_processed.csv"))
            df.to_csv(out, index=False)
            loaded += 1
        else:
            skipped += 1

    print(f"\n{SEP}\n  INGESTION SUMMARY\n{SEP}")
    print(f"  ✅ Loaded  : {loaded}  |  ❌ Skipped: {skipped}\n")
    for name, df in dataframes.items():
        print(f"  • {name:<40} {df.shape[0]:>7,} rows × {df.shape[1]:>2} cols")

    return dataframes


if __name__ == "__main__":
    dfs = run_ingestion()
    print("\n✅ Day 1 ingestion complete!")
