# Results Highlights

## Scenario Coverage
- Generated synthetic dataset (`data/synth_events.csv`) with 6 vessels × 5 stationary events each.
- Ran three scenarios:
  1. `baseline`: two boats with default shifts.
  2. `high_risk`: boost event risk weights by 1.5×.
  3. `extended_shift`: increase boat shift limits by 50%.

| Scenario       | Events Covered | Risk Coverage (%) | Avg Util (%) | Max Util (%) |
|----------------|----------------|-------------------|--------------|--------------|
| baseline       | 7 / 30         | 29                | 42           | 65           |
| high_risk      | 8 / 30         | 43                | 42           | 65           |
| extended_shift | 9 / 30         | 43                | 28           | 44           |

- **Insight**: Extending shift budgets had a larger effect on coverage than inflating risk scores - boats gained the flexibility to chase more distant hotspots without increasing fleet size.

## Visualization
- `results/synth_summary.png` plots risk coverage (bar) and total weight/utilization (line + bar) for each scenario.
- Clear diminishing returns: coverage plateaus near 40% until fleet capacity changes.

## Implications
- The heuristic prioritizes longer, higher-risk events but still leaves many short dwells uncovered, suggesting a multi-boat or staged response strategy.
- Next experiments: vary the number of boats and base locations to see how quickly risk coverage approaches 80%+, and benchmark against a MILP on smaller subsets to validate the greedy approach.
