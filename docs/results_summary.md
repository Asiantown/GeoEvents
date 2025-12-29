# Preliminary Scenario Findings

Using `data/synth_events.csv` (6 vessels × 5 events each):

| Scenario         | Events Covered | Risk Coverage | Avg Util (%) | Notes |
|------------------|----------------|---------------|--------------|-------|
| baseline         | 7              | 29%           | 42.1         | Boats saturated quickly, leaving many hotspots uncovered. |
| high_risk        | 8              | 43%           | 42.1         | Risk scaling nudged the heuristic to prioritize longer/high-risk dwells. |
| extended_shift   | 9              | 43%           | 28.1         | Extra shift time lets boats stretch further, increasing coverage without new vessels. |

Key takeaways:
- Even simple heuristics exhibit clear diminishing returns: extending shifts produced a bigger coverage jump than uniformly inflating risk scores.
- Hotspot clustering drives boat utilization >40% despite only two vessels - adding a third boat or redistributing base locations would likely yield >70% risk coverage.

Next steps:
1. Expand scenario grid (vary boat counts, base placements). 
2. Produce coverage vs. patrol budget plot for the write-up.
3. Cross-check heuristic results with a MILP on a subset of events.
