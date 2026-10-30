# V6 extension · Noisier adult information about the current situation

This extension preserves the original V6 as a separate comparison. It changes the advice decision layer and specifies how a situational recommendation is stored as general knowledge. No interior optimum is imposed.

## General knowledge and local circumstances

Global truth $\theta(t)\in\{-1,+1\}$ follows V6's Poisson switching process. The two memory scores $u$ and $b$ concern this general truth. Newborns have $u=b=0$; maturation transfers both unchanged. Juvenile encoding remains $\eta_F=1$, adult encoding $\eta_A=0.1$, and private global-cue accuracy remains $p=0.65$. All demographic constants are unchanged.

For each decision, a fresh local circumstance $z\in\{-1,+1\}$ makes the correct action $\theta z$. A juvenile observes $z$ with accuracy $p_F=0.9$; an advising adult observes it with accuracy $p_A\in\{0.55,0.70,0.85\}$. Thus every main scenario makes the adult's **current-situation information worse**. The adult can still possess better accumulated general knowledge. Cue errors are independent conditional on $z$ and renewed across decisions. Local observations are analytically averaged; no additional demographic state is introduced.

Let $U$ denote the correctness of a juvenile's accumulated private general judgment and $Q$ the correctness of the current adult testimony about general truth, including V6's fixed transmission error. Current-action source accuracies are

$$
P_I=(1-p_F)+(2p_F-1)U,
\qquad
P_A=(1-p_A)+(2p_A-1)Q.
$$

The juvenile chooses the adult's action with probability $d$ and otherwise its own action. Hence

$$
P_{\mathrm{public}}=(1-d)P_I+dP_A,
\qquad
\mu_F=\mu_{F,0}+k_F(1-P_{\mathrm{public}}).
$$

The same $d$ applies when judgments disagree; no correctness oracle determines acceptance. Private ability and both context precisions remain fixed within each sweep. Adult own-task payoffs retain the original global task. This explicitly models advice for juvenile-specific situations rather than degrading all adult cognition.

## How accepted advice affects later adult beliefs

If adults recommend actions without explicitly transmitting the general fact, a juvenile infers general knowledge by combining the recommended action with its own observation of the local circumstance. The two independent local observation errors disagree with probability

$$
\delta=p_F(1-p_A)+(1-p_F)p_A.
$$

If adult testimony about global truth recommends the positive sign with probability $q_+$, the inferred sign written to the conviction ledger has probability

$$
q_{+,\mathrm{stored}}=\delta+(1-2\delta)q_+.
$$

Accepted testimony moves $b$ one signed step at rate $d\nu_S$; it does not change private evidence $u$. This decoding uncertainty is derived from the observation process, not an arbitrary penalty proportional to deference. Private cues continue to update both ledgers. The **clean-factual-teaching ablation** transmits the general fact explicitly, replacing the stored probability by $q_+$. Action-only and memory-only ablations separate current substitution from storage.

## Demography and conditional invasion

The same conservative generators and two-stage equations apply:

$$
\dot F_g=[Q_F-\operatorname{diag}(1/\tau+\mu_F)]F_g+e_{00}B_g,
\qquad
\dot A_g=[Q_A-\operatorname{diag}(\mu_A)]A_g+F_g/\tau.
$$

Resources, adult mortality and fecundity retain the original V6 rules. Conditional mutants experience the resident's actual teachers and resources and the same environmental history. Population abundance maxima and conditional invasion maxima remain separate outcomes.

## Why noise does not guarantee an interior optimum

With fixed final source accuracies, expected correctness is affine in $d$:

$$
\frac{\partial P_{\mathrm{public}}}{\partial d}=P_A-P_I.
$$

If the adult is always worse, the best copying probability is zero; equal accuracies give neutrality. An intermediate optimum requires an additional nonlinearity, such as an effect of present copying on future cultural quality, demographic composition or performance across environments. Here those possibilities are measured through explicit cultural and demographic dynamics; no term is added solely to create an interior maximum.

A context-dependent policy can choose different sources in different situations even if the best constant $d$ lies at a boundary. This experiment evaluates fixed inherited propensities, not a fully optimized confidence-sensitive learner. An interior grid maximum, if found, is not proof of fixation, an ESS or historical childhood dogmatism.
