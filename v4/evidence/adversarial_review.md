# Adversarial scientific review: developmental deference, endogenous culture, and invasion fitness

**Review role:** causal and mathematical adversarial review  
**Date:** 2026-10-30  
**Scope:** the proposed v4 finite-state model with two demographic stages, inherited juvenile deference `d`, exponential maturation with mean parameter `tau`, endogenous adult testimony, retained cognitive state at maturation, fixed-private-cognition controls, confidence dynamics, post-shock reversal, and conditional rare-mutant growth.

This review starts from the null hypothesis that the intended result is not identified. A simulation can generate a deference--maturation association while failing to show that juvenile deference itself caused it, that confidence persistence emerged rather than being imposed, or that a demographic growth comparison is an evolutionary invasion comparison. The tests below are designed to discriminate those possibilities.

## Provisional verdict

The proposed finite-state design can answer a narrow and useful question:

> Given a particular cultural-memory mechanism, fixed private-signal accuracy, and specified correctness-dependent demography, what are the total demographic and conditional invasion consequences of a juvenile rule that selects adult testimony on private--adult conflicts?

It cannot, by construction, establish that deference is biologically independent of cognition, that the mechanism historically evolved in humans or another species, or that confidence persistence is novel. It also does not isolate *behavioral deference alone* if choosing adult testimony writes the chosen answer into the juvenile's stored confidence state. That version estimates the effect of **deference plus internalization**. An action-only ablation is therefore a necessary identifying control, not an optional sensitivity analysis.

The design is scientifically defensible if all of the following remain explicit:

1. `d` changes only the probability of choosing adult testimony on a genuine conflict; private signal accuracy, evidence capacity, encounter rate, update rate, and payoff mapping do not vary with `d`.
2. Stored cognitive state is carried through maturation by the exact flux `m F_z -> A_z`, while births enter a declared naive state, normally `F_0`.
3. Adult testimony is computed from the resident adult cognitive distribution before the learner's update. It is not an exogenous accuracy parameter in the primary model.
4. Confidence persistence is operationally measured and tested against memory-depth, boundary, and update-rate nulls. It is not described as a genetically assigned adult rigidity trait.
5. A rare mutant hears the shared resident culture and experiences the resident density/resource environment. Low-density `r0` is not called invasion fitness.
6. Static eigenvalue fitness is used only at a joint ecological--cultural equilibrium. Periodic or stochastic environments use a Floquet or Lyapunov calculation with all normalization factors retained.

## Availability and evidence status

At the first review pass, `research_contract.md`, `research-plan-modeling.json`, and the proposed state design were available. The equations, implementation, experiment outputs, and verification artifacts were not yet available. Consequently, the early sections below are **predeclared failure criteria**, not claims that the implementation has passed them.

| Item | First-pass status | What would constitute evidence |
| --- | --- | --- |
| Exact transition equations | Not yet available | A full generator or event table for every stage-by-confidence state |
| State-preserving maturation | Not yet tested | Code/equations and a mass-balance test showing `m F_z` leaves `F_z` and enters the same `A_z` |
| Birth cognitive state | Not yet tested | All state-specific adult births enter the declared juvenile prior state |
| Endogenous testimony timing | Not yet tested | `q_A` is calculated from the pre-update resident adult distribution |
| Dogmatism mechanism | Not yet tested | Boundary audit, `H` sensitivity, `H=1` ablation, common update rules, and post-shock reversal curves |
| Comparator calibration | Not yet tested | Information sets and update timing are written explicitly and no comparator reads current truth accidentally |
| Rare-mutant operator | Not yet tested | Frozen-resident operator plus self-neutral residual and eigenvalue tests |
| Numerical convergence | Not yet tested | Time-step/event-rate, state-capacity, equilibrium, and eigenvalue convergence evidence |
| Novelty | Not assessed here | This review makes no novelty claim; literature equivalences below are cautionary |

## 1. What is the causal estimand?

There are at least three effects that can otherwise be collapsed into one heatmap.

### 1.1 Immediate action effect

On an encounter with a fresh private recommendation `s_I` and an adult recommendation `s_A`, the focal juvenile uses the adult recommendation with probability `d` only when `s_I != s_A`. This changes current correctness and therefore current juvenile mortality if mortality depends on the public action.

This is the cleanest meaning of juvenile deference. Holding private accuracy `p_I`, adult signal, encounter rate, state, and payoff fixed, a matched `d` contrast identifies an immediate behavioral substitution effect.

### 1.2 Internalization effect

If the endorsed answer also moves stored confidence `z` toward that answer, `d` changes what the juvenile later remembers, teaches, and transmits after maturation. The total effect then includes a culturally mediated path:

```text
d -> conflict choice -> stored z -> adult testimony/productivity
  -> future juvenile states -> future adult culture
```

That is a legitimate mechanism, but it is not behavioral deference alone. The chosen action is being reused as a memory-writing event. Unless externally justified, this can become a self-confirmation mechanism: selecting a source causes the learner to store that source as if selection itself supplied new evidence.

The primary report should therefore name the mechanism **deference with internalization** and show an action-only comparison in which `d` changes current behavior but copied testimony does not change stored confidence.

### 1.3 Culture-mediated total effect

When each resident trait is allowed to generate its own equilibrium adult culture, comparing two monomorphic residents estimates a total eco-cultural effect. It does not isolate the direct effect of `d`, because the comparison also changes the mediator `q_A` and the full adult confidence distribution.

At minimum, report both:

- a **frozen-culture controlled contrast**, changing mutant `d` at common resident `q_A` and density; and
- an **equilibrium total contrast**, allowing each resident trait to create its own adult culture and density.

The first is conditional on a common environment. The second includes niche/culture construction. They answer different questions and need not have the same sign.

## 2. Required state accounting

Let the acquired confidence score be `z in {-H, ..., H}`. The demographic state variables are `F_z` and `A_z`; `F = sum_z F_z` and `A = sum_z A_z` remain the only two demographic stages. Cognitive subclasses do not create additional life-history stages, but they do increase the dynamical dimension and should not be described as an exactly two-ODE model.

A minimal continuous-time form is

```text
dF/dt = births into F_0 + juvenile cognitive transitions
        - maturation - juvenile deaths

dA/dt = state-preserving maturation + adult cognitive transitions
        - adult deaths.
```

More explicitly, with cognitive generators `Q_F` and `Q_A`, maturation hazard `m = 1/tau`, and state-specific mortality/productivity,

```text
dot F_z = 1[z=0] * sum_y b_y(N, culture) A_y
          + (Q_F F)_z - (m + mu_F,z) F_z

dot A_z = m F_z + (Q_A A)_z - mu_A,z A_z.
```

The orientation of `Q` must be documented; its transition contribution must sum to zero. Summing over `z` must give

```text
dot N = sum_y b_y A_y - sum_z mu_F,z F_z - sum_z mu_A,z A_z.
```

Maturation must cancel exactly. The following are blockers:

- maturation sends `F_z` to `A_0` or to a re-estimated adult state;
- births enter the parent's adult `z`, silently adding direct vertical cultural inheritance;
- cognitive transition rows/columns fail to conserve mass;
- the same transition is counted once as a confidence update and again as a demographic flow;
- `tau` is treated as a fixed birthday in interpretation while implemented as a constant hazard.

### Age-hazard interpretation

With `m=1/tau`, `tau` is the mean maturation waiting time in the absence of death, not a fixed developmental duration. If a juvenile's total mortality hazard is `mu_F`, survival to maturation is not one; in the constant-hazard special case it is `m/(m+mu_F)`, and the time to stage exit is `1/(m+mu_F)`. Correctness-dependent mortality makes the surviving maturants a selected subset of confidence histories.

Consequently:

- longer `tau` changes both expected learning opportunities and exposure to prereproductive death;
- the cognitive distribution of adults is survivor-biased even when all genotypes share identical private cognition;
- an adult-state accuracy improvement with `tau` is not automatically a pure learning effect; it can partly be selective disappearance of wrong juveniles.

A decisive decomposition records the confidence distribution (i) among all juveniles before mortality weighting, (ii) among maturation fluxes `mF_z`, and (iii) among standing adults.

## 3. Adult testimony and cultural inheritance

For true environmental sign `theta in {-1,+1}`, a natural adult testimony accuracy is

```text
q_A(t) = sum_z A_z(t) P(testimony is theta | z) / sum_z A_z(t).
```

The `z=0` rule must be explicit. Random testimony at `z=0` contributes accuracy `1/2`; deterministic sign conventions at zero can generate a hidden initial bias.

### Timing requirement

At a juvenile encounter, testimony must be sampled from the **pre-encounter** resident adult distribution. Recomputing `q_A` after updating the learner and using that value in the same event is an algebraic self-loop. In a deterministic ODE, all transition rates should be functions of the current state, not of the state after the transition they generate.

### One draw versus duplicated evidence

A single adult draw from a large, well-mixed resident adult distribution is fully summarized for that binary decision by its current marginal accuracy, provided the fresh private signal is conditionally independent of teacher identity given the environment. Cultural genealogy then matters through the endogenous value and dynamics of `q_A`, not through a second likelihood factor in the same decision.

Double counting appears if the model or a comparator:

- treats repeated testimonies from the same culturally descended population as independent likelihood increments without modelling their dependence;
- estimates `q_A` using the current realized truth/outcome and then uses that estimate as if it were prior knowledge in the same decision;
- counts agreement between private and adult signals as two independent evidence units when the update rule only has one endorsed-action increment; or
- counts the chosen action once as evidence and its observed payoff again without declaring two distinct observations.

### Cultural rather than genetic inheritance

The intended causal path is:

```text
adult distribution -> testimony -> juvenile acquired z
-> state-preserving maturation -> future adult distribution.
```

The genotype transmits `d` and `tau`; it should not transmit parental `z`. Newborns entering `F_0` are socially exposed to adults after birth. This separation must remain visible in equations, code, exports, and prose.

## 4. Does dogmatism emerge, or is it encoded?

The proposed acquired state is a bounded signed confidence score. It should not be called literal Bayesian evidence unless step sizes equal the appropriate source-specific log-likelihood ratios. A private source with fixed `p_I=.65` and an adult source with varying endogenous `q_A(t)` do not generally justify equal `+1/-1` likelihood increments.

### Acceptable interpretation

`z` can be interpreted as a coarse, bounded confidence or endorsement tally. All individuals use the same update rule; adults continue to receive fresh private information; no genotype carries an adult learning-rate, stubbornness, absorbing-confidence, or rigidity parameter. Persistence then arises from accumulated distance from the sign boundary.

### Unacceptable construction

The model has assigned dogmatism rather than generated it if any of the following is true:

- adults stop updating solely because they are adults;
- extreme confidence states are absorbing under contradictory evidence;
- high-`d` genotypes receive smaller contradictory update steps or a lower adult learning rate;
- `H` changes with genotype;
- a separate heritable stubbornness parameter is introduced;
- post-shock reversal is slow only because the solver clips at a boundary incorrectly.

### Boundary audit

For each boundary state, a contradictory update must move inward. A confirming update can remain at the cap, but the code must not prevent subsequent contradictory evidence from reducing confidence. Unit tests should enumerate every transition at `-H`, `0`, and `+H` under both environmental signs.

### Operational outcomes

Avoid inferring dogmatism from mean accuracy alone. Report at least:

- wrong-sign mass after a shock;
- high-confidence wrong-sign mass, with threshold declared before analysis;
- mean signed confidence relative to the current environment, `E[theta z]/H`;
- the number or expected time of contradictory private updates required to cross zero;
- adult testimony accuracy `q_A(t)`;
- public action accuracy separately from stored belief accuracy.

The cautious term is **confidence-induced cultural persistence**. “Dogmatism” is reasonable only as a defined model phenotype, not as a psychological or species-level claim.

### Decisive memory ablations

1. **`H=1`:** preserves a sign/neutral memory but removes deep confidence accumulation. Immediate deference remains possible. A large loss of post-shock lag shows that persistence was carried by confidence depth.
2. **Action-only / public-only:** `d` changes the current action but adult testimony is not written into `z`. This isolates immediate mortality from future culture.
3. **Maturation reset:** send `mF_z` to `A_0`. This intentionally breaks retained knowledge and should collapse the intergenerational memory channel.
4. **Adult-update off:** adults retain maturation state but receive no fresh private updates. The difference from the primary model measures recovery by within-adult revision versus cohort replacement.
5. **Capacity sweep:** repeat at several `H` values. If the claimed qualitative effect changes sign or reversal time scales almost linearly with the arbitrary cap, report that dependence rather than a generic dogmatism result.

## 5. Comparator audit

All comparators must receive the same private signal, adult testimony, payoff opportunities, and encounter clock. A comparator with access to current source accuracy or unchosen outcomes is an oracle benchmark, not an equally informed cognitive alternative.

### 5.1 Private-only comparator

This is the clean null: choose the fresh private signal on every conflict. It should be equivalent to `d=0` for current public actions. If it is not, some other mechanism differs.

### 5.2 “Calibrated Bayes” source chooser

For symmetric binary sources, prior `1/2`, conditional independence, and known accuracies `p_I` and `q_A`, a conflict is resolved by the source with the larger likelihood ratio. With both sources positively informative, that reduces to choosing the more accurate source. These assumptions must be stated.

Serious limitations:

- If the comparator reads the contemporaneous true `q_A(t)` calculated using `theta`, it has oracle knowledge unavailable to a learner.
- Immediately after an environmental sign flip, culture can have `q_A<1/2`. A fully calibrated observer would treat it as anti-informative and invert it; merely choosing private is not the general Bayes rule.
- Instant access to post-shock `q_A(t)` leaks the new environmental truth and can make reversal look artificially immediate.
- With a non-neutral prior or correlated sources, “choose the more accurate source” is not the full posterior rule.

The safe label is **oracle-calibrated one-decision source choice**. If the dashboard uses “Bayes,” it should include the assumptions beside the metric. A more behaviorally comparable alternative freezes calibration at its pre-shock estimate and updates it only from subsequently observed outcomes.

### 5.3 RL trust comparator

An EWMA trust learner is not defined until its observation protocol is specified:

- Does it see whether adult advice was correct even when the advice was not followed (full-information feedback)?
- Or does it update only after choosing the adult source (bandit feedback), which makes learning endogenous to its own choices?
- Is trust individual and reset for newborns, or a population/global value inherited across cohorts?
- Is the EWMA driven by realized Bernoulli correctness or by the deterministic expected `q_A(t)`?
- Are learning rate, initial trust, and softmax temperature fixed across all genotypes and scenarios?

A deterministic EWMA of the true expected `q_A` is another oracle approximation. A softmax temperature and EWMA learning rate also control persistence; they may be fixed common comparator settings, but persistence produced by them is not evidence that dogmatism emerged in the focal finite-state model.

If the `d` axis is inactive for Bayes and RL, plots must say so. Sweeping and displaying `d` for those comparators would create visually duplicated cells, not an evolutionary response of `d`.

## 6. Demography, density, and selection are not interchangeable

Three outcomes should remain separate:

1. **Low-density demographic growth:** growth of a monomorphic population near zero density under a declared initial or equilibrium culture.
2. **Resident equilibrium abundance/culture:** the joint fixed point of density and all stage-by-confidence states.
3. **Rare-mutant invasion growth:** the mutant's initial asymptotic growth in the resident's equilibrium density and resident adult culture.

The earlier two-stage low-density eigenvalue is not an invasion fitness once teacher quality and adult productivity are endogenous. A trait can have high low-density growth but fail to invade a resident that constructs a different resource and cultural environment.

### Frozen-resident mutant operator

For resident equilibrium `x_r*`, define

```text
N_r*     = total resident density
q_A,r*   = resident adult testimony distribution/accuracy
L_m      = L(d_m, tau_m | N_r*, q_A,r*, theta).
```

`L_m` acts on the mutant's own `F_z,A_z` vector. The mutant:

- shares resident resource/density limitation;
- samples resident adult testimony while rare;
- retains its own cognitive state at maturation;
- has its own state-specific survival and adult productivity;
- produces mutant-genotype newborns in `F_0`;
- does not alter resident `q_A` or `N` at first order.

Freezing resident culture is correct in the invasion linearization: the mutant's `O(epsilon)` effect on a shared teaching distribution changes its own `O(epsilon)` dynamics only at `O(epsilon^2)`. It would be wrong to let a rare mutant hear only mutant adults or to recalculate culture from the mutant vector.

### Adult productivity cannot be averaged away

If stored adult sign changes productivity, `L_m` must contain state-specific birth rates and route all births into the declared juvenile prior state. Passing only the mutant's average correctness into a two-state matrix discards the cognitive-state mechanism.

This also means the model contains an **endogenous developmental preparation benefit**: longer juvenile duration can alter adult state and hence adult productivity, even though no direct `tau` bonus is prescribed. The honest claim is “no exogenous tau reward,” not “no benefit of delayed maturation.”

### Resident-against-itself neutrality

At a joint resident equilibrium, the exact frozen-environment operator used for mutants should satisfy

```text
L_r x_r* = 0.
```

If `L_r` is irreducible Metzler and `x_r*` is strictly positive, Perron--Frobenius theory implies that its dominant real eigenvalue is zero. This yields two distinct numerical checks:

1. the normalized residual `||L_r x_r*|| / ||x_r*||` is small; and
2. the spectral abscissa `max Re(eig(L_r))` is close to zero.

The residual alone is insufficient if the operator is reducible or equilibrium states are exactly zero: a positive eigenvalue can coexist with a zero eigenvector on another block. The transition graph should therefore be checked for irreducibility under primary parameter values, or boundary/reducible cases should be reported separately.

A failed self-neutrality check usually indicates one of four mismatches: resident culture was not at equilibrium, mutant and resident rates differ in code, births enter a different cognitive state, or the operator uses a rounded/independently recomputed density or testimony value.

### Multiple cultural attractors

An endogenous cultural system can be bistable or history dependent. Convergence from one initial condition does not establish a unique resident equilibrium. Invasion fitness should be labelled conditional on the resident attractor and initialization. A minimal check starts the same genotype from correct, wrong, and neutral adult cultures.

## 7. Post-shock reversal

An environmental sign flip is a strong diagnostic because it separates information retention from adaptability. The pre-shock resident should first reach a declared equilibrium or stationary regime; otherwise post-shock lag partly reflects unfinished initialization.

Report separate time series for:

- current public action accuracy;
- juvenile stored-sign accuracy;
- maturation-flux accuracy;
- adult testimony accuracy;
- high-confidence wrong adult mass;
- population density and births/deaths.

Predeclare reversal outcomes such as time to cross chance (`q_A=0.5`), time to recover half of the lost accuracy, and accuracy debt (integrated deficit after the shock). If a threshold is never crossed in the horizon, treat it as right-censored rather than setting it to the horizon.

### Directional-information null

With private accuracy `p_I=0.5` and no other truth-linked innovation channel, the model has no directional information about the new environment. Replicate-average accuracy should not systematically recover above chance. A sign crossing can still occur through symmetric drift or deterministic tie conventions; that is not adaptive reversal.

### Expected diagnostic patterns, not required favorable results

- Raising `H` should usually increase potential memory depth and slow reversal, but clipping can make scaling nonlinear.
- Faster adult private-update rates should speed within-cohort reversal.
- Maturation reset should remove inherited adult knowledge and greatly weaken intergenerational persistence.
- Action-only deference can retain an immediate mortality effect while removing the culture-mediated future effect.
- `d=0` supplies the private-learning recovery baseline.
- Adult-update-off isolates recovery by cohort replacement.

Failure to observe these patterns is not automatically a software bug, but each failure requires explanation from the transition structure.

## 8. Periodic and stochastic invasion calculations

A static dominant eigenvalue is valid only for a time-homogeneous resident environment. After a shock, during a cultural transient, or under a periodic/stochastic environment, `L(t)` varies.

For a periodic resident path of period `T`, compute the monodromy matrix or integrate a fundamental solution over one period. The fitness is the Floquet exponent

```text
lambda_F = log(rho(Phi(T))) / T.
```

For a stochastic resident history, propagate the positive mutant vector along the same resident `N(t),q_A(t),theta(t)` path and accumulate log scale factors. Renormalizing the vector is numerically appropriate only if every removed scale factor is retained in the long-run log-growth estimate.

The resident-self control must use the same path, time discretization, event ordering, and normalization. Over an arbitrary post-shock transient it need not have instantaneous eigenvalue zero. A zero long-run resident-self exponent is expected only for a stationary or periodic resident regime with bounded population dynamics.

## 9. Decisive null and ablation matrix

| Null or ablation | Causal path removed | Decisive expected implication |
| --- | --- | --- |
| `d=0` / private only | adult choice on conflicts | Immediate behavior equals private comparator; culture can still improve through private learning |
| `p_I=0.5` | directional private information | No systematic post-shock adaptive recovery above chance without another innovation channel |
| No correctness payoff | cognition -> survival/productivity | Trait-selection differences vanish, though cultural distributions may still differ |
| Fixed exogenous adult testimony | juvenile culture -> future teachers | Isolates contemporaneous response from endogenous feedback |
| Action-only/public-only | chosen testimony -> stored `z` | Isolates immediate deference from internalization and future teaching |
| Reset `z` at maturation | juvenile memory -> adult teacher | Removes retained developmental knowledge |
| Adult private update off | adult experience -> revised culture | Recovery occurs only through new cohorts/maturation |
| `H=1` | deep confidence accumulation | Preserves immediate decisions with minimal persistence memory |
| Several larger `H` | arbitrary cap dependence | Shows whether reversal/dogmatism conclusions depend on the chosen memory capacity |
| Freeze common culture and density | resident niche/culture construction | Gives controlled conditional mutant contrast across `d,tau` |
| Multiple resident initial cultures | assumed unique attractor | Reveals bistability/history-dependent invasion values |
| Encounter-rate rescaling | arbitrary number of learning events per time | Shows whether effects are tied to event-clock calibration |
| Time-step/tolerance refinement | discretization | Key signs, equilibrium residuals, and exponents should be stable |

The no-correctness-payoff null must remove all routes from correctness to both juvenile survival and adult productivity. Turning off only juvenile error mortality while leaving state-dependent adult births is not a neutral-fitness null.

## 10. Literature equivalence and novelty cautions

This is not the primary literature review; it records only equivalences that materially constrain interpretation.

### Ghirlanda, Enquist, and Nakamaru (2006)

[Ghirlanda, Enquist, and Nakamaru, “Cultural Evolution Develops Its Own Rules: The Rise of Conservatism and Persuasion,” *Current Anthropology* 47, 1027--1034, DOI 10.1086/508696](https://doi.org/10.1086/508696) modeled openness to copying and persuasion as cultural traits that alter their own transmission. Their dynamics favor types that are less influenced by others and more able to influence others under the stated copying process.

The proposed v4 mechanism is not identical: `d` is an inherited juvenile trait, while the acquired confidence state is what persists culturally; correctness and demography provide explicit payoffs. Nevertheless, “cultural dynamics can generate conservatism/persistence without a genetically specified adult-rigidity trait” is not a novel conceptual conclusion. The distinction must be the particular confidence, demography, maturation, and invasion construction, if it proves useful—not the generic emergence of conservatism.

### Acerbi, Enquist, and Ghirlanda (2009)

[Acerbi, Enquist, and Ghirlanda, “Cultural evolution and individual development of openness and conservatism,” *PNAS* 106, 18931--18935, DOI 10.1073/pnas.0908889106](https://doi.org/10.1073/pnas.0908889106) explicitly modeled development from initially open/ineffective individuals toward effective cultural models and often toward conservatism. Openness and effectiveness were themselves culturally transmitted, and larger repertoires or slower acquisition could maintain openness.

The v4 retention mechanism—juveniles acquire state, mature without a reset, and become models for later juveniles—is qualitatively close to that developmental-cultural logic. The v4 difference is a binary truth-linked confidence task, inherited conflict deference, continuing private adult updates, explicit demography, and rare-mutant analysis. It should be described as a mechanistic comparison or extension in a different formal setting, not as the first demonstration that age-linked conservatism can arise culturally.

### Simon (1990)

[Simon, “A Mechanism for Social Selection and Successful Altruism,” *Science* 250, 1665--1668, DOI 10.1126/science.2270480](https://doi.org/10.1126/science.2270480) used docility/bounded rationality as a tendency to accept socially transmitted knowledge and advice, with adaptive information benefits potentially carrying socially prescribed costly behavior.

The v4 model instantiates only a restricted informational-benefit component: adult testimony can improve a binary factual action and thereby lower mortality or raise productivity. It has no bundled altruistic prescription, norm package, group benefit, or altruism cost. Therefore it cannot test Simon's proposed explanation for successful altruism. At most it formalizes a narrow premise that receptivity to advice can have a direct individual fitness benefit under bounded private information.

### Acerbi and Parisi (2006)

[Acerbi and Parisi, “Cultural Transmission Between and Within Generations,” *JASSS* 9(1):9](https://www.jasss.org/9/1/9.html) studied intergenerational retention and abrupt environmental change, finding that inherited culture can preserve useful behavior but slow replacement after a reversal, while other transmission routes can introduce adaptive variation.

Thus the basic retention-versus-postshock-adaptation tradeoff also has clear precedent. V4 can offer a different finite-state, demographic, and evolutionary decomposition; it should not claim the reversal phenomenon itself as new.

## 11. Claim boundaries

Even if every numerical check passes, the strongest warranted conclusions are conditional:

- In this model, at fixed private-signal accuracy and specified common learning rules, inherited juvenile conflict deference changes demographic outcomes through immediate action and, when enabled, acquired cultural memory.
- The sign and magnitude depend on adult culture, memory capacity, encounter timing, maturation hazard, correctness payoffs, and environmental regime.
- Conditional mutant growth is evaluated in a shared resident culture and density; it is not fixation probability or proof of an ESS.
- Confidence-induced persistence can arise without a separate adult-rigidity genotype under the specified update process.

The following claims are unavailable:

- that deference and cognition are genetically separable in real organisms;
- that long juvenile dependence evolved for teaching or obedience;
- that humans, a named population, or another species follows these equations;
- that the model identifies a historical cause;
- that “Bayes” or “RL” describes real learners rather than a formal comparator;
- that a single resident optimum is globally evolutionarily stable;
- that emergent conservatism, cultural retention, or post-shock lag is novel.

## 12. Implementation-facing test checklist

These are the concrete checks to run when code and outputs are available.

### Algebra and generator

- Enumerate every state and transition for small `H`, including `z=-H,0,+H`.
- Verify nonnegative off-diagonal generator entries and zero cognitive-transition column/row sums under the documented convention.
- For random positive states, compare `sum(dot F + dot A)` to births minus deaths.
- Verify maturation cancellation state by state.
- Verify all births enter the declared newborn state.
- Verify `d` never changes private accuracy, encounter rate, `H`, adult update rate, or payoff coefficients.

### Culture

- Recompute `q_A` independently from adult state counts and the zero-state rule.
- Confirm juvenile transitions use resident pre-update `q_A`.
- Confirm rare mutants never recompute testimony from mutant adults.
- Confirm adult confidence continues to update in the primary model.

### Comparators

- At `d=0`, public action probabilities equal private-only exactly.
- Under the narrow symmetric independent case, enumerate all four signal pairs and compare the oracle source chooser with the analytic posterior decision.
- Test `q_A<0.5` explicitly; document whether advice is inverted, ignored, or treated by a restricted rule.
- Record the RL information set, initialization, feedback mode, learning rate, and temperature.
- Confirm the displayed `d` control is disabled or explicitly irrelevant for comparators that do not use it.

### Equilibria and invasion

- Converge the full resident state, not only `N`.
- Start from correct, neutral, and wrong cultures to test attractor uniqueness.
- Build the resident-self operator from the exact equilibrium values used by the mutant operator.
- Check `||L_r x_r*||/||x_r*||` and the dominant eigenvalue independently.
- Check the operator's transition graph/irreducibility for primary cases.
- Compare analytic eigenvalues with direct low-density mutant integration.
- For periodic cases, compare monodromy estimates at two time steps.
- For stochastic cases, accumulate every renormalization factor and run independent resident-history replicates.

### Post-shock and ablations

- Pre-equilibrate before flipping the environment.
- Run the full null/ablation table above.
- Treat unreached reversal thresholds as censored.
- Repeat at multiple `H`, encounter rates, solver tolerances, and horizons.
- Preserve negative, flat, boundary, and non-reversal findings.

## 13. Disconfirmation targets

Before accepting a favorable narrative, actively try to show each of the following:

1. The apparent benefit of `d` is only the immediate mortality mapping; adult culture adds nothing after the action-only ablation.
2. The apparent emergence of dogmatism is almost entirely the selected `H` cap or an absorbing-boundary bug.
3. Bayes/RL outperform because they read contemporaneous truth-linked `q_A`, not because their update logic is better.
4. The reported evolutionary optimum is a low-density demographic optimum that fails in the resident culture/density.
5. The self-neutral invasion test passes only because the same code constructs both expected and observed values circularly; an independently reconstructed operator should also pass.
6. A post-shock “recovery” at `p_I=.5` is actually a zero-state tie convention or finite-population drift.
7. Longer `tau` appears to improve cognition only because wrong juveniles die before maturation.
8. The result changes across alternative resident cultural attractors.

These failures are scientifically informative. The v4 study is strongest if it exposes exactly which mechanism survives them rather than optimizing parameters to preserve a preferred deference narrative.

## 14. Implementation audit and measured verification

The implementation and model documents subsequently became available. I inspected `experiments/model.py`, `experiments/run_experiments.py`, `experiments/evolution.py`, `experiments/selection_refinement.py`, `experiments/age_robustness.py`, `experiments/volatility.py`, `mathematical_model.md`, `model_comparison.md`, and the generated outputs. I also wrote and ran `experiments/test_verification.py`; its full results are in `experiments/verification.json`.

### State and causal wiring

The implemented primary source satisfies the central state-accounting contract:

- `F_(z,r)` and `A_(z,r)` are finite density states inside juvenile and adult demographic stages.
- Births from every adult state enter neutral juvenile score/trust.
- Primary maturation transfers `F_(z,r)` to the identical `A_(z,r)` at hazard `1/tau`; the reset ablation reroutes the flux to neutral adult state.
- The adult recommendation is the abundance-weighted sign accuracy of the current adult distribution, with `z=0` contributing one half and symmetric transmission error applied afterward.
- Adults continue to receive fresh private updates with common fixed accuracy and common nonheritable rate.
- Adult mortality and productivity are score-specific; juvenile mortality depends on current public-action accuracy.
- A frozen-resident mutant operator retains the complete mutant stage-by-score state and state-specific adult productivity.

The primary causal caveat also remains real in code. For fixed, private, and oracle policies, `internalize=True` reduces the full juvenile update to a score step whose correctness probability equals public-action correctness. Thus the learner's source choice writes the selected answer into future memory. The fixed model is a deference--internalization package; `internalize=False` is the action-only comparison.

The RL comparator is an individual finite trust counter, not an EWMA of expected population accuracy. It enumerates realized private/adult correctness branches, resets trust at birth, and uses full-information feedback about adult correctness even when the adult source was not selected. This removes the feared deterministic-`q_A` RL leak, but it remains an informationally advantaged full-feedback comparator.

### Independent verification results

All 23 checks in `experiments/verification.json` passed.

| Check family | Measured result | Interpretation |
| --- | ---: | --- |
| Reflecting score/trust boundaries | exact, error `0` | Contradictory updates move inward; caps are not absorbing |
| Learning plus maturation mass conservation | `2.22e-16` | Cognitive and transfer flows conserve density |
| Pure maturation closed form | max absolute error `9.78e-8` | `m=1/tau` transfer matches the analytic exponential solution |
| State-preserving maturation and reset control | exact, error `0` | Primary carry and reset ablation route flux as declared |
| Neutral-state births | exact, error `0` | No direct parental score inheritance |
| Total flux identity | error `2.66e-15` | Summed derivative equals independently reconstructed births minus deaths |
| Equal-accuracy `q=p` full-generator null | exact, error `0` | In the fixed mean-field model, the entire frozen generator is `d`-invariant at equal source accuracy |
| Fixed conflict-choice identity | error below `2e-15` | Public accuracy equals `p+d(q-p)` |
| Oracle anti-information rule | error below `2e-15` | It inverts `q=.2` advice when effective accuracy is `.8`, but ignores `q=.4` advice when effective accuracy is below private `.65` |
| RL realized-feedback routing | error below `2e-12` | Certain correct/wrong adult outcomes move trust up/down; `feedback=0` prevents trust movement |
| No-payoff demographic `d` null | max difference `2.84e-13` | Culture can differ, but aggregate demography is `d`-neutral when every correctness payoff is disabled |
| Metzler and irreducible primary operators | no violations | Positive-rate primary generators support the Perron self-neutrality argument |
| Matrix-exponential parity | scaled error `3.10e-10` | Basis-built operator agrees with fixed-environment time integration |
| RK4 `dt=.1` versus DOP853 | scaled error `1.40e-5` | Within the declared `2e-5` tolerance |
| RK4 `dt=.05` versus DOP853 | scaled error `7.92e-7` | Step halving reduces error by about a factor of 18 |
| Three resident-self residuals | max `8.18e-14` | Frozen resident operators annihilate their equilibrium vectors |
| Three resident-self spectral abscissae | max magnitude `3.01e-13` | Self-invasion is numerically neutral |
| Perturbed-resource negative controls | rates `0.00294` to `0.00483` | Self-neutrality is not an operator that returns zero for every environment |
| All-zero state and invalid inputs | exact/rejected | Zero is absorbing and NaN/Inf/nonintegral-`H` inputs fail early |

These are strong internal-consistency and numerical tests. They are not an independent empirical oracle: the matrix operator and the time derivative share the same model source, and the self-neutral equilibrium and invasion operator share the same vital-rate definitions. The independently reconstructed flux identity, analytic maturation solution, exact nulls, perturbed-environment controls, and DOP853 comparison reduce circularity but cannot validate the biological assumptions.

The separate one-dimensional pairwise invasibility tables also have near-zero diagonal entries: maximum absolute self rates were approximately `1.41e-15` for the `d` axis and `4.91e-12` for the `tau` axis. Common-resident dynamic invasion used 11 periodic/stochastic histories; resident-self relative rates stayed within about `4.3e-18` of zero. Periodic `dt=.1` versus `.05` relative-rate discrepancy was `8.17e-12`.

## 15. What the outputs do and do not show

### Immediate benefit versus cultural amplification

At `tau=3` in the stable fixed-policy runs, raising `d` from `0` to `1` changed final density from about `4186.8` to `5825.6` and adult stored-belief accuracy from `0.7847` to `0.8638`. This is not a pure behavioral-deference result.

The public-only ablation, which preserves action choice but prevents adult testimony from being written into score, changed density only from about `4186.8` to `4619.2`; adult belief accuracy remained much flatter (`0.7847` to `0.7878`). The reset-at-maturation ablation reduced density to roughly `3354.9`--`3439.5` and made final adult belief essentially independent of `d` (`0.697798` across the three tested `d` values). Therefore a large portion of the primary stable benefit is specifically carried by internalization and retained juvenile memory. The narrow conclusion is selection on a deference--internalization--retention package.

The no-payoff ablation was decisive: at common `tau=3`, all three `d` values produced the same density (`1210.9587` to numerical precision) even though adult cultural accuracy and high-depth mass differed. The model does not contain an undisclosed direct demographic reward for `d`.

### Shock cost and confidence persistence

Immediately after the sign flip, the minimum adult accuracy at `tau=3` fell progressively with primary-model `d`: approximately `0.2155`, `0.1813`, and `0.1365` for `d=0,.5,1`. Thus the same cultural feedback that improves stable-environment accuracy makes the inherited culture initially more wrong after reversal.

The memory-depth and Erlang-age sensitivity outputs support a retention--reversal trade-off, but they also show parameter dependence. For exponential maturation (`L=1`) at `tau=8`, raising `d` from `0` to `1` raised peak high-confidence wrong-adult mass from about `0.297` to `0.551` and post-shock accuracy debt from `3.39` to `10.16`. With four Erlang juvenile phases of the same mean maturation time, the corresponding peak wrong-high-confidence mass was about `0.410` to `0.784` and debt `3.76` to `19.99`. The qualitative effect survives the age-hazard sensitivity, while its magnitude does not.

The Erlang extension is a robustness model with serial juvenile transit substates. It preserves the conceptual juvenile/adult distinction but is mathematically no longer the same one-compartment memoryless juvenile process. It should be reported as a limited age-distribution sensitivity, not as proof that the result is invariant to general age structure.

### Environmental switching rate changes the deference contrast

The original stochastic runs used only one telegraph mean interval. The targeted volatility sensitivity adds mean intervals `20,50,100,200`, six fresh histories per interval (seeds `4000`--`4005`), and the same fixed-policy configuration (`p=.65`, `H=6`, `T=600`, `dt=.1`). Within each of the 24 histories, all nine combinations of `d in {0,.5,1}` and `tau in {1,3,8}` experience the identical environmental path. Reinitializing the same seed at each interval couples the rate conditions through common standardized exponential draws. `experiments/volatility.csv` stores the paired results and `experiments/volatility.json` stores the summaries and realized path variability.

The across-history mean paired finite-horizon growth contrasts, `r_600(d=1)-r_600(d=0)`, were:

| Telegraph mean interval | `tau=1` | `tau=3` | `tau=8` |
| ---: | ---: | ---: | ---: |
| 20 | `-4.78e-5` | `-1.72e-4` | `-7.08e-4` |
| 50 | `+2.63e-5` | `+8.34e-5` | `+5.65e-5` |
| 100 | `+1.48e-4` | `+4.98e-4` | `+1.004e-3` |
| 200 | `+1.50e-4` | `+5.01e-4` | `+1.018e-3` |

At interval 20 the contrast was positive in only `2/6`, `1/6`, and `1/6` histories for `tau=1,3,8`; at interval 50 it was mixed (`4/6`, `3/6`, `3/6`); at intervals 100 and 200 it was positive in all six histories at every tested `tau`. Across-history standard deviations at interval 20 were `8.52e-5`, `2.53e-4`, and `6.23e-4`; at interval 50 they rose to `1.39e-4`, `4.85e-4`, and `1.19e-3`. Thus the sign near the intermediate scale is history-dependent, particularly for long juvenile residence.

The environmental replicates themselves were variable. Mean realized switch counts over 600 time units were `26.8`, `10.5`, `5.17`, and `2.67` as the intended interval increased, with respective ranges `23--35`, `7--17`, `2--10`, and `1--5`. The fraction of time in the `+1` state ranged from `0.404--0.610`, `0.412--0.654`, `0.352--0.678`, and `0.084--0.931`. Paired paths remove this environmental imbalance from the within-history `d` contrast, but six histories do not precisely characterize its sampling distribution. Every history starts at `+1` with initial adults biased toward the corresponding correct sign; the slow-switch finite-horizon results therefore also retain an initialization/phase effect and are not stationary-regime averages.

These results support the limited prediction that sufficiently rapid environmental reversal can erode or reverse the finite-horizon advantage of high fixed deference, with stronger costs at longer `tau`. They do not prove monotonicity, identify a selected switching threshold, or establish a general stochastic-environment result. `r_600` is monomorphic population growth from a common initial state, not rare-mutant invasion fitness.

### Density and selection rankings diverge

The stable finite-horizon monomorphic `r_T` surface had its best coarse fixed-policy cell at `d=1`, `tau≈3.487`; refinement put the corresponding finite-horizon maximum at `tau≈3.192`. This is population change over `T=400` from a common initial state under density regulation; its final 100-time-unit log growth was already near zero (`3.17e-8` at the coarse best cell) because the population was approaching equilibrium.

The evolutionary analysis gave a different maturation result. A coarse mutation--selection competition concentrated at `d=1,tau=.5`, but a nearby `d=1,tau=.55` mutant had positive invasion growth, refuting local uninvadability of that coarse boundary cell. The follow-up frozen-resident gradient calculation located a candidate at `d=1,tau≈0.74655`; its finite-difference gradient was about `-1.10e-9`, changed from positive to negative across the candidate, and none of 1,281 tested joint mutants had positive growth (largest tested rate about `-7.49e-7`, with the exact resident self point treated separately).

This is useful evidence of the density/selection distinction requested by the research contract. It is still a **finite-grid numerical singular candidate at a boundary in `d`**, not an analytic ESS proof, fixation result, or global convergence theorem.

An additional out-of-sample contrast makes the ranking reversal concrete. The refined monomorphic finite-horizon resident `d=1,tau≈3.192` had higher equilibrium abundance than the short-development monoculture `d=1,tau≈0.7466` (`5828.0` versus `5476.2`), yet the short-development mutant invaded the long-development resident at rate `0.0010006`. The same qualitative mismatch remained under `p=.6`, `p=.75`, `H=3`, and `H=9`, with positive invasion rates from about `0.000988` to `0.002053`. Thus neither higher equilibrium abundance nor the monomorphic finite-horizon maximum identifies the invasion-selected maturation value in this model.

### Shared-culture invasion is implemented correctly at first order

Equilibrium mutant generators freeze the resident resource factor and resident adult advice while retaining mutant cognitive states and mutant state-specific births. The nonstationary calculation propagates all mutant traits against the same live resident density/culture/environment path, renormalizes mutant probes while accumulating log scale factors, and subtracts resident log growth over the same post-burn interval. The near-zero resident-self controls and step-halving result support this implementation.

The reported dynamic values are finite long-window common-path exponents after burn-in. The periodic calculation numerically approximates the periodic growth exponent; it does not explicitly construct a monodromy matrix. The stochastic calculation estimates pathwise growth over the finite declared histories, not an infinite-time almost-sure theorem.

### No tested bistability in the default cases

The `wrong_history` and ordinary initializations converged to the same stored resident equilibria for the tested fixed, public-only, memoryless, private, oracle, and RL policies. This is evidence against initialization dependence in those default cases, not a general uniqueness proof over the full parameter domain.

## 16. Remaining warnings and unavailable claims

### Core recovery metrics now use matched baselines; the age-hazard sensitivity does not

Core postprocessing now records three distinct quantities: chance-crossing time, five-sample half-recovery toward each cell's matched stable adult accuracy, and adaptation debt relative to the matched stable trajectory. It preserves the former `0.75` crossing under the explicit name `recovery_absolute75`. This resolves the primary dashboard/sweep comparability problem.

The separate age-hazard robustness script still defines both recovery and accuracy debt relative to the absolute threshold `0.75`. Stable equilibria differ across `d`, `tau`, and hazard model. For example, the `L=1,d=0,tau=1` stable adult accuracy is about `0.7465`, so its shock recovery is censored even when it returns to its own equilibrium. Its `recovery_time` and `postshock_accuracy_debt` fields therefore remain arbitrary-threshold summaries, not matched recovery measures. The wrong-high-confidence peak remains directly comparable as defined.

### The combined no-directional-information control passes

Setting private accuracy to chance alone does not remove all directional information when correct adult scores still receive lower mortality and higher productivity. Accordingly, the `p=.5,payoff=True` ablation is not the decisive null. The added combined control uses `p=.5,payoff=False`; final adult accuracies for `d=0,.5,1` were respectively `0.5`, `0.499999999999796`, and `0.499993498882614`. Thus no tested deference value generated sustained above-chance information once both private innovation and truth-linked demographic selection were removed. The tiny low deviation at `d=1` is numerical/transient, not evidence of directional learning.

### High-depth mass is not dogmatism

The source field named `dogmatism` is `Pr(|z|>3)` among adults, regardless of whether the sign is correct. The dashboard appropriately relabels it “high-depth adults,” and postprocessing now derives high-confidence *wrong* mass separately. Any prose that calls the raw field dogmatism without this definition would overreach.

### Tail-window growth is not asymptotic growth

The main experiment's field `long_run_growth` is actually

```text
log[N(T)/N(T-100)] / 100.
```

It is a final-window diagnostic. It is not a stationary eigenvalue, a Floquet exponent, or a Lyapunov exponent, especially in shock and periodic contexts. The separate `dynamic_invasion.csv` calculation is the appropriate common-path evolutionary rate. Both the dashboard template and regenerated `index.html` now label the metric “Last-100-time-unit log growth,” describe it as finite-window and non-asymptotic, and distinguish it from invasion. The internal field name remains legacy nomenclature only.

### Comparators have different information sets

The oracle reads exact contemporaneous adult accuracy and can invert anti-informative culture. RL instead learns a five-level trust state from objective full-information feedback. Fixed `d` has neither capability. These are useful ceiling/flexibility comparisons, but performance rankings cannot be attributed only to “Bayes versus RL versus deference”; information access differs by design.

### Source dependence remains absent

Adult testimony is one redraw from an anonymous mean-field pool. The learner has no teacher identity, genealogy, repeated-adviser relation, or representation of culturally correlated evidence. The model can recycle culture through the population state, but it cannot show that learners discount double-counted testimony or solve an information cascade.

### Historical and empirical claims remain unavailable

No parameter is fitted to a species, no genetic covariance architecture is modeled, and no historical data are used. The computation cannot establish actual genetic independence of deference and private cognition, historical selection for childhood, a psychology of obedience, or any real-world magnitude. The model's `d` and `tau` inheritance assumptions are experimental controls.

## 17. Final adversarial assessment

**Technical assessment:** the implemented finite-state demographic/cultural mechanism is internally consistent under the tests run. State-preserving maturation, neutral births, endogenous resident testimony, score-specific adult performance, density regulation, rare-mutant linearization, and numerical integration all have direct passing evidence.

**Causal assessment:** the main stable-environment advantage is not attributable to behavioral deference alone. It is substantially amplified by writing selected adult answers into juvenile memory and carrying that state into adulthood. The public-only and reset controls expose this cleanly. This should be a headline qualification, not a footnote.

**Evolutionary assessment:** the study successfully demonstrates why monomorphic finite-horizon performance, equilibrium abundance, mutation--selection competition, and frozen-resident invasion must be separated. The refined `d=1,tau≈.7466` point is a numerical local candidate only.

**Novelty assessment:** no elementary novelty claim is supportable. The defensible contribution, if desired, is an incremental architecture and decomposition: a finite acquired confidence state carried across maturation, generated adult culture, explicit correctness-dependent demography, and shared-culture invasion analysis. Ghirlanda et al. (2006), Acerbi et al. (2009), Simon (1990), and Acerbi and Parisi (2006) preclude broader claims about first demonstrating culturally emergent conservatism, docility benefits, or retention--reversal trade-offs.

**Disposition:** suitable as a critically qualified computational feasibility result. The primary recovery metric, dashboard tail-window label, and combined no-directional-information null have been corrected or added. The absolute-`0.75` recovery/debt fields in the age-hazard sensitivity remain an explicitly limited auxiliary summary. The study is not evidence for a historical adaptation or a general theory of dogmatism.

---

**Current status:** implementation and outputs reviewed; independent verification passed 23/23 checks. The principal requested corrections are present in the regenerated artifacts, including the private-source metric distinction. Remaining caveats concern interpretation and scope, especially the unmatched absolute-threshold recovery fields in the separate age-hazard analysis and the limited six-history volatility sample. No novelty claim is made.
