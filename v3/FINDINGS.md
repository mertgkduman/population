# v3 findings: declining copying and a rising adult advice feature

Run `20261030T022304Z`. All quantities are **simulation data** in arbitrary model time and population-density units. The finite-horizon outcome below is `r_200 = log(N(200)/N(0))/200`, measured from `F(0)=80`, `A(0)=20`. Matched contrasts compare `d0=1` with `d0=0` at the same `tau`, scenario, policy, maturation model, and mechanism rates. The tabulated tau is the grid point nearest 3 (`3.1623`). These are independent populations, not competitors or rare-mutant invasion tests.

## What the experiment found

| Advice and policy, M0 | Deference decay λd | Feature growth λQ | Matched Δr200 at tau≈3.16 | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Helpful, copying | 0 | 0 | +0.004180 | Accurate copied advice reduces follower mortality. |
| Helpful, copying | 0.005 | 0.005 | +0.001836 | Benefit survives, but wanes as copying declines. |
| Helpful, copying | 0.020 | 0 | +0.000110 | Fast deference loss almost removes the advantage. |
| Helpful, copying | 0 | 0.020 | +0.004988 | Improving advice raises the advantage if copying persists. |
| Noisy, copying | 0 | 0 | −0.044272 | Initially poor advice makes copying harmful. |
| Noisy, copying | 0.005 | 0.005 | +0.000301 | Rising quality can reverse the finite-horizon sign. |
| Noisy, copying | 0.020 | 0 | −0.000432 | Deference decay alone shrinks, but does not reverse, harm. |
| Noisy, copying | 0 | 0.020 | +0.002605 | Rapid improvement makes copying beneficial over this horizon. |
| Biased, copying | 0.005 | 0.005 | −0.002630 | The persistent bias keeps copying harmful. |
| No error consequence, copying | 0.005 | 0.005 | 0 | Decision errors have no demographic payoff when `k_error=0`. |

The noisy copying reversal is mechanism dependent. For this scenario `sigma_A(0)=2`, `Q0=0`, and `Qmax=2`; its adult mean squared error falls below private mean squared error only after `Q(t)>1`. At `λQ=0.01`, that threshold is `t=ln(2)/0.01=69.3147` model time. Crossing the instantaneous accuracy threshold does not by itself guarantee a positive finite-horizon contrast; earlier damage and the level of remaining copying both matter.

With **equal-quality independent** advice and no quality growth, random copying is exactly flat in `d0`; the 21 tied deference values at the M0 growth-maximizing tau are a range, not a unique optimum. Weighted judgment at the same rates has an interior optimum at `d0=0.5`, because averaging independent signals lowers variance. This is an information-pooling effect, not evidence for an authority preference. When quality later improves, the equal-quality copying contrast becomes positive. The no-error-consequence scenario remains flat across all 98 policy-model-rate contexts (two policies, two maturation models, 49 rate pairs).

Across the 98 copying contexts per scenario (the two maturation assumptions and 49 rate pairs), the matched `d0=1` contrast at tau≈3.16 is positive in all 98 helpful contexts, positive in 70 and negative in 28 noisy contexts, negative in all 98 biased contexts, and zero in all 98 no-error-consequence contexts. This is a tally over predeclared parameter settings, not a statistical test or estimate about nature.

The M0 growth-maximizing tau is always the lower grid boundary, `0.5`, in all 49 rate pairs per scenario and policy. Its optimum reflects the absence of a preparation benefit. In M1, the added hypothetical fecundity benefit produces interior optima for these settings: helpful copying with both rates zero has tau≈`5.499`; with `λd=λQ=0.005`, tau≈`3.162`; with `λd=0, λQ=0.020`, tau≈`7.953`; and with `λd=0.020, λQ=0`, tau≈`2.630`. Thus the maturation optimum is sensitive to the prescribed preparation and time-change assumptions. The 41×41 refinement was run for 32 selected contexts; its maximum was at least the coarse maximum within `1.14×10^-12` numerical discrepancy.

## Mathematical consequences and limits

The signs of the instantaneous copying effect follow directly from `L_copy=(1-d) sigma_I²+d(sigma_A²+bias_A²)` and `mu_F=mu_F_base+k_error L`. In the biased preset, `bias_A²=2.25>sigma_I²=1`, so even perfect removal of adult noise cannot make copying accuracy-beneficial. When `d0=d_floor=0`, changes in adult quality are demographically invisible; when `k_error=0`, both time-varying mechanisms are demographically invisible. These are algebraic consequences of the defined mechanism, not biological discoveries.

There are still exactly two demographic ODE states, `F` and `A`. Both `d(t)` and `Q(t)` depend on calendar model time, not on an individual's age or learning history. Consequently the model has no stationary long-run equilibrium while those functions change and does not define a stationary rare-mutant invasion fitness for nonzero rates. The displayed frozen-time eigenvalue is an instantaneous diagnostic; the reported `r_T` is finite-horizon growth, not selection in a resident population. Nothing here determines whether deference and cognition can vary independently in organisms, how adult expertise arises, whether copying behavior evolves, or whether a prolonged childhood was historically selected.

## Verification

The predeclared scientific checks and numerical comparisons passed: 22 checks in `verification.json`. The browser RK4 implementation was compared with 64 SciPy DOP853 reference trajectories, including extreme rate settings, both policies, and both maturation models; maximum scaled state error was `4.58×10^-7` and step-halving difference was `3.61×10^-7`, both below the declared `2×10^-5` tolerance. The offline Chrome dashboard test passed 28 checks recorded in `browser_verification.json`, with no HTTP requests or console errors. See `run_manifest.json` for solver settings, dependency versions, and hashes.

**Technical verdict: VALIDATED** for the implemented v3 mechanism and checks. This verdict does not validate an evolutionary adaptation or empirical account of any species.
