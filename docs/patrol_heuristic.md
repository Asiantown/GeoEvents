# Greedy Patrol Allocation Heuristic

1. **Prioritize events**
   - Compute weight `w = risk * duration_sec` for each stationary event.
   - Sort events by descending `w` (tie-breaker: earlier end time) so high-value events are attempted first.

2. **Per-boat scheduling**
   - Normalize timestamps by subtracting the earliest event start; treat boat departure as time 0.
   - Iterate candidate events in ascending end-time order and attempt to append them to the boat's route.
   - For each event, compute travel time from current location using straight-line speed and add any waiting time until the event starts.
   - Require that the boat can remain on station for `detect_buffer` seconds (or the full event duration if `detect_buffer = 0`) before the event ends; otherwise skip it.
   - Track cumulative mission time (travel + waiting + on-station). Reject events that would exceed the boat's `shift_limit`.

3. **Multi-boat allocation**
   - After scheduling a boat, remove its selected events from the candidate pool to avoid double assignment.
   - Repeat for remaining boats in priority order to obtain a disjoint set of coverages.

4. **Outputs & metrics**
   - For each boat, report the ordered event IDs, total covered weight, time used, and utilization = `time_used / shift_limit`.
   - Aggregate KPIs: total risk covered, per-boat utilization, unserved high-risk events (for sensitivity analysis).

This heuristic is intentionally simple (no MILP solver required) yet encodes key OR elements—resource limits, time windows, and prioritization by value. It serves as a baseline before exploring more advanced interval-scheduling or set-cover formulations.
