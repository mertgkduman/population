# Exact mathematical model implemented in `experiments/model.py`

**Code state documented:** 2026-10-30  
**Implementation status:** equations transcribed from source before the broad experiment run; numerical and adversarial pass/fail results belong in later verification artifacts  
**Model scope:** hypothetical binary-task model with two demographic stages and finite acquired cognitive/cultural substates

## 1. State variables and inherited traits

The environmental state is

```text
theta(t) in {-1,+1}.
```

For each inherited trait pair

```text
g=(d,tau),     0<=d<=1,     tau>0,
```

the model tracks juvenile/follower density `F_(z,r)` and adult density `A_(z,r)`.

- `d` is used only by policy `fixed` and is the probability of following adult advice on a private/adult conflict.
- `tau` is the mean waiting time to maturation in the absence of death; maturation hazard is `m=1/tau`.
- `z in {-H,...,+H}` is a bounded signed confidence/endorsement score.
- For the RL policy only, `r in {-2,-1,0,+1,+2}` is learned trust in the adult source. Other policies have one dummy trust state.

Thus there are exactly two demographic stages per inherited trait and `2(2H+1)` cultural substates for fixed/private/oracle policies or `10(2H+1)` joint score–trust substates for RL. These are not extra demographic ages.

The score yields two distinct readouts:

```text
stored belief:       B(z)=sign(z), with a random sign at z=0
confidence depth:    C(z)=|z|, reported unnormalized in the code.
```

`z` is not literal Bayesian evidence: all score steps have size one even though private and adult reliabilities generally differ.

## 2. Implemented default parameters

| Code field | Symbol | Default | Meaning |
|---|---:|---:|---|
| `H` | `H` | 6 | score bound |
| `p` | `p` | 0.65 | fixed fresh private accuracy |
| `juvenile_rate` | `nu_F` | 1.0 | juvenile encounter/update rate |
| `adult_rate` | `nu_A` | 0.3 | adult private-update rate |
| `transmission_error` | `eta` | 0.05 | probability adult recommendation flips in transmission |
| `mu_F` | `mu_F0` | 0.03 | baseline juvenile mortality |
| `mu_A` | `mu_A0` | 0.10 | baseline adult mortality |
| `error_death` | `k_F` | 0.25 | juvenile error-mortality increment |
| `adult_error_death` | `k_A` | 0.10 | adult wrong-belief mortality increment |
| `beta_base` | `beta_0` | 0.35 | adult baseline productivity |
| `beta_skill` | `beta_1` | 0.85 | productivity increment for correct stored belief |
| `K` | `K` | 1000 | density scale in resource supply |
| `S0` | `S_0` | 1.0 | maximum resource supply |
| `KS` | `K_S` | 1.0 | resource half-saturation constant |
| `feedback` | `f` | 1.0 | probability RL observes objective adult-source correctness |
| `trust_temperature` | `lambda_r` | 1.5 | slope of RL adult-follow gate |
| `internalize` | — | true | store endorsed action rather than private recommendation |
| `reset_maturation` | — | false | whether maturation erases score and trust |
| `payoff` | — | true | activate all correctness-dependent vital rates |
| `initial_adult_correct` | `q_init` | 0.8 | fraction initially placed on correct adult score |
| `policy` | — | `fixed` | one of fixed/private/oracle/rl |
| `dt` | `Delta t` | 0.1 | RK4 maximum step |
| `T` | `T` | 400 | default trajectory horizon |

Validation enforces probabilities in range, `eta<=0.5`, positive scales, nonnegative rates, valid policy, `tau>0`, and `d in [0,1]`.

## 3. Initial condition

Every run starts with 80 juveniles at neutral score and neutral trust:

```text
F_(0,0)(0)=80.
```

There are 20 adults. Let `k=min(2,H)`. For initial `theta=+1`,

```text
A_(+k,0)(0)=20 q_init
A_(-k,0)(0)=20(1-q_init).
```

All other states start at zero. Runs whose initial environment is `theta=-1` must interpret or construct the initial condition carefully; the helper `initial()` itself always places the `q_init` share at positive `z`.

## 4. Stored-belief correctness and adult advice

For current environment `theta`, define

```text
chi_theta(z) = [1+theta sign(z)]/2.
```

It equals one for a correct sign, zero for a wrong sign, and one-half at `z=0`.

For total adult density `A=sum_(z,r) A_(z,r)`, pre-transmission adult accuracy is

```text
q_A = sum_(z,r) chi_theta(z) A_(z,r) / A,
```

with `q_A=1/2` if `A=0`. After independent symmetric transmission error,

```text
q = eta+(1-2 eta) q_A.
```

The implementation calls this returned quantity `q`; documents and plots may call it `q_adv`. It is computed from the current, pre-update adult distribution at every ODE evaluation. Adult confidence does not change sampling or transmission: every adult sign contributes according to abundance, regardless of `|z|`.

The model is mean-field. A new adult recommendation is independently redrawn from the aggregate distribution at every juvenile encounter. Teacher identity, teacher genealogy, network structure, and repeated contact are not tracked.

## 5. Density/resource feedback

For total density

```text
N=sum_(z,r)[F_(z,r)+A_(z,r)],
```

resource supply and the realized productivity multiplier are

```text
S(N) = S_0/(1+N/K)
R(N) = S(N)/(K_S+S(N)).
```

`R(N)` is always nonnegative. With defaults it equals `1/(2+N/K)`.

## 6. Juvenile policies and public accuracy

Every juvenile encounter contains a fresh private recommendation of accuracy `p`. Let `w_r` be the probability of using the adult source when the private and effective adult recommendations conflict.

### Fixed deference

```text
w_r=d
q_eff=q.
```

### Private-only

```text
w_r=0
q_eff=q.
```

Adult advice is generated but ignored.

### Oracle-calibrated one-decision selector

```text
q_eff=max(q,1-q)
w_r=1{q_eff>p}.
```

If `q<1/2` and `1-q>p`, the oracle inverts adult advice. If `q_eff=p`, it uses the private source. This policy reads contemporaneous aggregate `q`; it is an oracle benchmark, not a sequential Bayesian learner.

### Finite RL trust

```text
w_r = logistic(lambda_r r) = 1/[1+exp(-lambda_r r)]
q_eff=q,
r in {-2,-1,0,+1,+2}.
```

`d` is ignored by private, oracle, and RL policies.

For every policy and trust state, marginal public-action accuracy is

```text
a_r = p+w_r(q_eff-p).
```

For fixed deference this follows exactly from resolving only disagreements:

```text
P(U=theta)=p+d(q-p).
```

The source-pair enumeration in RL additionally assumes conditional independence of fresh private and adult correctness given `theta`.

## 7. Bounded score transitions

Define capped movement

```text
clip_H(z+s)=min(H,max(-H,z+s)),     s in {-1,+1}.
```

A confirming step at a cap remains at the cap; a contradictory step always moves inward. Therefore boundary states are not absorbing.

### Fixed, private, and oracle policies

If `internalize=True`, the public/endorsed action is stored and its probability of being correct is `ell_r=a_r`. If `internalize=False`, the fresh private recommendation is stored and `ell_r=p`, although public action and juvenile mortality still use `a_r`.

The raw score increment is correct-sign with probability `ell_r`. Equivalently,

```text
P(delta z=+1) = ell_r       if theta=+1
                 1-ell_r    if theta=-1,
```

and `P(delta z=-1)` is the complement. Encounters occur at rate `nu_F`.

For these policies there is only one trust state, so the juvenile cognitive generator is a clipped nearest-neighbor birth–death chain.

### RL joint score–trust transitions

At an RL encounter, let

```text
i in {0,1}: private recommendation wrong/correct
s in {0,1}: adult recommendation wrong/correct
h in {0,1}: private/adult source selected on conflict
y in {0,1}: objective adult-source feedback absent/present.
```

The implementation enumerates independent Bernoulli correctness:

```text
P(i,s)=p^i(1-p)^(1-i) q^s(1-q)^(1-s).
```

Conditional source selection has probabilities

```text
P(h=1|r)=w_r,
P(h=0|r)=1-w_r.
```

The stored correctness indicator is

```text
c_store = s if internalize=True and h=1
          i otherwise.
```

The signed score step is

```text
delta z = theta(2 c_store-1).
```

Objective feedback occurs with probability `f`. When present, trust moves toward the observed adult correctness:

```text
delta r = 2s-1       if y=1
          0          if y=0,
```

with caps at `-2,+2`. Feedback is full-information: the learner can update adult trust even when it chose the private source. Trust is updated from the realized Bernoulli correctness of adult advice, not directly from expected `q`.

The transition rate for each enumerated event is

```text
nu_F P(i,s) P(h|r) P(y).
```

## 8. Adult private updating

Adults receive a fresh private recommendation at rate `nu_A`, with the same fixed accuracy `p` as juveniles. It moves `z` one capped step toward the recommendation. Trust `r` is unchanged. Adults therefore retain the score and trust acquired as juveniles but continue to revise the score throughout adulthood.

## 9. Vital rates

When `payoff=True`, juvenile mortality depends on current public-action accuracy:

```text
mu_F,r = mu_F0+k_F(1-a_r).
```

Adult mortality and productivity depend on stored-belief correctness:

```text
mu_A,z = mu_A0+k_A[1-chi_theta(z)]
beta_z = beta_0+beta_1 chi_theta(z).
```

Thus `z=0` receives half of the skill benefit and half of the adult error-mortality increment.

When `payoff=False`, all three correctness effects are removed simultaneously:

```text
mu_F,r=mu_F0,
mu_A,z=mu_A0,
beta_z=beta_0.
```

There is no direct reward or penalty for `d`, no direct fecundity function of `tau`, and no heritable score capacity, learning rate, adult update rate, or trust rule.

## 10. Birth and maturation

Total birth influx is

```text
Birth = R(N) sum_(z,r) beta_z A_(z,r).
```

All newborns enter neutral score and neutral trust:

```text
Birth -> F_(0,0).
```

There is no direct parent-to-offspring score transmission. Culture is transmitted obliquely through later sampling of the adult pool.

With `reset_maturation=False`, the exact maturation flux is state preserving:

```text
F_(z,r) --1/tau--> A_(z,r).
```

With `reset_maturation=True`, all maturation flux is intentionally rerouted to `A_(0,0)`. This is a memory-breaking ablation, not the primary mechanism.

## 11. ODE system

Let `Q_F` denote the juvenile score or joint score–trust generator and `Q_A` the adult score generator. They are oriented so their transition contributions conserve total density. For the primary state-preserving model,

```text
dot F = e_(0,0) Birth + Q_F F - (tau^-1 I+D_F)F
dot A = tau^-1 F       + Q_A A - D_A A.
```

Here `D_F=diag(mu_F,r)` repeated across score states and `D_A=diag(mu_A,z)` repeated across trust states. Componentwise,

```text
dot F_(z,r) = 1{z=0,r=0} Birth
              +(Q_F F)_(z,r)
              -(tau^-1+mu_F,r)F_(z,r)

dot A_(z,r) = tau^-1 F_(z,r)
              +(Q_A A)_(z,r)
              -mu_A,z A_(z,r).
```

Summing all states cancels cognitive transitions and maturation:

```text
dot N = Birth-sum_(z,r)mu_F,r F_(z,r)-sum_(z,r)mu_A,z A_(z,r).
```

An optional mutation matrix can redistribute total births among an outer batch of inherited trait types. It is not part of the resident or rare-mutant definition below.

## 12. Analytical nulls and benchmarks

### Fixed-policy equal-accuracy null

Because

```text
a(d,q)=p+d(q-p),
```

`q=p` makes juvenile mortality independent of `d`. In the implemented mean-field internalization model, the score generator also depends on `d` only through `a`, so the **entire fixed-policy generator is independent of `d` at `q=p`**.

This stronger null is specific to the marginal-accuracy/independent-redraw construction. It need not survive repeated named teachers, correlated source histories, source-specific step sizes, or a memory state that records source identity.

### Learning-only `H=1` stationary distribution

For fixed correct-step probability `a` and environment `theta=+1`, set `rho=a/(1-a)`. The stationary clipped walk over `z=-1,0,+1` is proportional to

```text
(1,rho,rho^2).
```

Stored-belief accuracy is `(rho^2+rho/2)/(1+rho+rho^2)`.

### Collapsed demographic matrix

If cultural states have identical vital rates and productivity is constant `beta`, the two-stage matrix is

```text
M = [-(tau^-1+mu_F), beta]
    [ tau^-1,       -mu_A]
```

with dominant eigenvalue

```text
r_+ = -[tau^-1+mu_F+mu_A]/2
      +0.5 sqrt([tau^-1+mu_F-mu_A]^2+4 beta/tau).
```

## 13. Resident equilibrium and rare-mutant operator

For a resident `g_R`, first solve the nonlinear ODE until the full state, not merely total density, reaches an ecological–cultural equilibrium `x_R*`. Extract

```text
q_R=q_adv(x_R*,theta),
R_R=R(N_R*).
```

For mutant `g_M`, freeze `(q_R,R_R,theta)` and construct a column-oriented linear operator by applying the exact right-hand side to basis states:

```text
dot x_M = L_M(g_M | q_R,R_R,theta) x_M.
```

The operator retains all mutant score/trust states, state-specific adult productivity, state-specific mortality, maturation, births into the mutant neutral juvenile state, and mutant policy rules. The mutant samples resident advice and experiences resident resources. Its own rare adults do not alter the shared adult pool at first order.

Equilibrium invasion fitness is the spectral abscissa

```text
s(g_M;g_R)=max Re eig[L_M(g_M|q_R,R_R,theta)].
```

### Exact next-generation and Euler–Lotka benchmark

The frozen-resident mutant operator also has a useful analytical decomposition. Put every non-birth juvenile transition into

```text
J = Q_F-diag(mu_F+m),      m=1/tau_M,
```

every non-birth adult transition into

```text
C = Q_A-diag(mu_A),
```

the maturation map into `M` (`M=mI` when score and trust are retained, or the appropriate reset map in the reset-maturation ablation), and state-specific adult birth output into the row vector `b^T`. Births enter the neutral juvenile state `e_0`, so

```text
L_M = [ J       e_0 b^T ]
      [ M          C    ].
```

When `-J` and `-C` are transient nonsingular M-matrices, the expected lifetime offspring production of one neutral mutant newborn is

```text
R_0 = b^T(-C)^(-1) M(-J)^(-1)e_0.
```

The corresponding Euler–Lotka function is

```text
R(r)=b^T(rI-C)^(-1) M(rI-J)^(-1)e_0.
```

Its real root `R(r)=1` equals the dominant eigenvalue of `L_M`; in the irreducible case, `s>0`, `s=0`, and `s<0` correspond respectively to `R_0>1`, `R_0=1`, and `R_0<1`. This is an exact benchmark for the frozen-resident linearization, not an approximation that collapses cultural states. Numerical tests should compare the root, the full operator eigenvalue, and the sign of `R_0-1`.

This decomposition also makes the ecological–cultural externality explicit. A mutant's `tau_M` changes its juvenile residence and maturation map while the adult testimony distribution and resource factor remain those produced by the resident. A shorter-`tau` mutant can therefore invade culture supported by a longer-`tau` resident even when the shorter-`tau` genotype has lower equilibrium abundance in monoculture and there is no direct reward assigned to `tau`. Lower equilibrium abundance does **not** imply a lower intrinsic or low-density growth rate: in the reported benchmark, the short-`tau` type has the higher low-density rate. The demonstrated mismatch is equilibrium abundance versus invasion fitness in the resident-created environment, not a claim of a novel general mechanism or proof of an ESS.

Required resident-self checks are both

```text
||L_R x_R*||/||x_R*|| approximately 0
max Re eig(L_R) approximately 0.
```

The transition graph must also be irreducible under primary positive-rate parameters, or reducible cases must be reported. Alternative resident histories are tested using initially mostly correct and mostly wrong adult cultures; invasion values remain conditional on the resident attractor. A broader initialization search would be required to exclude additional attractors.

The helper `equilibrium()` currently integrates in 800-time-unit blocks, up to six blocks total, until a maximum-component residual divided by total density is below `1e-9`, then reports resident `q`, resource factor, dominant mutant-operator eigenvalue, and residual. These settings require verification rather than being assumed sufficient.

## 14. Time-changing environments

`run()` accepts a common function `theta_fn(t)`. A fixed-step classical RK4 integrator evaluates `theta` at the step midpoint, so shock timing should align with or be refined relative to `dt`.

For a changing resident environment, static eigenvalues are not invasion fitness. The intended calculation is:

1. simulate and save the resident path `theta(t),q_R(t),R_R(t)`;
2. propagate each mutant linearly along that same path;
3. for a periodic path, use the dominant Floquet exponent of the one-period fundamental matrix;
4. for a stochastic common path, accumulate the pathwise top Lyapunov exponent with all numerical normalization factors retained;
5. compare with a resident clone probe propagated on the same path.

## 15. Reported metrics in the current code

| Key | Exact computation | Interpretation constraint |
|---|---|---|
| `F,A,N` | total stage and population densities | demographic abundance |
| `B` | total density-regulated births | flow, not stock |
| `DF,DA,D` | total juvenile/adult/all deaths | flows |
| `M` | `F/tau` | total maturation flow |
| `per_capita` | `(B-D)/N` | instantaneous demographic rate |
| `belief_F` | score-sign correctness among juveniles | stored belief, not public action |
| `belief_A` | score-sign correctness among adults | pre-transmission adult belief accuracy |
| `advice` | `q` after transmission error | testimony accuracy reaching juveniles |
| `public_F` | public action accuracy | weighted across trust states |
| `confidence` | adult mean `|z|` | unnormalized depth, range `[0,H]` |
| `dogmatism` | adult fraction with `|z|>3` | persistence-capacity proxy only |
| `override` | probability mass of conflicts on which adult is selected | assumes conditional source independence |
| `private_sampling` | `nu_F` | every juvenile encounter samples a fresh private signal; this is an event rate, not source choice |
| `private_choice_on_conflict` | `1-E_F(w_r)` | conditional propensity to select the private recommendation when the two recommendations conflict |
| `rT` | `log[N(T)/N(0)]/T` | full stored-horizon population growth, not invasion |
| `long_run_growth` | `log[N(T)/N(T-100)]/100` | last-100-time-unit diagnostic; not asymptotic, stationary, Floquet, or Lyapunov growth |
| `wrong_high_confidence` | adult mass with incorrect score sign and `|z|>3`, divided by adult mass | time series; dashboard landscape is its final value |
| `peak_wrong_confidence` | maximum of `wrong_high_confidence` over stored times | distinguishes confidently wrong persistence from high depth alone |
| `recovery` | first post-shock time beginning five stored points (20 time units) all above `0.5+0.5(q_A,stable(T)-0.5)` | model-specific half-recovery relative to its matched stable endpoint |
| `recovery_absolute75` | same sustained rule with threshold `0.75` | legacy fixed-threshold sensitivity metric only |
| `chance_recovery` | same sustained rule with threshold `0.5` | chance-crossing time after shock |
| `adaptation_debt` | trapezoidal integral of `max(0,q_A,stable(t)-q_A,shock(t))` after the shock | pathwise deficit relative to the matched stable trajectory |

The `dogmatism` name must not be interpreted psychologically. `|z|>3` means three opposing unit steps would not yet reverse the current sign. It does not measure observed refusal to update. Private-signal sampling and private choice on a conflict are separate quantities and must not be substituted for one another.

## 16. Assumptions and limitations

1. Private accuracy is fixed and identical at juvenile and adult updates.
2. Recommendations and truth are binary and symmetric.
3. The fixed model uses only aggregate adult accuracy; adult confidence is displayed but not used for credibility.
4. Each encounter independently redraws a teacher from a well-mixed adult pool.
5. RL assumes conditional independence of private and adult correctness and, by default, objective full-information feedback after every event.
6. RL trust is retained at maturation but has no expressed adult effect in the current model.
7. Maturation is a constant hazard, not a fixed birthday. Adult entrants are survivor-selected.
8. Score caps are fixed model structure, not inherited traits.
9. Correctness affects both adult survival and productivity in the primary payoff model; their separate contributions require ablations.
10. There is oblique population-level cultural transmission, not explicit parent teaching, norms, social sanctions, kin structure, or horizontal juvenile–juvenile learning.
11. The model does not test Simon's altruism mechanism: it contains no bundled costly norm or group-level altruistic benefit.
12. It does not establish empirical genetic separability, a historical explanation for childhood, obedience, morality, or a named species' cognition.

## 17. Implementation mapping

| Mathematical object | Python function |
|---|---|
| state dimensions | `shape` |
| initial conditions | `initial` |
| capped score/trust movement | `shift` |
| `chi_theta(z)` | `correct` |
| adult advice and resource | `environment` |
| policy follow probability | `choice` |
| metrics | `metrics` |
| full event generator and demography | `rhs` |
| RK4 step | `rkstep` |
| trajectory integration | `run` |
| frozen-environment linear operator | `generator` |
| resident equilibrium helper | `equilibrium` |

The executable source remains authoritative when a later code revision changes an equation. Any such change must update this document and the run manifest together.


## Conditional survival to maturity

The dashboard survival metric holds final advice accuracy fixed and follows a neutral newborn's juvenile process. For policies without learned trust, it is exactly m/(m+mu_F). For RL, let J be the five-state trust transition generator minus diagonal maturation and trust-specific mortality hazards. Then survival is m 1^T(-J)^(-1)e_0. Trust transitions still occur at juvenile_rate×feedback with objective success/failure probabilities q and 1−q. The score can be marginalized because juvenile mortality depends on trust/action accuracy, not the stored score. This is a frozen-advice conditional probability, not cohort survival over an environmental shock. The independent numerical verification includes transient integration of this killed process. It replaces an invalid coarse time-quadrature estimate; no demographic trajectory used that estimate.
