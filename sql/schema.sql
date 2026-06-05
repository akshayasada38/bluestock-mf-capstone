-- ============================================================
-- schema.sql
-- Bluestock MF Capstone — SQLite Star Schema
-- Day 2: Database Design
-- ============================================================

PRAGMA foreign_keys = ON;

-- ── DIMENSION: dim_fund ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code          TEXT PRIMARY KEY,
    fund_house         TEXT NOT NULL,
    scheme_name        TEXT NOT NULL,
    category           TEXT,
    sub_category       TEXT,
    plan               TEXT,
    launch_date        DATE,
    benchmark          TEXT,
    expense_ratio_pct  REAL,
    exit_load_pct      REAL,
    fund_manager       TEXT,
    risk_category      TEXT,
    sebi_category_code TEXT
);

-- ── DIMENSION: dim_date ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS dim_date (
    date_id     TEXT PRIMARY KEY,   -- YYYY-MM-DD
    year        INTEGER,
    month       INTEGER,
    quarter     INTEGER,
    month_name  TEXT,
    is_weekday  INTEGER             -- 1=weekday, 0=weekend
);

-- ── FACT: fact_nav ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fact_nav (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code    TEXT NOT NULL REFERENCES dim_fund(amfi_code),
    nav_date     TEXT NOT NULL,     -- YYYY-MM-DD
    nav          REAL NOT NULL,
    daily_return REAL,              -- (nav_t - nav_t-1) / nav_t-1
    UNIQUE(amfi_code, nav_date)
);

-- ── FACT: fact_transactions ──────────────────────────────────
CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id   TEXT PRIMARY KEY,
    amfi_code        TEXT REFERENCES dim_fund(amfi_code),
    transaction_date TEXT,
    transaction_type TEXT,          -- SIP / Lumpsum / Redemption
    amount           REAL,
    units            REAL,
    nav_at_transaction REAL,
    investor_age_group TEXT,
    city_tier        TEXT,
    state            TEXT,
    kyc_status       TEXT
);

-- ── FACT: fact_performance ───────────────────────────────────
CREATE TABLE IF NOT EXISTS fact_performance (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code        TEXT REFERENCES dim_fund(amfi_code),
    period           TEXT,          -- e.g. '1Y', '3Y', '5Y'
    return_pct       REAL,
    benchmark_return REAL,
    alpha            REAL,
    beta             REAL,
    sharpe_ratio     REAL,
    expense_ratio    REAL,
    UNIQUE(amfi_code, period)
);

-- ── FACT: fact_aum ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fact_aum (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_house       TEXT NOT NULL,
    month            TEXT NOT NULL,  -- YYYY-MM
    aum_lakh_crore   REAL,
    UNIQUE(fund_house, month)
);

-- ── INDEXES for fast query performance ───────────────────────
CREATE INDEX IF NOT EXISTS idx_nav_amfi_date   ON fact_nav(amfi_code, nav_date);
CREATE INDEX IF NOT EXISTS idx_nav_date        ON fact_nav(nav_date);
CREATE INDEX IF NOT EXISTS idx_txn_amfi        ON fact_transactions(amfi_code);
CREATE INDEX IF NOT EXISTS idx_txn_date        ON fact_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_txn_state       ON fact_transactions(state);
CREATE INDEX IF NOT EXISTS idx_perf_amfi       ON fact_performance(amfi_code);
