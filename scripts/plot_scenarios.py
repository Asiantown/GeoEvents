#!/usr/bin/env python3
"""Plot scenario summary metrics with a clean financial-report style."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", required=True, help="Scenario summary CSV (from run_scenarios.py)")
    parser.add_argument("--output", required=True, help="Output PNG path")
    parser.add_argument("--title", default="Scenario Comparison", help="Figure title")
    parser.add_argument(
        "--subtitle",
        default="Patrol coverage and resource utilization",
        help="Figure subtitle",
    )
    return parser.parse_args()


def load_summary(path: str):
    with open(path, "r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    if not rows:
        raise ValueError("Summary CSV is empty")
    return rows


def plot(rows, output_path: str, title: str, subtitle: str) -> None:
    scenarios = [row["scenario"] for row in rows]
    coverage = [float(row["risk_coverage_ratio"]) * 100 for row in rows]
    total_weight = [float(row["total_weight"]) for row in rows]
    avg_util = [float(row["avg_utilization"]) * 100 for row in rows]
    max_util = [float(row["max_utilization"]) * 100 for row in rows]

    accent = "#0F62FE"
    neutral = "#4D5358"
    canvas_bg = "#FFFFFF"

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Risk Coverage", "Utilization & Weight"),
        specs=[[{"type": "bar"}, {"secondary_y": True}]],
        horizontal_spacing=0.12,
    )

    fig.add_trace(
        go.Bar(
            x=scenarios,
            y=coverage,
            marker_color=accent,
            opacity=0.9,
            hovertemplate="Scenario: %{x}<br>Coverage: %{y:.1f}%<extra></extra>",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            x=scenarios,
            y=avg_util,
            name="Avg Util (%)",
            marker_color=accent,
            opacity=0.35,
            hovertemplate="Avg Util: %{y:.1f}%<extra></extra>",
        ),
        row=1,
        col=2,
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=scenarios,
            y=max_util,
            name="Max Util (%)",
            mode="lines+markers",
            line=dict(color=neutral, width=2),
            marker=dict(size=8, symbol="circle"),
            hovertemplate="Max Util: %{y:.1f}%<extra></extra>",
        ),
        row=1,
        col=2,
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=scenarios,
            y=total_weight,
            name="Total Weight",
            mode="lines+markers",
            line=dict(color="#8C9BA5", width=2, dash="dot"),
            marker=dict(size=8, symbol="square"),
            hovertemplate="Total Weight: %{y:.0f}<extra></extra>",
        ),
        row=1,
        col=2,
        secondary_y=True,
    )

    fig.update_layout(
        width=1200,
        height=700,
        plot_bgcolor=canvas_bg,
        paper_bgcolor=canvas_bg,
        font=dict(family="Helvetica, Arial, sans-serif", size=14, color="#1A1F36"),
        margin=dict(l=60, r=60, t=110, b=90),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
        title=dict(
            text=f"{title}<br><span style='font-size:16px;color:#4D5358;'>{subtitle}</span>",
            x=0,
            xanchor="left",
            yanchor="top",
        ),
    )

    fig.update_yaxes(
        title_text="Coverage (%)",
        gridcolor="#E0E3E8",
        zeroline=False,
        row=1,
        col=1,
    )
    fig.update_xaxes(showline=False, showgrid=False, row=1, col=1)

    fig.update_yaxes(
        title_text="Utilization (%)",
        gridcolor="#E0E3E8",
        zeroline=False,
        row=1,
        col=2,
        secondary_y=False,
    )
    fig.update_yaxes(
        title_text="Total Weight",
        gridcolor="#FFFFFF",
        showgrid=False,
        zeroline=False,
        row=1,
        col=2,
        secondary_y=True,
    )
    fig.update_xaxes(showline=False, showgrid=False, row=1, col=2)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.write_image(output_path, scale=1)


def main() -> None:
    args = parse_args()
    rows = load_summary(args.summary)
    plot(rows, args.output, args.title, args.subtitle)


if __name__ == "__main__":
    main()
