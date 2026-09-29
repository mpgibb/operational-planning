# Operational planning under uncertainty

Completed reproducible synthetic study · Python 3.11.16 · NumPy 2.2.6 · SciPy 1.17.1

Case study: https://michaelpgibb.com/projects/operational-planning

## Executive summary

**Lower staffing cost comes with a service decision.**

The uncertainty-aware plan reduced simulated 52-week cost by $59,028 (7.0%) versus the buffer rule. It served 99.38% of demand, versus 99.83% for the buffer rule.

Decision implication: Set an acceptable service floor, validate shortage costs, then test the schedule in shadow mode before operational use.

Key caution: After a sudden sustained demand increase, the estimated savings fell to about $80 per week and the interval included zero. This is a one-site synthetic study with simplified labor constraints.

All findings describe synthetic data. They are not client results. Independent technical review remains pending.

## Reproduce

```bash
git clone https://github.com/mpgibb/operational-planning.git
cd operational-planning
uv sync --frozen
uv run python -W error -m unittest discover -s tests -v
uv run python -W error study.py
git diff --exit-code -- data results
```

The frozen `uv.lock` resolves the pinned numerical libraries. The pipeline requires no credentials, paid data or network calls after environment setup. Correctness tests cover numerical fixtures, information timing and decision constraints. Running the study regenerates every CSV and `results/summary.json` from `config.json`. Monetary and probability outputs are rounded to six decimal places when serialized; forecast comparisons use the unrounded calculations.

## Research materials

- [PROTOCOL.md](PROTOCOL.md): question, models, baselines, timing and evaluation design recorded before evaluation.
- [DATA.md](DATA.md): units, schema, observation windows and permitted model inputs.
- [REPORT.md](REPORT.md): complete comparisons, robustness, practical implications and limits.
- `study.py` and `common.py`: generator, model, evaluator and numerical/provenance utilities.
- `tests/`: hand-calculated and adversarial correctness checks.
- `data/`: original generated observations; evaluator-only oracle files where applicable.
- `results/`: detailed predictions/decisions and machine-readable summaries, including source/data SHA-256 hashes.

## Scope and use

This completed simulation does not establish actual cost savings or staffing feasibility for an employer. Marginal 80% demand intervals cover only 73.6% of stable held-out days, and shifts can degrade performance. The four-week block-bootstrap cost interval describes one synthetic history. A lower-cost plan may deliver lower service; neither forecast accuracy nor cost alone is a sufficient operating criterion.

Agree on a service floor, shortage economics and actual staffing constraints with an operating owner. Backtest an authorized demand history and run a shadow schedule before changing staff assignments.

The synthetic data are original study materials and contain no customer or employer records. No original source/data reuse license has been selected; public availability permits inspection but does not itself grant reuse rights. Numerical libraries retain their own licenses and are installed from the lockfile, not vendored here.
