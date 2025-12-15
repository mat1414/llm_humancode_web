# save as: phillips_sampler.py

"""
Phillips Curve Classification Sampler
======================================
Creates stratified random samples of FOMC arguments for human validation
of Claude's Phillips curve slope classifications.

Sampling Strategy:
- Target ~50 arguments per classification category (steep, flat, moderate, null)
- Total sample: ~200 arguments
- Stratified to ensure representation across all categories
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime


class PhillipsSampler:
    """
    Creates stratified samples for Phillips curve classification validation.
    """

    def __init__(self, arguments_path='original_scripts/all_arguments.pkl',
                 classifications_path='original_scripts/phillips_classifications.pkl',
                 seed=42):
        """
        Initialize sampler with data files.

        Parameters:
        -----------
        arguments_path : str
            Path to all_arguments.pkl
        classifications_path : str
            Path to phillips_classifications.pkl
        seed : int
            Random seed for reproducibility
        """
        self.seed = seed
        np.random.seed(seed)

        # Load arguments
        self.args = pd.read_pickle(arguments_path)

        # Filter to Phillips curve relevant variables
        self.args = self.args[self.args['variable'].isin(['Growth', 'Inflation', 'Employment'])].copy()

        # Load and merge classifications
        pc = pd.read_pickle(classifications_path)
        self.args['claude_pc_slope'] = pc
        self.args['claude_pc_category'] = self.args['claude_pc_slope'].map({
            1.0: 'steep',
            -1.0: 'flat',
            0.0: 'moderate'
        }).fillna('none')  # Use 'none' instead of 'null' to avoid CSV parsing issues

        # Store original index
        self.args['original_index'] = self.args.index

        # Clean data - remove very short quotations
        self.args = self.args[self.args['quotation'].str.len() >= 10]

        print(f"Loaded {len(self.args)} valid arguments")
        print(f"\nClaude classification distribution:")
        print(self.args['claude_pc_category'].value_counts())

    def sample_stratified(self, n_per_category=50):
        """
        Create stratified sample with equal representation per category.

        Parameters:
        -----------
        n_per_category : int
            Number of arguments to sample per classification category

        Returns:
        --------
        pd.DataFrame : Sampled arguments
        dict : Summary statistics
        """
        print(f"\n{'='*60}")
        print(f"Stratified Sampling: {n_per_category} per category")
        print(f"{'='*60}")

        samples = []
        categories = ['steep', 'flat', 'moderate', 'none']

        for cat in categories:
            cat_args = self.args[self.args['claude_pc_category'] == cat]
            n_available = len(cat_args)
            n_sample = min(n_per_category, n_available)

            sampled = cat_args.sample(n=n_sample, random_state=self.seed)
            samples.append(sampled)

            print(f"  {cat.upper()}: sampled {n_sample} / {n_available} available")

        # Combine and shuffle
        sample_df = pd.concat(samples, ignore_index=True)
        sample_df = sample_df.sample(frac=1, random_state=self.seed + 1000).reset_index(drop=True)

        # Calculate statistics
        stats = {
            'total_sampled': len(sample_df),
            'n_per_category': n_per_category,
            'category_distribution': sample_df['claude_pc_category'].value_counts().to_dict(),
            'variable_distribution': sample_df['variable'].value_counts().to_dict(),
            'timestamp': datetime.now().isoformat(),
            'seed': self.seed
        }

        print(f"\nTotal sampled: {len(sample_df)} arguments")
        print(f"\nBy economic variable:")
        print(sample_df['variable'].value_counts())

        return sample_df, stats

    def create_coding_files(self, sample_df, output_dir='validation_samples/production'):
        """
        Create files for human coding.

        Creates:
        - coding_phillips.csv: What human coders see (no Claude classifications)
        - key_phillips.csv: Validation key with Claude's classifications (hidden)
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Create coding IDs
        coding_ids = [f'PC_{str(i).zfill(4)}' for i in range(len(sample_df))]

        # === CODING FILE (for human coders - NO Claude classifications) ===
        coding_df = pd.DataFrame({
            'coding_id': coding_ids,
            'quotation': sample_df['quotation'].values,
            'description': sample_df['description'].values,
            'explanation': sample_df['explanation'].values,
            'variable': sample_df['variable'].values,
        })

        coding_file = output_path / 'coding_phillips.csv'
        coding_df.to_csv(coding_file, index=False)

        # === VALIDATION KEY (includes Claude classifications - hidden from coders) ===
        key_df = pd.DataFrame({
            'coding_id': coding_ids,
            'original_index': sample_df['original_index'].values,
            'quotation': sample_df['quotation'].values,
            'description': sample_df['description'].values,
            'explanation': sample_df['explanation'].values,
            'variable': sample_df['variable'].values,
            'stablespeaker': sample_df['stablespeaker'].values,
            'ymd': sample_df['ymd'].values,
            'claude_pc_slope': sample_df['claude_pc_slope'].values,
            'claude_pc_category': sample_df['claude_pc_category'].values,
        })

        key_file = output_path / 'key_phillips.csv'
        key_df.to_csv(key_file, index=False)

        # === STATISTICS FILE ===
        stats = {
            'n_arguments': len(sample_df),
            'category_distribution': sample_df['claude_pc_category'].value_counts().to_dict(),
            'variable_distribution': sample_df['variable'].value_counts().to_dict(),
            'created_at': datetime.now().isoformat(),
            'seed': self.seed
        }

        stats_file = output_path / 'stats_phillips.json'
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"\nFiles created:")
        print(f"  Coding file (for coders): {coding_file}")
        print(f"  Validation key (hidden):  {key_file}")
        print(f"  Statistics: {stats_file}")

        return coding_file, key_file, stats_file


def main():
    """Run the sampling process."""
    # Initialize sampler
    sampler = PhillipsSampler(
        arguments_path='original_scripts/all_arguments.pkl',
        classifications_path='original_scripts/phillips_classifications.pkl',
        seed=42
    )

    # Create stratified sample
    sample_df, stats = sampler.sample_stratified(n_per_category=50)

    # Create coding files
    sampler.create_coding_files(sample_df)

    print("\n" + "="*60)
    print("SAMPLING COMPLETE")
    print("="*60)
    print("\nCoding file ready at: validation_samples/production/coding_phillips.csv")
    print("Give this file to human coders (Claude's classifications are hidden)")


if __name__ == "__main__":
    main()
