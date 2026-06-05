-- ============================================================
-- queries.sql
-- Bluestock MF Capstone — 10 Analytical SQL Queries
-- Day 2: SQL Analytics
-- ============================================================

-- Q1: Top 5 fund houses by latest AUM
SELECT
    fund_house,
    ROUND(SUM(aum_lakh_crore), 2) AS total_aum_lakh_crore
FROM fact_aum
WHERE month = (SELECT MAX(month) FROM fact_aum)
GROUP BY fund_house
ORDER BY total_aum_lakh_crore DESC
LIMIT 5;

-- Q2: Average NAV per month for each fund (last 6 months)
SELECT
    f.scheme_name,
    SUBSTR(n.nav_date, 1, 7)   AS month,
    ROUND(AVG(n.nav), 4)       AS avg_nav
FROM fact_nav n
JOIN dim_fund f ON n.amfi_code = f.amfi_code
WHERE n.nav_date >= DATE('now', '-6 months')
GROUP BY f.scheme_name, month
ORDER BY f.scheme_name, month;

-- Q3: SIP inflow YoY growth
SELECT
    month,
    sip_inflow_crore,
    yoy_growth_pct,
    ROUND(LAG(sip_inflow_crore, 12) OVER (ORDER BY month), 2) AS sip_prev_year
FROM monthly_sip_inflows
ORDER BY month;

-- Q4: Transaction amount by state (top 10 states)
SELECT
    state,
    COUNT(*)                        AS transaction_count,
    ROUND(SUM(amount), 2)           AS total_amount,
    ROUND(AVG(amount), 2)           AS avg_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_amount DESC
LIMIT 10;

-- Q5: Funds with expense ratio less than 1%
SELECT
    amfi_code,
    fund_house,
    scheme_name,
    sub_category,
    expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

-- Q6: Best performing funds by 1-year return
SELECT
    f.scheme_name,
    f.fund_house,
    f.sub_category,
    p.return_1yr_pct,
    p.sharpe_ratio
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.return_1yr_pct DESC
LIMIT 10;

-- Q7: NAV growth % from start to latest date per fund
SELECT
    f.scheme_name,
    f.fund_house,
    MIN(n.nav)                                      AS nav_start,
    MAX(n.nav)                                      AS nav_latest,
    ROUND((MAX(n.nav) - MIN(n.nav)) / MIN(n.nav) * 100, 2) AS total_growth_pct
FROM fact_nav n
JOIN dim_fund f ON n.amfi_code = f.amfi_code
GROUP BY n.amfi_code
ORDER BY total_growth_pct DESC;

-- Q8: SIP vs Lumpsum vs Redemption split
SELECT
    transaction_type,
    COUNT(*)                    AS count,
    ROUND(SUM(amount), 2)       AS total_amount,
    ROUND(AVG(amount), 2)       AS avg_amount,
    ROUND(SUM(amount) * 100.0 /
        SUM(SUM(amount)) OVER(), 2) AS pct_of_total
FROM fact_transactions
GROUP BY transaction_type
ORDER BY total_amount DESC;

-- Q9: Category-wise fund count and average expense ratio
SELECT
    category,
    sub_category,
    COUNT(*)                            AS fund_count,
    ROUND(AVG(expense_ratio_pct), 3)    AS avg_expense_ratio,
    ROUND(MIN(expense_ratio_pct), 3)    AS min_expense_ratio,
    ROUND(MAX(expense_ratio_pct), 3)    AS max_expense_ratio
FROM dim_fund
GROUP BY category, sub_category
ORDER BY category, fund_count DESC;

-- Q10: Monthly transaction volume trend (last 12 months)
SELECT
    SUBSTR(transaction_date, 1, 7)  AS month,
    COUNT(*)                        AS transaction_count,
    ROUND(SUM(amount), 2)           AS total_amount,
    COUNT(DISTINCT amfi_code)       AS funds_transacted
FROM fact_transactions
WHERE transaction_date >= DATE('now', '-12 months')
GROUP BY month
ORDER BY month;
