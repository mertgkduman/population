# V6 situational-advice results

Run `v6-local-20261030T212739Z`. Adult local-cue accuracies .55,.70,.85 are all worse than the juvenile local-cue accuracy .90. Global private-cue accuracy remains .65; juvenile/adult encoding remains1/.1. Main analysis: 9,504 isolated and 9,504 shared-resident mutant trajectories. Dense held-out tests add6,336 population trajectories at τ=3,33 d values and16 new paths. Five ablations add1,320 population trajectories. This is hypothetical mechanistic simulation data.

## Did an interior deference optimum appear?

**No interior optimum was observed** in the main mean-abundance grid, its fixed-τ slices, or the33-value held-out deference sweeps at τ=3. Conditional invasion maxima were also at endpoints. This is a numerical finding for the tested mechanism/domain, not a proof that intermediate deference is impossible. Adult information noise changes which boundary is favored; it does not automatically create a middle optimum.

| Adult local-cue accuracy | Environmental κ | Best abundance d | Best abundance τ | Mean N at grid maximum | Best invasion d | Best invasion τ |
|---|---|---|---|---|---|---|
| 0.55 | 0.0 | 0 | 0.6871 | 4504.242 | 0 | 0.5 |
| 0.55 | 0.01 | 0 | 0.5 | 4311.714 | 0 | 0.5 |
| 0.55 | 0.05 | 0 | 0.5 | 3781.722 | 0 | 0.5 |
| 0.55 | 0.2 | 0 | 0.5 | 3282.119 | 0 | 0.5 |
| 0.7 | 0.0 | 1 | 0.5 | 4592.460 | 1 | 0.5 |
| 0.7 | 0.01 | 1 | 0.5 | 4376.785 | 1 | 0.5 |
| 0.7 | 0.05 | 1 | 0.5 | 3791.618 | 1 | 0.5 |
| 0.7 | 0.2 | 0 | 0.5 | 3282.119 | 0 | 0.5 |
| 0.85 | 0.0 | 1 | 0.9441 | 4807.262 | 1 | 0.6871 |
| 0.85 | 0.01 | 1 | 0.6871 | 4502.733 | 1 | 0.5 |
| 0.85 | 0.05 | 1 | 0.5 | 3845.283 | 1 | 0.5 |
| 0.85 | 0.2 | 1 | 0.5 | 3284.659 | 1 | 0.5 |

τ=.5 and d=0 or1 are grid boundaries. Intermediate maturation times in this table are sampled optima, not exact optimized ages. Abundance is a post-burn-in average over times200–600; it is not a selection coefficient. Conditional invasion is relative to a common resident d=.5,τ=3, with the same local-cue parameters, teachers, resources and environmental path.

## Fixed maturation: dense independent validation at τ=3

| Adult local precision | κ=0 | κ=.01 | κ=.05 | κ=.2 |
|---|---|---|---|---|
| 0.55 | 0.0 | 0.0 | 0.0 | 0.0 |
| 0.7 | 0.0 | 0.0 | 0.0 | 0.0 |
| 0.85 | 1.0 | 1.0 | 0.0 | 0.0 |

The table gives the best d on the33-value grid, using16 environmental histories. Very noisy advice is rejected throughout. With adult local precision.85, copying is favored in stable/slow environments at τ=3 but rejected under faster change. With.70 precision, copying can maximize abundance at very short maturation times while rejection is better at τ=3. Thus following adults is not a situation-invariant optimum. Monte Carlo SE is retained for every curve; nearby strategies should not be treated as confidently ordered solely by the numerical maximum.

## Why adding noise did not produce a middle optimum

The fixed-source copying null has affine accuracy: P(d)=(1−d)P_I+d P_A. Universally poorer final advice favors d=0; equal accuracies give neutrality. Adults in the full model have a poorer local sensor but can still have more accurate general knowledge, so their final advice need not always be worse. A state-dependent policy is different from one intermediate copying probability applied everywhere.

The additional cultural memory mechanism was tested rather than hidden: stored situational recommendations must be interpreted through the juvenile context cue. Its error probability is derived by enumerating both observation channels. It is not an arbitrary penalty assigned to d.

## Mechanism ablations at adult local precision.70 and τ=3

| Architecture | Best d, stable | Best d, κ=.2 |
|---|---|---|
| full | 0.0 | 0.0 |
| clean_fact | 1.0 | 0.0 |
| action_only | 0.0 | 0.0 |
| memory_only | 1.0 | 0.0 |
| equal_context | 1.0 | 0.0 |

The equal-context control sets adult local precision to.90. In the stable case, clean explicit factual teaching favors d=1 while the full interpreted-advice model favors d=0. Action-only substitution favors rejection; memory-only acceptance favors copying. The transmission format and bundling of immediate action with knowledge storage materially affect the conclusion. These controls do not establish a distinctive adaptation for dogmatic authority.

## Numerical and interpretive limits

Private ability, local-cue quality and demographic constants are fixed within each scenario. d=0 demographic invariance to adult local precision, exact observation-channel enumeration, flux accounting, state-preserving maturation, matrix limits, self-neutrality and DOP853/step-halving are verified. All newborns are neutral; adults retain learned ledgers. Adult rigidity remains specified.

Main map averages use4-unit observations. An initial20-unit held-out observation interval differed by16.11 density units in a stress check, so all dense held-out averages were recomputed at4-unit resolution using the same core integrator. The original miss and coarse results are preserved. UI curves display every second saved observation (8 units), preserving exact sampled values; the full4-unit raw histories remain in the repository. Poisson events are exact integration boundaries, independent of display spacing.

Different environmental hazards generate fluctuating regimes, not proven stationary equilibria. Finite bounded memory, ordinary social information transfer, imposed adult plasticity and juvenile-specific versus adult own-task differences limit interpretation. No mutation process, fixation, ESS or historical childhood adaptation is established.
