# 📊 Bluestock MF Capstone Project

> **End-to-End Mutual Fund Analytics Platform**  
> Intern: Akshaya Sada | Data Analysis Track | Jun 2026

---

## 🗂️ Project Overview

A complete data analytics platform for Indian Mutual Funds covering:
- **ETL pipeline** ingesting 10 datasets (46,000+ NAV records, 32,778 transactions)
- **SQLite star-schema database** with 23 tables
- **15+ EDA charts** covering NAV trends, AUM, SIP, demographics, sector allocation
- **Performance metrics**: CAGR, Sharpe Ratio, Sortino, Alpha, Beta, VaR, Max Drawdown
- **Interactive Power BI dashboard** with 4 pages and slicers
- **Fund recommender system** based on risk appetite
- **Advanced analytics**: Rolling Sharpe, Cohort Analysis, SIP Continuity, HHI

---

## 📁 Folder Structure

```
bluestock_mf_capstone/
├── data/
│   ├── raw/                    ← 10 original CSV datasets
│   ├── processed/              ← 17 cleaned CSVs + metric outputs
│   └── db/
│       └── bluestock_mf.db     ← SQLite database (23 tables)
├── notebooks/
│   ├── EDA_Analysis.ipynb      ← Day 3: 15+ EDA charts
│   ├── Performance_Analytics.ipynb  ← Day 4: CAGR, Sharpe, Alpha
│   └── Advanced_Analytics.ipynb    ← Day 6: VaR, Cohort, HHI
├── scripts/
│   ├── etl_pipeline.py         ← Clean + load SQLite
│   ├── compute_metrics.py      ← CAGR, Sharpe, Alpha, VaR, Scorecard
│   └── recommender.py          ← Fund recommender by risk appetite
├── sql/
│   ├── schema.sql              ← Star schema DDL
│   └── queries.sql             ← 10 analytical SQL queries
├── dashboard/
│   └── bluestock_mf.pbix       ← Power BI dashboard (4 pages)
├── reports/
│   ├── Final_Report.pdf
│   ├── Bluestock_MF_Presentation.pptx
│   ├── data_quality_summary.txt
│   └── charts/                 ← 15 EDA + 2 performance charts
├── data_ingestion.py           ← Day 1: Load & inspect all CSVs
├── live_nav_fetch.py           ← Day 1: Fetch live NAV from mfapi.in
├── fund_exploration.py         ← Day 1: Explore fund master + AMFI validation
├── run_pipeline.py             ← Master execution script
├── data_dictionary.md          ← All columns documented
├── requirements.txt            ← Python dependencies
└── README.md
```

---

## ⚙️ Setup

```bash
# 1. Clone the repo
git clone https://github.com/akshayasada38/bluestock-mf-capstone.git
cd bluestock-mf-capstone

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place the 10 CSV files in data/raw/
```

---

## 🚀 How to Run

### Run everything at once:
```bash
python run_pipeline.py
```

### Or run individual steps:
```bash
# Day 1 — Data Ingestion
python data_ingestion.py
python live_nav_fetch.py
python fund_exploration.py

# Day 2 — ETL & Database
python scripts/etl_pipeline.py

# Day 4 — Performance Metrics
python scripts/compute_metrics.py

# Day 6 — Fund Recommender
python scripts/recommender.py
```

### Open Notebooks:
```bash
jupyter notebook notebooks/EDA_Analysis.ipynb
jupyter notebook notebooks/Performance_Analytics.ipynb
jupyter notebook notebooks/Advanced_Analytics.ipynb
```

---

## 📡 API Used

**mfapi.in** — Free Mutual Fund API for India  
`GET https://api.mfapi.in/mf/{scheme_code}`

| Scheme | AMFI Code |
|--------|-----------|
| HDFC Top 100 Direct | 125497 |
| SBI Bluechip | 119551 |
| ICICI Bluechip | 120503 |
| Nippon Large Cap | 118632 |
| Axis Bluechip | 119092 |
| Kotak Bluechip | 120841 |

---

## 📊 Dataset Descriptions

| File | Rows | Description |
|------|------|-------------|
| 01_fund_master.csv | 40 | Scheme metadata, risk, expense ratio |
| 02_nav_history.csv | 46,000 | Daily NAV 2022–2026 |
| 03_aum_by_fund_house.csv | 90 | Quarterly AUM |
| 04_monthly_sip_inflows.csv | 48 | Monthly SIP data |
| 05_category_inflows.csv | 144 | Category-level inflows |
| 06_industry_folio_count.csv | 21 | Quarterly folio count |
| 07_scheme_performance.csv | 40 | Performance metrics |
| 08_investor_transactions.csv | 32,778 | Transaction records |
| 09_portfolio_holdings.csv | 322 | Stock holdings |
| 10_benchmark_indices.csv | 8,050 | NIFTY/BSE indices |

---

## 🏆 Key Results

| Metric | Result |
|--------|--------|
| Avg 3yr CAGR | 14.09% |
| Best Sharpe Ratio | 1.45 (Mirae Asset Large Cap) |
| SIP Growth (2022–2025) | +169% |
| Total Folios Growth | +97% (13.26→26.12 Cr) |
| Top Scored Fund | Mirae Asset Large Cap (85.9/100) |

---

## 🔗 Links

- **GitHub**: https://github.com/akshayasada38/bluestock-mf-capstone
- **Data Source**: AMFI India + mfapi.in + Bluestock Fintech
- **Intern**: Akshaya Sada | Jun 2026
