# Data Dictionary
## Bluestock MF Capstone Project — Day 2

---

## 01_fund_master.csv

| Column | Type | Description |
|--------|------|-------------|
| amfi_code | TEXT | AMFI unique scheme code (Primary Key) |
| fund_house | TEXT | AMC name (e.g. SBI Mutual Fund) |
| scheme_name | TEXT | Full official AMFI scheme name |
| category | TEXT | Equity / Debt / Hybrid |
| sub_category | TEXT | Large Cap / Mid Cap / Small Cap / Liquid etc. |
| plan | TEXT | Regular or Direct |
| launch_date | DATE | Fund launch date (YYYY-MM-DD) |
| benchmark | TEXT | Official benchmark index |
| expense_ratio_pct | REAL | Annual expense ratio in % (e.g. 1.05) |
| exit_load_pct | REAL | Exit load % (0 for Liquid/Index funds) |
| fund_manager | TEXT | Name of primary fund manager |
| risk_category | TEXT | SEBI risk: Low / Moderate / High / Very High |
| sebi_category_code | TEXT | Internal code: EC01=LargeCap, DC01=Liquid |

---

## 02_nav_history.csv

| Column | Type | Description |
|--------|------|-------------|
| amfi_code | TEXT | Foreign key to fund_master |
| date | DATE | NAV date (business days only, YYYY-MM-DD) |
| nav | REAL | NAV in Rs. (e.g. 892.4560) |
| daily_return | REAL | Computed: (nav_t - nav_t-1) / nav_t-1 |

---

## 03_aum_by_fund_house.csv

| Column | Type | Description |
|--------|------|-------------|
| fund_house | TEXT | AMC name |
| month | TEXT | YYYY-MM format |
| aum_lakh_crore | REAL | Total AUM in Rs. lakh crore |

---

## 04_monthly_sip_inflows.csv

| Column | Type | Description |
|--------|------|-------------|
| month | TEXT | YYYY-MM format |
| sip_inflow_crore | REAL | Total SIP inflows in Rs. crore |
| active_sip_accounts_crore | REAL | Active SIP accounts in crore |
| new_sip_accounts_lakh | REAL | New SIP registrations in lakh |
| sip_aum_lakh_crore | REAL | Total SIP AUM in Rs. lakh crore |
| yoy_growth_pct | REAL | YoY growth % (NULL for first 12 months — expected) |

---

## 05_category_inflows.csv

| Column | Type | Description |
|--------|------|-------------|
| month | TEXT | YYYY-MM format |
| category | TEXT | Fund category |
| net_inflow_crore | REAL | Net inflows in Rs. crore |

---

## 06_industry_folio_count.csv

| Column | Type | Description |
|--------|------|-------------|
| month | TEXT | YYYY-MM format |
| total_folios_crore | REAL | Total investor folios in crore |

---

## 07_scheme_performance.csv

| Column | Type | Description |
|--------|------|-------------|
| amfi_code | TEXT | Foreign key to fund_master |
| return_1yr_pct | REAL | 1-year return % |
| return_3yr_pct | REAL | 3-year annualised return % |
| return_5yr_pct | REAL | 5-year annualised return % |
| sharpe_ratio | REAL | Risk-adjusted return (higher = better) |
| alpha | REAL | Excess return over benchmark |
| beta | REAL | Sensitivity to market movements |
| expense_ratio_pct | REAL | Annual expense ratio % |

---

## 08_investor_transactions.csv

| Column | Type | Description |
|--------|------|-------------|
| transaction_id | TEXT | Unique transaction ID (Primary Key) |
| amfi_code | TEXT | Foreign key to fund_master |
| transaction_date | DATE | Date of transaction (YYYY-MM-DD) |
| transaction_type | TEXT | SIP / Lumpsum / Redemption / Switch |
| amount | REAL | Transaction amount in Rs. |
| units | REAL | Units purchased or redeemed |
| nav_at_transaction | REAL | NAV on transaction date |
| investor_age_group | TEXT | Age bracket (e.g. 25-34) |
| city_tier | TEXT | T1 / T2 / T3 (Tier 1/2/3 city) |
| state | TEXT | Indian state name |
| kyc_status | TEXT | KYC / NON-KYC |

---

## 09_portfolio_holdings.csv

| Column | Type | Description |
|--------|------|-------------|
| amfi_code | TEXT | Foreign key to fund_master |
| stock_name | TEXT | Name of held equity/debt instrument |
| sector | TEXT | Sector classification |
| holding_pct | REAL | % of portfolio in this holding |
| month | TEXT | YYYY-MM format |

---

## 10_benchmark_indices.csv

| Column | Type | Description |
|--------|------|-------------|
| date | DATE | Trading date (YYYY-MM-DD) |
| index_name | TEXT | e.g. Nifty 50, Nifty 100, BSE SmallCap |
| close_value | REAL | Closing index value |
| daily_return | REAL | Daily return % |

---

## Notes
- All monetary values are in **Indian Rupees (Rs.)**
- AUM columns with `lakh_crore` suffix = Rs. lakh crore (1 lakh crore = Rs. 1 trillion)
- AUM columns with `crore` suffix = Rs. crore
- Dates follow **YYYY-MM-DD** format throughout
- Source: AMFI India + mfapi.in + Bluestock Fintech provided datasets
