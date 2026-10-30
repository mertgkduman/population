# v3: time-coupled copying and adult advice quality

Open [index.html](index.html) directly in a browser. The Plotly bundle, model code, and precomputed summaries are embedded; the dashboard requires no server or network access. It uses exactly two demographic ODE states: nonreproducing followers `F` and reproductive adults `A`, with irreversible maturation. The copied adult feature `Q(t)` is a prescribed quality modifier, not an additional state or a model of individual adult learning.

`v3-time-coupled-copying` branches from `v2-advice-drift`; `main` contains the v1 baseline. The scientific specification and predeclared checks are in [EXPERIMENTS.md](EXPERIMENTS.md); measured interpretation is in [FINDINGS.md](FINDINGS.md). All outcomes are hypothetical simulation data.

## Reproduce

Python 3.12 with NumPy, SciPy, and Plotly is required; exact observed versions and tolerances are in `run_manifest.json`. Node.js is used for JavaScript parity and browser tests. The full sweep is computationally substantial.

```bash
cd v3
python run_experiments.py
node parity.js
python verify.py
CHROME_BIN=/path/to/chrome node browser_verify.js
python finalize.py
```

The browser test's default Chrome path is the path used in this workspace; set `CHROME_BIN` on another machine. `finalize.py` records file hashes and rebuilds the downloadable archive in the repository root. A fresh sweep creates a new run identifier and replaces v3 outputs only.

To extract a complete CSV from the compressed sweep without rerunning it:

```bash
python export_slice.py --scenario helpful --policy copy --model M0 --lambda-d 0.005 --lambda-Q 0.005 --horizon 200 --out my_slice.csv
```

`sweep.npz` contains `F`, `A`, `N`, and `r_T` with axes `(scenario, policy, model, λd, λQ, d0, tau, horizon)`. Its coordinate arrays and run ID are included. `summary.csv/json` provides 980 context summaries; `selected_slices.csv` gives four full 21×21 trait grids per scenario/policy/model; `refined_summary.csv/json` reports 41×41 refinement in selected contexts; `representative_series.csv` contains time-resolved states, fluxes, and behavior; `fixtures.json` is the shared SciPy/browser comparison set. `sample_slice.csv` demonstrates a full export.

The dashboard offers a clickable d0×tau outcome map, λd×λQ rate map, 3D surface, five additional time-series/trajectory views, animation and scrubbing, matched independent-population pins, scenario and policy controls, parameter import/export, map and series exports, chunked numerical maps with cancel/restart, and a responsive offline layout. `science.js` is the browser numerical implementation; `model.py` is the SciPy reference. `dashboard_template.html` and `app.js` generate the single-file `index.html` via `run_experiments.py`.
