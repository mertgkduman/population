# V5 repertoire companion: actual knowledge coverage under finite access

**Status:** predeclared companion experiment completed 2026-10-30  
**Implementation:** [`experiments/repertoire.py`](experiments/repertoire.py)  
**Raw generation summaries:** [`experiments/repertoire.csv`](experiments/repertoire.csv)  
**Endpoint summaries and validation:** [`experiments/repertoire.json`](experiments/repertoire.json)

## Purpose and claim boundary

The main V5 ODE uses `D` as a rate divisor—an effective information-load or repertoire-dilution parameter. It does not represent multiple things to know. This companion addresses that limitation directly: each organism carries separate private and held scores for `D=4,16,64` independent binary facts. It can therefore measure knowledge coverage, between-context heterogeneity, cultural retention, and recovery context by context.

This is not a replacement for the demographic model. Cohorts are fixed at `N=128`; there is no birth, death, density dependence, reproduction weighting, mutant invasion, or selection. It supports claims about learning and cultural transmission only. Independent binary facts also do not constitute combinatorial reasoning, multi-step skill, cooperation, social norms, teaching, or a dependency-structured technology. Computational score capacity and sampling budgets are equal within every scenario.

## Predeclared design

No parameter was tuned after seeing results.

| Component | Value |
|---|---|
| Repertoire size | `D ∈ {4,16,64}` independent binary facts |
| Cohort size | 128 organisms |
| Generations | 24 recorded cohorts; generation 0 is the acquired founder cohort |
| Score state | Per-fact private `u` and held `b`, integers bounded to `[-4,4]` |
| Private cue quality | `p ∈ {0.55,0.70,0.90}` |
| Homogeneous deference | `d ∈ {0,0.5,1}` |
| Juvenile private budget | 16 random-context cues; each cue moves both `u` and `b` |
| Juvenile social budget | 16 random-context encounters with random adults from the prior cohort |
| Social update | A nonzero adult `sign(b)` is accepted with probability `d` and moves child `b` only |
| Current conflict action | A child follows conflicting nonzero adult advice with probability `d`; this is recorded but does not alter payoffs |
| Adult retained-update | 16 additional private cues |
| Adult frozen | 0 additional private cues |
| Adult confidence-audit | 16 opportunities; query when `abs(b)<2`, otherwise with probability 0.05 |
| Founder acquisition | All founders start `u=b=0`, then receive 16 common private-cue opportunities before teaching |
| Environments | Stable; or exactly 25% of context truths flip before generation 12 learns |
| Replication | Seeds 501–506 |
| Full grid | 972 runs, 23,328 run-generation rows, 162 six-seed aggregate cells |

All adult advice is endogenous. A learner samples the prior cohort's actual `b` for the selected context; there is no fixed teacher accuracy. Founder quality is an observed result of their 16 private cues, not an initialization parameter. Private-only `d=0` learners retain childhood knowledge and satisfy `u=b` exactly.

### Common random numbers

Within each `D × seed` block, every matched `p`, `d`, adult policy, and environment reuses the same initial truths, flip mask, sampled contexts, teacher identities, cue-quality uniforms, testimony-acceptance uniforms, conflict-override uniforms, private tie breaks, and audit uniforms. Correct-cue sets are nested across `p`: every cue correct at `p=.55` is also correct at `.70` and `.90`.

Stable and quarter-flip runs are exactly identical through generation 11. State-dependent audit eligibility and endogenous teacher signs necessarily diverge after policies produce different `b` states. SHA-256 hashes for all 18 `D × seed` schedules are stored in the JSON.

## Update order

For each nonfounder generation:

1. Apply the truth flip at generation 12 in the shock environment.
2. Freeze the preceding adult cohort as the current teachers and score its accuracy against current truth.
3. Initialize the new cohort at `u=b=0`.
4. Give every juvenile 16 private cues on random contexts; each cue moves both ledgers.
5. Give every juvenile 16 random-context encounters with random prior-generation adults. Nonzero testimony is accepted with probability `d` and moves `b` only.
6. Record private–adult action conflicts and stochastic overrides. A private tie is resolved by a pre-generated fair coin; a teacher with `b=0` supplies no testimony.
7. Apply the adult update, frozen, or confidence-audit query policy.
8. Score the adult cohort; it becomes the sole teacher pool for the next generation.

The true-state shock occurs before teacher accuracy is scored at generation 12. Thus the immediate teacher-accuracy loss measures how much previously accumulated culture has become obsolete.

## Metrics and output schema

The CSV has one row per run-generation. Core fields are:

- identifiers: `run_id, seed, D, p, d, policy, environment, generation`;
- knowledge: `adult_accuracy, private_accuracy, held_coverage, private_coverage`;
- confidence and heterogeneity: `held_confidence, private_confidence, wrong_high_confidence, knowledge_heterogeneity, context_accuracy_sd, context_coverage_sd`;
- information use: `juvenile_private_queries, juvenile_social_encounters, adult_queries`;
- endogenous source quality: `teacher_accuracy, teacher_accuracy_expressed, teacher_coverage, teacher_knowledge_heterogeneity`;
- social action: `social_testimonies, accepted_social_testimonies, child_conflicts, child_overrides, child_conflict_override_rate`.

Accuracy assigns 0.5 to an unknown (`score=0`) fact. Coverage is the fraction of organism–context scores that are nonzero. Knowledge heterogeneity is the mean across facts of within-cohort variance in correctness scores `{0,0.5,1}`. This keeps lack of coverage distinct from confidently wrong knowledge.

The JSON stores exact parameters, schedule hashes, invariant results, all 972 endpoint summaries, and six-seed mean/SD aggregates. Shock summaries include pre-shock accuracy (generations 9–11), generation-12 accuracy, final recovery fraction, first generation reaching 90% recovery, and mean post-shock accuracy.

## Verification results

All predeclared checks passed:

| Check | Measured result |
|---|---|
| `d=0` retained-knowledge invariant | Maximum `abs(u-b) = 0` over every context, organism, generation, policy, environment, and seed |
| No-signal test | Accuracy 0.5, coverage 0, and no nonzero score |
| Founder acquisition | Exactly 16 queries per founder; identical within matched `D,seed,p`; no fixed source accuracy |
| Matched cue quality | Nested correct-cue sets across `.55 ≤ .70 ≤ .90` |
| Matched environments | Maximum stable versus shock difference before generation 12: 0 |
| Private-channel isolation | Under frozen and unconditional retained-update policies, private accuracy/coverage is identical across `d`: maximum difference 0 |
| Score bounds | Maximum observed absolute score 4 |
| Adult query policies | Retained-update exactly 16 per adult-generation; frozen exactly 0; audit observed range 0.609–15.727 |
| Conflict override | Aggregated rates: 0 for `d=0`, 0.4983 mean for `d=.5`, and 1 for `d=1` |

## Measured results

### 1. Social testimony improves stable-world accuracy, but its marginal value shrinks with a larger actual repertoire

The table averages the end-accuracy and coverage difference from the matched `d=0` control across all three cue qualities and adult policies (nine cells per entry).

| Actual repertoire | `d=.5` accuracy Δ | `d=1` accuracy Δ | `d=.5` coverage Δ | `d=1` coverage Δ |
|---:|---:|---:|---:|---:|
| 4 facts | +0.0612 | +0.1518 | +0.0337 | +0.0615 |
| 16 facts | +0.0336 | +0.0691 | +0.0568 | +0.1059 |
| 64 facts | +0.0069 | +0.0145 | +0.0234 | +0.0494 |

Every stable-world aggregate cell had a positive accuracy difference from its matched `d=0` control, but the mean benefit at `D=64` was only 0.0145 even under `d=1`. With fixed 16-event private and social budgets, a larger repertoire spreads encounters thinly across facts. Testimony still increases coverage, yet most facts lack enough repeated, independent evidence for strong accuracy gains.

This is the central result that a pure rate divisor cannot show: cultural access can broaden coverage while delivering progressively smaller per-fact accuracy gains as the number of actual facts grows.

### 2. Freezing is advantageous only in a narrow, dense-repetition corner

Stable-world held accuracy under full deference (`d=1`) was:

| `D` | `p` | Confidence audit | Frozen | Retained-update |
|---:|---:|---:|---:|---:|
| 4 | .55 | .9100 | **.9261** | .8477 |
| 4 | .70 | **.9902** | .9827 | .9854 |
| 4 | .90 | .9997 | .9990 | **.9998** |
| 16 | .55 | .5828 | .5656 | **.5834** |
| 16 | .70 | **.7956** | .7341 | .7948 |
| 16 | .90 | .9411 | .8822 | **.9413** |
| 64 | .55 | .5232 | .5139 | .5232 |
| 64 | .70 | .5954 | .5557 | .5954 |
| 64 | .90 | .6880 | .6107 | .6880 |

Freezing led only at `D=4,p=.55`, where many encounters revisit the same few facts and private evidence is weak. In that corner, recurrent testimony allows a coherent cultural majority to persist while additional noisy private cues can erode it. Once the repertoire expands, frozen adults have insufficient coverage and are consistently worse than update/audit adults. This is a learning result, not a fitness advantage: frozen adults pay no modeled biological cost here because this companion has no fitness function.

### 3. Confidence auditing saves queries only after confidence can accumulate

Retained-update adults made 368 postfounder queries over generations 1–23 in every run; frozen adults made none. Under `d=1`, confidence-audit totals were:

| `D` | `p=.55` | `p=.70` | `p=.90` |
|---:|---:|---:|---:|
| 4 | 64.4 | 30.0 | 19.3 |
| 16 | 250.9 | 215.8 | 152.1 |
| 64 | 354.2 | 351.8 | 344.2 |

For four facts, repeated evidence quickly crosses the audit threshold and the audit policy approaches update-level accuracy with far fewer queries. For 64 facts, most context scores remain low, so the audit policy queries almost as often as retained-update and has essentially identical accuracy. The audit rule therefore adapts its effort to represented coverage, but it should still be described as an imposed heuristic rather than an optimal stopping policy.

### 4. A real state change exposes the risk of frozen low-quality culture

The clearest persistence–recovery contrast occurred at `D=4,p=.55,d=1`:

| Adult policy | Pre-shock accuracy | Generation-12 accuracy | End accuracy | End recovery fraction |
|---|---:|---:|---:|---:|
| Confidence audit | .8967 | .7127 | .8963 | .9964 |
| Frozen | .9214 | .7207 | .7922 | .3575 |
| Retained-update | .8432 | .7012 | .8449 | 1.0109 |

Frozen adults began with the best stable knowledge in this low-quality, four-fact corner but retained obsolete convictions after 25% of truths changed. Audit and retained-update recovered essentially all lost accuracy by the end; frozen recovered only about 36%. At `p=.70` and `.90`, even frozen lineages recovered because accurate juvenile private cues rebuilt the teacher pool across generations, although recovery lagged updating policies.

At `D=64`, the immediate shock loss was small (for `d=1`, roughly 0–0.016 depending on `p` and policy), but this is not evidence of robust knowledge: absolute end accuracy was only .514–.688. The cultural state was too sparse to be strongly correct before the shock, so there was less accumulated accuracy to lose.

## Interpretation

The companion supports four restrained conclusions:

1. Endogenous social testimony can aggregate weak evidence in a stable world, especially when a small actual repertoire is revisited often.
2. Increasing the number of facts at fixed learning budgets raises the value of social transmission for coverage but dilutes its accuracy benefit per fact.
3. Freezing is not generally superior to competent retained private learning. Its only leading stable cell is the small-repertoire, low-cue-quality condition, and that same condition shows its sharpest failure after real change.
4. Confidence auditing is economical only when the evidence process can actually build confidence; in a large sparse repertoire it approaches continuous updating.

These results complement rather than duplicate the main ODE. The ODE addresses population dynamics and selection-related questions; this model shows how finite access is distributed across represented knowledge. No abundance, mortality, or invasion conclusion should be drawn from this companion.

## Limitations and next discriminating tests

- Facts are independent and equally likely to be sampled. There are no prerequisites, complementarities, recombination, or task-level rewards.
- Adults transmit only `sign(b)`, not confidence, provenance, demonstration quality, or full action sequences.
- Random teachers can share cultural ancestry; source-lineage correlation is generated implicitly but not labeled or corrected by the learner.
- Every generation is a new fixed-size cohort. The experiment does not model overlapping ages, parent choice, reproduction, or demographic filtering.
- Deference is homogeneous within a run and controls both testimony acceptance and conflict override. Since override is observational only here, held-knowledge effects arise through acceptance, but a future behavioral-reward model should split the channels.
- Recovery after the 25% flip is driven by new private evidence and cohort replacement. It is not learner-side identification of whether evidence is misinformation or true environmental change.
- Six paired seeds characterize Monte Carlo variation for this bounded companion; they are not a basis for population-level empirical calibration.

A genuinely compositional extension would assign dependencies among subskills and let teachers expose selected procedures rather than isolated signs. That is outside this experiment and should not be inferred from the present `D` effects.

## Reproduction

From the repository root:

```bash
python v5/experiments/repertoire.py --self-test-only
python v5/experiments/repertoire.py
```

The first command runs a lightweight deterministic invariant check. The second regenerates all 972 runs and overwrites only `v5/experiments/repertoire.csv` and `v5/experiments/repertoire.json`.

---

## Exploratory post-main follow-up: observable-confidence tutor search

**Status:** exploratory mechanism-identification analysis prompted by the main repertoire dilution result; it is not a preregistered confirmation.  
**Implementation:** [`experiments/repertoire_tutors.py`](experiments/repertoire_tutors.py)  
**Generation summaries:** [`experiments/repertoire_tutors.csv`](experiments/repertoire_tutors.csv)  
**Paired summaries:** [`experiments/repertoire_tutors.json`](experiments/repertoire_tutors.json)

### Question and mechanism

The main companion samples a random prior-generation adult. That mixes adults with formed convictions, weak one-cue impressions, and no knowledge of the selected context. The follow-up asks whether the observed dilution is partly a **source-access problem** rather than an absence of cultural knowledge.

Two teacher rules are paired:

- **Random:** sample one random prior-generation adult; `b=0` returns no testimony.
- **Observable-confidence filter:** search the prior cohort for adults satisfying `abs(b_context)≥2`, then uniformly sample one qualifying adult. If nobody qualifies, return no testimony and retain the child's private knowledge/action.

The filter never observes truth, past correctness, payoff, age, prestige, or genotype. Confidently wrong adults are eligible. All adult knowledge still comes from the same founder, juvenile, social, and adult acquisition processes as in the main companion; no experts are generated or assigned.

This filter receives **cost-free full-cohort search**. That is a deliberately favorable mechanism probe, not an optimal policy. The outputs therefore retain candidate-pool fraction, search availability, endorsements returned, endorsements accepted, and conditional advice accuracy. Any practical claim would need to price search or constrain the visible candidate set.

### Fixed exploratory grid and pairing

The grid uses `D={4,16,64}`, `p={.55,.70}`, `d={0,.5,1}`, all three adult policies, stable and quarter-flip environments, and six new seeds 800–805. Cohort size, 16 private cues, 16 social encounters, 16 adult opportunities, score bound, audit rule, generation count, and generation-12 truth flip are unchanged. The full comparison contains 1,296 runs, 648 paired filter contrasts, 108 six-seed aggregate cells, and 31,104 generation rows.

Within each `D × seed` block, teacher rules share initial truths, flip contexts, private and adult cues, social contexts, the underlying teacher-choice variate, testimony-acceptance draws, conflict-override draws, tie breaks, and audit uniforms. For random sampling, the common teacher variate maps over all 128 adults; for filtering, it maps to a rank within the eligible set.

All checks passed:

- `d=0` satisfies `u=b` exactly and produces identical accuracy, coverage, and queries under both teacher rules;
- matched stable and shock runs are identical through generation 11;
- cue-correctness sets are nested across `p`;
- all founders acquire evidence from exactly 16 cues rather than fixed accuracy;
- scores remain within `[-4,4]`;
- the filtered rule uses only `abs(b_context)≥2`, and an empty eligible set returns no testimony.

### Result 1: confidence filtering partially reverses actual-repertoire dilution

The table reports **filtered minus random** final held accuracy under full deference in the stable environment.

| `D` | `p` | Confidence audit | Frozen | Retained-update |
|---:|---:|---:|---:|---:|
| 4 | .55 | +.0086 | +.0212 | +.0452 |
| 4 | .70 | −.0003 | +.0011 | +.0023 |
| 16 | .55 | +.0772 | +.1646 | +.0874 |
| 16 | .70 | +.0494 | +.0962 | +.0518 |
| 64 | .55 | +.0258 | +.0460 | +.0275 |
| 64 | .70 | +.0547 | +.0773 | +.0550 |

Filtering adds little once four-context culture is already near saturation. It adds substantially at 16 contexts and remains helpful at 64, particularly for frozen adults. This identifies one source of the main dilution result: random encounters often reach ignorant or weakly committed adults even when the cohort contains a smaller set of strongly committed tutors.

The filter does not eliminate dilution. Averaged across adult policies under `d=1`, filtered final accuracy at `D=64` is only .5530 for `p=.55` and .6439 for `p=.70`. Selective access improves which information is transmitted, but fixed encounter budgets still limit repertoire coverage and the amount of independent evidence per fact.

### Result 2: the benefit combines better advice with far more available endorsements

Stable `d=1` summaries averaged across adult policies were:

| `D` | `p` | Eligible pool fraction, filtered state | Search availability | Filtered advice accuracy | Random advice accuracy | Filtered endorsements | Random endorsements |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | .55 | .838 | 1.000 | .930 | .876 | 47,104 | 44,013 |
| 4 | .70 | .941 | 1.000 | .991 | .983 | 47,104 | 46,278 |
| 16 | .55 | .393 | 1.000 | .792 | .603 | 47,104 | 33,828 |
| 16 | .70 | .511 | 1.000 | .960 | .841 | 47,104 | 36,287 |
| 64 | .55 | .071 | .989 | .678 | .556 | 46,595 | 16,290 |
| 64 | .70 | .091 | .994 | .931 | .724 | 46,802 | 16,599 |

At `D=64`, only about 7–9% of adults qualify for an encountered fact, yet a global search almost always finds at least one because the cohort has 128 adults. The filter therefore returns nearly the maximum possible 47,104 endorsements per run, while random sampling returns only about 16,000. The accuracy gain cannot be attributed to discernment alone: it combines **higher conditional advice quality** with **roughly threefold greater testimony availability**. Search is free in this experiment, so these results do not establish that filtered tutoring is net beneficial once discovery time, attention, competition, or access costs are included.

The wrong-confidence risk is visible rather than removed. At `D=64,p=.55`, qualifying pools are about 32% wrong on average in the filtered trajectories, and selected advice is only .678 accurate. Confidence is an informative cue in these runs, not an oracle.

### Result 3: true change can turn confidence selection into a persistence trap

The sharp boundary is again `D=4,p=.55,d=1` after 25% of truths flip:

| Adult policy | Teacher rule | Pre-shock | Shock generation | End | End recovery fraction |
|---|---|---:|---:|---:|---:|
| Confidence audit | Filtered | .9245 | .7288 | .8592 | .6672 |
| Confidence audit | Random | .9068 | .7227 | .9009 | .9776 |
| Frozen | Filtered | .9520 | .7313 | .7295 | −.0140 |
| Frozen | Random | .9260 | .7236 | .8283 | .5237 |
| Retained-update | Filtered | .8944 | .7257 | .8896 | .9744 |
| Retained-update | Random | .8443 | .7090 | .8464 | 1.0283 |

Before the shock, filtering makes culture more accurate and confident. Immediately after the shock, that same confidence points learners toward obsolete tutors. Continuous retained updating eventually converts the filtered advantage into improved end accuracy (+.0433 versus random), but audit filtering ends .0417 below random and frozen filtering ends .0988 below random. Under frozen filtered teaching, recovery is effectively absent by generation 23.

This is not misinformation identification. The selector observes confidence only and cannot know whether confidence was earned under the current truth. The result is a direct counterexample to “formed convictions are necessarily better tutors”: observable confidence helps in stable or recoverable settings but can amplify obsolete, confidently wrong culture after real change.

### Exploratory interpretation

The follow-up supports a narrower mechanism claim:

> Actual-repertoire dilution partly reflects difficulty locating knowledgeable sources. Observable conviction can improve advice quality and restore testimony availability, but cost-free cohort-wide search and environmental stability are doing important work; after change, confidence filtering can retard correction unless adults continue to acquire private evidence.

It does not support claims that confidence is generally calibrated, global tutor search is free or optimal, filtered teaching raises fitness, or adults are intrinsically expert. There is still no demography or selection in this companion.

To reproduce this separate follow-up without rerunning the main grid:

```bash
python v5/experiments/repertoire_tutors.py --self-test-only
python v5/experiments/repertoire_tutors.py
```
