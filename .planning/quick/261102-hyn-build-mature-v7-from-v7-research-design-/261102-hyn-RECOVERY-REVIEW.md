---
reviewed: 2026-11-03T05:25:00Z
scope: independent-scientific-recovery
readiness: needs_revision_for_full_scientific_goal
bounded_controls: verified_with_claim_limits
official_verification_modified: false
science_or_ui_sources_modified: false
---

# V7 scientific recovery review

## Assessment

The accepted final controls are source-frozen, hash-consistent, numerically reproducible from their saved rows, and materially repair the weak early recovery drafts. They support the bounded claims made in `v7/final_controls.md`. They do **not** complete the original scientific program: the authority-sensitive label intervention, independent-information provenance factorial, accept-to-memory × override factorial, and check-complete cumulative-procedure test remain absent or only partial.

Accordingly, the recovery is **ready within the bounded control scopes but needs revision for the full V7 scientific goal**. This review does not change the official verification or scientific-check dispositions.

## Evidence integrity

- All 43 paths indexed by `v7/experiments/output/corrected_primary_registry.json` existed and matched their declared SHA-256 at review time. The canonical summary's registry digest `14e9f4c2...b885` matched the live registry.
- The live source hashes and every member of the four accepted `source.tar.gz` archives matched the registrations for `execution_planner`, `resource_control`, `carrier_control`, and `belief_control`; no member was absent or extra relative to each registration's source set.
- Registrations and source archives predate their raw outputs. All raw hashes in the four accepted summaries matched live bytes.
- The accepted R3 label control also passed archive/live/raw identity: source archive `ed217c4e...f92`, raw `95a42873...896`, five archive members, zero mismatches.
- Targeted source tests passed 10/10: three execution-planner tests, four resource-control tests, and three belief-control tests. The whole suite and browser/UI were not rerun because the final UI executor was active in those files.

## Recomputed gates and counts

| Control | Independent recomputation | Verdict |
|---|---|---|
| Execution-priced planner | 216 unique rows = 24 seeds × 3 regimes × 3 policies; every row completed 240 seasons; max ledger residual `2.73e-12`; max actual time use 11/12. Durable counts reconcile teacher-present + no-teacher = all initial decisions. | PASS within one-decision `Q0` scope; not global RL. |
| Planner contrasts | Paired mean-N differences/MCSE exactly reproduce: vector `(0.0033/.2304, -.2023/.2145, .1927/.3407)` and execution EVI `(-4.4550/.2576, -6.4066/.2617, -4.1332/.3797)` in regimes 1/5/9. Paired energy MCSEs are `.00057`–`.00144`. | PASS; the matched planner performs worse here, a valid negative result. |
| Closed-resource control | 168 endpoints = 120 core + 48 no-innovation carrier endpoints; 48 paired-effort endpoints = 24 independent pairs. Max stock residual `8.04e-11`; max work/person/season 4; all saved population identities close. | PASS for resource/time/demographic accounting. |
| Matched work | 2,880 paired season rows form 1,440 seed-season pairs; offered effort, realized effort, and cross-arm effort are exactly equal in all pairs. Mean-N delta `4.3181`, paired MCSE `.6071`. | PASS for the declared equal-realized-work comparison. |
| Resource genealogy sample | The representative seed contains 2,089 acquisitions: 535 physical discoveries, 1,436 teachings, 118 storage reads. All roots are well-formed; the transmission arm has 83 complete recipes, all multi-origin, 74 in descendants, and 75 whose learner is not an originator. | Supports actual demographic reuse/recombination, but only as a one-seed sampled origin record, not the required procedure DAG. |
| Total-carrier control | 48 endpoints = 24 paired seeds; 960 post-restart season rows; every restart has 10 blank agents and external energy 80 in both arms. All 24 storage-off endpoints have zero recipe/storage/function; all 24 storage-on runs recover and every recovered root is in the paid artifact ledger. | PASS for `ACCUM-02`; explicitly an external intervention, not natural fitness. |
| Carrier accounting | All paired input fields match; 48 histories have exactly 20 steps, close `N`, use ≤4 work/person, and have max residual `3.13e-12`. Each seed has six paid writes and six stored prefixes. | PASS. |
| Fixed-proposition belief control | 3,840 training rows = 96 forty-step histories; 15,360 adult rows = 768 twenty-step cloned sequences. Truth and source conviction are fixed within every training history; adult truth is fixed within every sequence; adult inherited override is always zero; `K` is fixed in adulthood. | PASS for the declared adult learning/intervention mechanics. |
| Belief/action ledger | Across matched `d=0/.5`, training and adult private/audit/feedback tapes and every `L/B` value are exactly identical; max `B` difference is zero. All 15,360 chosen-action updates and material-credit identities recompute exactly; approval never enters material credit. | PASS for information equalization and belief/action separation. |
| Adult endpoints | Static-prior reversal baseline is correct in 4/24 blocks; reliable evidence gives 22/24. Switching-prior reversal is correct in 24/24. This is prior-model dependence, not irrational dogmatism. | Valid negative/boundary result. |

## Targeted AUTH-01 firewall result

The R3 confirmation raw contains 422,132 juvenile rows covering 105,533 actual teacher-present, age-0–4 opportunities. They form 211,066 same-role `d0`/`applicable_dhalf` pairs and 211,066 peer/authority pairs.

For every one of the 211,066 same-role `d` pairs:

- `B`, `K`, `T`, `H`, message content excluding the tested label, source history, tested label message, private hardware accuracy, neutral action, conflict, and `pre_override_digest` were exactly equal;
- projected operation count was 1 and projected charge was `.01` in both rows;
- neither policy requested an information purchase;
- `d0` made zero overrides; `applicable_dhalf` made 33,096 overrides; and the chosen action differed in exactly those 33,096 cases.

This **does satisfy the before-arbitration firewall within the R3 immediate counterfactual-decision scope**: changing `d` leaves the observed pre-arbitration state and neutral computation unchanged, then acts only through the override. It does not complete full `AUTH-01` acceptance because:

1. `time_tokens`, `computation_budget`, and `operation_cap` are not columns in the raw export. Equality follows from source construction—both decisions reuse the same `PolicyObservation` and cap 128—and from equal projected cost/operations, rather than a bitwise raw budget field.
2. The `d0` and `dhalf` records are counterfactual re-decisions on observations produced by one live `.5/.5` ecology. They do not export postdecision mediated outcomes from two executed ecological trajectories.

The label contrast is also exactly zero for both traits, but this is a structural-null test of label-neutral policies. It does not satisfy `AUTH-02`'s missing authority-sensitive-policy arm and must not be interpreted as evidence that a genuine authority cue has no effect.

## Initial gaps: closure status

| Initial gap | Recovery status | Evidence and remaining boundary |
|---|---|---|
| Canonical corrected reporting route | CLOSED | `output/summary.json` points to the hash-matched derived corrected registry; frozen `run_manifest.json` remains untouched and provenance-only. |
| Comparator query/cost/counter defects | CLOSED within bounded scope | Query `.8` and verify `.9` agree in expectation/execution; incremental cost and one information token execute; 12 deliberation units are a common sunk planner cost; counters include dead/newborn actors. No global-RL superiority/equivalence claim follows. |
| Carrier loss/storage factorial | CLOSED | Total removal, blank restart, innovation off, paid storage/read ledger, and paired external inputs meet `ACCUM-02`. |
| Demographic resource/work control | SUBSTANTIALLY CLOSED | Closed finite resources, paid teaching/births, equal work, blank newborns, and actual root origins are demonstrated. `ACCUM-01` remains partial for the reasons below. |
| Sequential adult intervention mechanics | CLOSED for the three core interventions | Fixed-proposition training, 20 real updates, audience removal, free audit, and matched supporting/reversal evidence are present. The result is prior inertia/action-value learning, not dogmatism or obligation. |
| Causal opportunity denominators | PARTLY CLOSED | Planner world totals and R3 opportunity rows are durable. Adult endpoint precision and several causal designs remain unresolved; repeated rows are not independent trials. |

## Demonstrated data issues

1. **Carrier endpoint mixed-phase fields.** `mean_population` divides the 20 post-restart observations by the model's configured horizon 60; `mean_population_post` is the correct post-restart mean (for example, `7.55` versus `22.65`). `innovations`, `transmissions`, `probes`, and `work` also retain pre-restart counts. These fields do not invalidate the storage claim, but downstream reporting must use `mean_population_post` and must not call cumulative counters post-restart events.
2. **Incomplete cumulative-procedure genealogy export.** `representative_acquisitions.json.gz` covers only seed 82601 and records learner plus ultimate roots, but not the donor/teacher edge, parent procedure ID, biological parent, transmission fidelity, or a reconstructible two-edge DAG. This prevents full independent verification of `ACCUM-01` even though the sample clearly contains multi-origin descendant recipes.
3. **Clustered belief denominators.** The summary's `3064/3840` private-signal count repeats the same 960 seed-episode tapes across `d` and hazard; the independent-tape count is `766/960`, and scientific endpoints have 24 seed blocks. The narrative currently states the 24-block limit; future calculations must not use 3,840 or 15,360 as independent binomial denominators.
4. **Adult precision is unresolved.** Wilson 95% half-width is `.146` for 4/24 and `.118` for 22/24, both above the original `.10` target. The saved reports do not record that stopping/precision disposition. These are valid observed endpoint counts, not precise rate estimates; do not adaptively add seeds unless a new extension is preregistered.

## Prioritized remaining scientific blockers

1. **Authority/provenance causal design remains unexecuted (`AUTH-02`, `PROV-01`).** Run the already specified bounded authority-sensitive policy arm and the independent/copied-root × visible/hidden-provenance factorial. The existing structural label null and distinct source IDs cannot substitute for these experiments or be relabeled as negative results.
2. **Genuine cumulative culture remains unestablished (`ACCUM-01`).** The model permits individual acquisition (`48` minimum work versus harvest-reserved lifetime ceiling `54`), lacks transmission-only and no-retention ablations, does not export a full parent-procedure/teacher DAG, and has no held-out functional task test across at least two transmission edges. Current evidence supports resource-accounted ordinary knowledge reuse/recombination, not a completed cumulative-culture claim.
3. **Memory acceptance versus override is still bundled (`AUTH-03`).** The required fixed-exposure 2×2 accept-to-memory × conflict-override assay with separately exported belief, procedure memory, immediate action, and later reuse was not run. This is an omission, not a null result.
4. **Claim-specific planned work remains absent.** `RISK-01` has no low-density random-projection/branching validation, and no 120-season direct competition ran. These omissions do not invalidate the finite `T=80` paid-newborn contrasts, which remain valid as finite endpoint comparisons; they block multiplicative-risk, asymptotic invasion, fixation, ESS, stable-polymorphism, and stronger selection claims.

The optional H4 institutional/norm package and acquired obligation state are not closure blockers. The absence of global-optimal RL is also not a defect for the explicitly bounded planner, provided no general superiority or adaptation claim is made. The current reports respect both boundaries.

## Review quality scorecard

Totals below are scoped review units, not an accuracy percentage.

### Scientific-control quality

| Category | Observed defects | Assessment |
|---|---:|---|
| Usefulness/completeness | 4 / 11 | Four mandatory scientific designs remain partial or not run; bounded controls answer their narrower questions. |
| Analytical clarity | 2 / 11 | Carrier mixed-phase fields and clustered belief denominators need explicit field-level caveats. |
| Interaction/UI consistency | N/A | UI was intentionally outside this concurrent scientific review. |

### Analytical correctness and robustness

| Category | Observed defects | Assessment |
|---|---:|---|
| Source authority and confidence | 0 / 5 | Four final controls plus accepted R3 have matching live/archive/raw hashes. |
| Value accuracy | 0 / 10 | Consequential counts, paired means/MCSEs, ledger identities, and transition equations independently recompute. |
| Cross-artifact consistency | 0 / 5 | Registrations, summaries, registry, source archives, and raw hashes agree at review time. |
| Data-quality controls | 3 / 9 | Budget fields absent from R3 raw, carrier phase-mixed counters, and clustered belief denominators constrain reuse. |
| Conclusion support | 4 / 11 | Current bounded conclusions are supported; four broader mandatory claims/tests remain unavailable. |

---

_Independent scientific recovery review; no experiment, report, dashboard, data, official verification, or source file was modified._
