# Developmental deference, cultural learning and demographic fitness

Repository: https://github.com/mertgkduman/population · Interactive research: https://mertgkduman.github.io/population/

Hypothetical computational research. Technical validation does not establish a historical adaptation or genetic separability from cognition.

## Versions at a glance

| Version | Scientific question / change | Data and specification |
|---|---|---|
| V1 | Two demographic ODEs isolate deference and maturation under fixed private and adult error distributions. | [v1/](v1/) |
| V2 | Adult advice precision changes with a signed, externally imposed calendar-time drift. | [v2/](v2/) |
| V3 | Copying propensity declines over time while an adult advice-quality feature increases. | [v3/](v3/) |
| V4 | Adults transmit beliefs acquired as juveniles; cognitive substates retain confidence and learned trust. | [v4/](v4/) |
| V5 | Separates retained private evidence from held conviction, with noisy access, query costs and actual fact repertoires. | [v5/](v5/) |
| Further work | Research directions motivated by unresolved identification, learning, cultural and demographic questions. | [proposals/](proposals/) |
| V6 | Juveniles encode private cues more readily than adults; retained convictions generate advice while environmental truth switches stochastically. | [v6/](v6/) |


## View the research

Build and preview the seven-tab site:

~~~bash
python scripts/restore_large_files.py
python scripts/build_pages.py
python -m http.server 8000 --directory docs
~~~

Open http://localhost:8000. The tabs are V1–V5, Further work and V6, in that order. Each has Model, Results, Changes and Shortcomings. The original interactive dashboards retain every plot family. Under each plot, an exact displayed-data ZIP supplies JSON, CSV, available parameters and units, alongside a reference-data package. Data and definitions remain version-specific. Large results load when requested. No new results are claimed for proposals.

## Prepare GitHub Pages

The research history contains files above GitHub's [100 MiB regular-Git limit](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github). Preserve that history locally and create a clean publishable snapshot:

~~~bash
python scripts/prepare_github.py --output dist/github-repository
~~~

The output is a Git repository on **main**, containing every version's source, specification and data. Large originals are losslessly chunked inside their version folder. Run the following in the exported repository to restore original paths and verify their SHA-256 hashes:

~~~bash
python scripts/restore_large_files.py
~~~

The existing research history is not rewritten. Per-version records retain their contemporaneous branch names and verification context; the current main branch unifies every version. To publish, add your GitHub remote to the prepared repository, push main, and select **Settings → Pages → Source: GitHub Actions**. No remote or public deployment is performed by these preparation scripts. Do not push the original research history directly: it still contains historical oversized blobs.

The included workflow restores large files, builds and verifies the static site, then publishes the generated output. The builder enforces the [1 GB Pages site limit](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits). URLs are relative for project-site prefixes. Runtime assets are local; no API key or backend is required. Original standalone dashboards remain available offline after restoration. The portal's shared-data adapters use ordinary HTTP, as on GitHub Pages.


Select **GitHub Actions**, not **Deploy from a branch**. Publishing the source root runs Jekyll on the README and omits the generated Results pages. Equations are rendered with bundled KaTeX, including fonts; no runtime CDN is used.

## Equations and definitions

The equations below use mathematical notation. Time and density units are hypothetical; cognitive substates do not add biological stages. Full original specifications remain in each version folder.

## V1 equations

# V1 · Controlled advice and two demographic stages

The model isolates deference $d\in[0,1]$ and maturation timescale $\tau>0$. Followers $F$ do not reproduce; adults $A$ do. Private ability and adult advice quality are fixed within each parameter sweep. All units are hypothetical.

## Decision errors

The private error has mean zero and variance $\sigma_I^2$. Adult error has mean $b_A$ and variance $\sigma_A^2$:

$$
\mathbb E[e_I]=0,\qquad
\mathbb E[e_A]=b_A,\qquad
\operatorname{Cov}(e_I,e_A)=\rho\sigma_I\sigma_A.
$$

**Random copying:** with probability $d$ substitute the adult estimate for the private estimate.

$$
L_{\mathrm{copy}}(d)
=(1-d)\sigma_I^2+d\left(\sigma_A^2+b_A^2\right).
$$

**Weighted judgment:** pool the two estimates with weights $1-d$ and $d$.

$$
L_{\mathrm{blend}}(d)
=(1-d)^2\sigma_I^2+d^2\left(\sigma_A^2+b_A^2\right)
+2\rho d(1-d)\sigma_I\sigma_A.
$$

Only the stated moments are required; Gaussian errors are not assumed. Better decisions lower follower mortality:

$$
\mu_F(d)=\mu_{F,\mathrm{base}}+k_{\mathrm{error}}L(d).
$$

## Resources and reproduction

Let $N=F+A$ and $m=1/\tau$. The resource closure and birth rate are

$$
S(N)=\frac{S_0}{1+N/K_N},
\qquad
\beta(N,\tau)=\beta_{\max}(\tau)
\frac{S(N)}{K_S+S(N)}.
$$

$K_N$ is a density scale, not a carrying capacity. The two explicitly separate maturation assumptions are

$$
\begin{aligned}
\mathrm{M0}:\quad&\beta_{\max}(\tau)=\beta_{\mathrm{const}},\\
\mathrm{M1}:\quad&\beta_{\max}(\tau)=
\beta_{\min}+\beta_{\mathrm{gain}}
\frac{\tau}{\tau+\tau_{\mathrm{learning}}}.
\end{aligned}
$$

M1 prescribes a preparation benefit; it does not derive acquired knowledge from the demographic equations.

## Demography and accounting

$$
\frac{dF}{dt}=\beta(N,\tau)A-(m+\mu_F)F,
\qquad
\frac{dA}{dt}=mF-\mu_AA.
$$

$$
B=\beta A,\qquad
D=\mu_FF+\mu_AA,\qquad
M=mF,\qquad
\frac{dN}{dt}=B-D.
$$

Maturation transfers density and creates no births or deaths. With zero births and deaths,

$$
F(t)=F(0)e^{-mt},
\qquad
A(t)=A(0)+F(0)\left(1-e^{-mt}\right).
$$

For constant competing mortality,

$$
\Pr(\text{survive to maturation})=\frac{m}{m+\mu_F},
\qquad
\mathbb E[T_{\mathrm{stage\ exit}}]=\frac{1}{m+\mu_F}.
$$

$\tau$ is the mean maturation waiting time without death, not a fixed birthday or the observed age of surviving adults.

## Growth, abundance and invasion

At low density, define $\beta_0=\beta_{\max}S_0/(K_S+S_0)$:

$$
G_0=
\begin{pmatrix}
-(m+\mu_F)&\beta_0\\
m&-\mu_A
\end{pmatrix}.
$$

$$
r_0=
\frac{-(m+\mu_F+\mu_A)
+\sqrt{(m+\mu_F-\mu_A)^2+4m\beta_0}}{2}.
$$

Persistence requires $m\beta_0>\mu_A(m+\mu_F)$. Matched and finite-horizon growth are

$$
\Delta r_0(d,\tau)=r_0(d,\tau)-r_0(0,\tau),
\qquad
r_T=\frac{\log\left[N(T)/N(0)\right]}{T}.
$$

At a positive equilibrium,

$$
\beta_{\mathrm{required}}=\mu_A(1+\mu_F\tau),
$$

$$
N_*=
K_N\left[
\frac{S_0}{K_S}
\left(\frac{\beta_{\max}}{\beta_{\mathrm{required}}}-1\right)-1
\right],
$$

$$
A_*=\frac{N_*}{1+\mu_A\tau},
\qquad
F_*=\mu_A\tau A_*.
$$

Use the positive equilibrium only when $r_0>0$; otherwise the nonnegative equilibrium is zero. For a rare mutant, replace $\beta_0$ by its birth rate in the resident environment:

$$
s(g_m;g_r)=
\max\operatorname{Re}\lambda
\begin{pmatrix}
-(m_m+\mu_{F,m})&\beta(N_{*,r},\tau_m)\\
m_m&-\mu_A
\end{pmatrix}.
$$

Positive invasion growth supports initial invasion under the model, not fixation or a historical adaptation.


Original source: [v1/SPEC.md](v1/SPEC.md).

## V2 equations

# V2 · Improving or decaying adult advice

V2 retains V1's two demographic equations, decision policies, resource closure and M0/M1 assumptions. It changes adult advice quality with calendar time:

$$
\sigma_A(t)=
\operatorname{clamp}\!\left(
\sigma_A(0)e^{-gt},
\sigma_{\mathrm{floor}},
\sigma_{\mathrm{ceiling}}
\right).
$$

Positive $g$ improves precision; negative $g$ degrades it. Bias $b_A$ and private error $\sigma_I$ remain fixed within a scenario.

$$
L_{\mathrm{copy}}(d,t)
=(1-d)\sigma_I^2
+d\left[\sigma_A(t)^2+b_A^2\right],
$$

$$
L_{\mathrm{blend}}(d,t)
=(1-d)^2\sigma_I^2
+d^2\left[\sigma_A(t)^2+b_A^2\right]
+2\rho d(1-d)\sigma_I\sigma_A(t).
$$

$$
\mu_F(d,t)=\mu_{F,\mathrm{base}}
+k_{\mathrm{error}}L(d,t).
$$

$$
\dot F=\beta(F+A,\tau)A-
\left[\frac1\tau+\mu_F(d,t)\right]F,
\qquad
\dot A=\frac F\tau-\mu_AA.
$$

The plotted frozen-time diagnostic is

$$
r_{\mathrm{inst}}(t)=
\frac{
-\left[m+\mu_F(d,t)+\mu_A\right]
+\sqrt{\left[m+\mu_F(d,t)-\mu_A\right]^2+4m\beta_0}
}{2}.
$$

When $g\ne0$, this is a nonautonomous system: $r_{\mathrm{inst}}$ is not a single stationary invasion rate. The primary finite-horizon measures are

$$
r_T=\frac{\log[N(T)/N(0)]}{T},
\qquad
\Delta r_T(d,\tau)=r_T(d,\tau)-r_T(0,\tau).
$$

Advice quality is prescribed externally, not acquired by individual adults. Setting $g=0$ recovers V1.


Original source: [v2/EXPERIMENTS.md](v2/EXPERIMENTS.md).

Original source: [v2/README.md](v2/README.md).

## V3 equations

# V3 · Declining deference and an improving copied feature

V3 adds two calendar-time functions:

$$
d(t)=d_{\mathrm{floor}}+
\left(d_0-d_{\mathrm{floor}}\right)e^{-\lambda_dt},
$$

$$
Q(t)=Q_0+
\left(Q_{\max}-Q_0\right)
\left(1-e^{-\lambda_Qt}\right).
$$

Here $\lambda_d,\lambda_Q\ge0$, $0\le d_{\mathrm{floor}}\le d_0\le1$, and $Q_{\max}\ge Q_0$. The advice error is

$$
\sigma_A(t)=
\sigma_{A0}\frac{1+Q_0}{1+Q(t)}.
$$

The decision losses become

$$
L_{\mathrm{copy}}(t)=
[1-d(t)]\sigma_I^2
+d(t)\left[\sigma_A(t)^2+b_A^2\right],
$$

$$
\begin{aligned}
L_{\mathrm{blend}}(t)={}&[1-d(t)]^2\sigma_I^2\\
&+d(t)^2\left[\sigma_A(t)^2+b_A^2\right]\\
&+2\rho\,d(t)[1-d(t)]\sigma_I\sigma_A(t).
\end{aligned}
$$

$$
\mu_F(t)=\mu_{F,\mathrm{base}}+
k_{\mathrm{error}}L(t),
$$

$$
\dot F=\beta(F+A,\tau)A-
\left[\frac1\tau+\mu_F(t)\right]F,
\qquad
\dot A=\frac F\tau-\mu_AA.
$$

The resource closure and M0/M1 fecundity equations are those of V1. Fluxes still satisfy

$$
B=\beta A,\quad D=\mu_F(t)F+\mu_AA,\quad M=F/\tau,
\quad \dot N=B-D.
$$

Finite-horizon comparisons use

$$
r_T=\frac{\log[N(T)/N(0)]}{T},
\qquad
\Delta r_T=r_T(d_0,\tau)-r_T(0,\tau).
$$

These functions describe calendar time, not an individual's age or accumulated knowledge. Setting both rates to zero recovers the constant V1 mechanism.


Original source: [v3/EXPERIMENTS.md](v3/EXPERIMENTS.md).

Original source: [v3/README.md](v3/README.md).

## V4 equations

# V4 · Acquired culture, confidence and inherited strategies

Each inherited genotype is $g=(d,\tau)$, with maturation hazard $m=1/\tau$. There are two biological stages. Cognitive substates are a signed conviction score $z\in\{-H,\ldots,H\}$ and, for reinforcement learning, a trust score $r\in\{-2,\ldots,2\}$.

$$
F_g=\sum_{z,r}F_{g,z,r},\qquad
A_g=\sum_{z,r}A_{g,z,r},\qquad
N=\sum_g(F_g+A_g).
$$

A neutral conviction predicts either sign equally. For environmental truth $\theta\in\{-1,+1\}$, define

$$
c_\theta(z)=\frac{1+\theta\,\operatorname{sgn}(z)}{2}.
$$

## Endogenous adult advice

Adult belief accuracy and advice accuracy after transmission error $\varepsilon$ are

$$
q_A=\frac{\sum_{g,z,r}A_{g,z,r}c_\theta(z)}
{\sum_{g,z,r}A_{g,z,r}},
\qquad
q=\varepsilon+(1-2\varepsilon)q_A.
$$

The private cue accuracy $p$ is identical across candidate traits in a scenario. Followers choose adult information with probability $w_r$:

$$
\begin{aligned}
w_{\mathrm{fixed}}&=d,\\
w_{\mathrm{private}}&=0,\\
w_{\mathrm{oracle}}&=\mathbf1\{\max(q,1-q)>p\},\\
w_{\mathrm{RL}}(r)&=\frac{1}{1+e^{-\lambda_r r}}.
\end{aligned}
$$

The oracle can invert an anti-informative source; it has privileged access to actual reliability. Let $q_{\mathrm{eff}}=\max(q,1-q)$ for that oracle and $q_{\mathrm{eff}}=q$ otherwise.

$$
a_r=(1-w_r)p+w_rq_{\mathrm{eff}}.
$$

## Acquisition, retention and correction

Let $\operatorname{clip}_H$ restrict scores to $[-H,H]$. At a juvenile encounter, private and adult correctness bits are independently drawn:

$$
i\sim\operatorname{Bernoulli}(p),\qquad
a\sim\operatorname{Bernoulli}(q),\qquad
f\sim\operatorname{Bernoulli}(w_r).
$$

The endorsed correctness is $y=a$ if $f=1$ and $y=i$ otherwise. Main-policy conviction updates are

$$
z'=\operatorname{clip}_H\!\left[z+\theta(2y-1)\right].
$$

In the public-only ablation, use $i$ in place of $y$ for storage, while public action may still copy adults. Adults retain their juvenile score and receive private corrections at rate $\nu_A$.

For RL, objective feedback is available with probability $f_{\mathrm{feedback}}$:

$$
r'=
\begin{cases}
\operatorname{clip}_2[r+(2a-1)],&\text{feedback observed},\\
r,&\text{otherwise}.
\end{cases}
$$

These event probabilities define conservative transition generators $Q_F$ and $Q_A$. Conviction is an endorsement score, not a calibrated log-likelihood.

## Vital rates and demographic equations

$$
\mu_{F,r}=\mu_{F,0}+k_F(1-a_r),
\qquad
\mu_A(z)=\mu_{A,0}+k_A[1-c_\theta(z)].
$$

$$
S(N)=\frac{S_0}{1+N/K},
\qquad
b_z(N)=
[\beta_0+\beta_1c_\theta(z)]
\frac{S(N)}{K_S+S(N)}.
$$

Using column vectors over cognitive states, neutral newborn state $e_0$, and maturation matrix $M=mI$,

$$
\begin{aligned}
\dot{\mathbf F}_g
&=Q_{F,g}\mathbf F_g
-\operatorname{diag}(m_g+\mu_{F,r})\mathbf F_g
+e_0\,\mathbf b_g^\top\mathbf A_g,\\
\dot{\mathbf A}_g
&=Q_{A,g}\mathbf A_g+M_g\mathbf F_g
-\operatorname{diag}(\mu_A)\mathbf A_g.
\end{aligned}
$$

The reset ablation replaces $M_g\mathbf F_g$ by $m_g e_0\mathbf1^\top\mathbf F_g$. No factual knowledge is copied genetically into newborns.

$$
B=\sum_g\mathbf b_g^\top\mathbf A_g,\quad
D=\sum_g\left(\boldsymbol\mu_{F,g}^\top\mathbf F_g+
\boldsymbol\mu_A^\top\mathbf A_g\right),\quad
M=\sum_gm_gF_g,\quad
\dot N=B-D.
$$

Uniform genetic mutation among $G$ candidate classes replaces each class's inherited birth input by

$$
\widetilde B_g=(1-\eta)B_g+\frac{\eta}{G}\sum_hB_h.
$$

## Growth, invasion and reproductive value

$$
r_T=\frac{\log[N(T)/N(0)]}{T}.
$$

For a resident equilibrium with fixed advice and resources, let $J_m$ be the mutant's transient juvenile operator and $C_{A,m}$ its adult operator. The complete rare-mutant operator is

$$
G_m=
\begin{pmatrix}
J_m&e_0\mathbf b_m^\top\\
M_m&C_{A,m}
\end{pmatrix},
\qquad
s(g_m;g_r)=\max\operatorname{Re}\lambda(G_m).
$$

The mutant uses resident teachers and resource limitation. Its next-generation reproduction benchmark is

$$
\mathcal R_0=
\mathbf b_m^\top(-C_{A,m})^{-1}
M_m(-J_m)^{-1}e_0.
$$

Conditional newborn survival under that fixed information environment is

$$
P_{\mathrm{mat}}=m\,\mathbf1^\top(-J)^{-1}e_0.
$$

For a changing resident environment, the recorded finite-window mutant rate is

$$
s_T=
\frac{\log\|\mathbf x_m(T)\|-\log\|\mathbf x_m(t_b)\|}
{T-t_b},
$$

computed by integration and log normalization, not by averaging frozen eigenvalues.

## Cultural and recovery measurements

The high-depth score fraction and contrary-belief fraction are

$$
P_{\mathrm{deep}}=
\frac{\sum A_{z,r}\mathbf1\{|z|>3\}}{A},
\qquad
P_{\mathrm{wrong,deep}}=
\frac{\sum A_{z,r}\mathbf1\{|z|>3\}[1-c_\theta(z)]}{A}.
$$

They measure score persistence, not a diagnosis of dogmatism. After a shock at $t_s$, the recovery target and integrated accuracy deficit are

$$
q_{\mathrm{target}}=
\frac12+\frac12\left(q_{A,\mathrm{stable}}(T)-\frac12\right),
$$

$$
\mathcal D=
\int_{t_s}^{T}
\max\!\left[0,q_{A,\mathrm{stable}}(t)-q_A(t)\right]\,dt.
$$

The recovery target must be maintained for the declared observation window. Missing recovery is censored.

The Erlang robustness check divides childhood into $L$ exposure phases with transfer hazard $L/\tau$. Internal phase transfers conserve juvenile density; the mean maturation time without death remains $\tau$.


Original source: [v4/mathematical_model.md](v4/mathematical_model.md).

Original source: [v4/model_comparison.md](v4/model_comparison.md).

## V5 equations

# V5 · Private evidence, held conviction and information access

V5 retains two biological stages but separates a private-evidence score $u$ from a held-conviction score $b$:

$$
u,b\in\{-H,\ldots,H\},\qquad
F_g=\sum_{u,b}F_g(u,b),\qquad
A_g=\sum_{u,b}A_g(u,b).
$$

Every private-only learner retains childhood knowledge. Fresh private evidence moves both scores; accepted testimony moves only $b$. Newborns start at $(u,b)=(0,0)$.

## Advice and current judgment

Define the private probability of choosing the positive action and the correctness of a held belief:

$$
j(u)=\frac{1+\operatorname{sgn}(u)}{2},
\qquad
c_\theta(b)=\frac{1+\theta\operatorname{sgn}(b)}{2}.
$$

The adult pool supplies an endogenous positive recommendation probability

$$
q_+=\varepsilon+(1-2\varepsilon)
\frac{\sum_{g,u,b}A_g(u,b)j(b)}
{\sum_{g,u,b}A_g(u,b)}.
$$

For fixed deference, public behavior and its accuracy are

$$
p_+(u)=(1-d)j(u)+dq_+,
\qquad
a_F(u)=\frac{1+\theta[2p_+(u)-1]}{2}.
$$

Thus $d$ is the probability of choosing adult judgment when the private and adult signs disagree. Social acceptance also occurs on agreement in the main model.

## Information access and state transitions

With private access $a$ and effective information load $D$,

$$
\lambda_F=\frac{\nu_Ia}{D},\qquad
\lambda_S=\frac{\nu_S}{D},\qquad
\lambda_{A,0}=\frac{\nu_Aa}{D}.
$$

$D$ rescales exposure rates in the demographic model; it is not a model of complex reasoning.

A signed private cue $y\in\{-1,+1\}$ has actual positive-sign probability $\pi_I(t)$. Its transition is

$$
(u,b)\longrightarrow
\left(\operatorname{clip}_H(u+y),\operatorname{clip}_H(b+y)\right).
$$

Accepted testimony $s$ changes only held conviction:

$$
(u,b)\longrightarrow
\left(u,\operatorname{clip}_H(b+s)\right).
$$

Independent acceptance and action switches distinguish mechanisms:

$$
d_{\mathrm{memory}}=s_{\mathrm{memory}}d,\qquad
d_{\mathrm{action}}=s_{\mathrm{action}}d,
\qquad s_{\mathrm{memory}},s_{\mathrm{action}}\in\{0,1\}.
$$

Social positive and negative storage rates are respectively $\lambda_Sd_{\mathrm{memory}}q_+$ and $\lambda_Sd_{\mathrm{memory}}(1-q_+)$. Conflict-only storage multiplies them by $1-j(u)$ and $j(u)$, respectively. At $d=0$, the main retained-private model preserves $u=b$ exactly.

## Adult correction, freezing and auditing

$$
\lambda_A(b)=
\begin{cases}
\lambda_{A,0},&\text{continuous updating},\\
0,&\text{frozen conviction},\\
\lambda_{A,0},&\text{audit policy and }|b|<h,\\
\alpha_{\mathrm{audit}}\lambda_{A,0},&
\text{audit policy and }|b|\ge h.
\end{cases}
$$

These are specified query policies. Freezing is not assumed to emerge spontaneously.

The privileged confidence-gating comparator uses

$$
\gamma(u)=
\frac{1}{1+\exp[-|u|\operatorname{logit}(p)]},
\qquad
w(u)=\mathbf1\{\max(q,1-q)>\gamma(u)\}.
$$

It can invert anti-informative adult advice. Its true reliability access and bounded-score confidence proxy do not make it a full Bayesian learner.

## Mortality, reproduction and the two stages

$$
\mu_F(u)=\mu_{F,0}
+k_F[1-a_F(u)]+c_{\mathrm{query}}\lambda_F,
$$

$$
\mu_A(b)=\mu_{A,0}
+k_A[1-c_\theta(b)]+c_{\mathrm{query}}\lambda_A(b).
$$

$$
S(N)=\frac{S_0}{1+N/K},
\qquad
\beta(b,N)=
[\beta_0+\beta_1c_\theta(b)]
\frac{S(N)}{K_S+S(N)}.
$$

With conservative cognitive generators $Q_I,Q_S,Q_A$ and neutral newborn state $e_{00}$,

$$
\begin{aligned}
\dot{\mathbf F}_g
&=(Q_I+Q_S)\mathbf F_g
-\operatorname{diag}(m_g+\mu_F)\mathbf F_g
+e_{00}\,\boldsymbol\beta_g^\top\mathbf A_g,\\
\dot{\mathbf A}_g
&=Q_A\mathbf A_g+m_g\mathbf F_g
-\operatorname{diag}(\mu_A)\mathbf A_g,
\qquad m_g=\frac1{\tau_g}.
\end{aligned}
$$

The reset ablation transfers into $A(0,0)$ instead of preserving the joint score. Birth, death and maturation sums still satisfy $\dot N=B-D$.

$$
Q_{\mathrm{private}}=
\lambda_FF+
\sum_{g,u,b}\lambda_A(b)A_g(u,b),
\qquad
C_{\mathrm{query}}=c_{\mathrm{query}}Q_{\mathrm{private}}.
$$

No term directly rewards $d$, $\tau$ or freezing.

## Demographic and evolutionary measurements

$$
r_T=\frac{\log[N(T)/N(0)]}{T},
\qquad
\Delta r_T(d,\tau)=r_T(d,\tau)-r_T(0,\tau).
$$

The rare-mutant operator, conditional survival and changing-environment log-growth definitions are those of V4, now over joint $(u,b)$ states. Mutants share resident teachers and resources.

$$
s(g_m;g_r)=\max\operatorname{Re}\lambda(G_m),
\qquad
P_{\mathrm{mat}}=m\,\mathbf1^\top(-J)^{-1}e_{00}.
$$

High-depth and wrong high-depth fractions use the indicator $\mathbf1\{|b|>2\}$. Recovery uses the matched stable-baseline target and deficit integral defined in V4.

## Actual fact repertoires

The separate cohort companion carries arrays of $D$ independent facts, with private and held scores $(u_j,b_j)$ for each context $j$. The same private and social transitions apply per visited fact. Confidence-qualified tutors satisfy

$$
|b_{j,\mathrm{teacher}}|\ge2.
$$

Selection uses confidence rather than true correctness. If no qualifying teacher exists, no testimony is supplied. In this companion neutral teachers abstain; the main demographic model instead treats a neutral expressed sign as a fair tie. Search across the cohort has no cost in the executed follow-up. Cohort learning outcomes are not demographic fitness.

## Exact Bayesian information benchmark

Let the calibrated prior be $q_0=\Pr(\theta=+1)$, the private cue accuracy be $p$, and $k$ positive cues be observed in $n$ independent draws:

$$
P_+(k)=\binom nkp^k(1-p)^{n-k},
\qquad
P_-(k)=\binom nk(1-p)^kp^{n-k}.
$$

Optimal expected decision accuracy is

$$
A_{\mathrm{Bayes}}(n)=
\sum_{k=0}^{n}
\max\left[q_0P_+(k),(1-q_0)P_-(k)\right].
$$

For valid cost-free independent evidence in a stable world,

$$
A_{\mathrm{Bayes}}(n+1)\ge A_{\mathrm{Bayes}}(n)
\ge A_{\mathrm{Bayes}}(0)=q_0.
$$

The bounded unit-step score comparator can lose accuracy when it misweights weak cues relative to a strong prior. This benchmark isolates that limitation; it does not model cultural demography, changing truth or query cost.


Original source: [v5/mathematical_model.md](v5/mathematical_model.md).

Original source: [v5/model_comparison.md](v5/model_comparison.md).

Original source: [v5/repertoire_model.md](v5/repertoire_model.md).

Original source: [v5/bayesian_benchmark.md](v5/bayesian_benchmark.md).

## V6 equations

# V6 · Developmental plasticity and stochastic environmental change

V6 extends V5's retained private evidence and held convictions. All rates and population units are hypothetical. The adult reduction in plasticity is an imposed mechanism, not an evolved result.

## States, learning and inheritance

For inherited traits $g=(d,\tau)$, the juvenile and adult densities are $F_g(u,b)$ and $A_g(u,b)$, with private evidence $u$ and held conviction $b$ on the integers from $-H$ to $H$. Default $H=3$. These are cognitive substates of exactly two demographic stages. Births enter $(u,b)=(0,0)$; maturation transfers both ledgers unchanged, irreversibly, at rate $m=1/\tau$. Offspring inherit their parent's trait pair; there is no mutation in the present isolated runs or rare-mutant analysis.

Private cues have the same accuracy $p=0.65$, exposure rate $\nu_F=\nu_A=1$, and memory capacity at every age and trait pair. A cue is encoded with probability $\eta_F=1$ in juveniles and $\eta_A\in\{0,0.1,1\}$ in adults. Thus the successful private-update hazards are

$$
\lambda_F=\eta_F\nu_F\frac{\mathrm{access}}{\mathrm{load}},
\qquad
\lambda_A=\eta_A\nu_A\frac{\mathrm{access}}{\mathrm{load}}.
$$

A successful private cue shifts both ledgers one signed step, clipped only at the declared memory boundaries. Failure to encode leaves the state unchanged. This probability thinning is mathematically equivalent to a reduced private update rate in this model; it does not establish a biological distinction between attention, access and plasticity. Exposure costs, if enabled, are charged on the unthinned cue rate. Default query cost is zero to isolate accuracy consequences.

Adults advise according to their held conviction. Define

$$
j(z)=\frac{1+\operatorname{sgn}(z)}{2},
\qquad
q_+=\varepsilon+(1-2\varepsilon)
\frac{\sum_{g,u,b}A_g(u,b)j(b)}{\sum_{g,u,b}A_g(u,b)}.
$$

Neutral scores choose each sign with equal probability. With no adults, advice is unavailable. A juvenile's public positive action probability is

$$
a_+(u)=(1-d)j(u)+dq_+.
$$

Accepted testimony, at rate $d\nu_S/\mathrm{load}$, shifts only $b$. This retains V5's bundled action substitution and memory acceptance; it is not a clean identification of conflict-only deference. Adults express $j(b)$ and do not express juvenile deference. With $\eta_A=0$, an adult retains its state after maturation, but culture can still change through adult death and juvenile recruitment.

## Random environment

Truth $\theta(t)\in\{-1,+1\}$ switches sign at the jump times of a homogeneous Poisson process:

$$
\Pr\{\theta(t+h)=-\theta(t)\mid\theta(t)\}
=\kappa h+o(h),
\qquad
\Delta t\sim\operatorname{Exponential}(\kappa).
$$

$\kappa$ has units of inverse model time. Zero means a fixed environment. The private cue's probability of a positive sign is

$$
\pi_I(t)=\frac{1+\theta(t)(2p-1)}{2}.
$$

For every positive hazard, the environment's stationary probabilities are one half for each truth sign. Its persistence changes with the hazard:

$$
\mathbb E[\theta(t)\theta(0)]=e^{-2\kappa t}.
$$

Thus comparisons across positive hazards change temporal predictability, not the long-run fraction of positive truths.

Every matched population and the rare mutants share the same event times within a seed. Events change truth and the private cue channel together. This is environmental randomness only; cultural transitions and demography are conditional deterministic density equations. No finite-population extinction is simulated.

## Demography

Let $c_\theta(b)=[1+\theta\operatorname{sgn}(b)]/2$ and let $c_F(u)$ be the probability that the juvenile public action is correct. Conservative learning generators $Q_F(q_+,\theta)$ and $Q_A(\theta)$ implement the transitions above. With column-state convention,

$$
\dot F_g=
\left[Q_F-\operatorname{diag}(m+\mu_F)\right]F_g
+e_{00}\sum_{u,b}\beta(b,N)A_g(u,b),
$$

$$
\dot A_g=
\left[Q_A-\operatorname{diag}(\mu_A)\right]A_g+mF_g.
$$

The payoff and resource rules are inherited from V5:

$$
\begin{aligned}
\mu_F(u)&=\mu_{F,0}+k_F[1-c_F(u)],\\
\mu_A(b)&=\mu_{A,0}+k_A[1-c_\theta(b)],\\
\beta(b,N)&=[\beta_0+\beta_{\mathrm{skill}}c_\theta(b)]
\frac{S(N)}{K_S+S(N)},\\
S(N)&=\frac{S_0}{1+N/K}.
\end{aligned}
$$

The displayed equations use the default zero query cost. The source supports the V5 additional query-hazard terms. No direct reward is given to deference, delayed maturation or rigidity. The stage totals satisfy

$$
\dot F=B-M-D_F,\qquad
\dot A=M-D_A,\qquad
\dot N=B-D_F-D_A.
$$

## Fixed equilibria versus stochastic regimes

When $\kappa=0$, a fixed equilibrium must satisfy the full demographic-cultural residual, not just a near-flat total population. Reversing both truth and all score signs leaves the equations unchanged: the two fixed environments have mirrored belief distributions and equal abundance equilibria under symmetric initial conditions. Unequal carrying capacities are not inserted to manufacture a difference.

For $\kappa>0$, trajectories continue to fluctuate. We estimate finite-window, post-burn-in summaries and distributions:

$$
\bar N=\frac{1}{T-t_b}\int_{t_b}^T N(t)\,dt,
\qquad
r_T=\frac{\log[N(T)/N(0)]}{T}.
$$

Neither is automatically an invariant distribution or a long-run evolutionary fitness. Eight independent environmental seeds provide path SD and Monte Carlo SE; deterministic cases have no sampling uncertainty. Recovery measures first sampled adult accuracy of at least $0.75$ after a flip, before the next flip. Unresolved events are censored; success fractions are reported separately. The sampling interval is four model-time units.

## Conditional rare-mutant growth

A resident with $d_r=0.5,\tau_r=3$ supplies the resource and adult advice environment. Mutants do not affect either. At every Runge–Kutta stage, integrate

$$
\dot x_m=G_m[N_r(t),q_r(t),\theta(t)]x_m.
$$

After periodic normalization, accumulate log abundance and calculate

$$
s_m=\frac{\log\|x_m(T)\|_1-\log\|x_m(t_b)\|_1}{T-t_b},
\qquad
s_{\mathrm{relative}}=s_m-
\frac{\log[N_r(T)/N_r(t_b)]}{T-t_b}.
$$

The dashboard distinguishes absolute and resident-relative invasion growth. The self-mutant's relative rate is zero up to numerical error. In a stochastic finite window the resident's absolute rate need not be zero. Positive values do not demonstrate fixation, an ESS, or a historical adaptation.

## Scope

Private signal accuracy is held fixed, but stage-specific updating is prescribed. Finite bounded scores can misweight correlated or unequal evidence. Adults do not independently choose their plasticity, and Bayesian trust calibration is not solved here. The extension can show conditional cultural retention/adaptation tradeoffs, not that childhood dogmatism is a distinct evolved mechanism. Differences across environmental hazards concern stochastic responses; stable environments can yield identical abundance with different cultural signs.


Original source: [v6/mathematical_model.md](v6/mathematical_model.md).

Original source: [v6/research_contract.md](v6/research_contract.md).

## Further work

See [research proposals](proposals/RESEARCH_PROPOSALS.md). These are proposed, unexecuted investigations.
