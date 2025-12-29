# Scenario Simulation Plan

## Goals
- Quantify how patrol resource levels, event thresholds, and spatial distributions influence detection coverage.
- Produce marginal-return curves and sensitivity tables suitable for OR write-up sections.

## Inputs
- `events.csv`: stationary events with duration, centroid, drift radius, risk.
- Patrol configs: number of boats, base locations, shift lengths, speeds, fuel/time caps.
- Travel matrix: precomputed times/distances between bases and event centroids.
- Random seeds for stochastic event generation (optional synthetic cases).

## Scenario Dimensions
1. **Patrol budget sweep**: vary boats from 1..B_max and shift length from 2–12 hours.
2. **Detection thresholds**: adjust stationary detection `T` and `D` to see effect on event counts and sizes.
3. **Spatial clustering**: simulate uniform vs. hotspot distributions of events.
4. **Risk weighting**: compare uniform risk vs. heavy-tailed risk scores.

## Procedure
1. For each scenario tuple `(budget, thresholds, distribution, risk)`:
   - Load/construct event set.
   - Run optimization heuristic/MILP to allocate patrols.
   - Compute KPIs: events covered, illegal time covered, average response gap, boat utilization.
2. Repeat with multiple random seeds if synthetic data is used to estimate variance.
3. Store outputs in tidy CSV (one row per scenario) for plotting.

## KPIs & Visuals
- Coverage curve: % events detected vs. patrol hours.
- Marginal gains: incremental detections per additional boat.
- Heatmap: detection probability by spatial cell.
- Sensitivity bars: effect of `T`/`D` on total illegal time captured.

## Tools
- Python notebook or script orchestrating scenarios.
- `matplotlib`/`seaborn` for figures.
- Optional `geopandas`/`kepler.gl` for spatial validation.

## Validation
- Cross-check heuristic results with MILP on small instances.
- Inspect random subset of patrol schedules for feasibility (respect time windows, travel bounds).
