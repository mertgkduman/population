# V6 situational advice: predeclared extension

Before simulation, distinguish a worse local sensor from uniformly worse final advice. A fixed-reliability random-copying null has accuracy (1-d)p_I+d p_A. If p_A<p_I, its optimum is d=0. Noise alone does not imply an interior optimum.

## Mechanism

Retain V6's two demographic stages, both knowledge ledgers, private global-cue accuracy .65, equal exposure rates, juvenile encoding1 and adult encoding.1, zero query cost, inherited d/tau, state-preserving maturation and Poisson global environmental switches. A fresh local circumstance z=±1 multiplies global truth theta to determine the currently correct action. Learners observe z with accuracy p_F=.9; remote advising adults observe it with p_A in {.55,.70,.85}, strictly lower in every main scenario. Errors are independent conditional on z and renewed across decisions. These local cues are algebraically averaged, not additional ODE states.

A learner uses its private estimate of theta times its local cue; an adult recommends its held estimate of theta times its own noisier local cue. Deference d substitutes the adult action with probability d, independent of correctness. Adults may have better accumulated global knowledge; their local sensor is always worse. Reproductive-adult own-task payoffs remain the baseline global task, isolating noise in advice for juvenile-specific situations.

When accepted situational advice is stored, a juvenile infers global theta from the adult action and its own local cue. Context mismatch has probability delta=p_F+p_A-2p_F*p_A. Thus stored testimony is an additional binary-symmetric corruption of the existing adult testimony distribution. This follows from the two observation channels; it is not an arbitrary d penalty. A clean-teaching ablation transmits the adult's general fact explicitly and omits this decoding noise. Action-only and memory-only ablations separate the bundled deference channels.

## Hypotheses and checks

- Given fixed source accuracies, when random-copy d varies, accuracy is affine. Worse adult final advice favors d=0; equal sources are neutral. An interior optimum is not a mathematical consequence of adding noise.
- Given p_A<p_F but endogenous adult global knowledge, when d/tau vary, optima may be at either boundary, interior, or flat. Preserve all results.
- Given unit local precision in both stages, the extension exactly recovers V6 baseline.
- Given d=0, changing adult local sensor quality has no effect on the isolated population.
- Given an accepted adult action, the derived decoding error matches exact enumeration over local truth and both cue errors.
- Given population transitions and shared-resident invasion, flux accounting, nonnegativity, memory preservation, identical newborns and self-relative neutrality must still hold.

## Design

Pilot: 9 d values, 5 logarithmic tau values, p_A=.55,.7,.85 and kappa=0,.05,.2, seed71001, T=600. Main: original V6 grid of9 d by11 logarithmic tau values [.5,12], all three adult local precisions, all four kappa values0,.01,.05,.2, eight common paths71001–71008, T=600, burn-in200, RK4 dt=.1,151 observations. No demographic parameters are changed to manufacture interior optima.

Store all per-seed outcomes and full histories in the repository. Published reference packages contain every seed's map outcomes and the exact seed71001 trajectories displayed by the dashboard; unused full histories remain downloadable from the repository. This keeps the Pages site within1GB while preserving complete research data.

If a pilot/main interior candidate appears, refine d at the same declared conditions and adjacent tau values, confirm on held-out seeds74001–74016, compare dt=.05 and null/ablated mechanisms, and report whether it is reproducible. Also run predeclared tau=3, p_A=.7, kappa=0,.2 action-only, memory-only and clean-teaching controls; do not retune local precisions to obtain an interior maximum. Numerical references use DOP853 rtol1e-10 atol1e-12. All uncertainty is environmental-path uncertainty, not invented deterministic significance.
