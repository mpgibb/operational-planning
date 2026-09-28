# Data dictionary and observation rules

The data contain 156 weeks × seven days = 1,092 observations per scenario. Final evaluation uses weeks 104–155. `data/*_demand.csv` contains zero-based day, week, weekday and integer service demand. Each week combines trend, weekday effects, annual seasonality, an autoregressive weekly shock and daily noise. The surge and volatility changes start only at week 104.

The planner at week t can read demand through day 7t−1. Historical training features are themselves built from values available before each historical forecast week. Archived residual vectors were forecast at their own cutoffs and are added only after their outcomes occurred. Up to 52 past error vectors calibrate a seven-day predictive scenario distribution.

`results/*_daily_decisions.csv` records week, weekday, method, actual demand, forecast, marginal lower80/upper80, regular workers, realized cost, shortage units, overtime workers and unused capacity. `results/*_weekly.csv` aggregates cost, demand, shortages, overtime/regular worker-days and unused capacity by week and policy.

One regular or overtime worker supplies twelve same-day service units. Regular staffing is committed before demand; overtime is recourse after observing that day’s demand. There are no backlogs, inventory, induced demand, skill differences, absences or cross-week ramp requirements. Every unserved unit carries the stated shortage penalty. All dollar quantities are synthetic modeling assumptions, not labor-market prices. Source/data hashes are in `results/summary.json`.
