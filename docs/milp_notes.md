# MILP vs. Greedy Benchmark

Using the first 8 synthetic events:
- MILP objective (optimal risk × duration): **15,788** with assignments `Alpha -> [1,3]`, `Bravo -> [6,8]`.
- Greedy heuristic objective: **4,237** with a 73% gap.

Interpretation:
- Greedy scheduler is overly conservative when events are widely separated; it spends travel time reaching the first high-risk event and never reallocates.
- MILP at least highlights the upper bound, even if our travel approximations are simple (service-only time budget). For the write-up, emphasize that the heuristic is a baseline and future work includes incorporating MILP insights back into heuristics (e.g., interval scheduling with compatibility windows).

Next improvement: refine the heuristic to account for cumulative coverage weight rather than single-path greediness, or introduce iterative re-optimization per boat.
