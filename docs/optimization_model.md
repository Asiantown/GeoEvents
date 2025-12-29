# Patrol Allocation Optimization Model

## Sets and Indices
- `E`: set of stationary events, index `e`.
- `B`: set of patrol boats, index `b`.
- `T`: discrete time periods (optional discretization for tighter constraints), index `t`.

## Parameters
- `start_e`, `end_e`: start/end timestamps of event `e`.
- `dur_e = end_e - start_e`.
- `loc_e`: centroid coordinates of event `e`.
- `risk_e`: risk or priority score for event `e` (default 1 if unknown).
- `travel_{b,e}`: travel time from boat `b`'s base to event `e`.
- `travel_{e1,e2}`: travel time from event `e1` to `e2` (triangle inequality assumed).
- `speed_b`: maximum speed for boat `b` (used for travel time if needed).
- `shift_b`: total patrol time budget for boat `b` in the planning horizon.
- `detect_buffer`: minimum overlap (seconds) boat must spend at event to count as detection.
- `M`: large constant for linearization (e.g., max horizon length).

## Decision Variables
- `x_{b,e} ∈ {0,1}`: 1 if boat `b` is assigned to visit event `e`.
- `y_e ∈ {0,1}`: 1 if event `e` is covered by at least one boat (derived variable).
- `s_{b,e}` continuous: start time when boat `b` arrives at event `e` (if assigned).
- `z_{b,e1,e2} ∈ {0,1}`: sequencing variable, 1 if boat `b` visits `e1` before `e2`.

## Objective Examples
Maximize weighted detections:
```
maximize  Σ_e risk_e * y_e
```
Alternative objective (replace or combine): maximize illegal fishing time covered `Σ_e risk_e * dur_e * y_e`, or minimize total response time `Σ_e (s_{b,e} - start_e)^+`.

## Constraints
1. **Coverage definition**
```
y_e ≤ Σ_b x_{b,e}    ∀ e
```
2. **Boat budget**
```
Σ_e (travel_{b,e} + detect_buffer) * x_{b,e} ≤ shift_b    ∀ b
```
(Extend with pairwise travel and service times for tours via Miller–Tucker–Zemlin or flow constraints if sequencing matters.)

3. **Temporal feasibility** (simplified pairwise sequencing)
```
s_{b,e1} + service_e1 + travel_{e1,e2} ≤ s_{b,e2} + M * (1 - z_{b,e1,e2})
```
```
z_{b,e1,e2} + z_{b,e2,e1} = x_{b,e1} + x_{b,e2} - 1
```
4. **Detection validity**
```
s_{b,e} ≥ start_e - M * (1 - x_{b,e})
```
```
s_{b,e} + dur_e ≤ end_e + M * (1 - x_{b,e})
```
ensuring arrival during the event window.

5. **Single-visit per boat per event**
```
x_{b,e} ∈ {0,1}
```
6. **Optional time discretization**: introduce `cover_{b,e,t}` to ensure a boat occupies only one event per time slot and respects operating hours.

## Heuristic Variant
When MILP is overkill, use weighted interval scheduling: sort events by end time, define weight `risk_e * dur_e`, and select events subject to `travel`-adjusted compatibility. Boats can be handled greedily by iterating assignments.

## Outputs
- Selected events per boat with arrival times (`s_{b,e}`) and travel paths.
- Coverage metrics: % events detected, total risk covered, response delay distribution.
- Resource utilization per boat.
