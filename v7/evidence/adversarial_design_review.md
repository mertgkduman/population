# V7 adversarial design review

**Review status:** preimplementation, 2026-11-02. No V7 implementation or empirical V7 result existed when this review was written. A proposed check is not a passed check.

**Scope:** causal identification and failure-mode review of `V7_RESEARCH_DESIGN_AND_WORK_PROMPT.md`, checked against targeted pinned V5/V6 source and results. The locally inspected files match the prompt's pinned commit `9e95c6c` by SHA-256 for the two V6 model files, both invasion files, both results files, `v5/experiments/repertoire.py`, and `v5/repertoire_model.md`. The pinned Git object is absent from the local clone, so parity was checked against the corresponding raw GitHub files rather than by local `git diff`.

## Verdict

The design is scientifically defensible only if its cautions become executable claim gates. Its central danger is not another endpoint optimum. It is a flexible agent-based model in which authority response, information acquisition, teacher access, computation, inherited priors, and cultural history can silently differ across genotypes. Any one of those differences can manufacture an apparent "deference advantage."

The minimal defensible causal sequence is:

1. prove on yoked histories that `d=0` remains a fully capable social learner and that changing extra override changes only conflict resolution;
2. prove newborn knowledge is blank and founders learn through logged events;
3. beat a resource-matched learned-trust/metareasoning rival, not an asocial or deliberately myopic control;
4. establish functional, genealogical cultural improvement with retention and innovation ablations;
5. close the demographic, resource, and invasion ledgers before making selection claims; and
6. reserve "dogmatism" for deficient factual revision under matched, accessible counterevidence, while treating persistent action as habit or normative commitment until separately discriminated.

Null, endpoint, conditional-corner, and polymorphic outcomes are all legitimate. An interior mean is never itself evidence for an interior individual disposition.

## BLOCKER findings

### B1. The additional-authority estimand can collapse back into ordinary social learning

V6 demonstrates the exact confound V7 must remove. In both model variants, `_weights` starts with `w=d`; `w` controls public action substitution and also scales testimony written into memory (`v6/experiments/model.py:85-96,112-144`; `v6/situational_advice/experiments/model.py:91-100,115-147`). Thus `d=0` is effectively denied that social-memory channel. The V6 ablation is useful evidence that action and storage matter differently, but it does not identify extra authority response.

**Claim gate:** under identical messages, demonstrations, source histories, sensor outputs, initial states, and event/computation budgets, a neutral reliability-sensitive learner and every `d` genotype must compute the same authority-neutral posterior and material action value before the conflict override. `d` may act only after a logged conflict. Randomly permuting an explicitly uninformative authority label must leave the neutral learner invariant. If `d` changes acquisition, reliability estimation, search success, memory, evidence availability, or private experiment success on a yoked history, no authority-specific causal claim is allowed.

**Minimum test:** a content × authority-label × accept-to-memory × conflict-override factorial with common random event identities. Report the intention-to-treat authority-label contrast and the conflict-conditional override contrast separately. Conditioning only on naturally occurring conflicts is post-treatment selection unless conflicts are induced from a common frozen pre-override state.

### B2. Genotype, inherited prior, and factual/procedural inheritance are not yet separated by an executable firewall

The prose says offspring inherit policies but not content. That is necessary but insufficient. A genotype can still carry a task-specific lookup table, graph-indexed prior, source ID, or initialized value function that encodes the correct solution while being named a "policy." V6 births are neutral (`v6/experiments/model.py:145-151`), but V6 initial adults are preloaded 80% correct at conviction magnitude two (`v6/experiments/model.py:153-155`). The V5 repertoire founders are cleaner: they start at zero and acquire 16 logged private cues (`v5/experiments/repertoire.py:337-353`).

**Claim gate:** newborn `K`, factual `B`, provenance, habits, and task-specific action values must be blank before post-birth events. Cross-fostering and parent-knowledge permutation must make content follow cultural exposure, not biological parent. Relabeling task nodes and permuting solution branches in held-out worlds must prevent a policy genotype from smuggling a solution. An informative evolved prior is permitted only if it is declared and costed as such; it cannot count as learned cultural competence.

### B3. The proposed strong comparator can still be weakened by budget or tuning asymmetry

The exact planner is an upper bound only if it receives the same observations and utility and its policy class contains the focal behavior. The practically important rival is a finite resource-rational learner, not an unlimited oracle and not a weak heuristic. It must decide whether to inspect, query, verify, execute, or teach using the expected value of computation, learn domain-specific source reliability, and respect testimony provenance. Authority/age is merely a learnable feature, with no authority bonus.

**Claim gate:** use an exact tiny-world Bayes-adaptive/POMDP solution where feasible and a separately tuned resource-matched approximation for ecological worlds. Count every model update, hypothesis evaluation, search, query, and verification operation under the same budget. Use equal training worlds and freeze hyperparameters before holdout. If the focal heuristic exceeds the exact policy under the same information and utility, assume a bug or mismatch. If it beats only the finite approximation, the supported claim is computational economy under the stated approximation, not a uniquely deferential faculty.

### B4. Task graphs can manufacture social-learning and authority advantages through a hidden needle

Depth 6 is not automatically a meaningful cumulative task. A unique all-or-nothing path, zero-valued prefixes, privileged founder solutions, or vanishing independent discovery probability would make social access mechanically essential. Conversely, padding a recipe with no-op nodes can manufacture "depth" without progress.

**Claim gate:** before selection experiments, enumerate or sample the solution landscape with an exact small-world solver. Report the number/measure of viable solutions, best safe alternative, marginal reward of useful prefixes, private-discovery probability under the same total work, and minimal pruned successful depth. Require at least two viable solution families and nonzero partial rewards in the primary world. Repeat claims on graph ensembles with branch labels permuted, prerequisites shuffled, and no-op nodes pruned. A condition in which private solvers have zero successes cannot by itself support an adaptation claim.

### B5. Statement accumulation, recipe length, and persistence are not cumulative procedural progress

V5 explicitly measures independent-fact accuracy and coverage, not multi-step functional technology (`v5/repertoire_model.md`). V7 must not promote counts of statements, confidence, nominal depth, or mere survival of a recipe into cumulative culture.

**Claim gate:** require realized held-out task performance plus a cultural genealogy linking successful modifications across at least two transmission steps. Compare with no transmission at matched per-person and total work, transmission without modification, innovation without retention, and shuffled prerequisites. The functional trend must depend on both retention and modification. Report minimal useful depth after pruning dead steps, not serialized recipe length. Total carrier loss must erase culture unless a separately costed artifact store is enabled.

### B6. Demographic and invasion claims fail if accounting, extinction, or teacher composition is conditioned incorrectly

The V6 rare-mutant code broadcasts a resident-derived teacher/resource environment to every mutant (`v6/experiments/invasion.py:8-17`), which is appropriate for its declared conditional assay, although mutants are warm-started as scaled copies of a state containing adults (`v6/experiments/invasion.py:19-22`). V7's individual model introduces more opportunities for leakage: transfers can be counted as production, teaching may be free on one side, extinct lineages can disappear from growth estimates, and rare mutants can accidentally receive mutant teachers.

**Claim gates:** every event has one ledger ID; transfers sum to zero apart from declared conversion loss or external input; teaching/provisioning debits the donor and credits the recipient once; births spend energy and satisfy eligibility; and the population identity closes exactly. Report extinction unconditionally. Never average log growth only among survivors. In oblique transmission, a newborn rare mutant draws teachers from the actual resident-dominated reachable pool; it does not receive a mutant teacher pool. In vertical transmission, retain the real mutant-parent correlation. Introduce default mutants as newborns, with adult warm starts labeled as a separate estimand.

### B7. Audience removal plus persistence does not identify a norm, and persistence does not identify dogmatism

The design correctly separates belief and action, but its planned interventions still leave a rival: cached instrumental habit. A habit can persist after audience removal and free audit while factual beliefs update normally. Conversely, a rational strong prior may resist weak counterevidence without dogmatism.

**Claim gate:** keep factual posterior, expected material value, anticipated social evaluation, cached habit value, and normative obligation state distinct in both state and output. Dogmatism requires a shallower or source-asymmetric factual revision slope than a likelihood-aware matched benchmark under strong, independent, accessible evidence, conditioning on the prior. Normative commitment requires action persistence with adequate factual revision and no current audience, sanction, promised reward, or material access consequence. To distinguish it from habit, add outcome devaluation/contingency degradation and obligation-generalization or explicit countermand probes. If those mechanisms are not modeled, report "learned action persistence," not normative internalization.

## IMPORTANT findings

### I1. Interior behavior has three incompatible generators

Every reported intermediate mean must be decomposed into:

- within-agent stochastic propensity under repeated identical observable states;
- nearly deterministic conditional response across states; and
- between-agent polymorphism.

Export genotype/policy parameters, individual repeated-state responses, the conditional disagreement surface, and population distributions. A scalar mean or heatmap is insufficient. Synthetic classifier fixtures should include all three cases before simulation results are interpreted.

### I2. Earlier reproductive eligibility weakly dominates later eligibility unless a real tradeoff is imposed

If reproduction is optional and eligibility changes nothing else, the earlier-eligible policy can reproduce the later policy exactly by waiting. It has a superset of feasible actions. Any later-maturity advantage then reveals an implementation side effect, forced reproduction, or an undeclared investment tradeoff.

**Safeguard:** a paired emulation test must show that an early-eligible agent forced to use the later policy's reproduction schedule has the identical state/resource path. Evolve maturity only after adding and reporting a developmental allocation or reproduction-opportunity tradeoff.

### I3. Founder acquisition needs sparse and failed-culture controls, not only a burn-in label

A recorded burn-in can still seed experts if it uses privileged demonstrations, excessive work, or selection on surviving successful founders. Predeclare blank, sparse/private-acquisition, ordinary learned, and alternative/wrong founder cultures with equal logged budgets. Include unsuccessful burn-ins and report selection into the analyzed founder pool. Do not discard failed cultures and call the remainder representative.

### I4. Testimony lineage must be part of the evidence model

Repeated copies of the same root trial are not independent likelihood factors. Give physical trials and innovations immutable root IDs and messages a provenance DAG. A provenance-aware learner should be invariant to duplicating a message along the same known root, except for explicitly modeled evidence about transmission fidelity. A provenance-blind comparator may overcount, but its advantage/disadvantage must be labeled as such. Merging lineages requires set union of unique roots, not summing path counts.

### I5. Shared multiplicative risk does not transfer automatically to the age-structured population

The scalar diagnostic is correct, but only for shared multiplicative environments with the stated frequency. Idiosyncratic errors diversified within a large population, density regulation, overlapping ages, and reproduction timing change the growth object. The implemented model needs its own low-density random projection/branching derivation or a clearly defined finite-window estimand. Arithmetic abundance, mean instantaneous eigenvalues, and survivor-conditioned log abundance are not substitutes.

### I6. Conditional analyses can induce collider bias

Teacher availability, disagreement, survival to adulthood, and having enough resources to audit are all policy-affected. Contrasts restricted to observed conflicts, observed teachers, survivors, or auditors need a yoked predecision assay or explicit principal-stratum/standardization interpretation. Always report unconditional intention-to-treat contrasts alongside conditional mechanism summaries.

### I7. Keyed randomness must prevent policy-dependent random-stream drift

Policies take different numbers of actions. Sequential RNG consumption can make all later environments, innovations, births, and observations differ, creating a fake treatment effect. Key exogenous draws by world/replicate/time/entity/event type and demonstrate that unused policy-specific draws do not change future exogenous events. Shared environmental randomness, individual demographic randomness, innovation randomness, and observation randomness need separate namespaces.

### I8. Hidden-state access requires a runtime information-flow audit

The simulator needs truth to score outcomes. Ordinary policies must not receive graph truth, actual correctness, true source reliability, future change times, or evaluator labels. Use typed observation objects or capability boundaries, log every policy input, and test label permutation. Oracle benchmarks must be named and excluded from ordinary comparisons.

## Analytic diagnostics: independent checks

### Occupancy diagnostic

For a Poisson encounter process of rate `nu*d` whose events are uniformly split among `M` items, Poisson thinning gives each item's count as Poisson with mean `nu*d*T/M`. Therefore

`E[distinct] = M[1-exp(-nu*d*T/M)]`.

For `W(d)=vM[1-exp(-nu*d*T/M)]-cLd`,

- `W'(d)=v*nu*T*exp(-nu*d*T/M)-cL`;
- `W''(d)=-v*(nu*T)^2/M*exp(-nu*d*T/M)<0`; and
- a strict interior maximum occurs exactly when `v*nu*T*exp(-nu*T/M) < cL < v*nu*T`, with the stated `d*`.

An independent numeric minimization with `M=7, nu=1.3, T=4.2, v=2, cL=7` found `d*=0.5701100238`; the closed form is `0.5701100273` (absolute difference `3.47e-9`). One million Poisson-splitting replicates agreed with the occupancy expectation within `0.00180` items at the four checked `d` values.

**Boundary:** the exponential formula depends on Poisson arrivals. With exactly `N` encounters, the expectation is `M[1-(1-1/M)^N]`. At `M=7,N=5`, this is `3.761349`, versus `3.573208` under a Poisson count with mean five. The implementation must declare which arrival process it uses. The reduced payoff also bundles uptake and costly local error into one scalar `d`; it is a diagnostic of a restricted policy, not evidence that vector deference should be interior.

### Multiplicative-risk diagnostic

The arithmetic multiplier is `1+0.05d`, so it is maximized at `d=1`. For

`G(d)=0.5 log(1+0.4d)+0.5 log(1-0.3d)`,

setting the derivative to zero gives `d=5/12`; the second derivative there is `-0.117551<0`. Independent bounded optimization returned `0.4166666707` (absolute difference `4.01e-9`). Numerically, `G(0)=0`, `G(1)=-0.0101014`, and `G(5/12)=0.0103096`.

This verifies the scalar example only. The V7 implementation still needs an age-structured growth derivation and must separate shared environmental shocks from idiosyncratic within-population errors.

## Strongest rival model

Use a **provenance-aware resource-rational metareasoner** as the primary rival.

Its state is a posterior over small task graphs, local context, and domain-specific source reliability, plus the set of unique evidential roots. Its actions are private observation/intervention, observe demonstration, query, verify a component, execute, innovate, teach, or rest. At each decision it allocates a common event/computation budget using the expected value of computation or a separately trained approximation. Age, prestige, and authority labels are ordinary observable features whose predictive value must be learned; there is no source-authority bonus or forced override. A habitual action-value cache can be added as a separately switchable rival for persistence.

This model predicts apparently deferential behavior whenever reliable teachers cheaply compress search, but predicts no effect of a randomized uninformative authority label after content and learned reliability are held fixed. It predicts reduced reliance when audit becomes cheap and no factual dogmatism after strong evidence equalization, although action habits may remain. On tiny worlds solve it exactly; on ecological worlds match its operations/time and tune it on separate worlds.

The decisive contrast is not focal deference versus asocial learning. It is focal deference versus this rival on frozen, yoked histories and held-out graphs. If both make the same choices and achieve the same value, authority deference is behaviorally redundant. If focal deference wins only because it begins with an informative source prior, report a genetic-prior/lifetime-learning cost comparison. If it retains a randomized-label effect with no reliability information, that is the clean authority-specific effect—but it still needs a demographic benefit rather than a direct obedience bonus.

## Additional hypotheses and counterexamples

### H7 — Metareasoning equivalence

**Hypothesis:** the apparent advantage of inherited authority response vanishes when a provenance-aware learned-trust agent receives the same calibration experiences and computation budget.

**Rival:** inherited deference is a lower-cost prior that remains advantageous under short lifetimes even after fair calibration.

**Test:** cross lifetime length × calibration cost × free-audit intervention on held-out relabeled graphs. Compare authority-label ITT effects, functional yield, total operations, and growth. A remaining advantage must be decomposed into prior information versus execution override.

### H8 — Provenance saturation

**Hypothesis:** benefits attributed to authoritative repetition are largest when learners overcount copied testimony and shrink sharply when unique evidential roots are tracked.

**Rival:** repeated messages provide independent evidence about transmission fidelity or source consensus even with common roots.

**Test:** hold message count and content fixed while varying the number of unique root trials and disclosed lineage structure. Cross provenance-aware/blind learners. Measure posterior change, audits, action, and performance.

### Counterexample 1 — Conditional corner dominates a scalar interior

A world can make `d_procedure=1, d_local=0` dominate every scalar `d`, while the scalar restriction has an apparent interior optimum. This is not an interior agent disposition; it is omitted policy dimensions. Always include the vector comparison before interpreting a scalar curve.

### Counterexample 2 — Habit mimics internalized obligation

Repeated approval can cache an action value that survives audience removal even when factual posterior revision is normal. Audience removal, information equalization, and free audit alone can therefore produce "persistent behavior" without a represented norm. Outcome devaluation, contingency degradation, and obligation generalization are needed for the stronger label.

## Minimal robust implementation order

1. Build typed hidden state/observation separation and immutable event/provenance/resource ledgers.
2. Implement the tiny world, exact rival, neutral social learner, and extra override with yoked histories.
3. Pass inheritance, label-neutrality, duplicate-lineage, event-budget, and earlier-eligibility emulation tests.
4. Calibrate non-needle task ensembles before any preferred-policy sweep.
5. Establish functional accumulation with causal ablations and carrier-loss tests.
6. Add variable demography only after energy and census ledgers close exactly.
7. Add newborn rare-mutant assays with actual resident teacher composition and unconditional extinction reporting.
8. Add institutional/norm modules one at a time; do not use normative or dogmatism language until the discriminating probes pass.

The machine-readable gates and the independently measured formula values are in `v7/evidence/predeclared_checks.json`.
