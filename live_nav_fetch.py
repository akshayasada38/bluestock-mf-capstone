"""
live_nav_fetch.py
Day 1 - Tasks 4 & 5: Fetch live NAV from mfapi.in for 6 mutual fund schemes.
Saves each scheme's NAV history as a CSV in data/raw/.
"""

import os
import time
import requests
import pandas as pd
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "raw")
BASE_URL = "https://api.mfapi.in/mf"

SCHEMES = {
    "HDFC_Top100_Direct":     125497,   # Task 4 — primary scheme
    "SBI_Bluechip":           119551,   # Task 5
    "ICICI_Bluechip":         120503,   # Task 5
    "Nippon_LargeCap":        118632,   # Task 5
    "Axis_Bluechip":          119092,   # Task 5
    "Kotak_Bluechip":         120841,   # Task 5
}

SEPARATOR = "=" * 70


def fetch_nav(scheme_code: int, scheme_name: str) -> dict | None:
    """
    Fetch NAV data for a given AMFI scheme code from mfapi.in.
    Returns parsed JSON or None on failure.
    """
    url = f"{BASE_URL}/{scheme_code}"
    print(f"\n  📡 Fetching: {scheme_name} (code: {scheme_code})")
    print(f"     URL: {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"     ✅ Status: {response.status_code} | Records: {len(data.get('data', []))}")
        return data
    except requests.exceptions.ConnectionError:
        print(f"     ❌ Connection error — check internet/API availability.")
    except requests.exceptions.Timeout:
        print(f"     ❌ Request timed out.")
    except requests.exceptions.HTTPError as e:
        print(f"     ❌ HTTP error: {e}")
    except Exception as e:
        print(f"     ❌ Unexpected error: {e}")
    return None


def parse_nav_to_dataframe(data: dict, scheme_name: str, scheme_code: int) -> pd.DataFrame | None:
    """
    Parse mfapi.in JSON response into a clean Pandas DataFrame.

    Response structure:
    {
        "meta": { "fund_house": ..., "scheme_type": ..., "scheme_name": ... },
        "data": [ { "date": "DD-MM-YYYY", "nav": "123.456" }, ... ]
    }
    """
    if not data or "data" not in data:
        print(f"     ⚠️  No 'data' key in response for {scheme_name}.")
        return None

    meta = data.get("meta", {})
    nav_records = data["data"]

    if not nav_records:
        print(f"     ⚠️  Empty NAV history for {scheme_name}.")
        return None

    df = pd.DataFrame(nav_records)

    # ── Type Conversions ──────────────────────────────────────────────────────
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")

    # ── Add Metadata Columns ──────────────────────────────────────────────────
    df["scheme_code"]  = scheme_code
    df["scheme_name"]  = scheme_name
    df["fund_house"]   = meta.get("fund_house", "Unknown")
    df["scheme_type"]  = meta.get("scheme_type", "Unknown")
    df["scheme_category"] = meta.get("scheme_category", "Unknown")
    df["fetched_at"]   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ── Sort by date ascending ────────────────────────────────────────────────
    df = df.sort_values("date").reset_index(drop=True)

    print(f"     📊 Date range: {df['date'].min().date()} → {df['date'].max().date()}")
    print(f"     📈 Latest NAV: ₹{df['nav'].iloc[-1]:.4f}  |  Total records: {len(df)}")

    return df


def save_nav_csv(df: pd.DataFrame, scheme_name: str) -> str:
    """Save NAV DataFrame to data/raw/ as CSV."""
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    filename = f"nav_{scheme_name.lower()}.csv"
    filepath = os.path.join(RAW_DATA_DIR, filename)
    df.to_csv(filepath, index=False)
    print(f"     💾 Saved → {filepath}")
    return filepath


def run_nav_fetch() -> dict[str, pd.DataFrame]:
    """Fetch NAV for all schemes and save to CSVs."""
    print("\n" + SEPARATOR)
    print("  LIVE NAV FETCH — mfapi.in")
    print(SEPARATOR)
    print(f"  Schemes to fetch: {len(SCHEMES)}")
    print(f"  Output directory: {RAW_DATA_DIR}\n")

    all_dfs = {}
    failed = []

    for scheme_name, scheme_code in SCHEMES.items():
        raw_data = fetch_nav(scheme_code, scheme_name)

        if raw_data:
            df = parse_nav_to_dataframe(raw_data, scheme_name, scheme_code)
            if df is not None:
                save_nav_csv(df, scheme_name)
                all_dfs[scheme_name] = df
            else:
                failed.append(scheme_name)
        else:
            failed.append(scheme_name)

        time.sleep(0.5)   # Be polite to the API — small delay between requests

    # ── Combined file ─────────────────────────────────────────────────────────
    if all_dfs:
        combined_df = pd.concat(all_dfs.values(), ignore_index=True)
        combined_path = os.path.join(RAW_DATA_DIR, "nav_all_schemes_combined.csv")
        combined_df.to_csv(combined_path, index=False)
        print(f"\n  📦 Combined CSV saved → {combined_path}")
        print(f"     Total rows: {len(combined_df):,}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{SEPARATOR}")
    print("  FETCH SUMMARY")
    print(SEPARATOR)
    print(f"  ✅ Success : {len(all_dfs)} schemes")
    if failed:
        print(f"  ❌ Failed  : {len(failed)} schemes → {', '.join(failed)}")

    print(f"\n  Latest NAV Snapshot:")
    print(f"  {'Scheme':<30} {'Code':>8}  {'Latest NAV':>12}  {'Date'}")
    print(f"  {'-'*65}")
    for name, df in all_dfs.items():
        latest = df.iloc[-1]
        print(f"  {name:<30} {latest['scheme_code']:>8}  ₹{latest['nav']:>11.4f}  {latest['date'].date()}")

    return all_dfs


if __name__ == "__main__":
    nav_data = run_nav_fetch()
    print("\n✅ Live NAV fetch complete!")
