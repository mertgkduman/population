---
spike: 017
idea: developmental-cultural-evolution
name: local-context
type: comparison
validates: "Given procedure and local override coordinates, when corrected exploratory and fresh held-out regimes are compared, then contextual effects, sampled ties, and selected-candidate contrasts are reported without forcing an optimum"
verdict: PARTIAL
related: [014, 015]
tags: [v7, context, holdout, uncertainty]
---

# Spike 017: local context

## What This Validates

**Given** a 3×3 vector grid, scalar restriction, ordinary/asocial/learned comparators, and nine regimes, **when** raw discovery and held-out exports are paired by seed, **then** all per-regime 0→1 effects, class-specific sampled ties/boundaries, and fresh candidate contrasts are reproducible. No unique continuous optimum is imposed.

## Research

Executed via GSD quick task `261102-hyn --research --validate`. The 504-row discovery has only four seeds per cell and an L9 environment design with aliased interactions. The 1,368-row holdout has 24 fresh seeds per registered cell; asocial runs only at regimes 1, 5, and 9. A 288-row control makes d=0 source calibration depth-aware.

## How to Run

```bash
python -m unittest v7.tests.test_ecology v7.tests.test_confirm_extensions v7.tests.test_reporting
python v7/synthesize_results.py --verify-only
```

## What to Expect

Corrected selected vector `(d_procedure=.5,d_local=0)` minus ordinary net stock per agent-season ranges −0.001000 to +0.001478 across regimes, with paired MCSE 0.000892–0.001707; paired mean-N differences range −0.390 to +0.448. Depth-aware d=0 remains close at the three sentinels. Corrected raw hashes: discovery `ae2e130c08df484d6f6605d59f489886ecc025dcdbec4c89049c7d0306381341`; holdout `5956bde27a901f99f6520d3c5d227a6da1069fa3f86d586785ae6f46b383e5e0`; depth control `3badd2572da962f2b48cea6066bed72aed5f2490a0cf7dc15bfc0064c9e041d6`. Frozen raw remains an invalidated provenance layer.

## Observability

Per-seed N/net-resource rows, policy/regime IDs, paired MCSE, exploratory class tables, and rate diagnostics. Event numerator/denominator counts are absent, so Wilson rate precision remains unresolved.

## Investigation Trail

2026-11-02: recomputed all 54 coordinate contrasts, 27 class/regime sampled tops, every held-out candidate contrast, and depth-aware controls directly from gzip exports.

## Results

**PARTIAL.** Fresh corrected-overlay discovery and holdout restore a valid implemented no-teacher/asocial path. Local override is often negative for exploratory mean N; class-specific sampled tops/ties vary by regime; the pooled net-resource freeze selects vectors `(.5,0)` and `(1,0)` plus scalar `.25`; repaired asocial sentinels exceed ordinary for N and net stock in the three tested regimes. Four discovery seeds, L9 aliasing, missing event counts, objective dependence, and sign-changing held-out vector contrasts prohibit equivalence, a unique optimum, general policy benefit, or adaptation claims.
