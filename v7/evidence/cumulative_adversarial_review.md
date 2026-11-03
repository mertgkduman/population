# Adversarial review: exploratory cumulative-procedure assay

## Verdict

**PARTIAL — do not claim genuine V7 cumulative procedural complexity, selection, or a deference advantage.** The assay demonstrates a narrow, deterministic two-cohort causal composition chain: a blank successor can perform a depth-3 held-out procedure only after paid prefix transmission and later private completion. That is useful feasibility evidence for a separate cognitive mechanism. It is not sufficient evidence that the frozen IBM has cumulative culture, that the mechanism would persist under the planned ecology, or that it supports H2 or any demographic/selection inference.

The strongest defensible statement is: *under these registered toy-work assumptions, paid transmission of two causal prefixes plus a later paid completion lets a blank second successor execute two depth-3 procedures with nonzero held-out performance.* It must retain the existing `PARTIAL` label.

## Evidence inspected

| Item | Result |
| --- | --- |
| Commit | `b6c39c3 feat(v7-3a): run cognitive cumulative-procedure assay` |
| Code/test | `v7/experiments/cumulative.py`, `v7/tests/test_cumulative.py` |
| Registration | `v7/evidence/cumulative_registration.json`, source SHA `bfe076b9df46529672f6f7e9f04023feb70c7e1c2e64d3b7e9a1834d14f14bfb` |
| Raw export | `v7/experiments/output/cumulative_assay.csv.gz`, SHA-256 `1d19bbb5d9e18ae02a8b6da2c7a4b3a85247fdf8c70f8b82d7b39dcb3bb0063c` |
| Executed tests | `python -m unittest v7.tests.test_cumulative -v`: 3/3 passed |
| Design | 4 pilot seeds (`73997..74000`), then 24 fresh seeds (`74001..74024`) × 6 registered arms = 144 confirmation rows |

The transmission-plus-innovation arm reports useful depth 3, 48 two-edge functional procedures (two per confirmation seed), and mean held-out score 0.7083. It has two genuinely different procedures (`water`, `shelter`), blank constructed cohort members, paid teacher and learner transfers, and terminal source-history strings. Those are real positives, but they do not cure the limitations below.

## What is and is not causally established

### Narrowly established

- Individual private work is capped at two successful 30-unit verification events under a 60-unit lifetime budget; a single normal learner cannot complete the three-module procedure by private verification alone.
- The main arm transfers two prefixes with one unit debited to both teacher and learner per transmission, permits a later private third-module completion, then transfers the functioning sequence to a blank second successor.
- The exported held-out measure is an action/task outcome conditioned on functional prerequisite depth, rather than a confidence or statement-count measure.

### Blocking limitations

1. **Controls are not total-work matched.** Per exported confirmation cell, private plus teaching work is 200 for `transmission_innovation`, 120 for `no_transmission`, 128 for `transmission_without_modification` and `shuffled_or_removed_prerequisites`, 240 for `innovation_without_retention`, and 300 for the alleged pooled-work upper bound. The upper-bound learner is explicitly assigned three private verifications (90 private work) despite the nominal 60-unit individual lifetime bound. It can remain an idealized upper bound, but cannot be described as a matched independent solver.
2. **The five zero ablations are largely all-or-nothing construction effects.** The terminal cohort is deliberately blank in no-transmission, transmission-without-modification, and innovation-without-retention branches. Their zero held-out score therefore does not measure the useful-prefix benefit or distinguish loss of modification from loss of retention. Prefix performance is not exported as a counterfactual outcome.
3. **The shuffled/removed-prerequisite condition does not isolate prerequisite structure.** Its `shuffled=True` branch removes teaching-side prerequisite checks, but it still transfers the same first two modules and does not enable the third-module innovation. Its zero is consequently confounded with the no-modification arm, not evidence that a shuffled causal graph harms a matched functional procedure.
4. **Private verification has no modeled error or observed evidence outcome.** Every eligible private verification succeeds deterministically. The code records source-history labels, but those labels do not calibrate a source or alter a later decision. This is not a fixed-accuracy evidence comparison and does not distinguish ordinary social learning from a source-sensitive learner.
5. **There is no ordinary-social `d=0` versus asocial/access-off comparison.** No `d` appears in the assay and no judgment-conflict policy is exercised. This is appropriate for avoiding a manufactured authority result, but it blocks any claim about deference, H2, or a specific V7 social-policy competitor.
6. **Blank-state evidence is weakly audited.** All cohorts are constructed blank in code, but the exported `all_newborns_blank` field checks a newly constructed audit learner rather than the actual cohorts. This is not an evidence of contamination, but it is not a strong data-level blank-state audit.
7. **The exact equality of the main-arm and pooled-upper-bound score (0.7083) is not a performance advantage.** It is compatible with the same depth-3 success kernel and a fixed small sample. It should not be ranked or interpreted as cultural superiority.

## H1–H9 synthesis recommendation

| Item | Recommendation |
| --- | --- |
| `ACCUM-01` / §5.1 | Keep **PARTIAL**. Cite a cognitive two-edge feasibility demonstration only; do not say cross-generation cumulative complexity is established in the IBM. |
| `ACCUM-02` | **NOT TESTED** by this assay. It has no carrier-death or artifact-storage manipulation. |
| H2 | **NOT TESTED**. No inherited override/deference competitor is evaluated. |
| H3/H4/H6 | Do not update from this assay. |
| H8 | Do not update from this assay; there is no provenance-root or repeated-testimony manipulation. |
| H9 | Do not update from this assay; it has no ecology, root diversity, shock recovery, or demographic outcome. |

For future strengthening, use the same causal graph with exported cohort-level prefix outcomes, a genuinely shuffled graph that retains the same modification opportunity and work, a cost-matched independent multi-agent comparator that respects the 60-unit lifetime constraint, observed private verification errors/evidence, and a separately labeled `d=0` versus asocial decision comparison. Those additions must remain outside the frozen core unless separately planned.
