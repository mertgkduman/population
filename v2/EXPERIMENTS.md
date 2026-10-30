# Predeclared v2 experiment matrix and checks

The adult advice error standard deviation is prescribed externally as `sigma_A(t) = clamp(sigma_A(0) exp(-g t), sigma_floor, sigma_ceiling)`. Positive `g` improves precision; negative `g` decays it. The bias and correlation stay fixed. `g` does not directly affect births or deaths. All adults provide advice from the same time-dependent distribution. This is a population-wide quality drift, not an adult-age or cultural-learning model.

The two demographic ODEs remain `F'=beta(N,tau) A-(1/tau+mu_F(d,t))F`, `A'=F/tau-mu_A A`; `mu_F(d,t)=mu_F_base+k_error L(d,t)`. M0 and M1 retain their v1 definitions. For `g != 0`, the system is nonautonomous: no single stationary r0 or N* is reported. The dashboard instead shows a **frozen-time low-density eigenvalue** `r_inst(t)` and finite-horizon outcomes. A positive instantaneous eigenvalue is not a time-varying invasion proof.

## Main matrix

- Six labeled initial advice scenarios, two policies, two maturation models, nine signed drift rates, nine d values, and eleven logarithmic tau values: **21,384 independent trait trajectories** at T=200.
- Outcomes at T=50,100,200 from those same integrations: **64,152 horizon records**.
- The only varying traits within a scenario/policy/model/drift-rate/horizon sweep are d and tau. Cross-rate comparisons deliberately change g and must be labeled as such.
- Refined 25×25 maps at g=-0.005,0,+0.005 for helpful-advice M0 copying: 1,875 additional trajectories to inspect coarse-grid sensitivity.

## Given/When/Then checks recorded before execution

1. Given g=0, when v2 is run with v1 parameters, then losses, instantaneous r0, and trajectories match v1.
2. Given d=0, when g changes, then trajectories are unchanged within a scenario/model/policy.
3. Given k_error=0, when d and g vary, then demographic trajectories are unchanged at fixed tau/model.
4. Given g>0 or g<0, when time advances, then sigma_A respectively decreases or increases until a declared bound is reached.
5. Given copying and a drift that crosses adult/private MSE equality, when d changes, then the instantaneous mortality effect changes sign at the predicted crossing.
6. Given both policies and models at signed drift extremes, when RK4 and DOP853 are compared, then errors and step halving stay within declared tolerances.
7. Given the batched 21,384-trait sweep, when representative cells are solved individually, then batched and individual DOP853 outcomes agree.
8. Given invalid bounds, drift, tau, or d, when validated, then inputs are rejected; all-zero remains absorbing; computed populations are nonnegative.
9. Given the offline HTML, when controls, signed drift, map selection, matched comparisons, export, and responsive layout are exercised, then results or unavailable browser tests are recorded.
