# V5: information access and retained conviction

Open **research_dashboard.html** directly in a modern browser. It embeds Plotly and all interactive data, works without network access, and needs no backend or API key. `index.html` is an identical convenience copy. The HTML is about171 MB because it retains all trajectories/distributions and research comparisons. Allow time for its first load. Controls select completed experiments rather than silently running new parameter combinations.

Start with executive_summary.md and results.md. The scientific definitions are in mathematical_model.md, model_comparison.md, research_questions.md and research_contract.md. literature_review.md extends the prior literature investigation. repertoire_model.md and bayesian_benchmark.md explain the separate learning benchmarks. verification.md records measured checks and limitations.

## Reproduction

Use Python3.12 with NumPy2.2.6, SciPy1.17.1, Numba0.64.0 and Plotly7.1.0. The core Config dataclass is the parameter authority; generated parameter_schema.json records defaults, units and scenarios. All numerical sources are in experiments/. The first Numba compilation adds startup time; cached compiled files are not required for reproduction.

From the repository root:

```bash
OPENBLAS_NUM_THREADS=1 python v5/experiments/run_experiments.py
OPENBLAS_NUM_THREADS=1 python v5/experiments/followups.py
OPENBLAS_NUM_THREADS=1 python v5/experiments/evolution.py
OPENBLAS_NUM_THREADS=1 python v5/experiments/refine.py
OPENBLAS_NUM_THREADS=1 python v5/experiments/selection_refinement.py
OPENBLAS_NUM_THREADS=1 python v5/experiments/mechanism_invasion.py
OPENBLAS_NUM_THREADS=1 python v5/experiments/frozen_replacement.py
OPENBLAS_NUM_THREADS=1 python v5/experiments/repertoire.py
OPENBLAS_NUM_THREADS=1 python v5/experiments/repertoire_tutors.py
OPENBLAS_NUM_THREADS=1 python v5/experiments/bayes_benchmark.py
OPENBLAS_NUM_THREADS=1 python v5/experiments/analyze_results.py
OPENBLAS_NUM_THREADS=1 python v5/experiments/test_verification.py
OPENBLAS_NUM_THREADS=1 python v5/experiments/verify_artifacts.py
OPENBLAS_NUM_THREADS=1 python v5/experiments/verify_followups.py
python v5/build_dashboard.py
node v5/browser_verify.js
python v5/finalize.py
python v5/finalize.py --verify
```

Repertoire scripts have their own command-line options; their defaults reproduce the saved grids. The browser harness uses Chrome for Testing and Node24, with CHROME_BIN override documented in browser_verify.js. No package installation is needed in the current workspace. requirements.txt records numerical dependencies for another environment.

Raw arrays retain full numerical precision. Dashboard JSON rounds to nine decimal places; inactive oracle rows are losslessly deduplicated in the HTML and reconstructed for inspection/export. Null/censored quantities remain visibly unavailable. Whole-repertoire simulations use stochastic seeds; the demographic distributions average learning events deterministically. These uncertainty sources are distinct.

## What is and is not modeled

Two biological stages per inherited genotype remain, with cognitive substates for personal evidence and held convictions. Private learners retain their childhood knowledge. Adult advice comes from acquired adult beliefs; inheritance of d,tau is separate from cultural transmission. The main information-load parameter rescales encounter rates. Actual fact arrays are explored in a separate cohort model without demographic fitness. Neither component simulates semantic reasoning, cooperation norms or historical humans.

Freezing and auditing are explicitly imposed adult architectures, and the oracle receives privileged reliability information. The exact Bayesian benchmark is a limited cost-free stable-information bound. Positive copying results alone do not identify a unique authority or dogmatism mechanism.

## Provenance and package

Branch: v5-information-access, descending from40187b0. The installed gsd-spike --quick workflow (Core1.14.0) produced evidence records009–011 and manifest entries, without a full project-planning cycle or deployment. Earlier versions remain in their Git branches.

finalize.py produces project_manifest.json with source/data hashes and v5_research_complete.zip in the repository root. The archive contains all V5 source, data, documents, HTML, screenshots and the three GSD records. It does not duplicate V1–V4. The integrity command works after extraction; Git is optional for running the experiments.
