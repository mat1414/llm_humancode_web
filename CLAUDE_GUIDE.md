# Claude Guide: Model Parameter Human Coding Framework

## Quick Reference

| Resource | Link/Location |
|----------|---------------|
| **GitHub Repo** | https://github.com/mat1414/llm_humancode_web |
| **Streamlit App** | https://share.streamlit.io (deploy from GitHub) |
| **Local Directory** | `/home/ben/projects/llm_humancode_web` |

---

## Overview

This project provides a web-based Streamlit interface for human validation of LLM-estimated model parameters from FOMC transcripts, following the Mullainathan et al. (2024) framework for LLM output validation.

**Current Implementation**: Phillips Curve Classification - LIVE on Streamlit Cloud

**Planned**: Stock Market Wealth Effects classification (to be implemented later)

---

## Project Structure

```
llm_humancode_web/
├── coding_interface.py          # Main Streamlit app (deployed to cloud)
├── validation_analysis.py       # Cohen's kappa & confusion matrix analysis
├── phillips_sampler.py          # Stratified sampler for Phillips curve
├── parameter_sampler.py         # Generic template (unused)
├── requirements.txt             # Python dependencies for Streamlit Cloud
├── .gitignore                   # Git ignore rules
├── CLAUDE_GUIDE.md              # This file
├── original_scripts/            # Original LLM classification scripts & data
│   ├── 07.1_phillips_classication.py    # Claude prompts for Phillips curve
│   ├── 07.2_stock_market_wealth.py      # Claude prompts for wealth effects
│   ├── all_arguments.pkl                # Full FOMC arguments (56MB)
│   ├── phillips_classifications.pkl     # Claude's Phillips classifications
│   ├── stock_market_wealth_classifications.pkl
│   └── wealth_arguments_with_classification.pkl
└── validation_samples/
    ├── production/              # Coding files for deployment
    │   ├── coding_phillips.csv  # 200 arguments for human coders
    │   ├── key_phillips.csv     # Validation key (hidden from coders)
    │   └── stats_phillips.json  # Sample statistics
    └── coded/                   # Local storage (not deployed)
```

---

## Deployment Architecture

### How It Works

1. **Code lives on GitHub**: https://github.com/mat1414/llm_humancode_web
2. **Streamlit Cloud pulls from GitHub** and deploys automatically
3. **Coders access the web app** via Streamlit Cloud URL
4. **Results are downloaded** by coders (cloud filesystem is ephemeral)
5. **Coders share CSV files** with the research team

### Key Limitation

Streamlit Cloud has an **ephemeral filesystem** - files don't persist between sessions. Therefore:
- Coders must **download their results CSV** before closing the browser
- To resume, coders **upload their previous results file**
- All result CSVs should be collected and stored locally or on Dropbox

---

## Updating the Deployed App

### Step 1: Make Changes Locally

```bash
cd /home/ben/projects/llm_humancode_web

# Edit files as needed
# e.g., update coding_interface.py, add new features, etc.
```

### Step 2: Commit Changes

```bash
git add -A
git status  # Review what will be committed

git commit -m "Description of changes"
```

### Step 3: Push to GitHub

```bash
git push origin main
```

### Step 4: Streamlit Auto-Deploys

Streamlit Cloud automatically detects the push and redeploys within ~1-2 minutes. No manual action needed.

### Verify Deployment

1. Go to https://share.streamlit.io
2. Check your app's status (should show "Running")
3. Visit the app URL to verify changes

---

## Adding a New Coding Interface (e.g., Stock Market Wealth Effects)

### Option A: Add to Existing App (Multi-page)

1. Create new sampler: `wealth_effects_sampler.py`
2. Generate sample: `python wealth_effects_sampler.py`
3. Modify `coding_interface.py` to support both measures (add dropdown to select measure type)
4. Commit and push

### Option B: Create Separate App

1. Create `coding_interface_wealth.py`
2. Deploy as separate Streamlit app
3. In Streamlit Cloud, create new app pointing to the new file

### Steps for Wealth Effects Implementation

```python
# 1. Create wealth_effects_sampler.py (similar to phillips_sampler.py)
# Categories: strong, weak, moderate, none
# Source variables: Growth, Employment, Stock Market, Credit Markets

# 2. Generate sample
python wealth_effects_sampler.py

# 3. Update coding_interface.py or create new one

# 4. Commit and push
git add -A
git commit -m "Add stock market wealth effects coding"
git push origin main
```

---

## Phillips Curve Classification Details

### Task Description

Human coders classify FOMC speaker statements based on whether they express a belief about how labor market conditions affect inflation (the Phillips curve relationship).

### Classification Categories

| Category | Numeric | Description |
|----------|---------|-------------|
| **STEEP** | 1 | Labor markets SIGNIFICANTLY affect inflation |
| **FLAT** | -1 | Labor markets have LITTLE/NO effect on inflation |
| **MODERATE** | 0 | Qualified/partial relationship |
| **NONE** | NaN | No Phillips curve belief expressed (default) |

### Context Shown to Coders

- **Quotation**: Direct quote from FOMC transcript
- **Description**: Short summary of the argument
- **Explanation**: Policy implication/interpretation
- **Variable**: Economic variable (Growth, Inflation, or Employment)

### Current Sample

| Category | Sampled | Available in Full Dataset |
|----------|---------|---------------------------|
| Steep | 50 | 5,651 |
| Flat | 50 | 1,753 |
| Moderate | 50 | 864 |
| None | 50 | 74,501 |
| **Total** | **200** | 82,769 |

---

## Workflow for Coders

### Initial Coding Session

1. Go to the Streamlit app URL
2. Enter your name in the sidebar
3. Select "Use default sample" (200 arguments pre-loaded)
4. For each argument:
   - Read quotation, description, explanation
   - Select classification (steep/flat/moderate/none)
   - Click "Save & Continue"
5. **Important**: Click "Download Results CSV" before closing browser

### Resuming a Session

1. Go to the Streamlit app URL
2. Enter your name
3. In "Resume Session" section, upload your previous results CSV
4. Click "Load Session"
5. Continue coding from where you left off
6. Download updated results when done

### Submitting Results

Coders should send their final `coded_{name}_phillips_{timestamp}.csv` file to the research team via email or shared Dropbox folder.

---

## Running Validation Analysis

After collecting all coder results:

### Step 1: Collect Results

Place all `coded_*_phillips_*.csv` files in:
```
/home/ben/projects/llm_humancode_web/validation_samples/coded/
```

### Step 2: Run Analysis

```bash
cd /home/ben/projects/llm_humancode_web
python -c "from validation_analysis import run_validation; run_validation()"
```

### Output

- Cohen's kappa (unweighted and weighted)
- Confusion matrix
- Per-category precision, recall, F1
- Disagreement analysis
- `confusion_matrix_phillips.png` visualization

---

## Git Commands Reference

### Check Status
```bash
cd /home/ben/projects/llm_humancode_web
git status
```

### View Recent Commits
```bash
git log --oneline -10
```

### Pull Latest Changes
```bash
git pull origin main
```

### Push Updates
```bash
git add -A
git commit -m "Your message"
git push origin main
```

### Discard Local Changes
```bash
git checkout -- filename.py  # Specific file
git checkout -- .            # All files
```

---

## Regenerating the Coding Sample

If you need a new random sample:

```bash
cd /home/ben/projects/llm_humancode_web

# Edit phillips_sampler.py to change seed or sample size if needed

python phillips_sampler.py

# Commit and push new sample
git add validation_samples/production/
git commit -m "Regenerate Phillips curve sample"
git push origin main
```

---

## Troubleshooting

### App Not Updating After Push

1. Check Streamlit Cloud dashboard for deployment status
2. May take 1-2 minutes to redeploy
3. Try hard refresh (Ctrl+Shift+R) in browser

### Large File Push Errors

```bash
git config http.postBuffer 524288000
git push origin main
```

### Coder Lost Their Progress

- If they downloaded a results CSV previously, they can upload it to resume
- If no download exists, they need to start over (this is why downloading is important!)

### Import Errors on Streamlit Cloud

Check `requirements.txt` has all needed packages:
```
streamlit>=1.24.0
pandas>=1.5.0
numpy>=1.23.0
scikit-learn>=1.2.0
scipy>=1.10.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

---

## Data Files Reference

### Source Data

| File | Size | Contents |
|------|------|----------|
| `all_arguments.pkl` | 56MB | 102,419 FOMC arguments |
| `phillips_classifications.pkl` | 1.9MB | Claude's Phillips classifications |
| `stock_market_wealth_classifications.pkl` | 1.8MB | Claude's wealth effect classifications |

### Generated Files

| File | Contents |
|------|----------|
| `coding_phillips.csv` | 200 arguments for human coders (no Claude labels) |
| `key_phillips.csv` | Validation key with Claude's classifications |
| `stats_phillips.json` | Sample statistics |

---

## Future: Stock Market Wealth Effects

**Status**: Data available, interface not yet built

**Classification Categories** (planned):
| Category | Numeric | Description |
|----------|---------|-------------|
| STRONG | 1 | Stock markets significantly affect consumption/economy |
| WEAK | -1 | Stock markets have little/no effect |
| MODERATE | 0 | Qualified/partial relationship |
| NONE | NaN | No wealth effect belief expressed |

**Source Variables**: Growth, Employment, Stock Market, Credit Markets

**To implement**: Follow the same pattern as Phillips curve - create sampler, update/create interface, deploy.

---

## Contact & Context

This project is part of a larger research effort involving FOMC transcript analysis. The validation framework ensures that LLM-estimated parameters can be used reliably in academic research by quantifying and correcting any systematic biases.

### Related Projects

- **Original FOMC Argument Coding**: `/home/ben/llm_humancode/`
- **Model Fit Analysis**: `/home/ben/projects/gdm_parameter_extraction_vf/`
