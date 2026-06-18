"""
compute_metrics.py
Day 4 — Fund Performance Analytics
Computes: daily returns, CAGR, Sharpe, Sortino, Alpha, Beta,
          Max Drawdown, Fund Scorecard, Benchmark Comparison
"""

import warnings; warnings.filterwarnings("ignore")
import pandas as pd
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pathlib import Path

BASE    = Path(__file__).parent.parent
RAW     = BASE / "data" / "raw"
PROC    = BASE / "data" / "processed"
CHARTS  = BASE / "reports" / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

RF_ANNUAL  = 0.065          # RBI repo rate proxy
RF_DAILY   = RF_ANNUAL / 252
TRADING_DAYS = 252
SEP = "=" * 65

plt.rcParams.update({
    "figure.facecolor": "#0f1117", "axes.facecolor": "#1a1d2e",
    "axes.edgecolor": "#444466", "axes.labelcolor": "#ccccdd",
    "xtick.color": "#aaaacc", "ytick.color": "#aaaacc",
    "text.color": "#ccccdd", "grid.color": "#2a2d3e",
    "grid.alpha": 0.5, "axes.titlesize": 13,
})
COLORS = ["#6c8ebf","#82b366","#d6a91a","#e07b54","#9b72cf",
          "#4db6ac","#e57373","#81c784","#ffb74d","#64b5f6"]


# ── Load ─────────────────────────────────────────────────────────────────────
def load_data():
    nav   = pd.read_csv(RAW / "02_nav_history.csv", parse_dates=["date"])
    funds = pd.read_csv(RAW / "01_fund_master.csv")
    bench = pd.read_csv(RAW / "10_benchmark_indices.csv", parse_dates=["date"])
    nav   = nav.merge(funds[["amfi_code","scheme_name","fund_house",
                              "sub_category","plan","expense_ratio_pct"]], on="amfi_code", how="left")
    nav   = nav.sort_values(["amfi_code","date"]).reset_index(drop=True)
    return nav, funds, bench


# ── Task 1: Daily Returns ─────────────────────────────────────────────────────
def compute_daily_returns(nav):
    print("Task 1: Daily Returns...")
    nav["daily_return"] = nav.groupby("amfi_code")["nav"].pct_change()
    # Validate
    stats_ret = nav["daily_return"].dropna().describe()
    print(f"  Mean daily return : {stats_ret['mean']*100:.4f}%")
    print(f"  Std daily return  : {stats_ret['std']*100:.4f}%")
    print(f"  Min               : {stats_ret['min']*100:.4f}%")
    print(f"  Max               : {stats_ret['max']*100:.4f}%")
    outliers = (nav["daily_return"].abs() > 0.15).sum()
    print(f"  Outliers >15%     : {outliers} ✅")
    return nav


# ── Task 2: CAGR ─────────────────────────────────────────────────────────────
def compute_cagr(nav):
    print("\nTask 2: CAGR Computation...")
    results = []
    latest_date = nav["date"].max()
    
    for code, grp in nav.groupby("amfi_code"):
        grp = grp.sort_values("date")
        name = grp["scheme_name"].iloc[0]
        fh   = grp["fund_house"].iloc[0]
        cat  = grp["sub_category"].iloc[0]
        plan = grp["plan"].iloc[0]
        nav_latest = grp["nav"].iloc[-1]
        
        row = {"amfi_code": code, "scheme_name": name,
               "fund_house": fh, "sub_category": cat, "plan": plan,
               "nav_latest": round(nav_latest, 4)}
        
        for years, label in [(1,"cagr_1yr"), (3,"cagr_3yr"), (5,"cagr_5yr")]:
            start_date = latest_date - pd.DateOffset(years=years)
            sub = grp[grp["date"] >= start_date]
            if len(sub) >= 50:
                nav_start = sub["nav"].iloc[0]
                nav_end   = sub["nav"].iloc[-1]
                n_years   = (sub["date"].iloc[-1] - sub["date"].iloc[0]).days / 365.25
                cagr      = (nav_end / nav_start) ** (1 / n_years) - 1
                row[label] = round(cagr * 100, 4)
            else:
                row[label] = np.nan
        results.append(row)
    
    cagr_df = pd.DataFrame(results)
    print(f"  Computed CAGR for {len(cagr_df)} funds ✅")
    print(f"  Avg 3yr CAGR: {cagr_df['cagr_3yr'].mean():.2f}%")
    return cagr_df


# ── Task 3: Sharpe Ratio ──────────────────────────────────────────────────────
def compute_sharpe(nav):
    print("\nTask 3: Sharpe Ratio...")
    results = []
    for code, grp in nav.groupby("amfi_code"):
        ret = grp["daily_return"].dropna()
        if len(ret) < 50: continue
        excess = ret - RF_DAILY
        sharpe = (excess.mean() / ret.std()) * np.sqrt(TRADING_DAYS)
        results.append({"amfi_code": code, "sharpe_ratio": round(sharpe, 4),
                         "ann_return_pct": round(ret.mean() * TRADING_DAYS * 100, 4),
                         "ann_volatility_pct": round(ret.std() * np.sqrt(TRADING_DAYS) * 100, 4)})
    df = pd.DataFrame(results)
    df["sharpe_rank"] = df["sharpe_ratio"].rank(ascending=False).astype(int)
    print(f"  Best Sharpe : {df['sharpe_ratio'].max():.4f}")
    print(f"  Worst Sharpe: {df['sharpe_ratio'].min():.4f}")
    return df


# ── Task 4: Sortino Ratio ─────────────────────────────────────────────────────
def compute_sortino(nav):
    print("\nTask 4: Sortino Ratio...")
    results = []
    for code, grp in nav.groupby("amfi_code"):
        ret = grp["daily_return"].dropna()
        if len(ret) < 50: continue
        excess    = ret - RF_DAILY
        downside  = ret[ret < 0]
        down_std  = downside.std() * np.sqrt(TRADING_DAYS)
        sortino   = (excess.mean() * TRADING_DAYS) / down_std if down_std > 0 else np.nan
        results.append({"amfi_code": code, "sortino_ratio": round(sortino, 4),
                         "downside_vol_pct": round(downside.std() * np.sqrt(TRADING_DAYS) * 100, 4)})
    df = pd.DataFrame(results)
    df["sortino_rank"] = df["sortino_ratio"].rank(ascending=False).astype(int)
    print(f"  Avg Sortino : {df['sortino_ratio'].mean():.4f} ✅")
    return df


# ── Task 5: Alpha & Beta ──────────────────────────────────────────────────────
def compute_alpha_beta(nav, bench):
    print("\nTask 5: Alpha & Beta...")
    nifty100 = (bench[bench["index_name"]=="NIFTY100"]
                .sort_values("date").copy())
    nifty100["bench_return"] = nifty100["close_value"].pct_change()
    nifty100 = nifty100[["date","bench_return"]].dropna()

    results = []
    for code, grp in nav.groupby("amfi_code"):
        grp = grp.sort_values("date").dropna(subset=["daily_return"])
        merged = grp.merge(nifty100, on="date", how="inner")
        if len(merged) < 100: continue
        
        slope, intercept, r_val, p_val, _ = stats.linregress(
            merged["bench_return"], merged["daily_return"])
        
        alpha_annual = intercept * TRADING_DAYS * 100
        beta         = round(slope, 4)
        r_squared    = round(r_val**2, 4)
        
        results.append({
            "amfi_code"    : code,
            "scheme_name"  : grp["scheme_name"].iloc[0],
            "fund_house"   : grp["fund_house"].iloc[0],
            "sub_category" : grp["sub_category"].iloc[0],
            "plan"         : grp["plan"].iloc[0],
            "alpha_annual_pct": round(alpha_annual, 4),
            "beta"         : beta,
            "r_squared"    : r_squared,
        })
    
    df = pd.DataFrame(results)
    df["alpha_rank"] = df["alpha_annual_pct"].rank(ascending=False).astype(int)
    print(f"  Computed Alpha/Beta for {len(df)} funds ✅")
    print(f"  Avg Beta  : {df['beta'].mean():.4f}")
    print(f"  Avg Alpha : {df['alpha_annual_pct'].mean():.4f}%")
    return df


# ── Task 6: Maximum Drawdown ──────────────────────────────────────────────────
def compute_max_drawdown(nav):
    print("\nTask 6: Maximum Drawdown...")
    results = []
    for code, grp in nav.groupby("amfi_code"):
        grp = grp.sort_values("date").copy()
        grp["rolling_max"] = grp["nav"].cummax()
        grp["drawdown"]    = grp["nav"] / grp["rolling_max"] - 1
        
        max_dd     = grp["drawdown"].min()
        max_dd_idx = grp["drawdown"].idxmin()
        max_dd_date= grp.loc[max_dd_idx, "date"]
        
        # Find peak before max drawdown
        peak_idx  = grp.loc[:max_dd_idx, "nav"].idxmax()
        peak_date = grp.loc[peak_idx, "date"]
        
        results.append({
            "amfi_code"       : code,
            "scheme_name"     : grp["scheme_name"].iloc[0],
            "max_drawdown_pct": round(max_dd * 100, 4),
            "drawdown_peak_date": str(peak_date.date()),
            "drawdown_trough_date": str(max_dd_date.date()),
            "drawdown_duration_days": (max_dd_date - peak_date).days,
        })
    
    df = pd.DataFrame(results)
    df["dd_rank"] = df["max_drawdown_pct"].rank(ascending=False).astype(int)
    worst = df.loc[df["max_drawdown_pct"].idxmin()]
    print(f"  Worst Drawdown: {worst['max_drawdown_pct']:.2f}% ({worst['scheme_name'][:30]})")
    print(f"  Avg Drawdown  : {df['max_drawdown_pct'].mean():.2f}% ✅")
    return df


# ── Task 7: Fund Scorecard ────────────────────────────────────────────────────
def compute_scorecard(cagr_df, sharpe_df, alpha_df, dd_df, funds):
    print("\nTask 7: Fund Scorecard...")
    
    sc = cagr_df[["amfi_code","scheme_name","fund_house","sub_category","plan"]].copy()
    sc = sc.merge(cagr_df[["amfi_code","cagr_3yr"]], on="amfi_code", how="left")
    sc = sc.merge(sharpe_df[["amfi_code","sharpe_ratio","sharpe_rank"]], on="amfi_code", how="left")
    sc = sc.merge(alpha_df[["amfi_code","alpha_annual_pct","alpha_rank"]], on="amfi_code", how="left")
    sc = sc.merge(dd_df[["amfi_code","max_drawdown_pct","dd_rank"]], on="amfi_code", how="left")
    sc = sc.merge(funds[["amfi_code","expense_ratio_pct"]], on="amfi_code", how="left")
    
    # Ranks (lower rank number = better)
    sc["cagr_rank"] = sc["cagr_3yr"].rank(ascending=False)
    sc["er_rank"]   = sc["expense_ratio_pct"].rank(ascending=True)   # lower ER is better
    sc["dd_rank"]   = sc["max_drawdown_pct"].rank(ascending=False)   # less negative is better
    
    n = len(sc)
    # Composite score: higher = better
    sc["score"] = (
        0.30 * (1 - (sc["cagr_rank"]   - 1) / (n - 1)) * 100 +
        0.25 * (1 - (sc["sharpe_rank"] - 1) / (n - 1)) * 100 +
        0.20 * (1 - (sc["alpha_rank"]  - 1) / (n - 1)) * 100 +
        0.15 * (1 - (sc["er_rank"]     - 1) / (n - 1)) * 100 +
        0.10 * (1 - (sc["dd_rank"]     - 1) / (n - 1)) * 100
    )
    sc["score"]        = sc["score"].round(2)
    sc["overall_rank"] = sc["score"].rank(ascending=False).astype(int)
    sc = sc.sort_values("overall_rank")
    
    print(f"  Top Fund   : {sc.iloc[0]['scheme_name'][:40]} — Score: {sc.iloc[0]['score']:.1f}")
    print(f"  Bottom Fund: {sc.iloc[-1]['scheme_name'][:40]} — Score: {sc.iloc[-1]['score']:.1f}")
    return sc


# ── Task 8: Benchmark Comparison Chart ───────────────────────────────────────
def benchmark_chart(nav, bench, scorecard):
    print("\nTask 8: Benchmark Comparison Chart...")
    
    # Top 5 funds by scorecard
    top5 = scorecard.head(5)["amfi_code"].tolist()
    
    # Benchmark data
    nifty50  = bench[bench["index_name"]=="NIFTY50"].sort_values("date").copy()
    nifty100 = bench[bench["index_name"]=="NIFTY100"].sort_values("date").copy()
    start    = pd.Timestamp("2023-01-01")
    
    nifty50  = nifty50[nifty50["date"] >= start].copy()
    nifty100 = nifty100[nifty100["date"] >= start].copy()
    nifty50["norm"]  = nifty50["close_value"]  / nifty50["close_value"].iloc[0]  * 100
    nifty100["norm"] = nifty100["close_value"] / nifty100["close_value"].iloc[0] * 100
    
    fig, axes = plt.subplots(2, 1, figsize=(14, 12))
    fig.patch.set_facecolor("#0f1117")
    
    # Chart A: Normalised performance
    axes[0].plot(nifty50["date"],  nifty50["norm"],  color="#ffb74d", linewidth=2.5,
                 linestyle="--", label="NIFTY 50", zorder=5)
    axes[0].plot(nifty100["date"], nifty100["norm"], color="#ff8a65", linewidth=2.5,
                 linestyle=":", label="NIFTY 100", zorder=5)
    
    tracking_errors = []
    for i, code in enumerate(top5):
        grp = nav[nav["amfi_code"]==code].copy()
        grp = grp[grp["date"] >= start].sort_values("date")
        if len(grp) < 10: continue
        grp["norm"] = grp["nav"] / grp["nav"].iloc[0] * 100
        name = grp["scheme_name"].iloc[0].split("-")[0].strip()[:22]
        axes[0].plot(grp["date"], grp["norm"], color=COLORS[i], linewidth=1.8, label=name)
        
        # Tracking error vs NIFTY 100
        merged = grp.merge(nifty100[["date","close_value"]].rename(
            columns={"close_value":"bench_val"}), on="date", how="inner")
        if len(merged) > 10:
            merged["fund_ret"]  = merged["nav"].pct_change()
            merged["bench_ret"] = merged["bench_val"].pct_change()
            te = (merged["fund_ret"] - merged["bench_ret"]).std() * np.sqrt(252) * 100
            tracking_errors.append({"scheme": name, "tracking_error_pct": round(te, 4)})
    
    axes[0].set_title("Top 5 Funds vs NIFTY 50 & NIFTY 100 (Base=100, Jan 2023)", pad=12)
    axes[0].set_ylabel("Normalised Value (Base 100)")
    axes[0].legend(fontsize=8, framealpha=0.3); axes[0].grid(True)
    
    # Chart B: Tracking Error
    if tracking_errors:
        te_df = pd.DataFrame(tracking_errors).sort_values("tracking_error_pct")
        bars = axes[1].barh(te_df["scheme"], te_df["tracking_error_pct"],
                             color=COLORS[:len(te_df)], alpha=0.85)
        for bar, val in zip(bars, te_df["tracking_error_pct"]):
            axes[1].text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                         f"{val:.2f}%", va="center", fontsize=9)
        axes[1].set_title("Tracking Error vs NIFTY 100 (Annualised)", pad=12)
        axes[1].set_xlabel("Tracking Error (%)")
        axes[1].grid(True, axis="x")
    
    plt.suptitle("Benchmark Comparison — Top 5 Funds", fontsize=14, y=1.01)
    plt.tight_layout()
    out = CHARTS / "D4_benchmark_comparison.png"
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="#0f1117")
    plt.close()
    print(f"  ✅ Saved: D4_benchmark_comparison.png")
    
    return pd.DataFrame(tracking_errors) if tracking_errors else pd.DataFrame()


# ── Main ─────────────────────────────────────────────────────────────────────
def run():
    print(f"\n{SEP}\n  DAY 4 — FUND PERFORMANCE ANALYTICS\n{SEP}")
    
    nav, funds, bench = load_data()
    
    nav       = compute_daily_returns(nav)
    cagr_df   = compute_cagr(nav)
    sharpe_df = compute_sharpe(nav)
    sortino_df= compute_sortino(nav)
    alpha_df  = compute_alpha_beta(nav, bench)
    dd_df     = compute_max_drawdown(nav)
    scorecard = compute_scorecard(cagr_df, sharpe_df, alpha_df, dd_df, funds)
    te_df     = benchmark_chart(nav, bench, scorecard)
    
    # ── Save CSVs ─────────────────────────────────────────────────────────────
    print(f"\n{SEP}\n  SAVING CSVs\n{SEP}")
    PROC.mkdir(parents=True, exist_ok=True)
    
    # fund_scorecard.csv
    sc_out = PROC / "fund_scorecard.csv"
    scorecard.to_csv(sc_out, index=False)
    print(f"  ✅ fund_scorecard.csv ({len(scorecard)} rows)")
    
    # alpha_beta.csv
    ab_out = PROC / "alpha_beta.csv"
    alpha_df.to_csv(ab_out, index=False)
    print(f"  ✅ alpha_beta.csv ({len(alpha_df)} rows)")
    
    # full_metrics.csv
    full = (cagr_df
            .merge(sharpe_df[["amfi_code","sharpe_ratio","ann_volatility_pct"]], on="amfi_code", how="left")
            .merge(sortino_df[["amfi_code","sortino_ratio","downside_vol_pct"]], on="amfi_code", how="left")
            .merge(alpha_df[["amfi_code","alpha_annual_pct","beta","r_squared"]], on="amfi_code", how="left")
            .merge(dd_df[["amfi_code","max_drawdown_pct","drawdown_peak_date","drawdown_trough_date"]], on="amfi_code", how="left")
            .merge(scorecard[["amfi_code","score","overall_rank"]], on="amfi_code", how="left"))
    full_out = PROC / "full_performance_metrics.csv"
    full.to_csv(full_out, index=False)
    print(f"  ✅ full_performance_metrics.csv ({len(full)} rows)")
    
    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{SEP}\n  PERFORMANCE SUMMARY — TOP 10 FUNDS\n{SEP}")
    top10 = scorecard.head(10)[["overall_rank","scheme_name","sub_category",
                                  "cagr_3yr","sharpe_ratio","alpha_annual_pct",
                                  "max_drawdown_pct","score"]]
    print(top10.to_string(index=False))
    
    print(f"\n✅ Day 4 complete!")
    return full, scorecard, alpha_df

if __name__ == "__main__":
    run()
