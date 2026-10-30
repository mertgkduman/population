---
spike: 001
idea: deference-demography
name: deference-demography
type: standard
validates: "Given the specified two-state model, when d and tau vary, then analytic and numerical outcomes agree and an offline dashboard exposes them"
verdict: VALIDATED
related: []
tags: [demography, numerical, dashboard]
---

# Spike 001: Deference, maturation, and population fitness

## What This Validates

Given the controlling specification in `../../../DEFERENCE_GSD_SPIKE_PROMPT.md`, when follower deference and mean maturation waiting time vary under fixed within-scenario advice and demographic parameters, then the two-state analytic and numerical outputs agree and can be inspected in a working offline dashboard. **VALIDATED is a technical verdict about the implemented experiment and checks, not a biological adaptation claim.**

## Research

The installed `gsd-spike` skill and `workflows/spike.md` (GSD Core 1.14.0) were read before execution. Its documented `--quick` mode skips idea decomposition and alignment while retaining the predeclared hypothesis, research, verification, investigation trail, README, and manifest. The workflow was applied through the installed Codex skill interface; no shell command named `gsd-spike` was claimed or run.

| Approach | Tool | Advantage | Constraint | Choice |
|---|---|---|---|---|
| Analytic low-density and equilibrium maps | NumPy / browser formulas | Fast, transparent, no integration error | Restricted to specified outcomes | Primary |
| High-accuracy trajectories | SciPy `solve_ivp` DOP853 | Independent numerical reference | Python needed to regenerate | Reference |
| Offline interactive trajectories/maps | Plain JS RK4 + embedded Plotly | Single-file browser use | Finite step error; checked against SciPy | Dashboard |

Sources: [Open GSD spike guide](https://github.com/open-gsd/gsd-core/blob/next/docs/how-to/spike-and-sketch.md), [SciPy solve_ivp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html), [Plotly offline use](https://plotly.com/javascript/is-plotly-free/), [Plotly click events](https://plotly.com/javascript/click-events/). Background context: [Deffner and McElreath 2022](https://doi.org/10.1371/journal.pone.0267204); [de Roos 2018](https://doi.org/10.1007/s12080-018-0374-3). The equations and parameter values here are specified assumptions, not estimates drawn from those papers.

## How to Run

Open `index.html` directly in a modern browser. No server, account, key, or network is needed. The single HTML embeds Plotly and the exact `science.js` source.

To regenerate and verify the saved data with the versions in `requirements.txt`:

```sh
python run_spike.py
node browser_verify.js
python finalize.py
```

The browser check uses the included Chrome for Testing path in this environment; adapt that path if running elsewhere. `node parity.js` is called by `run_spike.py` and requires Node 24 for the browser harness only. The dashboard itself is plain JavaScript.

## What to Expect

The default helpful-advice, M0 copying heatmap favors larger d and τ=0.5, the lower grid boundary. Switch to M1 to inspect the prescribed preparation tradeoff; switch to equal, cloned, noisy, biased, and no-effect advice to see null and adverse results. `FINDINGS.md` gives the measured interpretation.

## Observability

The dashboard exposes calculation status, missing-cell counts, run ID in exports, a cancel control, selected trajectory and fluxes, and a quasi-extinction threshold. `browser_verification.json` logs browser checks and console errors. `run_manifest.json` records versions, settings, timestamps, and hashes.

## Investigation Trail

1. Created `CHECKS.md` before running the model or sweep. Kept the one-spike `--quick` scope and exactly two ODE states.
2. Implemented the shared `schema.json`, Python reference, and browser `science.js`. Generated 51×61 analytic maps for all six scenarios, both policies, and both maturation assumptions; generated a 25×25 finite-horizon map for each maturation model under default helpful copying.
3. First checks exposed a test-design error: the `no_effect` preset changes k_error, so it cannot be used to isolate adult-moment changes at d=0. Corrected the check to compare only presets with fixed k_error; kept a separate k_error=0 null check. The model was not tuned.
4. Compared browser RK4 against SciPy DOP853 at 12 trait/policy/model fixtures and half the RK4 step, both in Node and in offline Chrome. Added analytic JS/Python parity for loss, mortality, r0, equilibrium, and self-invasion.
5. Ran Chrome from `file://` with HTTP(S) blocked. Exercised animation, scrubbing, heatmap click, resident invasion, pins, scenario invariance, M0/M1 and policy controls, import/export, cancellation, resize, and console logging. All recorded checks passed.
6. Invoked the installed GSD `query commit` step for the spike artifacts and manifest. It returned `committed: false`, `reason: staging_failed` because the workspace is not a Git repository. No repository was initialized for this spike.

## Results

**Technical verdict: VALIDATED.** The recorded scientific and browser checks pass. The primary M0 τ optimum is a lower grid boundary; M1 has an interior τ optimum only under its imposed preparation benefit. Equal, cloned, and no-effect scenarios preserve null results; noisy/biased copying can make deference harmful. See `FINDINGS.md` and the machine-readable verification files.

This directory is not inside a Git repository. The installed GSD commit step was attempted but could not create a commit; the manifest and artifacts are preserved on disk. No new-project cycle or deployment was run.
