---
spike: 016
idea: developmental-cultural-evolution
name: procedures-cost
type: comparison
validates: "Given paid procedural learning and equal aggregate-work cognitive controls, when corrected fresh-seed assays run, then procedural feasibility and comparator limits are measured without claiming demographic cumulative culture"
verdict: PARTIAL
related: [015]
tags: [v7, procedure, cost, cumulative, budget]
---

# Spike 016: procedures and cost

## What This Validates

**Given** paid messages, computation, material ledgers, and a corrected 144-row cognitive assay, **when** procedure/cost controls are recomputed, **then** all six arms use aggregate work 360 and material debit 3.6 and two-edge functional procedures can be counted. This does not establish a feasible individual-budget solver or demographic cumulative culture.

## Research

Executed through GSD quick task `261102-hyn --research --validate`; no standalone spike workflow was invoked. The earlier cumulative export is retained as invalidated. Fresh seeds 74601–74624 correct the obvious aggregate-budget mismatch. The ideal pooled upper bound nevertheless permits per-learner private work above 60 and compensating negative safe work, so it is not a feasible matched comparator. Shuffled prerequisites remain close to the main arm.

## How to Run

```bash
python -m unittest v7.tests.test_cumulative v7.tests.test_reporting
python v7/synthesize_results.py --verify-only
```

## What to Expect

Tests and raw parity pass. Corrected raw hash: `20da7626013cc43a430604847115ccd421a12cb385c58aca60dd665615def599`; cumulative source hash: `2928a86ac424fd910295ce44e3fbda5d5149d1a149f7a95ea10f9905f4136bef`.

## Observability

Per-arm work/material totals, useful depth, functional score, two-edge counts, upper-bound flag, invalidation record, and explicit claim limit.

## Investigation Trail

2026-11-02: independently read corrected source and raw rows; confirmed equal aggregate totals and 28 two-edge procedures, then found the individual-budget defect in the pooled upper-bound arm.

## Results

**PARTIAL.** The corrected assay is a useful cognitive feasibility check. It does not complete ACCUM-01, prove causal prerequisite accumulation, couple to demography/selection, or support H2.
