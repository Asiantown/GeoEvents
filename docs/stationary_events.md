# Stationary Event Specification

## Event Schema
Each stationary event derived from the raw GPS track must include the following fields:

- `event_id`: monotonically increasing identifier within a track.
- `start_time`: timestamp of the first trackpoint in the event window.
- `end_time`: timestamp of the last trackpoint that still satisfies the distance constraint relative to the seed point.
- `duration_sec`: `end_time - start_time`.
- `centroid_lat`, `centroid_lon`: arithmetic mean of latitudes and longitudes for all points in the event.
- `drift_radius_m`: maximum great-circle distance between any point in the event and the centroid (captures spread/drift).
- `num_points`: count of contributing samples (for diagnostics / variance checks).
- `source_track_id`: identifier of the originating track / vessel.
- `quality_flag`: categorical note (e.g., `good`, `sparse`, `gapped`) depending on sampling density.

## Extraction Rules

1. **Inputs**: ordered trackpoints with lat/lon/time, a time threshold `T` (seconds), and a distance threshold `D` (meters).
2. **Eligibility**: a candidate anchor point `P` may start an event only if the remaining track length from `P` to the final point is ≥ `T`.
3. **Window growth**: expand forward from `P` while each subsequent point stays within `D` meters of `P` and the elapsed time from `P` is < `T`.
4. **Completion**: once the window duration reaches or exceeds `T`, close the event at the last point that was within `D`.
5. **Centroid & radius**: compute centroid over all included points; drift radius is the max distance to centroid.
6. **Advancing**: skip ahead to the first point outside distance `D` from the anchor (prevents overlapping events) and treat this as the next anchor candidate.
7. **Merging**: if consecutive events are separated by a gap shorter than `gap_merge` seconds and their centroids are within `D/2`, merge them (update start/end/duration/centroid).
8. **Sparsity guard**: flag events as `sparse` if median sampling interval exceeds `T/4` or if fewer than `min_points` samples were captured.
9. **Output**: append structured records (CSV/JSON) for downstream optimization models.

## Derived Products

- `events.csv`: tabular dump of the schema for easy ingestion.
- `events.geojson`: optional spatial output for mapping or validation.

## Validation Checklist

- Manual spot-check of a few tracks to ensure event durations align with expectations.
- Histogram of drift radii vs. distance threshold to confirm thresholds are respected.
- Consistency check: sum of per-event durations should never exceed total stationary time detected by legacy point output.