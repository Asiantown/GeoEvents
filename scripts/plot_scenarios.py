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
    plt.style.use("seaborn-v0_8-whitegrid")
    scenarios = [row["scenario"] for row in rows]
    coverage = [float(row["risk_coverage_ratio"]) * 100 for row in rows]
    total_weight = [float(row["total_weight"]) for row in rows]
    avg_util = [float(row["avg_utilization"]) * 100 for row in rows]
    max_util = [float(row["max_utilization"]) * 100 for row in rows]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharex=True)

    # Panel A: risk coverage
    bar_colors = ["#1b9e77", "#d95f02", "#7570b3"]
    axes[0].bar(scenarios, coverage, color=bar_colors[: len(scenarios)])
    axes[0].set_ylabel("Risk Coverage (%)")
    axes[0].set_ylim(0, max(coverage + [50]) + 20)
    axes[0].set_title("Scenario Risk Coverage")
    for idx, val in enumerate(coverage):
        axes[0].text(idx, val + 2, f"{val:.0f}%", ha="center", va="bottom", fontsize=9)

    # Panel B: utilization vs. total weight
    axes[1].bar(scenarios, avg_util, color="#4c78a8", alpha=0.8, label="Avg Util (%)")
    axes[1].plot(scenarios, max_util, color="#f58518", marker="o", label="Max Util (%)")
    ax2 = axes[1].twinx()
    ax2.plot(scenarios, total_weight, color="#54a24b", marker="s", linestyle="--", label="Total Weight")
    axes[1].set_ylabel("Utilization (%)")
    ax2.set_ylabel("Total Weight")
    axes[1].set_title("Resource Utilization")

    # Combined legend
    lines, labels = axes[1].get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    axes[1].legend(lines + lines2, labels + labels2, loc="upper left", fontsize=9)

    fig.suptitle("Scenario Comparison", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.subplots_adjust(top=0.88)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=250)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    rows = load_summary(args.summary)
    plot(rows, args.output)


if __name__ == "__main__":
    main()
