# Independent Final Scientific Review — Corrected-Primary V7 Slice 3B

**Review date:** 2026-11-02 (America/New_York)
**Independent verdict:** **PARTIAL WITH CORRECTED PRIMARY AND FROZEN INVALIDATION.**

The corrected-primary results, verification, manuscript outline, mathematical model, research contract, construct map, hypothesis ledger, executed checks, handoff, source, registrations, raw exports, and tests are mutually consistent on the claims checked below. I found no remaining report-blocking numerical error or high-risk construct misclassification. The original frozen ecology is not valid primary evidence: its no-teacher path can choose a phantom teacher action and expose hidden `z`. The fresh corrected overlay is valid for the bounded simulated contrasts it actually ran. It does not complete the broader scientific program, so a PASS, adaptation claim, novelty claim, equivalence claim, or selection-stability claim would be unwarranted.

## Provenance and correction boundary

- `v7/experiments/corrected_model.py` defines exactly three methods: `_local_state`, `_local_observation`, and `_local_attempt`. With `teacher=None`, it makes the tutor placeholder equal the private cue, exposes only the private action at expected value `2.0`, and executes that private cue. With a teacher present, all three paths delegate to the frozen base. Its SHA-256 is `7f60d4014649d18f1940a4296f9cc113a82576c4176ac7f6d3876f0bd3ea0b92`.
- The frozen failure is independently reproduced in `frozen_local_no_teacher_defect.json`: private and teacher actions tie at zero, lexical tie-breaking selects teacher, and the phantom tutor signal equals hidden `z`. `corrected_local_no_teacher_audit.json` reproduces the repaired behavior. Frozen bytes and frozen raw outputs remain an invalidated audit trail rather than being silently repaired.
- The discovery source-snapshot manifest is `45ad1045d094c39994bad0ccaf8099a27c555c6b3fe5a56fdd70a7f78cb55f7c` and its archive is `192ae4cccca8a4d2ac833f30b83f7a129cdea8a973bdc2889bb1f7af7c83784f`. The corrected-evolution snapshot manifest is `04f453fb97544149f70e29a48b90bda1cf196275af650faeed58275981622ac3` and its archive is `57698ea421d1f27793a11623c704c693bc2da8ed1c2c1ae6357470f5df206dfc`.
- The pre-holdout corrected freeze manifest is `4e8ff2f8a653c8720b2d2c7938458ccee5dd6c6007c46d09583a551ea9b2fc13`; its overlay archive is `d87f582d37a7cfc8448379543621116029c5b354e27e02d1393870ac19eb1287`. The freeze records vectors `(.5,0)` and `(1,0)`, scalar `.25`, and the fixed ordinary comparator. Holdout and evolution registrations point to that freeze. The frozen and corrected replay digests independently reproduce as `94467195bc1f6dcb9f20983f91ec3e86bad9c02845790979f802fa9d6ac1a070` and `708132b42d001a03bbe39db751221946246125afeb2c318103410009c6ad5d23`.
- Registration-time snapshots, the pre-holdout freeze, seed partitions, and live/result hash identity are durable evidence against cached rescoring or favorable retuning. Operational filesystem-mode guards were not durably recorded and are not evidence.

## Independent recomputation from corrected raw exports

### Discovery

The discovery gzip has 504 unique seed-regime-policy rows, four seeds per cell, SHA-256 `ae2e130c08df484d6f6605d59f489886ecc025dcdbec4c89049c7d0306381341`. I independently recomputed all 27 within-seed `d=0` to `d=1` mean-N contrasts and across-seed MCSEs. They match the report exactly. The procedure-only mean effects across regimes 1–9 are `-0.0990, 0.1344, -0.5156, 0.1510, -0.3250, -0.4396, -0.4208, 0.2365, -0.0635`; the local-only effects are `-1.8781, -0.2010, 0.0083, -1.4521, -0.5427, -3.3083, 0.3073, -3.4240, -1.5083`; and scalar-diagonal effects are `-1.4198, -0.1771, -0.6583, -1.1875, -0.3396, -3.9750, -0.1073, -3.1031, -1.5698`.

I also independently recomputed every class-specific sample-mean top, two-MCSE compatibility set, and boundary label. They match the report. The vector-class sample tops by regime are `(0,0)`, `(.5,.5)`, `(.5,1)`, `(1,0)`, `(.5,.5)`, `(0,0)`, `(.5,.5)`, `(.5,0)`, and `(.5,0)`; the scalar-restriction tops are `(0,0)`, `(.5,.5)`, `.25`, `(0,0)`, `(.5,.5)`, `(0,0)`, `(.5,.5)`, `(0,0)`, and `.25`. Compatibility sets are broad in many regimes. These are sampled-grid descriptions under an aliased L9 design, not confidence/equivalence sets, unique continuous optima, or ESS results. Candidate freezing used pooled discovery net stock rather than mean N and did not jointly optimize an interior point or `tau`.

### Fresh holdout and calibration control

The holdout has 1,368 unique rows, 24 paired seeds per cell, SHA-256 `5956bde27a901f99f6520d3c5d227a6da1069fa3f86d586785ae6f46b383e5e0`. The focal frozen vector `(.5,0)` minus ordinary spans `-0.3902778` to `+0.4480903` in mean N and `-0.000999735` to `+0.001477633` in net stock change per agent-season across nine regimes. The asocial-access-off sentinel was run only at regimes 1, 5, and 9; its paired `(ΔN, Δnet)` values are `(1.671, 0.003067)`, `(1.500, 0.003026)`, and `(2.519, 0.005688)`. These are bounded model outcomes, not general evidence for asocial advantage.

The separate 288-row depth-aware calibration control has SHA-256 `3badd2572da962f2b48cea6066bed72aed5f2490a0cf7dc15bfc0064c9e041d6` and stays numerically close to ordinary at the three sentinel regimes. It is a control, not an optimized strong learner or a causal explanation. Rate MCSEs are correctly computed across independent seeds. The registered Wilson-rate criterion remains unresolved because event numerators and denominators were not exported; per-agent or per-event Bernoulli pseudo-replication would be invalid.

### Corrected finite-lineage assay

The corrected evolution export has 2,112 unique arm rows, SHA-256 `bbaba43758311955eb5ad24fed294e201a77dd0032c6f5622e277c157c97775e`. It contains 12 directed contrasts, 24 arms, 88 registered seeds, and 88 paired paid births per contrast. All 2,112 rows are complete fixed-batch paid-birth rows; no-birth, cap-censored, and incomplete-batch denominators are all zero. There are 1,846 finite-extinction arm rows, retained unconditionally.

All 12 descendant means, paired MCSEs, and zero-difference counts reproduce the report. The maximum paired descendant MCSE is `0.2255814816`; the maximum arm-level establishment Wilson half-width is `0.0971737666`, meeting the registered `0.25` and `0.10` precision thresholds at 88 seeds. These are conditional T=80 descendant endpoints. Numerical precision does not establish significance, equivalence, direct competition, rare-mutant invasion, fixation, ESS, stable polymorphism, or biological adaptation.

### Corrected H9 diagnostic

The corrected H9 export has 216 unique rows (three regimes × three arms × 24 seeds), SHA-256 `058a9ac5fe86dc3c5628039659d05fdd645a0290772879d01ae9002f0feae4a4`. All reported N/K means, MCSEs, and removed-K totals reproduce from raw rows. The run clones corrected `d=0` states, changes `theta`, and optionally erases K/independent-success memory. It does not kill carriers, manipulate root diversity, estimate recovery time, or cross shock with `d`. Its mean-N statistic averages the full 240-season run, including 150 shared pre-intervention seasons, so the population contrast is diluted by construction. This is a mixed N/K diagnostic, not a causal test of canonical H9 monoculture debt.

## High-risk construct audit

- `d=0` is ordinary social learning, not asociality. `asocial_access_off` is the separate cultural-access removal condition.
- FeatureTrust is action-blind: its feature score has no action index, and the scalar prediction is added only to the advised action. Its performance cannot support a claim about general action-conditional RL.
- Candidate B evaluates only the current decision, not future learning. Its evaluator uses calibrated source reliability, while executed query accuracy is fixed at `.80`; evaluator and execution therefore differ. Its opportunity price subtracts `(D+1) × safe_yield`, whereas an actual information purchase consumes one time token. Query/verification purchase counts are absent from corrected aggregates. “Bayes-optimal,” “nonmyopic,” and “fully resource-rational” are unsupported.
- Teacher eligibility is age-neutral and requires K, two successes, and time, but the procedural ranking key `T[outcome:family]` is read and never updated. Default ties resolve by identity, and content is the lexical first eligible K sequence. Teacher identity/content order, rather than updated B or predicted performance, remains a rival explanation.
- Adult direct genetic override is off at age `>=5`; fixed `tau=5` is not jointly optimized and is not the V1–V6 exponential maturation mean. Births inherit genotype only and begin with blank acquired B/K/T/H.
- IBM Q0 is a greedy whole-procedure posterior proxy. `ExactTinyPOMDP` is a separate two-episode toy oracle and bounds only its matched restricted toy policy; it is not a full-IBM optimality bound.
- `mean_population`, birth/death flux, endpoint net stock per agent-season, and finite descendants are distinct estimands. Net stock is an endpoint resource-plus-living-energy residual divided by full-horizon agent-seasons, including burn-in; it is not fitness, population growth, or task performance.
- H7 canonical metareasoning equivalence is unresolved: no equivalence margin, strong matched action-conditional learner, consistent information pricing, or purchase counts exist. H8 canonical provenance saturation is partial: same-root fixture bookkeeping exists, but the independent/copied × visible/hidden ecological manipulation does not. H9 is diagnostic partial for the reasons above.
- The post-freeze persistence assay supports generic learned action-habit persistence with factual revision, not private-belief dogmatism or obligation. The corrected cumulative assay is equal-work but cognitive-only, and its pooled upper bound is not a feasible per-person budget comparator. Neither establishes demographic cumulative culture.

## Bounded executable checks

The following checks were rerun from the repository root during this review:

```text
python -m unittest discover -s v7/tests -p 'test_*.py'
63 tests in 4.521 s: OK (expected failures=1)

python v7/synthesize_results.py --verify-only
verified; primary evidence=corrected_overlay; verdict=PARTIAL_WITH_CORRECTED_PRIMARY_AND_FROZEN_INVALIDATION

python v7/experiments/run_postfreeze.py --verify-freeze --manifest v7/evidence/core_freeze/manifest.json
passed; frozen live/archive replay and source-byte checks all true
```

The one expected failure deliberately demonstrates that the desired no-teacher invariant does not hold in the frozen base; active corrected-path tests cover all ages/policies, private-cue execution, teacher-present delegation, birth blanks, adult override-off, source identities, raw/report parity, and finite-claim guards. A separate non-writing corrected replay recomputation also matched `708132b4...5d23`.

## Residual scientific requirements and claim boundary

The PARTIAL verdict is required. Authority-label ITT, joint memory-by-override exposure, full hidden-state and event-key CRN invariance, exported event counts, a strong action-conditional comparator, realized information-purchase counts, feasible individual-budget cumulative accumulation, direct competition/rare-mutant growth, carrier loss, ancestry/root-diversity risk, recovery time, and institutional/normative mechanisms remain absent or incomplete. The 25-check ledger accordingly remains 3 passed, 20 partial, and 2 not run.

The defensible paper claim is limited to reproducible, corrected-model, finite-horizon response surfaces and contrasts under the implemented policy classes, task, costs, and seed designs, plus explicit negative findings about what those implementations do not test. Claims of biological adaptation, specialized authority cognition, unique optimality, general-RL necessity, equivalence/no effect, dogmatism, obligation, demographic cumulative culture, canonical monoculture debt, invasion, fixation, ESS, stable polymorphism, or broad novelty are unsupported.

## Stable evidence pointers

- Corrected synthesis source: `v7/synthesize_results.py`, SHA-256 `4f070cb38ccfd5f340a5ba762d28f829c9d0b67a9d025824896f8d05f1c743b8`.
- Corrected raw exports: discovery `ae2e130c...1341`; holdout `5956bde2...e5e0`; depth control `3badd257...41d6`; evolution `bbaba437...75e`; H9 `058a9ac5...4a4`.
- Source snapshots and freeze: `v7/evidence/corrected/`; frozen invalidation and corrected audit: `v7/evidence/frozen_local_no_teacher_defect.json` and `v7/evidence/corrected_local_no_teacher_audit.json`.
- Claim/status contracts: `v7/research_contract.md`, `v7/constructs_and_estimands.md`, `v7/evidence/hypothesis_ledger.json`, and `v7/evidence/executed_checks.json`.
- Final generated reporting surfaces: `v7/results.md`, `v7/verification.md`, `v7/manuscript_outline.md`, `v7/README.md`, `v7/research_gaps_and_next_steps.md`, `v7/project_manifest.json`, and `v7/evidence/handoffs/07-results.json`.

This review remains valid only while the corrected raw hashes, registered source identities, replay digests, prohibited-claim boundaries, and PARTIAL classifications above remain unchanged.
