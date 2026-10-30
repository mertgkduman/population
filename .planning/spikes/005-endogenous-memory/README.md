---
spike: 005
idea: developmental-cultural-evolution
name: endogenous-memory
type: comparison
validates: "Given state-preserving maturation, when juveniles internalize testimony, then adults retain cultural beliefs with measurable persistence"
verdict: PARTIAL
related: [001, 002, 003]
tags: [v4, culture, demography, selection]
---

# Spike 005: endogenous-memory

## What This Validates
Given state-preserving maturation, when juveniles internalize testimony, then adults retain cultural beliefs with measurable persistence. Technical verification and scientific hypothesis outcome are reported separately.

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
**PARTIAL.** Juvenile scores survive maturation and alter later adult advice; confidence persistence is conditional on the internalization mechanism.

At tau≈2.9225, d=0→1 increases adult accuracy .78369→.86158 and score persistence .21289→.31848. Public-only d=1 gives .78672 and .22004. Contradictory evidence always enters; permanent dogmatic refusal and genetic separability are not established.

Evidence: [verification](../../../v4/verification.md), [results](../../../v4/results.md), [source](../../../v4/experiments/ablations.py), and machine-readable JSON under v4/experiments. [Offline dashboard](../../../v4/research_dashboard.html).

The technical verdict concerns executable mechanisms and measured checks. It does not establish that childhood deference is a distinct historical adaptation.
