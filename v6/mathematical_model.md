# V6 · Developmental plasticity and stochastic environmental change

V6 extends V5's retained private evidence and held convictions. All rates and population units are hypothetical. The adult reduction in plasticity is an imposed mechanism, not an evolved result.

## States, learning and inheritance

For inherited traits $g=(d,\tau)$, the juvenile and adult densities are $F_g(u,b)$ and $A_g(u,b)$, with private evidence $u$ and held conviction $b$ on the integers from $-H$ to $H$. Default $H=3$. These are cognitive substates of exactly two demographic stages. Births enter $(u,b)=(0,0)$; maturation transfers both ledgers unchanged, irreversibly, at rate $m=1/\tau$. Offspring inherit their parent's trait pair; there is no mutation in the present isolated runs or rare-mutant analysis.

Private cues have the same accuracy $p=0.65$, exposure rate $\nu_F=\nu_A=1$, and memory capacity at every age and trait pair. A cue is encoded with probability $\eta_F=1$ in juveniles and $\eta_A\in\{0,0.1,1\}$ in adults. Thus the successful private-update hazards are

$$
\lambda_F=\eta_F\nu_F\frac{\mathrm{access}}{\mathrm{load}},
\qquad
\lambda_A=\eta_A\nu_A\frac{\mathrm{access}}{\mathrm{load}}.
$$

A successful private cue shifts both ledgers one signed step, clipped only at the declared memory boundaries. Failure to encode leaves the state unchanged. This probability thinning is mathematically equivalent to a reduced private update rate in this model; it does not establish a biological distinction between attention, access and plasticity. Exposure costs, if enabled, are charged on the unthinned cue rate. Default query cost is zero to isolate accuracy consequences.

Adults advise according to their held conviction. Define

$$
j(z)=\frac{1+\operatorname{sgn}(z)}{2},
\qquad
q_+=\varepsilon+(1-2\varepsilon)
\frac{\sum_{g,u,b}A_g(u,b)j(b)}{\sum_{g,u,b}A_g(u,b)}.
$$

Neutral scores choose each sign with equal probability. With no adults, advice is unavailable. A juvenile's public positive action probability is

$$
a_+(u)=(1-d)j(u)+dq_+.
$$

Accepted testimony, at rate $d\nu_S/\mathrm{load}$, shifts only $b$. This retains V5's bundled action substitution and memory acceptance; it is not a clean identification of conflict-only deference. Adults express $j(b)$ and do not express juvenile deference. With $\eta_A=0$, an adult retains its state after maturation, but culture can still change through adult death and juvenile recruitment.

## Random environment

Truth $\theta(t)\in\{-1,+1\}$ switches sign at the jump times of a homogeneous Poisson process:

$$
\Pr\{\theta(t+h)=-\theta(t)\mid\theta(t)\}
=\kappa h+o(h),
\qquad
\Delta t\sim\operatorname{Exponential}(\kappa).
$$

$\kappa$ has units of inverse model time. Zero means a fixed environment. The private cue's probability of a positive sign is

$$
\pi_I(t)=\frac{1+\theta(t)(2p-1)}{2}.
$$

For every positive hazard, the environment's stationary probabilities are one half for each truth sign. Its persistence changes with the hazard:

$$
\mathbb E[\theta(t)\theta(0)]=e^{-2\kappa t}.
$$

Thus comparisons across positive hazards change temporal predictability, not the long-run fraction of positive truths.

Every matched population and the rare mutants share the same event times within a seed. Events change truth and the private cue channel together. This is environmental randomness only; cultural transitions and demography are conditional deterministic density equations. No finite-population extinction is simulated.

## Demography

Let $c_\theta(b)=[1+\theta\operatorname{sgn}(b)]/2$ and let $c_F(u)$ be the probability that the juvenile public action is correct. Conservative learning generators $Q_F(q_+,\theta)$ and $Q_A(\theta)$ implement the transitions above. With column-state convention,

$$
\dot F_g=
\left[Q_F-\operatorname{diag}(m+\mu_F)\right]F_g
+e_{00}\sum_{u,b}\beta(b,N)A_g(u,b),
$$

$$
\dot A_g=
\left[Q_A-\operatorname{diag}(\mu_A)\right]A_g+mF_g.
$$

The payoff and resource rules are inherited from V5:

$$
\begin{aligned}
\mu_F(u)&=\mu_{F,0}+k_F[1-c_F(u)],\\
\mu_A(b)&=\mu_{A,0}+k_A[1-c_\theta(b)],\\
\beta(b,N)&=[\beta_0+\beta_{\mathrm{skill}}c_\theta(b)]
\frac{S(N)}{K_S+S(N)},\\
S(N)&=\frac{S_0}{1+N/K}.
\end{aligned}
$$

The displayed equations use the default zero query cost. The source supports the V5 additional query-hazard terms. No direct reward is given to deference, delayed maturation or rigidity. The stage totals satisfy

$$
\dot F=B-M-D_F,\qquad
\dot A=M-D_A,\qquad
\dot N=B-D_F-D_A.
$$

## Fixed equilibria versus stochastic regimes

When $\kappa=0$, a fixed equilibrium must satisfy the full demographic-cultural residual, not just a near-flat total population. Reversing both truth and all score signs leaves the equations unchanged: the two fixed environments have mirrored belief distributions and equal abundance equilibria under symmetric initial conditions. Unequal carrying capacities are not inserted to manufacture a difference.

For $\kappa>0$, trajectories continue to fluctuate. We estimate finite-window, post-burn-in summaries and distributions:

$$
\bar N=\frac{1}{T-t_b}\int_{t_b}^T N(t)\,dt,
\qquad
r_T=\frac{\log[N(T)/N(0)]}{T}.
$$

Neither is automatically an invariant distribution or a long-run evolutionary fitness. Eight independent environmental seeds provide path SD and Monte Carlo SE; deterministic cases have no sampling uncertainty. Recovery measures first sampled adult accuracy of at least $0.75$ after a flip, before the next flip. Unresolved events are censored; success fractions are reported separately. The sampling interval is four model-time units.

## Conditional rare-mutant growth

A resident with $d_r=0.5,\tau_r=3$ supplies the resource and adult advice environment. Mutants do not affect either. At every Runge–Kutta stage, integrate

$$
\dot x_m=G_m[N_r(t),q_r(t),\theta(t)]x_m.
$$

After periodic normalization, accumulate log abundance and calculate

$$
s_m=\frac{\log\|x_m(T)\|_1-\log\|x_m(t_b)\|_1}{T-t_b},
\qquad
s_{\mathrm{relative}}=s_m-
\frac{\log[N_r(T)/N_r(t_b)]}{T-t_b}.
$$

The dashboard distinguishes absolute and resident-relative invasion growth. The self-mutant's relative rate is zero up to numerical error. In a stochastic finite window the resident's absolute rate need not be zero. Positive values do not demonstrate fixation, an ESS, or a historical adaptation.

## Scope

Private signal accuracy is held fixed, but stage-specific updating is prescribed. Finite bounded scores can misweight correlated or unequal evidence. Adults do not independently choose their plasticity, and Bayesian trust calibration is not solved here. The extension can show conditional cultural retention/adaptation tradeoffs, not that childhood dogmatism is a distinct evolved mechanism. Differences across environmental hazards concern stochastic responses; stable environments can yield identical abundance with different cultural signs.
