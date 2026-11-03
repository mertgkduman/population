# V7 constructs and estimands

**Purpose:** fix what each V7 variable and comparison means before implementation or result selection. This document does not report simulated evidence. The model notation is defined in [`model_candidates.md`](model_candidates.md).

## Unit, treatment, and observation conventions

- The mechanistic unit is an individual decision opportunity embedded in an individual life history.
- The ecological unit is a complete stochastic population trajectory from acquired founder culture through a prespecified horizon, including extinction.
- The evolutionary unit is a policy-mutant newborn created by an actual paid resident birth and compared with a matched neutral newborn in the same resident resource/culture state.
- `do(.)` below means a simulator intervention on a declared policy/module while holding paired exogenous streams and starting observed state fixed where possible. It is not a claim about identification from observational data.
- Evaluator-only truth may score performance but is excluded from ordinary policy inputs. Every estimand states whether it is a yoked immediate contrast, a total life-history contrast, or a selection contrast.

## Construct map

| Construct | Operational state/measure | Explicit nonexample |
|---|---|---|
| Factual belief | `B_i`: posterior over structural bits or current local condition, updated only by declared observations/likelihoods | The action taken, cached recipe, approval habit, or simulator truth |
| Procedural knowledge | `K_i`: stored executable sequence plus provenance, practice, and observed outcomes | A true recipe silently granted by the simulator |
| Causal understanding | Calibrated predictive beliefs about how action changes transition/outcome probabilities, scored on held-out interventions | High task yield alone or memorizing the right sequence |
| Action | Publicly executed step/recommendation response at one event | A belief update or permanent memory acceptance |
| Source reliability estimate | `T_i`: finite-history estimate based on observable scored claims, domain, and provenance | True source accuracy or evaluator-rated competence |
| Actual competence | Evaluator-scored expected physical yield on held-out task episodes using the individual's current `K/B` | Age, confidence, prestige, or teaching eligibility |
| Observable mastery | Age-neutral offer-to-teach rule based on a stored procedure and logged independent successful attempts | Oracle access to actual competence |
| Ordinary social learning | Content and demonstrations affect `B`, `K`, `T`, and therefore neutral value `Q^0` | Extra conflict override |
| Behavioral deference | Following advice only when the common neutral material-value action conflicts, caused by `d_procedure` or `d_local` | Following because evidence/reliability makes advice best |
| Epistemic deference | A later, separately enabled authority-credit term changes factual updating under matched content/reliability | Candidate A's behavioral override by itself |
| Approval sensitivity | Current expected approval enters motivation with weight `gamma`, separate from material value | Food, energy, fertility, or factual likelihood |
| Learned action habit | `H_i(a)`, acquired through evaluative reinforcement and capable of persisting without an audience | Frozen belief, an obligation representation, or an adult-only learning deficit |
| Internalized obligation | An explicitly represented, acquired obligation generalizes appropriately and persists after audience, tutor, sanction, and promised social reward removal, while surviving habit probes | Compliance while monitoring remains or cached instrumental habit alone |
| Epistemic dogmatism | Deficient or source-asymmetric factual revision after accessible, informative, matched counterevidence relative to a likelihood-aware benchmark | Strong justified prior, absent evidence, or persistent obligation after belief revision |
| Cultural accumulation | Cross-generation transmission plus modification increases functional held-out performance/depth beyond work-matched no-transmission controls | More statements, confidence, or storage alone |
| Biological genealogy | Parent-child edges created by costly births | Teacher-learner relation |
| Cultural genealogy | Content-specific transmission/modification edges with provenance roots | Genetic inheritance or a free global library |

## The ordinary social learner at `d=(0,0)`

This definition is a hard validation target. The ordinary social learner:

1. observes demonstrations and messages;
2. enters their content into likelihood/value calculations using learned source reliability and provenance;
3. can store, practise, modify, and teach acquired procedures;
4. can choose the tutor's action whenever that action maximizes `Q^0`;
5. refuses only the *additional stochastic override* when its own neutral action conflicts.

Therefore `d=0` cannot be called private-only, asocial, skeptical, nonencoding, or low-memory. The asocial control is a different intervention that removes cultural access while preserving private budgets/hardware.

## Primary causal contrasts

Let `Y` be a prespecified outcome and `omega` a paired exogenous world/event stream.

### 1. Value of cultural access

$$
\tau_{social}(Y)=E_\omega\left[Y\{do(\text{ordinary social},d=(0,0))\}
-Y\{do(\text{asocial access-off})\}\right].
$$

This estimates the total value of social content under the specified costs. It is not the effect of extra deference.

### 2. Immediate extra-deference effect under yoked history

For a conflict event in domain `k`, freeze the same observed history, content, source estimate, energy, and random outcome schedule. Define

$$
\tau^{yoked}_{defer,k}(u\mid h)=E\left[u(a^{d_k})-u(a^{0})
\mid a_T\ne a^0, h,k\right],
$$

where `u` includes the common declared current and downstream material horizon. This is the clean immediate effect of conflict override. No later exposure, survival, or cultural mediation is included.

Naturally observed conflict is policy-affected and can induce selection bias. Create the primary conflict-conditional estimand by freezing a common pre-override state and inducing/randomizing the override switch. Always accompany it with an unconditional intention-to-treat contrast over all assigned decision opportunities. Apply the same caution to analyses restricted to available teachers, survivors, or agents able to afford audit.

### 3. Total ecological policy effect

$$
\tau^{eco}_{g,g'}(Y;T)=E_\omega[Y_T\{do(g)\}-Y_T\{do(g')\}],
$$

for complete trajectories with each policy allowed to alter its future learning, source access, demography, and culture. This total effect must not be interpreted as the immediate conflict effect.

Primary comparisons are vector policy versus ordinary social, scalar restriction versus vector, and each versus feature-trust/resource-rational policies. Compare asocial only to identify the value of cultural access.

### 4. Domain dissociation and scalar restriction cost

For procedure depth/opacity `O` and tutor-context match `chi`, estimate the factorial surface

$$
M(d_p,d_l;O,\chi)=E[Y\mid d_{procedure}=d_p,d_{local}=d_l,O,\chi].
$$

The scalar restriction cost is

$$
L_{scalar}=\max_{d_p,d_l}M(d_p,d_l)-\max_d M(d,d).
$$

Report the selected coordinates and their uncertainty. A corner such as `(1,0)` is domain specialization, not indiscriminate obedience and not an "interior optimum." Distinguish: an individual's stochastic interior propensity; a conditional policy whose average following is intermediate; and a polymorphic population of near-endpoint types.

### 5. Authority-label effect

Hold message content, demonstrator behavior, observable reliability history, timing, and costs fixed; randomize an explicitly uninformative authority/age label. Then

$$
\tau_{label}=E[Y\{do(L=authority)\}-Y\{do(L=neutral)\}].
$$

For the label-neutral ordinary learner, the action distribution and belief update must be invariant. A nonzero label effect is interpretable as authority response only if the learner knows the label is uninformative; otherwise it may be rational reliability inference. Assign the label before the decision and report its unconditional intention-to-treat effect as primary. A conflict-only label effect is a mechanism summary from the frozen induced-conflict assay, not a substitute for the unconditional contrast.

### 6. Content, memory acceptance, and override factorial

Use three independently assigned switches after common message exposure: social content enters neutral evaluation (`C in {0,1}`), the proposed procedure may be accepted into durable memory (`M in {0,1}`), and extra conflict override is enabled (`O in {0,1}`). The eight cells identify content/evidence, memory acceptance, behavioral override, and interactions. The scientifically central immediate comparison is `(C=1,M=m,O=1)` versus `(C=1,M=m,O=0)` at each fixed `m`, not versus access-off. Message exposure and event budgets remain identical.

## Decision and learning outcomes

### Realized response surface

Among genuine conflicts, estimate

$$
D_k(x)=P(a=a_T\mid a_T\ne a^0,k,x),
$$

where `x` includes age, private confidence, estimated source reliability, observable mismatch, and task depth. Report denominators and uncertainty. Do not replace this conditional surface with population-average `d`.

### Knowledge and understanding

- **Procedure coverage:** fraction of task families for which `K_i` contains an executable sequence.
- **Useful depth:** greatest prerequisite depth completed above a preregistered held-out success/yield threshold.
- **Held-out competence:** mean resource yield net of execution cost on evaluator-held-out worlds; evaluator truth scores but does not guide the agent.
- **Causal calibration:** Brier/log score of predicted transition probabilities on held-out interventions.
- **Procedure-understanding dissociation:** held-out competence stratified by causal-calibration quantile and vice versa.
- **Wrong mastered procedure:** observable mastery is met while held-out competence is below threshold; this keeps confidence/practice separate from truth.

### Task-landscape adequacy

Before selection, report exact/sampled viable-procedure count, safe-option yield, useful-prefix marginal rewards, matched-work private-discovery probability, and minimal successful depth after no-op pruning. A primary world is adequate only when at least two distinct procedures have positive expected net return, prefixes and a safe action have nonzero value, and independent discovery succeeds with nonzero probability. Repeat on task/branch relabelings and prerequisite-shuffled ensembles.

### Source use

Record query rate, teacher-search time, conditional message accuracy, calibration of `T`, unique testimony roots, redundant copies, and action/value changes attributable to social content. Source accuracy is an observed outcome, never a fixed tutor parameter in the main model.

### Learning and teaching costs

Report time tokens and energy/material cost separately for private trials, observations, queries, verification, teaching, computation, and failed production. A net effect must show gross resource yield and every cost component; do not hide teacher time in learner-side averages.

## Demographic and resource estimands

### Ledger identities

For every season verify

$$
N_{t+1}=N_t+B_t-D_t
$$

and

$$
R_{t+1}+\sum_i E_i(t+1)=R_t+\sum_i E_i(t)+G_t
-L_t^{conversion}-L_t^{metabolic}-L_t^{failure}-L_t^{birth}-L_t^{other}.
$$

Transfers cancel in the population sum. Every residual above numerical tolerance is an invalid run, not noise.

### Ecological outcomes

Predeclare and report together:

- gross and net per-capita resource yield;
- births, deaths by cause, survival to maturity, realized offspring, and generation interval;
- finite-window per-capita change `T^{-1} log(N_T/N_0)` with extinction represented explicitly rather than omitted;
- low-density establishment probability under a fixed introduction protocol;
- regulated mean abundance conditional and unconditional on persistence, clearly labeled;
- population extinction probability and time to extinction;
- recovery after structural change, with nonrecovery/censoring included.

Regulated equilibrium growth near zero is not a sufficient fitness measure. Survivor-only means are always secondary and labeled conditional.

## Evolutionary estimands

The default assay assigns the candidate mutation at `n_0` otherwise ordinary resident births after endogenous burn-in. Resident parents pay the full birth cost, newborn energy equals the normal `E_0`, and acquired state is empty. A paired neutral tagged newborn uses the same paid-birth protocol and resident state. An external immigrant protocol is secondary and must debit an explicit source account. Let `N_m^r(T)` be mutant descendants in replicate `r`, including zero.

Before exposure, inspect newborn `B`, `K`, `T`, `H`, and task-specific values. Parent-knowledge permutation, cross-fostering, and held-out task-node/solution relabeling must make acquired content follow cultural exposure rather than biological parent or genotype. Any informative inherited prior is a separately declared/costed treatment, not learned competence.

### Unconditional finite-window descendant expansion

$$
\widehat g_m^{(T)}=T^{-1}\log\left(
\frac{R^{-1}\sum_r N_m^r(T)}{n_0}\right).
$$

Do not compute a mean of `log N_m` only among survivors. Accompany this with the full descendant-count distribution, establishment probability, `P[N_m(T)=0]`, and time-to-lineage-extinction. If all lineages are zero, report extinction and `g=-infinity` rather than adding an unexplained pseudocount. A newborn in a mixed-age resident population is not an age-neutral draw, so `g_m^(T)` is a finite-lineage statistic, not an asymptotic invasion exponent or Lyapunov growth rate.

### Frequency and competition

For runs in which both types remain, the descriptive frequency contrast is

$$
s_T=T^{-1}\left[\operatorname{logit}p_m(T)-\operatorname{logit}p_m(0)\right],
$$

but fixation/extinction masses are reported separately and not discarded. Reciprocal newborn-lineage establishment assays, nearby mutants on both sides, endpoint mutants, and direct multi-strategy competition are needed before describing an interior candidate as locally attracting. Positive finite-window `g_m^(T)` is finite descendant-expansion evidence only, not an asymptotic invasion exponent, ESS, or fixation proof.

### Neutral and exchange tests

- **Self-mutant:** a genetically and culturally identical paid newborn marker, matched on birth state and parental cost, must have zero mean selective contrast within Monte Carlo error.
- **Exchange symmetry:** swapping resident/mutant labels and keyed streams negates the directed contrast when initial numbers/culture are symmetrically swapped.
- **Neutral drift:** fixation/extinction frequencies must agree with the model's neutral finite-population benchmark.
- **Actual resident culture:** mutants sample the existing source pool and resource state; no mutant-only teachers are synthesized.

Burn-in extinction is reported as resident nonestablishment. Any invasion estimate conditional on a surviving resident is explicitly conditional and paired with the unconditional establishment probability.

## Cultural accumulation and genealogy estimands

### Functional accumulation contrast

Let `P_T` be held-out functional performance at generation/time `T`. The primary contrast is

$$
A_T=E[P_T^{transmission+innovation}-P_T^{work\text{-}matched\ no\ transmission}].
$$

Secondary factorial controls are transmission without modification, innovation without retention, no prerequisites with matched marginal rewards, and total-work-matched independent solvers. `A_T>0` plus increasing useful depth across cultural generations supports accumulation; storage, population confidence, or repertoire count alone does not.

### Genealogy measures

- procedure-root survival and time to root loss;
- modification depth from a physically tested ancestor procedure;
- effective independent lineage number `L_eff=1/sum_l p_l^2`, where `p_l` is the share of current procedure carriers descending culturally from root `l`;
- biological-cultural parent overlap and teacher age distribution;
- fraction of transmissions from nonreproductive competent teachers;
- repertoire loss after the last carrier dies.

A kill-all-carriers assay must yield zero future access in the main model. Persistence after carrier loss is permitted only in the explicitly enabled, costed artifact variant.

## Approval, learned persistence, optional obligation, and dogmatism estimands

These are evaluated only after the epistemic model is frozen.

### Compliance under audience

$$
C_{aud}=P(a=a_{approved}\mid audience)-P(a=a_{approved}\mid no\ approval\ history).
$$

This combines current expected approval and acquired habit unless they are separately ablated.

### Audience-removed learned action persistence

After training, remove audience, evaluator, sanctions, promised rewards, and fresh instruction while retaining the individual's acquired `H`:

$$
I_H=P(a=a_{trained}\mid remove\ audience,H)-P(a=a_{trained}\mid remove\ audience,H\ reset).
$$

Hold factual beliefs, procedural knowledge, energy, and test evidence fixed. A positive `I_H` is acquired behavioral persistence; it is not automatically beneficial, factual, normative, or dogmatic.

### Habit versus obligation probes

Run outcome devaluation and contingency degradation. If persistence tracks cached past reinforcement despite a changed action-outcome contingency, habit is sufficient. A stronger internalized-obligation claim requires a separately represented and acquired injunction plus appropriate generalization to novel instances and a countermand probe, while current audience, sanction, promised reward, and material access effects remain absent. If these probes/state are not implemented, use only “learned action persistence.”

### Free-audit response

Set verification time/material cost to zero without changing evidence quality or social consequences. Measure audit uptake, factual posterior change, action change, and net yield separately. If persistence disappears only because audit becomes cheap, the mechanism is bounded verification rather than an age-imposed evidence gate.

### Evidence-equalized revision

For a matched independent evidence sequence with declared log likelihood ratio `LLR`, define the revision ratio

$$
R_B=\frac{\operatorname{logit}B_{post}-\operatorname{logit}B_{pre}}{LLR}.
$$

Compare the distribution of `R_B` to the likelihood-aware ordinary learner, conditional on prior confidence and in both evidential directions. Dogmatism requires deficient or asymmetric revision after verifying that the evidence was observed and encodable. An agent that revises `B` but continues the trained action because `H` remains shows learned action persistence, not factual dogmatism; call it normative commitment only if it also passes the obligation probes.

### Required three-way report

Every persistence result reports:

1. factual posterior revision;
2. public/private action persistence;
3. habit/approval contribution.

This prevents "adult rigidity" from being inferred from behavior alone.

## Exact, approximate, and learned-trust benchmark estimands

In the exact tiny world, compare each visited belief state on:

- action-value error `max_a |Q_hat(a)-Q_exact(a)|`;
- policy regret `V_exact-V_policy` under identical observations and utility;
- hidden-state invariance given identical observed histories;
- calibration of source reliability and local/structural beliefs;
- actual operation count and charged computation cost.

The exact planner's action set contains following, rejecting, querying, auditing, and experimenting. Hence `V_exact>=V_deference` in expectation under the benchmark model. A violation outside Monte Carlo tolerance invalidates the implementation or objective matching. In larger worlds, compare vector deference to both an equally capped rollout planner and feature-based learned trust; no uniquely deferential advantage is supported if either explains the result at equal or lower cost.

## H9 estimand: cultural monoculture debt

For the H9 design in [`model_candidates.md`](model_candidates.md), define pre-change independent lineage diversity `L_eff(0-)` and recovery time

$$
T_{rec}=\inf\{t>0:P_t\ge P_{pre}-\epsilon\},
$$

with `T_rec` right-censored at the declared horizon and nonrecovering/extinct runs retained. The primary test is the controlled effect of `d_procedure x shock` on `T_rec` after matching census, age, energy, mean held-out competence, and repertoire depth at the shock. The mediation claim additionally requires that diversity-preserving reassignment changes recovery while message count/content quality is held fixed.

Rival-specific interventions are energy equalization, source-estimate reset, age matching with a no-birth diagnostic window, and direct matching on mean competence. H9 fails if the proposed diversity pathway does not survive these controls.

## Primary outcome hierarchy and multiplicity boundary

For each spike, choose one primary from the following before opening holdout outcomes:

1. net energy yield for yoked decision assays;
2. extinction-inclusive expected descendant growth for selection;
3. held-out functional performance/useful depth for cultural accumulation;
4. evidence-equalized factual revision for dogmatism;
5. audience-removed action contrast for learned persistence (and obligation only if the extra probes pass);
6. censored recovery time for H9.

All other measures are mechanism diagnostics or secondary outcomes. Do not select a policy separately for every metric and then describe all selected maxima as confirmation.

## Monte Carlo and holdout rules

- Use exactly 4 paired seeds for discovery; they support candidate selection, not confirmation.
- Freeze policies, hyperparameters, primary outcomes, contrasts, and censoring rules before holdout.
- Use at least 24 fresh holdout seeds, unseen task-graph permutations, adjacent parameter values, and independent resident burn-ins.
- Add seeds in batches of eight up to 96 according to the prespecified interval-width rule in [`model_candidates.md`](model_candidates.md), never according to a changing p-value.
- Report seed-level paired contrasts, uncertainty intervals, extinction/fixation masses, and all exclusions/censoring.
- A null, endpoint, corner policy, learned-trust equivalence, or exact-planner dominance is a valid outcome.

## Construct-validity vetoes

No result can support its named construct if the corresponding veto occurs:

| Claimed construct | Veto |
|---|---|
| Extra deference | Comparison is against asocial access-off rather than fully social `d=0`, or no conflict occurred |
| Epistemic deference | Only action changed; belief update was not separately manipulated/measured |
| Dogmatism | Evidence was absent, weak, correlated, inaccessible, or posterior revision was not conditioned on prior/LLR |
| Internalized obligation | Audience, sanctions, promised rewards, or tutor access remained active; or habit/outcome-devaluation/generalization rivals were not tested |
| Cumulative culture | Better performance is explained by more total work, fixed storage, or within-generation learning only |
| Evolutionary advantage | Only isolated abundance/heatmap maxima were evaluated |
| Specialized authority mechanism | Feature trust or resource-rational control matches it at the same information and budget |
| Competent teaching | Teacher status was granted by age or true state instead of acquired observable history |
| Robustness to change | Extinct and nonrecovering runs were removed |

## Provenance and claim boundary

The construct distinctions follow the V7 design brief in [`../V7_RESEARCH_DESIGN_AND_WORK_PROMPT.md`](../V7_RESEARCH_DESIGN_AND_WORK_PROMPT.md). The bundled action/memory behavior being replaced is documented in [`../v6/situational_advice/mathematical_model.md`](../v6/situational_advice/mathematical_model.md); the acquired-founder precedent and its fixed-census limits are in [`../v5/repertoire_model.md`](../v5/repertoire_model.md). Definitions and equations in this file are V7 proposals/derived diagnostics, not external empirical facts and not V7 findings.
