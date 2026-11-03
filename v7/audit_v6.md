# V7 audit of the pinned V6 baseline

**Baseline:** `mertgkduman/population` commit `9e95c6ce2e21587f9dbe2d18dcb5ab7787b140f6`  
**Audit date:** 2026-11-02  
**Scope:** source, result summaries, and retained scientific infrastructure; the published sweeps were not independently rerun.

## Source identity and audit method

The source of truth is the clean published repository at `dist/github-repository`, read at the pinned commit. The primary working repository has a different commit history (`28e095246e874a4134f0618c4e12d98467031f5d` during this audit), while the clean published repository is currently at `75b13533df7de947dcdce26213e0fb1444c95742`. This is a commit-mapping issue, not a content discrepancy. The six critical scientific files below have identical Git blob IDs in the working tree, pinned commit, and clean published HEAD. [VERIFIED: local `git hash-object` and `git rev-parse` audit, 2026-11-02]

| File | Identical blob |
|---|---|
| `v6/results.md` | `e96cad2b3a92c7dbaa8c02551e3cf5b2327e71a2` |
| `v6/situational_advice/results.md` | `1559266cc001462ba4fe2cb0e0d2369534acc7bb` |
| `v6/mathematical_model.md` | `3287ac29f1fd55f0d469fa97920f29c21251ee4e` |
| `v6/situational_advice/mathematical_model.md` | `12845c029aded1abf8748e0bf371b6d22079fa2c` |
| `v6/situational_advice/experiments/model.py` | `13bca1f636adfeae4f7671d04d8c4eefdef42b35` |
| `v5/repertoire_model.md` | `2f8dba15a26eef40606039f78b4c3c10df842424` |

This audit therefore cites pinned paths and line numbers even though the same text is readable in the primary tree. Machine-readable source and bibliographic evidence is recorded in `v7/evidence/literature_sources.json`.

## What V6 establishes

### Main developmental-plasticity model

The main V6 grid reports `d=1` as the abundance maximum in all 12 combinations of three adult-encoding levels and four environmental hazards. Its conditional-invasion maximum is also `d=1` in those contexts, but every mutant is tested against the same resident (`d=.5`, `tau=3`); the report explicitly says this is not an ESS. [VERIFIED: pinned `v6/results.md:5-24`; `v6/mathematical_model.md:112-129]

The global grid maximum does not imply monotonic benefit at a fixed maturation time. On 16 held-out paths at `tau=3`, adult encoding `.1`, and hazard `.2`, mean abundance is 2200.303 at `d=0`, 2115.379 at `d=.5`, and 2077.566 at `d=1`; the paired endpoint difference is -122.737 (SE 25.519). [VERIFIED: pinned `v6/results.md:27-35`; local `v6/experiments/findings_summary.json`, key `heldout`]

The imposed adult-plasticity mechanism behaves as specified: in a no-birth/no-death reversal cohort, the first sampled time reaching `.75` accuracy is censored through time 200 at adult encoding 0, 137 at `.1`, and 14 at 1. This is a mechanism check, not evidence that selection evolved adult rigidity. [VERIFIED: pinned `v6/results.md:37-41`]

### Situational-advice extension

The extension already gives tutors poorer access to juvenile-specific local circumstances. The exact declared values are:

DATA_Q7N4B2LA_START
> `context_F:float=.9`, `context_A:float=.7`, with the main sweep using adult local accuracies `.55`, `.70`, and `.85`; juvenile/adult encoding is `1/.1` and global private-cue accuracy is `.65`.
DATA_Q7N4B2LA_END

[VERIFIED: pinned `v6/situational_advice/experiments/model.py:13-35`; `v6/situational_advice/results.md:1-7`]

No interior `d` maximum was observed in the joint abundance grids, any fixed-`tau` slice, the 33-value held-out sweeps at `tau=3`, or the conditional-invasion maxima. Adult local noise changes which endpoint wins; it did not generate an interior compromise in this architecture. [VERIFIED: pinned `v6/situational_advice/results.md:5-24`; local `v6/situational_advice/experiments/findings_summary.json`, keys `main_joint_interior_d`, `fixed_tau_interior_d`, and `heldout_interior_d`, each 0]

The strongest mechanism-identification evidence is the stable-environment ablation at adult local precision `.70` and `tau=3`: full interpreted advice selects `d=0`; clean factual teaching selects `d=1`; action-only substitution selects `d=0`; memory-only acceptance selects `d=1`; equal tutor/learner context selects `d=1`. Under hazard `.2`, all five select `d=0`. [VERIFIED: pinned `v6/situational_advice/results.md:42-52`; local `v6/situational_advice/experiments/followups.json`, key `ablations`]

This reversal is evidence that reusable-content acquisition and present-action delegation should not share one coefficient. It is not evidence that memory acceptance is a uniquely authority-sensitive mechanism: ordinary useful social information can produce the same endpoint.

## Construct audit

### What `d` currently means

V6 applies one inherited `d` both to public action substitution and to acceptance of testimony into held conviction. The mathematical specification gives public action probability `(1-d)j(u)+dq_+` and accepted-testimony rate `d*nu_S/load`. [VERIFIED: pinned `v6/mathematical_model.md:19-34`]

The implementation has switchable `accept` and `override` flags, but the same computed weight `w=d` drives both when enabled:

DATA_M3T8K5RP_START
> `accept:bool=True`, `override:bool=True`; current choice uses `act=w if c[18]>0 else 0.`, while memory flux uses `social_weight=w if c[17]>0 else 0.`
DATA_M3T8K5RP_END

[VERIFIED: pinned `v6/situational_advice/experiments/model.py:39-47,91-100,108-147`]

Consequently, V6 does not cleanly identify extra authority response. At `d=0`, social intake and memory are switched off alongside conflict override; this is not the V7 control, where a no-extra-deference individual remains a competent reliability-sensitive social learner.

### Cognitive and life-history structure

V6 has two density stages, not individuals with histories. Each subpopulation carries two bounded integer ledgers about one binary global truth, newborns enter at `(u,b)=(0,0)`, and maturation transfers both ledgers. Adult encoding is prescribed and default private query cost is zero:

DATA_C9V2H6JW_START
> `H:int=3`, `p:float=.65`, `plasticity_F:float=1.`, `plasticity_A:float=.1`, `query_cost:float=0.`
DATA_C9V2H6JW_END

[VERIFIED: pinned `v6/situational_advice/experiments/model.py:13-50`; `v6/mathematical_model.md:5-17`]

The situational extension renews a binary local circumstance at each decision and analytically averages it; local observations are not retained as individual episodes. Accepted action advice is decoded back into general truth using the tutor and juvenile observation channels. [VERIFIED: pinned `v6/situational_advice/mathematical_model.md:5-43`]

Adult knowledge is endogenous in the density dynamics, but “adult” is still a stage and teaching competence is not separately acquired or recorded. The model has no procedural prerequisites, delayed multistep production, teacher search cost, source genealogy, individually limited event budget, or separate factual belief versus learned normative value.

### V5 repertoire boundary

V5 must not be described as purely single-fact. Its companion explicitly uses:

DATA_Z5P1D8FS_START
> `D ∈ {4,16,64}` independent binary facts, a cohort size of `128`, `16` juvenile private cues, `16` social encounters, and `16` adult opportunities for the retained-update policy.
DATA_Z5P1D8FS_END

[VERIFIED: pinned `v5/repertoire_model.md:14-38`]

That companion has fixed cohorts and no births, deaths, density dependence, reproduction weighting, invasion, or selection. Its facts are independent and lack prerequisites, recombination, demonstrations, full action sequences, and task-level rewards. [VERIFIED: pinned `v5/repertoire_model.md:8-12,163-173`]

## Retain versus replace

| V6 asset | V7 decision | Reason |
|---|---|---|
| Immutable V1-V6 results and dashboards | **Retain unchanged** | They are legitimate negative/endpoint findings and essential comparators. |
| Exact birth-death-maturation and resource accounting | **Retain pattern; reimplement for individuals** | V7 still needs closed demographic and energy ledgers. |
| Common environmental paths and paired comparisons | **Retain and strengthen** | Keyed event streams should preserve pairing even when policies take different numbers of actions. |
| Conservative learning transitions, neutral controls, self-mutant checks, solver cross-checks | **Retain as validation principles** | They prevent numerical and accounting artifacts. |
| V5 distinct knowledge items and matched schedules | **Retain as fixtures/controls** | Useful for regression tests and comparison with prerequisite-structured procedures. |
| Scalar bundled `d` | **Retain only as a V6 bridge comparator** | Replace as the main construct with separate ordinary learning, procedure conflict override, and local-action override. |
| Two homogeneous density stages | **Replace** | Individual histories, source lineages, acquired competence, event budgets, and norms require an individual-based life history. |
| Prescribed adult encoding `.1` | **Replace as a default assumption** | Adult persistence must arise from explicit histories, habits, verification choices, or a separately tested evidence gate. |
| Zero default private-query cost | **Replace** | Learning, verification, demonstration, teaching, and production must compete for real opportunities. |
| One binary changing truth | **Replace as main task** | Use reusable multistep procedures plus faster private local contexts; retain the binary world as a regression fixture. |
| Analytically averaged fresh local circumstance | **Replace as main context** | Persist observable individual episodes and tutor delay/distance so context mismatch is measurable. |
| Common-resident conditional invasion only | **Retain for parity, then extend** | V7 needs newborn mutant introduction, resident cultural exposure, both invasion directions, direct competition, and multiple cultural initial conditions. |
| Existing export/provenance/portal machinery | **Retain** | Add V7 views without rewriting prior versions. |

## Required V7 regression and construct tests

1. Reproduce the fixed-source affine endpoint and selected V6 scalar-`d` results before adding ecology.
2. Under yoked histories, changing conflict override must not change sensors, memory capacity, available messages, or private likelihoods.
3. With extra override set to zero, a learner must still acquire and evaluate demonstrations and testimony using the common social-learning mechanism.
4. Separately switch procedure acquisition, present-action override, epistemic authority credit, approval value, and internalized norm value.
5. Reproduce the V6 ablation logic in a tiny world: message content, current execution, and memory must have separable causal effects.
6. Preserve V6's result labels: abundance optimum, conditional invasion maximum, fixation, and ESS are distinct claims.
7. Never relabel persistence without accessed counterevidence as dogmatism. Record factual posterior, public behavior, private behavior, and normative obligation separately.

## Audit conclusion

V6 is internally explicit about its limitations and its results remain valid for the tested bundled mechanisms. The decisive V7 change is not “more noise” or a forced interior optimum. It is construct identification: preserve ordinary social learning and private ability, then measure any additional conflict override, authority credit, approval sensitivity, and learned normative commitment on separate channels. The situational ablations already supply the local evidence for making that split.
