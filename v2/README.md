# v2: signed adult-advice quality drift

This branch extends the committed `main`/`v1` baseline. `v1/` remains the frozen, verified constant-advice experiment; `v2/` is a separate self-contained experiment with improving **or decaying** adult advice precision. Both retain two demographic ODE states, followers `F` and adults `A`, with irreversible maturation. Adults still supply advice; followers vary deference `d` from 0 to 1.

## Mechanism

`sigma_A(t)=clamp[sigma_A(0) exp(-g t), sigma_floor, sigma_ceiling]` with default bounds 0.1 and 3.0. A positive rate `g` improves adult precision, a negative rate degrades it, and `g=0` reproduces v1. Adult bias and private ability remain fixed within a scenario. The quality trajectory is an externally specified population-wide approximation, not an adult-age or cultural-learning state. The policy losses and M0/M1 maturation assumptions are unchanged from v1. See `EXPERIMENTS.md` for the predeclared matrix and checks.

The system is nonautonomous when `g≠0`. The dashboard therefore emphasizes finite-horizon `r_T`, N(T), matched `Δr_T`, and trajectories. `r_inst(t)` is only the frozen-time low-density eigenvalue; a single stationary r₀, N*, or conditional invasion eigenvalue is not used for drifting advice.

## Open and rerun

Open [index.html](index.html) directly in a modern browser, offline. The HTML embeds Plotly, the parameter schema, the exact `science.js` solver, and the experiment summary. No server or key is needed.

With Python, Node 24, and the versions in `requirements.txt`:

```sh
python run_experiments.py
python verify.py
node browser_verify.js
python finalize.py
```

`browser_verify.js` uses this environment's Chrome for Testing path; adapt the path elsewhere. The dashboard itself does not need Node or Chrome.

## Results and reproducibility

- `schema.json`: defaults, advice presets, grid, signed rates, horizons, and solver settings.
- `model.py`, `science.js`: readable Python reference and the exact browser model.
- `run_experiments.py`, `verify.py`, `parity.js`, `browser_verify.js`: data generation and checks.
- `sweep.csv/json`: 64,152 finite-horizon records from 21,384 trait trajectories.
- `refined_sweep.csv/json`: 1,875 additional 25×25 trait runs.
- `representative_series.csv/json`, `fixtures.json`: selected trajectories and SciPy references.
- `verification.json`, `browser_verification.json`, `run_manifest.json`: measured results, versions, timestamps, and hashes.
- `FINDINGS.md`: mathematical, assumption-sensitive, null, negative, boundary, and limitation findings.

**Technical status: verified.** This means the implementation and specified checks passed. It does not establish historical selection for childhood, social deference, or obedience. No public deployment was made.
