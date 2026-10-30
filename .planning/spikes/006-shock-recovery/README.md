---
spike: 006
idea: developmental-cultural-evolution
name: shock-recovery
type: comparison
validates: "Given environmental reversal, when equally capable strategies respond, then private belief and public behavior recover on measurable timescales"
verdict: VALIDATED
related: [001, 002, 003]
tags: [v4, culture, demography, selection]
---

# Spike 006: shock-recovery

## What This Validates
Given environmental reversal, when equally capable strategies respond, then private belief and public behavior recover on measurable timescales. Technical verification and scientific hypothesis outcome are reported separately.

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
**VALIDATED.** Endogenous memory delays measured recovery; rapid switching supplies a counterexample to unconditional benefit.

Matched-baseline half-recovery at tau≈2.9225 is 10 time units for d=0 and 20 for d=1 (5-unit observation resolution). Six-history rate sensitivity reverses the mean deference advantage at switching interval20. Absolute-.75 recovery is retained separately because it confounds baseline accuracy. This validates implementation and conditional recovery measurements, not universal predictions.

Evidence: [verification](../../../v4/verification.md), [results](../../../v4/results.md), [source](../../../v4/experiments/postprocess.py), and machine-readable JSON under v4/experiments. [Offline dashboard](../../../v4/research_dashboard.html).

The technical verdict concerns executable mechanisms and measured checks. It does not establish that childhood deference is a distinct historical adaptation.
