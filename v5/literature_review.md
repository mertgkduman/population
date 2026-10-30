# V5 targeted literature review: costly evidence, cultural access, and retained conviction

**Search cutoff:** 2026-10-30  
**Completed:** 2026-10-30  
**Scope:** primary theory and experiments on costly private information, strategic social learning, information access in complex tasks, selective use of disconfirming evidence, evidence stopping, and distinguishing noise from environmental change.  
**Evidence ledger:** [`evidence/literature_sources.json`](evidence/literature_sources.json)  
**Relationship to V4:** this is a targeted extension, not a second comprehensive review. V4's cascade, adviser-trust, cultural-conservatism, age-structure, and developmental-schedule evidence remains in [`../v4/literature_review.md`](../v4/literature_review.md).

## Bottom line

The proposed V5 contrast is scientifically useful, but its strongest defensible question is narrower than “complex environments make adult convictions adaptive.” The model can test whether **endogenous, historically accumulated testimony can improve performance when private evidence is scarce, noisy, or costly, and when that benefit survives controls for retained private learning, query cost, and environmental reversal**. This is not a new general mechanism by itself. Costly individual learning, conditional social learning, selective copying, retained cultural knowledge, confidence-gated updating, and change-point learning all have established primary literatures. [VERIFIED: [Rogers 1988](https://doi.org/10.1525/aa.1988.90.4.02a00030); [Enquist et al. 2007](https://doi.org/10.1525/aa.2007.109.4.727); [Rendell et al. 2010](https://pmc.ncbi.nlm.nih.gov/articles/PMC2989663/); [Nassar et al. 2010](https://pmc.ncbi.nlm.nih.gov/articles/PMC2945906/)]

The decisive identification problem in the prose contract is that its single `d` controls both (1) whether adult testimony enters persistent conviction `b` and (2) whether a juvenile overrides `sign(u)` at a decision. A difference attributed to “adult accumulated conviction” could therefore be caused by testimony acquisition, action-level compliance, or their interaction. The current implementation resolves this at the experiment layer with independent `accept`, `override`, and `conflict_only` flags and a predeclared 2×2 ablation; those results must remain separate in reporting. A second problem is terminology: dividing both private and social opportunity rates by `D` implements shared evidence scarcity or repertoire load, not task complexity. It contains no multi-step task, recombination, dependency graph, or difficulty-dependent error process. [VERIFIED: [`research_contract.md`](research_contract.md); [`experiments/model.py`](experiments/model.py); INFERENCE from the specified transition rates]

**Contribution status before results:** potentially publishable as a disciplined **coupled cultural-demographic stress test** of retained endogenous testimony, especially if it establishes a non-obvious three-way interaction among private-access scarcity, adult cultural quality, and environmental change. It is not presently a new learning mechanism, a model of true task complexity, an evolved theory of dogmatism, or an identification model for misinformation. Novelty should rest on a result that survives the channel-splitting, zero-cost, retained-private, wrong-culture, reversal, and invasion controls below.

## Contract identification audit

| Contract object | What it actually identifies | What it does not identify | Required guardrail |
|---|---|---|---|
| `d` applied to testimony acceptance and action override | A package of cultural belief acquisition plus behavioral deference | Which channel caused a demographic or accuracy effect | **Addressed in design:** independent `accept`/`override` flags and 2×2 ablation; retain separate reporting |
| `D` dividing `nu_I` and `nu_S` | Lower per-task evidence encounter rates / shared information load | Intrinsic task complexity, compositional structure, or a larger learned repertoire | Call it **effective evidence scarcity/repertoire dilution**; do not infer complexity effects |
| `c_query` mortality per actual private query | A biological or opportunity cost of sampling | Cognitive difficulty or error severity | Report realized query counts and cost separately; include `c_query=0` |
| frozen adults | An imposed absorbing no-query policy | Evolved dogmatism or normatively optimal stopping | Compare with retained+updating, confidence audit, and an explicit value-of-information comparator |
| confidence audit | A hand-specified state-dependent sampling heuristic | Bayesian optimality | Label it heuristic unless derived from the same reward, hazard, and observation model |
| oracle confidence gate | A privileged reliability comparator with finite-memory proxy | Learner-accessible full Bayes | Keep “oracle” in every label and report its information advantage |
| temporary misleading cue channel | A learner-observed adverse data stream | Intentional deception or source-aware misinformation | Prefer “temporarily misleading private channel” unless a source/process variable is modeled |
| same cue history under unchanged vs changed truth | Observational equivalence for the learner | Cause identification from accuracy scored by an external observer | H4 is an impossibility control; add source metadata or truth feedback to make causes identifiable |

H4 is especially important. If the learner receives exactly the same signed cues and costs in two regimes, and neither its transition rule nor its observation includes the latent truth, then its cognitive path has the same distribution. Calling one path “misinformation” and the other “environmental change” changes the evaluator's accuracy label, not what the learner can infer. Change-point models distinguish noise from change only because they assume different likelihood structure and a hazard prior; they cannot identify two causes engineered to produce identical observation histories. [VERIFIED: [Nassar et al. 2010](https://pubmed.ncbi.nlm.nih.gov/20844132/); [Glaze et al. 2015](https://elifesciences.org/articles/08825); INFERENCE for the equivalence claim]

## Operational definitions

| Term | V5 operational meaning | Important exclusion |
|---|---|---|
| **Private-information access** | Rate at which a learner can obtain conditionally informative cues | Not cue accuracy and not task complexity |
| **Cue quality** | Conditional probability or likelihood of the cue given the current state | Not the number or cost of observations |
| **Sampling cost** | Fitness, mortality, time, or payoff foregone per observation | Not an intrinsic penalty for being an individual learner |
| **Effective information load `D`** | A divisor that spreads fixed learning opportunities over exchangeable targets | Not a compositional task or a literal repertoire unless targets are explicitly represented |
| **Adult accumulated conviction** | Adult `b` generated endogenously from earlier private and accepted social evidence | Not guaranteed expertise, independent evidence, prestige, or truth |
| **Behavioral deference** | Using an adult-recommended action when it conflicts with private judgment | Not necessarily private belief change |
| **Testimony acceptance** | Updating persistent `b` from an adult sign | Not necessarily immediate compliance |
| **Evidence stopping** | Ceasing or reducing sampling because its expected value no longer exceeds its cost | Not equivalent to being unable or unwilling to revise after diagnostic contrary evidence |
| **Dogmatism / rigidity** | Disproportionately weak updating to relevant counterevidence, beyond what follows from uncertainty and cost | Not any high-confidence belief or any frozen policy imposed by the analyst |
| **Misinformation** | Information that is false or misleading relative to the state, ideally with an identifiable source/process | A stochastic but correctly specified low-quality cue is simply noise |
| **Environmental change** | A change in the latent state or data-generating process | Not a temporary streak of surprising observations in an unchanged world |

## Targeted primary-source and mechanism map

Eleven new sources were selected to cover the V5 mechanism rather than repeat V4. Publication dates and identifiers were checked against Crossref, PubMed/PMC, and publisher or author full texts; all are before the cutoff. Full access details are in the evidence ledger.

| Primary source | Design and established mechanism | Direct V5 use | Boundary / critical counterexample |
|---|---|---|---|
| [Rogers 1988](https://doi.org/10.1525/aa.1988.90.4.02a00030) | Gene-culture model in which social learning can invade without raising equilibrium mean fitness | Separate strategy success from population improvement | Cheap copying is not automatically adaptive culture |
| [Enquist, Eriksson & Ghirlanda 2007](https://doi.org/10.1525/aa.2007.109.4.727) | “Critical social learning”: try social learning, then individually learn if the acquired solution is unsatisfactory | Closest prior mechanism to conditional audit after testimony | Social-first plus checking is already modeled; it fails when transmission is very unfaithful, environments very variable, or social learning relatively costly |
| [McElreath et al. 2005](https://doi.org/10.1016/j.evolhumbehav.2005.04.003) | Laboratory microsocieties used formal predictions that social reliance rises with task difficulty and falls with environmental change | Empirical motivation for the access/volatility factorial | The experiment motivates conditional use, not a fixed adult-override coefficient or `D` as complexity |
| [Rendell et al. 2010](https://pmc.ncbi.nlm.nih.gov/articles/PMC2989663/) | Restless multi-armed-bandit tournament with `INNOVATE`, `OBSERVE`, and `EXPLOIT`; heavy copying won even with equal move costs because performers filtered the displayed repertoire | Strong reason to distinguish social access from social cue quality and behavioral filtering | Removing performer filtering made social learning poor; winning invasion performance did not maximize monomorphic mean fitness |
| [Morgan et al. 2012](https://pubmed.ncbi.nlm.nih.gov/21795267/) | Experiments found adaptive modulation of social-information use by demonstrator number/consensus, learner confidence, task difficulty, and asocial cost | Empirical benchmark for uncertainty- and cost-sensitive deference | Supports conditional arbitration, not uniform lifelong copying or adult infallibility |
| [Muthukrishna et al. 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC3843838/) | Access to five rather than one model improved image-editing accumulation and preserved expert knot-tying across transmission chains | Positive empirical connection between access to multiple models and maintaining difficult skills | The task exposes multiple artifacts/models and permits information integration; V5's `D` does neither |
| [Fay et al. 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6452720/) | Paper-plane chains with one, two, or four prior models; larger access did not improve cumulative performance and smaller populations improved most | Mandatory counterexample to “more social access helps” | Extra inputs can overload selection or expose low-quality models when success filtering is unavailable |
| [Drugowitsch et al. 2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3329788/) | Diffusion evidence accumulation plus dynamic programming estimated observation costs in monkeys and humans; inferred costs were time-varying | Normative anchor for a value-of-information stopping comparator | A permanently frozen adult is not shown optimal merely because sampling costs exist |
| [Nassar et al. 2010](https://pmc.ncbi.nlm.nih.gov/articles/PMC2945906/) | Human change-point task and approximate Bayesian delta rule; unexpected outcomes receive more weight when attributed to a state change rather than persistent stochasticity | Direct benchmark for adaptive reopening after surprising evidence | Requires an assumed generative model and change hazard; surprising evidence is not itself proof of change |
| [Glaze, Kable & Gold 2015](https://elifesciences.org/articles/08825) | Normative leaky, non-absorbing evidence accumulation tuned to expected environmental hazard; human behavior adapted imperfectly | Motivates hazard-sensitive forgetting rather than irreversible bounds | Retained confidence should weaken with expected volatility; absorbing `b=±H` is a special assumption |
| [Ecker et al. 2011](https://doi.org/10.3758/s13423-011-0065-1) | Experiments orthogonally manipulated misinformation and retraction strength; corrections reduced but did not always eliminate continued influence | Empirical reason to measure persistence after a misleading interval and corrective evidence | Narrative correction is not equivalent to a binary cue channel, and persistence is not universal dogmatism |

### Reused V4 anchors, not counted as new targeted sources

- [Bikhchandani, Hirshleifer & Welch 1992](https://doi.org/10.1086/261849): public actions can become correlated and stop revealing independent private information. Adult signs therefore cannot be counted as independent samples without lineage tracking.
- [Behrens et al. 2008](https://doi.org/10.1038/nature07538): human learners update adviser fidelity and volatility; a learned trust state is an established mechanism.
- [Kappes et al. 2020](https://doi.org/10.1038/s41593-019-0549-2): participants underused the strength of disconfirming social opinions while responding to confirming strength, motivating an asymmetric-evidence test.
- [Anglin 2019](https://doi.org/10.1016/j.jesp.2019.02.004): across four studies, participants generally shifted beliefs with empirical evidence even when it challenged prior views; strong perseverance is not a safe default.
- [Ghirlanda, Enquist & Nakamaru 2006](https://doi.org/10.1086/508696) and [Acerbi, Enquist & Ghirlanda 2009](https://doi.org/10.1073/pnas.0908889106): cultural conservatism and developmental openness already emerge in transmission models, so imposed freezing is not a novel rigidity mechanism.

## What the literature says for each V5 theme

### 1. Costly individual information and the economics of social learning

There are three distinct economic advantages that should not be collapsed. First, social learning may avoid a direct private-learning cost (Rogers; Enquist et al.). Second, observing others may supply a **selected** rather than random sample: in Rendell et al., demonstrators performed their currently best-known behavior, and social learning deteriorated when that behavioral filtering was removed. Third, learners may condition information choice on uncertainty, task difficulty, consensus, and price (McElreath et al.; Morgan et al.). [VERIFIED: targeted primary sources above]

V5 implements the first advantage through `c_query` and potentially the second only indirectly. Adults advise `sign(b)`, but they are not selected as high performers at each encounter. Any benefit is therefore due to endogenous adult population composition and historical evidence, not the tournament's explicit “best item in repertoire” filter. This distinction is useful: if V5 still produces a benefit without performer selection, it isolates cultural memory/demographic filtering; it should not cite Rendell et al.'s outcome as if the mechanisms were identical. [INFERENCE grounded in the contract and Rendell et al.]

The critical comparison is not `d>0` versus an amnesic `d=0`. The contract correctly retains `u=b` for private-only learners. The remaining economic test is a decomposition:

1. accuracy with zero query cost;
2. realized private and social samples per life;
3. mortality or payoff cost paid;
4. adult cultural quality over time;
5. homogeneous abundance and rare-mutant invasion separately.

Rogers and Rendell et al. make the last separation mandatory: a strategy may invade while depressing population mean fitness, and a high-performing mixed-population strategy need not maximize monomorphic mean payoff. [VERIFIED: primary sources]

### 2. Task complexity, repertoire size, and social access

Muthukrishna et al. provide a positive result with genuinely structured tasks: learners had access to one or five prior models and attempted complex image-editing or knot-tying performances. Fay et al. provide the needed counterexample: on a paper-plane task, larger model sets exposed participants to more variants but did not improve cumulative performance, plausibly because useful selection was harder without success-filtering and additional inputs imposed information-processing demands. [VERIFIED: full texts]

This pair rules out a monotone “more teachers / harder task / more culture benefit” interpretation. Social access helps only if the learner can identify, combine, or preserve the useful information. In V5, lowering both cue streams by `D` changes evidence rate without representing more variants, recombination, task dependencies, or model choice. The honest interpretation is therefore **performance under information dilution**, not cumulative solution of a complex environment.

A useful later extension, outside the predeclared V5 mechanism, would represent `K` subskills with heterogeneous cue quality and correlated teachers. That would permit direct tests of repertoire size, selective access, bottlenecks, and recombination. It is not needed for the present stress test and should not be retrofitted after outcomes are seen.

### 3. Selective preservation and confirmation under noisy signals

The V4 evidence supports both selective resistance and broad evidence responsiveness. Kappes et al. found an asymmetry in using the **strength** of confirming versus disconfirming social opinions. Ecker et al. found continued influence after retraction, modulated by initial encoding and correction strength. But Anglin found that participants generally changed beliefs in the direction of empirical evidence across contested topics. [VERIFIED: primary studies]

V5's symmetric saturating score does not implement confirmation bias: a cue of either sign moves `b` one step toward its sign, conditional only on the same acceptance rule. Persistence can arise from accumulated magnitude, saturation, low access, or freezing. Those are inertia mechanisms, not preferential acceptance of congenial evidence. If confirmation is claimed, add a predeclared diagnostic comparison with `P(accept | cue agrees with b)` separated from `P(accept | cue conflicts with b)`; otherwise call the result **confidence-dependent persistence**.

### 4. Optimal stopping versus dogmatism

Sampling should stop when the expected gain from another observation is below its cost, given the current belief, time horizon, reward function, and environmental hazard. Drugowitsch et al. demonstrate how this can be formalized with dynamic programming and show that inferred evidence cost need not be constant over time. Glaze et al. show that unpredictable changes favor leaky, non-absorbing evidence accumulation whose discounting depends on expected hazard. [VERIFIED: primary studies]

The V5 frozen architecture has no decision rule comparing expected information value to cost; it is an analyst-imposed “never query after maturation” policy. It can be an informative endpoint but not evidence of optimal stopping or evolved dogmatism. The confidence audit is closer, yet still a heuristic unless the audit probabilities are derived from the same environment and fitness objective.

The minimum diagnostic is to compare policies at equal information budgets or equal realized costs. Otherwise frozen adults may win solely because they never pay `c_query`. The zero-cost ablation asks whether retained beliefs improve accuracy; a matched-query-budget comparison asks whether **when** evidence is sampled matters.

### 5. Misleading evidence versus real environmental change

Nassar et al. and Glaze et al. formalize the key distinction: an outlier in a stable process should usually have less influence than evidence diagnostic of a change point, but the learner needs a generative model—likelihoods, uncertainty, and a change hazard—to make that attribution. Ecker et al. additionally shows that labeled correction and source status can affect persistence after misinformation. [VERIFIED: primary studies]

V5's H3 comparison is valuable as an evaluator-side stress test: the same retention that protects against transient misleading evidence can delay adaptation after a true reversal. H4 correctly prevents a stronger epistemic claim. The model cannot “recognize misinformation” if its observation stream contains no source identity, truth feedback, causal cue, or likelihood difference that distinguishes misinformation from change.

The right outcome language is:

- “retention protects performance during a transient adverse cue regime”;
- “retention slows adaptation after latent-state reversal”;
- “the learner does not identify the cause under observational equivalence.”

Avoid “the learner detects fake information” or “distinguishes propaganda from real change.”

## Ranked tests that could add information beyond known mechanisms

1. **Split testimony acquisition from action override — predeclared and implemented.** Report all `accept × override` corners, plus `conflict_only` storage and the intended coupled continuum. This determines whether cultural memory, immediate compliance, or agreement-driven confidence amplification causes the effect. The ablation resolves the main causal underidentification only if results are not pooled back into one `d` effect.
2. **Separate accuracy value from sampling savings.** For every adult architecture, report `c_query=0`, realized query rates, cumulative costs, and an equal-cost/equal-query comparison. This decides whether freezing preserves knowledge or merely avoids mortality.
3. **Cross adverse evidence with true state, using identical observed histories.** Reuse exactly the same cue stream in unchanged-truth and reversed-truth runs with truth-linked filtering disabled. Matching cognitive trajectories validates H4; diverging trajectories indicate unintended truth leakage.
4. **Challenge endogenous culture, not only private cues.** Seed adult `b` correct, neutral, and wrong; vary adult replacement and teacher exposure. A social strategy that wins only from correct initial culture has not solved the bootstrapping problem.
5. **Test invasion and lineage correlation.** Compare homogeneous abundance with rare-mutant growth in a shared resident culture; then reduce the apparent sample size of repeated adult signs according to source lineage. This addresses Rogers-style frequency dependence and cascade correlation.

The first test is now built into the design; the next two remain essential for interpreting the present contract. The fourth and fifth are high-value robustness tests if computational scope permits. A multi-skill task, cooperation game, parent-offspring conflict, and individual reinforcement learner over the joint `(u,b,source)` state remain future mechanisms, not V5 claims.

## Critical counterexamples the results must survive

- **More social access can reduce performance.** Fay et al. found no general advantage of larger model sets and strongest improvement in smaller populations. [VERIFIED]
- **Social information succeeds partly because actions are selected.** Rendell et al.'s copying advantage collapsed when demonstrator performance no longer filtered what was observed. V5 adult signs do not automatically have that property. [VERIFIED]
- **Invasion success can oppose group performance.** Rogers and Rendell et al. both warn against treating population abundance or mean payoff as selection. [VERIFIED]
- **Environmental volatility can favor reopening.** Enquist et al., McElreath et al., Nassar et al., and Glaze et al. all make stable-world retention conditional on change rate. [VERIFIED]
- **Belief perseverance is not universal.** Anglin found substantial evidence-responsive updating; therefore frozen or saturated states are model assumptions, not a generic empirical law. [VERIFIED]
- **Agreement is not independent replication.** Shared cultural ancestry can make many adult signs one correlated signal; the present model does not explicitly track lineages. [VERIFIED: Bikhchandani et al. mechanism; INFERENCE for V5]
- **Stopping can be rational without rigidity.** High confidence plus costly information can make non-sampling optimal even for a fully revisable learner. [VERIFIED: Drugowitsch et al. mechanism]
- **A learner cannot classify observationally identical causes.** Without truth-linked feedback or different likelihoods, misinformation and reversal labels exist only for the analyst. [INFERENCE grounded in Nassar/Glaze generative models]

## Empirical-to-model connections

| Empirical/theoretical result | Minimal V5 observable | Informative comparison | Interpretation limit |
|---|---|---|---|
| Social reliance rises with uncertainty, task difficulty, or private cost | Social actions/accepted signs conditional on `|u|`, access, and cost | fixed `d` versus confidence-conditioned policy | `D` is not task complexity |
| Demonstrator behavior can filter high-payoff options | Accuracy of adult advice conditional on adult state and survival | random adult sign versus performance/survival-filtered adult pool | Adult age alone is not success bias |
| Multiple models sometimes preserve difficult skills | Adult sign diversity and learner accuracy under teacher exposure | one versus multiple accessible adults with controlled total samples | Sign-only advice cannot test recombination |
| Additional models can inhibit improvement | Accuracy as social exposure rises at fixed time/information budget | sparse, intermediate, dense adult encounters | More encounters are not necessarily more independent information |
| Disconfirming social opinion can be underweighted | Updates to `b` split by agreement with current sign | symmetric acceptance versus conflict-specific acceptance | Symmetric saturation is inertia, not confirmation bias |
| Corrections may reduce but not erase misinformation effects | Persistence half-life after adverse cue interval | retained, updating, audit, frozen | Narrative retraction evidence does not calibrate binary cues |
| Evidence costs induce stopping bounds | Accuracy, decision time/query count, and fitness | frozen/audit versus value-of-information or equal-budget policy | Winning frozen policy is not automatically optimal |
| Change-point probability raises learning rate | Update/recovery after surprise as a function of hazard | fixed retention versus hazard-sensitive leak/audit | Requires identifiable generative differences |
| Same observation histories imply same learner paths | State-by-state equality of `(u,b)` trajectories under paired histories | paired unchanged/reversed truth with identical cues | Accuracy may differ because truth is external |

## Existing-equivalence warnings

1. **Critical social learning already combines social acquisition with individual checking.** A testimony-first/audit-later policy is close to Enquist et al. unless V5's cultural-demographic feedback produces a distinct result.
2. **Confidence- and volatility-sensitive social arbitration already exists.** V4's Behrens/Diaconescu evidence and the Nassar/Glaze models cover learned reliability and hazard-sensitive updating.
3. **Retained cultural knowledge and developmental conservatism are established.** Freezing or saturating `b` is not new on its own.
4. **Costly information stopping is a normative decision problem.** A no-query adult policy is a boundary comparator, not a derived optimum.
5. **Repertoire size is not represented by slowing a single exchangeable task.** `D` changes opportunity rates only.
6. **Misinformation identification is not represented by scoring cues against hidden truth.** Identification needs learner-visible source/process evidence.
7. **A fixed scalar social propensity is less expressive than existing adaptive-strategy experiments.** V5's contribution must come from coupled endogenous culture and demography, not from the mere existence of social learning.

## Negative evidence and exclusions

- No targeted primary source establishes that adult conviction is generally more accurate than a competent individual's retained private evidence.
- No targeted primary source licenses `D` as a measure of true task complexity in this model.
- No targeted source makes freezing after maturation an evolved or Bayesian-optimal rule under the V5 objective.
- No targeted source implies that confirmation bias or correction failure is universal.
- No targeted source resolves cultural-lineage dependence by sampling more adults.
- The present design does not test cooperation, social coordination payoffs, parent-offspring conflict, prestige exchange, teaching effort, intentional deception, source identity, or compositional cumulative culture.
- No post-cutoff or unavailable future work was used. All eleven targeted records predate 2026-10-30, and full texts or author manuscripts were available for mechanism checking.

## Candidate paper claim, calibrated before results

The independent acceptance/override flags materially strengthen identification, but they do not by themselves create mechanism novelty. If the main effects survive the remaining required controls, the defensible claim is:

> In an age-structured cultural-demographic model with retained private learning and endogenous adult testimony, the value of juvenile deference depends jointly on evidence access, sampling cost, cultural initialization, and environmental change; separating belief acquisition from action override reveals which channel produces the effect.

That would be an incremental but coherent synthesis. Stronger claims—“complexity selects dogmatic adults,” “adult conviction beats individual judgment,” or “retention detects misinformation”—are not supported by the current mechanism. A null or reversal result would also be informative because the positive intuition is contradicted by Rogers-style frequency dependence, Fay et al.'s access result, and the volatility-sensitive learning literature.

## Verification note

Searches used primary publisher pages, DOI/Crossref metadata, PubMed/PMC, eLife, and author or institutional full-text copies. Mechanism descriptions in the table are source-backed. Statements labeled **INFERENCE** are model-design conclusions drawn from comparing those sources with [`research_contract.md`](research_contract.md), not claims made by the cited authors. The machine-readable dates, links, access status, and limitations are in the evidence ledger.
