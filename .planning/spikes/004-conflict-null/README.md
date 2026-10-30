---
spike: 004
idea: developmental-cultural-evolution
name: conflict-null
type: comparison
validates: "Given exogenous source quality, when d varies, then analytical conflict accuracy and demographic limits match numerical solutions"
verdict: VALIDATED
related: [001, 002, 003]
tags: [v4, culture, demography, selection]
---

# Spike 004: conflict-null

## What This Validates
Given exogenous source quality, when d varies, then analytical conflict accuracy and demographic limits match numerical solutions. Technical verification and scientific hypothesis outcome are reported separately.

## Research
See ../../../v4/literature_review.md and model_comparison.md. Primary literature and competing approaches were reviewed by independent research/modeling/adversarial roles before broad experiments.

## How to Run
`OPENBLAS_NUM_THREADS=1 python v4/experiments/run_experiments.py` and the corresponding verification/evolution scripts documented in v4/README.md.

## What to Expect
Open v4/research_dashboard.html offline; inspect precomputed maps, trajectories and selection data.

## Observability
Run log, configuration, seeds, CSV/NPZ and JSON evidence under v4/experiments.

## Investigation Trail
2026-10-30: invoked installed Codex gsd-spike --quick workflow, inspected previous experiments, read research, documented hypotheses, ran pilot before broad sweep.

2026-10-30 investigation continued: compared main internalization against public-only, memoryless, private, oracle and feedback learners; ran pilot before factorial sweeps and seed replication. Adversarial review corrected equilibrium residual timing, recovery baselines, private-sampling labels, and coarse-optimum interpretation. A final independent audit replaced invalid coarse-quadrature survival with a conditional transient-operator calculation; demographic trajectories and invasion results were unaffected. Offline browser and export checks cover the final rendered data.

## Results
**VALIDATED.** The fixed-culture accuracy identity and neutral information controls match the generator; pure maturation conserves density.

Exact conflict-choice and equal-accuracy checks have zero discrepancy. Matrix-exponential parity has scaled error 3.10e-10. No-payoff d demographic error is 2.84e-13. These are mathematical consequences, not evidence of a historical adaptation.

Evidence: [verification](../../../v4/verification.md), [results](../../../v4/results.md), [source](../../../v4/experiments/test_verification.py), and machine-readable JSON under v4/experiments. [Offline dashboard](../../../v4/research_dashboard.html).

The technical verdict concerns executable mechanisms and measured checks. It does not establish that childhood deference is a distinct historical adaptation.
