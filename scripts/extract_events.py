#!/usr/bin/env python3
"""CLI for converting GPS trackpoints into stationary events."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import List, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.stationary_events import StationaryEvent, TrackPoint, extract_events


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input",
        nargs="?",
        help="Path to track file (lat lon time per row). Defaults to stdin.",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Optional output CSV path. Defaults to stdout.",
    )
    parser.add_argument(
        "--time-threshold",
        type=float,
        required=True,
        help="Seconds required to mark a stationary event.",
    )
    parser.add_argument(
        "--distance-threshold",
        type=float,
        required=True,
        help="Max meters from anchor allowed during stationary window.",
    )
    parser.add_argument(
        "--gap-merge",
        type=float,
        default=0.0,
        help="Merge events separated by ≤ this many seconds (default: 0).",
    )
    parser.add_argument(
        "--min-points",
        type=int,
        default=2,
        help="Minimum samples per event (default: 2).",
    )
    parser.add_argument(
        "--track-id",
        help="Identifier to tag output events with.",
    )
    return parser.parse_args()


def read_trackpoints(path: str | None) -> List[TrackPoint]:
    fh = sys.stdin if not path else open(path, "r", encoding="utf-8")
    try:
        points: List[TrackPoint] = []
        for line in fh:
            line = line.strip()
            if not line or line.lstrip().startswith("#"):
                continue
            tokens = _tokenize(line)
            if len(tokens) < 3:
                continue
            try:
                lat, lon, timestamp = float(tokens[0]), float(tokens[1]), float(tokens[2])
            except ValueError:
                # probably a header row
                continue
            points.append(TrackPoint(lat=lat, lon=lon, time=timestamp))
        return points
    finally:
        if fh is not sys.stdin:
            fh.close()


def _tokenize(row: str) -> List[str]:
    if "," in row:
        row = row.replace(",", " ")
    return [token for token in row.split() if token]


def write_events(events: Sequence[StationaryEvent], path: str | None) -> None:
    fieldnames = [
        "event_id",
        "start_time",
        "end_time",
        "duration_sec",
        "centroid_lat",
        "centroid_lon",
        "drift_radius_m",
        "num_points",
        "source_track_id",
        "quality_flag",
        "risk",
    ]
    dest = sys.stdout if not path else open(path, "w", newline="", encoding="utf-8")
    close_after = dest is not sys.stdout
    try:
        writer = csv.DictWriter(dest, fieldnames=fieldnames)
        writer.writeheader()
        for event in events:
            writer.writerow(
                {
                    "event_id": event.event_id,
                    "start_time": event.start_time,
                    "end_time": event.end_time,
                    "duration_sec": event.duration_sec,
                    "centroid_lat": event.centroid_lat,
                    "centroid_lon": event.centroid_lon,
                    "drift_radius_m": event.drift_radius_m,
                    "num_points": event.num_points,
                    "source_track_id": event.source_track_id or "",
                    "quality_flag": event.quality_flag,
                    "risk": event.risk,
                }
            )
    finally:
        if close_after:
            dest.close()


def main() -> None:
    args = parse_args()
    points = read_trackpoints(args.input)
    events = extract_events(
        points,
        time_threshold=args.time_threshold,
        distance_threshold=args.distance_threshold,
        gap_merge=args.gap_merge,
        min_points=args.min_points,
        track_id=args.track_id,
    )
    write_events(events, args.output)


if __name__ == "__main__":
    main()
