# GeoEvents OR Pipeline

Optimization-focused toolkit for transforming GPS tracks into stationary events, allocating limited patrol resources, and analyzing scenario tradeoffs.

## Components
- `src/stationary_events.py`: event extraction logic (centroid, duration, drift radius, risk).
- `scripts/extract_events.py`: CLI to convert `lat lon time` tracks into event CSVs.
- `scripts/assign_patrols.py`: greedy patrol allocator for one scenario.
- `scripts/run_scenarios.py`: batch runner for multiple scenario configs.
- `scripts/generate_synthetic_events.py`: creates reproducible multi-vessel event datasets.
- `scripts/plot_scenarios.py`: plots coverage/utilization metrics.
- `scripts/milp_benchmark.py`: small MILP baseline for validation.
- Docs in `docs/` capture schema, modeling assumptions, results, and next steps.

## Quick Start
1. **Extract events**
   ```bash
   ./scripts/extract_events.py path/to/track.txt \
       --time-threshold 180 --distance-threshold 200 \
       --gap-merge 60 --track-id VESSEL_01 > data/events.csv
   ```
2. **Assign patrols**
   ```bash
   ./scripts/assign_patrols.py data/events.csv configs/sample_boats.json \
       --output results/assignments.csv
   ```
3. **Run scenarios**
   ```bash
   ./scripts/run_scenarios.py \
       --events data/events.csv \
       --boats configs/sample_boats.json \
       --scenarios configs/scenarios.json \
       --output results/scenario_summary.csv \
       --per-boat-json results/per_boat.json
   ```
4. **Plot summary & generate synthetic data**
   ```bash
   ./scripts/generate_synthetic_events.py --output data/synth_events.csv
   ./scripts/plot_scenarios.py --summary results/scenario_summary.csv \
       --output results/scenario_summary.png
   ```

## Dependencies
- Python 3.12+
- `matplotlib` for plotting (`python3 -m pip install --user matplotlib`)
- `pulp` for MILP benchmarking (`python3 -m pip install --user pulp`)

## Documentation Highlights
- `docs/stationary_events.md`: event schema & extraction rules.
- `docs/optimization_model.md`: patrol formulation (variables, constraints).
- `docs/results_discussion.md`: scenario findings & policy implications.
- `docs/milp_notes.md`: heuristic vs. MILP comparison.

## Testing
- `python3 -m compileall src scripts`
- Sample CLI invocations above; see `docs/usage.md` for more.

## Next Steps
Future improvements (see `docs/next_steps.md`): richer scenario sweeps, MILP-informed heuristics, and report generation.
