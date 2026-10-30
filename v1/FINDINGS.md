# Findings — simulation data, not empirical estimates

## Mathematical consequences of the specified equations

- Under copying, loss is affine in d. Helpful adult advice (adult MSE 0.16 versus private MSE 1) lowers follower mortality from 0.330 at d=0 to 0.078 at d=1. Noisy advice (adult MSE 4) raises it from 0.330 to 1.230. These directions follow algebraically from the loss and mortality equations.
- Equal-MSE advice under copying is flat in d. Cloned advice is flat under both policies. With k_error=0, d has no demographic effect. At d=0, adult moments do not matter. These nulls are preserved, not assigned a preferred d.
- Independent equal-quality signals under weighted judgment have loss 0.5 at d=0.5 versus loss 1 at either endpoint. This is information pooling, not an advantage of literal obedience or adult authority.
- In M0, the helpful-advice copying r0 maximum on the specified domain is d=1, τ=0.5, r0≈0.34521 per model time. **τ=0.5 is the lower grid boundary.** The model includes waiting costs but no preparation benefit, so this is not evidence for prolonged childhood. All d values at τ=0.5 tie in the equal-MSE copying case.
- The deterministic equilibrium N* is abundance, not growth. The near-threshold test has r0≈1.17×10⁻⁶, N*=0.0200, yet N(200)≈41.49; a T=200 trajectory does not establish equilibration there.

## Results sensitive to the prescribed assumptions

- In M1, the helpful-advice copying grid maximum is d=1, τ≈2.6296, r0≈0.22021. This τ is interior to the specified grid because M1 prescribes a saturating adult fecundity benefit. At fixed d=0, the M1 grid maximum is τ≈2.0563; at d=0.5 it is τ≈2.3254. Lower follower mortality shifts the M1 growth-maximizing τ upward under these defaults. The tradeoff was specified before execution and not fitted to produce this result.
- In the noisy and biased copying presets, adult MSE exceeds private MSE, so deference reduces growth in matched within-scenario comparisons. In the noisy M0 grid, the maximum is d=0, τ=0.5. Adult advice quality is externally fixed within every sweep.
- Positive conditional rare-mutant invasion rates mean initial growth at the pinned resident equilibrium under perfect trait inheritance, rarity, shared resources, and fixed advice. They do not show fixation, an ESS, or historical evolution.

## What this model cannot answer

The spike does not estimate any human or animal parameters, establish biological separability of deference from cognition, explain how adults gained expertise, model teacher capacity, track cultural knowledge, represent age at a fixed birthday, estimate stochastic extinction, or demonstrate historical selection for childhood or obedience.

## Verification summary

See `verification.json` and `browser_verification.json` for measured pass/fail records. SciPy DOP853 uses rtol=1e-10 and atol=1e-12. The same `science.js` file bundled in the page was run in Node and in offline Chrome against 12 SciPy trajectory fixtures across both policies and maturation models, including d endpoints and τ extremes. RK4 max step is 0.05 model time; Chrome's max absolute F/A discrepancy was ≈8.52×10⁻⁵ density units, max scaled discrepancy ≈2.35×10⁻⁶ using denominator max(1, |reference state|), and max scaled step-halving difference ≈2.21×10⁻⁶. The predeclared acceptance tolerance was 2×10⁻⁵ for scaled errors. Analytic JS/Python fixture discrepancy was zero at recorded precision. All 24 browser checks passed in Chrome with HTTP(S) blocked.

These are deterministic numerical checks. They do not use p-values or confidence intervals.
