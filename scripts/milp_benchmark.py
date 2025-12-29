#!/usr/bin/env python3
"""Solve a simplified patrol allocation MILP for benchmarking."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import List

import pulp

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.patrol_heuristic import PatrolBoat, assign_boats
from src.stationary_events import StationaryEvent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", required=True, help="Stationary events CSV")
    parser.add_argument("--boats", required=True, help="Boat config JSON")
    parser.add_argument("--limit", type=int, default=10, help="Max events to include in MILP (default 10)")
    return parser.parse_args()


def load_events(path: str) -> List[StationaryEvent]:
    with open(path, "r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        events: List[StationaryEvent] = []
        for row in reader:
            events.append(
                StationaryEvent(
                    event_id=int(row["event_id"]),
                    start_time=float(row["start_time"]),
                    end_time=float(row["end_time"]),
                    duration_sec=float(row["duration_sec"]),
                    centroid_lat=float(row["centroid_lat"]),
                    centroid_lon=float(row["centroid_lon"]),
                    drift_radius_m=float(row["drift_radius_m"]),
                    num_points=int(row["num_points"]),
                    source_track_id=row.get("source_track_id") or None,
                    quality_flag=row.get("quality_flag", "good"),
                    risk=float(row.get("risk", 1.0)),
                )
            )
        return events


def load_boats(path: str) -> List[PatrolBoat]:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    boats: List[PatrolBoat] = []
    for entry in data:
        boats.append(
            PatrolBoat(
                boat_id=str(entry["boat_id"]),
                base_lat=float(entry["base_lat"]),
                base_lon=float(entry["base_lon"]),
                speed_mps=float(entry["speed_mps"]),
                shift_limit=float(entry["shift_limit"]),
                detect_buffer=float(entry.get("detect_buffer", 0.0)),
            )
        )
    return boats


def solve_milp(events: List[StationaryEvent], boats: List[PatrolBoat]):
    model = pulp.LpProblem("PatrolAllocation", pulp.LpMaximize)
    x = {
        (b.boat_id, e.event_id): pulp.LpVariable(f"x_{b.boat_id}_{e.event_id}", 0, 1, cat=pulp.LpBinary)
        for b in boats
        for e in events
    }
    # Objective: maximize risk * duration coverage
    model += pulp.lpSum(e.risk * e.duration_sec * x[(b.boat_id, e.event_id)] for b in boats for e in events)
    # Each event served at most once
    for e in events:
        model += pulp.lpSum(x[(b.boat_id, e.event_id)] for b in boats) <= 1
    # Boat shift limits (service time only; optimistic)
    for b in boats:
        model += (
            pulp.lpSum((e.duration_sec + max(b.detect_buffer, 0.0)) * x[(b.boat_id, e.event_id)] for e in events)
            <= b.shift_limit
        )
    model.solve(pulp.PULP_CBC_CMD(msg=False))
    selected = {
        b.boat_id: [e.event_id for e in events if x[(b.boat_id, e.event_id)].value() > 0.5]
        for b in boats
    }
    total_weight = sum(
        e.risk * e.duration_sec * x[(b.boat_id, e.event_id)].value()
        for b in boats
        for e in events
    )
    return selected, total_weight


def main() -> None:
    args = parse_args()
    events = load_events(args.events)[: args.limit]
    boats = load_boats(args.boats)

    milp_selection, milp_weight = solve_milp(events, boats)
    heuristic_assignments = assign_boats(events, boats)
    heuristic_weight = sum(a.total_weight for a in heuristic_assignments)

    print("MILP objective:", milp_weight)
    print("MILP assignments:", milp_selection)
    print("Heuristic objective:", heuristic_weight)
    print(
        "Gap (%):",
        100 * (milp_weight - heuristic_weight) / milp_weight if milp_weight else 0,
    )


if __name__ == "__main__":
    main()
