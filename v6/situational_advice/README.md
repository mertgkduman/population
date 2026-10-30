# V6 extension: adults with poorer local information

The original V6 remains unchanged in v6/experiments and its standalone HTML. This extension concerns juvenile-specific situations: adults can know general conditions but observe a follower's immediate circumstances less accurately. Juvenile local-cue accuracy is .90; adult local-cue accuracy is .55,.70 or.85. Global private-learning accuracy remains .65 and juvenile/adult encoding probabilities remain1/.1.

A follower substitutes adult judgment with probability d. Accepted situational recommendations are interpreted using the follower's own context cue before being stored as general knowledge. The resulting memory noise is derived from the observation channels. Clean-teaching, action-only and memory-only controls distinguish that assumption from direct action substitution. No term rewards intermediate deference.

Open index.html offline after building it. On the publication site, select V6 → Results → Situational advice. The original plasticity experiment remains selectable alongside it. Model equations and scientific limitations are in mathematical_model.md; the contract precedes broad runs.

## Reproduce from repository root

```bash
OPENBLAS_NUM_THREADS=1 python v6/situational_advice/experiments/run_experiments.py
OPENBLAS_NUM_THREADS=1 python v6/situational_advice/experiments/followups.py
OPENBLAS_NUM_THREADS=1 python v6/situational_advice/experiments/verify.py
python v6/situational_advice/experiments/pack_data.py
python v6/situational_advice/experiments/verify_extended.py
python v6/situational_advice/experiments/analyze_results.py
python v6/situational_advice/build_dashboard.py
node v6/situational_advice/browser_verify.js
python scripts/make_readme.py
python scripts/build_pages.py
python scripts/verify_pages.py
```

Use the dependency versions recorded in the run manifest. No additional library, API key or backend is needed. Published reference packages contain all path-specific map outcomes and every actual time series shown by the explorer. The repository additionally retains full histories from the other environmental seeds. Keeping unused histories outside the Pages artifact respects its1GB hosting limit without losing research data. Every graph has an exact displayed-data ZIP.

Fixed-source random copying has affine accuracy: universally inferior adult advice produces a d=0 optimum, not an interior optimum. Conditional policies and interior constant propensities are different objects. Any reported maximum is a sampled abundance or conditional-invasion maximum, not an ESS or historical adaptation.

Main and refined held-out abundance averages use4-unit observations. The standalone visualization displays a strict8-unit subset of actual trajectory observations; it never interpolates fabricated simulation values. Full-resolution histories remain in the repository. The initial coarser averaging miss and its original results are retained for audit.
