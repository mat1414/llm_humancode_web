# save as: parameter_sampler.py

"""
Parameter Sampler
=================
Creates structured random samples of model parameter estimates for human validation
following Mullainathan et al. (2024) framework.

This script is adapted from the FOMC argument sampler to support sampling of
LLM-estimated econometric model parameters (e.g., Phillips curve slope, stock
market wealth effects).

Key differences from argument sampling:
- Samples are parameter estimates, not text arguments
- Stratification may be by time period, model specification, etc.
- Output files contain parameter estimates and context for human coding
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime

class ParameterSampler:
    """
    Creates structured random samples of model parameters for human validation
    following Mullainathan et al. (2024) framework
    """

    def __init__(self, data_path, seed=42):
        """
        Initialize sampler with data and random seed for reproducibility

        Parameters:
        -----------
        data_path : str
            Path to the data file containing LLM parameter estimates
        seed : int
            Random seed for reproducibility
        """
        self.seed = seed
        np.random.seed(seed)

        # Load data - support both pickle and CSV
        if data_path.endswith('.pkl'):
            self.df = pd.read_pickle(data_path)
        elif data_path.endswith('.csv'):
            self.df = pd.read_csv(data_path)
        else:
            raise ValueError(f"Unsupported file format: {data_path}")

        # Add unique key if it doesn't exist
        if 'parameter_id' not in self.df.columns:
            print("Adding unique parameter_id column...")
            self.df['parameter_id'] = ['PARAM_' + str(i).zfill(8) for i in range(len(self.df))]

        # Store original index for tracking
        self.df['original_index'] = self.df.index

        print(f"Loaded {len(self.df)} parameter estimates from {data_path}")

    def clean_data(self, df, parameter_type=None):
        """
        Clean data for a specific parameter type

        Parameters:
        -----------
        df : pd.DataFrame
            Input dataframe
        parameter_type : str, optional
            If provided, filter to specific parameter type
        """
        df_clean = df.copy()

        # Filter by parameter type if specified
        if parameter_type and 'parameter_type' in df_clean.columns:
            df_clean = df_clean[df_clean['parameter_type'] == parameter_type]

        # Remove rows with missing estimates
        estimate_cols = [col for col in df_clean.columns if 'estimate' in col.lower() or 'value' in col.lower()]
        if estimate_cols:
            df_clean = df_clean.dropna(subset=estimate_cols)

        return df_clean

    def sample_parameters(self, parameter_type=None, target_n=100, stratify_by=None):
        """
        Create structured sample for validation

        Parameters:
        -----------
        parameter_type : str, optional
            Type of parameter to sample
        target_n : int
            Target number of parameters to sample
        stratify_by : str or list, optional
            Column(s) to stratify sampling by (e.g., 'year', 'specification')
        """

        print(f"\n{'='*60}")
        print(f"Sampling parameters" + (f" for {parameter_type}" if parameter_type else ""))
        print(f"{'='*60}")

        # Clean data
        df_clean = self.clean_data(self.df, parameter_type)
        print(f"Total valid parameter estimates: {len(df_clean)}")

        if len(df_clean) == 0:
            print("WARNING: No valid parameters found!")
            return None, None

        # Sample based on stratification
        if stratify_by:
            sample_df = self._stratified_sample(df_clean, target_n, stratify_by)
        else:
            # Simple random sample
            n_sample = min(target_n, len(df_clean))
            sample_df = df_clean.sample(n=n_sample, random_state=self.seed)

        # Calculate summary statistics
        summary_stats = self.calculate_summary_stats(sample_df)

        print(f"\nFinal sample size: {len(sample_df)} parameters")

        return sample_df, summary_stats

    def _stratified_sample(self, df, target_n, stratify_by):
        """
        Perform stratified sampling
        """
        if isinstance(stratify_by, str):
            stratify_by = [stratify_by]

        # Group and sample proportionally
        grouped = df.groupby(stratify_by)
        n_groups = len(grouped)
        n_per_group = max(1, target_n // n_groups)

        samples = []
        for name, group in grouped:
            n_sample = min(n_per_group, len(group))
            samples.append(group.sample(n=n_sample, random_state=self.seed))

        return pd.concat(samples, ignore_index=True)

    def calculate_summary_stats(self, sample_df):
        """
        Calculate summary statistics for the sample
        """
        stats = {
            'n_parameters': len(sample_df),
            'timestamp': datetime.now().isoformat()
        }

        # Numeric columns statistics
        numeric_cols = sample_df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if 'estimate' in col.lower() or 'value' in col.lower():
                stats[f'{col}_mean'] = sample_df[col].mean()
                stats[f'{col}_std'] = sample_df[col].std()
                stats[f'{col}_min'] = sample_df[col].min()
                stats[f'{col}_max'] = sample_df[col].max()

        return stats

    def create_coding_files(self, sample_df, parameter_type, output_dir='validation_samples/production',
                           context_columns=None, llm_estimate_column='llm_estimate'):
        """
        Create files for human coding

        Parameters:
        -----------
        sample_df : pd.DataFrame
            Sampled parameters
        parameter_type : str
            Type of parameter (for file naming)
        output_dir : str
            Output directory
        context_columns : list, optional
            Columns to include as context for human coders
        llm_estimate_column : str
            Column name containing LLM estimates
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Shuffle for coding
        sample_shuffled = sample_df.sample(frac=1, random_state=self.seed+1000).reset_index(drop=True)

        # Create coding IDs
        coding_ids = [f'CODE_{parameter_type}_{str(i).zfill(4)}' for i in range(len(sample_shuffled))]

        # Prepare coding file (what human coders see)
        coding_data = {'coding_id': coding_ids}

        # Add context columns if specified
        if context_columns:
            for col in context_columns:
                if col in sample_shuffled.columns:
                    coding_data[col] = sample_shuffled[col].values

        coding_df = pd.DataFrame(coding_data)
        coding_file = output_path / f'coding_{parameter_type.lower()}.csv'
        coding_df.to_csv(coding_file, index=False)

        # Create validation key (includes LLM estimates - hidden from coders)
        key_data = {
            'coding_id': coding_ids,
            'parameter_id': sample_shuffled['parameter_id'].values if 'parameter_id' in sample_shuffled.columns else None,
            'original_index': sample_shuffled['original_index'].values if 'original_index' in sample_shuffled.columns else None,
        }

        # Add all columns from sample
        for col in sample_shuffled.columns:
            if col not in ['parameter_id', 'original_index']:
                key_data[col] = sample_shuffled[col].values

        key_df = pd.DataFrame(key_data)
        key_file = output_path / f'key_{parameter_type.lower()}.csv'
        key_df.to_csv(key_file, index=False)

        # Save summary statistics
        stats = self.calculate_summary_stats(sample_shuffled)
        stats_file = output_path / f'stats_{parameter_type.lower()}.json'
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2, default=str)

        print(f"\nFiles created:")
        print(f"  Coding file: {coding_file}")
        print(f"  Validation key: {key_file}")
        print(f"  Statistics: {stats_file}")

        return coding_file, key_file, stats_file


# Usage example
if __name__ == "__main__":
    print("Parameter Sampler ready - configure for your specific parameter data!")
    print("\nExample usage:")
    print("  sampler = ParameterSampler('llm_estimates.csv', seed=42)")
    print("  sample_df, stats = sampler.sample_parameters('phillips_curve', target_n=100)")
    print("  sampler.create_coding_files(sample_df, 'phillips_curve')")
