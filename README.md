# Developmental deference, cultural learning and demographic fitness

Hypothetical computational research. Technical validation does not establish a historical adaptation or genetic separability from cognition.

## Versions at a glance

| Version | Scientific question / change | Data and specification |
|---|---|---|
| V1 | Two demographic ODEs isolate deference and maturation under fixed private and adult error distributions. | [v1/](v1/) |
| V2 | Adult advice precision changes with a signed, externally imposed calendar-time drift. | [v2/](v2/) |
| V3 | Copying propensity declines over time while an adult advice-quality feature increases. | [v3/](v3/) |
| V4 | Adults transmit beliefs acquired as juveniles; cognitive substates retain confidence and learned trust. | [v4/](v4/) |
| V5 | Separates retained private evidence from held conviction, with noisy access, query costs and actual fact repertoires. | [v5/](v5/) |
| Further work | Research directions motivated by unresolved identification, learning, cultural and demographic questions. | [proposals/](proposals/) |

## View the research

Build and preview the six-tab site:

~~~bash
python scripts/build_pages.py
python -m http.server 8000 --directory docs
~~~

Open http://localhost:8000. The tabs are V1–V5 and Further work. Each has Model, Results, Changes and Shortcomings. The original interactive dashboards retain every plot family. Under each plot, an exact displayed-data ZIP supplies JSON, CSV, available parameters and units, alongside a reference-data package. Data and definitions remain version-specific. Large results load when requested. No new results are claimed for proposals.

## Prepare GitHub Pages

The research history contains files above GitHub's [100 MiB regular-Git limit](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github). Preserve that history locally and create a clean publishable snapshot:

~~~bash
python scripts/prepare_github.py --output dist/github-repository
~~~

The output is a Git repository on **main**, containing every version's source, specification and data. Large originals are losslessly chunked inside their version folder. Run the following in the exported repository to restore original paths and verify their SHA-256 hashes:

~~~bash
python scripts/restore_large_files.py
~~~

The existing research history is not rewritten. Per-version records retain their contemporaneous branch names and verification context; the current main branch unifies every version. To publish, add your GitHub remote to the prepared repository, push main, and select **Settings → Pages → Source: GitHub Actions**. No remote or public deployment is performed by these preparation scripts. Do not push the original research history directly: it still contains historical oversized blobs.

The included workflow restores large files, builds and verifies the static site, then publishes the generated output. The builder enforces the [1 GB Pages site limit](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits). URLs are relative for project-site prefixes. Runtime assets are local; no API key or backend is required. Original standalone dashboards remain available offline after restoration. The portal's shared-data adapters use ordinary HTTP, as on GitHub Pages.

## Equations and definitions

Each section below belongs to its own scientific version. F is the nonreproductive follower stage and A the reproductive adult stage. Maturation is irreversible at constant hazard m=1/tau. Extra cognitive substates in V4/V5 are not additional biological stages. All time and density units are arbitrary model units.

### V1: behavioral decisions and two-stage demography

The private error has mean0 and variance sigma_I²; adult error has mean b_A, variance sigma_A², and covariance rho sigma_I sigma_A with private error.

$$L_{copy}(d)=(1-d)\sigma_I^2+d(\sigma_A^2+b_A^2).$$

$$L_{blend}(d)=(1-d)^2\sigma_I^2+d^2(\sigma_A^2+b_A^2)+2\rho d(1-d)\sigma_I\sigma_A.$$

$$\mu_F=\mu_{F,base}+k_{error}L,\quad m=1/\tau,\quad N=F+A.$$

$$S(N)=\frac{S_0}{1+N/K_N},\quad \beta(N,\tau)=\beta_{max}(\tau)\frac{S(N)}{K_S+S(N)}.$$

$$\dot F=\beta(N,\tau)A-(m+\mu_F)F,\qquad \dot A=mF-\mu_A A.$$

$$B=\beta A,\quad D=\mu_F F+\mu_A A,\quad M=mF,\quad \dot N=B-D.$$

M0 has constant beta_max=beta_const. M1 separately imposes:

$$\beta_{max}(\tau)=\beta_{min}+\beta_{gain}\frac{\tau}{\tau+\tau_{learning}}.$$

At low density beta0=beta_max S0/(KS+S0), with demographic matrix:

$$G_0=\begin{pmatrix}-(m+\mu_F)&\beta_0\\m&-\mu_A\end{pmatrix}.$$

$$r_0=\frac{-(m+\mu_F+\mu_A)+\sqrt{(m+\mu_F-\mu_A)^2+4m\beta_0}}{2}.$$

Positive growth requires m beta0 > mu_A(m+mu_F).

$$\Delta r_0(d,\tau)=r_0(d,\tau)-r_0(0,\tau),\qquad r_T=\frac{\log[N(T)/N(0)]}{T}.$$

For positive persistent equilibrium:

$$\beta_{required}=\mu_A(1+\mu_F\tau),$$

$$N_*=K_N\left[\frac{S_0}{K_S}\left(\frac{\beta_{max}}{\beta_{required}}-1\right)-1\right],$$

$$A_*=\frac{N_*}{1+\mu_A\tau},\qquad F_*=\mu_A\tau A_*.$$

When r0<=0, the nonnegative equilibrium is0. Conditional mutant invasion uses the mutant matrix with beta(N*_resident,tau_mutant) and the same external advice distribution. Its dominant eigenvalue supports initial invasion, not fixation.

Survival to maturation with constant competing mortality is m/(m+mu_F); mean stage-exit time is1/(m+mu_F). Tau is not the mean observed age of surviving adults. With zero births and deaths:

$$F(t)=F(0)e^{-mt},\qquad A(t)=A(0)+F(0)(1-e^{-mt}).$$

### V2: externally improving or decaying adult advice

$$\sigma_A(t)=\operatorname{clamp}[\sigma_A(0)e^{-gt},\sigma_{floor},\sigma_{ceiling}].$$

Positive g improves precision; negative g degrades it. Substitute sigma_A(t) into both V1 losses and mu_F(t). F and A retain the same ODEs. A frozen-time eigenvalue r_inst(t) is a diagnostic; changing advice does not have the single stationary interpretation used for V1.

### V3: declining copying and increasing advice feature

$$d(t)=d_{floor}+(d_0-d_{floor})e^{-\lambda_d t},$$

$$Q(t)=Q_0+(Q_{max}-Q_0)(1-e^{-\lambda_Q t}),$$

$$\sigma_A(t)=\sigma_{A0}\frac{1+Q_0}{1+Q(t)}.$$

Substitute d(t) and sigma_A(t) into V1's losses, mortality and two demographic equations. Rates lambda_d,lambda_Q are nonnegative. These are calendar-time functions rather than individual age or learned knowledge.


## V4: full endogenous-culture model

Source: [v4/mathematical_model.md](v4/mathematical_model.md)

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


## V5: full private-evidence model and companion benchmarks

Source: [v5/mathematical_model.md](v5/mathematical_model.md)

# V5 mathematical model

All parameters are hypothetical. This model isolates an inherited source-use propensity from cognitive hardware and private-cue quality. It does not establish genetic separability in organisms.

## Stages and memory

For each inherited trait g=(d,tau), F_g(u,b) and A_g(u,b) are juvenile and adult densities. u and b are integers in [-H,H]; H=4 by default. u stores only personally obtained evidence; b stores held convictions, including accepted testimony. A neutral score predicts either action with equal probability. Each biological individual remains in exactly one of two stages. The cognitive subcompartments give 2(2H+1)^2 ODE variables per genotype.

Fresh private evidence moves both u and b one signed step. At the caps, an outward update stays at the cap; contradictory evidence always moves inward. Accepted adult testimony moves b only. No source writes factual content into newborns: births enter F(0,0). Maturation transfers the existing joint state at hazard m=1/tau. A deliberately labeled reset ablation instead transfers into A(0,0). tau is an exponential waiting-time parameter, not a fixed age or observed survivor age.

Crucially, d=0 organisms retain everything they acquired during childhood. In the main d=0 model u=b exactly. The meaningful private-learning comparison is not a learner forced to forget at maturation.

## Information and deference

Let j(u)=(1+sign(u))/2 be the probability that the accumulated private judgment recommends +. The adult pool's probability of recommending + is

q_plus = epsilon + (1−2 epsilon) [sum_g,u,b A_g(u,b) j(b)] / [sum_g,u,b A_g(u,b)].

The default transmission error epsilon=.05 is externally fixed. The pool is the candidate's own population in an isolated run and the common resident adult pool in invasion/competition. No adult age implies correct knowledge. At zero adults, social learning and action substitution are disabled.

A juvenile publicly chooses the adult judgment with probability d and its own accumulated private judgment otherwise. Hence

P(public + | u) = (1−d)j(u)+d q_plus,

and P(override | disagreement)=d. A social learning encounter accepts an adult sign into b with probability d even when both judgments agree. Thus the main d is explicitly a bundle of public action substitution and memory acceptance. The accept×override factorial separates those paths; a conflict-only acceptance ablation excludes agreement reinforcement. The main result alone cannot be identified as the benefit of ignoring one's own judgment.

Private cue opportunities occur at lambda_F=nu_private access/load; social encounters occur at lambda_S=nu_social/load. Actual probability of a signed + private cue is pi_I(t). In ordinary conditions it equals p if truth theta=+1 and 1−p if truth theta=−1. The misleading-channel experiment changes pi_I while truth stays fixed. All genotypes within a scenario have identical cue quality, exposure opportunities and memory capacity. Achieved accuracy can differ through learning histories, action choices and survival filtering; this is not an inherited cognitive-accuracy change.

`load` is an effective exposure divisor. It is algebraically a rescaling of opportunities relative to demographic time, not a mechanistic model of complex reasoning. The separate stochastic repertoire experiment represents multiple distinct facts explicitly and is described in repertoire_model.md.

## Adult policies and costs

Adults express sign(b) and transmit that same belief. Adult private cues continue to move both u and b, with query rate

- retained/updating: lambda_A = nu_adult access/load;
- frozen: lambda_A = 0;
- audit: lambda_A(b) = nu_adult access/load times 1 when |b|<h, and audit_floor otherwise.

Default h=2 and audit_floor=.05. These policies are imposed experimental architectures; neither freezing nor confidence-based auditing is called emergent or optimal dogmatism. When H<h, auditing always samples and coincides with continuous updating. Adults who freeze can still disappear and be replaced by newly matured adults: zero within-adult updating does not make population culture immutable.

Each actual private query contributes query_cost×query_rate to mortality. This is a stated energetic/hazard approximation, not an observed biological cost. It never directly rewards d or freezing. Sampling-cost and accuracy channels are separated by zero-cost experiments. The model does not charge search/teaching or social-observation costs.

The oracle confidence gate compares max(q_correct,1−q_correct) with sigmoid(|u| logit(p)), uses the better source when it exceeds this private-confidence proxy, and can invert an anti-informative adult source. It knows true current adult reliability. It is a privileged finite-score heuristic, not a full Bayesian learner or a realistic learned-trust model. Its displayed d axis is inactive. The additional exact Bayesian benchmark establishes a narrower information-value bound.

## Demographic equations

Let Q_I shift both scores under private cues, Q_S shift b under accepted social signs, and Q_A implement adult querying. These are conservative Markov generators. For each genotype, with column-state convention,

F_dot = (Q_I+Q_S)F − diag(m+mu_F(u))F + e_00 sum_b,u beta(b,N) A(u,b),

A_dot = Q_A A + m F − diag(mu_A(b))A.

The held-belief correctness is c_theta(b)=(1+theta sign(b))/2. Juvenile public correctness uses the same expression applied to the probability of public +. Rates are

mu_F(u) = mu_F_base + k_F [1−public_correct(u)] + query_cost lambda_F,

mu_A(b) = mu_A_base + k_A [1−c_theta(b)] + query_cost lambda_A(b),

beta(b,N) = [beta_base+beta_skill c_theta(b)] S(N)/[K_S+S(N)],

S(N) = S0/[1+N/K].

There is no direct fecundity-versus-tau curve or deference bonus. K is a resource-density scale, not a carrying capacity. The scalar stage totals obey F_dot=B−M−D_F, A_dot=M−D_A and N_dot=B−D. Maturation and cognitive transitions conserve total density. Accuracy-linked terms and query cost are both disabled for the neutral control.

For homogeneous populations, the operators average learning events exactly. There is no Monte Carlo error in those ODE maps. The stochastic environmental-history and repertoire experiments have separate seed-based uncertainty.

## Inheritance and selection

Offspring inherit their parent's d and tau, then acquire culture from the current shared adult pool. Broad trait competition uses uniform mutation probability .001 across the declared nine genotypes. A separate four-architecture competition has equal initial frequencies, zero mutation and common tau=3; it treats the specified adult policy as an additional inherited architecture for that comparison only.

At a resident ecological-cultural equilibrium, freeze its q_plus and resource factor. Construct the mutant's complete linear operator over F(u,b),A(u,b), using its own d,tau and policy. The largest real eigenvalue is conditional rare-mutant invasion growth. Adult teachers are resident adults, not an independent mutant population. Self-invasion and residuals are checked. A positive eigenvalue supports initial invasion, not guaranteed fixation or an ESS.

Time-dependent invasion integrates resident and rare-mutant equations together, excludes mutant feedback on resident teachers/resources, repeatedly normalizes mutant densities and accumulates log growth. Reported rates are finite windows after burn-in, not arithmetic averages of instantaneous eigenvalues. Resident-against-itself has zero relative growth; its absolute finite-window rate need not be exactly zero.

## Measurements and limitations

Maps separate r_T=log(N(T)/N(0))/T, N(T), last-100-time-unit growth, conditional invasion, private versus held belief accuracy, public action accuracy, score depth, wrong high confidence, query rates/costs and recovery. Recovery is relative to the same policy's stable baseline, sustained over 20 units at five-unit observations; unavailable values are censored. Score persistence |b|>2 means retaining a nonzero sign after two opposing unit steps. It is not refusal to process evidence.

Survival to maturity is the exact absorbing probability of a neutral newborn under final advice and private-cue statistics held fixed: m 1^T(−J)^−1 e_00, where J is the transient juvenile operator including mortality and maturation. It is not realized cohort survival through a changing environment.

Population-level gains can reflect ordinary information transfer. Finite score caps and equal-sized endorsements can misweight unequal evidence, so freezing's advantage over this updating rule is not a proof against calibrated Bayesian updating. Task correlation, teacher genealogy, costly search, normative collaboration, sanctions, physical coercion and empirical life-history calibration are absent. The scientific question is conditional mechanism identification, not historical proof of childhood obedience.

Source: [v5/repertoire_model.md](v5/repertoire_model.md)

# V5 repertoire companion: actual knowledge coverage under finite access

**Status:** predeclared companion experiment completed 2026-10-30  
**Implementation:** [`experiments/repertoire.py`](experiments/repertoire.py)  
**Raw generation summaries:** [`experiments/repertoire.csv`](experiments/repertoire.csv)  
**Endpoint summaries and validation:** [`experiments/repertoire.json`](experiments/repertoire.json)

## Purpose and claim boundary

The main V5 ODE uses `D` as a rate divisor—an effective information-load or repertoire-dilution parameter. It does not represent multiple things to know. This companion addresses that limitation directly: each organism carries separate private and held scores for `D=4,16,64` independent binary facts. It can therefore measure knowledge coverage, between-context heterogeneity, cultural retention, and recovery context by context.

This is not a replacement for the demographic model. Cohorts are fixed at `N=128`; there is no birth, death, density dependence, reproduction weighting, mutant invasion, or selection. It supports claims about learning and cultural transmission only. Independent binary facts also do not constitute combinatorial reasoning, multi-step skill, cooperation, social norms, teaching, or a dependency-structured technology. Computational score capacity and sampling budgets are equal within every scenario.

## Predeclared design

No parameter was tuned after seeing results.

| Component | Value |
|---|---|
| Repertoire size | `D ∈ {4,16,64}` independent binary facts |
| Cohort size | 128 organisms |
| Generations | 24 recorded cohorts; generation 0 is the acquired founder cohort |
| Score state | Per-fact private `u` and held `b`, integers bounded to `[-4,4]` |
| Private cue quality | `p ∈ {0.55,0.70,0.90}` |
| Homogeneous deference | `d ∈ {0,0.5,1}` |
| Juvenile private budget | 16 random-context cues; each cue moves both `u` and `b` |
| Juvenile social budget | 16 random-context encounters with random adults from the prior cohort |
| Social update | A nonzero adult `sign(b)` is accepted with probability `d` and moves child `b` only |
| Current conflict action | A child follows conflicting nonzero adult advice with probability `d`; this is recorded but does not alter payoffs |
| Adult retained-update | 16 additional private cues |
| Adult frozen | 0 additional private cues |
| Adult confidence-audit | 16 opportunities; query when `abs(b)<2`, otherwise with probability 0.05 |
| Founder acquisition | All founders start `u=b=0`, then receive 16 common private-cue opportunities before teaching |
| Environments | Stable; or exactly 25% of context truths flip before generation 12 learns |
| Replication | Seeds 501–506 |
| Full grid | 972 runs, 23,328 run-generation rows, 162 six-seed aggregate cells |

All adult advice is endogenous. A learner samples the prior cohort's actual `b` for the selected context; there is no fixed teacher accuracy. Founder quality is an observed result of their 16 private cues, not an initialization parameter. Private-only `d=0` learners retain childhood knowledge and satisfy `u=b` exactly.

### Common random numbers

Within each `D × seed` block, every matched `p`, `d`, adult policy, and environment reuses the same initial truths, flip mask, sampled contexts, teacher identities, cue-quality uniforms, testimony-acceptance uniforms, conflict-override uniforms, private tie breaks, and audit uniforms. Correct-cue sets are nested across `p`: every cue correct at `p=.55` is also correct at `.70` and `.90`.

Stable and quarter-flip runs are exactly identical through generation 11. State-dependent audit eligibility and endogenous teacher signs necessarily diverge after policies produce different `b` states. SHA-256 hashes for all 18 `D × seed` schedules are stored in the JSON.

## Update order

For each nonfounder generation:

1. Apply the truth flip at generation 12 in the shock environment.
2. Freeze the preceding adult cohort as the current teachers and score its accuracy against current truth.
3. Initialize the new cohort at `u=b=0`.
4. Give every juvenile 16 private cues on random contexts; each cue moves both ledgers.
5. Give every juvenile 16 random-context encounters with random prior-generation adults. Nonzero testimony is accepted with probability `d` and moves `b` only.
6. Record private–adult action conflicts and stochastic overrides. A private tie is resolved by a pre-generated fair coin; a teacher with `b=0` supplies no testimony.
7. Apply the adult update, frozen, or confidence-audit query policy.
8. Score the adult cohort; it becomes the sole teacher pool for the next generation.

The true-state shock occurs before teacher accuracy is scored at generation 12. Thus the immediate teacher-accuracy loss measures how much previously accumulated culture has become obsolete.

## Metrics and output schema

The CSV has one row per run-generation. Core fields are:

- identifiers: `run_id, seed, D, p, d, policy, environment, generation`;
- knowledge: `adult_accuracy, private_accuracy, held_coverage, private_coverage`;
- confidence and heterogeneity: `held_confidence, private_confidence, wrong_high_confidence, knowledge_heterogeneity, context_accuracy_sd, context_coverage_sd`;
- information use: `juvenile_private_queries, juvenile_social_encounters, adult_queries`;
- endogenous source quality: `teacher_accuracy, teacher_accuracy_expressed, teacher_coverage, teacher_knowledge_heterogeneity`;
- social action: `social_testimonies, accepted_social_testimonies, child_conflicts, child_overrides, child_conflict_override_rate`.

Accuracy assigns 0.5 to an unknown (`score=0`) fact. Coverage is the fraction of organism–context scores that are nonzero. Knowledge heterogeneity is the mean across facts of within-cohort variance in correctness scores `{0,0.5,1}`. This keeps lack of coverage distinct from confidently wrong knowledge.

The JSON stores exact parameters, schedule hashes, invariant results, all 972 endpoint summaries, and six-seed mean/SD aggregates. Shock summaries include pre-shock accuracy (generations 9–11), generation-12 accuracy, final recovery fraction, first generation reaching 90% recovery, and mean post-shock accuracy.

## Verification results

All predeclared checks passed:

| Check | Measured result |
|---|---|
| `d=0` retained-knowledge invariant | Maximum `abs(u-b) = 0` over every context, organism, generation, policy, environment, and seed |
| No-signal test | Accuracy 0.5, coverage 0, and no nonzero score |
| Founder acquisition | Exactly 16 queries per founder; identical within matched `D,seed,p`; no fixed source accuracy |
| Matched cue quality | Nested correct-cue sets across `.55 ≤ .70 ≤ .90` |
| Matched environments | Maximum stable versus shock difference before generation 12: 0 |
| Private-channel isolation | Under frozen and unconditional retained-update policies, private accuracy/coverage is identical across `d`: maximum difference 0 |
| Score bounds | Maximum observed absolute score 4 |
| Adult query policies | Retained-update exactly 16 per adult-generation; frozen exactly 0; audit observed range 0.609–15.727 |
| Conflict override | Aggregated rates: 0 for `d=0`, 0.4983 mean for `d=.5`, and 1 for `d=1` |

## Measured results

### 1. Social testimony improves stable-world accuracy, but its marginal value shrinks with a larger actual repertoire

The table averages the end-accuracy and coverage difference from the matched `d=0` control across all three cue qualities and adult policies (nine cells per entry).

| Actual repertoire | `d=.5` accuracy Δ | `d=1` accuracy Δ | `d=.5` coverage Δ | `d=1` coverage Δ |
|---:|---:|---:|---:|---:|
| 4 facts | +0.0612 | +0.1518 | +0.0337 | +0.0615 |
| 16 facts | +0.0336 | +0.0691 | +0.0568 | +0.1059 |
| 64 facts | +0.0069 | +0.0145 | +0.0234 | +0.0494 |

Every stable-world aggregate cell had a positive accuracy difference from its matched `d=0` control, but the mean benefit at `D=64` was only 0.0145 even under `d=1`. With fixed 16-event private and social budgets, a larger repertoire spreads encounters thinly across facts. Testimony still increases coverage, yet most facts lack enough repeated, independent evidence for strong accuracy gains.

This is the central result that a pure rate divisor cannot show: cultural access can broaden coverage while delivering progressively smaller per-fact accuracy gains as the number of actual facts grows.

### 2. Freezing is advantageous only in a narrow, dense-repetition corner

Stable-world held accuracy under full deference (`d=1`) was:

| `D` | `p` | Confidence audit | Frozen | Retained-update |
|---:|---:|---:|---:|---:|
| 4 | .55 | .9100 | **.9261** | .8477 |
| 4 | .70 | **.9902** | .9827 | .9854 |
| 4 | .90 | .9997 | .9990 | **.9998** |
| 16 | .55 | .5828 | .5656 | **.5834** |
| 16 | .70 | **.7956** | .7341 | .7948 |
| 16 | .90 | .9411 | .8822 | **.9413** |
| 64 | .55 | .5232 | .5139 | .5232 |
| 64 | .70 | .5954 | .5557 | .5954 |
| 64 | .90 | .6880 | .6107 | .6880 |

Freezing led only at `D=4,p=.55`, where many encounters revisit the same few facts and private evidence is weak. In that corner, recurrent testimony allows a coherent cultural majority to persist while additional noisy private cues can erode it. Once the repertoire expands, frozen adults have insufficient coverage and are consistently worse than update/audit adults. This is a learning result, not a fitness advantage: frozen adults pay no modeled biological cost here because this companion has no fitness function.

### 3. Confidence auditing saves queries only after confidence can accumulate

Retained-update adults made 368 postfounder queries over generations 1–23 in every run; frozen adults made none. Under `d=1`, confidence-audit totals were:

| `D` | `p=.55` | `p=.70` | `p=.90` |
|---:|---:|---:|---:|
| 4 | 64.4 | 30.0 | 19.3 |
| 16 | 250.9 | 215.8 | 152.1 |
| 64 | 354.2 | 351.8 | 344.2 |

For four facts, repeated evidence quickly crosses the audit threshold and the audit policy approaches update-level accuracy with far fewer queries. For 64 facts, most context scores remain low, so the audit policy queries almost as often as retained-update and has essentially identical accuracy. The audit rule therefore adapts its effort to represented coverage, but it should still be described as an imposed heuristic rather than an optimal stopping policy.

### 4. A real state change exposes the risk of frozen low-quality culture

The clearest persistence–recovery contrast occurred at `D=4,p=.55,d=1`:

| Adult policy | Pre-shock accuracy | Generation-12 accuracy | End accuracy | End recovery fraction |
|---|---:|---:|---:|---:|
| Confidence audit | .8967 | .7127 | .8963 | .9964 |
| Frozen | .9214 | .7207 | .7922 | .3575 |
| Retained-update | .8432 | .7012 | .8449 | 1.0109 |

Frozen adults began with the best stable knowledge in this low-quality, four-fact corner but retained obsolete convictions after 25% of truths changed. Audit and retained-update recovered essentially all lost accuracy by the end; frozen recovered only about 36%. At `p=.70` and `.90`, even frozen lineages recovered because accurate juvenile private cues rebuilt the teacher pool across generations, although recovery lagged updating policies.

At `D=64`, the immediate shock loss was small (for `d=1`, roughly 0–0.016 depending on `p` and policy), but this is not evidence of robust knowledge: absolute end accuracy was only .514–.688. The cultural state was too sparse to be strongly correct before the shock, so there was less accumulated accuracy to lose.

## Interpretation

The companion supports four restrained conclusions:

1. Endogenous social testimony can aggregate weak evidence in a stable world, especially when a small actual repertoire is revisited often.
2. Increasing the number of facts at fixed learning budgets raises the value of social transmission for coverage but dilutes its accuracy benefit per fact.
3. Freezing is not generally superior to competent retained private learning. Its only leading stable cell is the small-repertoire, low-cue-quality condition, and that same condition shows its sharpest failure after real change.
4. Confidence auditing is economical only when the evidence process can actually build confidence; in a large sparse repertoire it approaches continuous updating.

These results complement rather than duplicate the main ODE. The ODE addresses population dynamics and selection-related questions; this model shows how finite access is distributed across represented knowledge. No abundance, mortality, or invasion conclusion should be drawn from this companion.

## Limitations and next discriminating tests

- Facts are independent and equally likely to be sampled. There are no prerequisites, complementarities, recombination, or task-level rewards.
- Adults transmit only `sign(b)`, not confidence, provenance, demonstration quality, or full action sequences.
- Random teachers can share cultural ancestry; source-lineage correlation is generated implicitly but not labeled or corrected by the learner.
- Every generation is a new fixed-size cohort. The experiment does not model overlapping ages, parent choice, reproduction, or demographic filtering.
- Deference is homogeneous within a run and controls both testimony acceptance and conflict override. Since override is observational only here, held-knowledge effects arise through acceptance, but a future behavioral-reward model should split the channels.
- Recovery after the 25% flip is driven by new private evidence and cohort replacement. It is not learner-side identification of whether evidence is misinformation or true environmental change.
- Six paired seeds characterize Monte Carlo variation for this bounded companion; they are not a basis for population-level empirical calibration.

A genuinely compositional extension would assign dependencies among subskills and let teachers expose selected procedures rather than isolated signs. That is outside this experiment and should not be inferred from the present `D` effects.

## Reproduction

From the repository root:

```bash
python v5/experiments/repertoire.py --self-test-only
python v5/experiments/repertoire.py
```

The first command runs a lightweight deterministic invariant check. The second regenerates all 972 runs and overwrites only `v5/experiments/repertoire.csv` and `v5/experiments/repertoire.json`.

---

## Exploratory post-main follow-up: observable-confidence tutor search

**Status:** exploratory mechanism-identification analysis prompted by the main repertoire dilution result; it is not a preregistered confirmation.  
**Implementation:** [`experiments/repertoire_tutors.py`](experiments/repertoire_tutors.py)  
**Generation summaries:** [`experiments/repertoire_tutors.csv`](experiments/repertoire_tutors.csv)  
**Paired summaries:** [`experiments/repertoire_tutors.json`](experiments/repertoire_tutors.json)

### Question and mechanism

The main companion samples a random prior-generation adult. That mixes adults with formed convictions, weak one-cue impressions, and no knowledge of the selected context. The follow-up asks whether the observed dilution is partly a **source-access problem** rather than an absence of cultural knowledge.

Two teacher rules are paired:

- **Random:** sample one random prior-generation adult; `b=0` returns no testimony.
- **Observable-confidence filter:** search the prior cohort for adults satisfying `abs(b_context)≥2`, then uniformly sample one qualifying adult. If nobody qualifies, return no testimony and retain the child's private knowledge/action.

The filter never observes truth, past correctness, payoff, age, prestige, or genotype. Confidently wrong adults are eligible. All adult knowledge still comes from the same founder, juvenile, social, and adult acquisition processes as in the main companion; no experts are generated or assigned.

This filter receives **cost-free full-cohort search**. That is a deliberately favorable mechanism probe, not an optimal policy. The outputs therefore retain candidate-pool fraction, search availability, endorsements returned, endorsements accepted, and conditional advice accuracy. Any practical claim would need to price search or constrain the visible candidate set.

### Fixed exploratory grid and pairing

The grid uses `D={4,16,64}`, `p={.55,.70}`, `d={0,.5,1}`, all three adult policies, stable and quarter-flip environments, and six new seeds 800–805. Cohort size, 16 private cues, 16 social encounters, 16 adult opportunities, score bound, audit rule, generation count, and generation-12 truth flip are unchanged. The full comparison contains 1,296 runs, 648 paired filter contrasts, 108 six-seed aggregate cells, and 31,104 generation rows.

Within each `D × seed` block, teacher rules share initial truths, flip contexts, private and adult cues, social contexts, the underlying teacher-choice variate, testimony-acceptance draws, conflict-override draws, tie breaks, and audit uniforms. For random sampling, the common teacher variate maps over all 128 adults; for filtering, it maps to a rank within the eligible set.

All checks passed:

- `d=0` satisfies `u=b` exactly and produces identical accuracy, coverage, and queries under both teacher rules;
- matched stable and shock runs are identical through generation 11;
- cue-correctness sets are nested across `p`;
- all founders acquire evidence from exactly 16 cues rather than fixed accuracy;
- scores remain within `[-4,4]`;
- the filtered rule uses only `abs(b_context)≥2`, and an empty eligible set returns no testimony.

### Result 1: confidence filtering partially reverses actual-repertoire dilution

The table reports **filtered minus random** final held accuracy under full deference in the stable environment.

| `D` | `p` | Confidence audit | Frozen | Retained-update |
|---:|---:|---:|---:|---:|
| 4 | .55 | +.0086 | +.0212 | +.0452 |
| 4 | .70 | −.0003 | +.0011 | +.0023 |
| 16 | .55 | +.0772 | +.1646 | +.0874 |
| 16 | .70 | +.0494 | +.0962 | +.0518 |
| 64 | .55 | +.0258 | +.0460 | +.0275 |
| 64 | .70 | +.0547 | +.0773 | +.0550 |

Filtering adds little once four-context culture is already near saturation. It adds substantially at 16 contexts and remains helpful at 64, particularly for frozen adults. This identifies one source of the main dilution result: random encounters often reach ignorant or weakly committed adults even when the cohort contains a smaller set of strongly committed tutors.

The filter does not eliminate dilution. Averaged across adult policies under `d=1`, filtered final accuracy at `D=64` is only .5530 for `p=.55` and .6439 for `p=.70`. Selective access improves which information is transmitted, but fixed encounter budgets still limit repertoire coverage and the amount of independent evidence per fact.

### Result 2: the benefit combines better advice with far more available endorsements

Stable `d=1` summaries averaged across adult policies were:

| `D` | `p` | Eligible pool fraction, filtered state | Search availability | Filtered advice accuracy | Random advice accuracy | Filtered endorsements | Random endorsements |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | .55 | .838 | 1.000 | .930 | .876 | 47,104 | 44,013 |
| 4 | .70 | .941 | 1.000 | .991 | .983 | 47,104 | 46,278 |
| 16 | .55 | .393 | 1.000 | .792 | .603 | 47,104 | 33,828 |
| 16 | .70 | .511 | 1.000 | .960 | .841 | 47,104 | 36,287 |
| 64 | .55 | .071 | .989 | .678 | .556 | 46,595 | 16,290 |
| 64 | .70 | .091 | .994 | .931 | .724 | 46,802 | 16,599 |

At `D=64`, only about 7–9% of adults qualify for an encountered fact, yet a global search almost always finds at least one because the cohort has 128 adults. The filter therefore returns nearly the maximum possible 47,104 endorsements per run, while random sampling returns only about 16,000. The accuracy gain cannot be attributed to discernment alone: it combines **higher conditional advice quality** with **roughly threefold greater testimony availability**. Search is free in this experiment, so these results do not establish that filtered tutoring is net beneficial once discovery time, attention, competition, or access costs are included.

The wrong-confidence risk is visible rather than removed. At `D=64,p=.55`, qualifying pools are about 32% wrong on average in the filtered trajectories, and selected advice is only .678 accurate. Confidence is an informative cue in these runs, not an oracle.

### Result 3: true change can turn confidence selection into a persistence trap

The sharp boundary is again `D=4,p=.55,d=1` after 25% of truths flip:

| Adult policy | Teacher rule | Pre-shock | Shock generation | End | End recovery fraction |
|---|---|---:|---:|---:|---:|
| Confidence audit | Filtered | .9245 | .7288 | .8592 | .6672 |
| Confidence audit | Random | .9068 | .7227 | .9009 | .9776 |
| Frozen | Filtered | .9520 | .7313 | .7295 | −.0140 |
| Frozen | Random | .9260 | .7236 | .8283 | .5237 |
| Retained-update | Filtered | .8944 | .7257 | .8896 | .9744 |
| Retained-update | Random | .8443 | .7090 | .8464 | 1.0283 |

Before the shock, filtering makes culture more accurate and confident. Immediately after the shock, that same confidence points learners toward obsolete tutors. Continuous retained updating eventually converts the filtered advantage into improved end accuracy (+.0433 versus random), but audit filtering ends .0417 below random and frozen filtering ends .0988 below random. Under frozen filtered teaching, recovery is effectively absent by generation 23.

This is not misinformation identification. The selector observes confidence only and cannot know whether confidence was earned under the current truth. The result is a direct counterexample to “formed convictions are necessarily better tutors”: observable confidence helps in stable or recoverable settings but can amplify obsolete, confidently wrong culture after real change.

### Exploratory interpretation

The follow-up supports a narrower mechanism claim:

> Actual-repertoire dilution partly reflects difficulty locating knowledgeable sources. Observable conviction can improve advice quality and restore testimony availability, but cost-free cohort-wide search and environmental stability are doing important work; after change, confidence filtering can retard correction unless adults continue to acquire private evidence.

It does not support claims that confidence is generally calibrated, global tutor search is free or optimal, filtered teaching raises fitness, or adults are intrinsically expert. There is still no demography or selection in this companion.

To reproduce this separate follow-up without rerunning the main grid:

```bash
python v5/experiments/repertoire_tutors.py --self-test-only
python v5/experiments/repertoire_tutors.py
```

Source: [v5/bayesian_benchmark.md](v5/bayesian_benchmark.md)

# Exploratory calibrated-Bayes benchmark

This benchmark isolates one binary task in a stable world. It is not a demographic model and does not assume that adults are intrinsically wiser. The initial probability `q0` is calibrated prior knowledge for this benchmark only; successive cues are conditionally independent and have known accuracy `p`.

After `n` cues, with `k` positive cues, the exact expected accuracy of the posterior-optimal decision is

\[
\sum_{k=0}^{n}\max\{q_0\Pr(k\mid\theta=+),\ (1-q_0)\Pr(k\mid\theta=-)\}.
\]

The finite-memory comparator starts at score `+4`, adds `+1` or `-1` for each cue, clips at `[-4,4]` with a boundary self-loop, chooses by the score sign, and randomizes at zero. Its distribution is propagated by an exact nine-state Markov transition, not Monte Carlo.

## Result

Calibrated Bayes was nondecreasing in expected accuracy and never fell below the initial prior across all 369 cells (`q0` = 0.70, 0.85, 0.95; `p` = 0.55, 0.65, 0.85; `n` = 0…40). The bounded unit-step rule fell below the prior in four parameter combinations:

| Prior `q0` | Cue accuracy `p` | Worst `n` | Bounded accuracy | Loss versus prior | Bayes at same `n` |
|---:|---:|---:|---:|---:|---:|
| 0.70 | 0.55 | 4 | 0.699374 | 0.000626 | 0.700000 |
| 0.85 | 0.55 | 40 | 0.720980 | 0.129020 | 0.865491 |
| 0.95 | 0.55 | 40 | 0.729586 | 0.220414 | 0.950760 |
| 0.95 | 0.65 | 40 | 0.939043 | 0.010957 | 0.990960 |

Thus, in this cost-free stable-world control, preserving a calibrated prior can outperform misweighted bounded updating when weak evidence is counted in unit steps. That supports a narrower interpretation of the V5 frozen-versus-updating contrast: freezing may beat this finite-memory update rule, but it cannot beat optimal cost-free calibrated Bayes in expected accuracy under the benchmark assumptions.

## Verification and limits

All six exact checks passed: transition probabilities normalized and stayed nonnegative (maximum error `3.33e-16`), both rules equaled `q0` at `n=0`, Bayes had no material negative value of information (roundoff at most `2.22e-16`), and the Markov distributions matched independent enumeration of all `2^10` cue paths (maximum error `8.88e-16`). Full values are in [`experiments/bayes_benchmark.json`](experiments/bayes_benchmark.json), generated by [`experiments/bayes_benchmark.py`](experiments/bayes_benchmark.py).

This is an analytical comparator, not a claim that humans or organisms update optimally. Conditional independence, calibrated priors, known cue accuracy, and a stable binary world are imposed here; the V5 population model includes ecological and cultural feedbacks absent from this calculation.


## Further work

See [proposed investigations](proposals/RESEARCH_PROPOSALS.md). They are not executed V6 results.
