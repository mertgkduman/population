# V7 model candidates

**Status:** design recommendation; no V7 result is reported here. All numerical ranges below are hypothetical starting values to be calibrated against neutral viability and conservation tests, not empirical estimates.

## Recommendation in one paragraph

Use Candidate A: a discrete-event, overlapping-generation individual-based model with two task families and prerequisite depths `D in {1,3,6}`. Individuals learn fallible general procedures, obtain a private cue about the present local context, estimate source reliability from observable histories, and choose a material-value-maximizing action. The inherited coordinates `(d_procedure, d_local)` act only if that neutral action conflicts with a tutor recommendation. Thus `(0,0)` is an ordinary reliability-sensitive social learner, not an asocial or memory-impaired control. Every learning, teaching, production, verification, computation, and birth event consumes a common finite budget. Adults and other potential teachers become competent only through logged experience; age never creates expertise. Add approval-trained habits only after the epistemic kernel passes its tests. Retain Candidate B, a provenance-aware resource-rational metareasoning policy with no deference trait, as the substantive independently derived alternative.

## Candidate A — finite-resource task-and-culture IBM

### 1. World and task graph

A run has two task families `f in {1,2}`. A treatment fixes a common prerequisite depth `D in {1,3,6}`; using two families at every depth avoids confounding depth with a unique family. Family `f` has a slowly changing structural vector

$$
\theta_f(t)=(\theta_{f1},\ldots,\theta_{fD}),\qquad \theta_{f\ell}\in\{0,1\}.
$$

Each task episode has a fresh individual-local finishing condition `z in {0,1}`. The simulator owns `theta` and `z`; ordinary agents never receive them. At prerequisite node `ell`, the agent selects `a_ell in {0,1}` or exits through a safe action that yields a small known return `h_safe` and no structural evidence. With `X_0=1`, advancement for a non-safe action is

$$
P(X_\ell=1\mid X_{\ell-1}=1,a_\ell,\theta_{f\ell})
=p_-+(p_+-p_-)\mathbf 1[a_\ell=\theta_{f\ell}],
$$

and `X_ell=0` otherwise. A failed node ends the episode with a small depth-dependent salvage yield; successful completion reaches a finishing choice `a_z in {0,1}` and withdraws `h_H` resource units when `a_z=z`, or `h_L>0` when `a_z!=z`. Use `0<p_-<p_+<1`, `h_L>0`, and positive salvage. Before any policy sweep, enumerate tiny landscapes and calibrate the primary graph ensemble so at least two distinct full procedures have positive expected net return under matched work, prefixes have nonzero marginal value, the safe action is viable but lower-yield, and private discovery has nonzero success. Both binary branches can therefore work, feedback arrives at intermediate failures, and depth six is difficult without being a deliberately unsearchable needle. Prune no-op steps and repeat on relabeled and prerequisite-shuffled graphs.

Structural change flips one randomly selected structural bit with seasonal probability `q_theta`; an agent does not observe that a flip occurred. Local `z` is redrawn each episode. These are deliberately different timescales.

Every agent's local sensor has the same accuracy `rho`:

$$
P(y_i=z_i)=\rho.
$$

A potential tutor observes its own local state with the same sensor hardware. Context mismatch is ecological, not physiological: `P(z_T=z_i)=chi` with `chi in {0.5,0.75,1}`. Consequently tutor advice can be stale or inapplicable without lowering a tutor genotype's sensory ability. Include reversed-access assays in which the tutor's observation is more current than the learner's.

### 2. Individual state and strict separations

Individual `i` carries:

- age `a_i`, reproductive eligibility, energy `E_i`, remaining seasonal time, and remaining computation operations;
- inherited `g_i=(d_procedure,d_local)` in the core model;
- factual beliefs `B_i`: posteriors over structural bits and the current local state;
- procedural memory `K_i`: cached action sequences, practice counts, and observed outcomes; a cached procedure can be wrong;
- source model `T_i`: domain-specific reliability estimates and testimony provenance;
- later, norm/habit values `H_i`, stored outside `B_i` and `K_i`;
- one biological parent identifier and zero or more cultural-teacher edges.

These objects must not alias one another. Executing advice does not by itself change a factual posterior or cache a procedure. A message or demonstration may update `B`; storing/practising a procedure updates `K`; a physical outcome may update both through explicitly different rules. Public action is logged separately from private belief and procedural memory. A typed policy-observation object excludes simulator truth and is serialized at every call; evaluator/oracle objects are inaccessible to ordinary policies.

For a source `j` and domain `k`, initialize an uninformative finite-sample estimate

$$
\widehat r_{ijk}=\frac{\alpha_{ijk}}{\alpha_{ijk}+\beta_{ijk}}.
$$

Start with `alpha=beta=1`. For a physical prerequisite outcome `x in {0,1}`, a hypothesized structural bit uses likelihood `p_+` when the chosen action matches the hypothesis and `p_-` otherwise. A local cue uses likelihood `rho` for its indicated state. For a source message `m in {0,1}` about binary state `s`, use

$$
P(m\mid s,T_i)=\widehat r_{ijk}\mathbf 1[m=s]+(1-\widehat r_{ijk})\mathbf 1[m\ne s].
$$

When independent physical evidence later scores the claim only probabilistically, use soft observable-history counts `alpha += P(claim correct | independent evidence)` and `beta += 1-P(claim correct | independent evidence)`; do not score against hidden truth. Advice copied from a common testimony root carries that root's provenance; repeated descendants of one root contribute at most one independent likelihood term unless independent physical evidence is observed. Neither true reliability nor evaluator-scored competence is exposed to a policy. An explicit learn/memorize event may cache the transmitted sequence in `K`; merely executing one advised step cannot. Successful independent executions increment the mastery counter.

Procedural teaching eligibility is age-neutral. An individual may offer family `f` once it has a stored sequence and at least two logged, independently attempted successful completions. This is an observable mastery rule, not an oracle of correctness. A juvenile or nonreproductive learner meeting it can teach; an adult without it cannot masquerade as an expert merely because of age.

### 3. Common evidence and decision kernel

Messages can contain (i) a general procedure, (ii) a demonstration and observed outcome, or (iii) a present local recommendation. Before any deference response, every social policy uses the same authority-neutral update from private observations, message content, demonstrations, provenance, and estimated reliability. For example, a binary source message is entered with the learned mixture likelihood implied by `r_hat`, not as guaranteed truth.

For each feasible action, compute

$$
Q_i^0(a\mid h_i)=E_{\widehat P_i}\left[
\sum_{s=0}^{H_Q}\delta^s\{\Delta E_{i,t+s}-c_{i,t+s}\}
+\delta^{H_Q} \widehat V_i(K_{t+H_Q})\mid h_i,a
\right],
$$

where `h_i` contains observed history only, `P_hat_i` is the individual's learned model, and the horizon includes the remainder of the task plus the same declared future-use approximation for every policy. The action favored by the common kernel is

$$
a_i^0=\arg\max_a Q_i^0(a\mid h_i),
$$

with keyed neutral tie-breaking. Social evidence can make `a_i^0` equal the tutor recommendation. That is ordinary social learning, not extra deference.

The same `Q^0` machinery ranks feasible nonreproductive event types (trial, query, verify, produce, teach, rest) under a common two-episode lookahead `H_Q` and `delta in [0.95,1]`; no `d` coordinate changes event availability or its pre-override value. The common demographic rule below reserves reproduction time before this allocation. Candidate B changes only how the finite computation budget is allocated to estimating event/action values.

Let `a_T` be the selected tutor's recommendation, selected using availability and observable `T_i`, never true competence. If there is no recommendation or `a_T=a_i^0`, execute `a_i^0`. Only on conflict draw

$$
a_i=\begin{cases}
a_T,&U_{i,e}<d_{ik},\\
a_i^0,&\text{otherwise},
\end{cases}
\quad
k=\begin{cases}
\text{procedure},&\text{prerequisite decision},\\
\text{local},&\text{finishing decision}.
\end{cases}
$$

The random variate is keyed to individual and event. At `d_procedure=d_local=0`, the agent still queries, observes, updates source reliability, learns and stores procedures, and can rationally follow a tutor whenever social evidence makes that action valuable. The two coordinates add only conflict override. They never change sensors, memory, computation, innovation, or physiological execution.

The neutral evaluator must not be made artificially pessimistic about delayed procedural value. The exact tiny-world planner below checks its values; explanation, free-verification, horizon, and downstream-value sensitivity tests reject a purported deference advantage that exists only because `Q^0` omits an obvious common benefit.

### 4. Costed event types and same hardware

Every individual receives `B_time` indivisible time tokens per season and `B_comp` primitive belief/value operations per decision. Permitted events are private trial, observe demonstration, query, verify, produce one task step, teach, transfer/provision, reproduce, and rest. A paired teaching event consumes one token from both teacher and learner plus the declared energy costs. Each production step consumes a token, so deeper procedures have real opportunity cost. Verification consumes material and time even if it disconfirms a claim. Actual computation uses operations and energy `c_op` per operation; all policies have the same cap and price. An algorithm that needs fewer operations may keep that efficiency benefit, but no policy receives a larger cap.

Within a matched comparison, all genotypes have identical `rho`, memory record capacity, `B_time`, `B_comp`, motor success probabilities conditional on an action, and innovation success conditional on the same experiment. Different realized histories are policy-mediated outcomes and must be reported as such.

### 5. Finite environmental and individual energy ledgers

Let `R_t` be a finite environmental resource pool with capacity `K_R`. At the beginning of a season it receives exogenous regeneration

$$
G_t=g_R(K_R-R_t),\qquad R_t^+=\min(K_R,R_t+G_t).
$$

Task extraction removes gross `H_e` from `R` and adds `eta H_e` to the producer, with conversion loss `(1-eta)H_e`. An individual's energy update over a season is

$$
E_i(t+1)=E_i(t)+\eta\sum_e H_{ie}-m(a_i)-C_i^{\rm learn}
-C_i^{\rm teach}-C_i^{\rm compute}-C_i^{\rm birth}
+T_i^{\rm in}-T_i^{\rm out}.
$$

Every term is logged once. Transfers sum to zero across individuals. Regeneration is the only unpriced external inflow; metabolic, conversion, failure, and birth losses are explicit sinks. Extraction cannot exceed the resource pool available at the event. Randomized, keyed event order and a proportional-allocation sensitivity check control first-mover artifacts.

Reproduction is an event, not replacement. Under the initial genotype-invariant demographic rule, an individual with `a_i>=tau` and pre-action `E_i>=C_birth+E_reserve` reserves one seasonal time token and attempts at most one birth with probability

$$
P(B_i=1)=b_{max}\operatorname{logit}^{-1}\left(\frac{E_i-C_{birth}-E_{reserve}}{s_E}\right),
$$

using `b_max=0.25-0.75`, `E_reserve=2-5`, and `s_E=1-3` as hypothetical calibration ranges. The draw and reservation occur after maintenance; the event executes after production only if the parent survives and still has `C_birth+E_reserve`, otherwise the reserved opportunity is lost. An executed event spends `C_birth`; the newborn begins next season at age zero with energy `E_0<C_birth`, empty `B`, empty `K`, no source estimates beyond the common prior, and a possibly mutated copy of `g`. No fact, procedure, source reliability, or habit is inherited genetically. Starvation occurs at `E_i<=0`. Conditional on survival of task hazards, background death uses

$$
P(D_i=1\mid a_i)=1-\exp\{-\mu_0-\mu_1\max(a_i-a_0,0)\},
$$

with `mu_0=0.002-0.01`, `a_0=20`, and `mu_1=0.005-0.02` as starting values. Population size is therefore variable and extinction is an outcome. A computational emergency cap, if ever reached, stops and labels the run censored; it must never kill or replace individuals silently.

### 6. Event order

The following order is part of the model and receives an alternative-order sensitivity test:

1. Transition slow structure and regenerate the finite resource pool using pre-season state.
2. Snapshot living agents, age, energy, time, culture carriers, and teacher availability; pay maintenance. Starved individuals die and their unreplicated culture disappears. Apply the common reproduction-attempt draw and reserve one time token for successful draws.
3. Generate task opportunities, local contexts, and private cues. Agents see only declared observations.
4. Process keyed random event opportunities. A choice is made from the pre-event observed state. A query/teaching pair reserves both participants' time before content is sent. A teacher must be eligible at event start.
5. Realize physical outcomes and energy/resource debits. At event end, deliver observations and update `B`, `K`, `T`, and later `H` through separate rules. Newly achieved mastery permits teaching only from the next event.
6. Process reproduction events from eligible survivors; debit parent energy immediately and queue newborns with mutated traits and empty acquired state.
7. Apply task and background mortality, finalize births and deaths, age survivors, close the energy/resource ledger, and record biological and cultural edges. Newborns act next season.

This ordering prevents same-event knowledge teleportation, free teaching, inherited facts, and post-mortem libraries.

### 7. Founder culture and genealogies

Initialize `N_0` founders at a declared age distribution with empty procedures, uninformative beliefs, and no competent adults. Run a monomorphic founder burn-in under the same costed learning and task events, with trait mutation disabled during culture establishment unless mutation is the declared treatment. Any competent adult at the measurement snapshot must have a complete logged acquisition history. Failure to generate a competent teacher is a legitimate state; never inject a correct recipe or guaranteed expert.

Use five initial-culture controls produced by acquisition rather than truth seeding, with equal logged opportunity budgets where the comparison requires it:

- **blank:** no premeasurement competence and no privileged demonstration;
- **sparse-private:** limited private acquisition with no guaranteed successful founder;
- **learned:** the ordinary burn-in snapshot;
- **alternative/wrong:** an independent acquired genealogy that may encode a different or poor procedure;
- **failed:** every unsuccessful/extinct burn-in retained in unconditional establishment summaries.

Every birth creates a biological edge `(parent, child, time)`. Every social acquisition creates a separate cultural edge `(teacher, learner, family, procedure hash, root provenance, time, mode)`. The main model has no artifact store. If the last living carrier of a procedure dies, it is inaccessible. A separately labeled institutional variant may add a finite-capacity, maintained artifact with write/read costs and decay; it is not active by default. Pre-exposure newborn-state inspection, parent-knowledge permutation, cross-fostering, and held-out task-node/solution relabeling must show that content follows post-birth cultural exposure rather than biological parent or a task-specific lookup hidden inside the genotype.

### 8. Staged approval, habit, and optional obligation module

Do not enable this module until the core epistemic model passes leakage, cost, benchmark, and neutral tests. Introduce a convention/norm action component distinct from structural truth. An evaluator can emit observed approval `r_eval in {-1,0,1}` at its own time/energy cost. Approval is not energy, food, fecundity, or objective correctness.

For action `a`, let

$$
Q_i^{\rm act}(a)=Q_i^0(a)+\gamma_i\widehat A_i(a)\mathbf 1[\text{audience}]+H_i(a),
$$

and update habit after observed evaluation by

$$
H_i(a,t+1)=(1-\lambda_H)H_i(a,t)+\alpha_H r_{\rm eval}\mathbf 1[a_i=a].
$$

Use the same `alpha_H`, `lambda_H`, evidence access, and belief update capacity at every age in the first module. There is no maturation freeze or imposed adult rigidity. Keep approval expectation, acquired habit, factual posterior, and conflict override switchable separately.

Required interventions are: (i) audience removal, setting current expected approval to zero while retaining acquired `H`; (ii) free audit, setting verification time/material cost to zero without changing evidence; and (iii) information equalization, delivering the same independent, likelihood-calibrated evidence sequence in both directions. This first stage supports only **learned action persistence**. Add outcome-devaluation and contingency-degradation probes; if behavior tracks cached reward history, call it habit. A later optional obligation state may be introduced only with explicit injunction acquisition plus countermand and cross-context obligation-generalization probes. Reserve **normative commitment** for persistence that survives the habit rivals while factual belief updates adequately. Failure of a factual posterior to respond to accessible counterevidence relative to the matched benchmark is the separate dogmatism construct.

## Candidate B — provenance-aware resource-rational metareasoning without deference

This independently derived alternative asks whether apparent selective following is simply a rational response to costly computation and verification. It has no `d_procedure` or `d_local`. It shares the same observations, beliefs, source model, physical abilities, memory, time, and computation cap as Candidate A. Its evidential state is a set/DAG of unique physical-trial and innovation roots, so copying a known root cannot masquerade as an independent observation; a separately labeled provenance-blind ablation may overcount it.

At a conflict, the controller considers computations `m` such as one procedure audit, one source-history lookup, one demonstration query, a local re-observation, or stopping. From its learned model, not true state, it estimates

$$
\widehat{VOC}_i(m)=E_{o\sim\widehat P_i(\cdot\mid m)}
\left[\max_a Q_i^0(a\mid h_i,o)\right]
-\max_a Q_i^0(a\mid h_i)-c_m.
$$

An equally capped finite-rollout estimator chooses the positive-`VOC` computation with greatest estimated net value; when none is positive it executes the current neutral best action. Following advice can emerge because verification is not worth its cost, but an uninformative authority label has no direct term. The controller predicts immediate sensitivity to free audit and computation-price changes, whereas an inherited override can persist until selected or learned away. This makes Candidate B a substantive rival, not an ablation of Candidate A.

## Comparator set and policy-class limitation

Use the following policies on matched exogenous streams:

1. asocial learner (cultural access off; value of culture only);
2. ordinary reliability-sensitive social learner, Candidate A with `(0,0)`;
3. scalar bridge `d_procedure=d_local`;
4. vector Candidate A;
5. feature-based learned trust, a contextual reliability/reward learner using observable source and task features;
6. resource-matched approximate planner, including Candidate B's finite-rollout controller;
7. exact tiny-world planner;
8. approval/habit learner only in the later module.

For the exact benchmark, restrict to one family, `D=1` (and a factored `D=3` check if it fits), a two-episode horizon, finite energy bins, one potential tutor, and enumerated hidden states and observations. Dynamic programming integrates hidden states but never reveals their realized values. Give it the same observations and utility and choose the smallest common `B_comp` (starting at 128 operations) in which its complete recursion fits; the approximate and feature controls receive that identical cap and operation price. Compare simulated values to exact action values and visitation frequencies.

The exact policy class includes every action available to the deference heuristic, including following advice. Therefore, with the correct generative model, identical observations and utility, its expected value weakly exceeds every restricted override policy: it can always choose the restricted policy and may choose better. An observed systematic excess over it is an implementation, objective, or Monte Carlo failure, not evidence for deference. Candidate A can only earn an explanatory advantage against finite-computation or finite-learning controls, or through separately modeled social consequences and commitment. Conditional analyses of naturally occurring conflicts, available teachers, survivors, or auditors are policy-selected; pair every such mechanism summary with an unconditional intention-to-treat contrast or an induced-conflict assay frozen before override.

The ecological study cannot include every history-dependent policy: the state/action tree grows exponentially with depth, source histories, population size, and horizon, and an unrestricted black-box policy would defeat construct identification. Limit the main comparison to interpretable Markov summaries `(B,K,T,E,a,observable context,costs)` with identical feature access and budgets. Conclusions are correspondingly limited to this declared set; do not claim a globally optimal evolved faculty. The exact tiny case, multiple strong approximate controls, and matched feature-trust learner bound the most important omitted-policy risk.

## Starting parameter envelope

These values are deliberately broad and must first pass monomorphic viability, no-free-energy, and nontrivial-task calibration. Do not tune them for an interior `d`.

| Quantity | Starting values/range | Purpose |
|---|---:|---|
| Task families | 2 | Reuse without a large ontology |
| Prerequisite depth | 1, 3, 6 | Main structure treatment |
| Step success `p_+, p_-` | `p_+=0.85-0.95`; `p_-=0.35-0.60` | Graded, non-needle alternatives |
| Gross finish yield `h_H, h_L` | `6-10`, `1-3`; positive prefix salvage `0.1-0.4` per reached node | Delayed benefit plus partial utility |
| Structure flip `q_theta` | 0, 0.005, 0.02 per family-season | Stable/slow/faster worlds |
| Shared sensor accuracy `rho` | 0.75-0.85 | Same hardware for all ages/traits |
| Tutor/learner context concordance `chi` | 0.50, 0.75, 1.00 | Mismatch without unequal sensors |
| Time budget `B_time` | 12-20 tokens/season | Binds learning, work, teaching, birth |
| Computation cap `B_comp` | 128 primitive operations/decision | Same cap for exact-tiny/approximate/trust |
| Verification/production cost ratio | 0.1, 0.5, 1.5 | Low/medium/high audit cost |
| Teacher and learner time | 1 token each/message or demonstration | No free teaching |
| Private trial material cost | 0.2-0.8 energy plus step inputs | Costly independent discovery |
| Environmental capacity `K_R`; regeneration `g_R` | 1000-2500; 0.04-0.12/season | Finite support with replenishment |
| Conversion efficiency `eta` | 0.6-0.9 | Explicit physical loss |
| Maintenance | 0.4-0.8 energy/season plus mild age term | Makes production necessary |
| Maturity `tau` | 4-6 seasons, fixed initially | Eligibility, not expertise |
| Birth cost/newborn energy | `C_birth=12-20`; `E_0=6-10<C_birth` | Costly variable births |
| Birth opportunity | `b_max=0.25-0.75`; `E_reserve=2-5`; logistic scale `s_E=1-3`; 1 reserved time token | Common genotype-invariant fertility rule |
| Background mortality | 0.002-0.01/season plus senescent slope after age 20 | Variable lifetimes and extinction |
| Mutation | 0.005-0.02/coordinate/birth; reflected normal step SD 0.025-0.10 | Newborn trait variants |
| Founder count/burn-in | 48-96 naive founders; 40-80 seasons | Endogenous culture only |
| Recorded horizon | 250-500 seasons | Demography and cultural turnover |

Calibration gate: `(0,0)` and asocial monomorphic populations must each have at least one viable and one extinction-prone resource regime; task success cannot be almost zero at depth six; tutor correctness must span below/equal/above learner quality across treatments. These are design-coverage requirements, not preferred substantive outcomes.

Keep maturity `tau` fixed in the main study. If maturity later evolves, an early-eligible agent forced to use the later type's reproduction schedule must reproduce its state/resource path exactly; otherwise the code has introduced an undeclared maturity tradeoff. Any delayed-maturity advantage requires a separately declared developmental allocation or reproduction-opportunity cost.

## Evolutionary protocol

After candidate policies are frozen, run the full resident burn-in. The default mutant originates at an otherwise ordinary resident reproduction event: the resident parent pays the full `C_birth`, the newborn receives the same `E_0` and empty acquired state as any other birth, and only its policy trait is assigned the candidate mutation. Pair it with a genetically neutral tagged newborn created under the same birth-state protocol. This avoids free immigrant energy and makes the comparison newborn-to-newborn within the actual mixed-age resident resource/cultural environment. An externally inserted newborn is a secondary introduction estimand and must debit an explicit source account; it is never free. Mutants select cultural sources by the same observable rules and normally learn from residents; never construct a mutant-only teacher pool. Preserve real parent-offspring correlations when vertical transmission is enabled.

For each directed resident-mutant pair, report unconditional expected descendant number (including zero lineages), mutant-lineage establishment/extinction probability, time-to-extinction/fixation distributions, and direct frequency change. A default finite-window descendant-expansion summary is

$$
g_m^{(T)}=T^{-1}\log\left(\frac{E[N_m(T)]}{N_m(0)}\right),
$$

where extinct replicates contribute `N_m(T)=0` before taking the replicate mean. Also show the raw distribution; do not replace it with survivor-only log growth. Because a newborn is compared within a mixed-age resident population and the lineage is finite, `g_m^(T)` is not an age-neutral asymptotic invasion exponent, Lyapunov growth rate, or proof of fixation/ESS. Use the matched neutral-newborn distribution and direct competition for the selection contrast.

Required checks are matched neutral-newborn/self-mutant neutrality, swapped-label exchange symmetry, neutral fixation/extinction against drift expectations, reciprocal newborn-lineage assays, nearby and endpoint competitors, multiple acquired resident cultures, and direct multi-strategy competition when reciprocal establishment occurs. Burn-in extinction is itself reported; conditioning an estimate on resident establishment must be explicit.

## Tractable staged experiment size

- **Kernel/exact gate:** deterministic enumeration in the `D=1` tiny world plus paired stochastic replications sufficient to make the exact-value discrepancy smaller than simulation Monte Carlo error. No evolutionary interpretation.
- **Discovery:** 27 mechanistic environments (`3 depths x 3 verification-cost levels x 3 context-gap levels`), 14 unique policies (coarse vector grid `{0,.5,1}^2`, scalar-only `.25` and `.75`, asocial, learned trust, and resource-rational approximate planner), and 4 paired discovery seeds: 1,512 runs. Treat all selections as exploratory.
- **Holdout:** freeze at most four discovered candidate policies plus the ordinary social, feature-trust, and approximate-planner controls; evaluate all on at least 24 fresh seeds, adjacent parameter values, and unseen task-graph permutations. Add seeds in preregistered batches of eight up to 96 until the 95% Monte Carlo interval is at most 0.10 pooled SD for continuous primary contrasts and at most 0.10 wide for extinction probability; otherwise call the result unresolved.
- **Evolution:** choose at most six regimes before looking at invasion outcomes. For no more than six directed resident-mutant pairs per regime, use at least 24 fresh resident cultures/event seeds (864 initial assays), expanding by the same precision rule.

Random streams are keyed separately for environment, demography, task outcomes, innovation, observation, and conflict override. Paired policies share exogenous streams without forcing state-dependent endogenous events to be identical.

## Failure-mode controls that can veto a claim

| Failure mode | Decisive control |
|---|---|
| Hidden-state leakage | Replay identical observed histories with different hidden `theta/z`; ordinary policies must emit identical decisions and random-key use. Audit the typed policy input object and its serialized log. |
| `d=0` secretly asocial | Show nonzero queries, social posterior changes, learned procedures, rational tutor-following, and teaching at `(0,0)`; compare separately with access-off asocial policy. |
| Conflict conditioning/collider bias | Randomize authority labels before response and report unconditional intention-to-treat effects; use frozen induced conflicts for conflict-conditional effects. Never rely only on naturally observed conflicts, teachers, survivors, or auditors. |
| Guaranteed tutor truth/expertise | All tutors start empty, learn through logged events, use identical sensors, and may transmit wrong/stale content. Teacher selection cannot access evaluator competence. |
| Pessimistic neutral evaluator | Exact tiny-world agreement, common horizon/value approximation, explanation and free-audit probes, and a resource-matched rollout planner. Reject effects that vanish only when an omitted common benefit is restored. |
| Intentionally weak comparator | Tune approximate and feature policies on discovery worlds only, grant identical features/caps, freeze them before holdout, and publish their calibration diagnostics. |
| Free social learning | Debit both parties' time and all energy/material costs once; replay the full ledger. |
| Action/belief/knowledge bundling | Separate state variables and update logs; an override without new evidence must not alter `B` or `K`. |
| Adult rigidity imposed | Identical age-independent update capacity in the core; use learned habit and explicit interventions only in the later module. |
| Cultural immortality | Kill all carriers in a test; procedure access must become zero unless a separately enabled paid artifact exists. |
| Genetic content smuggling | Inspect blank newborn state; cross-foster, permute parent knowledge, and relabel task nodes/solutions on holdout. Content must follow exposure, not genotype/parent. |
| Needle/padded tasks | Enumerate/sample solution landscapes; require a safe alternative, at least two positive-net procedures, useful prefixes, nonzero private success, and robustness to relabeling, prerequisite shuffling, and no-op pruning. |
| Event-order artifact | Rerun alternative defensible ordering and proportional resource allocation; identify qualitative reversals. |
| Density/census forcing | Verify `N(t+1)=N(t)+births-deaths`, no replacement births, no hidden cap, and explicit censored runs. |
| Correlated testimony counted repeatedly | Clone one provenance lineage without new physical evidence; posterior evidence cannot scale as independent copies. |
| Selection in a fictitious culture | Newborn mutants enter stored resident snapshots and predominantly face resident teachers/resources; compare multiple independent cultural snapshots. |
| Extinction omitted | Every ecological and invasion summary includes extinct runs and reports establishment conditioning separately. |
| Manufactured interior optimum | Include endpoints, nearby conditional policies, scalar/vector distinction, and null/neutral worlds; no direct `d` term appears in reward, fertility, or mortality. |

## Additional modeler hypothesis beyond H1-H8

The independent adversarial review already numbers metareasoning equivalence and provenance saturation as H7 and H8. To avoid a conflicting label, this model-specific addition is:

**H9 — Cultural monoculture debt.** In slowly changing deep tasks, high procedural override can raise pre-change mean yield while reducing independent procedural lineage diversity; after an unannounced structural flip, such populations recover more slowly than matched populations with the same pre-change mean competence but greater lineage diversity.

The falsifiable signature is a `d_procedure x structural-change` interaction on recovery time that is mediated by pre-change effective lineage number, not by factual confidence alone. At the shock, match or reweight populations on census, age, energy, mean task competence, and repertoire depth; freeze births in a short diagnostic window; then swap cultural genealogies or impose a diversity-preserving teacher assignment without changing message count.

Rivals and discriminators:

- **Energy-reserve rival:** recovery differs because high-yield populations hold different energy. Equalize energy at the shock; a lineage-diversity effect should remain.
- **Source-calibration-lag rival:** stale reliability estimates, not monoculture, delay switching. Reset or equalize `T` while preserving procedures and genealogies.
- **Demographic-age rival:** carrier age/turnover explains recovery. Match ages and use the no-birth diagnostic window.
- **Pure competence rival:** only mean procedure quality matters. Compare populations matched on evaluator-scored competence but differing in independent procedure roots.

If the interaction disappears under these controls, H9 is invalidated; a null is fully acceptable. No literature-novelty claim is made here.

## Local design evidence

The separations and safeguards above operationalize the V7 brief in [`../V7_RESEARCH_DESIGN_AND_WORK_PROMPT.md`](../V7_RESEARCH_DESIGN_AND_WORK_PROMPT.md). The prior situational-advice model explicitly used one coefficient for action substitution and memory acceptance and preserved fixed source structure; see [`../v6/situational_advice/mathematical_model.md`](../v6/situational_advice/mathematical_model.md). The V5 repertoire companion provides a useful local precedent for acquired, rather than preloaded, founder knowledge and also states its fixed-census and independent-fact limitations; see [`../v5/repertoire_model.md`](../v5/repertoire_model.md). Those artifacts motivate the replacement but do not constitute V7 results.
