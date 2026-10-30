# V6 results · simulation data

Run `v6-20261030T202112Z`. The predeclared factorial contains 9,504 isolated-population trajectories and 9,504 conditional rare-mutant trajectories (12 contexts × 99 trait pairs × 8 environmental histories), plus 75 pilot trajectories. Independent held-out paths add 144 population and 144 mutant trajectories. Fixed-environment controls cover 27 representative trait/plasticity settings. These are conditional models, not fitted biological estimates.

## Best observed grid cells, not established evolutionary equilibria

Maxima use post-burn-in mean abundance, not raw net births minus deaths. All other parameters and each random history are fixed within a context. The table reports a range if cells are numerically tied. Eight histories do not establish a unique stochastic optimum. Conditional invasion uses a common resident (d=.5, τ=3); its best mutant is not an ESS.

| Adult encoding η_A | Flip hazard κ | Abundance-max d | Abundance-max τ | Mean N | d boundary? | τ boundary? | Best relative-invasion d | Best relative-invasion τ |
|---|---|---|---|---|---|---|---|---|
| 0.0 | 0.0 | 1 | 3.3659 | 5620.135 | yes | no | 1 | 1.783 |
| 0.0 | 0.01 | 1 | 1.7826 | 4437.634 | yes | no | 1 | 0.9441 |
| 0.0 | 0.05 | 1 | 0.68705 | 3518.495 | yes | no | 1 | 0.5 |
| 0.0 | 0.2 | 1 | 0.5 | 3053.320 | yes | yes | 1 | 0.5 |
| 0.1 | 0.0 | 1 | 3.3659 | 5760.835 | yes | no | 1 | 1.297 |
| 0.1 | 0.01 | 1 | 1.2973 | 4800.627 | yes | no | 1 | 0.6871 |
| 0.1 | 0.05 | 1 | 0.5 | 3963.350 | yes | yes | 1 | 0.5 |
| 0.1 | 0.2 | 1 | 0.5 | 3248.106 | yes | yes | 1 | 0.5 |
| 1.0 | 0.0 | 1 | 0.68705 | 6509.208 | yes | no | 1 | 0.5 |
| 1.0 | 0.01 | 1 | 0.5 | 6088.367 | yes | yes | 1 | 0.5 |
| 1.0 | 0.05 | 1 | 0.5 | 5228.114 | yes | yes | 1 | 0.5 |
| 1.0 | 0.2 | 1 | 0.5 | 3919.778 | yes | yes | 1 | 0.5 |

No context had both abundance-maximizing parameters in the interior: d=1 was the upper-boundary maximum in all 12 contexts. With adult η_A=.1, the abundance-maximizing grid τ decreases from about 3.366 at κ=0 to .5 at κ=.2. Stable abundance and conditional invasion favor different sampled maturation times; neither is a demonstrated ESS.


## Held-out matched contrasts at τ=3, adult η_A=.1

Each contrast reuses the same environmental path for d=0 and d=1. SE describes Monte Carlo path variation, not invented uncertainty for a deterministic equation.

| κ | Mean N at d=0 | Mean N at d=.5 | Mean N at d=1 | N(d=1)−N(d=0) | Paired SE (16 new paths) |
|---|---|---|---|---|---|
| 0.0 | 4283.826 | 4867.400 | 5770.471 | 1486.645 | 0.000 |
| 0.01 | 3888.094 | 4200.124 | 4690.843 | 802.749 | 81.114 |
| 0.2 | 2200.303 | 2115.379 | 2077.566 | -122.737 | 25.519 |

## Retention, adaptation and fixed environments

In an adult-only cohort with no births or deaths, the first post-reversal time at which accuracy reaches .75 is None (censored through time 200) for η_A=0, 137.0 for η_A=.1, and 14.0 for η_A=1. This directly checks the imposed encoding mechanism; it is not evidence that genetic selection produced rigidity. Frozen-adult populations can still adapt through demographic replacement, unlike this fixed cohort.

All 27/27 representative fixed-environment settings meet the full relative residual criterion 1e-8. The maximum residual is 8.76e-13. Opposite truth signs have equal equilibrium abundance and mirrored cognitive states by symmetry; measured mirrored-RHS errors are at most 6.82e-13. This is an informative null result, not a reason to alter environmental payoffs.

With κ>0, population and culture fluctuate and are summarized over times 200–600. Different hazards need not have different true invariant equilibria, and this finite run does not prove mixing or uniqueness. Recovery is censored at the next flip; short episodes can have no sampled recovery observation. Inspect recovery fraction alongside conditional recovery time.

## Numerical and scientific limits

27/27 numerical/model checks pass. Maximum scaled RK4 error against segment-wise DOP853 is 4.08e-08; timestep halving is recorded per case in verification.json. A fine-observation check on an independent fast-changing history changes mean N by at most 2.458 density units and average adult accuracy by 0.002771. This is output-sampling error, separate from solver error.

Mathematical consequences: maturation conserves individuals and learned state; zero payoff consequences remove demographic effects of deference/learning; κ=0 removes environmental seed variation; truth reversal preserves demographic symmetry.

Assumption-sensitive findings: any retention/adaptation tradeoff depends on the prescribed plasticity, finite unit-step memory, signal rate/quality, environmental hazard and error-associated demographic rates. Deference still bundles public substitution and social storage; ordinary social information transfer can explain benefits. There is no newly evolved dogmatism parameter or empirical test of historical childhood. Encoding thinning is algebraically an effective update-rate change.

Unsupported claims: a proven stationary distribution, a general interior optimum, fixation, an ESS, novelty relative to all cultural-evolution research, or validation of an evolved childhood obedience adaptation.
