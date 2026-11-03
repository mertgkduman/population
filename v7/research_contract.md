# V7 executable research contract

## Scope and claim boundary

V7 is an offline, bounded individual-based simulation (IBM), not a human-calibrated
model or public service.  It can establish properties of the declared mechanism only.
It must report null, endpoint, conditional, polymorphic, comparator-equivalent,
extinction-prone, and unresolved outcomes without relabeling them as confirmation.
V1--V6 remain untouched comparison artifacts.

## State and truth firewall

`WorldState` alone owns hidden structural bits `theta`, current local condition `z`,
the correct task branch, evaluator labels, source competence, future changes, and
resource pool.  Ordinary policies receive a frozen `PolicyObservation`, containing
only identity/time/age, remaining energy/time/computation budgets, private cue,
summaries of acquired `B` (belief), `K` (procedures), `T` (source estimates), `H`
(learned habits), observable message/provenance/source history, feasible actions,
declared prices, and advice.  Unknown fields and truth-bearing fields are rejected.

`PolicyDecision` records common neutral values `Q0`, the neutral action, advice,
conflict flag, chosen action, operation count, charged costs, and any override key
and draw.  An override without new declared evidence cannot update `B`, `K`, or `T`.
The exact solver may integrate hypotheses over hidden states but never receives a
realized hidden state.  The evaluator may score truth after an event only.

## Construct separation

Every policy first computes the same authority-neutral `Q0` from permitted private
and social evidence.  The fully social ordinary learner is `d=(0,0)`: it queries,
updates `B` and `T`, stores/practises/modifies/teaches acquired `K`, and follows advice
when `Q0` favors it.  It rejects only an *additional* stochastic override on a true
conflict.  The asocial control is a distinct access-off intervention with unchanged
private hardware and budgets; it is not the meaning of `d=0`.

For domain `k in {procedure, local}`, a primary juvenile-only override is

`a = advice` with probability `d_k` only if `age < tau`, `a_Q0 != advice`, and a
logged conflict exists; otherwise `a = a_Q0`.

The fixed main window is `tau=5`.  Learning capacity, memory, sensor accuracy, and
evidence encoding are identical at every age.  A lifelong override is separately
labeled robustness work.  Adult persistence assays set direct override to zero after
training and remove audience/tutor/sanction/promised reward; they test acquired `H`
and optional obligations, never an adult genetic deference effect.

Procedural and local overrides are independent coordinates.  Feature-trust is
ordinary reliability learning, not a hidden deference trait.  Candidate B is a
provenance-aware, finite-operation resource-rational metareasoner with no deference
trait.  Its common input/utility/action contract is shared with all policy classes.

## Acquisition, teaching, and inheritance

Runs begin with 64 naive founders with empty `B/K/T/H`.  Their culture is acquired
under declared costs during a 60-season burn-in; blank, sparse-private, learned,
alternative/wrong, failed, and extinct burn-ins are retained.  Newborns have empty
`B/K/T/H` and inherit policy traits only.  There is no expert reseeding, factual or
procedural inheritance, fixed census, replacement newborn, immortal library, or
truth-conditioned teacher selection.  Teaching is age-neutral and requires a stored
sequence plus two independently logged successful attempts; a mature age alone is
never competence.

## Accounting and randomness

`KeyedRNG(namespace, replicate, graph, season, entity, event_type, ordinal)` keeps
environment, observation, innovation, demography, task-outcome, and override streams
separate. Adding an unused draw cannot change a later shared event.  One immutable
ledger event ID joins learner and teacher time, material/resource transfer, operation
charge, physical outcome, births/deaths, and biological/cultural edges. Transfers
cancel in aggregate; both sides of teaching and every birth cost are explicit.

Each individual-season has 12 indivisible time tokens.  Each decision has at most 128
primitive operations, charged at the same price.  `Q0` has a two-episode horizon with
`delta=.97`. Private trials, queries, teaching, verification, production,
computation, rest, and reproduction consume declared opportunities or resources.

## Bounded execution and reporting

Ecology is fixed at 60 burn-in plus 180 measurement seasons, H9 shocks at measurement
90 (recovery censored at 180), paid-newborn lineage at 80 seasons, direct competition
at 120 seasons, and persistence at 40 training plus 20 seasons per intervention.
Stop-but-retain cap-censored trajectories at population 512, 1,500,000 processed
events, or 120 seconds. The full program uses at most 4 workers, 12 hours, and 12,000
launched trajectories.  Exhaustion yields `UNRESOLVED`, never outcome-responsive
reallocation.  Discovery/holdout, source/config hashes, all extinctions, censoring,
and representative-history selection must be recorded.

Paid-newborn selection compares an actual resident-paid mutant birth with an equally
paid neutral tagged newborn in the same resident state.  It reports finite descendant
counts, zeroes, establishment, and extinction; it never calls finite establishment
asymptotic invasion or ESS.

## Required implementation interface for Slice 1B

`v7.experiments.model` must export `WorldState`, `PolicyObservation`,
`PolicyDecision`, `KeyedRNG`, `LedgerEvent`, `OrdinarySocialPolicy`, `AsocialPolicy`,
`VectorOverridePolicy`, `FeatureTrustPolicy`, `CandidateBPolicy`, and
`validate_policy_observation`.  `Policy.decide(observation, operation_cap, keyed_rng)`
returns a `PolicyDecision`; policy-facing objects cannot expose truth fields.  The
array-oriented IBM may use Numba-compatible numeric arrays internally, but typed
serialization is the only policy boundary.

## Post-execution registration deviations and invalidations (append-only)

This section was appended after execution. It does not rewrite the preregistered
requirements above. “Registered” below describes the intended design; “implemented”
describes source and raw artifacts retained in the repository.

### Frozen-base invalidation: no-teacher local hidden oracle

An adversarial post-execution probe found a correctness failure not caught by the
original truth-firewall tests. When no local teacher exists, the frozen base:

1. retains both `private` and `teacher` feasible actions with equal zero `Q0`;
2. selects `teacher` by the deterministic lexical tie-break despite `advice=None`;
3. constructs the absent tutor signal as exactly the hidden local state `z`.

The asocial arm always uses this no-teacher path on local turns and is therefore
invalid, not merely approximate. No-teacher exposure counts were not exported for
other policies, so frozen discovery, holdout, H9, and finite-lineage policy effects
are retained as reproducible but contaminated artifacts rather than valid evidence.
Frozen source, archive, replay, and raw outputs remain unchanged.

A separately registered corrected overlay makes only three changes: with no teacher,
the tutor placeholder equals the private cue, the only feasible action is `private`
with expected value `.8*3-.2*2=2.0`, and physical execution is forced through that
private cue. It uses fresh seeds and new output paths. This is a correctness repair,
not favorable tuning; teacher-present behavior and all other parameters are fixed.

### Neutral value and exact benchmark

- **Registered:** common `Q0` had a two-episode horizon with `delta=.97`.
- **Implemented frozen IBM:** `Q0` is a current-decision posterior mixture of fully
  enumerated `.90/.50` procedure returns (or the local advice/private payoff). It has
  no future belief recursion or learning continuation.
- **Implemented exact benchmark:** `ExactTinyPOMDP` separately implements the
  two-episode theta/z Bellman problem. Its upper bound applies only to the matched
  restricted tiny policy, never the IBM.

### Learned and resource-rational comparators

- FeatureTrust performs one paid normalized-LMS update from source/context/root
  features and realized payoff. The feature vector omits action; its scalar prediction
  is added only to advice. It is an action-blind reward heuristic, not general RL or
  calibrated action-conditional trust.
- Candidate B computes one-step EVI under the IBM `Q0`. It has no future-learning
  term. A purchased signal spends one actual token, while its procedure opportunity
  proxy is `(D+1)` safe-work tokens. It is approximate and conservatively priced, not
  verified Bayes-optimal or fully resource-rational control. Its query evaluator uses
  source calibration as hypothetical accuracy, but executed query signals use fixed
  `.80` accuracy; this evaluator/execution mismatch is retained as an implementation
  limitation rather than described as calibrated planning.

### Teaching and acquisition

- Teacher eligibility is age-neutral and requires stored `K` plus two independent
  successes, as registered.
- The procedural teacher ranking reads `T[outcome:family]`, but no executed transition
  updates that key. Its default `.5` therefore ties and teacher choice effectively
  resolves by identity among time-available eligible individuals; it is not an
  updated performance ranking.
- The frozen content offer is the lexicographically first eligible family sequence.
  It is not selected from updated learner `B` or expected performance. Adult-belief
  dogmatism and adaptive recovery cannot be inferred from this order rule.
- Births copy genotype only and blank `B/K/T/H`; the fixed override threshold is
  `tau=5`. V7 did not optimize tau and it is not a V1--V6 exponential maturation mean.

### Output estimands and missing precision fields

- Frozen `mean_population` averages `population_next` over the whole simulated
  horizon, including burn-in, rather than only the labeled measurement window.
- `net_energy_per_agent_season` is endpoint resource-plus-living-energy stock change
  divided by summed `population_next` over that same whole horizon.
- Event numerators/denominators needed for the registered Wilson action/revision rate
  criterion were not exported. Rate MCSE is across independent seeds only; Wilson
  precision remains unresolved.
- Candidate-B query/verification purchase counts were not exported. Source inspection
  verifies the decision route and charges, but aggregate results cannot establish how
  frequently either information action was actually purchased.

### Assays not equivalent to the primary IBM

- The corrected 144-row cumulative assay is a separate six-learner cognitive program.
  Its aggregate work is matched, but the ideal pooled upper bound exceeds an
  individual budget and compensates with negative safe work. ACCUM-01 remains partial;
  H2 and demographic cumulative culture are not tested.
- The 120-row persistence assay is a separate generic reinforcement process. Its
  `intervention_seasons=20` field is metadata, not 20 sequential probe updates, and
  the “bidirectional” label uses only one evidence direction. It supports partial
  action-habit persistence with factual revision, not dogmatism or obligation. H4 was
  not modeled.
- Frozen H9 flips theta and optionally erases `K`/success memory at `d=0`. It is not
  carrier death, root-diversity manipulation, d-by-shock mediation, or a functional
  recovery-time assay; the frozen-base local defect further invalidates it.
- The frozen lineage assay runs paired 80-season descendants. No registered
  120-season direct competition ran. Finite numerical precision is not significance,
  equivalence, invasion, fixation, ESS, or stable polymorphism. Corrected lineage
  inference requires fresh overlay-based continuations.

### Corrected fresh executions

The three-method overlay was source-snapshotted at discovery registration, frozen
before holdout, and reused unchanged for fresh seeds. Corrected primary exports are:
discovery 504 rows (seeds 77001--77004), holdout 1,368 rows (78001--78024),
depth-aware control 288 rows (78501--78524), and H9 diagnostic 216 rows
(78601--78624). The freeze selected two additional vector candidates `(.5,0)` and
`(1,0)` while retaining ordinary `(0,0)` as a fixed comparator, plus scalar `.25`.

The corrected finite-lineage source was separately snapshotted before outcomes. It
stopped at seed 79088 after both registered precision thresholds passed, retaining
2,112 fresh arm rows (88 pairs in each of 12 contrasts), with zero no-birth, cap, or
incomplete-batch rows. This precision does not imply significance, equivalence, or an
asymptotic selection result. Fresh H9 still changes only theta and optional K/success
memory at d=0; it does not implement carrier death, root diversity, recovery time, or
d-by-shock mediation.

### Final claim disposition

The post-review canonical extension numbering is: **H7 metareasoning
equivalence**, **H8 provenance saturation**, and **H9 cultural monoculture debt**.
The earlier `literature_map.md` heading “H7 — provenance-compression” is a
pre-review label and is subsumed under canonical H8; it does not create a second H7
in the final ledger.

The frozen implementation/replay and raw arithmetic are reproducible, but software
reproducibility is not scientific validity. Primary frozen ecology claims are
invalidated by the local hidden-oracle defect. The project remains scientifically
PARTIAL even if a corrected overlay reproduces some descriptive patterns, because
authority-label ITT, full memory-by-override identification, feasible cumulative
demography, strong action-conditional comparators, direct competition, carrier loss,
root diversity, obligation, and registered rate precision remain absent.

## Post-verification recovery record

The independent GSD review initially returned `gaps_found`. Its historical report is preserved. Additional source/config-frozen controls were registered before fresh outcomes in `evidence/execution_planner`, `evidence/resource_control`, `evidence/carrier_control`, and `evidence/belief_control`. They use separate seeds and explicitly labeled models; original base/corrected sources, registrations and raw data remain unchanged. Earlier recovery drafts with inadequate state/accounting are preserved, not accepted as final scientific evidence. `experiments/output/corrected_primary_registry.json` classifies those scopes and indexes the current inputs.

The final protocol includes216 planner comparisons,168 resource-control endpoints,24 independent matched-effort pairs,24 total-carrier-loss/restart pairs, and24 seed blocks of actual childhood/adult learning. The experimental naive restart has an audited external population/energy input and is not a natural birth process. No additional trait or preparation benefit was tuned to obtain an interior optimum. Fixed-horizon, extinction, hypothetical model-unit, and independent-seed limitations remain explicit. The final cognitive control compares a static versus switching prior without changing private cognitive accuracy; apparent inertia is not automatically dogmatism.
