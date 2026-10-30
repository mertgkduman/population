---
spike: 013
idea: developmental-cultural-evolution
name: developmental-plasticity
type: comparison
validates: "Given state-preserving maturation and fixed cue accuracy, when adult encoding slows and the environment changes stochastically, then matched demographic, cultural and shared-environment invasion outcomes can be computed and verified"
verdict: VALIDATED
related: [009, 010, 011, 012]
tags: [v6, plasticity, stochastic-environment, culture, selection]
---

# Spike 013: developmental plasticity

## What This Validates

Run V6 rather than presume its outcome. Adult rigidity is specified as a lower encoding probability; deference and cognitive signal quality remain separate. Compare frozen, slower and equally plastic adults and matched random histories.

## Research

Continued installed Codex gsd-spike **--quick** workflow (Core 1.14.0), executed inline without helper agents or a project lifecycle. Runtime identity verified through the actual installed gsd-tools.cjs interface; the skill/workflow is the supported orchestration interface, not a guessed shell subcommand. No project config exists; default commit_docs=true applies, and the user explicitly requested local commits and no push.

| Approach | Advantage | Limitation | Decision |
|---|---|---|---|
| V5 two-ledger population equations, stage-specific encoding | Retains private/public distinction; exact cultural event averaging | Finite memory and imposed rigidity | Selected |
| Individual agent simulation | Rich histories | Adds sampling noise and duplicated scientific implementation | Deferred |
| Fixed environmental averages | Cheap equilibrium calculation | Misses lag and history under switches | Fixed-environment control only |

Reused V5 research and source. Primary context: [Acerbi et al. 2009](https://doi.org/10.1073/pnas.0908889106) openness/conservatism and [Maisonneuve et al. 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC11813578/) learning schedules. Neither establishes novelty for this extension. Numerical reference: [SciPy solve_ivp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html). Exact switch times avoid approximate per-step flip probabilities.

## How to Run

See [V6 README](../../../v6/README.md).

## What to Expect

An offline explorer with trait maps, stochastic trajectories, cultural distributions, matched controls and resident-relative invasion; the publication tab order is V1,V2,V3,V4,V5,Further work,V6.

## Observability

Predeclared contract, seeds, parameters, run/source hashes, solver settings, raw NPZ/CSV/JSON, numerical and browser evidence under v6. No push or deployment.

## Investigation Trail

2026-10-30: created local branch v6-plasticity-stochastic. Copied the V5 equations with an origin SHA; added probabilities of encoding a private cue while retaining unmodified query exposure costs. Wrote the contract before broad runs. Symmetric environments must not be reported as unequal abundance equilibria merely because labels differ.

## Results

**VALIDATED technically.** 9,504 homogeneous and 9,504 common-resident mutant trajectories, eight environmental paths per context, three adult encoding controls and four switching hazards. Held-out tests use 16 additional paths; 27 fixed equilibria converge. At fixed tau=3 and eta_A=.1, copying raises mean abundance in stable/slow environments but lowers it under rapid changes. The abundance-optimal maturation grid point moves from about3.37 to the minimum.5 as changes accelerate; d=1 is a boundary maximum in every main context, so no joint interior optimum was observed. Fixed opposite truths have mirrored beliefs and equal abundance. No special historical dogmatism adaptation is established.

27 numerical checks, 6 full-horizon refinement checks, 19 offline-browser interactions, 11 browser-export parity checks, 66 publication-browser checks and 28 static checks pass at the explicitly documented precision. The first 2e-6 private-accuracy target was narrowly missed; a third timestep confirms convergence and the 5e-6 probability target is justified and disclosed in verification.md. Raw diagnostic failure retained. Lossless NPZ repacking preserves all internal NPY bytes and keeps the built site below1GB. Local branch and commits only; do not push.


The publication tab order is verified as V1–V5, Further work, V6. Investigation continued through an actual offline Chrome run, a publication-server restart, full-horizon three-timestep convergence and source-byte archive verification. See [V6 verification](../../../v6/verification.md) and [findings](../../../v6/results.md).

The installed query-commit helper timed out while staging the large research-data folder. No commit was produced by that attempt. Native git staging/commit completes the same local artifact set and commit convention; no push is performed.
