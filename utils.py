"""
Utility functions for the Cart2Insights project.
Schema-agnostic — works on whatever CSVs get dropped into data/raw/.
"""

import os
import pandas as pd


def load_all_csvs(data_dir="data/raw/"):
    """Load every CSV in a directory into a dict of DataFrames keyed by filename."""
    dfs = {}
    for f in sorted(os.listdir(data_dir)):
        if f.endswith(".csv"):
            name = f.replace(".csv", "")
            dfs[name] = pd.read_csv(os.path.join(data_dir, f))
    return dfs


def inspect_table(df: pd.DataFrame, name: str = "table"):
    """Print a quick data-quality snapshot for one table."""
    print(f"\n{'=' * 60}\n{name}\n{'=' * 60}")
    print(f"Shape: {df.shape}")
    print(f"\nDtypes:\n{df.dtypes}")
    print(f"\nMissing values:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
    print(f"\nDuplicate rows: {df.duplicated().sum()}")
    print(f"\nSample:\n{df.head(3)}")


def inspect_all(dfs: dict):
    """Run inspect_table on every DataFrame in a dict."""
    for name, df in dfs.items():
        inspect_table(df, name)


def check_pk_uniqueness(df: pd.DataFrame, pk_col: str, table_name: str = "table"):
    """Verify a candidate primary key column is actually unique and non-null."""
    n_total = len(df)
    n_unique = df[pk_col].nunique()
    n_null = df[pk_col].isnull().sum()
    is_valid_pk = (n_unique == n_total) and (n_null == 0)
    print(
        f"[{table_name}] PK candidate '{pk_col}': "
        f"{n_unique}/{n_total} unique, {n_null} nulls -> "
        f"{'VALID PK' if is_valid_pk else 'NOT a valid PK'}"
    )
    return is_valid_pk
