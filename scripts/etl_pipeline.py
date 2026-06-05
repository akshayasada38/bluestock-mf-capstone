"""
etl_pipeline.py
Day 2 — Data Cleaning + SQLite Database Load
"""

import re
import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy import create_engine, text

BASE    = Path(__file__).parent.parent
RAW     = BASE / "data" / "raw"
PROC    = BASE / "data" / "processed"
DB_DIR  = BASE / "data" / "db"
SQL_DIR = BASE / "sql"
SEP     = "=" * 70

PROC.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "bluestock_mf.db"

def log(msg): print(f"  {msg}")

# ── Cleaners ─────────────────────────────────────────────────────────────────

def clean_nav_history(df):
    log("Cleaning 02_nav_history ...")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["nav"]  = pd.to_numeric(df["nav"], errors="coerce")
    df = df.dropna(subset=["date","nav","amfi_code"])
    df = df[df["nav"] > 0]
    df = df.drop_duplicates(subset=["amfi_code","date"])
    df = df.sort_values(["amfi_code","date"]).reset_index(drop=True)

    # Forward-fill per fund for weekends/holidays
    filled = []
    for code, grp in df.groupby("amfi_code"):
        g = grp.set_index("date")[["nav"]].resample("B").ffill()
        g["amfi_code"] = code
        filled.append(g)
    df = pd.concat(filled).reset_index().rename(columns={"index":"date","level_0":"date"})
    if "level_0" in df.columns: df = df.drop(columns=["level_0"])

    df = df.sort_values(["amfi_code","date"]).reset_index(drop=True)
    df["daily_return"] = df.groupby("amfi_code")["nav"].pct_change().round(6)
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    log(f"  nav_history → {len(df):,} rows ✅")
    return df

def clean_transactions(df):
    log("Cleaning 08_investor_transactions ...")
    mapping = {"sip":"SIP","lumpsum":"Lumpsum","redemption":"Redemption",
               "switch":"Switch","stp":"STP","swp":"SWP"}
    df["transaction_type"] = (df["transaction_type"].str.strip().str.lower()
                               .map(mapping).fillna(df["transaction_type"]))
    df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce")
    df = df[df["amount_inr"] > 0]
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["kyc_status"] = df["kyc_status"].str.upper().str.strip()
    log(f"  investor_transactions → {len(df):,} rows ✅")
    return df

def clean_scheme_performance(df):
    log("Cleaning 07_scheme_performance ...")
    for col in df.columns:
        if any(k in col.lower() for k in ["return","sharpe","alpha","beta","ratio"]):
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "expense_ratio_pct" in df.columns:
        mask = df["expense_ratio_pct"].notna()
        df = df[~mask | df["expense_ratio_pct"].between(0.1, 2.5)]
    log(f"  scheme_performance → {len(df):,} rows ✅")
    return df

def clean_generic(df, name):
    log(f"Cleaning {name} ...")
    df = df.drop_duplicates()
    for col in df.select_dtypes(include=["object","string"]).columns:
        df[col] = df[col].astype(str).str.strip()
    log(f"  {name} → {len(df):,} rows ✅")
    return df

def build_dim_date():
    dates = pd.date_range("2022-01-01","2025-12-31",freq="D")
    return pd.DataFrame({
        "date_id":    dates.strftime("%Y-%m-%d"),
        "year":       dates.year,
        "month":      dates.month,
        "quarter":    dates.quarter,
        "month_name": dates.strftime("%B"),
        "is_weekday": (dates.dayofweek < 5).astype(int),
    })

# ── Main ─────────────────────────────────────────────────────────────────────

def run_etl():
    print(f"\n{SEP}\n  DAY 2 — ETL PIPELINE\n{SEP}")

    # Load
    print(f"\n{'─'*70}\n  STEP 1: LOAD RAW CSVs\n{'─'*70}")
    raw = {}
    for f in sorted(RAW.glob("*.csv")):
        raw[f.stem] = pd.read_csv(f)
        log(f"Loaded {f.name} → {raw[f.stem].shape}")

    # Clean
    print(f"\n{'─'*70}\n  STEP 2: CLEAN\n{'─'*70}")
    cleaned = {}
    for key, df in raw.items():
        if   "nav_history"          in key: cleaned[key] = clean_nav_history(df.copy())
        elif "investor_trans"       in key: cleaned[key] = clean_transactions(df.copy())
        elif "scheme_performance"   in key: cleaned[key] = clean_scheme_performance(df.copy())
        else:                               cleaned[key] = clean_generic(df.copy(), key)

    # Save processed
    print(f"\n{'─'*70}\n  STEP 3: SAVE PROCESSED CSVs\n{'─'*70}")
    for key, df in cleaned.items():
        out = PROC / f"clean_{key}.csv"
        df.to_csv(out, index=False, encoding="utf-8")
        log(f"Saved → {out.name}")

    # SQLite
    print(f"\n{'─'*70}\n  STEP 4: LOAD SQLITE → {DB_PATH.name}\n{'─'*70}")
    engine = create_engine(f"sqlite:///{DB_PATH}")

    with open(SQL_DIR / "schema.sql", encoding="utf-8") as f:
        schema = f.read()
    with engine.connect() as conn:
        for stmt in schema.split(";"):
            s = stmt.strip()
            if s and not s.startswith("--"):
                try: conn.execute(text(s))
                except: pass
        conn.commit()
    log("Schema applied ✅")

    def load(tname, df, msg):
        df.to_sql(tname, engine, if_exists="replace", index=False)
        log(f"{msg} → {len(df):,} rows ✅")

    # dim_fund
    fk = next((k for k in cleaned if "fund_master" in k), None)
    if fk:
        df = cleaned[fk].copy(); df["amfi_code"] = df["amfi_code"].astype(str)
        load("dim_fund", df, "dim_fund")

    load("dim_date", build_dim_date(), "dim_date")

    # fact_nav
    nk = next((k for k in cleaned if "nav_history" in k), None)
    if nk:
        df = cleaned[nk].copy(); df["amfi_code"] = df["amfi_code"].astype(str)
        df = df.rename(columns={"date":"nav_date"})
        cols = [c for c in ["amfi_code","nav_date","nav","daily_return"] if c in df.columns]
        load("fact_nav", df[cols], "fact_nav")

    # fact_transactions
    tk = next((k for k in cleaned if "investor_trans" in k), None)
    if tk:
        df = cleaned[tk].copy(); df["amfi_code"] = df["amfi_code"].astype(str)
        load("fact_transactions", df, "fact_transactions")

    # fact_performance
    pk = next((k for k in cleaned if "scheme_performance" in k), None)
    if pk:
        df = cleaned[pk].copy(); df["amfi_code"] = df["amfi_code"].astype(str)
        load("fact_performance", df, "fact_performance")

    # fact_aum
    ak = next((k for k in cleaned if "aum_by_fund" in k), None)
    if ak:
        load("fact_aum", cleaned[ak].copy(), "fact_aum")

    # remaining
    done = {"dim_fund","dim_date","fact_nav","fact_transactions","fact_performance","fact_aum"}
    for key, df in cleaned.items():
        tname = re.sub(r"^\d+_","", key)
        if tname not in done:
            load(tname, df, tname)

    # Verify
    print(f"\n{'─'*70}\n  STEP 5: VERIFY\n{'─'*70}")
    with engine.connect() as conn:
        tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")).fetchall()
        print(f"\n  {'Table':<35} {'Rows':>8}")
        print(f"  {'-'*45}")
        for (t,) in tables:
            cnt = conn.execute(text(f'SELECT COUNT(*) FROM "{t}"')).scalar()
            print(f"  {t:<35} {cnt:>8,}")

    print(f"\n✅ ETL complete! DB saved → {DB_PATH}")
    return engine

if __name__ == "__main__":
    run_etl()
