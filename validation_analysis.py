# save as: validation_analysis.py

"""
Phillips Curve Validation Analysis
===================================
Analyzes human coding results and compares with Claude's classifications
following Mullainathan et al. (2024) validation framework.

For categorical classifications (steep/flat/moderate/null), we use:
- Cohen's kappa for inter-rater agreement
- Confusion matrices
- Category-wise accuracy
- Weighted kappa for ordinal data (since steep > moderate > flat is ordinal)
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import glob
from sklearn.metrics import (
    cohen_kappa_score,
    confusion_matrix,
    classification_report,
    accuracy_score
)
import matplotlib.pyplot as plt
import seaborn as sns


class PhillipsValidationAnalyzer:
    """
    Analyzes human validation results for Phillips curve classifications.
    """

    def __init__(self):
        self.categories = ['steep', 'flat', 'moderate', 'none']
        # Numeric mapping for ordinal analysis
        self.category_to_numeric = {
            'steep': 1,
            'moderate': 0,
            'flat': -1,
            'none': np.nan
        }

    def load_human_coding(self, pattern='validation_samples/coded/coded_*_phillips_*.csv'):
        """
        Load all human coding files for Phillips curve.
        """
        files = glob.glob(pattern)

        if not files:
            raise FileNotFoundError(f"No coding files found matching {pattern}")

        dfs = []
        for file in files:
            df = pd.read_csv(file)
            print(f"Loaded {len(df)} codings from {file}")
            dfs.append(df)

        all_codings = pd.concat(dfs, ignore_index=True)

        coders = all_codings['coder_name'].unique()
        print(f"\nFound {len(coders)} coders: {', '.join(coders)}")

        return all_codings

    def merge_with_claude(self, human_df, key_file='validation_samples/production/key_phillips.csv'):
        """
        Merge human codings with Claude's classifications.
        """
        key_df = pd.read_csv(key_file)

        merged = human_df.merge(
            key_df[['coding_id', 'claude_pc_category', 'claude_pc_slope',
                    'variable', 'stablespeaker', 'ymd']],
            on='coding_id',
            how='left'
        )

        return merged

    def calculate_agreement_metrics(self, merged_df, human_col='classification', claude_col='claude_pc_category'):
        """
        Calculate agreement metrics between human and Claude classifications.
        """
        # Remove rows where either classification is missing
        valid = merged_df.dropna(subset=[human_col, claude_col])

        human_cats = valid[human_col].values
        claude_cats = valid[claude_col].values

        n = len(valid)
        print(f"\nAgreement metrics based on {n} arguments")

        # Basic accuracy
        accuracy = accuracy_score(claude_cats, human_cats)

        # Cohen's kappa (unweighted)
        kappa = cohen_kappa_score(claude_cats, human_cats)

        # For non-none categories, calculate weighted kappa (ordinal)
        non_null_mask = (valid[human_col] != 'none') & (valid[claude_col] != 'none')
        if non_null_mask.sum() > 0:
            non_null = valid[non_null_mask]
            # Map to ordinal for weighted kappa
            human_ordinal = non_null[human_col].map({'flat': -1, 'moderate': 0, 'steep': 1})
            claude_ordinal = non_null[claude_col].map({'flat': -1, 'moderate': 0, 'steep': 1})
            weighted_kappa = cohen_kappa_score(claude_ordinal, human_ordinal, weights='linear')
        else:
            weighted_kappa = np.nan

        print(f"\n=== AGREEMENT METRICS ===")
        print(f"Accuracy: {accuracy:.3f} ({accuracy*100:.1f}%)")
        print(f"Cohen's kappa (unweighted): {kappa:.3f}")
        print(f"Cohen's kappa (weighted, non-null only): {weighted_kappa:.3f}")

        # Interpretation
        print(f"\nKappa Interpretation:")
        if kappa < 0:
            print("  Less than chance agreement")
        elif kappa < 0.20:
            print("  Slight agreement")
        elif kappa < 0.40:
            print("  Fair agreement")
        elif kappa < 0.60:
            print("  Moderate agreement")
        elif kappa < 0.80:
            print("  Substantial agreement")
        else:
            print("  Almost perfect agreement")

        return {
            'n': n,
            'accuracy': accuracy,
            'kappa': kappa,
            'weighted_kappa': weighted_kappa
        }

    def calculate_confusion_matrix(self, merged_df, human_col='classification', claude_col='claude_pc_category'):
        """
        Calculate and display confusion matrix.
        """
        valid = merged_df.dropna(subset=[human_col, claude_col])

        # Confusion matrix
        labels = ['steep', 'moderate', 'flat', 'none']
        cm = confusion_matrix(valid[claude_col], valid[human_col], labels=labels)

        print(f"\n=== CONFUSION MATRIX ===")
        print("(Rows: Claude, Columns: Human)")
        print()

        # Pretty print
        header = "          " + "  ".join([f"{l:>8}" for l in labels])
        print(header)
        print("-" * len(header))

        for i, label in enumerate(labels):
            row_str = f"{label:>8}  " + "  ".join([f"{cm[i,j]:>8}" for j in range(len(labels))])
            print(row_str)

        # Per-category metrics
        print(f"\n=== PER-CATEGORY METRICS ===")
        report = classification_report(valid[claude_col], valid[human_col],
                                      labels=labels, output_dict=True, zero_division=0)

        for label in labels:
            if label in report:
                metrics = report[label]
                print(f"\n{label.upper()}:")
                print(f"  Precision: {metrics['precision']:.3f}")
                print(f"  Recall: {metrics['recall']:.3f}")
                print(f"  F1-score: {metrics['f1-score']:.3f}")
                print(f"  Support: {metrics['support']}")

        return cm, report

    def calculate_inter_rater_reliability(self, codings_df):
        """
        Calculate inter-rater reliability if multiple coders coded same arguments.
        """
        multi_coded = codings_df.groupby('coding_id').filter(lambda x: len(x) > 1)

        if len(multi_coded) == 0:
            print("\nNo arguments coded by multiple coders")
            return None

        n_multi = multi_coded['coding_id'].nunique()
        print(f"\nInter-rater reliability based on {n_multi} multi-coded arguments")

        results = {}
        coders = multi_coded['coder_name'].unique()

        for i in range(len(coders)):
            for j in range(i+1, len(coders)):
                coder1, coder2 = coders[i], coders[j]

                coder1_df = multi_coded[multi_coded['coder_name'] == coder1].set_index('coding_id')
                coder2_df = multi_coded[multi_coded['coder_name'] == coder2].set_index('coding_id')

                overlap_ids = coder1_df.index.intersection(coder2_df.index)

                if len(overlap_ids) > 0:
                    cats1 = coder1_df.loc[overlap_ids, 'classification']
                    cats2 = coder2_df.loc[overlap_ids, 'classification']

                    kappa = cohen_kappa_score(cats1, cats2)
                    accuracy = accuracy_score(cats1, cats2)

                    results[f"{coder1}-{coder2}"] = {
                        'n_overlap': len(overlap_ids),
                        'kappa': kappa,
                        'accuracy': accuracy
                    }

                    print(f"\n{coder1} vs {coder2} ({len(overlap_ids)} arguments):")
                    print(f"  Cohen's kappa: {kappa:.3f}")
                    print(f"  Accuracy: {accuracy:.3f}")

        return results

    def analyze_disagreements(self, merged_df, human_col='classification', claude_col='claude_pc_category'):
        """
        Analyze patterns in disagreements between human and Claude.
        """
        valid = merged_df.dropna(subset=[human_col, claude_col])
        disagreements = valid[valid[human_col] != valid[claude_col]]

        print(f"\n=== DISAGREEMENT ANALYSIS ===")
        print(f"Total disagreements: {len(disagreements)} / {len(valid)} ({100*len(disagreements)/len(valid):.1f}%)")

        if len(disagreements) == 0:
            return None

        # Most common disagreement patterns
        print(f"\nMost common disagreement patterns:")
        patterns = disagreements.groupby([claude_col, human_col]).size().sort_values(ascending=False)
        for (claude_cat, human_cat), count in patterns.head(10).items():
            print(f"  Claude: {claude_cat} -> Human: {human_cat}: {count}")

        # Disagreements by variable
        if 'variable' in disagreements.columns:
            print(f"\nDisagreements by economic variable:")
            for var in disagreements['variable'].unique():
                var_disagree = disagreements[disagreements['variable'] == var]
                var_total = valid[valid['variable'] == var]
                pct = 100 * len(var_disagree) / len(var_total) if len(var_total) > 0 else 0
                print(f"  {var}: {len(var_disagree)} ({pct:.1f}%)")

        return disagreements

    def plot_confusion_matrix(self, merged_df, human_col='classification', claude_col='claude_pc_category',
                             output_file='confusion_matrix_phillips.png'):
        """
        Create visualization of confusion matrix.
        """
        valid = merged_df.dropna(subset=[human_col, claude_col])
        labels = ['steep', 'moderate', 'flat', 'none']
        cm = confusion_matrix(valid[claude_col], valid[human_col], labels=labels)

        # Normalize by row (Claude's predictions)
        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        cm_normalized = np.nan_to_num(cm_normalized)

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Raw counts
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=labels, yticklabels=labels, ax=axes[0])
        axes[0].set_xlabel('Human Classification')
        axes[0].set_ylabel('Claude Classification')
        axes[0].set_title('Confusion Matrix (Counts)')

        # Normalized
        sns.heatmap(cm_normalized, annot=True, fmt='.2f', cmap='Blues',
                   xticklabels=labels, yticklabels=labels, ax=axes[1])
        axes[1].set_xlabel('Human Classification')
        axes[1].set_ylabel('Claude Classification')
        axes[1].set_title('Confusion Matrix (Normalized by Row)')

        plt.tight_layout()
        plt.savefig(output_file, dpi=150)
        plt.close()

        print(f"\nConfusion matrix saved to {output_file}")

    def generate_report(self, merged_df, human_col='classification', claude_col='claude_pc_category'):
        """
        Generate comprehensive validation report.
        """
        agreement = self.calculate_agreement_metrics(merged_df, human_col, claude_col)
        cm, report = self.calculate_confusion_matrix(merged_df, human_col, claude_col)
        disagreements = self.analyze_disagreements(merged_df, human_col, claude_col)

        # Summary
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)

        print(f"""
Phillips Curve Classification Validation
-----------------------------------------
Sample size: {agreement['n']}
Overall accuracy: {agreement['accuracy']:.1%}
Cohen's kappa: {agreement['kappa']:.3f}
Weighted kappa (ordinal, non-null): {agreement['weighted_kappa']:.3f}

Interpretation:
- Kappa > 0.80: Almost perfect agreement
- Kappa 0.60-0.80: Substantial agreement
- Kappa 0.40-0.60: Moderate agreement
- Kappa 0.20-0.40: Fair agreement
- Kappa < 0.20: Slight agreement
""")

        return {
            'agreement': agreement,
            'confusion_matrix': cm,
            'classification_report': report,
            'n_disagreements': len(disagreements) if disagreements is not None else 0
        }


def run_validation(human_pattern='validation_samples/coded/coded_*_phillips_*.csv',
                   key_file='validation_samples/production/key_phillips.csv'):
    """
    Run complete validation analysis.
    """
    analyzer = PhillipsValidationAnalyzer()

    # Load data
    human_df = analyzer.load_human_coding(human_pattern)
    merged = analyzer.merge_with_claude(human_df, key_file)

    # Calculate inter-rater reliability if multiple coders
    analyzer.calculate_inter_rater_reliability(human_df)

    # Generate report
    results = analyzer.generate_report(merged)

    # Create visualization
    analyzer.plot_confusion_matrix(merged)

    return results


if __name__ == "__main__":
    print("Phillips Curve Validation Analysis")
    print("="*60)
    print("\nTo run validation after coding is complete:")
    print("  python validation_analysis.py")
    print("\nOr import and use:")
    print("  from validation_analysis import run_validation")
    print("  results = run_validation()")
