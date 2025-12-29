# Results & Discussion

## Coverage Insights
Using the synthetic dataset (6 vessels × up to 5 events each, 30 total events), the greedy heuristic produced the following coverage metrics:

- **Baseline** (2 boats, default shifts): covered 7 events (29% of total risk). Utilization averaged 42%, indicating both boats were busy but still left hotspots untouched.
- **High-Risk** (risk weights ×1.5): covered 8 events (43% risk). Prioritization shifted toward longer dwell times, but without more hours or boats the gain was modest.
- **Extended Shift** (shift limits ×1.5): covered 9 events (43% risk) while average utilization dropped to 28%. Extra patrol hours let boats reach additional clusters more efficiently than risk re-weighting alone.

The coverage plateau highlights a classic OR tradeoff: reallocating existing resources (longer shifts) can beat changing weights when the fleet is the bottleneck. Figure `results/synth_summary.png` visualizes these trends - risk coverage bars flatten while utilization drops as shift time increases.

## Discussion & Implications
1. **Resource Allocation**: With only two boats, risk coverage stalls below 50%. Adding even one more boat or redeploying bases near hotspots would likely yield >70% coverage - an obvious target for future optimization.
2. **Heuristic Behavior**: The greedy scheduler favors long events with high risk. Short but frequent dwells remain uncovered, suggesting a need for alternative strategies (e.g., set-cover approximations or MILP with binary visitation variables) when short events are critical.
3. **Sensitivity**: Extending shifts had a non-linear effect - boats consumed only ~2.1k seconds per mission, so pushing shift limits much further won’t help unless travel-to-event times shrink or more events become reachable.
4. **Policy Takeaway**: Investing in endurance (fuel, crew shifts) may deliver higher marginal benefit than simply reprioritizing incidents, especially when hotspots are far from patrol bases.

## Next Enhancements
- Benchmark the greedy heuristic against a small MILP to quantify optimality gaps.
- Expand scenario sweeps (vary boat counts, base placements) and integrate plots directly into the final write-up.
- Consider dual-use framing (urban delivery) to showcase OR versatility.
