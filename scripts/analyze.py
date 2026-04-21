"""
analyze.py -- Extract plot-ready dataframe from DMA database and run statistical tests.

Outputs:
    build/dma_dataframe.csv   -- tidy dataframe ready for plotting
    build/stats_results.txt   -- statistical test results

Usage:
    python scripts/analyze.py build/dma.db build/
"""

import sys
import os
import sqlite3
import pandas as pd
import numpy as np
from scipy import stats
from scipy.signal import argrelmax


def load_dataframe(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(
        """
        SELECT sample, axis, temperature, frequency,
               storage_modulus, loss_modulus, tan_delta
        FROM dma_measurements
        ORDER BY sample, axis, temperature
        """,
        conn,
    )
    conn.close()
    return df


def find_tg(df, sample, axis):
    """Glass transition temperature = temperature at peak tan_delta."""
    sub = df[(df["sample"] == sample) & (df["axis"] == axis)].dropna(subset=["tan_delta"])
    if sub.empty:
        return np.nan
    idx = sub["tan_delta"].idxmax()
    return sub.loc[idx, "temperature"]


def run_ttest(df, column, label):
    a = df[df["sample"] == "product_board"][column].dropna()
    b = df[df["sample"] == "solder_board"][column].dropna()
    t, p = stats.ttest_ind(a, b, equal_var=False)
    lines = [
        f"\nIndependent t-test: {label}",
        f"  product_board  n={len(a):4d}  mean={a.mean():.4f}  std={a.std():.4f}",
        f"  solder_board   n={len(b):4d}  mean={b.mean():.4f}  std={b.std():.4f}",
        f"  t={t:.4f}  p={p:.4e}  {'*significant*' if p < 0.05 else 'not significant'} (alpha=0.05)",
    ]
    return "\n".join(lines)


def run_anova_axes(df, column, label):
    groups = [df[df["axis"] == ax][column].dropna() for ax in ["x", "y", "z"]]
    f, p = stats.f_oneway(*groups)
    lines = [
        f"\nOne-way ANOVA across axes: {label}",
        f"  F={f:.4f}  p={p:.4e}  {'*significant*' if p < 0.05 else 'not significant'} (alpha=0.05)",
    ]
    return "\n".join(lines)


def main(db_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    print(f"Loading data from: {db_path}")
    df = load_dataframe(db_path)
    print(f"  Total rows: {len(df)}")

    # Save tidy plot-ready dataframe
    csv_path = os.path.join(out_dir, "dma_dataframe.csv")
    df.to_csv(csv_path, index=False)
    print(f"  Dataframe saved: {csv_path}")
    print(f"\n  Columns: {list(df.columns)}")
    print(f"  Samples: {df['sample'].unique().tolist()}")
    print(f"  Axes:    {df['axis'].unique().tolist()}")
    print(f"\n  Head:\n{df.head(3).to_string(index=False)}")

    # Statistical tests
    results = ["=" * 60, "DMA Statistical Analysis Results", "=" * 60]

    results.append(run_ttest(df, "storage_modulus", "Storage Modulus (Pa)"))
    results.append(run_ttest(df, "loss_modulus",    "Loss Modulus (Pa)"))
    results.append(run_ttest(df, "tan_delta",       "Tan Delta"))

    results.append(run_anova_axes(df, "storage_modulus", "Storage Modulus (Pa)"))
    results.append(run_anova_axes(df, "tan_delta",       "Tan Delta"))

    # Tg per sample/axis
    results.append("\nGlass Transition Temperature (Tg) -- peak tan_delta:")
    for sample in ["product_board", "solder_board"]:
        for axis in ["x", "y", "z"]:
            tg = find_tg(df, sample, axis)
            results.append(f"  {sample:15s}  {axis}-axis  Tg = {tg:.1f} °C" if not np.isnan(tg) else f"  {sample:15s}  {axis}-axis  Tg = N/A")

    results.append("\n" + "=" * 60)
    report = "\n".join(results)

    stats_path = os.path.join(out_dir, "stats_results.txt")
    with open(stats_path, "w") as f:
        f.write(report)

    print("\n" + report)
    print(f"\nStats saved: {stats_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scripts/analyze.py <db_path> <out_dir>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
