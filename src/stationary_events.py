"""Utilities for deriving stationary events from raw GPS trackpoints."""
from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from typing import List, Sequence
import math


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance in meters between two lat/lon pairs."""
    radius_earth = 6371000.0  # meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius_earth * c


@dataclass(frozen=True)
class TrackPoint:
    lat: float
    lon: float
    time: float  # seconds since epoch


@dataclass
class StationaryEvent:
    event_id: int
    start_time: float
    end_time: float
    duration_sec: float
    centroid_lat: float
    centroid_lon: float
    drift_radius_m: float
    num_points: int
    source_track_id: str | None = None
    quality_flag: str = "good"


def extract_events(
    points: Sequence[TrackPoint],
    time_threshold: float,
    distance_threshold: float,
    *,
    gap_merge: float = 0.0,
    min_points: int = 2,
    track_id: str | None = None,
) -> List[StationaryEvent]:
    """Return stationary events that satisfy the given time and distance thresholds."""
    if time_threshold <= 0 or distance_threshold <= 0:
        raise ValueError("time_threshold and distance_threshold must be positive")
    if not points:
        return []

    pts = sorted(points, key=lambda p: p.time)
    events: List[StationaryEvent] = []
    n = len(pts)
    i = 0
    event_counter = 1
    while i < n:
        anchor = pts[i]
        if pts[-1].time - anchor.time < time_threshold:
            break
        window_deadline = anchor.time + time_threshold
        last_valid = i
        j = i
        valid = True
        while j < n and pts[j].time < window_deadline:
            if _within_distance(anchor, pts[j], distance_threshold):
                last_valid = j
                j += 1
            else:
                valid = False
                break
        if not valid:
            i += 1
            continue
        # ensure observations reach the deadline so duration >= threshold
        deadline_time = pts[j].time if j < n else pts[-1].time
        if deadline_time < window_deadline:
            break

        # extend event while the vessel remains within the distance bound
        while j < n and _within_distance(anchor, pts[j], distance_threshold):
            last_valid = j
            j += 1

        duration = pts[last_valid].time - anchor.time
        num_pts = last_valid - i + 1
        if num_pts >= min_points and duration >= time_threshold:
            event_points = pts[i : last_valid + 1]
            centroid_lat, centroid_lon, radius = _centroid_radius(event_points)
            quality_flag = _quality_flag(event_points, time_threshold, min_points)
            events.append(
                StationaryEvent(
                    event_id=event_counter,
                    start_time=anchor.time,
                    end_time=pts[last_valid].time,
                    duration_sec=duration,
                    centroid_lat=centroid_lat,
                    centroid_lon=centroid_lon,
                    drift_radius_m=radius,
                    num_points=num_pts,
                    source_track_id=track_id,
                    quality_flag=quality_flag,
                )
            )
            event_counter += 1
            next_i = last_valid + 1
            while next_i < n and _within_distance(anchor, pts[next_i], distance_threshold):
                next_i += 1
            i = next_i
        else:
            i += 1

    if gap_merge > 0 and events:
        events = _merge_events(events, gap_merge, distance_threshold / 2)
        for idx, event in enumerate(events, start=1):
            event.event_id = idx  # type: ignore[misc]
    return events


def _within_distance(p1: TrackPoint, p2: TrackPoint, threshold: float) -> bool:
    return haversine_meters(p1.lat, p1.lon, p2.lat, p2.lon) <= threshold


def _centroid_radius(points: Sequence[TrackPoint]) -> tuple[float, float, float]:
    lat = sum(p.lat for p in points) / len(points)
    lon = sum(p.lon for p in points) / len(points)
    radius = max(haversine_meters(lat, lon, p.lat, p.lon) for p in points)
    return lat, lon, radius


def _quality_flag(points: Sequence[TrackPoint], time_threshold: float, min_points: int) -> str:
    if len(points) < max(min_points, 2):
        return "sparse"
    intervals = _sampling_intervals(points)
    if intervals:
        med = median(intervals)
        if med > time_threshold / 4:
            return "sparse"
    return "good"


def _sampling_intervals(points: Sequence[TrackPoint]) -> List[float]:
    return [points[i + 1].time - points[i].time for i in range(len(points) - 1)]


def _merge_events(
    events: Sequence[StationaryEvent],
    gap_merge: float,
    centroid_threshold: float,
) -> List[StationaryEvent]:
    merged: List[StationaryEvent] = [events[0]]
    for event in events[1:]:
        prev = merged[-1]
        gap = event.start_time - prev.end_time
        centroid_dist = haversine_meters(
            prev.centroid_lat, prev.centroid_lon, event.centroid_lat, event.centroid_lon
        )
        if gap <= gap_merge and centroid_dist <= centroid_threshold:
            merged[-1] = _combine_events(prev, event)
        else:
            merged.append(event)
    return merged


def _combine_events(a: StationaryEvent, b: StationaryEvent) -> StationaryEvent:
    total_points = a.num_points + b.num_points
    centroid_lat = (a.centroid_lat * a.num_points + b.centroid_lat * b.num_points) / total_points
    centroid_lon = (a.centroid_lon * a.num_points + b.centroid_lon * b.num_points) / total_points
    radius = max(
        a.drift_radius_m + haversine_meters(a.centroid_lat, a.centroid_lon, centroid_lat, centroid_lon),
        b.drift_radius_m + haversine_meters(b.centroid_lat, b.centroid_lon, centroid_lat, centroid_lon),
    )
    quality = "good" if a.quality_flag == b.quality_flag == "good" else "sparse"
    return StationaryEvent(
        event_id=a.event_id,
        start_time=a.start_time,
        end_time=b.end_time,
        duration_sec=b.end_time - a.start_time,
        centroid_lat=centroid_lat,
        centroid_lon=centroid_lon,
        drift_radius_m=radius,
        num_points=total_points,
        source_track_id=a.source_track_id or b.source_track_id,
        quality_flag=quality,
    )


__all__ = [
    "TrackPoint",
    "StationaryEvent",
    "extract_events",
    "haversine_meters",
]
