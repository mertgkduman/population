# V6 predeclared experiment contract

Recorded before broad simulations. A short compile/smoke pilot checked the reused solver; it is not a hypothesis test.

## Identification and assumptions

Keep two irreversible biological stages and V5's private-evidence ledger u and held conviction b. At maturation retain both ledgers exactly. Private cues have identical accuracy p=.65 and identical exposure rate 1 in both stages. A juvenile encodes a cue with probability eta_F=1; an adult encodes it with probability eta_A. This is an imposed plasticity difference, separate from deference d and from cue quality. Adults advise from their held belief. Juveniles accept adult testimony and may substitute its action as in V5. Zero default query cost isolates accuracy effects. No benefit is assigned directly to tau, d, or retention.

Environmental truth flips sign at exact exponentially distributed waiting times with hazard kappa (units inverse model time). All trait pairs and plasticity controls share each seed's switch times. Truth changes cue correctness and behavioral payoffs together; there are no independent environmental histories for rare mutants. Fixed ± environments are symmetric: expect mirrored belief equilibria and equal equilibrium abundance, not two arbitrarily unequal carrying capacities. Changing environments require finite-window distribution summaries, not claims of fixed equilibria.

## Hypotheses (Given / When / Then)

- H1: Given a stable environment, when adult private plasticity decreases, then previously acquired beliefs persist longer within surviving adults; demographic gains are not assumed.
- H2: Given repeated truth reversals, when adult updating slows, then adult belief accuracy and abundance can decrease and recovery may depend on replacement by maturing juveniles. Compare identical histories.
- H3: Given the same private ability, when d and tau vary, then the best isolated-population abundance and best rare-mutant growth may differ. Any boundary optimum is reported as such.
- H4: Given symmetric truth and initial beliefs, when all score signs and truth are reversed, then demographic outputs are identical and signed beliefs are reflected.
- H5: Given kappa=0, when seeds change, then all trajectories are identical; given eta_F=eta_A=1, V6 must reduce to its copied V5 equations with matched parameters.
- H6: Given zero fitness consequences and query cost, when d, plasticity and environmental switching vary at fixed tau, then demographics are invariant.

## Design fixed before broad runs

Pilot 5 by 5 traits; main 9 d values in [0,1] by 11 logarithmic tau values in [.5,12]. eta_A in {0,.1,1}, kappa in {0,.01,.05,.2}; eight paths seeded 65001–65008, T=600, burn-in=200, RK4 dt=.1, observations every 4 time units. eta_A=1 is the equal-plasticity control, eta_A=0 freezes within-adult learning. All cue rates remain equal. Parameter values inherit V5 except the explicitly listed differences. Do not tune parameters after seeing optima.

Use mean abundance, accuracy and fluctuations over [200,600], finite log growth, and full population/flux trajectories. Monte Carlo SD and SE describe path variation; deterministic outputs have no confidence intervals. Recovery after each flip is the first sampled attainment of adult accuracy >=.75 before the next flip; unresolved events are censored and success fraction is separate. Sampling gives a four-time-unit timing resolution.

Rare-mutant analysis uses resident d=.5,tau=3, the same adult plasticity and the same path. Integrate a nonfeedback mutant in the resident's cultural/resource environment at every RK4 stage, normalize periodically, and accumulate log growth over [200,600]. Report absolute and resident-relative finite-window invasion growth separately. This does not prove fixation, ESS, or historical evolution.

Held-out seeds 68001–68016 compare d={0,.5,1}, tau=3 in the stable, slow and fast changing environments at eta_A=.1. Check numerical convergence at dt=.05 and against segment-by-segment SciPy DOP853 (rtol=1e-10,atol=1e-12), population conservation/nonnegativity, exact switch boundaries, inherited memory, self-mutant relative neutrality, and offline/browser/export integrity. Also estimate a representative equilibrium residual in each fixed truth; report unconfirmed convergence honestly.
