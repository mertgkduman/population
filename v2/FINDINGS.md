# v2 findings — simulation data

## Mechanistic and algebraic consequences

The signed rate `g` changes adult advice error by `sigma_A(t)=clamp[sigma_A(0) exp(-g t), 0.1, 3.0]`. Positive `g` lowers error standard deviation, negative `g` raises it, and `g=0` reproduces v1. Deference enters only through the specified copying or weighted-judgment loss, then through follower mortality; there is no direct reward for deferring.

At `d=0`, drift has no demographic effect. With `k_error=0`, neither `d` nor `g` affects demography. The batched `d=0` sweep had a maximum absolute N(T) spread of 9.66×10⁻⁶ density units across drift rates, or 6.12×10⁻⁹ scaled by population size; independent single-trait solves agreed to numerical precision. This spread comes from DOP853 choosing steps for a batch that also includes drift-sensitive cells.

For helpful advice under copying with `g=-0.01`, adult MSE crosses private MSE at `t≈91.629` model time. The instantaneous effect of increasing `d` on follower mortality changes sign there. This is an algebraic prediction of the prescribed drift and loss; it is not evidence of a biological learning mechanism.

## Finite-horizon observations sensitive to assumptions

The main comparisons below use `r_T=log[N(T)/N(0)]/T` at `T=200`, not the stationary `r₀` from v1. Main sweep values use a 9×11 `(d,τ)` grid; reported optima are grid locations.

| Initial advice, policy, model | g | Growth-maximizing d | Growth-maximizing τ | Matched d=1 minus d=0 at τ≈3 |
|---|---:|---:|---:|---:|
| Helpful, copy, M0 | −0.005 | 0 | 0.5, lower boundary | −0.000060 /time |
| Helpful, copy, M0 | 0 | 1 | 0.5, lower boundary | +0.004180 /time |
| Helpful, copy, M0 | +0.005 | 1 | 0.5, lower boundary | +0.004950 /time |
| Helpful, copy, M1 | −0.005 | 0 | ≈2.187, interior grid cell | −0.000129 /time |
| Helpful, copy, M1 | 0 | 1 | ≈6.613, interior grid cell | +0.003752 /time |
| Helpful, copy, M1 | +0.005 | 1 | ≈9.564, interior grid cell | +0.004474 /time |

The 25×25 refined M0 helpful-copy maps at `g=-0.005,0,+0.005` reproduce the coarse-grid maximizing `d` and all retain **τ=0.5 as the lower boundary**. M1's interior τ behavior depends on its separately prescribed adult fecundity benefit. The M1 τ optima for finite-horizon growth cannot be compared directly with v1's low-density asymptotic r₀ optima as if they were the same quantity.

Negative drift can reverse which fixed copying coefficient performs best. For helpful advice at `g=-0.01`, d=1 at τ≈3 gives N(200)≈29.7 versus ≈1914.6 at d=0. For `g=+0.005`, the corresponding values are ≈5152.2 versus ≈1914.6. These are separate populations in matched conditions, not direct competition or evolutionary substitution.

Equal-quality and initially cloned advice are flat in d at `g=0` under their v1 null conditions. Nonzero drift changes adult variance, so the cloned preset is only identical to private information at `t=0`; it should not be called cloned throughout a drifting run. The biased scenario remains adverse under copying even when precision improves, because its fixed bias 1.5 yields adult MSE above private MSE. The `no_effect` scenario stays flat across all d and g. Noisy advice can begin harmful and become useful if positive drift crosses the MSE threshold early enough.

The sweep includes deterministic near-zero positive populations. They are not literal extinctions. No stochastic extinction probability is estimated.

## Verification and limits

The run contains 21,384 main trait trajectories, 64,152 horizon records at T=50,100,200, and 1,875 refined trait trajectories. All 19 numerical checks and 26 offline Chrome checks passed. At `g=0`, v2 trajectories match the saved v1 fixtures with maximum scaled F/A error 1.68×10⁻⁷. The browser RK4 solver's maximum scaled discrepancy from 24 SciPy DOP853 fixtures was 2.35×10⁻⁶, with maximum scaled step-halving difference 2.21×10⁻⁶, below the declared 2×10⁻⁵ acceptance threshold. The browser loaded from `file://` with HTTP(S) blocked and no console errors.

Adult advice drift is externally prescribed and shared across adults. This two-state model cannot resolve adult age, accumulated experience, learning mechanisms, teaching capacity, culture, ecological calibration, stochastic extinction, inheritance of the drift process, fixation, an ESS, or historical selection. For `g≠0`, the displayed `r_inst(t)` is a frozen-time low-density diagnostic; no single stationary equilibrium or simple invasion eigenvalue is asserted.
