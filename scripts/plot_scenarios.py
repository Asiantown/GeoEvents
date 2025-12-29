#!/usr/bin/env python3
"""Plot scenario summary metrics."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", required=True, help="Scenario summary CSV (from run_scenarios.py)")
    parser.add_argument("--output", required=True, help="Output PNG path")
    return parser.parse_args()


def load_summary(path: str):
    with open(path, "r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    if not rows:
        raise ValueError("Summary CSV is empty")
    return rows


def plot(rows, output_path: str) -> None:
    scenarios = [row["scenario"] for row in rows]
    coverage = [float(row["risk_coverage_ratio"]) * 100 for row in rows]
    total_weight = [float(row["total_weight"]) for row in rows]
    avg_util = [float(row["avg_utilization"]) * 100 for row in rows]

    fig, axes = plt.subplots(2, 1, figsize=(8, 8))

    axes[0].bar(scenarios, coverage, color="#1f77b4")
    axes[0].set_ylabel("Risk Coverage (%)")
    axes[0].set_ylim(0, 110)
    axes[0].set_title("Scenario Coverage vs. Risk Scaling")
    axes[0].grid(axis="y", alpha=0.3)

    axes[1].plot(scenarios, total_weight, marker="o", label="Total Weight", color="#ff7f0e")
    axes[1].bar(scenarios, avg_util, alpha=0.4, label="Avg Util (%)", color="#2ca02c")
    axes[1].set_ylabel("Weight / Utilization")
    axes[1].set_title("Resource Usage Across Scenarios")
    axes[1].grid(axis="y", alpha=0.3)
    axes[1].legend()

    fig.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    rows = load_summary(args.summary)
    plot(rows, args.output)


if __name__ == "__main__":
    main()
