"""
run_pipeline.py
Master execution script — Bluestock MF Capstone Project
Runs the complete pipeline in order: Ingest → ETL → Metrics → Analytics
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
SEP  = "=" * 65

def run(script: str, label: str) -> bool:
    """Run a Python script and return True if successful."""
    print(f"\n{SEP}")
    print(f"  ▶  {label}")
    print(SEP)
    result = subprocess.run([sys.executable, script], capture_output=False)
    if result.returncode == 0:
        print(f"  ✅ {label} — COMPLETE")
        return True
    else:
        print(f"  ❌ {label} — FAILED (exit code {result.returncode})")
        return False


def main():
    start = datetime.now()
    print(f"\n{'='*65}")
    print(f"  BLUESTOCK MF CAPSTONE — MASTER PIPELINE")
    print(f"  Started: {start.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*65}")

    steps = [
        (BASE / "data_ingestion.py",       "Step 1: Data Ingestion (Load 10 CSVs)"),
        (BASE / "live_nav_fetch.py",        "Step 2: Live NAV Fetch (mfapi.in)"),
        (BASE / "fund_exploration.py",      "Step 3: Fund Master Exploration & Validation"),
        (BASE / "scripts" / "etl_pipeline.py",    "Step 4: ETL Pipeline (Clean + Load SQLite)"),
        (BASE / "scripts" / "compute_metrics.py", "Step 5: Performance Metrics (Sharpe, Alpha, VaR)"),
        (BASE / "scripts" / "recommender.py",     "Step 6: Fund Recommender"),
    ]

    results = []
    for script, label in steps:
        if script.exists():
            ok = run(str(script), label)
        else:
            print(f"\n  ⚠️  Script not found: {script}")
            ok = False
        results.append((label, ok))

    # Summary
    end = datetime.now()
    duration = (end - start).seconds
    print(f"\n{SEP}")
    print(f"  PIPELINE SUMMARY")
    print(SEP)
    for label, ok in results:
        status = "✅" if ok else "❌"
        print(f"  {status}  {label}")

    passed = sum(1 for _, ok in results if ok)
    print(f"\n  {passed}/{len(results)} steps completed in {duration}s")
    print(f"  Finished: {end.strftime('%Y-%m-%d %H:%M:%S')}")
    print(SEP)


if __name__ == "__main__":
    main()
