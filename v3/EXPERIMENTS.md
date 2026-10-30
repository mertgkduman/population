# Predeclared v3 mechanism, experiment matrix, and checks

## Interpretation fixed before running

The **copied feature** is a dimensionless adult advice-quality feature `Q_A(t)`. It rises monotonically with calendar model time:

`Q_A(t)=Q0+(Q_max-Q0)(1-exp(-lambda_Q t))`, with `lambda_Q≥0` and `Q_max≥Q0`.

Its specified effect on the adult advice error standard deviation is

`sigma_A(t)=sigma_A0 (1+Q0)/(1+Q_A(t))`.

Follower copying propensity falls monotonically with calendar model time:

`d(t)=d_floor+(d0-d_floor)exp(-lambda_d t)`, with `lambda_d≥0` and `0≤d_floor≤d0≤1`.

Under copying, `d(t)` is the probability of substituting adult judgment for private judgment. Under weighted judgment it is the compromise weight. Both policies retain the v1 moment-based expected loss formulas with `d(t)` and `sigma_A(t)` substituted. `mu_F(t)=mu_F_base+k_error L(t)`. There is no direct reward for `d`, `Q`, or their rates. All adults provide advice from the same prescribed distribution; `Q` is not an extra ODE state and does not track individual adult age or acquired knowledge.

The demographic ODEs are still exactly `F'=beta(N,tau)A-(1/tau+mu_F(t))F` and `A'=F/tau-mu_A A`. M0 and M1 retain their v1 definitions. When both rates are zero, the model reduces to v1. With changing `d` or `Q`, finite-horizon growth `r_T` is the primary comparison; `r_inst(t)` is a frozen-time diagnostic only.

## Main matrix

- Five initial advice scenarios, two policies, two maturation assumptions, seven deference-decay rates, seven feature-growth rates, 21 initial-deference values, and 21 log-spaced maturation times: **432,180 independent trait trajectories**.
- Outcomes at T=50,100,200 from the same solutions: **1,296,540 horizon records**.
- Within each scenario/policy/model/rate-pair/horizon slice, only `d0` and `tau` vary. Cross-rate comparisons are labeled as mechanism comparisons.
- A 41×41 refinement for selected helpful/noisy, M0/M1, copy/blend rate pairs will check the main 21×21 grid's optima.

## Given/When/Then checks recorded before execution

1. Given both rates zero, when v3 matches v1 parameters, then loss, trajectories, and low-density eigenvalues match v1.
2. Given nonnegative rates and valid bounds, when time advances, then `d(t)` never increases, `Q(t)` never decreases, and `sigma_A(t)` never increases.
3. Given `d0=0` and `d_floor=0`, when feature growth changes, then demographic outputs remain unchanged.
4. Given `k_error=0`, when `d0`, decay, and feature growth vary, then demography remains unchanged.
5. Given copying with biased advice whose bias alone exceeds private RMSE, when quality grows, then deference remains accuracy-harmful.
6. Given initially noisy advice, when Q crosses the adult/private MSE threshold, then the instantaneous copying-mortality effect changes sign; the time and any finite-horizon advantage are measured separately.
7. Given extreme rate pairs, both policies, and M0/M1, when browser RK4 is compared with SciPy DOP853 and the step is halved, then scaled errors meet declared tolerances.
8. Given batched sweeps, when representative cells are solved individually, then batched and individual DOP853 results agree.
9. Given zero births and deaths, when maturation proceeds, then N is conserved and F/A match the exponential closed form.
10. Given invalid parameters, the all-zero state, and near-zero populations, when solved, then invalid values fail, nonnegativity and absorption hold, and no deterministic small population is labeled literally extinct.
11. Given the offline dashboard, when controls, animation, two heatmaps, 3D surface, rate comparisons, exports, resize, and console are exercised, then working behavior or unavailable tests are recorded.
