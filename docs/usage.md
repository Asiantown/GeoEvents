# Usage Guide

## 1. Extract stationary events
```
./scripts/extract_events.py path/to/track.txt \
    --time-threshold 180 \
    --distance-threshold 200 \
    --gap-merge 60 \
    --track-id VESSEL_01 \
    > data/events_vessel01.csv
```
Input track files contain `lat lon time` per line (whitespace- or comma-separated). The script emits CSV with the stationary-event schema described in `docs/stationary_events.md`.

## 2. Assign patrol boats
Prepare a boat config JSON (example):
```
[
  {"boat_id": "A", "base_lat": 0.0, "base_lon": 0.0, "speed_mps": 5.0, "shift_limit": 3600, "detect_buffer": 120},
  {"boat_id": "B", "base_lat": 0.05, "base_lon": 0.02, "speed_mps": 6.0, "shift_limit": 5400}
]
```
Run the allocator:
```
./scripts/assign_patrols.py data/events_all.csv configs/boats.json --output results/assignments.csv
```
The output CSV lists each boat, the event IDs covered (semicolon-separated), total covered weight (`risk * duration`), utilization fraction, and total mission time used.

## 3. Testing shortcuts
- `python3 -m compileall src scripts` — quick syntax check
- `./scripts/extract_events.py ...` with `--time-threshold` / `--distance-threshold` variations to sanity-check event counts
- `./scripts/assign_patrols.py sample/events.csv sample/boats.json` for heuristic smoke tests

## 4. Next steps
- Plug the assignments into the simulation framework (`docs/simulation_plan.md`) to sweep patrol budgets and thresholds.
- Integrate metrics into the project write-up outline (`docs/writeup_outline.md`).
