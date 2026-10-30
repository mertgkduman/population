# V5 controlling question and predeclared design

V4 did find a stable-environment benefit of retaining socially acquired knowledge. V5 asks whether that benefit strengthens when learning a complex environment alone entails noisy, sparse or costly evidence, and whether freezing convictions is advantageous compared with competent individual learners who ALSO retain their knowledge.

Continue the installed Codex gsd-spike --quick adapter (Core1.14.0), without project planning or deployment. New branch v5-information-access, parent40187b0. Three focused quick experiments009–011 reuse V4 literature and verification conventions. Four research roles continue: source/gap review, mathematical design (root), implementation/verification (root plus independent reviewer), dashboard (bounded helper).

## Selected mechanism, before experiments

Two biological stages F,A per genotype(d,tau). Each stage has a joint private-evidence score u and held-conviction score b, both integers[-H,H]. These are cognitive substates, not extra life stages. A fresh private cue moves both u and b one step toward its sign. Juvenile social encounters accept an adult sign into b with probability d; u is unchanged. At an action requiring a decision, the juvenile uses adult judgment with probability d and its accumulated private judgment sign(u) otherwise. Thus d is P(override | disagreement). At u=0 the private choice is a fair tie. Source acceptance also occurs when judgments agree; that separate convention is explicit. Adult behavior/advice comes from sign(b). Adults' accuracy is endogenous. All newborns start(u,b)=(0,0); maturation retains both scores unless an explicitly labeled reset ablation is selected.

Private-only d=0 keeps childhood knowledge into adulthood. It is not forced to relearn from scratch. Cognitive processing, score capacity, cue quality and information access are identical across genotypes within a scenario. Adult expertise emerges from previous juvenile and adult experience; it is not granted by age. Cultural history affects offspring through testimony, not by genetically copying factual beliefs.

Adult architectures: retained+updating (main), frozen conviction (no adult private queries, an explicitly imposed policy—not emergent dogmatism), confidence-based audit (full query rate at low conviction, occasional audits at high conviction), and reset-at-maturation (causal ablation). An oracle confidence-gating comparator uses true current adult reliability and the private score likelihood proxy; label its privileged information and finite-memory approximation. It is not full Bayesian optimal learning.

Private evidence opportunities have rate nu_I*access/D. Social transmission has rate nu_S/D. D is an effective repertoire/information-load multiplier in an exchangeable-task approximation, not a simulated combinatorial world or cooperation game. Cue accuracy p is an environmental evidence property, fixed across d/tau; no genotype changes cognition. Explicit sample cost adds mortality c_query times actual query rate, including state-dependent auditing. No reward for d, tau or freezing itself. A zero-cost ablation isolates accuracy from sampling savings.

Birth/death/maturation use the V4 Monod closure and accuracy-linked vital rates. Juvenile mortality uses the probability of the current public action being wrong; adult mortality and fecundity use held-belief correctness. Maturation hazard1/tau; no direct developmental fecundity bonus.

## Predeclared hypotheses and controls

H1: Reduced private cue quality/access can increase the benefit of copying, but sparse teacher exposure or degraded endogenous culture can remove it. Test clean/noisy/sparse/repertoire scenarios with within-scenario matched d.
H2: Stable worlds can reward retained or frozen useful knowledge. Compare freezing against both d=0 retained knowledge and confidence-based auditing, not merely a reset strawman. No-cost and wrong-initial-culture controls may reverse the result.
H3: A temporary misleading private channel with unchanged truth can favor retention, while a true environmental reversal can make it harmful. Compare the two explicitly.
H4 (identification): With identical signed cue statistics and no truth-linked demographic filtering, an unchanged world with misinformation and a changed world must produce identical cognitive trajectories for learners without truth access. Different true accuracy alone does not mean the learner can distinguish the causes.
H5 (selection): Shared-culture invasion and explicit competition may disagree with homogeneous abundance rankings. Do not infer selection from separate-population grids.
H6: The private-only retained control has u=b exactly. With no samples or no adult access, no information may appear spontaneously. Zero payoff and zero query cost must make d demographically neutral. Frozen knowledge need not remain correct across generations because teachers are replaced.

Run pilot first, then a main factorial; refine only measured optima and convergence concerns. Preserve negative and boundary results. Use fresh seeds for random information/environment histories. Report costs separately from accuracy; frozen convictions are not evidence of an evolved dogmatism genotype. No inference of human genetic separability or historical adaptation.

## Identification amendments before broad sweeps

Independent review flagged that d links public action override and persistent source acceptance. A predeclared accept×override factorial (both/neither/action-only/storage-only), plus conflict-only storage, separates these pathways. Any tied-d advantage must be attributed to its surviving channel, not automatically to overruling private judgment. No-accept d0 private learners retain u=b exactly. D only rescales exposure rates; the report must not call that a mechanistic model of complex reasoning. Primary dt=.1 follows a pilot DOP853 comparison (.2 was less accurate for cognitive distributions); selected cases also use .05. These numerical choices were made before main results.
