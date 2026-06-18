"""
recommender.py
Day 6 — Simple Fund Recommender
Input: risk appetite (Low / Moderate / Moderately High / High / Very High)
Output: Top 3 funds by Sharpe ratio within matching risk_grade
"""

import pandas as pd
from pathlib import Path

BASE = Path(__file__).parent.parent
RAW  = BASE / "data" / "raw"


def recommend_funds(risk_appetite: str) -> pd.DataFrame:
    """
    Recommend top 3 funds based on risk appetite.
    Parameters:
        risk_appetite: "Low" | "Moderate" | "Moderately High" | "High" | "Very High"
    Returns:
        DataFrame with top 3 recommended funds
    """
    # Use perf file directly — it already has all needed columns
    perf = pd.read_csv(RAW / "07_scheme_performance.csv")

    risk_map = {
        "Low"            : ["Low"],
        "Moderate"       : ["Moderate", "Low"],
        "Moderately High": ["Moderately High", "Moderate"],
        "High"           : ["High", "Moderately High"],
        "Very High"      : ["Very High", "High"],
    }

    valid_input = list(risk_map.keys())
    if risk_appetite not in valid_input:
        print(f"  ❌ Invalid input. Choose from: {valid_input}")
        return pd.DataFrame()

    grades   = risk_map[risk_appetite]
    filtered = perf[perf["risk_grade"].isin(grades)]

    if filtered.empty:
        print(f"  ⚠️  No funds found for: {risk_appetite}")
        return pd.DataFrame()

    top3 = (filtered.sort_values("sharpe_ratio", ascending=False)
                    .head(3)
                    [["scheme_name","fund_house","plan",
                      "risk_grade","sharpe_ratio","return_3yr_pct",
                      "expense_ratio_pct","morningstar_rating"]]
                    .reset_index(drop=True))
    top3.index = top3.index + 1
    return top3


def run_recommender():
    """Run recommender for all risk levels."""
    SEP = "=" * 65
    print(f"\n{SEP}")
    print("  FUND RECOMMENDER — Bluestock MF Capstone")
    print(SEP)

    for risk in ["Low", "Moderate", "Moderately High", "High", "Very High"]:
        print(f"\n📊 Risk Appetite: {risk}")
        print("-" * 65)
        result = recommend_funds(risk)
        if not result.empty:
            for i, row in result.iterrows():
                print(f"  {i}. {row['scheme_name'][:45]}")
                print(f"     Fund House : {row['fund_house']}")
                print(f"     Plan       : {row['plan']}")
                print(f"     Sharpe     : {row['sharpe_ratio']:.4f}")
                print(f"     3yr Return : {row['return_3yr_pct']:.2f}%")
                print(f"     Expense    : {row['expense_ratio_pct']:.2f}%")
                print(f"     Rating     : {'⭐' * int(row['morningstar_rating'])}")

    print(f"\n{SEP}")
    print("✅ Recommendations complete!")


if __name__ == "__main__":
    run_recommender()
