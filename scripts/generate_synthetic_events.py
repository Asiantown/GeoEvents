#!/usr/bin/env python3
"""Generate synthetic stationary events for testing and simulation."""
from __future__ import annotations

import argparse
import csv
import math
import random
from typing import List, Sequence, Tuple


CLUSTER_CENTERS = [
    (0.0, 0.0),
    (0.15, 0.05),
    (-0.1, 0.12),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--num-vessels", type=int, default=5, help="Number of synthetic vessels")
    parser.add_argument("--events-per-vessel", type=int, default=4, help="Events per vessel")
    parser.add_argument("--horizon", type=float, default=86400.0, help="Planning horizon in seconds (default 1 day)")
    parser.add_argument("--min-duration", type=float, default=600.0, help="Minimum stationary duration (seconds)")
    parser.add_argument("--max-duration", type=float, default=3600.0, help="Maximum stationary duration (seconds)")
    parser.add_argument("--min-gap", type=float, default=300.0, help="Minimum travel gap between events (seconds)")
    parser.add_argument("--max-gap", type=float, default=3600.0, help="Maximum travel gap between events (seconds)")
    parser.add_argument("--cluster-radius", type=float, default=3000.0, help="Cluster radius in meters")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output", required=True, help="Output CSV path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    random.seed(args.seed)
    events: List[dict] = []
    event_id = 1
    for vessel_id in range(1, args.num_vessels + 1):
        time_cursor = random.uniform(0, args.min_gap)
        for _ in range(args.events_per_vessel):
            duration = random.uniform(args.min_duration, args.max_duration)
            if time_cursor + duration > args.horizon:
                break
            centroid = random_cluster_point(args.cluster_radius)
            drift_radius = random.uniform(20.0, args.cluster_radius / 5.0)
            num_points = max(6, int(duration / 60))
            risk = round(random.uniform(0.8, 1.5) * (1 + 0.2 * vessel_id), 2)
            events.append(
                dict(
                    event_id=event_id,
                    start_time=round(time_cursor, 2),
                    end_time=round(time_cursor + duration, 2),
                    duration_sec=round(duration, 2),
                    centroid_lat=centroid[0],
                    centroid_lon=centroid[1],
                    drift_radius_m=round(drift_radius, 2),
                    num_points=num_points,
                    source_track_id=f"VESSEL_{vessel_id:02d}",
                    quality_flag="good" if num_points >= 10 else "sparse",
                    risk=risk,
                )
            )
            event_id += 1
            gap = random.uniform(args.min_gap, args.max_gap)
            time_cursor += duration + gap
    write_events(events, args.output)


def random_cluster_point(radius_m: float) -> Tuple[float, float]:
    center_lat, center_lon = random.choice(CLUSTER_CENTERS)
    distance = random.uniform(0, radius_m)
    bearing = random.uniform(0, 2 * math.pi)
    delta_lat = (distance * math.cos(bearing)) / 111_000.0
    lat = center_lat + delta_lat
    delta_lon = (distance * math.sin(bearing)) / (111_000.0 * math.cos(math.radians(center_lat + 1e-6)))
    lon = center_lon + delta_lon
    return round(lat, 6), round(lon, 6)


def write_events(events: Sequence[dict], path: str) -> None:
    if not events:
        raise ValueError("No events generated; adjust parameters")
    fieldnames = list(events[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(events)


if __name__ == "__main__":
    main()
