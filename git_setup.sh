#!/bin/bash
# git_setup.sh
# Run this script ONCE to initialise the Git repo and push to GitHub.
# Usage: bash git_setup.sh

set -e  # Exit on any error

echo "=================================================="
echo "  GIT SETUP — Mutual Fund Analytics Project"
echo "=================================================="

# ── Step 1: Init repo ─────────────────────────────────────────────────────────
echo ""
echo "Step 1: Initialising Git repository..."
git init
git branch -M main

# ── Step 2: Create .gitignore ─────────────────────────────────────────────────
echo ""
echo "Step 2: Creating .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*.pyo
.env
venv/
.venv/
*.egg-info/

# Jupyter
.ipynb_checkpoints/
*.ipynb_checkpoints

# Data files (large raw CSVs — keep processed/reports)
data/raw/*.csv

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
EOF

echo "  .gitignore created."

# ── Step 3: Stage all files ───────────────────────────────────────────────────
echo ""
echo "Step 3: Staging files..."
git add .
git status

# ── Step 4: Day 1 commit ──────────────────────────────────────────────────────
echo ""
echo "Step 4: Making Day 1 commit..."
git commit -m "Day 1: Data ingestion complete"

echo ""
echo "✅ Local repo ready with Day 1 commit!"

# ── Step 5: Push to GitHub (update URL below) ─────────────────────────────────
echo ""
echo "=================================================="
echo "  PUSH TO GITHUB"
echo "=================================================="
echo ""
echo "To push to GitHub, run these commands:"
echo ""
echo "  git remote add origin https://github.com/YOUR_USERNAME/mf-analytics.git"
echo "  git push -u origin main"
echo ""
echo "Replace YOUR_USERNAME with your actual GitHub username."
echo "Create the repo on GitHub first (no README, no .gitignore)."
