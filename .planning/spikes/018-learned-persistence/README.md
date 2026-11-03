---
spike: 018
idea: developmental-cultural-evolution
name: learned-persistence
type: comparison
validates: "Given a separate learned-action process with B/K/T/H exports, when audience, outcome, contingency, audit, and counterevidence probes run, then action persistence is distinguished from factual belief and unsupported norm claims"
verdict: PARTIAL
related: [010, 015]
tags: [v7, persistence, habit, belief, norms]
---

# Spike 018: learned persistence

## What This Validates

**Given** a generic post-freeze reinforcement process, **when** five probes run over 24 seeds, **then** learned action value H can persist while factual B revises and adult genetic override remains zero. This is not private-belief dogmatism or an obligation mechanism.

## Research

Executed through GSD quick task `261102-hyn --research --validate`; no independent spike workflow was invoked. The 120 rows come from a separate synthetic process, not the frozen IBM. `intervention_seasons=20` is metadata rather than 20 sequential update iterations; the advertised bidirectional probe applies one evidence direction. The free-audit change affects reported checking cost only.

## How to Run

```bash
python -m unittest v7.tests.test_postfreeze v7.tests.test_reporting
python v7/synthesize_results.py --verify-only
```

## What to Expect

All probes preserve the explicit B/K/T/H exports and zero direct adult override. Raw hash: `90f787821b5ef91d509e066c6c7f97c413bbfabb48bd9a33086f1e18ae522c99`; postfreeze source hash: `e34d7bd30ccf2490a5ecc8d716c83da5c65f3330825146406e56366c8c157035`.

## Observability

Seed/probe, action persistence, H, B revision, K, T, checking cost, evidence count, audience/tutor/reward/sanction flags, and explicit construct label.

## Investigation Trail

2026-11-02: read source rather than relying on probe names; separated public action habit from private factual posterior and identified absent symmetric/no-habit comparators.

## Results

**PARTIAL.** Generic acquired action persistence with factual revision is measured. Dogmatism is NULL/unsupported, obligation is unsupported, H4 is not modeled, and no demographic persistence conclusion follows.
