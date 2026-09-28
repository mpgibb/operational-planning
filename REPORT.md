# Research report: Operational planning under uncertainty

## Executive summary

**Lower staffing cost comes with a service decision.**

The uncertainty-aware plan reduced simulated 52-week cost by $59,028 (7.0%) versus the buffer rule. It served 99.38% of demand, versus 99.83% for the buffer rule.

Decision implication: Set an acceptable service floor, validate shortage costs, then test the schedule in shadow mode before operational use.

Key caution: After a sudden sustained demand increase, the estimated savings fell to about $80 per week and the interval included zero. This is a one-site synthetic study with simplified labor constraints.

All findings describe synthetic data. They are not client results. Independent technical review remains pending.

## Decision and design

Lock seven days of regular staffing for a single service site, then use limited daily overtime after demand is observed. Choose a feasible plan under a weekly staffing budget and daily ramp limits, with explicit costs for labor and unserved requests.

A complete rolling forecast-and-decision evaluation over 156 synthetic weeks, with 52 final test weeks. All policies obey the same daily staffing bounds, weekly worker-day budget and within-week ramp limits. The optimizer is checked against exhaustive enumeration on small cases.

## Method

Fit a regularized trend/seasonal/recent-level model at each weekly cutoff. Add up to 52 past weekly error vectors to the new forecast, retaining within-week error dependence. Minimize expected labor plus shortage cost with exact dynamic programming over day, cumulative worker-days and previous-day staffing. Evaluate all feasible overtime choices as daily recourse. Compare the realized decisions with practical baselines under identical constraints.

- Compare ridge demand forecasts with seasonal-naive forecasts using only information available before each week.
- Evaluate a projected 20% buffer rule, point-forecast optimization and stochastic planning on the same held-out weeks.
- Report realized cost, service, shortages, overtime and unused capacity; use a perfect-information lower bound, demand-shock tests and shortage-cost sensitivity.

## Evaluated results

All policies share the same staffing bounds, weekly budget, within-week ramp and overtime choices. Perfect information sees held-out demand and is a lower bound, not an implementable policy. Savings intervals compare paired weekly costs using a four-week circular moving-block bootstrap (1,000 draws).

### stable

| Policy | 52-week cost | Demand served | Shortage units | Regular worker-days | Overtime worker-days | Mean weekly savings | 95% savings interval |
|---|---:|---:|---:|---:|---:|---:|---|
| buffer_rule | $848,316.00 | 99.83% | 124 | 6974 | 47 | $0.00 | $0.00 to $0.00 |
| point_plan | $791,208.00 | 99.46% | 407 | 6281 | 154 | $1,098.23 | $782.26 to $1,411.88 |
| stochastic_plan | $789,288.00 | 99.38% | 462 | 6176 | 206 | $1,135.15 | $804.66 to $1,473.70 |
| perfect_information | $764,904.00 | 99.40% | 451 | 6239 | 30 | $1,604.08 | $1,222.77 to $1,967.15 |

Model WAPE: 6.00%; seasonal-naive WAPE: 7.32%; nominal 80% demand interval coverage: 73.63%.

| Shortage penalty | Re-optimized cost | Demand served | Regular worker-days | Overtime worker-days |
|---|---:|---:|---:|---:|
| $12.00 | $768,732.00 | 92.73% | 5860 | 0 |
| $24.00 | $789,288.00 | 99.38% | 6176 | 206 |
| $48.00 | $795,492.00 | 99.83% | 6233 | 231 |

Costs use a different definition in each penalty row; cross-row differences are not savings estimates.

### surge

| Policy | 52-week cost | Demand served | Shortage units | Regular worker-days | Overtime worker-days | Mean weekly savings | 95% savings interval |
|---|---:|---:|---:|---:|---:|---:|---|
| buffer_rule | $965,184.00 | 99.08% | 826 | 7020 | 572 | $0.00 | $0.00 to $0.00 |
| point_plan | $968,448.00 | 98.90% | 992 | 6951 | 614 | $-62.77 | $-169.68 to $55.66 |
| stochastic_plan | $961,032.00 | 99.06% | 843 | 6931 | 606 | $79.85 | $-13.66 to $157.41 |
| perfect_information | $948,468.00 | 99.10% | 812 | 6933 | 539 | $321.46 | $196.77 to $459.46 |

Model WAPE: 6.88%; seasonal-naive WAPE: 7.62%; nominal 80% demand interval coverage: 70.88%.

| Shortage penalty | Re-optimized cost | Demand served | Regular worker-days | Overtime worker-days |
|---|---:|---:|---:|---:|
| $12.00 | $924,972.00 | 89.76% | 6786 | 0 |
| $24.00 | $961,032.00 | 99.06% | 6931 | 606 |
| $48.00 | $972,384.00 | 99.62% | 6948 | 680 |

Costs use a different definition in each penalty row; cross-row differences are not savings estimates.

### volatile

| Policy | 52-week cost | Demand served | Shortage units | Regular worker-days | Overtime worker-days | Mean weekly savings | 95% savings interval |
|---|---:|---:|---:|---:|---:|---:|---|
| buffer_rule | $875,388.00 | 99.50% | 382 | 6854 | 243 | $0.00 | $0.00 to $0.00 |
| point_plan | $840,552.00 | 99.21% | 603 | 6359 | 350 | $669.92 | $447.68 to $903.80 |
| stochastic_plan | $836,736.00 | 99.13% | 669 | 6215 | 416 | $743.31 | $503.28 to $998.84 |
| perfect_information | $789,648.00 | 99.33% | 512 | 6226 | 168 | $1,648.85 | $1,294.23 to $2,035.22 |

Model WAPE: 11.73%; seasonal-naive WAPE: 14.31%; nominal 80% demand interval coverage: 58.79%.

| Shortage penalty | Re-optimized cost | Demand served | Regular worker-days | Overtime worker-days |
|---|---:|---:|---:|---:|
| $12.00 | $801,996.00 | 88.47% | 5800 | 0 |
| $24.00 | $836,736.00 | 99.13% | 6215 | 416 |
| $48.00 | $848,292.00 | 99.67% | 6303 | 443 |

Costs use a different definition in each penalty row; cross-row differences are not savings estimates.

The stochastic plan’s stable savings come with lower service than the buffer rule. The demand-surge savings interval includes zero. Daily prediction intervals under-cover in the stable scenario, and neither prediction accuracy nor this selected cost function determines an acceptable service standard. The modest gap to the point-forecast plan should not be presented as evidence that all elaborate optimization is worthwhile.

## Assumptions and limitations

- Regular staffing is 8–26 workers daily, at most 135 worker-days weekly, and changes by at most four workers between adjacent days within a week.
- One worker supplies 12 units per day. Regular cost is $120 per worker-day; up to five overtime workers cost $180 each; unserved units cost $24 each.
- No cross-week ramp, skill mix, labor-law, absence, shift-length or multisite constraints are modeled.
- All demand and calibration errors available to a plan occur before its cutoff. The perfect-information planner is an evaluator-only benchmark.

This completed simulation does not establish actual cost savings or staffing feasibility for an employer. Marginal 80% demand intervals cover only 73.6% of stable held-out days, and shifts can degrade performance. The four-week block-bootstrap cost interval describes one synthetic history. A lower-cost plan may deliver lower service; neither forecast accuracy nor cost alone is a sufficient operating criterion.

## Reproduction and checks

Run the README commands. Nine tests pass, including hand-calculated or exhaustive fixtures, temporal leakage attempts and seeded determinism. The protocol, configuration, lockfile, model code, detailed evaluation CSVs and content hashes are included. No favorable seeds were selected after seeing results. Numerical libraries are pinned; stored results round to six decimal places to make reproduction portable.

## Next practical step

Agree on a service floor, shortage economics and actual staffing constraints with an operating owner. Backtest an authorized demand history and run a shadow schedule before changing staff assignments.

## Method references

- [Hyndman & Athanasopoulos — time-series cross-validation](https://otexts.com/fpp3/tscv.html)
- [Hyndman & Athanasopoulos — prediction intervals](https://otexts.com/fpp3/prediction-intervals.html)

These references motivate the design; this implementation does not claim their complete estimators or theoretical guarantees.
