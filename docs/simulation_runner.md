# Scenario Runner Design

## Inputs
- `events_dir`: folder containing per-track stationary-event CSV files (uniform schema).
- `boats_config`: JSON describing patrol boats (same format used by `scripts/assign_patrols.py`).
- `scenarios.yaml`: list of scenario definitions with overrides:
  - `name`: label for output rows.
  - `time_threshold`, `distance_threshold`: optional overrides for extraction (if regenerating events).
  - `boat_multiplier`: scale patrol fleet size or shift limits.
  - `risk_scale`: multiply event risk weights to test prioritization sensitivity.

## Workflow
1. Load events (or regenerate via `extract_events` if raw tracks provided).
2. Apply scenario-specific transformations:
   - Scale `risk` by `risk_scale`.
   - Duplicate boats or stretch `shift_limit` by `boat_multiplier`.
   - Filter events by spatial bounding box (optional fields `bbox_lat`, `bbox_lon`).
3. Run `assign_boats` heuristic for each scenario.
4. Collect KPIs:
   - `events_covered`, `total_weight`, `avg_utilization`, `max_utilization`, `unserved_events`, `risk_coverage`.
5. Write a tidy CSV (rows = scenarios) plus optional per-boat breakdown JSON.

## CLI Skeleton
```
./scripts/run_scenarios.py \
    --events data/events.csv \
    --boats configs/boats.json \
    --scenarios configs/scenarios.yaml \
    --output results/scenario_summary.csv
```

## Extensibility
- Plug in alternative allocators by exposing a strategy interface.
- Allow Monte Carlo sampling by specifying `repeat: N` and randomizing risk/noise per run.
