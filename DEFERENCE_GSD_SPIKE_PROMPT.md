# GSD spike: deference, maturation, and population fitness

## Task and execution mode

Use the installed gsd-spike workflow in --quick mode to implement and run the computational experiment below and deliver a working, self-contained interactive HTML dashboard. This is a scientific feasibility spike, not a request for a plan, mockup, or full production application.

First discover and read the actual installed GSD instructions and invoke the supported interface. The documented workflow name is gsd-spike; do not guess a shell command or claim an invocation that did not occur. Use --text only when the runtime needs it. Do not initiate a full new-project/roadmap cycle. Preserve the installed workflow's verification and manifest requirements. If GSD is genuinely unavailable after discovery, report that fact and still complete the compact experiment without pretending GSD ran.

Proceed with the assumptions specified here. Do not pause for cosmetic choices or tune assumptions to obtain a favorable result. Work in a new, isolated directory, preferably .planning/spikes/<next-id>-deference-demography/, following the installed conventions. Do not overwrite unrelated work, install or upgrade GSD, require API keys, or publicly deploy anything. Use existing numerical and visualization libraries where possible. A small local dependency installation is acceptable when necessary and permitted by the runtime.

Use one thin orchestrator. At most two bounded helpers may be used, for numerical verification and dashboard implementation, when supported and actually useful. Exchange file paths and compact summaries; persist substantive work to disk. Keep the numerical model readable. Do not build an agent-based simulation, neural model, database, or web backend for this spike.

## Scientific question

At fixed private judgment ability and adult advice quality, how do:

1. follower deference d in [0,1], and
2. the follower-to-adult maturation timescale tau > 0

change demographic growth, persistence, and conditional invasion fitness?

The primary experiment must isolate the propensity to defer from intelligence, adult accuracy, resource availability, and initial population composition. Within each parameter sweep, vary only d and tau. Other parameters define separately labeled scenarios, not hidden changes between cells.

Do not reward deference directly. Reward accuracy of behavior through lower error-associated mortality. Adult advice may be helpful, redundant, noisy, or systematically biased. Preserve negative and null results.

These are hypothetical mechanistic models, not fitted models of humans or any named animal. They test consequences of specified mechanisms, not whether evolution historically selected human childhood or moral obedience. Treating deference as independently variable is a modeling assumption; the simulation cannot establish biological or genetic separability from cognitive ability.

## Exactly two demographic states

- F(t): nonreproducing followers.
- A(t): reproductive adults who can be followed.
- N(t) = F(t) + A(t).
- Offspring enter F; maturation moves them irreversibly from F to A.
- No adult-to-follower transition.

All individuals in an isolated run have the same candidate trait pair (d, tau). Adults do not express follower deference after maturing. Advice quality is controlled externally and is identical across trait pairs within a scenario.

Use m = 1/tau as the constant maturation hazard. Tau is the mean waiting time to maturation in the absence of death, not a fixed birthday. With constant competing mortality, survival to maturation is m/(m + mu_F) and mean time to stage exit is 1/(m + mu_F). Do not describe tau as the observed mean age of surviving adults. An exact maturation age requires a delay equation or age structure and is outside the first spike.

Assume a well-mixed, tutor-accessible population: when adults are present, their advice is available without a capacity constraint. Start with both stages present. Do not introduce teacher-availability feedback silently. This is a controlled advice-quality experiment, not a model of endogenous cultural knowledge, teaching workload, or how adults acquired their expertise.

## Behavioral decision layer: no additional ODEs

For a task with an objectively rewarded action theta, a follower has a private estimate theta + e_I; an adult offers theta + e_A.

Define:

- E[e_I] = 0, Var(e_I) = sigma_I^2.
- E[e_A] = bias_A, Var(e_A) = sigma_A^2.
- Cov(e_I, e_A) = rho * sigma_I * sigma_A, with rho in [-1,1].

Hold these quantities fixed when varying deference. Errors are renewed across decisions; the model uses expected loss, not permanent individual quality classes. Gaussian errors are unnecessary for the formulas below; only the stated moments are required. If a Monte Carlo check is used, correlated Gaussian draws are one convenient verification device, not a demographic model assumption.

### Primary policy: follow or ignore

With probability d, use the adult's estimate instead of the private estimate; otherwise use the private estimate. The choice probability does not depend on which estimate is correct. Thus d measures willingness to substitute adult judgment for one's own.

Expected squared decision error:

L_copy(d) = (1-d)*sigma_I^2 + d*(sigma_A^2 + bias_A^2).

This policy should be the default. It is intentionally distinguishable from information pooling.

### Sensitivity policy: weighted judgment

Use the compromise estimate (1-d)*(theta + e_I) + d*(theta + e_A).

Expected squared decision error:

L_blend(d) = (1-d)^2*sigma_I^2 + d^2*(sigma_A^2 + bias_A^2) + 2*rho*d*(1-d)*sigma_I*sigma_A.

Label this policy weighted judgment, not literal obedience. Its potential interior optimum comes from the stated error structure, not an added preference for intermediate deference. Equal-quality independent information can help when pooled; it provides no accuracy benefit under random copying. Correlated information can remove the pooling advantage.

For both policies, use the analytic expected loss in the ODE. A stochastic simulation is not needed for the main sweeps.

## Behavioral payoff

mu_F(d) = mu_F_base + k_error * L(d).

Better decisions reduce follower mortality. k_error has units of inverse time per squared action-error unit. Adult mortality mu_A is constant. All demographic rates must be nonnegative. Do not add a direct +c*d growth reward, an arbitrary deference penalty, or an artificial interior-optimum term.

## Monod-type demography

Use an algebraic resource closure so the demographic system remains exactly two ODEs:

S(N) = S0 / (1 + N/K_N)

beta(N,tau) = beta_max(tau) * S(N)/(K_S + S(N)).

S0 and K_S have resource units; K_N is a population-density scale, NOT a carrying capacity. This is a quasi-steady resource approximation, not a full chemostat. It can be motivated by fast resource renewal and density-dependent uptake, but it is an assumption of this spike.

Implement:

dF/dt = beta(N,tau)*A - (m + mu_F(d))*F

dA/dt = m*F - mu_A*A.

The birth, death, and maturation fluxes are:

B = beta(N,tau)*A

D = mu_F(d)*F + mu_A*A

M = m*F.

Verify the identity dN/dt = B - D. Maturation is a transfer, not a birth or death.

## Two explicitly separated maturation assumptions

M0 — no benefit from delaying maturation (primary baseline):

beta_max(tau) = beta_const.

This baseline includes the costs of remaining a follower but no developmental preparation benefit. Do not be surprised if the growth optimum is at the minimum tau. For persistent populations, a boundary optimum is an informative consequence of this model, not a reason to alter it secretly. Do not claim that this baseline establishes selection for prolonged childhood.

M1 — preparation-benefit sensitivity model:

beta_max(tau) = beta_min + beta_gain * tau/(tau + tau_learning).

This prescribes a saturating adult reproductive/productive benefit from longer preparation. It is an additional, hypothetical trait-level tradeoff; it is NOT derived from the two-stage ODE and does not track actual accumulated knowledge. It changes adult fecundity, not adult advice accuracy. Keep it off in the primary baseline and show it as a separately labeled model.

Run the same deference-versus-tau comparison under both assumptions. Ask whether lower follower mortality changes the growth-maximizing tau when preparation has a benefit. Report an absent effect, a boundary optimum, or a flat region honestly. Do not tune this tradeoff after seeing results to manufacture prolonged dependence.

## Defaults and controlled scenarios

Use arbitrary, explicitly labeled model time and population-density units:

sigma_I = 1.0

sigma_A = 0.4

bias_A = 0.0

rho = 0.0

mu_F_base = 0.03

k_error = 0.30

mu_A = 0.15

S0 = 1.0

K_S = 1.0

K_N = 1000.0

beta_const = 1.2

beta_min = 0.2

beta_gain = 2.4

tau_learning = 3.0

F_initial = 80.0

A_initial = 20.0

T = 200.0

Primary trait domain: d in [0,1], tau in [0.5,20]. Start with 51 deference values and 61 logarithmically spaced tau values for analytic maps. Use a smaller clearly labeled grid, initially 25 by 25, for expensive numerical finite-horizon maps, with refinement available. The dashboard must correctly represent a logarithmic tau axis.

Scenario presets, all with sigma_I = 1:

1. Helpful adult advice: sigma_A=0.4, bias_A=0, rho=0.
2. Equal quality, independent advice: sigma_A=1, bias_A=0, rho=0.
3. Redundant cloned advice: sigma_A=1, bias_A=0, rho=1.
4. Noisy adult advice: sigma_A=2, bias_A=0, rho=0.
5. Biased adult advice: sigma_A=0.4, bias_A=1.5, rho=0.
6. No fitness consequence of errors: helpful-advice parameters, but k_error=0.

Changing a preset must not change initial conditions, demographic constants, or the selected maturation model. Do not interpret results across presets as isolated deference effects; use within-preset matched contrasts.

## Outcomes: distinguish growth, abundance, and selection

### Primary heatmap: low-density demographic growth rate

At low density:

beta0(tau) = beta_max(tau)*S0/(K_S+S0).

The demographic matrix is:

[ -(m+mu_F),   beta0 ]

[     m,      -mu_A ]

Compute its dominant eigenvalue analytically:

r0 = 0.5*(-(m+mu_F+mu_A) + sqrt((m+mu_F-mu_A)^2 + 4*m*beta0)).

This is a low-density asymptotic demographic growth rate, not automatically an invasion fitness in a populated environment. Show the r0=0 boundary. Positive growth requires m*beta0 > mu_A*(m+mu_F).

Always provide a matched-deference contrast:

Delta_r0(d,tau) = r0(d,tau) - r0(0,tau)

with the same scenario, maturation assumption, and other parameters.

### Time-resolved and finite-horizon quantities

- F(t), A(t), N(t), and follower/adult fractions.
- Birth, death, and maturation fluxes B(t), D(t), M(t).
- Raw net change B-D and per-capita growth (B-D)/N when N>0.
- Finite-horizon log growth r_T = log(N(T)/N(0))/T when numerically defined.
- N(T), and follower survival to maturation m/(m+mu_F).

Do not compare raw B-D across unequal population sizes as though it were a per-capita fitness measure. Do not label a deterministic tiny positive population as literally extinct. Report underflow or a user-chosen quasi-extinction threshold separately from model persistence.

### Long-run equilibrium as a separate outcome

At a positive equilibrium:

beta_required = mu_A*(1 + mu_F*tau)

N_star = K_N*((S0/K_S)*(beta_max(tau)/beta_required - 1) - 1).

Use a positive equilibrium only when r0>0; otherwise the nonnegative equilibrium is zero. Also:

A_star = N_star/(1 + mu_A*tau)

F_star = mu_A*tau*A_star.

Show N_star as equilibrium abundance, not as growth rate. At equilibrium births and deaths balance; that does not mean every trait pair has the same demographic performance. Do not assert that a trajectory has equilibrated solely because it reached T=200, especially near r0=0.

### Conditional rare-mutant invasion map

This requires no additional ODE states. Let the user pin a resident trait pair with r0_resident>0 and compute its N_star. For each candidate mutant (d_m,tau_m), replace beta0 in the same 2x2 matrix by beta(N_star_resident,tau_m) and use the mutant's maturation and follower mortality rates. Its dominant eigenvalue is the initial invasion growth rate in the resident environment.

State the assumptions: perfect inheritance of the candidate trait pair, rarity of the mutant, fixed resident equilibrium, identical externally specified advice distribution, and shared resource limitation. A positive value means initial invasion is possible under this model, not that fixation or an evolutionarily stable strategy has been demonstrated. Resident-against-itself must give zero within numerical tolerance. If the resident has no positive equilibrium, disable this mode with an explanation. Do not simulate mutations or claim trait evolution occurred.

## Fast computation and reference implementation

Prioritize analytic maps first; they provide meaningful interactive results without thousands of ODE integrations. Then add selected trajectories and numerical finite-horizon maps.

Use a small Python reference implementation with NumPy and SciPy solve_ivp, preferably DOP853 for high-accuracy reference trajectories. Explicitly record tolerances and library versions. Browser computations can use a small, documented RK4 integrator or a suitable existing solver; validate its step-size choice against the Python reference and timestep halving. Avoid two divergent scientific implementations: use one parameter schema, shared test fixtures, and a documented parity test.

Use a Web Worker or chunked computation for expensive browser sweeps. Provide a cancel/restart control and prevent obsolete computations from overwriting a newer configuration. Cache only by the full parameter configuration, policy, grid, model, horizon, and numerical settings. Invalid computations must be visibly missing, not silently assigned zero fitness.

For the HTML use plain JavaScript and a locally bundled/embedded plotting library such as Plotly. Avoid a backend or framework unless the host requires it. Target a single index.html with inline assets that works without network access; a local asset folder is acceptable only if a genuine packaging limitation is documented. Do not depend on CDN scripts or local-file fetch calls for essential functionality.

## Required interactive HTML

Deliver an actual functioning dashboard, not screenshots or an empty interface.

1. A compact control area for d, tau, scenario, decision policy, maturation model, horizon, and relevant advanced parameters. Show units and the active assumptions. Provide reset and parameter export/import.
2. An animated population view with follower and adult quantities, a visible irreversible maturation arrow, and birth/death/maturation flux labels from the actual computed trajectory. Include play, pause, reset, speed, and time-scrub controls. Any illustrative glyphs represent continuous densities, not simulated individual animals.
3. Synchronized time-series plots for F, A, N, and for B, D, B-D, with an optional per-capita display. The current-time cursor must stay synchronized with the animation.
4. A clickable 2D heatmap with d on x and tau on y. Metric choices: r0, matched Delta_r0, N_star, numerical r_T or N(T), and conditional invasion rate. Distinguish analytic from numerically integrated outputs. Hover shows the actual parameters, loss, mortality, and metric. Clicking a cell loads its trajectory. Time-dependent panels must not imply that an asymptotic fitness map itself changes with animation time.
5. Pin and compare at least three parameter pairs. Clearly identify comparisons as independent populations, not direct competition. Offer an easy matched-tau comparison across d.
6. A concise model/assumptions panel containing the equations, policies, definitions of fitness, the exponential-maturation limitation, and the distinction between M0 and M1. Show that adult accuracy is held fixed within each sweep.
7. Export the active configuration, sweep table, and selected time series. Include all units, policies, model labels, numerical settings, and a run identifier. Label all outputs as simulation data.

Use readable labels, keyboard-accessible controls, responsive layout, and consistent color limits for comparable heatmaps. Center signed difference and invasion maps at zero. Do not mark an arbitrary unique optimum in a genuinely flat landscape; indicate ties or ranges. Keep the interface useful rather than decorative.

## Predeclared checks and verification

Record these Given/When/Then checks before execution and report measured results:

- Given copying and equal private/adult mean squared error, varying d leaves loss and all demographic results unchanged.
- Given d=0, altering adult accuracy, bias, or correlation leaves outputs unchanged.
- Given redundant cloned signals, varying d leaves both decision policies unchanged.
- Given k_error=0, varying d has no demographic effect.
- Given copying, lower adult mean squared error lowers follower mortality as d increases; higher adult mean squared error reverses this. These are algebraic predictions, not discoveries validating the biological hypothesis.
- Given weighted judgment with independent equal-quality estimates, variance reduction can produce an interior optimum. Do not describe this as evidence that adult authority is necessary.
- Given zero births and zero deaths, maturation preserves N exactly and the trajectory matches F=F_initialexp(-mt), A=A_initial+F_initial*(1-exp(-m*t)).
- Given constant externally fixed resources, compare the numerical solution with the 2x2 matrix exponential; check the dominant eigenvalue independently.
- Verify the positive-equilibrium formulas at representative persistent settings, the r0=0 boundary, and resident self-invasion rate zero.
- Test valid parameter ranges, nonnegative populations, the absorbing all-zero population, and near-threshold trajectories. Do not conceal unstable integration with blanket clipping.
- Compare browser trajectories against Python references, including d=0, d=1, extreme tau, both policies, and both maturation models. Record absolute/relative errors and step-halving results; choose and justify tolerances.
- Check UI play/pause/scrub, heatmap selection, pinned comparisons, exports, resized layout, and browser-console errors. Run an offline test if claiming offline operation. Record browser tests that were unavailable instead of claiming they passed.

An optional Monte Carlo check of expected loss is acceptable but should not delay the main experiment; use a saved seed and report sampling uncertainty separately from deterministic sweep results. Do not add statistical significance tests or invented confidence intervals to deterministic ODE outputs.

## Deliverables and stopping rule

Preserve, using the installed GSD conventions:

- The spike hypothesis, assumptions, and investigation trail.
- Readable reference model and sweep/export scripts.
- A shared parameter schema and scenario definitions.
- Tests and machine-readable verification results.
- The functioning interactive HTML and necessary local assets.
- Sweep CSV/JSON, representative time-series CSV/JSON, and run manifests with source/config hashes when practical, solver settings, dependency versions, and timestamps.
- A short findings report identifying results that are mathematical consequences, results sensitive to assumptions, and questions this model cannot answer.
- The appropriate GSD manifest entry and technical VALIDATED / INVALIDATED / PARTIAL verdict. That verdict concerns implementation and specified checks, not proof of an evolutionary adaptation.

Finish the narrow end-to-end experiment before optional extensions. Do not implement age-distributed cohorts, endogenous teacher knowledge, social networks, stochastic extinction, ecological field calibration, or full evolutionary dynamics in this spike. List them only as limitations when materially relevant.

In the final response, open or link the actual HTML and provide a download of the complete project. Report the verification status and the most important positive, negative, and null findings, including whether any claimed maturation optimum is a grid boundary. Do not stop with a plan or claim a biological hypothesis was validated merely because the software worked.

## Minimal reference anchors

These orient the implementation; do not turn the spike into another literature review:

- Open GSD Core, docs/how-to/spike-and-sketch.md and the installed gsd-spike workflow: documented quick mode and persistent spike artifacts. Check the installed version rather than assuming a command syntax.
- Deffner and McElreath (2022), When does selection favor learning from the old? Social learning in age-structured populations. PLOS ONE, DOI 10.1371/journal.pone.0267204. Relevant distinction between social-learning selection and population fitness; not the source of the particular equations specified here.
- de Roos (2018), When individual life history matters: conditions for juvenile-adult stage structure effects on population dynamics. Theoretical Ecology, DOI 10.1007/s12080-018-0374-3. Stage-structured modeling context.
- Official SciPy solve_ivp and Plotly JavaScript documentation for numerical and interface behavior.

The particular behavioral losses, resource closure, parameter values, and preparation tradeoff in this specification are explicit proposed modeling assumptions, not empirical estimates taken from those sources.
