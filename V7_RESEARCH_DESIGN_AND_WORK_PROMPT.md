# V7 — Costly cultural competence, selective deference, and learned normative commitment

**Purpose:** a research design and executable Work/GSD brief, not completed V7 simulation results.

**Audited baseline:** `mertgkduman/population`, commit `9e95c6ce2e21587f9dbe2d18dcb5ab7787b140f6` (abbreviated `9e95c6c`). Review date: 2026-10-30. The audit below reads the model specifications, results, and situational-advice implementation; it does not independently rerun the full published sweeps.

**Primary recommendation:** replace the main homogeneous two-stage density model with a small, age-structured, individual-based simulation of costly acquisition and execution of reusable procedures. Preserve V1–V6 as immutable comparisons and preserve their accounting, provenance, validation, and visualization infrastructure. Build a reduced analytic model alongside the simulation, not instead of mechanisms that require individual histories.

## 1. What V6 actually establishes

The original V6 results report an abundance-maximizing `d=1` in all 12 adult-plasticity × environmental-hazard contexts. The same endpoint occurs for the best conditional mutant against the one specified resident. This is not an ESS result [R1].

However, at fixed maturation time tau=3 and adult plasticity=.1, held-out paths give mean abundance 2200.303 at d=0 versus 2077.566 at d=1 for kappa=.2. Thus the joint grid maximum at d=1 does not mean greater deference helps at every maturation time [R1].

The situational-advice extension already implements the proposed poorer adult access to juvenile-specific conditions. Juvenile local-cue accuracy is .90 and adult accuracy is .55, .70, or .85. It finds no interior deference maximum in its main grids, fixed-tau slices, or 33-value held-out sweeps at tau=3; conditional invasion maxima are endpoints too [R2].

Its most informative result is an ablation. At adult local precision .70, tau=3, and a stable environment:

| Mechanism | Best sampled d |
|---|---:|
| Full situational advice plus inferred memory | 0 |
| Clean explicit factual teaching | 1 |
| Action-only substitution | 0 |
| Memory-only acceptance | 1 |

This is evidence within the model that learning transferable knowledge and delegating the current local decision should not share one coefficient [R2].

V6 explicitly bundles action substitution and acceptance into memory. The default private query cost is zero. Adult private encoding is prescribed at .1 versus 1 for juveniles. Learning consists of bounded, unit-step evidence/conviction ledgers about one changing binary global truth. V6 itself acknowledges that this is not a clean identification of conflict-only deference, and that thinning encoding is mathematically equivalent to reducing the update rate [R3–R5].

Do not describe all earlier versions as single-fact models: V5 has a separate repertoire experiment with 4, 16, or 64 actual independent binary facts, endogenous teachers, and matched cue schedules. But that companion uses fixed-size cohorts and has no births, deaths, invasion, dependency-structured skills, or task rewards. Reuse its distinct knowledge items and paired sampling, not its fixed-census dynamics [R6].

### Interpretation

The endpoint results are legitimate negative findings for the tested mechanisms. The primary limitation is construct validity and task structure, not demonstrated numerical failure. Existing verification reports should not be presented as new independent verification by this design.

## 2. Scientific target and non-negotiable distinctions

Replace “obtain an intermediate d” with:

> Identify ecological and developmental regimes in which indiscriminate acceptance and indiscriminate rejection are both inferior, and determine whether the advantage requires authority-sensitive deference or is explained by ordinary social learning.

Three different results must never be conflated:

1. An individual uses a constant randomized propensity with a genuine interior optimum.
2. An individual makes almost deterministic but context-sensitive decisions; its aggregate acceptance rate is intermediate.
3. A population contains near-endpoint specialists whose mean propensity is intermediate.

A vector can have a biologically interesting selective policy at a corner, for example high acceptance of a reliable general procedure and low delegation of a local choice. That is not indiscriminate obedience. Do not penalize it merely because a coordinate is 0 or 1.

No acceptance criterion may require an interior maximum, an advantage for docility, dogmatism, bistability, or a new discovery. Do not add `+c*d*(1-d)`, a midpoint preference, or an arbitrary harmful-deference term to obtain a desired curve.

### Operational definitions

- **Social learning:** extracting information, procedures, or action values from other individuals.
- **Epistemic deference:** changing a factual judgment because of source authority, beyond the response explained by the available evidence and estimated reliability.
- **Behavioral deference:** executing an advised action despite the agent's current material-payoff estimate favoring an alternative.
- **Docility / approval sensitivity:** susceptibility to instruction, approval, and disapproval. This may alter motivation without changing factual belief.
- **Internalization:** a learned rule or preference continues to guide behavior without the original instructor, audience, or immediate social reinforcement.
- **Epistemic dogmatism:** deficient or source-asymmetric revision after informative, accessible counterevidence, relative to a stated matched benchmark. Strong confidence, persistence without new information, and a strong justified prior are not sufficient.
- **Normative commitment:** following a behavioral obligation; not automatically a false factual belief or epistemic dogmatism.

The causal claim is not “copying is good.” It is whether inherited or culturally acquired influence mechanisms have effects beyond equally competent, reliability-sensitive social learners.

## 3. Recommended model architecture

### 3.1 Age-structured individuals, not only two density compartments

Each individual i carries:

- age a_i, reproductive eligibility, energy/resources E_i;
- inherited policy traits g_i;
- acquired procedural repertoire K_i;
- beliefs about task mechanisms and local conditions B_i;
- estimated domain-specific source reliability T_i;
- learned habits and internalized norms H_i;
- sources/provenance of acquired information;
- biological parent and cultural teachers, recorded separately.

Use overlapping generations. Adult knowledge is produced by actual earlier learning. Offspring inherit policy traits, not factual knowledge or preloaded correct procedures. Founder culture must be acquired during a recorded burn-in, not silently seeded with experts. Include sparse, learned, and alternative founder-culture controls.

Learning can continue at all ages. Individuals can teach in domains where they have acquired competence; reproductive maturity must not automatically grant expertise. Juveniles can sometimes teach peers or older individuals. Age is a cue, not a correctness oracle.

Initially fix reproductive maturity tau. Study the deference mechanism first. Later permit a small age-dependent policy schedule and then maturation/allocation evolution. Changing the age when reproduction becomes possible is not, by itself, a costly transition: if reproduction is optional and nothing else changes, earlier eligibility weakly expands available choices. Do not manufacture a delayed-maturation optimum without an explicit developmental or reproductive investment tradeoff.

### 3.2 Small task worlds with reusable structure and private local context

Let the objective world be represented by a hidden structural mechanism:

    outcome = F_theta(procedure, local_context, environmental_noise).

Use a small prerequisite/causal graph with reusable subprocedures, not only independent facts. Begin with 2–3 task families and procedure depths 1, 3, and 6; expand only after the small model is understood.

An illustrative task is abstract resource processing: acquire inputs, prepare a tool, transform an intermediate, and choose a context-specific finishing operation. Early steps consume resources and final benefits are delayed. Include safe low-yield alternatives, partially useful subskills, and multiple viable solutions; avoid a single “needle in a haystack” solution designed to make independent learning impossible.

Separate two timescales:

- **Reusable structure theta:** changes slowly, with occasional technology/ecology changes.
- **Current context z_i,t:** individual-specific, faster-changing, and observed imperfectly.

The learner sees y_F drawn from P(y_F | z). A tutor sees y_T drawn from P(y_T | z, delay, distance), potentially noisier or stale. Teacher knowledge of theta is acquired, not stipulated. Both channels can be wrong, correlated, or reliable. Test cross-over cases where the tutor has better local knowledge too.

The adult can transmit:

1. a reusable conditional procedure;
2. a demonstration and its observable outcome;
3. a recommendation for the present situation;
4. a normative injunction or evaluative response in the later institutional extension.

These message types have different informational content. A learner may learn a procedure from an adult and still use its own observation to choose how to apply it.

Agents must never receive the hidden graph, true source reliability, correct task branch, environmental change time, or true payoff unless a declared benchmark has privileged access. The simulator knows truth for evaluation only.

### 3.3 Separate procedural competence from causal understanding

A learner can acquire a demonstrable procedure without recovering its full causal explanation. Conversely, an individual may understand a simple mechanism but lack a learned complex procedure. Record both.

Use small explicit latent hypotheses and Bayesian or well-specified statistical updates where tractable. For the smallest worlds, enumerate hypotheses and compute an exact benchmark. For larger worlds, use interpretable finite-budget approximations, not a hidden neural-network agent as the first implementation.

Private and social observations have explicit likelihoods. Repeated copies from one testimony lineage are not automatically independent observations. Compare provenance-aware and provenance-blind learners. A teacher's confident statement is not a verified physical trial.

### 3.4 Learning consumes actual opportunities

Each agent has the same time, sensor, memory, and computation capabilities within a matched comparison. Activities compete for a finite event budget:

- private observation or intervention;
- observing a demonstration;
- querying or searching for a teacher;
- verifying a claim or procedure component;
- executing a production step;
- innovating/recombining a known procedure;
- teaching, provisioning, reproduction, or rest.

Costs arise from elapsed time, material expenditure, risk of trial, and teacher effort. Do not make social learning free by default or merely divide all cue rates by a “complexity” parameter.

Every genotype can independently discover and can learn socially. Deference must not change sensor accuracy, memory capacity, innovation success conditional on the same experiment, or physiological ability. Realized experience may differ because policies allocate the same resources differently; report that as a mediated effect rather than an innate ability difference.

Use two experimental layers:

- **Yoked-history assays:** identical evidence, message content, budgets, and initial knowledge. These identify immediate deference effects.
- **Ecological life histories:** choices affect subsequent learning, survival, and cultural exposure. These estimate total demographic effects.

Do not confuse their estimands.

## 4. Deference must be a policy, not one bundled rate

### 4.1 A compact starting trait vector

Start with two primary conflict-response parameters:

    d = (d_procedure, d_local).

`d_procedure` affects willingness to execute an inherited procedure when the agent's own current evaluation would reject or interrupt it. `d_local` affects willingness to use a tutor's proposed local application when the agent favors another application.

Social information intake and memory are not switched off when these parameters are zero. A zero-extra-deference agent remains a capable social learner that evaluates testimony and demonstrations using the common learning mechanism.

Introduce, in separate modules rather than all at once:

    (gamma_approval, zeta_authority_credit, age_schedule).

`gamma_approval` weights social evaluation in motivation. `zeta_authority_credit` modifies epistemic authority weighting and is distinct from behavioral override. These are not different names for the same coefficient.

A useful realized response surface is:

    D(domain, age, confidence, estimated reliability, context mismatch)
      = P(follow advice | disagreement and observed state).

Fit/report this surface from actual decisions. A population-average d cannot replace it.

### 4.2 Primary identifiable arbitration rule

First compute a common, authority-neutral decision from all presently available private evidence, message content, demonstrations, and estimated source reliability. It may already follow the teacher. If its action conflicts with the tutor recommendation, a distinct conflict-override mechanism acts with probability d_domain(age, observable_state).

This identifies *additional* deference. A no-extra-deference agent is not an asocial control.

A conditional extension is:

    logit(d_i,k) = alpha_i,k + beta_age f(a_i)
                   + beta_r estimated_reliability
                   - beta_c private_confidence
                   - beta_x observed_context_mismatch.

No term uses true reliability or actual correctness. Domain labels must correspond to observable task features; include ambiguous/misclassified-domain robustness tests.

Behavioral action changes do not automatically overwrite factual belief. Belief, public action, and procedural memory have separate update rules. A joint-exposure baseline and accept×override factorial preserve comparability with V5/V6.

### 4.3 Alternative: authority in subjective value

The model-selection agent may prefer an explicit action-value formulation:

    P(a | history) ∝ exp{ [Q_material(a)
                          + beta_authority(domain, age) 1(a = advice)
                          + gamma_approval S_expected(a)
                          + H_learned(a)] / temperature }.

Here Q_material incorporates ordinary social evidence. The remaining terms identify authority-specific motivation, expected social evaluation, and learned commitments. Keep every term separately switchable.

Do not claim the two formulations are equivalent. They answer somewhat different questions; compare them on matched probe trials and retain one as the main model.

### 4.4 Strong comparator requirement

A fully optimal learner with the correct generative model, all the same observations, the same utility, and a policy class that includes deference cannot be outperformed in expected utility by a restricted deference heuristic. This is a policy-class inclusion argument, not a biological assertion.

Therefore, any advantage of an authority disposition must be traced to limited computation, limited lifetime experience, different social consequences, an informative evolved prior, or a commitment mechanism. Do not defeat an intentionally weak learner and call the result evidence for a specialized adaptation.

If deference is behaviorally equivalent to an ordinary reliability prior or feature-based reward learning, report that equivalence. Genetic preconfiguration and lifetime acquisition may still have different learning costs, but they are different hypotheses from a uniquely deferential faculty.

## 5. Cultural accumulation and social technology

### 5.1 Genuine cumulative procedures

Record innovations, parent procedures, recombination, transmission fidelity, mastery, and verified outcomes. No global library survives for free after all carriers die. Access to artifacts or written storage is an explicitly enabled institutional variant with its own cost and persistence.

Test accumulation by comparing:

- actual cross-generation transmission and innovation;
- no-transmission lineages with the same per-person resources;
- matched total-work independent solvers;
- transmission without further modification;
- innovation without retention;
- identical recipes with prerequisite structure shuffled or removed.

Measure functional performance, useful depth, diversity, and coverage separately. Increasing confidence or the number of stored statements does not establish cumulative improvement.

### 5.2 Optional institutional/norm package module

After the epistemic model passes its tests, let tutors transmit bundles containing useful procedures, conventional steps, and evaluative rules. Agents do not see evaluator-only labels such as “useful,” “ritual,” “false,” or “parasitic.”

The point is not to hard-code harmful dogma. It is to ask whether costly component-by-component verification allows low-value components to persist alongside valuable knowledge.

Include independently switchable mechanisms:

- practical verification is expensive;
- teachers prefer or reward particular behavior;
- pedagogical access can depend on compliance;
- recurrent approval/disapproval trains habits or normative preferences;
- cultural rules affect what should be investigated or taught.

Any real food, protection, access, or teaching transfer must be accounted for on both sides. Approval can be a psychological reinforcement signal without being a direct fecundity bonus. Do not insert a payoff for being obedient.

Useful and self-serving norms need separate material games. A coordination rule may benefit participants without being a factual belief. A costly cooperative rule may benefit partners or kin and require explicit assortment, reciprocity, or kin structure. A well-mixed public-goods model must not be expected to select costly altruism merely because total group output rises.

If tutor incentives evolve, give tutors heritable or cultural strategies, actual costs, and measurable payoffs. Do not stipulate that all adults act in offspring interests or that all exploit them.

This module is closely related to Simon's docility argument [L1]; it is a mechanistic elaboration, not a claim that the basic idea is new.

## 6. Adult persistence, internalization, and dogmatism

Do not impose lower adult sensory accuracy, freeze beliefs at maturation, or set rigidity to an increasing function of juvenile d.

Allow acquired histories to affect later behavior through explicitly labeled candidates:

1. learned action values and procedural habits;
2. bounded verification effort;
3. overcounting correlated testimony when provenance is unavailable;
4. reputation and anticipated approval;
5. learned rules about whom to trust or whether to audit.

All agents remain capable of encoding reliable evidence unless the model explicitly studies an evolved/learned evidence gate. Such a gate is a mechanism being assumed and selected, not a fact already explained.

Run three adult interventions:

- **Audience removal:** remove tutors, observers, sanctions, and promised social rewards.
- **Information equalization:** deliver the same reliable, independent counterevidence to adults matched on prior beliefs and resources.
- **Free audit:** remove the time/material cost of checking a challenged claim while preserving all other conditions.

Measure factual posterior changes, choices, and persistence separately. Failure to revise because evidence was never encountered is not dogmatism. Rational retention of a strong prior after weak evidence is not dogmatism. Updating belief but retaining an obligation is normative commitment, not factual blindness.

A standardized evidence sequence should include both directions and matched strengths. Compare revision slopes to a likelihood-aware benchmark, conditioning on prior confidence. Track correct and incorrect persistence, not only stability.

## 7. Demography and selection

### 7.1 Resource-accounted variable population

One possible transparent energy update is:

    E_i(t+1) = E_i(t) + production_i - maintenance_i
               - experiment_cost_i - teaching_cost_i
               - offspring_investment_i + net_transfers_i.

Intermediate actions and failed experiments consume time/resources even when no final benefit occurs. Fecundity depends on eligibility and available energy, and reproduction spends a declared cost. Death arises from baseline hazard, starvation, and task hazards. Newborns are not replacements inserted to maintain a fixed census.

Retain a simple saturating environmental resource factor if useful, but avoid duplicated density regulation and unlimited adult productivity. Log N(t+1)-N(t)=births-deaths exactly, and close the resource ledger including provisioning.

No direct demographic rate may contain a deference, obedience, dogma, or “good morality” bonus.

### 7.2 Separate objectives

Report:

- resource yield and learning/verification costs;
- births, deaths, survival to maturity, realized offspring;
- finite-window per-capita growth and low-density growth under a specified protocol;
- mean regulated abundance and extinction probability;
- actual cumulative knowledge performance;
- adaptation/recovery, including censored or failed recoveries;
- rare-mutant invasion and direct competition;
- internalization and dogmatism assays.

Regulated equilibrium net growth is near zero by construction. It cannot be the only fitness metric. Do not calculate stochastic growth by arithmetic averaging instantaneous eigenvalues. Do not average log abundance only among surviving runs and omit extinction.

### 7.3 Actual evolutionary tests

A grid of isolated populations is not evolutionary selection. After candidate regimes are found, test resident–mutant competition and, where appropriate, long-run rare-lineage growth.

Mutants face the actual resident cultural and resource environment. With oblique transmission they usually learn from residents; do not give them a fully mutant teacher pool. With explicitly vertical transmission, preserve real mutant-parent/offspring correlations rather than erasing them. State the cultural transmission rule in every invasion plot.

Introduce mutants as newborns for the default assay; warm-started adults answer a different invasion question. Separate transient initial-condition effects from asymptotic lineage growth. Track finite-lineage extinction and neutral drift. Use self-mutant and exchange-symmetry tests.

A positive finite-window invasion value does not prove fixation or ESS. For candidate interior attractors, examine selection on both sides, local and distant competitors, alternative cultural initial conditions, and direct multi-strategy competition. Report polymorphism rather than hiding it behind mean d.

## 8. Why heterogeneity alone is not enough

With fixed source outcomes and constant random copying:

    V(d) = (1-d) V_private + d V_adult.

Averaging this expression over contexts remains affine. Adding independent adult noise or mixing easy/hard tasks alone does not guarantee an interior optimum.

Nonlinearity can instead arise from mechanisms such as:

- acquiring a finite reusable repertoire with diminishing marginal coverage;
- current decisions changing future available knowledge;
- costly selective verification or delayed execution commitments;
- endogenous source reliability and innovation;
- coordination or competition with frequency-dependent returns;
- correlated environmental shocks affecting multiplicative demographic growth.

None is sufficient in every parameter regime. A conditional policy may eliminate an apparent scalar tradeoff by accepting the right component and rejecting the wrong one. That is an important result, not a defect.

### Analytic diagnostic A: finite useful items

If accepted learning encounters arrive at rate nu*d, there are M equally likely useful items, and each distinct item has future value v, expected acquired-item value after exposure T is

    v M [1 - exp(-nu*d*T/M)].

If the same *restricted bundled policy* also creates d*L costly context errors with cost c per error, its reduced expected payoff is

    W(d) = v M [1 - exp(-nu*d*T/M)] - c L d.

This has an interior maximum only when

    v nu T exp(-nu*T/M) < c L < v nu T,

with d* = M/(nu*T) log[v nu T/(c L)].

This is a derived occupancy/decision-cost diagnostic, not a permitted direct “fitness versus d” function for the main model. Once knowledge uptake and local compliance can vary independently, the compromise may disappear. Use the vector-policy comparison to expose that possibility.

### Analytic diagnostic B: shared environmental risk

In a scalar non-age-structured diagnostic with equally frequent shared environments, let actual per-generation multipliers from decisions be W_good=1+.4d and W_bad=1-.3d. Then arithmetic mean multiplier favors d=1, while log growth

    G(d)=.5 log(1+.4d)+.5 log(1-.3d)

is maximized at d=5/12. This proves only that an interior is possible under multiplicative shared risk. Independent idiosyncratic errors averaged within a large population do not automatically produce the same result. Nor does merely logging the output of an affine continuous-time scalar growth equation. Derive the appropriate growth measure for the actual age-structured simulation.

## 9. Model comparisons and causal probes

Essential comparators:

| Comparator | Why necessary |
|---|---|
| Asocial learner | Value of cultural access, not the main deference comparator |
| Reliability-sensitive social learner | Ordinary social learning without extra authority response |
| Feature-based learned trust | Domain-general learning alternative |
| Fixed scalar deference | Direct bridge to V6 |
| Two-domain/vector deference | Separates procedural acceptance from local delegation |
| Authority/approval-sensitive learner | Tests docility beyond information transfer |
| Exact small-world planner | Information/value bound and implementation check |
| Resource-matched approximate planner | Tests whether deference is a cheap useful heuristic |

Hold observation hardware and memory/computation budget fixed. Charge extra computations as operations/time in the same resource budget. Give benchmark algorithms adequate tuning on separate training worlds; do not handicap them or tune solely the preferred model.

Necessary matched interventions:

- Hold message and evidence content fixed; vary whether it carries an authority cue.
- Hold instruction fixed; vary demonstrator age independently of competence in a controlled assay.
- Remove approval, sanctions, and material access consequences separately.
- Transmit general rules with local observations versus issuing a local command.
- Equalize tutor and learner local access; reverse the access advantage.
- Remove instruction opacity by providing causal explanation or cheap verification.
- Randomize testimony provenance while preserving the number of repetitions.
- Break intergenerational inheritance without changing present teaching exposure.
- Remove prerequisites while preserving marginal rewards and task frequencies.
- Remove within-agent habit/internalization memory while retaining procedural knowledge.

An authority-label effect is not automatically irrational: labels can be informative. Use matched or explicitly uninformative labels and condition on what the learner knows about reliability.

## 10. Research hypotheses

Treat these as predeclared candidates, not expected outcomes.

**H1 — Domain dissociation.** Greater procedural opacity increases the advantage of transmitting executable procedures, while greater tutor–learner context mismatch decreases the advantage of local delegation. The test is the interaction of interventions, not only the location of a maximum.

**H2 — Additional authority advantage.** Under finite verification and lifetime sampling budgets, an inherited authority-response bias can outperform a matched learned-trust learner in some regimes. This advantage should shrink when verification or lifelong source-calibration becomes cheap. Failure is informative.

**H3 — Developmental path dependence.** Early social reinforcement changes adult decisions after instructor removal, independently of acquired technical competence. Factual dogmatism requires the stricter counterevidence assay.

**H4 — Cultural hitchhiking.** Low-value components can persist when co-transmitted with difficult-to-verify useful procedures; cheaper component-wise testing reduces retention. Distinguish true complementarity, coordination value, and teacher-imposed access conditions from hitchhiking.

**H5 — Ecology/evolution divergence.** Isolated abundance-optimal policies can differ from invasion-resistant policies because cultures and innovations are shared. Measure rather than assume the discrepancy.

**H6 — Dissociation rather than rigidity.** Early trusted instruction can enable more competent adult independence, rather than dogmatism, by supplying reusable knowledge. Compare to H3 rather than treating all retention as rigidity.

The research agents must propose at least two additional hypotheses not supplied here, with explicit rival explanations and observable discriminating tests. Search for precedents after exploratory findings; mark rediscoveries accurately.

## 11. GSD-spike execution sequence

Use the installed GSD tools. Discover the actual command and conventions before invocation. The documented quick spike workflow skips intake and produces 2–5 executable Given/When/Then investigations and evidence-backed verdicts [L10]. Do not silently assume a CLI binary exists.

### Spike 1 — Audit and behavioral kernel

Given: the pinned V5/V6 source and the fixed-source affine baseline.
When: implementing separated content learning and conflict override in a tiny task world.
Then: reproduce baseline endpoints, neutral cases, source access equalization, and the no-extra-deference social-learning comparator; verify private competence is invariant under yoked histories.

Stop adding ecology until these pass.

### Spike 2 — Procedures and cost of verification

Given: reusable multi-step procedures, delayed rewards, safe alternatives, and equal resource budgets.
When: varying structural depth, learning/verification cost, and tutorial content.
Then: identify whether the benefits are procedural social learning, authority override, or computational economy. Include a source-aware planner and a learned-trust baseline. Establish genuine cross-generation accumulation, not only increasing stored information.

### Spike 3 — Local context and conditional deference

Given: a learned adult repertoire and independently varied tutor/learner context sensors.
When: sweeping (d_procedure,d_local) and environmental timescales.
Then: compare vector policies with the scalar restriction, assess true interior optima versus context-specialized policies, and test whether source mismatch rather than learning quality explains the outcome.

### Spike 4 — Docility and learned persistence

Given: the working epistemic model.
When: enabling one institutional/norm mechanism at a time and applying audience-removal, free-audit, and evidence-equalization interventions.
Then: distinguish compliance, internalization, factual belief persistence, and dogmatism. Do not relabel a low update rate as an evolved dogma mechanism.

### Spike 5 — Demography, evolution, and adversarial replication

Given: one or two interpretable candidate mechanisms from earlier spikes.
When: adding resource-accounted variable population, competing inherited policies, held-out task worlds, and multiple cultural initial conditions.
Then: quantify demographic consequences and selection, test endpoint and conditional competitors, and reproduce surviving findings independently.

Build the dashboard incrementally after Spike 2, not after an unexplained giant sweep.

### Research roles

Use a primary orchestrator with bounded, fresh-context specialists:

- literature/novelty reviewer;
- mathematical modeler;
- simulation engineer;
- adversarial methods reviewer;
- verification/visualization specialist.

If parallel delegation is unavailable, execute these roles sequentially and record independent checks. Do not claim nonexistent agents ran.

Require an agent-generated alternative model, such as a resource-rational metareasoning model, a finite cultural-inventory process, or a network model of domain-specific expertise. Compare its predictions with the recommended agent-based task model. Do not implement every suggestion merely because it appears in this specification.

## 12. Experimental design and verification

Use pilot factorial designs on a few mechanistically chosen scenarios, then refine. Do not launch a full Cartesian grid over every cognitive, genetic, institutional, and ecological variable.

Suggested starting design, explicitly hypothetical:

- procedure depth: 1, 3, 6;
- stable, slowly changing, and rapidly changing global structures;
- fast local contexts with three tutor–learner observation-gap conditions;
- low, medium, high verification-to-production cost ratios;
- scalar d grid as a compatibility control;
- two-dimensional domain-deference grid as the main exploration;
- 4 discovery seeds, then at least 24 fresh confirmation seeds, expanded according to a prespecified Monte Carlo precision criterion rather than significance chasing.

Use paired external worlds and exogenous event streams. Random streams should be keyed to individual/task/event identities where possible; a different number of decisions must not accidentally desynchronize every later random event. Explicitly distinguish shared environmental, demographic, innovation, and observation randomness.

Separate parameter discovery from confirmation. Freeze candidate policies before holdout evaluation. Confirm over adjacent parameter regions and alternative task graphs, not just one favorable seed or one selected grid cell. Compare against nearby boundary values, endpoint strategies, and conditional competitors. Do not infer optimum certainty from a single colored maximum.

Verification must include:

- population and energy conservation;
- no reproduction without recorded cost/eligibility;
- no factual inheritance through the genotype;
- no advice when no reachable informed source exists;
- source-label independence in a label-neutral learner;
- equal private likelihoods and computation budgets across traits;
- all learning, teaching, verification, and production costs recorded once;
- acquisition distinct from execution and conviction;
- correct processing of repeated correlated messages;
- neutral selection and mutant-against-itself checks;
- no forced finite-population replacement or unreported simulation caps;
- stochastic convergence, event-order and timestep checks;
- agreement with exact tiny-world solutions;
- no knowledge surviving a total carrier loss unless storage is explicitly enabled;
- no use of true hidden state in an ordinary policy;
- correct handling of extinction and censored recovery;
- exported data exactly matching displayed figures.

## 13. Interactive HTML specification

Reuse the versioned portal and existing offline/export machinery, but add a scientifically distinct V7 section. Preserve V1–V6 results byte-for-byte unless an explicitly documented independent bug correction is authorized. Never rewrite old endpoint findings to make V7 look better.

Required views:

1. **Decision microscope.** Replay an actual interaction: learner private observation, tutor observation, source history, transmitted procedure/advice, inferred beliefs, recommendation conflict, accepted action, costs, delayed outcome. Include hidden truth as an evaluator-only overlay clearly unavailable to agents.
2. **Two-domain policy map.** Axes d_procedure × d_local; color selectable invasion growth, demographic performance, useful knowledge, or authority-specific effect. Show uncertainty and whether the cell is observed or an explicitly labeled interpolation.
3. **Environmental regime map.** Axes task opacity/verification cost × context mismatch or volatility; identify the best supported policy class, not only a scalar optimum. Mark unresolved ties and out-of-domain cases.
4. **Life-course and cohort view.** Age, skill, causal understanding, conviction, source use, resources, reproduction, and acquired norms; play/pause/scrub actual saved simulations.
5. **Cultural genealogy.** Reusable procedures and norm components, modifications, source lineages, functional performance, and transmission. Separate cultural reproduction from biological reproduction.
6. **Intervention panel.** Audience removal, explanation, reliable contrary evidence, and free audit; compare belief revision with behavioral persistence.
7. **Evolution panel.** Pairwise invasibility, direct competition, distributions of traits, initial cultural conditions, and any coexistence. Do not equate an isolated heatmap maximum with ESS.
8. **Research ledger.** Hypotheses, preregistered versus exploratory status, supporting and contradicting tests, and known limitations.

Make all view units and denominators explicit. Population glyphs should represent actual individuals or declared aggregates, not decorative populations disconnected from data. Keep storage reasonable: exact summary data plus representative actual trajectories, raw data separately. Exports include configuration, source revision, seed, cultural transmission rule, and metric definition. Build/test offline, and do not deploy publicly without explicit authorization.

## 14. Deliverables

Create a new `v7/` directory and normal spike artifacts. At minimum:

- `audit_v6.md` with pinned source evidence and what is retained/replaced;
- `literature_map.md` with primary sources, verified dates, closest precedents, and novelty limits;
- `constructs_and_estimands.md`;
- `model_candidates.md` including a serious independently proposed alternative;
- `mathematical_model.md` and a small exact/reduced model;
- `research_contract.md` with hypotheses, stopping/precision rules, and holdouts;
- reproducible simulation source, configuration schema, and versioned experiments;
- decision-level causal probe data and ecological outcomes;
- `verification.md` and executable tests;
- `results.md` separating analytic consequences, observed results, interpretation, and unknowns;
- `research_dashboard.html` and integration into the local versioned portal;
- a short manuscript outline only after results exist;
- GSD manifests with actual executable evidence and VALIDATED/INVALIDATED/PARTIAL hypothesis verdicts.

The final handoff must answer: what was already known; what V7 changed; what actually happened; what survives strong social-learning controls; whether the result is conditional policy specialization, stochastic interior behavior, or population polymorphism; whether dogmatism was generated, imposed, or absent; and what could plausibly be new.

## 15. Launch prompt

Paste the following into ChatGPT Work with this document and the repository available:

> Execute this V7 research specification using the installed GSD tools and the quick spike workflow. Discover its actual invocation before use. Inspect the pinned V6 baseline and the current repository; preserve existing scientific versions and do not deploy publicly. First perform the audit and construct-identification tests, then select a small age-structured task model with costly learning, reusable procedures, and private local context. Do not merely add another noise parameter to V6. Separate ordinary social learning from extra authority deference, approval sensitivity, and learned internalization. Generate at least one alternative model and two additional falsifiable hypotheses. Implement and test the selected model, conduct held-out confirmation and valid evolutionary comparisons, and produce the offline interactive V7 dashboard and reproducible evidence. Treat endpoint or null results as legitimate; do not manufacture an interior optimum or claim novelty without checking close precedents. Use the staged spikes, scientific safeguards, and deliverable requirements in this document. Run the research rather than returning only a plan.

## References and evidence

### Audited project artifacts

R1. V6 results, pinned release: https://github.com/mertgkduman/population/blob/9e95c6ce2e21587f9dbe2d18dcb5ab7787b140f6/v6/results.md

R2. V6 situational-advice results: https://github.com/mertgkduman/population/blob/9e95c6ce2e21587f9dbe2d18dcb5ab7787b140f6/v6/situational_advice/results.md

R3. V6 mathematical model: https://github.com/mertgkduman/population/blob/9e95c6ce2e21587f9dbe2d18dcb5ab7787b140f6/v6/mathematical_model.md

R4. Situational-advice mathematical model: https://github.com/mertgkduman/population/blob/9e95c6ce2e21587f9dbe2d18dcb5ab7787b140f6/v6/situational_advice/mathematical_model.md

R5. Situational-advice implementation: https://github.com/mertgkduman/population/blob/9e95c6ce2e21587f9dbe2d18dcb5ab7787b140f6/v6/situational_advice/experiments/model.py

R6. V5 repertoire companion: https://github.com/mertgkduman/population/blob/9e95c6ce2e21587f9dbe2d18dcb5ab7787b140f6/v5/repertoire_model.md

R7. V5 mathematical model: https://github.com/mertgkduman/population/blob/9e95c6ce2e21587f9dbe2d18dcb5ab7787b140f6/v5/mathematical_model.md

### Primary literature and methodological precedents

L1. Simon (1990), A mechanism for social selection and successful altruism. https://pubmed.ncbi.nlm.nih.gov/2270480/ — docility, bounded rationality, beneficial instruction and costly social influence.

L2. Acerbi, Enquist & Ghirlanda (2009), Cultural evolution and individual development of openness and conservatism. https://pmc.ncbi.nlm.nih.gov/articles/PMC2776418/ — cultural transmission can modify its own learning rules; do not claim this general mechanism as new.

L3. Derex, Bonnefon, Boyd & Mesoudi (2019), Causal understanding is not necessary for the improvement of culturally evolving technology. https://doi.org/10.1038/s41562-019-0567-9 — motivates separate procedural performance and causal understanding; not proof that understanding never matters.

L4. Saral, Ibanez de Aldecoa & Derex (2026), The roles of cultural transmission and causal reasoning in the cultural evolution of technology. https://pmc.ncbi.nlm.nih.gov/articles/PMC13070565/ — causal reasoning accelerates early improvement in these tasks, but cultural transmission can improve performance without it. Published March 26, 2026, PNAS Nexus 5(4), pgag090.

L5. Schultner, Molleman & Lindstrom (2025), Feature-based reward learning shapes human social learning strategies. https://pmc.ncbi.nlm.nih.gov/articles/PMC12545201/ — strong domain-general comparator, not evidence that all social learning is necessarily nonspecialized.

L6. Maisonneuve, Lehmann & Mullon (2025), The coevolution of learning schedules and teaching enhances cumulative knowledge and drives a teacher-innovator syndrome. https://pmc.ncbi.nlm.nih.gov/articles/PMC11813578/ — teaching/learning coevolution and specialization already have direct precedents.

L7. A demographic theory of similarity-biased social learning (2026). https://pubmed.ncbi.nlm.nih.gov/42531024/ — local knowledge transferability, target filtering, and frequency dependence. The work explicitly discusses age cohorts; contextual advice alone is not a novel gap. Verify full bibliographic author metadata during the agent's literature audit.

L8. Callaway et al. (2022), Rational use of cognitive resources in human planning. https://doi.org/10.1038/s41562-022-01332-8 — finite-computation planning and cost-aware comparison.

L9. Mesoudi & Thornton (2018), What is cumulative cultural evolution? https://pmc.ncbi.nlm.nih.gov/articles/PMC6015846/ — separates repeated transmission/improvement from storage or persistence alone.

L10. GSD documentation, Spike Command / quick workflow. https://www.opengsd.net/docs/v1/features — verify the installed interface; use Given/When/Then, executable tests, evidence-backed verdicts, and project-local manifests.

This is a targeted literature grounding, not an exhaustive novelty review. The execution team must trace direct and forward citations and revise the gap assessment accordingly.
