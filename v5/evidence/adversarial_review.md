# Adversarial review: information access, retained private evidence, and frozen conviction

**Review role:** causal, mathematical, and numerical adversarial review  
**Date:** 2026-10-30  
**Status:** operationalization, source, numerical, and exported-artifact audit complete within the declared simulation scope  
**Controlling source:** `v5/research_contract.md`

## Provisional verdict

V5 repairs an important weakness in V4: the private-only control now retains what it learned. Separating the private score `u` from the held-and-testified score `b` can distinguish private competence from socially modified conviction. The proposed model can therefore answer a narrow conditional question:

> Under a declared finite-score learning process, how do socially writing adult judgments into held belief, using adult judgment in juvenile action, retaining versus updating adult belief, and paying for private queries change demography and conditional invasion growth?

That question is identifiable only if the following distinctions remain explicit:

1. A single `d` changes both current source choice and which social signs are written into `b`. Its main contrast is therefore **action deference plus social memory acceptance**, not either component alone.
2. Accepted adult signs update `b` even when adult and private judgments agree. Consequently `d` controls confirmation frequency and confidence depth as well as conflict overrides.
3. `u` and `b` are bounded unit-step scores, not calibrated log odds. Their magnitudes are memory-depth proxies.
4. Freezing and confidence-based auditing are imposed adult query policies. Neither is culturally emergent dogmatism.
5. Query-cost savings are mechanically assigned by the architecture. A benefit of freezing under positive query cost is not by itself an informational benefit.
6. Finite-horizon abundance, equilibrium density, low-density growth, shared-culture invasion, and fixation are different outcomes.

The model cannot establish real genetic independence of deference and cognition, an evolutionary history of childhood or dogmatism, a combinatorial-world advantage, or human Bayesian inference. Those are unavailable regardless of numerical results.

## 1. Causal estimands and the `d` conflation

The proposed juvenile mechanism contains two paths from inherited `d` to fitness:

```text
d -> public source choice on disagreement -> current juvenile correctness -> mortality

d -> acceptance of adult signs into b -> retained/testified adult belief
  -> future adult culture -> future juvenile action and belief -> demography
```

The two uses of `d` may be a deliberate syndrome, but a favorable `d` result does not identify pure deference in action or pure social learning in memory. The minimal causal decomposition is:

- **action-only:** `d_action=d`, `d_store=0`;
- **storage-only:** `d_action=0`, `d_store=d`;
- **coupled primary:** `d_action=d_store=d`;
- **private retained:** both zero.

If only the coupled primary is implemented, prose must name it accordingly. The private-only `d=0` control is necessary but does not perform this decomposition.

### Agreement is a separate treatment

The contract explicitly allows accepted testimony to update `b` when private and adult judgments agree. This means an encounter can deepen `|b|` without changing the public action and without resolving a disagreement. With reflecting score caps, repeated agreement can keep `b` at a boundary while `u` remains less extreme. This is a confidence-amplification mechanism.

A targeted ablation should compare:

- acceptance on every social encounter; and
- acceptance only on private–adult sign disagreement.

The first estimates social reinforcement plus override. The second is closer to conflict deference. Neither is intrinsically preferable, but they answer different questions.

## 2. State semantics and accounting requirements

For each genotype, the demographic state should be a nonnegative density over

```text
F_(u,b), A_(u,b),  u,b in {-H,...,+H}.
```

There are two demographic stages and `2(2H+1)^2` cognitive substates. The model must not be described as a two-variable ODE.

The required events are:

| Event | Required state change | Forbidden shortcut |
| --- | --- | --- |
| Birth | adult productivity enters `F_(0,0)` | copying parental `u` or `b` |
| Private cue `s` | `(u,b)->(u+s,b+s)` with reflecting bounds | moving only the score favorable to the hypothesis |
| Accepted adult sign `a` | `(u,b)->(u,b+a)` | altering private evidence `u` |
| Rejected social sign | no cognitive change | hidden private update |
| Maturation | `F_(u,b)->A_(u,b)` | resetting unless explicitly labeled |
| Score-reset ablation | declared reset map | silently treating reset as the private-only control |
| Adult private query | architecture-specific rate; accepted cue moves both scores | updating `b` without the corresponding private record `u` |

At `+H`, a positive step must remain at `+H`, while a negative step must move to `H-1`; symmetrically at `-H`. A numerical integrator must not repair invalid density by clipping negative values. Reflecting score transitions and post-step density clipping are not the same operation.

Summing the derivative over every `u,b` must cancel private, social, audit, and maturation transitions. Only births and deaths may change total density. State-specific maturation must cancel exactly between `F` and `A`.

### The `d=0` invariant

When newborns satisfy `u=b`, private events move both by the same signed step, social acceptance is absent, and reset maps both identically, every occupied `d=0` state must satisfy `u=b`. This is stronger than equality of mean scores. The off-diagonal mass

```text
sum_(u != b) [F_(u,b)+A_(u,b)]
```

must stay zero to numerical precision for every adult architecture. Any violation indicates an unintended social update, asymmetric boundary rule, or inconsistent reset.

## 3. Information access is only partly identified

The private event rate is declared as

```text
lambda_I = nu_I * access / D,
```

and social transmission as

```text
lambda_S = nu_S / D.
```

Within this model, `nu_I`, `access`, and `D` are not three independently identified private-learning mechanisms. Many combinations produce the same `lambda_I`; if query mortality is proportional to actual queries, it also depends on the same product. Likewise, changing `D` rescales both private and social event clocks relative to maturation, mortality, and reproduction. It does not simulate a repertoire of `D` linked tasks.

Therefore:

- call `D` an effective information-load/rate multiplier;
- report the realized private and social rates beside scenario labels;
- do not attribute differences among algebraically equivalent parameterizations to distinct psychology;
- distinguish reduced cue accuracy `p` from reduced cue frequency `lambda_I`;
- distinguish sparse teacher exposure `lambda_S` from poor teacher accuracy;
- do not claim cooperation, division of labor, cumulative repertoire structure, or combinatorial complexity.

A useful exact test is invariance under parameter transformations that preserve both realized rates, for example multiplying `nu_I,nu_S,D` by the same factor while holding `access` fixed. If the implementation has no other direct use of those labels, generators must match exactly.

## 4. Adult architectures are interventions, not discovered psychologies

### Retained and updating

This is the appropriate primary adult control: maturation carries `(u,b)`, and fresh private queries continue to move both. Adult testimony remains `sign(b)`. It represents retained knowledge with continued correction.

### Frozen conviction

Setting the adult private-query rate to zero imposes freezing. It saves every adult query cost by construction and prevents every adult correction by construction. Compare it with retained-updating adults at:

- positive query cost;
- zero query cost;
- correct, neutral, and wrong initial culture;
- stable and reversed environments.

Only the zero-cost contrast isolates accuracy/persistence from the assigned sampling-cost advantage. A frozen-policy advantage with positive cost but not zero cost is a query-economy result, not evidence that epistemic rigidity is adaptive.

### Confidence-based audit

An audit rate that decreases with `|b|` is an imposed confidence-dependent query policy. Because `|b|` can be increased by accepted social agreement and is not calibrated evidence, the policy may convert socially reinforced confidence into less checking. This is a potentially useful feedback mechanism, but its rigidity is partly specified in the audit schedule.

The audit schedule must report:

- exact query rate at each `b`;
- minimum nonzero audit rate, if any;
- whether `u`, disagreement `|u-b|`, or only `|b|` affects auditing;
- treatment at `b=0` and `|b|=H`;
- query cost charged at the same state-specific rate.

Required sensitivities include the audit floor, confidence threshold/slope, and `H`. Otherwise conclusions may be an artifact of which integer score is called “high conviction.”

### Oracle confidence gating

An oracle that reads current true adult reliability has privileged contemporaneous population information. A likelihood proxy derived from bounded `u` is not a calibrated posterior unless the transition history and boundary censoring are accounted for. This comparator may be an information ceiling or diagnostic, but it is not full Bayes and is not information-matched to fixed `d`.

## 5. Public actions, testimony, and accuracy must remain separate

For a juvenile with private sign `s_u` and an adult sign `s_A`, the public rule “adult with probability `d`, otherwise private” has conditional correctness

```text
a = (1-d) P(s_u=theta) + d P(s_A=theta),
```

with a fair private tie at `u=0`. On agreement, both source choices yield the same sign; thus `d` is behaviorally visible only on disagreement even though the formula samples a source on every decision. The implementation should not multiply `d` by disagreement twice.

Track at least four different outputs:

1. private-score accuracy from `sign(u)`;
2. held-belief accuracy from `sign(b)`;
3. adult testimony accuracy from the adult `b` distribution after any transmission error;
4. juvenile public-action accuracy.

An adult can have accurate private evidence and wrong held belief, or the reverse. Reporting only public accuracy would erase the mechanism V5 was designed to expose.

Zero states must be handled consistently. A fair tie contributes `0.5` correctness and random sign testimony/action in the mean-field equations; it is not automatically wrong or correct.

## 6. Query costs and demographic attribution

The query mortality increment should be

```text
c_query * realized_query_rate(state, stage, architecture),
```

not a genotype label or a charge per correct sample. This creates several mechanically distinct paths:

```text
information -> correctness -> juvenile/adult vital rates
query rate  -> direct mortality cost
architecture -> query rate and correction ability
```

Outputs must separate direct query-cost deaths from correctness-linked deaths. Otherwise a frozen-policy abundance advantage cannot be attributed.

The decisive demographic null sets all of the following to zero or state independent:

- juvenile wrong-action mortality;
- adult correctness-dependent mortality;
- adult correctness-dependent fecundity;
- query cost.

With common baseline vital rates, common `tau`, and no direct trait reward, aggregate demographic trajectories must then be identical across `d` even if `(u,b)` distributions differ. If only query cost is disabled, accuracy-linked selection remains and `d` need not be neutral.

Maturation remains a constant hazard `1/tau`, not a fixed birthday. Longer `tau` changes expected exposure to private cues, social cues, baseline juvenile death, wrong-action death, and query cost. Any learning-duration interpretation must acknowledge all five paths.

## 7. Misleading evidence versus environmental reversal

H4 is an exact observational-equivalence test only when formulated in absolute signs.

Consider two scenarios beginning from the same absolute `(u,b)` distribution:

- **misinformation:** truth remains `+1`, but the private channel produces `-1` with probability `p`;
- **reversal:** truth is `-1`, and an accurate private channel produces `-1` with the same probability `p`.

The signed private-cue distribution is identical. If truth-linked juvenile mortality, adult mortality, and adult productivity are disabled, and query cost depends only on query occurrence, then the cognitive generator cannot distinguish the scenarios. Because adult testimony is generated from the same absolute `b` distribution, it is identical too. Full absolute-state trajectories must match; only truth-relative accuracy labels differ.

This equivalence fails legitimately if:

- any correctness-dependent vital rate remains active;
- the two cases use different absolute cue distributions;
- initial adult culture is reoriented to the new truth in only one case;
- an oracle reads the truth or current truth-relative reliability;
- an architecture's query rule explicitly uses truth-relative correctness.

The test should compare full `F_(u,b),A_(u,b)` arrays, total density, query flows, and absolute adult sign frequencies. Comparing only “accuracy” is insufficient because accuracy is defined relative to different truths.

This is an identification result, not evidence that real learners cannot infer environmental change. The model gives them no latent-cause representation, change-point prior, or external truth signal.

## 8. Shared culture and rare-mutant fitness

For resident trait `g_R=(d_R,tau_R)`, first solve the nonlinear demographic-cultural dynamics to a full resident equilibrium or declared stationary history. A rare mutant `g_M` must then:

- hear the resident adult testimony distribution;
- experience resident density/resource limitation;
- retain its own `(u,b)` states, public rule, maturation, mortality, productivity, query cost, and architecture;
- contribute negligibly to resident culture and resources at first order.

The frozen-resident linear operator must include births into mutant `(u,b)=(0,0)`. It must not substitute a mutant-only adult culture. Resident self-invasion must be zero at a resolved joint equilibrium, checked both by `L_R x_R*` and by the dominant eigenvalue. Perturbing the frozen resource or testimony should make the negative control nonzero.

Architecture comparisons should ordinarily be separate environmental treatments, not assumed heritable mutations, unless architecture is explicitly declared a mutant trait. A numerical singular point on a finite grid is not an ESS, fixation probability, or convergence proof.

## 9. Targeted independent numerical verification

The following checks are predeclared before the API is inspected. `experiments/test_verification.py` should rebuild expectations outside the experiment driver wherever possible.

### 9.1 State and bounds

1. Confirm shape `2 x (2H+1) x (2H+1)` per genotype and finite nonnegative initial densities.
2. Verify all births enter juvenile `(0,0)`.
3. Verify state-preserving maturation cell by cell and exact reset routing in each ablation.
4. Verify private events move `u` and `b` together; social events move only `b`.
5. At all four score edges/corners, confirm reflecting transitions conserve mass and a contradictory event moves inward.
6. Confirm the integrator raises on materially negative densities and does not clip them to zero.
7. Confirm all displayed accuracy/probability outputs lie in `[0,1]` and all flows/rates are finite.

### 9.2 Exact algebraic invariants

1. For `d=0`, verify zero mass at every `u!=b` state through time for every adult architecture.
2. With no private and no social events, neutral newborn cognition remains neutral.
3. Independently enumerate private-cue and social-sign branches for small `H` and compare one generator application with the source derivative.
4. Verify the public-action identity from the full state distribution, including `u=0` and adult `b=0` ties.
5. Verify the private cue accuracy parameter and realized private event rate are identical across `d,tau` within a scenario.
6. Verify parameter transformations preserving `nu_I*access/D` and `nu_S/D` produce the same generator when labels have no other role.
7. With zero correctness payoff and zero query cost, aggregate derivatives and trajectories are `d`-neutral at common `tau`.
8. Verify frozen adults have exactly zero adult private-query flow, while retained and audit flows equal their declared rates.

### 9.3 Linear-operator checks

1. Build a frozen-culture/resource generator by applying the derivative to basis states.
2. Check nonnegative off-diagonal entries (Metzler property).
3. Compare `expm(Lt)x0` against direct fixed-environment integration.
4. Check resident equilibrium residual and self spectral abscissa independently.
5. Use a resource/testimony perturbation as a nonzero negative control.

### 9.4 Numerical convergence

1. Compare representative nonlinear RK4 trajectories with DOP853 at tight tolerances.
2. Repeat RK4 at `dt=.1` and `.05`; error should decrease at approximately fourth order away from discontinuities.
3. Check total-flux accounting independently from reported metrics.
4. Repeat important results at multiple `H`; record boundary mass rather than assuming the cap is harmless.
5. For switching environments, align discontinuities or show step refinement stability.

### 9.5 Identification test

Construct the misinformation/reversal pair above with all truth-linked vital rates disabled. Use identical absolute initial states and signed cue laws. Compare complete state trajectories, not only summaries. Exact deterministic mean-field implementations should agree to roundoff. Then activate one truth-linked payoff as a positive control; demographic trajectories may diverge while the difference has a declared cause.

## 10. Decisive ablation matrix

| Comparison | Path removed or changed | Warranted interpretation |
| --- | --- | --- |
| retained private `d=0` | social action and storage | competent individual learner retaining knowledge |
| action-only | adult sign -> `b` | immediate behavioral deference |
| storage-only | adult sign -> public action | cultural-memory effect without current override |
| conflict-only storage | agreement reinforcement | override-driven memory without confidence pumping on agreement |
| frozen vs retained, cost on | adult queries and their cost | combined correction-loss/query-saving effect |
| frozen vs retained, cost off | direct query-cost path | accuracy/persistence effect of adult updating |
| audit floor/slope | imposed confidence-query schedule | sensitivity to assigned checking policy |
| score reset | juvenile `(u,b)` retention | causal value of developmental memory |
| wrong initial culture | favorable history | vulnerability to inherited error |
| true reversal | environmental persistence | cost of stale held belief |
| misleading channel | cue reliability, not truth | protection from temporary private misinformation |
| no payoff + no query cost | all cognitive state -> demography paths | exact demographic neutrality across `d` |
| common resident culture/resource | eco-cultural construction | conditional rare-mutant comparison |

Negative results are informative. In particular, failure of freezing under zero cost, disappearance of copying benefit when teacher exposure is sparse, or equivalence of `d` under no payoff should be preserved rather than tuned away.

## 11. Claim limits

Even if every check passes, warranted conclusions remain conditional:

- Private and held finite scores allow retained individual knowledge to be compared with socially modified conviction in this model.
- Fixed deference can change action and cultural memory while private cue accuracy and access are held invariant by construction.
- Imposed frozen or audit policies trade correction against declared query costs.
- Shared-culture invasion evaluates a mutant in one resident-created environment.

The following claims remain unavailable:

- real genetic separability of deference from cognition or information access;
- historical selection for childhood, obedience, conservatism, or dogmatism;
- a simulated complex or combinatorial environment;
- calibrated Bayesian belief or optimal change-point inference;
- a general advantage of freezing, copying, or long development;
- fixation, global evolutionary stability, or uniqueness from a finite grid;
- elementary novelty for retained knowledge, social learning, conservatism, or reversal costs.

## 12. Implementation audit and measured verification

The API subsequently became available in `v5/experiments/model.py`. I inspected the explicit Numba event kernel and wrote `v5/experiments/test_verification.py`, including a pure-Python reference enumerator that does not call the source transition kernel. Results are persisted in `v5/experiments/verification.json`.

An initial audit found a Numba compilation blocker in the adult-presence conversion (`float(bool)` under the installed Numba 0.64). The implementation replaced the unsupported casts with numeric conditionals before the measured suite ran. No model source was changed by this review.

### Measured results

All 30 independent checks passed after the final default-step and shallow-bound correction.

| Check family | Measured result | Interpretation |
| --- | ---: | --- |
| Independent event enumeration | maximum error `0` | Source derivative matches explicit fixed-policy events for retained-update, audit/conflict-only/override-off, and frozen/accept-off/reset cases |
| `H=1` shallow-score run | error `0` | The default audit threshold is allowed above reachable depth; audit then reduces transparently to full adult updating |
| Reflecting private/social edges | error `1.44e-16` | Confirming boundary events retain mass; contradictory events move inward |
| Neutral births | error `0` | All newborn density enters juvenile `(u,b)=(0,0)` |
| `d=0` support invariant | off-diagonal mass `0` | `u=b` exactly for update, frozen, and audit adult modes |
| No-information null | off-neutral mass `0` | No private/social/adult queries produces no spontaneous cognition |
| Private-information invariance | error `0` | Changing `d` does not change private evidence dynamics |
| Equivalent rate parameterizations | error `3.33e-16` | Scaling `nu_I,nu_S,nu_A,D` together leaves realized dynamics unchanged |
| Zero payoff and zero query cost | demographic difference `5.68e-14` | `d` is demographically neutral while adult held-belief trajectories can differ (`0.0676` maximum contrast) |
| No-adult-source null | error `0` | With adult presence zero, `d` cannot affect action or storage |
| Public/conflict/override algebra | error `0` | State-weighted action accuracy includes ties and applies `d` once |
| Acceptance/override separation | error `0` | Action-only and storage-only flags affect their declared paths independently |
| Total flux accounting | error `2.66e-15` | Cognitive and maturation events conserve density; births minus deaths determine total change |
| Misinformation/reversal equivalence | full-state error `0` | Identical absolute cue laws give identical `(u,b)` trajectories without truth-linked selection |
| Truth-linked positive control | maximum state difference `189.3` | Activating correctness payoffs makes the differently labeled truths causally consequential, so the equivalence test is not a dead path |
| Metzler generators | violation `0` | Frozen-environment linear operators have nonnegative off-diagonal rates |
| Matrix exponential parity | scaled error `6.55e-10` | Basis-built operators agree with direct fixed-environment integration |
| No clipping | both invalid cases rejected | Negative initial density and an unstable large step raise rather than being projected positive |
| Resident self residual/rate | `2.80e-16` / `5.06e-16` | The frozen shared-culture operator is self-neutral at the resolved representative equilibrium |
| Positive shared-culture invader | `+0.01853` | A `d=1,tau=1` mutant grows in the tested `d=.5,tau=3` resident environment; the operator is not trivially nonpositive |
| Resource perturbation control | `+0.00448` | Raising the frozen resource factor by 5% makes resident-self growth nonzero |
| Conditional survival | range valid; zero-mortality error `6.66e-16` | Frozen-environment newborn maturation probability behaves as a probability |

These tests establish internal algebraic and numerical consistency, not biological validity. The reference enumerator independently reconstructs events but necessarily shares the declared model assumptions. The equilibrium and mutant operator also share vital-rate definitions; the resource perturbation and direct time integration reduce, but do not eliminate, circularity.

### Integration-step recommendation

For representative nonlinear update and audit trajectories over 30 model-time units, maximum scaled full-state errors against tight DOP853 were:

| RK4 step | Maximum scaled error |
| ---: | ---: |
| `.2` | `8.69e-4` |
| `.1` | `4.06e-5` |
| `.05` | `2.19e-6` |

The roughly 18--21-fold reductions under halving are consistent with fourth-order convergence. The provisional `.2` step passes a loose `1.2e-3` check and gave much smaller errors in aggregate abundance than in small state cells, but `.1` is the defensible final default for distribution-sensitive, confidence, and shock comparisons. The implementation adopted `.1` as its default after this check. The Numba kernel makes the doubled step count practical.

### Shallow-score audit interpretation

`Config(H=1)` is now accepted even when the default `audit_threshold=2` exceeds the reachable confidence depth. The measured `H=1` audit run is finite and uses the full adult query rate in every state, as implied by `|b|<2`. Thus the audit comparator deliberately collapses to retained-and-updating at this shallow depth; it should not be interpreted as a distinct auditing treatment there.

## 13. Exported-artifact and evolution audit

I independently audited the final exported dashboard payload, 50 NPZ source files, main sweep, supplementary factorials, repertoire outputs, and evolutionary products with `v5/experiments/verify_artifacts.py`. The persisted record is `v5/experiments/artifact_verification.json`. All 30 artifact checks passed.

### Serialization, accounting, and censoring

The main payload contains the declared 13 deference values, 15 maturation values, and 81 times for each of 50 model-scenario contexts. It has 7,950 unique computed trajectories and 9,750 dashboard view cells because the oracle's 15 tau trajectories are duplicated across the 13 inactive `d` views. The following discrepancies were the maxima over all contexts:

| Audit | Maximum discrepancy or range |
| --- | ---: |
| NPZ versus dashboard time series | `5.00e-10` |
| NPZ versus dashboard score distributions | `5.00e-10` |
| dashboard metrics versus sweep CSV | `5.00e-10` |
| stage-distribution sums versus `F,A,N` | `2.73e-12` |
| main last-100-time-unit growth recomputation | `5.00e-10` |
| minimum exported density | `0` |
| conditional maturation survival | `[0.355923, 0.985222]` |

Recovery is explicitly censored: 1,950 transient grid cells recovered within the stored horizon and 7,800 cells are null/`nan`; observed recovery times span 10--80 time units. All nontransient contexts are censored by construction rather than assigned a fictitious zero. The obsolete window-dependent `tail_growth` field is absent from every supplementary CSV/JSON generated with coarser saved points. The main 81-point artifact retains it because both the original and corrected index identify the exact last 100 time units there.

The exported fixed-policy `d=0` states have exactly zero mass at `u!=b`. The oracle is exactly duplicated over its inactive `d` display axis. Every candidate architecture in a main scenario references the same retained, updating `d=.5,tau=3` resident environment; transient truth-reversal and misinformation scenarios correctly have no frozen equilibrium resident.

### Source-rate and mechanism contrasts

Sparse access and high effective load are not generally equivalent treatments. They match the private and adult rates, but load additionally reduces social exposure. Their full final states agree exactly on the no-social `d=0` slice for retained, frozen, audit, and reset architectures. At `d=1`, maximum abundance-trajectory differences between sparse and load are `2655.5`, `2964.9`, and `2707.6` for retained, frozen, and audit, respectively. Reset remains equal to roundoff (`1.82e-12`) because stored juvenile testimony is erased at maturation and does not determine the current public override. Therefore no general "source access = effective load" claim is warranted.

The 2x2 action/storage factorial gives actual contrasts rather than an assumed deference benefit. At `d=1,tau=3`, isolated current-action override raises public accuracy but lowers finite-horizon growth in the noisy (`-1.30e-4`) and sparse (`-4.52e-5`) cases. The corresponding public-accuracy differences are positive (`+0.0503` and `+0.0561`). Isolated storage is positive in those cells (`+6.25e-4` and `+1.03e-3`), with positive interaction terms. These results show ecological and cultural feedback: immediate accuracy improvement is not sufficient to sign the growth contrast. They do not prove that storage or deference is generally beneficial.

All 486 paired `d=1-d=0` source-condition cells have positive `delta_rT` in the chosen grid, but this is a conditional result over the declared `p`, access, cost, architecture, and `tau=3` values. The JSON contrast table recomputes from the 972 source rows to `1e-8`. It is not a causal response surface for independently manipulating cue quality and social exposure.

### Evolutionary products

The architecture invasion table contains 96 comparisons; its self spectral diagonal is neutral to `3.45e-15`. The 648-row retained-architecture pairwise table has a maximum self-diagonal magnitude of `3.37e-9`, resident residual `5.08e-10`, and resident self rate `3.37e-9`. All ten explicit-genotype competition frequency vectors remain nonnegative and sum to one within `3.0e-9`.

The dynamic rare-mutant output contains 216 rows: two environmental histories, twelve common paths, and nine candidates. The mutant operator reads the live resident testimony/resource environment at every RK stage while excluding mutant feedback; mutant masses are normalized only after their log growth increment is accumulated. Resident-self relative growth is zero to `2.42e-17` in the CSV. The serialized `.1` versus `.05` convergence difference is zero at the artifact's nine-decimal precision. This establishes implementation consistency for the recorded finite-window statistic, not an ESS, fixation result, or global convergence claim.

## 14. Exploratory calibrated-Bayes benchmark

The noisy main result raises a narrower alternative explanation: a frozen score can preserve a reliable initial state while the retained unit-step rule overweights weak repeated cues. To test that construction directly, `v5/experiments/bayes_benchmark.py` compares exact calibrated Bayes with the bounded `H=4` unit-step rule in a cost-free, stable, one-task world. Results and definitions are in `v5/experiments/bayes_benchmark.json` and `v5/bayesian_benchmark.md`.

All six exact checks passed. Markov probability normalization error is `3.33e-16`; both rules equal the calibrated prior at `n=0`; Bayes is nondecreasing and never materially below the prior (roundoff at most `2.22e-16`); and the Markov distribution matches independent enumeration of all `2^10` cue paths to `8.88e-16`.

Weak unit-step cues can erode the bounded rule while Bayes cannot have negative expected value of information under these assumptions. The largest tested case begins at calibrated accuracy `.95`, uses cue accuracy `.55`, and after 40 cues has bounded accuracy `.729586` versus Bayes `.950760`. Erosion also occurs for `q0=.85,p=.55` and, more mildly, `q0=.95,p=.65`. Thus a defensible claim is:

> Freezing can outperform misweighted finite-memory updating, but it cannot outperform optimal cost-free calibrated Bayes in expected accuracy in this benchmark.

This does not assert human Bayesian optimality. Conditional cue independence, known reliability, calibrated initial knowledge, and environmental stability are imposed analytical conditions; the demographic-cultural model violates or extends several of them.

## 15. Current disposition

The operationalization removes the reset strawman and explicitly separates private evidence from held/testified belief. Its strongest design risk remains that one `d` simultaneously governs current action and social writing into memory, including agreement reinforcement. Its strongest interpretation risk is treating imposed query suppression as emergent rigidity. Its strongest identification result is the exact misinformation-versus-reversal equivalence control.

The inspected source is internally consistent under 30 targeted equation-level checks and 30 exported-artifact checks. The final factorial outputs support conditional comparisons but not generic benefits: the action-only effect reverses sign in noisy and sparse cases, access and load diverge when social exposure is active, and a calibrated-Bayes benchmark diagnoses finite-memory misweighting as an alternative to any distinct "dogmatism advantage." No historical, empirical, elementary-novelty, global optimality, or evolutionary-stability claim is supported by these verification results.
