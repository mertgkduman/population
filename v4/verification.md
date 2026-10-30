# V4 verification

Technical implementation status: **VALIDATED within the tested scope**. Scientific conclusion: **PARTIAL**—endogenous cultural learning and selection are demonstrated under explicit assumptions; a distinct evolutionary adaptation for dogmatic childhood deference is not established.

The final machine-readable suites pass **28/28 numerical checks**, **103/103 artifact consistency checks**, and **45/45 offline browser checks**. These are complementary checks, not independent scientific replications. See experiments/verification.json, experiments/artifact_verification.json and browser_verification.json. project_manifest.json hashes the final sources and outputs. The archive also receives ZIP CRC verification.

## Predeclared tests and measured evidence

Given/When/Then hypotheses were recorded in evidence/predeclared_experiments.json, research_questions.md and the five numbered GSD records before broad sweeps. A preliminary three-trait feasibility pilot preceded that record and was used for runtime/positivity, not model tuning. The predeclared DOP853 tolerances were 1e-10/1e-12; final verification tightened them to rtol=1e-11, atol=1e-13.

| Given / when | Then / measured result |
|---|---|
| Equal exogenous private/adult accuracy; vary fixed d | Entire generator unchanged, discrepancy zero |
| Fixed source accuracy; vary conflict choice | p+d(q−p) exactly matches enumerated events |
| No correctness-linked vital-rate effects; vary d | Demographic difference ≤2.84e-13; cultural states can differ |
| Maturation and cognitive transfers only | Density conserved to 2.22e-16; pure-maturation trajectory error 9.78e-8 against a 2e-7 limit |
| General births, deaths and transfers | Sum of derivatives equals B−D to 2.66e-15 |
| Maturation with retained versus reset scores | State-preserving and neutral-state routing match exactly |
| Oracle encounters anti-informative advice | Its explicit inversion/reliability rule matches enumerated events |
| RL receives objective outcome feedback | Trust routing matches enumerated Bernoulli events |
| Externally fixed cultural/resource environment | RK4 matches matrix exponential; maximum scaled error 3.10e-10 |
| Main RK4 dt=.1 versus DOP853 | Maximum scaled error 1.405e-5, below 2e-5 tolerance |
| Halve RK4 step to .05 | Maximum scaled error 7.92e-7, below 2e-6 tolerance |
| Resident tested against itself | Operator residual ≤8.19e-14; eigenvalue magnitude ≤3.02e-13 in representative cases |
| Perturb resource for self-invasion control | Rate becomes nonzero, demonstrating a nontrivial check |
| Absorbing all-zero population | Derivative exactly zero |
| Invalid ranges or nonfinite parameters | All 18 specified invalid configurations rejected |
| Corrected conditional maturation survival | All policies stay in [0,1]; fixed d=0/1 equal exact competing-risk expressions |
| RL survival with no feedback or no mortality | Reduces to neutral-trust scalar expression, or exactly one |
| RL survival versus independent killed-trust transient integration | Combined error including residual tail 1.13e-16 |

The trajectory error scale is max_i |numerical_i−reference_i|/max(1,|reference_i|): absolute below unit density and relative above it. It is not an unqualified relative error for tiny states. Tests cover fixed and RL generators, extreme and intermediate traits, and explicit limiting cases. The RK4 implementation raises on nonfinite populations or values below −1e-9; it does not apply blanket clipping. Primary sampled generator graphs are irreducible and off-diagonal entries are nonnegative. Passing these finite tests does not certify arbitrary user-specified rates or step sizes.

## Additional evolutionary and data checks

- Dynamic invasion uses a shared resident path, normalized mutant states and accumulated log growth; no separate mutant teacher population. Step halving changes measured rates by at most 8.18e-12. Self relative growth is about 2.1e-18.
- Next-generation reproduction signs agree with independent dominant-eigenvalue signs; resident R0 is one. Explicit zero-mutation replacement corroborates the positive invasion example.
- Every plotted series is compared with the corresponding saved NPZ array. Eight-decimal export discrepancies stay below 6e-9. All 30 contexts have stage accounting and finite-horizon growth parity checks. Corrected survival uses full-precision NPZ trait values and has separate probability/parity checks.
- All 9,690 displayed grid rows are represented in sweep.csv. Comparator d duplicates are labeled inactive and are not counted as independent trajectories.
- All resident environments used for stationary maps meet the explicit residual and self-invasion tolerances. A finite T alone is never an equilibrium criterion.
- Forty environmental histories include 20 held-out confirmatory seeds. Uncertainty describes variation across histories, not demographic stochasticity or parameter-estimation uncertainty. A separate six-seed-per-rate experiment tests volatility with shared histories across traits.
- Erlang L=1 matches the exponential-stage implementation. L=4 is a robustness scenario, not the main two-stage model or a deterministic maturation birthday. Its supplementary absolute-.75 recovery measure differs from the main baseline-relative recovery metric.

## Corrections preserved in the investigation trail

The adversarial process corrected parameter nonfiniteness acceptance, equilibrium residual timing, private-source sampling labels, recovery-baseline confounding, and overly strong coarse-grid optimum interpretations. Oracle information access and the limitations of the finite RL comparator are explicitly disclosed. A no-truth control removes both informative signals and correctness-linked demographic filtering; removing only informative private signals leaves an indirect truth channel.

A final probability audit discovered that coarse 5-unit trapezoidal integration could yield survival above one. That derived quantity was invalid. It was replaced by exact conditional survival with final advice held fixed, using a transient trust operator for RL. experiments/correct_survival.py regenerates every affected map/export; postprocess.py invokes it on reproduction. The dashboard and mathematical model describe the conditional interpretation. No population trajectory, growth, invasion, selection gradient or reported optimum used the discarded metric. Five new independent numerical checks and 31 artifact checks guard the correction.

## Browser and offline checks

Chrome for Testing 154.0.8037.92 opens the single HTML using file:// with HTTP and HTTPS blocked. The final 45 checks pass with **zero console errors and zero remote requests**. Tests exercise gzip/Plotly loading, all model/scenario contexts, logarithmic tau axis, populated plots, three pins, heatmap selection, synchronized scrub/play/pause/reset, inactive comparator axes, missing invalid invasion maps, selection/refinement/replacement displays, stochastic and volatility evidence, survival labeling, and desktop/mobile layout. Screenshots were inspected.

Seven JSON/CSV export actions were captured and checked for nonempty data and run identifiers. Plot-image download control availability was checked; the harness does not validate every exported image file. Offline verification is for this Chrome build, not every browser. A modern browser with native gzip DecompressionStream support is required. The interface selects precomputed simulations; it does not silently solve new equations or claim that animating time changes an asymptotic map.

## GSD verdicts

| Spike | Verdict | Scope |
|---|---|---|
| 004 conflict-null | VALIDATED | Analytical identities and demographic limits |
| 005 endogenous-memory | PARTIAL | Retained cultural confidence, not proof of adult dogmatism |
| 006 shock-recovery | VALIDATED | Conditional recovery measurements and counterexamples |
| 007 shared-culture-invasion | VALIDATED | Correct rare-mutant treatment and explicit competition, not an ESS proof |
| 008 feedback-and-history | PARTIAL | Replication/ablations complete; specialized superiority and bistability unsupported |

Unimplemented scope is recorded, not passed: normative cooperation games, sanctions, parent–offspring conflict, second-order beliefs, source genealogy/correlation, realistic sequential Bayesian inference, broad RL-architecture competition, empirical calibration and historical adaptation inference.
