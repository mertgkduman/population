# V4 developmental deference research

Open **research_dashboard.html** directly in a modern browser. It is self-contained, uses no HTTP requests, and exposes actual precomputed simulation data. `index.html` is an identical convenience copy. The interactive map shows stored parameter combinations; changing a control selects a completed experiment, not an unexecuted live simulation. Plotly and compressed data are embedded.

Read executive_summary.md first; results.md gives measurements and qualifications. literature_review.md verifies all 13 requested starting references and related studies through 2026-10-30. mathematical_model.md gives the full selected model; model_comparison.md compares four candidates and explains the selection. research_questions.md and evidence/predeclared_experiments.json preserve hypotheses before broad runs. The source is in experiments/; all primary trajectories, cognitive distributions, fluxes and seeds are retained.

## Reproduce

Run from the repository root with Python 3.12, NumPy 2.2.6, SciPy 1.17.1, Plotly 7.1.0, and Node 24. The browser harness uses Chrome for Testing 154 and accepts the Chrome-path setting documented in its source. No API key, backend or network is required for dashboard use. Regeneration runs take minutes and overwrite only v4 outputs.

```bash
OPENBLAS_NUM_THREADS=1 python v4/experiments/run_experiments.py
OPENBLAS_NUM_THREADS=1 python v4/experiments/evolution.py
OPENBLAS_NUM_THREADS=1 python v4/experiments/selection_refinement.py
OPENBLAS_NUM_THREADS=1 python v4/experiments/ablations.py
OPENBLAS_NUM_THREADS=1 python v4/experiments/postprocess.py
OPENBLAS_NUM_THREADS=1 python v4/experiments/reproductive_value.py
OPENBLAS_NUM_THREADS=1 python v4/experiments/replacement.py
OPENBLAS_NUM_THREADS=1 python v4/experiments/age_robustness.py
OPENBLAS_NUM_THREADS=1 python v4/experiments/volatility.py
OPENBLAS_NUM_THREADS=1 python v4/experiments/analyze_results.py
OPENBLAS_NUM_THREADS=1 python v4/experiments/test_verification.py
OPENBLAS_NUM_THREADS=1 python v4/experiments/verify_artifacts.py
python v4/build_dashboard.py
node v4/browser_verify.js
python v4/finalize.py
```

The main driver performs pilot -> main factorial -> selected refinement -> independent environmental replication -> sensitivities. All cases follow the same parameter schema in `model.Config`; main policies/scenarios are in run_experiments.py. Full floating-point arrays are in NPZ archives. The dashboard rounds values to eight decimals for size; export parity is checked against those arrays. `sweep.csv` is updated by postprocess.py with baseline-relative recovery while retaining the original absolute threshold as recovery_absolute75. Missing recovery is censored. `findings.json` summarizes, not replaces, raw data.

## Scientific scope

There are exactly two biological stages, juvenile F and adult A, per inherited genotype. Cognitive score/trust bins carry memory and cannot be collapsed to two scalar ODEs without losing it. Exponential maturation is the main assumption; an Erlang-stage check tests a different waiting-time variance. Genetic inheritance transmits d,tau; acquired scores are culturally transmitted through adults' advice, not copied into newborns at birth.

The model concerns one binary objectively rewarded task. Cooperation, normative truth, social sanctions, parent–offspring conflict and correlated source lineage are not implemented. The oracle has privileged source reliability; the RL comparator is a specific finite feedback learner. Confidence persistence is not a clinical or psychological diagnosis of dogmatism. Technical verification is not historical evidence for an adaptation.

## Branch and GSD provenance

Branch: v4-developmental-cultural-evolution, descending from v3 commit 2662dc9. The installed Codex gsd-spike skill adapter was invoked in --quick mode with GSD Core 1.14.0. Five focused evidence records are in .planning/spikes/004 through 008. Four requested roles were executed: literature, mathematical modeling, adversarial review, and implementation/verification. No full-project planning or public deployment occurred.

## Package integrity

`python v4/finalize.py` generates parameter_schema.json, project_manifest.json and ../v4_research_complete.zip. `python v4/finalize.py --verify` checks every packaged artifact against its SHA-256 record. The archive includes all V4 sources, numerical arrays, tables, literature and reports, the offline HTML, screenshots and the five GSD evidence records. Earlier versions remain preserved in their Git branches and are not duplicated in this V4 archive. No Git installation is required to run the scientific code or dashboard from an extracted archive.
