# Project Write-up Outline

1. **Introduction**
   - Maritime enforcement challenge and limited patrol resources.
   - Role of stationary event detection as upstream data.

2. **Data & Preprocessing**
   - Source of GPS tracks, sampling assumptions, noise handling.
   - Stationary event extraction (refer to schema, thresholds, validation checks).

3. **Patrol Optimization Model**
   - Define decision variables, objective, constraints.
   - Discuss modeling assumptions (travel times, shift limits, detection buffer).
   - Mention heuristic vs. MILP approach.

4. **Simulation Design**
   - Scenario dimensions (budget, thresholds, spatial distributions).
   - KPIs and evaluation methodology.

5. **Results**
   - Coverage vs. patrol resources charts.
   - Sensitivity analyses (thresholds, risk weighting).
   - Qualitative interpretation (e.g., diminishing returns, hotspot prioritization).

6. **Discussion**
   - Limitations (data sparsity, model simplifications, weather/sea state omissions).
   - Extensions: multi-day planning, stochastic arrivals, urban delivery analogue.

7. **Conclusion**
   - Key takeaways, policy implications, future work.

8. **Appendix**
   - Detailed parameter tables, solver settings, pseudocode for heuristics.
