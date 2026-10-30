# V5 mathematical model

All parameters are hypothetical. This model isolates an inherited source-use propensity from cognitive hardware and private-cue quality. It does not establish genetic separability in organisms.

## Stages and memory

For each inherited trait g=(d,tau), F_g(u,b) and A_g(u,b) are juvenile and adult densities. u and b are integers in [-H,H]; H=4 by default. u stores only personally obtained evidence; b stores held convictions, including accepted testimony. A neutral score predicts either action with equal probability. Each biological individual remains in exactly one of two stages. The cognitive subcompartments give 2(2H+1)^2 ODE variables per genotype.

Fresh private evidence moves both u and b one signed step. At the caps, an outward update stays at the cap; contradictory evidence always moves inward. Accepted adult testimony moves b only. No source writes factual content into newborns: births enter F(0,0). Maturation transfers the existing joint state at hazard m=1/tau. A deliberately labeled reset ablation instead transfers into A(0,0). tau is an exponential waiting-time parameter, not a fixed age or observed survivor age.

Crucially, d=0 organisms retain everything they acquired during childhood. In the main d=0 model u=b exactly. The meaningful private-learning comparison is not a learner forced to forget at maturation.

## Information and deference

Let j(u)=(1+sign(u))/2 be the probability that the accumulated private judgment recommends +. The adult pool's probability of recommending + is

q_plus = epsilon + (1−2 epsilon) [sum_g,u,b A_g(u,b) j(b)] / [sum_g,u,b A_g(u,b)].

The default transmission error epsilon=.05 is externally fixed. The pool is the candidate's own population in an isolated run and the common resident adult pool in invasion/competition. No adult age implies correct knowledge. At zero adults, social learning and action substitution are disabled.

A juvenile publicly chooses the adult judgment with probability d and its own accumulated private judgment otherwise. Hence

P(public + | u) = (1−d)j(u)+d q_plus,

and P(override | disagreement)=d. A social learning encounter accepts an adult sign into b with probability d even when both judgments agree. Thus the main d is explicitly a bundle of public action substitution and memory acceptance. The accept×override factorial separates those paths; a conflict-only acceptance ablation excludes agreement reinforcement. The main result alone cannot be identified as the benefit of ignoring one's own judgment.

Private cue opportunities occur at lambda_F=nu_private access/load; social encounters occur at lambda_S=nu_social/load. Actual probability of a signed + private cue is pi_I(t). In ordinary conditions it equals p if truth theta=+1 and 1−p if truth theta=−1. The misleading-channel experiment changes pi_I while truth stays fixed. All genotypes within a scenario have identical cue quality, exposure opportunities and memory capacity. Achieved accuracy can differ through learning histories, action choices and survival filtering; this is not an inherited cognitive-accuracy change.

`load` is an effective exposure divisor. It is algebraically a rescaling of opportunities relative to demographic time, not a mechanistic model of complex reasoning. The separate stochastic repertoire experiment represents multiple distinct facts explicitly and is described in repertoire_model.md.

## Adult policies and costs

Adults express sign(b) and transmit that same belief. Adult private cues continue to move both u and b, with query rate

- retained/updating: lambda_A = nu_adult access/load;
- frozen: lambda_A = 0;
- audit: lambda_A(b) = nu_adult access/load times 1 when |b|<h, and audit_floor otherwise.

Default h=2 and audit_floor=.05. These policies are imposed experimental architectures; neither freezing nor confidence-based auditing is called emergent or optimal dogmatism. When H<h, auditing always samples and coincides with continuous updating. Adults who freeze can still disappear and be replaced by newly matured adults: zero within-adult updating does not make population culture immutable.

Each actual private query contributes query_cost×query_rate to mortality. This is a stated energetic/hazard approximation, not an observed biological cost. It never directly rewards d or freezing. Sampling-cost and accuracy channels are separated by zero-cost experiments. The model does not charge search/teaching or social-observation costs.

The oracle confidence gate compares max(q_correct,1−q_correct) with sigmoid(|u| logit(p)), uses the better source when it exceeds this private-confidence proxy, and can invert an anti-informative adult source. It knows true current adult reliability. It is a privileged finite-score heuristic, not a full Bayesian learner or a realistic learned-trust model. Its displayed d axis is inactive. The additional exact Bayesian benchmark establishes a narrower information-value bound.

## Demographic equations

Let Q_I shift both scores under private cues, Q_S shift b under accepted social signs, and Q_A implement adult querying. These are conservative Markov generators. For each genotype, with column-state convention,

F_dot = (Q_I+Q_S)F − diag(m+mu_F(u))F + e_00 sum_b,u beta(b,N) A(u,b),

A_dot = Q_A A + m F − diag(mu_A(b))A.

The held-belief correctness is c_theta(b)=(1+theta sign(b))/2. Juvenile public correctness uses the same expression applied to the probability of public +. Rates are

mu_F(u) = mu_F_base + k_F [1−public_correct(u)] + query_cost lambda_F,

mu_A(b) = mu_A_base + k_A [1−c_theta(b)] + query_cost lambda_A(b),

beta(b,N) = [beta_base+beta_skill c_theta(b)] S(N)/[K_S+S(N)],

S(N) = S0/[1+N/K].

There is no direct fecundity-versus-tau curve or deference bonus. K is a resource-density scale, not a carrying capacity. The scalar stage totals obey F_dot=B−M−D_F, A_dot=M−D_A and N_dot=B−D. Maturation and cognitive transitions conserve total density. Accuracy-linked terms and query cost are both disabled for the neutral control.

For homogeneous populations, the operators average learning events exactly. There is no Monte Carlo error in those ODE maps. The stochastic environmental-history and repertoire experiments have separate seed-based uncertainty.

## Inheritance and selection

Offspring inherit their parent's d and tau, then acquire culture from the current shared adult pool. Broad trait competition uses uniform mutation probability .001 across the declared nine genotypes. A separate four-architecture competition has equal initial frequencies, zero mutation and common tau=3; it treats the specified adult policy as an additional inherited architecture for that comparison only.

At a resident ecological-cultural equilibrium, freeze its q_plus and resource factor. Construct the mutant's complete linear operator over F(u,b),A(u,b), using its own d,tau and policy. The largest real eigenvalue is conditional rare-mutant invasion growth. Adult teachers are resident adults, not an independent mutant population. Self-invasion and residuals are checked. A positive eigenvalue supports initial invasion, not guaranteed fixation or an ESS.

Time-dependent invasion integrates resident and rare-mutant equations together, excludes mutant feedback on resident teachers/resources, repeatedly normalizes mutant densities and accumulates log growth. Reported rates are finite windows after burn-in, not arithmetic averages of instantaneous eigenvalues. Resident-against-itself has zero relative growth; its absolute finite-window rate need not be exactly zero.

## Measurements and limitations

Maps separate r_T=log(N(T)/N(0))/T, N(T), last-100-time-unit growth, conditional invasion, private versus held belief accuracy, public action accuracy, score depth, wrong high confidence, query rates/costs and recovery. Recovery is relative to the same policy's stable baseline, sustained over 20 units at five-unit observations; unavailable values are censored. Score persistence |b|>2 means retaining a nonzero sign after two opposing unit steps. It is not refusal to process evidence.

Survival to maturity is the exact absorbing probability of a neutral newborn under final advice and private-cue statistics held fixed: m 1^T(−J)^−1 e_00, where J is the transient juvenile operator including mortality and maturation. It is not realized cohort survival through a changing environment.

Population-level gains can reflect ordinary information transfer. Finite score caps and equal-sized endorsements can misweight unequal evidence, so freezing's advantage over this updating rule is not a proof against calibrated Bayesian updating. Task correlation, teacher genealogy, costly search, normative collaboration, sanctions, physical coercion and empirical life-history calibration are absent. The scientific question is conditional mechanism identification, not historical proof of childhood obedience.
