---
spike: 007
idea: developmental-cultural-evolution
name: shared-culture-invasion
type: comparison
validates: "Given a resident cultural environment, when a rare inherited trait enters, then its growth uses the same teachers and resources"
verdict: VALIDATED
related: [001, 002, 003]
tags: [v4, culture, demography, selection]
---

# Spike 007: shared-culture-invasion

## What This Validates
Given a resident cultural environment, when a rare inherited trait enters, then its growth uses the same teachers and resources. Technical verification and scientific hypothesis outcome are reported separately.

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
**VALIDATED.** Rare mutants share resident culture and resources; explicit competition confirms a selection–abundance mismatch.

A refined candidate d=1,tau≈.74655 has no positive invader among1281 sampled traits, a finite-domain result, not an ESS proof. It invades d=1,tau≈3.1922 at rate+.0010006 and replaces that lineage in the shared-culture simulation. Equilibrium N falls about6%, while low-density growth increases. Self-invasion is numerically zero; a resource-perturbation negative control makes it nonzero.

Evidence: [verification](../../../v4/verification.md), [results](../../../v4/results.md), [source](../../../v4/experiments/evolution.py), and machine-readable JSON under v4/experiments. [Offline dashboard](../../../v4/research_dashboard.html).

The technical verdict concerns executable mechanisms and measured checks. It does not establish that childhood deference is a distinct historical adaptation.
