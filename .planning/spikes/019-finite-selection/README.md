---
spike: 019
idea: developmental-cultural-evolution
name: finite-selection
type: comparison
validates: "Given paired mutant and neutral-tag births in one resident prefix, when fixed complete seed batches run for 80 seasons, then finite living-descendant differences and unconditional denominators are measured without asymptotic claims"
verdict: PARTIAL
related: [007, 011, 015]
tags: [v7, lineage, selection, descendants, censoring]
---

# Spike 019: finite selection

## What This Validates

**Given** the same resident prefix and born ID for mutant and neutral-tag arms, **when** 80-season lineage trajectories execute in fixed seed batches, **then** paid-birth, zero, extinction, cap, and no-birth denominators and paired living-descendant differences can be recomputed. This is not direct competition or asymptotic invasion.

## Research

Executed through GSD quick task `261102-hyn --research --validate`; no separate `gsd-spike` shell workflow was invoked. The frozen 1,242-row assay is retained as an invalidated failure trail. The separately registered corrected-overlay run has 2,112 fresh paid-birth arm rows, all in wholly completed fixed batches (1,056 pairs), with zero incomplete, no-birth, and cap rows. Finite lineage extinction occurs in 1,846 arm rows and remains in the unconditional denominator.

## How to Run

```bash
python -m unittest v7.tests.test_selection v7.tests.test_reporting
python v7/synthesize_results.py --verify-only
```

## What to Expect

Twelve directed regime contrasts each have 88 paired paid births. Mean mutant-minus-neutral living descendants range −0.239 to +0.568. Maximum paired MCSE is 0.226 and maximum arm-level establishment Wilson half-width is 0.097, satisfying the registered 0.25/0.10 numerical-precision rule. Corrected raw hash: `bbaba43758311955eb5ad24fed294e201a77dd0032c6f5622e277c157c97775e`; corrected lineage source hash: `1f67409eb7699fec11f1e172064addc7cac0a1011560c87363090ae54eaa3b63`; overlay hash: `7f60d4014649d18f1940a4296f9cc113a82576c4176ac7f6d3876f0bd3ea0b92`.

## Observability

Born/parent IDs, paid energy transfer, blank birth, teacher-pool summary, total/living/dead descendants, finite extinction, cap/no-birth flags, frequency trajectory, ledger residual, and replay digest.

## Investigation Trail

2026-11-02: reproduced the frozen contamination, registered the corrected source snapshot and ecology-freeze parent before outcomes, then ran fixed eight-seed extensions through seed 79088. Source identities, all complete batches, paired gates, and raw/result hashes match.

## Results

**PARTIAL with valid corrected finite endpoints.** The fresh overlay-based continuations remove the frozen local oracle and pass the declared numerical-precision gates. They provide conditional T=80 carrier outcomes only. Numerical precision is not significance/equivalence, direct competition, rare-mutant invasion, fixation, ESS, stable polymorphism, or proof of a selection attractor.
