# V6: developmental plasticity in stochastic environments

This version adds a prescribed age difference in private learning: juveniles encode each private cue with probability 1 and adults with probability 0.1 by default. Adults retain both private evidence and held conviction at maturation, and advise juveniles from their acquired beliefs. Private cue accuracy and exposure are identical across ages and inherited deference traits. Adults with zero and unit plasticity provide frozen and equal-plasticity controls.

Environmental truth flips at exact Poisson event times with rate kappa. Stable ± environments are sign-symmetric, so they have mirrored cultural equilibria with equal abundance. Nonzero switching produces fluctuating regimes; finite-window averages are not automatically stationary equilibria.

Open [index.html](index.html) directly for the offline dashboard. The publication site places V6 after V5 and Further work, preserving Further work immediately next to V5. Its controls explore saved simulations; no browser backend or network access is needed for the standalone file.

## Reproduce

From the repository root, using the existing NumPy, SciPy, Numba and Plotly environment:

```bash
OPENBLAS_NUM_THREADS=1 python v6/experiments/run_experiments.py
OPENBLAS_NUM_THREADS=1 python v6/experiments/followups.py
OPENBLAS_NUM_THREADS=1 python v6/experiments/fixed_equilibria.py
OPENBLAS_NUM_THREADS=1 python v6/experiments/verify.py
python v6/experiments/pack_npz.py
python v6/experiments/analyze_results.py
python v6/build_dashboard.py
node v6/browser_verify.js
python scripts/make_readme.py
python scripts/build_pages.py
python scripts/verify_pages.py
```

The Node browser harness needs Chrome; `CHROME_BIN` overrides its documented runtime path. The scientific runs do not need Chrome. Dependency versions and solver tolerances are recorded in experiments/run_manifest.json and verification.json. No API key or new dependency is required.

## Files and interpretation

- [Mathematical model](mathematical_model.md), [predeclared contract](research_contract.md), [parameter schema](parameter_schema.json).
- [Measured results](results.md), [verification](verification.md).
- experiments/sweep.csv: every seed × trait × context outcome; environment_paths.json: exact switches; NPZ files: all saved series, distributions and raw per-path outcomes.
- `numpy.load('v6/experiments/adult0p1_k0p05.npz')` reads the raw data. NPZ archives may use ZIP_LZMA to keep publication under hosting limits. This is lossless: exact internal NPY member hashes are checked and recorded in storage_verification.json. No scientific values are rounded by repacking. Dashboard JSON rounds to nine decimal places for display; NPZ arrays retain full numerical precision.
- Held-out seeds, within-adult cohort diagnostics and 27 fixed-equilibrium controls are separate exported experiments. No stochastic significance tests or invented deterministic confidence intervals are used.
- Raw displayed-data ZIPs appear beneath every interactive figure. Reference packages retain the full model/configuration and raw experiment records. Time series exports identify the run and context; configuration export supplies all units and solver settings.

A finite-window mutant growth advantage is conditional on a fixed resident genotype, resident teachers/resources and a common stochastic environment. It does not prove fixation or an ESS. Isolated population maxima do not establish natural selection. Adult rigidity is specified, not shown to evolve, and positive deference effects can be ordinary information transfer. No historical adaptation is validated by this implementation.

V1–V5 scientific source/data remain unchanged. The user subsequently authorized publication. The [situational-advice extension](situational_advice/README.md) adds noisier adult observations of juvenile-specific situations and preserves this original baseline as a separate selectable experiment.
