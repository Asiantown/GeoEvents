#!/usr/bin/env python3
"""Assign patrol boats to stationary events using greedy heuristic."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.patrol_heuristic import Assignment, PatrolBoat, assign_boats
from src.stationary_events import StationaryEvent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("events", help="CSV of stationary events (from extract_events).")
    parser.add_argument("boats", help="JSON file describing patrol boats.")
    parser.add_argument("--output", "-o", help="Optional CSV to store assignments.")
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


def write_assignments(assignments: List[Assignment], path: str | None) -> None:
    fieldnames = ["boat_id", "events", "total_weight", "utilization", "time_used"]
    dest = sys.stdout if not path else open(path, "w", newline="", encoding="utf-8")
    close_after = dest is not sys.stdout
    try:
        writer = csv.DictWriter(dest, fieldnames=fieldnames)
        writer.writeheader()
        for assignment in assignments:
            writer.writerow(
                {
                    "boat_id": assignment.boat_id,
                    "events": ";".join(map(str, assignment.events)),
                    "total_weight": assignment.total_weight,
                    "utilization": assignment.utilization,
                    "time_used": assignment.time_used,
                }
            )
    finally:
        if close_after:
            dest.close()


def main() -> None:
    args = parse_args()
    events = load_events(args.events)
    boats = load_boats(args.boats)
    assignments = assign_boats(events, boats)
    write_assignments(assignments, args.output)


if __name__ == "__main__":
    main()
