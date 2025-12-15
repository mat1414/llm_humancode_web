# Claude Guide: Model Parameter Human Coding Framework

## Overview

This project provides a web-based interface for human validation of LLM-estimated model parameters from FOMC transcripts, following the Mullainathan et al. (2024) framework for LLM output validation.

**Current Implementation**: Phillips Curve Classification validation is complete and ready to use.

**Planned**: Stock Market Wealth Effects classification (to be implemented later).

---

## Project Structure

```
llm_humancode_web/
├── coding_interface.py          # Streamlit GUI for Phillips curve coding
├── validation_analysis.py       # Cohen's kappa & confusion matrix analysis
├── phillips_sampler.py          # Stratified sampler for Phillips curve
├── parameter_sampler.py         # Generic template (unused)
├── CLAUDE_GUIDE.md              # This file
├── original_scripts/            # Original LLM classification scripts
│   ├── 07.1_phillips_classication.py    # Claude prompts for Phillips curve
│   ├── 07.2_stock_market_wealth.py      # Claude prompts for wealth effects
│   ├── all_arguments.pkl                # Full FOMC arguments dataset
│   ├── phillips_classifications.pkl     # Claude's Phillips curve classifications
│   ├── stock_market_wealth_classifications.pkl  # Claude's wealth effect classifications
│   └── wealth_arguments_with_classification.pkl
├── data/                        # Reference data
│   └── arguments_with_classification.pkl
└── validation_samples/
    ├── production/              # Coding files
    │   ├── coding_phillips.csv  # For human coders (no Claude classifications)
    │   ├── key_phillips.csv     # Validation key (hidden from coders)
    │   └── stats_phillips.json  # Sample statistics
    └── coded/                   # Human coding outputs
        └── coded_{coder}_phillips_{timestamp}.csv
```

---

## Phillips Curve Classification

### Task Description

Human coders classify FOMC speaker statements based on whether they express a belief about how labor market conditions affect inflation (the Phillips curve relationship).

### Classification Categories

| Category | Numeric Value | Description |
|----------|---------------|-------------|
| **STEEP** | 1 | Labor markets SIGNIFICANTLY affect inflation |
| **FLAT** | -1 | Labor markets have LITTLE/NO effect on inflation |
| **MODERATE** | 0 | Qualified/partial relationship |
| **NONE** | NaN | No Phillips curve belief expressed (default) |

### Context Shown to Coders

For each argument, coders see:
- **Quotation**: Direct quote from FOMC transcript
- **Description**: Short summary of the argument
- **Explanation**: Policy implication/interpretation
- **Variable**: Economic variable (Growth, Inflation, or Employment)

Claude's classification is **hidden** from coders during the coding process.

### Sample Design

- **Target**: 50 arguments per classification category (200 total)
- **Stratification**: Equal representation of steep, flat, moderate, none
- **Source**: 82,770 arguments from FOMC transcripts (Growth, Inflation, Employment)

### Claude's Classification Distribution (Full Dataset)

| Category | Count | Percentage |
|----------|-------|------------|
| None | 76,320 | 92.2% |
| Steep | 4,254 | 5.1% |
| Flat | 1,730 | 2.1% |
| Moderate | 465 | 0.6% |

---

## Workflow

### Step 1: Generate Coding Sample (Already Done)

```bash
cd /home/ben/projects/llm_humancode_web
python phillips_sampler.py
```

Output:
- `validation_samples/production/coding_phillips.csv` - Give to coders
- `validation_samples/production/key_phillips.csv` - Hidden validation key

### Step 2: Human Coding

```bash
streamlit run coding_interface.py
```

1. Coder enters their name
2. Uploads `coding_phillips.csv`
3. For each argument:
   - Reads quotation, description, explanation
   - Selects classification (steep/flat/moderate/none)
   - Clicks "Save & Continue"
4. Progress auto-saves to `validation_samples/coded/`

### Step 3: Validation Analysis

After coding is complete:

```python
from validation_analysis import run_validation
results = run_validation()
```

Or run directly:
```bash
python validation_analysis.py
```

**Output metrics**:
- Overall accuracy
- Cohen's kappa (unweighted)
- Cohen's kappa (weighted, ordinal, for non-none categories)
- Confusion matrix
- Per-category precision, recall, F1
- Disagreement analysis

---

## Claude's Original Prompts

### Phillips Curve Prompt (from `07.1_phillips_classication.py`)

The prompt instructs Claude to:

1. **Check for explicit Phillips curve mentions** ("Phillips curve is flat/dead")
2. **Identify required components**:
   - Labor market indicators (unemployment, NAIRU, wage pressures, capacity)
   - Inflation outcomes (price pressures, inflation expectations, PCE)
3. **Identify causal connection** between the two components
4. **Classify the relationship type**:
   - STEEP: Strong causal language ("drives", "causes", "leads to")
   - FLAT: Disconnection language ("despite", "hasn't translated")
   - MODERATE: Hedging language ("some", "modest", "limited")
   - NULL: No belief expressed (default)

**Key rules**:
- Default to NULL unless clear belief expressed
- Both components must be present AND causally connected
- Mere description without interpretation = NULL

---

## File Descriptions

### `coding_interface.py`
Streamlit web application for human coding:
- Displays argument context (quotation, description, explanation)
- Radio buttons for classification selection
- Auto-saves progress after each coding
- Supports session resumption
- Shows progress bar

### `validation_analysis.py`
Analysis module using:
- `PhillipsValidationAnalyzer` class
- Cohen's kappa for categorical agreement
- Weighted kappa for ordinal analysis (steep > moderate > flat)
- Confusion matrix visualization
- Disagreement pattern analysis

### `phillips_sampler.py`
Stratified sampling:
- Loads `all_arguments.pkl` and `phillips_classifications.pkl`
- Filters to Growth/Inflation/Employment variables
- Samples 50 per category
- Creates blind coding file (no Claude classifications)
- Creates validation key (with Claude classifications)

---

## Data Structures

### Input: `all_arguments.pkl`
```
Columns:
- description: Short summary
- quotation: Direct quote from FOMC transcript
- explanation: Policy implication
- stablespeaker: Speaker identifier
- ymd: Meeting date (YYYYMMDD)
- variable: Economic variable (Growth/Inflation/Employment)
- belief_forecast_cyclical, belief_forecast_trend, etc.
```

### Input: `phillips_classifications.pkl`
```
pandas Series indexed by argument row number
Values: 1.0 (steep), -1.0 (flat), 0.0 (moderate), NaN (null)
```

### Output: `coded_{coder}_phillips_{timestamp}.csv`
```
Columns:
- coding_id: Unique identifier (PC_0001, etc.)
- coder_name: Human coder name
- classification: steep/flat/moderate/none
- notes: Optional coder notes
- coded_at: ISO timestamp
```

---

## Validation Metrics

### Cohen's Kappa Interpretation

| Kappa Range | Interpretation |
|-------------|----------------|
| < 0 | Less than chance |
| 0.00-0.20 | Slight agreement |
| 0.21-0.40 | Fair agreement |
| 0.41-0.60 | Moderate agreement |
| 0.61-0.80 | Substantial agreement |
| 0.81-1.00 | Almost perfect agreement |

### Weighted Kappa

For the ordinal categories (steep > moderate > flat), weighted kappa accounts for the severity of disagreements:
- steep vs flat = worst disagreement
- steep vs moderate = moderate disagreement
- moderate vs flat = moderate disagreement

---

## Future: Stock Market Wealth Effects

**Status**: Not yet implemented

**Classification Categories** (planned):
- STRONG: Stock markets significantly affect consumption/economy
- WEAK: Stock markets have little/no effect
- MODERATE: Qualified/partial relationship
- NONE: No wealth effect belief expressed

**Data**:
- `stock_market_wealth_classifications.pkl` available
- Covers Growth, Employment, Stock Market, Credit Markets variables

**To implement**:
1. Create `wealth_effects_sampler.py`
2. Update `coding_interface.py` or create separate interface
3. Adapt `validation_analysis.py` for wealth effect categories

---

## Quick Reference

### Run Coding Interface
```bash
cd /home/ben/projects/llm_humancode_web
streamlit run coding_interface.py
```

### Generate New Sample
```bash
python phillips_sampler.py
```

### Run Validation Analysis
```bash
python -c "from validation_analysis import run_validation; run_validation()"
```

### Required Packages
```
streamlit
pandas
numpy
scipy
scikit-learn
matplotlib
seaborn
```

---

## Related Projects

### Original FOMC Argument Coding Framework
Location: `/home/ben/llm_humancode/`

This project validated Claude's argument classifications (scores -3 to +3, argument categories, data categories). The current project adapts that framework for model parameter classifications.

Key differences:
- Original: Continuous scores + multiple categorical dimensions
- Current: Single categorical classification (steep/flat/moderate/none)
