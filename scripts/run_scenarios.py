#!/usr/bin/env python3
"""Run patrol allocation heuristic across multiple scenarios."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from copy import deepcopy
from dataclasses import asdict, replace
from pathlib import Path
from statistics import mean
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    yaml = None

from src.patrol_heuristic import Assignment, PatrolBoat, assign_boats
from src.stationary_events import StationaryEvent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", required=True, help="CSV containing stationary events")
    parser.add_argument("--boats", required=True, help="JSON describing patrol boats")
    parser.add_argument("--scenarios", required=True, help="YAML/JSON scenario list")
    parser.add_argument("--output", required=True, help="CSV summary output path")
    parser.add_argument("--per-boat-json", help="Optional path to dump per-boat assignments as JSON")
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


def load_scenarios(path: str) -> List[Dict]:
    text = Path(path).read_text(encoding="utf-8")
    if yaml is not None:
        data = yaml.safe_load(text)
    else:
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "PyYAML is not installed and the scenario file is not valid JSON."
            ) from exc
    if not isinstance(data, list):
        raise ValueError("Scenario file must contain a list")
    return data


def apply_scenario(events: List[StationaryEvent], scenario: Dict) -> List[StationaryEvent]:
    risk_scale = float(scenario.get("risk_scale", 1.0))
    filtered = _filter_events(events, scenario)
    return [replace(event, risk=event.risk * risk_scale) for event in filtered]


def _filter_events(events: List[StationaryEvent], scenario: Dict) -> List[StationaryEvent]:
    lat_min = scenario.get("lat_min", -float("inf"))
    lat_max = scenario.get("lat_max", float("inf"))
    lon_min = scenario.get("lon_min", -float("inf"))
    lon_max = scenario.get("lon_max", float("inf"))
    return [
        event
        for event in events
        if lat_min <= event.centroid_lat <= lat_max and lon_min <= event.centroid_lon <= lon_max
    ]


def scale_boats(boats: List[PatrolBoat], scenario: Dict) -> List[PatrolBoat]:
    multiplier = float(scenario.get("boat_multiplier", 1.0))
    adjusted: List[PatrolBoat] = []
    for boat in boats:
        adjusted.append(
            replace(
                boat,
                shift_limit=boat.shift_limit * multiplier,
            )
        )
    extra = int(scenario.get("duplicate_boats", 0))
    for _ in range(extra):
        for boat in boats:
            adjusted.append(deepcopy(boat))
    return adjusted


def summarize(assignments: List[Assignment], events: List[StationaryEvent]) -> Dict[str, float]:
    covered_ids = set()
    total_weight = 0.0
    utilizations = []
    for assignment in assignments:
        covered_ids.update(assignment.events)
        total_weight += assignment.total_weight
        utilizations.append(assignment.utilization)
    event_map = {event.event_id: event for event in events}
    risk_total = sum(event.risk * event.duration_sec for event in events)
    risk_covered = sum(event_map[eid].risk * event_map[eid].duration_sec for eid in covered_ids if eid in event_map)
    avg_util = mean(utilizations) if utilizations else 0.0
    max_util = max(utilizations) if utilizations else 0.0
    return {
        "events_covered": len(covered_ids),
        "unserved_events": max(len(events) - len(covered_ids), 0),
        "total_weight": total_weight,
        "risk_coverage_ratio": (risk_covered / risk_total) if risk_total else 0.0,
        "avg_utilization": avg_util,
        "max_utilization": max_util,
    }


SUMMARY_FIELDS = [
    "scenario",
    "events_covered",
    "unserved_events",
    "total_weight",
    "risk_coverage_ratio",
    "avg_utilization",
    "max_utilization",
]


def write_summary(rows: List[Dict], path: str) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    base_events = load_events(args.events)
    base_boats = load_boats(args.boats)
    scenarios = load_scenarios(args.scenarios)

    summary_rows: List[Dict] = []
    per_boat: Dict[str, List[Dict]] = {}
    for idx, scenario in enumerate(scenarios):
        name = scenario.get("name") or f"scenario_{idx+1}"
        scenario_events = apply_scenario(base_events, scenario)
        scenario_boats = scale_boats(base_boats, scenario)
        assignments = assign_boats(scenario_events, scenario_boats)
        metrics = summarize(assignments, scenario_events)
        metrics["scenario"] = name
        summary_rows.append(metrics)
        per_boat[name] = [asdict(assignment) for assignment in assignments]

    write_summary(summary_rows, args.output)
    if args.per_boat_json:
        with open(args.per_boat_json, "w", encoding="utf-8") as fh:
            json.dump(per_boat, fh, indent=2)


if __name__ == "__main__":
    main()
