# V7 implemented mathematical model

This document describes the executed V7 code, not the broader preregistered ideal.
The append-only deviation ledger in [`research_contract.md`](research_contract.md)
preserves the difference. Six systems must remain distinct:

| System | Role | Claim boundary |
|---|---|---|
| Frozen individual-based model (IBM) | archived ecology/demography evidence | byte-preserved but invalidated for policy inference by the no-teacher local oracle |
| Corrected IBM overlay | fresh discovery, holdout, H9, finite lineage | primary executed variant; changes only the three no-teacher local methods |
| `ExactTinyPOMDP` | reduced two-episode theta/z benchmark | exact only for its matched toy, never an upper bound on the IBM |
| Finite-lineage extension | paired 80-season newborn descendants | conditional finite endpoint, not direct competition or asymptotic invasion |
| Corrected cumulative cognitive assay | six-learner procedure-chain feasibility | separate from the IBM; not demographic cumulative culture or H2 evidence |
| Post-freeze assays | generic action persistence, adult yoked decisions, corrected d=0 shock/K erasure | diagnostic extensions, not new biological mechanisms |

The frozen and corrected source manifests/replay digests are recorded in
[`project_manifest.json`](project_manifest.json). Reporting code does not change the
frozen model or configuration.

## 1. IBM and corrected primary overlay

### State, observation, and acquired content

Individual `i` has age `a_i`, energy `E_i`, inherited trait
`d_i=(d_procedure,d_local)`, and acquired state `(B_i,K_i,T_i,H_i)`:

- `B`: branch/local factual weights;
- `K`: executable sequences with physical provenance roots;
- `T`: observed source/outcome histories and source estimates;
- `H`: reserved acquired habit state (not a genetic trait).

Policies receive typed observations, budgets, messages, provenance, declared prices,
and feasible actions. Hidden structural branch `theta`, current local state `z`,
future changes, evaluator truth, and the resource pool remain world-side. Birth copies
only `d`; newborn `B/K/T/H` are blank.

### Factual posterior and ordinary social learning

For a procedure family, let unnormalized stored branch weights be `B_0,B_1` and
private cue accuracy be `rho=.8`. The private cue multiplies the reported branch by
`rho` and the alternative by `1-rho`. If a teacher offers branch `m`, source
calibration is

`r = clip((2(s+1)/(s+f+2) + T_source)/3)`,

where `s,f` are observable successes/failures and `T_source` defaults to `.5`. Social
evidence multiplies offered branch `m` by `r` and the alternative by `1-r`, followed
by normalization. Neutral reliability `r=.5` is therefore neutral.

For local advice, private evidence updates the log odds of the advice-relative claim.
When social content is present, observable source reliability and context mismatch
enter the same advice posterior. `d=(0,0)` is therefore still social: it receives and
pays for content, updates acquired state from outcomes, can store `K`, and can teach.
The asocial policy is a separate intervention that removes messages, provenance,
advice, source ID, and source history while preserving private hardware and actions.

**Frozen-base defect.** In the archived base IBM, a no-teacher local observation
still exposes `private` and `teacher` actions with equal zero values. The lexical
tie-break selects `teacher`; the no-teacher local helper also sets the synthetic tutor
signal equal to hidden `z`. Thus the frozen asocial arm receives a behavioral hidden
state oracle on local turns. Frozen discovery, holdout, H9, and lineage exports are
retained for provenance but invalid for policy inference. The corrected variant is a
separately registered overlay and fresh rerun; it does not modify archived bytes or
rescore cached outcomes.

### Actual IBM `Q0`: one-decision posterior proxy

The IBM does **not** implement the preregistered two-episode Bellman continuation.
For procedure depth `D`, define the fully enumerated expected return for per-node
success probability `p`:

`G_D(p) = sum_(j=0)^(D-1) p^j(1-p)[-(j+1)c_step + j*salvage]`

`          + p^(D+1)[h_H(D)-D*c_step]`

`          + p^D(1-p)[-L_finish-D*c_step+D*salvage].`

With posterior probability `pi_b` that candidate branch `b` is structural,

`Q0_procedure(b) = pi_b G_D(.90) + (1-pi_b) G_D(.50).`

For local advice with posterior `p_A`, reward `3`, loss `2`, and advice action `A`,

`Q0_local(A)=3p_A-2(1-p_A)`,

`Q0_local(private)=3(1-p_A)-2p_A`.

The neutral action is the deterministic maximum of these current-action values. IBM
`Q0` contains no `delta=.97` term, future belief-state recursion, or future learning
value. The policy pays its declared operation charge after arbitration.

### Juvenile genetic override

Let `a0=argmax Q0`, `aT` be advice, and `C=1[a0 != aT]`. For domain
`k in {procedure,local}`:

`a=aT` if `C=1`, `age<tau`, and `U_override<d_k`; otherwise `a=a0`,

with fixed threshold `tau=5`. Direct genetic override is disabled at ages 5 and
above. Acquired juvenile `B/K/T/H` may nevertheless affect later action. V7 does not
optimize `tau`, and this threshold is not the V1--V6 exponential maturation mean.

### Task economics and physical execution

Primary depths are `D in {1,3,6}`. Constants are `p_plus=.90`, `p_minus=.50`,
safe yield `h_safe=1.2` per token, step cost `c_step=.20`, salvage `.20`, and incorrect
finish loss `L_finish=2`. The outcome-blind correct-finish reward is

`h_H(D)=ceil_0.1(((D+1)(h_safe+.30)+D*c_step)/p_plus^(D+1))`,

giving `(4.0,10.1,24.5)`. A procedure reserves `D+1` time tokens. Physical execution
uses independent keyed draws for `D` prerequisites and the finish; the terminal is a
prefix failure, correct finish, or incorrect finish. The same enumeration supplies
`G_D(.90)` and `G_D(.50)`.

Successful execution stores the selected sequence and increments its independent
success count. Every terminal updates the selected branch weight using the likelihood
of that exact terminal under `.90` versus `.50`. Message receipt alone never stores
`K`.

### Teaching and content selection

A procedural teacher is eligible for family `f` when it has a stored family sequence
with at least two independently logged successes and has not spent time that season.
Eligibility is age-neutral. Among eligible teachers, the code ranks an observable
`outcome:family` key and then identity, but no executed path updates that key, so its
default `.5` ties and selection is effectively by identity among currently
time-available eligible teachers. After a teacher is chosen, the offered content is
the **lexicographically first eligible `K` sequence for that family**. Neither teacher
nor content is selected from the learner's current `B`, an empirically updated
performance score, or hidden truth. These order rules are live alternative
explanations for content dynamics.

A procedural teaching event spends one token for teacher and learner, charges the
teacher `.05` energy, and records a cultural edge. A local recommendation uses the
first time-available other individual by identity, spends one token on each side,
and charges the teacher `.02`; it does not require stored procedural `K`.

In the corrected overlay only, `teacher=None` removes the teacher action, assigns the
private action its `.8*3-.2*2=2.0` expected value, forces physical execution through
the private cue, and makes the unused tutor placeholder equal to that private cue.
Teacher-present behavior, all prices, and every other algorithm remain unchanged.

### FeatureTrust and Candidate B

FeatureTrust uses the action-blind vector

`x=(1, calibrated_source, context_match, min(4, unique_roots))`.

For realized focal payoff `y`, one normalized-LMS update is

`y_hat=w dot x`,

`w' = w + eta (y-y_hat)x/(1+||x||^2)`, with `eta=.08`.

Prediction uses 4 declared primitive operations; the single post-outcome update uses
16 and is skipped if the common 128-operation cap cannot accommodate it. Each
operation costs `.01` energy. The scalar prediction `w dot x` is added only to the
current advised action's value. Because `x` omits the action and the update is a
reward heuristic, FeatureTrust is not a general reinforcement learner or a calibrated
action-conditional value model.

Candidate B inherits that predictor and evaluates a binary query/verification signal:

`EVI = E_signal[max_a Q0(a | signal)] - max_a Q0(a)`

`      - posted_information_price - posted_time_opportunity.`

It buys the best positive option, updates `B` with the realized signal, and makes one
ordinary re-decision without a genetic override. The decision-time query evaluator
uses current source calibration as the hypothetical signal accuracy, but the executed
world-side query draw uses fixed accuracy `.80`; verification uses `.90` in both
places. That evaluator/execution mismatch is an additional approximation, not a
calibrated query channel. The purchased signal consumes one actual time token, while
the procedure `time_opportunity` price is `(D+1)h_safe`; this is a declared
conservative proxy, not a literal one-token opportunity match. Candidate B has no
future-learning continuation and is an approximate current-decision metareasoner,
not verified Bayes-optimal or fully resource-rational control.

The corrected ecology exports do not include per-run query/verification purchase
counts. Realized purchase frequency therefore cannot be audited from aggregate CSVs;
the source establishes the route and charges, not how often each option was used.

### Demography, resources, and exported estimands

The ecology starts with resource `R=1600` and 64 blank founders of energy 8.
Regeneration is `.08(1600-R)`, conversion efficiency is `.75`, base maintenance is
`.6`, birth cost is 16, newborn energy is 8, reserve is 3, and maximum birth
probability is `.5`. Only ages `>=5` reproduce. A parent pays 16, the newborn receives
8, and the remaining 8 is a birth loss; acquired state is not copied.

For each season,

`N_(t+1)=N_t+births_t-deaths_t`.

The event replay checks the actual resource-plus-agent-energy stock movement; a
nonzero residual beyond tolerance invalidates the run. The main exported summaries
use the **entire simulated horizon, including burn-in**:

`mean_population = (1/S) sum_(t=1)^S N_t`,

`net_energy_per_agent_season = [R_S + sum_i E_i(S) - initial_total_stock]`

`                              / [sum_(t=1)^S N_t]`.

For ordinary ecology `S=60+180=240` unless a terminal condition stops the run. This
is a retained resource-plus-living-energy **endpoint stock residual** per agent-season.
In a regenerated, regulated stock system it can remain near zero while population,
birth/death balance, task performance, or carrier descendants differ. It is not a
fitness or performance proxy. These estimands are also different from the season-80
conditional lineage endpoint.

## 2. Separate exact tiny benchmark

`ExactTinyPOMDP` enumerates posterior states over `(theta,z)` for two episodes. Its
action set is safe, execute 0/1, learn, query, and verify; it has three time units, six
operations, context flip `.35`, and discount `.97` between episodes. Its Bellman
recursion is

`V(s)=max_a [r(s,a)+delta E[V(s')]]`

for terminal actions, with within-episode posterior recursion and explicit information
costs for learn/query/verify. It never observes realized hidden state while planning.

The enumerated value is `3.111372` with first action `learn`. A separately simulated
restricted override policy gives `2.260000` with MCSE `0.048466` over 4,000 replicates.
The upper-bound statement applies only to this matched toy policy and objective. It is
not a full-IBM bound, and its Monte Carlo uncertainty belongs only to the restricted
simulation.

## 3. Finite-lineage extension

The selection extension clones one acquired resident prefix, waits for the next
naturally sampled parent-paid birth, and assigns either mutant or resident traits to
the same born ID in paired counterfactual arms. Birth cost, newborn energy, blank
acquired state, resident teachers, and starting resource/culture are shared. The arm
runs 80 additional seasons and records living descendants, zero/extinction mass,
caps, no-birth censoring, and a descriptive frequency trajectory.

The primary computed contrast is paired living descendants:

`Delta_desc = mean_seed[N_mutant(80)-N_neutral_tag(80)]`.

The corrected fresh run stopped at the preregistered 88 seeds per contrast: 2,112 arm
rows, 1,056 complete mutant/neutral pairs, zero incomplete-batch rows, zero no-birth
censoring, and zero cap censoring. Finite lineage extinction occurs in 1,846 arm rows
and remains in the unconditional denominator. Across the 12 contrasts, mean paired
differences range from `-.238636` to `+.568182`; the maximum paired-descendant MCSE is
`.225581` and the maximum arm-level establishment Wilson half-width is `.097174`, so
the registered `.25/.10` precision gate passed. This is numerical precision for a
finite conditional endpoint, not significance or equivalence. No 120-season direct
competition assay ran, and these values are not invasion exponents, fixation, ESS, or
stable polymorphism.

## 4. Corrected cumulative cognitive assay

This is a separate deterministic/stochastic cognitive program, not the frozen IBM.
Six blank learners each have nominal lifetime budget 60; private verification costs
29 work units, teaching costs one unit to each side, and material debit is `.01` per
work unit. Six arms compare transmission/innovation and ablations. The corrected
fresh export fixes aggregate work at 360 and material debit at 3.6 per arm.

The `matched_total_work_independent_upper_bound` directly grants three verified
modules to a terminal learner, accumulating private work 87 before `_fill` assigns
negative safe work to restore the aggregate total. It is therefore an ideal pooled
upper bound, not a feasible per-person budget comparator. `all_newborns_blank` checks
fresh constructors rather than realized demographic cohorts. The assay supports only
partial cognitive two-edge feasibility; it does not establish demographic cumulative
culture, selection, or H2.

## 5. Post-freeze diagnostics

### Generic persistence process

The persistence module is separate from the IBM. Forty training iterations update
scalar `B,K,T,H`. For each probe, two same-direction independent evidence events
produce

`odds_post = odds_pre [q/(1-q)]^2`, with `q=.84`,

while devaluation multiplies `H` by `.72` and contingency degradation by `.68`.
Reported action probability is `clip(.25K+.75H)`, plus `.08` only if an audience,
tutor, sanction, or promised reward is present. `intervention_seasons=20` is exported
metadata; the implementation does not execute 20 sequential probe updates. The
“bidirectional” label does not implement both evidence directions. This is generic
learned-action persistence with factual revision, not private-belief dogmatism or an
obligation mechanism.

The adult yoked assay uses age 7 and identical synthetic histories across juvenile-d
labels; it verifies direct adult override is off. It is not an ecology or selection
effect.

### H9 observation

At burn-in plus 90 seasons, cloned corrected-overlay d=0 IBM states receive: no shock, a flip of both
`theta` family bits, or the same shock plus erasure of all `K` and independent-success
counts. There is no external storage. The assay does not kill carriers, export root
diversity, cross the shock with d, or compute functional recovery time. It is a partial
shock/K-memory diagnostic, not a causal test of monoculture debt.

## 6. Uncertainty and reporting rules

Ecology and lineage contrasts are paired within seed, then summarized across
independent seeds with sample-SD divided by `sqrt(n)`. Population N, full-horizon net
material stock change, and finite living descendants are never substituted for one
another. Extinction, zero, cap, no-birth, registered raw, and complete-batch
denominators remain explicit.

The frozen export contains seed-level `revision_rate`, `override_rate`, and
`cultural_action_accuracy`, but not every required event numerator/denominator.
Across-seed MCSE is valid as a replicate diagnostic. Registered Wilson/binomial rate
precision remains unresolved; exported proportions must not be treated as independent
Bernoulli trials.

## Final registered controls (separate models)

The corrected IBM above remains the primary V7 model. Final controls are additional tests, with separate parameters and independent seed blocks; they are not hidden changes to its grid.

### Execution-priced comparator

The bounded planner evaluates a binary query or audit under the common $Q_0$:

$$V_I=\sum_s P(s\mid h)\max_a Q_0(a\mid h,s)-c_I-c_{op}(n_I+1).$$

Its twelve declared abstract deliberation units are paid even when no information is purchased, so they are a common sunk cost in the option ranking. Query accuracy is .8, audit accuracy .9 in both expectation and execution. A purchase consumes one actual token and is disabled if it prevents the same physical action. These are finite one-decision values; neither full-horizon optimality nor general RL is claimed. Durable world-level request counts retain individuals that later die. See `experiments/execution_planner.py` and its frozen registration.

### Closed-resource procedure control

This additional model has ten blank founders, six ordered procedure modules, private accuracy .8, discovery effort eight tokens/module, four tokens/person/season, maturity3, lifespan18 and horizon60. Adults and juveniles have identical private hardware. Births debit6 energy, create a blank newborn with4, and book the residual2 as a sink. Every teacher and pupil pays actual tokens and energy; a central reservation table prevents retrospective teacher overuse.

$$R\leftarrow R+.06(800-R),\qquad d=\min(R,\text{harvest request}),\qquad R\leftarrow R-d,\qquad E_i\leftarrow E_i+.75d.$$

A physical harvest costs one token. A functional complete recipe can request4 resource units; an incomplete recipe uses safe harvest requesting2. Invalid compiled procedures receive no high yield and physical failure supplies stage feedback. There is no automatic skill income. Conversion loss, maintenance, learning, teaching, storage and death are explicit sinks:

$$R_t+\sum_iE_{i,t}=R_0+\sum_iE_{i,0}+\text{regeneration}_{0:t}-\text{sinks}_{0:t},$$

$$N_{t+1}=N_t+B_t-D_t-C_t,$$

where $C_t$ is an externally specified carrier-removal count. Every individual's work is at most4. An operational cap stops and censors; it never suppresses ongoing births. In the paired effort intervention, independently evolving populations receive the same ex-ante feasible total effort $W_t=4\min(N_{1,t},N_{2,t})$; they exchange no people, knowledge or resource. All offered and realized effort is exported. Mean population divides by the fixed60-season horizon, including zero after extinction.

Minimum independent discovery effort is48, compared with lifetime ceiling72 and harvest-reserved ceiling54. This model therefore does not establish a cognitive impossibility of solo acquisition. Its transmission advantage is ordinary knowledge reuse, not proof of a distinct authority trait. The prerequisite-scramble control changes the physical execution order halfway through the run; it does not merely rename modules. Source origins and actual recipe acquisitions are retained.

A second carrier-loss assay removes **all** people at checkpoint30, then externally supplies ten truly blank replacements and80 energy units. The input is explicitly booked and equal across artifact-on/off arms. Innovation is disabled thereafter. Every recovery must trace to paid stored artifacts. This experimental reset is not a natural demographic or invasion-fitness result.

### Fixed-proposition belief and action-value control

Each history begins with empty acquired state. Its objective proposition is fixed during40 training episodes; one source conviction is sampled with .7 reliability and counted as one root. Private evidence has .8 accuracy conditional on truth. Actual paid outcomes and approval update action values; psychological approval never enters material credits. After training, adult states are cloned across audience, audit-cost and evidence-quality interventions for20 episodes. Adult inherited override is zero; private accuracy and learning rate stay unchanged.

For presumed environmental-switch hazard $h\in\{0,.01\}$, the prior prediction and evidence update are

$$p^-_t=h+(1-2h)p_{t-1},\qquad L_t=\operatorname{logit}(p^-_t)+\sum_j(2s_j-1)\log\frac{q_j}{1-q_j}.$$

Log odds $L$ are retained directly, avoiding artificial irreversible certainty from rounded probabilities. Audit quality is .8 except the explicitly labeled reliable-evidence arm (.95). Supporting and reversal conditions use the same random-error tapes with opposite truth. The action value updates only the chosen action:

$$H_a\leftarrow .85H_a+.15(r_{material}-c_{checking}+r_{approval}).$$

All inherited deference acts in the juvenile arbitration window; it never directly modifies adult updating. Knowledge changes only after paid successful juvenile practice and stays fixed in the adult evidence assay. Every physical receipt, checking debit, prior/posterior and action value is saved.

With information equalized, factual trajectories are exactly invariant to the juvenile override coefficient in this control. Old beliefs can persist under a static-world prior after an unexpected reversal without a special dogmatism trait. This is ordinary prior/model dependence, not evidence of deficient revision or an evolved childhood adaptation.
