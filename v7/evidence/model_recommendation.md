# V7 model recommendation

**Decision:** select the finite-resource task-and-culture IBM (Candidate A) in [`../model_candidates.md`](../model_candidates.md) for implementation, conditional on the pre-ecology gates below. Retain the provenance-aware resource-rational metareasoning model as the required substantive alternative and strong comparator. Do not implement the approval/habit module until the epistemic and demographic kernel passes.

**Evidence status:** this is a design-selection memo, not a result. Model equations, parameter envelopes, and power/replication rules are proposals to test. The only empirical/model-history statements below are tied to opened local source artifacts.

## Why this candidate is the smallest adequate replacement

The prior situational-advice model used one `d` both for present action substitution and the rate at which accepted testimony moved held memory: it states, verbatim, “The juvenile chooses the adult's action with probability `d`” and “Accepted testimony moves `b` one signed step at rate `d nu_S`.” [VERIFIED: `v6/situational_advice/mathematical_model.md:19-27,29-43`] Its main local-access scenarios also fixed learner sensor accuracy at `0.9` and adult accuracy in `{0.55,0.70,0.85}`, with every main adult channel worse. [VERIFIED: `v6/situational_advice/mathematical_model.md:7-9`] This makes it an informative bridge/control, but not the desired identification of content learning followed by additional conflict override.

The V5 repertoire companion did acquire founder evidence rather than preload teacher accuracy: it states, verbatim, “All founders start `u=b=0`, then receive 16 common private-cue opportunities before teaching,” and “there is no fixed teacher accuracy.” [VERIFIED: `v5/repertoire_model.md:18-38`] It also explicitly used “`D in {4,16,64}` independent binary facts,” fixed `N=128`, and no birth, death, density dependence, mutant invasion, or selection. [VERIFIED: `v5/repertoire_model.md:8-22`] V7 should preserve acquired founders and paired streams while replacing independent facts/fixed cohorts with prerequisites, individual histories, and real demography.

Candidate A is the minimum design that simultaneously provides:

- reusable prerequisite procedures at depths `1`, `3`, and `6` without making incorrect branches impossible;
- a separate fast local condition observed through equal hardware;
- a common content-and-reliability-based material value before any override;
- two extra conflict traits `(d_procedure,d_local)`, with `(0,0)` still fully social;
- acquired, fallible teachers of any age and paid teacher time;
- factual beliefs, procedural memory, action, approval expectation, and habit as different states;
- a finite environmental/individual energy ledger, costly births, variable deaths, and extinction;
- distinct biological and cultural genealogies with no default immortal library;
- exact-tiny, equally capped approximate, feature-trust, and resource-rational comparisons;
- paid mutant-newborn establishment and descendants in actual resident culture/resources.

Removing any one of those components leaves at least one central construct unidentified. Adding more task ontology, networks, multi-parent genetics, artifacts, or evolved teacher incentives now would increase state space without improving the first causal test.

## Selected implementation contract

### Core world

Use two task families per run and vary a common prerequisite depth `D in {1,3,6}`. Each prerequisite choice has a better and worse but viable transition probability, a failed prefix has small salvage, a safe exit has a known low yield, and a successful chain ends in a local binary finishing decision. Before any preferred-policy sweep, enumerate/sample the landscape and require at least two positive-net procedures, useful prefixes, nonzero matched-work private discovery, and robustness to branch relabeling, prerequisite shuffling, and no-op pruning. Slow structural bits and fast local context are evaluator-hidden. Learner and tutor have the same sensory accuracy; tutor/learner mismatch is created by distance/delay/context concordance rather than genotype or age.

Use 12-20 time tokens per individual-season and a hard cap of 128 primitive belief/value operations per decision as initial hypothetical values. Querying/teaching reserves time from both agents. Every private trial, verification, procedure step, computation, reproduction, and transfer is ledgered once. Environmental regeneration is an explicit inflow; conversion, maintenance, failure, and birth losses are explicit sinks.

### State and kernel

Maintain separate `B` (factual posterior), `K` (possibly wrong executable procedure), `T` (observable-history source reliability/provenance), public action, and later `H` (approval-trained habit). An override action without new evidence cannot itself edit `B` or `K`. Ordinary policies receive a typed, serialized observation object; simulator truth/evaluator objects are outside that interface.

All social policies first compute the same authority-neutral value

$$
Q^0(a)=E_{\widehat P}[\text{finite-horizon material return and declared future procedure value}\mid a,\text{observed history}],
$$

where social content and estimated source reliability already affect `P_hat`. If the maximizing action agrees with advice, follow normally. Only when it disagrees may the genotype override with `d_procedure` at prerequisite decisions or `d_local` at the finishing decision. True structure, true local context, true source reliability, and evaluator competence never enter an ordinary policy.

This ordering is essential: the comparison is *extra response after competent ordinary social evaluation*, not copying versus private ignorance.

### Founders and teaching

Start 48-96 founders with empty acquired state and run 40-80 seasons of logged monomorphic burn-in under the same learning costs. Never create a correct adult or recipe at initialization. Any adult competence at the snapshot must have been acquired; if none develops, no expert is supplied. Retain blank, sparse-private, ordinary learned, alternative/wrong, and failed/extinct burn-ins rather than conditioning on successful culture. Permit an individual of any age to offer a procedure after a stored recipe and at least two independent successful attempts. This offer rule uses observable mastery, not true correctness.

### Demography and culture

Reproduction is a costly event available after a fixed initial maturity age, not an automatic replacement. A newborn receives energy, an inherited/mutated policy, empty acquired state, and one biological-parent edge. Pre-exposure inspection, parent-knowledge permutation, cross-fostering, and held-out task relabeling must rule out factual/procedural content smuggled through genotype. Social acquisition creates separate content-specific cultural edges. Death by starvation, task hazard, or age hazard removes the carrier and its unreplicated procedures. Extinction and failed resident establishment remain in all relevant summaries.

### Later norm module

After the core freezes, add current approval expectation and a separately learned, decaying habit value. Use the same evidence encoding at every age. Approval is not energy or a fecundity bonus. Run audience removal, free audit, bidirectional evidence equalization, outcome devaluation, and contingency degradation. The first stage supports “learned action persistence,” not a norm claim. Call it internalized obligation only if a separately represented/acquired injunction also passes countermand and cross-context obligation-generalization probes; call it factual dogmatism only when the factual posterior underreacts to accessible likelihood-calibrated evidence relative to the matched benchmark.

## Strong comparison set

| Policy | Role | Required fairness condition |
|---|---|---|
| Asocial access-off | Value of culture only | Same private hardware/budget |
| Ordinary social `(0,0)` | Primary no-extra-deference comparator | Full content, memory, reliability learning, and teaching |
| Scalar `d` | Bridge to earlier model | Same kernel; `d_procedure=d_local` |
| Vector `(d_procedure,d_local)` | Main inherited policy | Override only on conflict |
| Feature-based learned trust | Domain-general learning rival | Same observable features, records, and operation cap |
| Resource-rational metareasoner | Independently derived rival | Same learned model; no hidden state or authority bonus |
| Finite-rollout approximate planner | Computational-economy control | Same tuning worlds, horizon objective, cap, and operation price |
| Exact tiny-world planner | Correctness/value bound | Same observations/utility; complete recursion fits common tiny-world cap |

The exact planner's action class includes following advice. Therefore its expected utility cannot be lower than the restricted override heuristic under the same correct model, observations, and utility: the exact planner can choose the heuristic's action at every history. This is a direct policy-class inclusion consequence. If simulation suggests stable superiority over the exact planner, the implementation, objective matching, or Monte Carlo procedure is wrong.

The full ecological state space cannot support exact optimization over every possible history-dependent policy. Limit the implemented policies to interpretable Markov summaries of beliefs, procedures, source estimates, age/energy, observable context, and costs. This limits the conclusion to the declared policy set. Exact tiny-world agreement plus equally capped rollout and feature-trust controls is the defensible bound; a black-box policy would expand capacity while destroying construct identification.

## Pre-ecology gates

Do not add population selection until all gates pass.

1. **Observed-state firewall:** replay two worlds with identical typed policy-visible histories and random keys but different hidden structure/local truth. Every ordinary policy must produce identical actions and operation counts; serialize every policy input.
2. **Fully social zero:** `(0,0)` must query, update from social content, learn/store procedures, sometimes rationally follow advice, and teach. It must differ from the access-off asocial learner whenever content is informative.
3. **Action-state separation:** force an override without new evidence. `B` and `K` must remain unchanged; only action and physical outcome logs may change.
4. **Endogenous fallible teachers and blank inheritance:** every taught procedure must trace to a logged acquisition/modification. No teacher selection call may inspect true competence. Cross-over worlds must contain tutors worse than, equal to, and better than learners. Pre-exposure newborn inspection, cross-fostering, parent-knowledge permutation, and task relabeling must show content follows culture, not genotype.
5. **Exact tiny-world agreement:** state/action values and visitation frequencies must agree with dynamic programming within prespecified Monte Carlo error. The exact policy must not be systematically outperformed.
6. **Equal hardware/budget:** sensors, memory, motor success conditional on action, innovation probability conditional on experiment, and computation caps are byte-identical across traits; actual operations and costs are logged.
7. **Ledger closure:** births-deaths exactly close population count, and environmental plus individual energy closes after declared regeneration and losses.
8. **No cultural immortality or needle task:** deleting/killing all carriers makes the procedure unreachable when artifacts are off. Primary task ensembles must have a safe option, useful prefixes, at least two positive-net procedures, and nonzero private discovery after no-op pruning.
9. **Neutral selection:** self-mutant mean contrast is zero within Monte Carlo precision; swapped labels satisfy exchange symmetry; neutral lineage outcomes match drift expectations.
10. **Event-order robustness:** an alternative defensible order and proportional resource allocation do not silently reverse the core mechanism; any reversal becomes a stated dependency.

## Decisive scientific tests

### Test 1 — identify extra deference

Run a yoked `content x accept-to-memory x conflict-override` factorial after common message exposure. Hold evidence, message, reliability history, budgets, and outcomes fixed. A claim about behavioral deference uses override-on versus override-off at fixed content and memory acceptance. Assign authority labels before response and report an unconditional intention-to-treat contrast; use a frozen induced-conflict assay for the conflict-conditional mechanism. Asocial comparisons alone can support only the value of cultural access.

**Decisive failure:** `(0,0)` is information-starved, memory-disabled, or otherwise intentionally weak; the switches change anything beyond their declared target; or the only effect is a post-treatment subset of naturally occurring conflicts/teachers/survivors.

### Test 2 — rule out hidden tutor advantage

Cross context access so the learner is better, equal, and worse; separately cross demonstrator age and acquired competence; randomize an explicitly uninformative authority label while holding content/history fixed.

**Decisive failure:** tutors are guaranteed correct, teacher availability depends on evaluator truth, or a label-neutral learner changes under the uninformative label.

### Test 3 — determine whether deference is just bounded planning/trust

Compare the vector policy with exact tiny, equally capped rollout, feature trust, and resource-rational metareasoning. Tune all approximate policies only on discovery worlds and freeze them before holdout. Charge actual operations at the same price.

**Interpretation:** if learned trust or metareasoning matches the vector policy, report domain-general equivalence. A genetic learning-cost difference may remain, but a unique authority faculty has not been shown.

### Test 4 — separate procedure from local delegation

Use a coarse `{0,.5,1}^2` vector grid plus scalar `.25` and `.75` bridge points across depth, verification cost, and context match. Report the full response surface and scalar restriction loss.

**Interpretation:** a best corner such as `(1,0)` is a selective domain policy. It is not a failed search for an interior scalar propensity.

### Test 5 — culture and demography are genuine

Compare transmission+innovation with work-matched no-transmission, transmission-only, innovation-only, and prerequisite-removed controls. Kill all carriers in a library-off probe. Independently verify resource/population ledgers and include extinction.

**Decisive failure:** performance is only more stored statements/confidence, total work differs, knowledge survives without a carrier, or census is held fixed by replacement.

### Test 6 — actual selection

Create the default mutant at an actual resident reproduction event: the resident parent pays the full birth cost, the newborn receives ordinary `E_0` and empty acquired state, and only the policy mutates. Pair it with a paid neutral tagged newborn in the same resident state. Mutants normally learn from residents. Report unconditional descendants, establishment/extinction, endpoint/nearby competitors, multiple acquired cultures, and direct competition.

**Decisive failure:** mutants receive free immigrant energy, a mutant teacher pool, warm-started expertise, or survivor-only growth; a finite newborn-lineage statistic is called an asymptotic/Lyapunov invasion rate; or an isolated abundance maximum is called invasion resistance/ESS.

### Test 7 — learned persistence is not imposed rigidity

Train approval habit only after the epistemic kernel freezes. Apply audience removal, free audit, matched independent evidence in both directions, outcome devaluation, and contingency degradation. Measure factual posterior, action, and habit separately. Add an obligation representation only as a later switch with countermand and cross-context generalization.

**Decisive failure:** adults have lower sensor/update capacity by construction; behavior persistence alone is called dogmatism or normative commitment; or approval directly raises energy/fertility.

## Experiment budget and stopping rule

Use 4 paired discovery seeds only. A tractable mechanism screen is 27 environments (`3 depths x 3 verification-cost levels x 3 context-gap levels`) by 14 unique policies, totaling 1,512 discovery runs. Freeze at most four candidates plus ordinary-social, feature-trust, and approximate-planner controls.

Confirmation uses at least 24 fresh seeds, unseen graph permutations, and adjacent parameter values. Add seeds in fixed batches of eight up to 96 until the 95% Monte Carlo interval is no wider than 0.10 pooled SD for continuous primary contrasts and no wider than 0.10 for extinction probability. If precision remains inadequate, report unresolved. Never expand because a p-value is close to a threshold.

For evolution, choose at most six regimes before invasion outcomes and no more than six directed resident-mutant pairs per regime: at least `6 x 6 x 24 = 864` initial assays. Include independent resident cultures in the seed key. Key environment, observation, task, innovation, demographic, and override streams separately so policy-dependent event counts do not desynchronize all subsequent randomness.

## Independently derived alternative and discriminating prediction

The provenance-aware resource-rational metareasoner chooses another computation only when its estimated value of computation exceeds its time/material cost. Its evidential state counts unique physical trial/innovation roots rather than copied message paths:

$$
\widehat{VOC}(m)=E[\max_a Q^0(a\mid o_m)]-\max_a Q^0(a)-c_m.
$$

It predicts high apparent advice-following when audit/computation is expensive but an immediate decrease under free audit, with no residual effect of an uninformative authority label. An inherited override predicts residual following under matched evidence unless ecological selection has eliminated it. This intervention distinguishes a cost-aware general controller from a specialized conflict response without handicapping either.

## One additional modeler hypothesis

The independent adversarial review already assigns H7 to metareasoning equivalence and H8 to provenance saturation. The modeler's separate addition is **H9 — cultural monoculture debt:** in deep, slowly changing tasks, high `d_procedure` may increase pre-change yield while reducing independent procedure-root diversity, producing slower recovery after a hidden structural flip.

Predeclare the interaction on extinction-inclusive/censored recovery time. At the flip, match census, age, energy, mean competence, and repertoire depth. Rival tests are:

- energy equalization (resource-reserve rival);
- source-estimate reset (calibration-lag rival);
- age matching and a short no-birth window (demographic rival);
- direct competence matching plus diversity-preserving teacher reassignment (pure-quality rival).

H9 is rejected if diversity has no controlled effect after these interventions. It carries no literature-novelty claim.

## Go/no-go recommendation

Proceed with Candidate A only through the exact/kernel gates first. Proceed to ecological histories only after Gates 1-8 pass, to selection only after neutral Gate 9 passes, and to approval/habits only after the core policy comparison is frozen. Stop or redesign if hidden state leaks, `d=0` is not fully social, the ledger fails, the exact planner is beaten, or the result depends on guaranteed teacher truth/pessimistic common evaluation. Endpoint, null, feature-trust-equivalent, resource-rational-equivalent, extinction-prone, and exact-planner-dominant outcomes all satisfy the scientific contract.

## Source boundary

The complete governing design is [`../../V7_RESEARCH_DESIGN_AND_WORK_PROMPT.md`](../../V7_RESEARCH_DESIGN_AND_WORK_PROMPT.md). The selected equations and parameter ranges are fully specified in [`../model_candidates.md`](../model_candidates.md); construct-specific outcome definitions are in [`../constructs_and_estimands.md`](../constructs_and_estimands.md). No external package, empirical calibration, simulation result, or public deployment is recommended here.
