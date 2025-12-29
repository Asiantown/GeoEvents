"""Greedy patrol allocation heuristic with shift/time window checks."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .stationary_events import StationaryEvent, haversine_meters


@dataclass
class PatrolBoat:
    boat_id: str
    base_lat: float
    base_lon: float
    speed_mps: float
    shift_limit: float  # seconds
    detect_buffer: float = 0.0  # seconds of on-station time required


@dataclass
class Assignment:
    boat_id: str
    events: List[int]
    total_weight: float
    utilization: float
    time_used: float


class SchedulingError(Exception):
    pass


def assign_boats(
    events: Sequence[StationaryEvent],
    boats: Sequence[PatrolBoat],
) -> List[Assignment]:
    """Assign events to boats greedily while respecting shift and time windows."""
    remaining = sorted(events, key=lambda e: (-e.risk * e.duration_sec, e.start_time))
    assignments: List[Assignment] = []
    for boat in boats:
        selected, time_used = _schedule_for_boat(remaining, boat)
        total_weight = sum(event.risk * event.duration_sec for event in selected)
        assignments.append(
            Assignment(
                boat_id=boat.boat_id,
                events=[event.event_id for event in selected],
                total_weight=total_weight,
                utilization=time_used / boat.shift_limit if boat.shift_limit > 0 else 0.0,
                time_used=time_used,
            )
        )
        taken_ids = {event.event_id for event in selected}
        remaining = [event for event in remaining if event.event_id not in taken_ids]
    return assignments


def _schedule_for_boat(
    events: Sequence[StationaryEvent],
    boat: PatrolBoat,
) -> tuple[List[StationaryEvent], float]:
    if boat.speed_mps <= 0 or boat.shift_limit <= 0:
        raise SchedulingError("Boat speed and shift_limit must be positive")
    if not events:
        return [], 0.0
    offset = min(event.start_time for event in events)
    time_used = 0.0
    current_time = 0.0
    current_lat = boat.base_lat
    current_lon = boat.base_lon
    selected: List[StationaryEvent] = []

    for event in sorted(events, key=lambda e: e.end_time):
        start = event.start_time - offset
        end = event.end_time - offset
        if end <= start:
            continue
        travel_time = _travel_time(current_lat, current_lon, event.centroid_lat, event.centroid_lon, boat.speed_mps)
        arrival_time = current_time + travel_time
        wait = 0.0
        if arrival_time < start:
            wait = start - arrival_time
            arrival_time = start
        if arrival_time >= end:
            continue
        available_window = end - arrival_time
        if boat.detect_buffer > 0:
            service_time = boat.detect_buffer
        else:
            service_time = min(event.duration_sec, available_window)
        if service_time <= 0 or service_time > available_window:
            continue
        additional = travel_time + wait + service_time
        if time_used + additional > boat.shift_limit:
            continue
        selected.append(event)
        time_used += additional
        current_time = arrival_time + service_time
        current_lat = event.centroid_lat
        current_lon = event.centroid_lon
    return selected, time_used


def _travel_time(lat1: float, lon1: float, lat2: float, lon2: float, speed_mps: float) -> float:
    if speed_mps <= 0:
        raise SchedulingError("speed_mps must be positive")
    return haversine_meters(lat1, lon1, lat2, lon2) / speed_mps


__all__ = ["PatrolBoat", "Assignment", "assign_boats", "SchedulingError"]
