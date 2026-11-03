# V7 Verification

## Outcome

Software/replay verification: **PASS WITH ONE EXPECTED FROZEN-DEFECT FAILURE AND A PASSING CORRECTED-PATH REGRESSION**. Scientific requirement completion remains **PARTIAL** (6 passed, 18 partial, 1 not run across all 25 predeclared checks). The frozen failure is preserved; only the fresh corrected-overlay outputs are primary ecology evidence.

## Executed commands

```text
python -m unittest discover -s v7/tests -p 'test_*.py'
python v7/synthesize_results.py --verify-only
python v7/experiments/run_postfreeze.py --verify-freeze --manifest v7/evidence/core_freeze/manifest.json
python v7/experiments/run_corrected_experiments.py --stage discovery
python v7/experiments/run_corrected_experiments.py --stage freeze
python v7/experiments/run_corrected_experiments.py --stage holdout
python v7/experiments/run_corrected_experiments.py --stage depth-control
python v7/experiments/run_corrected_experiments.py --stage h9
python v7/experiments/run_corrected_evolution.py --max-seed 96
```

The frozen check reproduced `94467195bc1f6dcb9f20983f91ec3e86bad9c02845790979f802fa9d6ac1a070`; frozen bytes were deliberately not repaired. Corrected discovery has a registration-time source snapshot, and freeze `4e8ff2f8a653c8720b2d2c7938458ccee5dd6c6007c46d09583a551ea9b2fc13` with replay `708132b42d001a03bbe39db751221946246125afeb2c318103410009c6ad5d23` was written before holdout. Final live source hashes match the registrations and result records. Operational file-mode guards were not durably captured, so verification does not claim them. `frozen_local_no_teacher_defect.json` and `corrected_local_no_teacher_audit.json` retain both sides of the audit.

## Corrected primary export parity

| artifact | rows | sha256 |
|---|---|---|
| discovery | 504 | ae2e130c08df484d6f6605d59f489886ecc025dcdbec4c89049c7d0306381341 |
| holdout | 1368 | 5956bde27a901f99f6520d3c5d227a6da1069fa3f86d586785ae6f46b383e5e0 |
| depth_reliability_control | 288 | 3badd2572da962f2b48cea6066bed72aed5f2490a0cf7dc15bfc0064c9e041d6 |
| evolution | 2112 | bbaba43758311955eb5ad24fed294e201a77dd0032c6f5622e277c157c97775e |
| h9 | 216 | 058a9ac5fe86dc3c5628039659d05fdd645a0290772879d01ae9002f0feae4a4 |

Machine data-quality status: **PASSED** across 27 grain, row-count, seed, finiteness, result-hash, batch-volume, and registered-source checks.

## Frozen invalidated archive parity

| artifact | rows | sha256 |
|---|---|---|
| discovery | 504 | eeb791fdb8df6f3053479aa90de23e6821f4e5c9f9fe07ade4ada01802064098 |
| holdout | 1368 | d46e4ebb6e9dc377e83c04f438452d723dac9eaa198828fb0723d9946bdf87bb |
| depth_reliability_control | 288 | 48755d193b57fc4d4818882c8f8b3522837a51ae60bfffe5ce630d06ae718e2b |
| evolution | 1242 | 8c3a9dc1cc7efb3890d5a56a6248c58d53dce2d632ba2986823f0fdf7e9d7dc9 |
| persistence | 120 | 90f787821b5ef91d509e066c6c7f97c413bbfabb48bd9a33086f1e18ae522c99 |
| postfreeze_yoked | 648 | 0cdee387a81264e08a08942c9fbc1a056cd57025b178102d3aadef2ae09c2c47 |
| cumulative_assay | 144 | 20da7626013cc43a430604847115ccd421a12cb385c58aca60dd665615def599 |
| postfreeze_h9_observation | 216 | 325c2ecb42e68e1a334759d24bd510e9ad693c4ad2736306deacff09a092cbb4 |

## Predeclared scientific checks

| ID | status | evidence-based disposition |
|---|---|---|
| AUTH-01 | partial | Kernel isolation is consistent with conflict-only override, but the registered ecological decision-level bitwise B/K/T/H/budget audit was not exported. |
| AUTH-02 | passed | R4 crosses genuinely randomized uninformative labels with label-neutral, generic-source and imposed authority-sensitive policies, identical acquired tutor histories and common draws. Unconditional and conflict contrasts are exported. This is a mechanism assay, not evolved authority sensitivity. |
| AUTH-03 | passed | R4 runs the full joint-exposure memory-acceptance (0/1) by immediate override (0/.5) factorial with blank states, acquired B/K/T/H, actual budgets, actions and twenty adult reuse steps; adults have zero inherited override. Memory intervention changes storage, not cognitive capacity. |
| INHERIT-01 | partial | Births blank B/K/T/H and transmit genotype only; no cross-fostering/full relabel audit. |
| FOUNDER-01 | partial | Blank initialization is tested in fixtures, not all registered founder cultures and failed burn-ins. |
| COMP-01 | partial | ExactTinyPOMDP validates only a restricted two-episode toy; IBM Q0 is greedy, FeatureTrust is action-blind, and Candidate B is approximate with mismatched evaluated/executed query accuracy. The overlay repairs the asocial local oracle but does not create a strong general-RL or optimal-planning comparator. |
| BUDGET-01 | partial | The final resource_control enforces4 tokens/person and closed energy/resource budgets with24 equal-realized-work pairs. The final execution_planner charges12 common abstract deliberation units and actual incremental fees. Global-optimal learner matching and the old pooled upper bound remain unsupported. |
| TASK-01 | partial | Tiny and cognitive landscapes have partial alternatives/coverage; full ensemble and causal prerequisite robustness are incomplete. |
| ACCUM-01 | partial | The R4 eight-node DAG adds actual branching/recombination, receipt genealogies, held-out physical tests and fresh exactly equal-work pairs. Its solo-protocol energy bound excludes independent completion. Paid two-edge transfer passes23/24; private-only/no-retention/no-bootstrap controls produce no complete programs. Prerequisite scramble has identical endpoints and no separate modification-disabled control ran, so full causal-ablations criterion remains partial. |
| ACCUM-02 | passed | The final carrier_control removes all people, restarts ten blank agents with audited external energy, disables innovation, and tests costed artifacts on/off over24 fresh pairs. Off retains no recipe; recovered on-origins trace to paid artifacts. This is an intervention, not natural growth. |
| PROV-01 | partial | R4 blank tutors acquire independent .8 private histories; copied testimony shares an actual physical root. Exact enumeration verifies same-root duplication invariance and independent versus explicit hidden-mixture posteriors. The broader ecological merged-root implementation and attribution remain partial. |
| CLASS-01 | partial | Schema and grid classes are explicit; sampled-grid classification is descriptive and not a general surface recovery test. |
| MATURITY-01 | partial | Age threshold tau=5 and adult genetic override off are tested; full life-course confound audit is incomplete. |
| LEDGER-01 | passed | Material/time ledgers and residual checks pass across frozen and fresh corrected exports. |
| TEACH-01 | partial | Teacher eligibility is age-neutral, but the never-updated ranking key resolves by identity and the lexical-first K offer creates a second order artifact; updated performance selection is absent. |
| GROWTH-01 | passed | Mean N and per-agent-season net resource are exported separately with no scalar-growth relabeling. |
| INVASION-01 | partial | Fresh corrected paired neutral-tag finite descendants ran, but not rare-mutant growth or direct competition. |
| INVASION-02 | partial | Fresh corrected finite directional contrasts ran; no ESS, fixation, or stable-polymorphism identification. |
| NORM-01 | partial | The final belief_control trains blank learners on a fixed proposition, clones actual states, and gives matched-direction evidence/audience/cost controls under static/switching priors. Factual updating is likelihood-aware; no irrational dogmatism is established. Full normative/source-asymmetry probes remain absent. |
| NORM-02 | partial | Audience/reward probes exist in a separate process; obligation and novel-context injunction were not modeled. |
| RNG-01 | partial | Frozen and corrected replay identities/source snapshots pass, but common-random-number verification is narrower than full registered event identity audits. |
| HIDDEN-01 | partial | The frozen behavioral path fails because a phantom tutor equals hidden z. The separately registered three-method overlay passes the same adversarial no-teacher probe, while broader policy/world truth-firewall coverage remains partial. |
| RISK-01 | not_run | No low-density random-projection or branching-growth validation was run. |
| COND-01 | partial | Primary denominators are preserved. execution_planner adds actual whole-world initial-arbitration purchase/no-teacher/conflict counts, including dead actors; real juvenile label controls retain opportunity denominators. Independent information-history and demographic-ITT claims remain limited. |
| EXPORT-01 | passed | Reporting tests recompute frozen and corrected hashes, row counts, corrected paired contrasts, all 25 statuses, finite-claim guards, and both frozen-defect/corrected-path probes. |

Machine-readable records, including commands, exit status, evidence paths/hashes, corrected and frozen raw hashes, and claim consequences, are in `v7/evidence/executed_checks.json`. Wilson precision for action/revision/success rates remains unresolved because event numerators/denominators were not exported; their MCSE is across seeds only.


## Final controls

See `final_controls.md`, canonical `experiments/output/corrected_primary_registry.json`, and registrations under `evidence/{execution_planner,resource_control,carrier_control,belief_control,information_controls,cumulative_dag,cumulative_dag_matched}`. All source/config hashes are checked by `final_controls.py`; these controls do not promote global-RL, dogmatism, or adaptation claims.
