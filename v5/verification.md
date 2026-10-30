# V5 verification and limits

Technical implementation: **VALIDATED within the measured scope**. The scientific claim of a distinct dogmatism adaptation remains **PARTIAL/unsupported in its strong form**.

The final suites pass: 30/30 equation and numerical checks,30/30 artifact checks,12/12 follow-up integrity checks,6/6 exact Bayesian checks,8/8 repertoire invariants,7/7 tutor-follow-up invariants and99/99 offline browser checks. These are complementary checks, not independent biological replications.

## Independent mathematics and numerical implementation

experiments/test_verification.py implements an independent Python event enumerator, separate from the Numba flux kernel. It checks private evidence transitions, social acceptance, action override, conflict-only storage, frozen/audit policies, reset and maturation, births, mortality and resource use. Exact limiting cases include d=0 preserving u=b, no truth/no information controls, no-payoff/no-cost demographic neutrality, conservative transfers, all-zero absorption, and the misinformation-versus-real-change observational-equivalence control.

| Check | Measured maximum | Tolerance / interpretation |
|---|---:|---|
| Birth–death accounting | 2.67e-15 | 2e-12 |
| Fixed-environment matrix-exponential parity | 6.55e-10 | 2e-9 scaled error |
| RK4 dt=.2 vs DOP853 | 8.69e-4 | Pilot; not used for main runs |
| RK4 dt=.1 vs DOP853 | 4.06e-5 | 7e-5 scaled tolerance; main step |
| RK4 dt=.05 vs DOP853 | 2.19e-6 | 5e-6 scaled tolerance |
| Representative self-operator residual | 2.80e-16 | 2e-9 |
| Representative self-invasion magnitude | 5.06e-16 | 2e-8 |
| Conditional survival with zero mortality | 6.67e-16 from 1 | 2e-12 |
| Dynamic invasion dt-halving | 6.75e-12 | 1e-7 rate tolerance |
| Dynamic self-relative growth | 7.16e-18 | 1e-10 |
| Refined abundance dt-halving | 5.43e-10 density | 1e-6 |

Reference integration is SciPy DOP853 with rtol=1e-11 and atol=1e-13. Scaled state error is max |computed−reference|/max(1,|reference|): absolute at densities below1 and relative above1. Step halving shows approximately fourth-order convergence. Exact environmental segment boundaries are respected. The integrator raises on nonfinite or substantively negative states; no blanket population clipping is used. Arbitrarily extreme user parameters may require a smaller step; passing representative checks is not a stability certificate for every positive tau.

## Data, evolutionary and stochastic checks

The artifact audit compares every exported main series/distribution with its NPZ source: maximum discrepancy is 5.00e-10, consistent with nine-decimal dashboard encoding. Stage distributions reconcile to stocks within 2.73e-12; minimum stored density is 0. The conditional survival metric lies in[.355923,.985222]. The main tail diagnostic uses exactly the last100 time units. Missing recovery is explicit; for scenarios without a shock it means not applicable, not evidence of failed recovery.

All candidate architectures use the same retained resident d=.5,tau=3 when displaying the primary invasion maps. Architecture self-invasion is neutral within 3.45e-15. Pairwise-map self rates are within 3.38e-9 and resident residuals within 5.09e-10. Dynamic rare-mutant rates use shared resident trajectories; they are not frozen-eigenvalue averages. Explicit competition frequencies are nonnegative and sum to1. Small deterministic frequencies are not labeled literal extinction. Local selection roots and their primary-versus-expanded trait domains are checked separately from abundance optima.

The12/12 follow-up checks cover refined abundance convergence, selection-root bracketing and domain labels, long-replacement mass/frequency accounting and rare initial frequency, full-precision dynamic convergence, and companion verification status. The tiny convergence differences are stored in full precision rather than rounded to zero.

Repertoire experiments use common random numbers for matched traits and verify retained private ledgers, founder acquisition rather than granted wisdom, cue-quality matching, pre-shock pairing, score bounds and query policies. The tutor follow-up uses new seeds and selects only observable |b|>=2, never true correctness. Its extra search is cost-free and increases availability; that limitation is part of the reported result. Across-seed deviations and across-history intervals represent those stochastic designs only, not empirical uncertainty or demographic stochasticity.

The exact Bayesian benchmark checks normalization, initial accuracy, monotonic expected value of additional valid information, the prior floor, and independent path enumeration. Maximum enumeration discrepancy is 8.89e-16. Its sixth check records the bounded-score counterexample. It does not validate a realistic omniscient organism or establish Bayes optimality in changing, correlated or costly environments.

## Offline dashboard

Chrome for Testing 154.0.8037.92 opened the actual HTML through file:// with HTTP(S) blocked. All 99 browser assertions pass, with **zero console errors and zero remote requests**. Checks cover the 50 contexts, all main dimensions, actual Plotly axis titles and logarithmic tau ticks, matched retained-private comparison, pins, heatmap clicks, synchronized animation/scrubbing, population and confidence distributions, source/query units, mechanisms, access maps, repertoire and tutor uncertainty, Bayesian curves, shared-culture selection and actual long replacement, exports and mobile layout. Screenshots were visually inspected.

The builder losslessly deduplicates inactive oracle rows and the browser reconstructs them; export parity is verified. Scientific values are not rounded further by this optimization. The self-contained HTML remains large because it includes all data and Plotly. Offline operation was tested in this Chrome build; all browsers and every possible downloadable image format were not certified. A modern browser with native gzip decompression support is required.

## Investigation corrections and scientific limits

The pilot exposed Numba incompatibilities with boolean casts and repeat(axis); explicit equivalent operations fixed them. Distribution-sensitive convergence favored dt=.1 over the initial .2 pilot. An unused supplementary tail-growth field had inconsistent windows across output grids; it was removed from supplementary exports, while the main last100 metric is independently checked. A final visual audit also corrected slider positions after heatmap selection, with a dedicated synchronization assertion. Actual historical failure logs are retained alongside final passing reports.

The independent review also changed the design before main runs: private learners retain knowledge; action override and memory acceptance are separated; load is labeled an exposure-rate transformation; freezing and auditing are imposed policies. Later confidence-tutor, Bayesian and cost/memory tests are explicitly exploratory, not retroactively preregistered confirmations.

GSD009 and011 are VALIDATED for their executable information-access/selection questions;010 is PARTIAL for the stronger conviction/dogmatism interpretation. Semantic causal complexity, source genealogy, costly teacher search, normative cooperation, psychological dogmatism, real genetic separability and historical adaptation remain outside what these checks establish.
