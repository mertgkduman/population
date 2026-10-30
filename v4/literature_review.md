# V4 primary-literature review: developmental deference, culture, and demography

**Search cutoff:** 2026-10-30  
**Completed:** 2026-10-30  
**Scope:** primary theoretical, computational, and empirical work relevant to inherited juvenile deference, maturation, endogenous adult knowledge, belief persistence, evidence conflict, and demographic versus evolutionary fitness.  
**Evidence ledger:** [`evidence/literature_sources.json`](evidence/literature_sources.json)

## Bottom line before model selection

The literature does not support treating deference as a fixed, intrinsically beneficial trait. It separates at least four mechanisms: an inherited or developed propensity to use social information; learned trust in a particular source; a private belief updated from evidence; and a public action that may express conformity without private belief change. Simon's docility, Henrich and Gil-White's prestige, Bikhchandani et al.'s cascade, and Gavrilets et al.'s pluralistic ignorance occupy different parts of this mechanism space. Collapsing them into one scalar `d` would erase the very distinctions needed to explain when deference helps or harms. [VERIFIED: [Simon 1990](https://pubmed.ncbi.nlm.nih.gov/2270480/); [Henrich & Gil-White 2001](https://doi.org/10.1016/S1090-5138(00)00071-4); [Bikhchandani et al. 1992](https://doi.org/10.1086/261849); [Gavrilets et al. 2026](https://pmc.ncbi.nlm.nih.gov/articles/PMC12913015/)]

The strongest modelable gap is narrower than “combine culture and demography.” Age-structured social learning, endogenous learning schedules, memory, developmental plasticity, teaching, demographic filtering, prestige bias, and changing advice reliability all already have primary models. The defensible opportunity is to connect a two-stage demographic system to **experience-dependent source trust and explicit evidence conflict**, while keeping private belief separate from public copying and measuring both population growth and rare-mutant invasion. [VERIFIED: [Lehmann et al. 2013](https://doi.org/10.1111/evo.12040); [Deffner & McElreath 2022](https://doi.org/10.1371/journal.pone.0267204); [van den Berg et al. 2024](https://doi.org/10.1038/s41467-024-49530-4); [Maisonneuve et al. 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC11813578/)]

**Primary modeling recommendation:** use a juvenile-only inherited prior or learning-rate parameter for reliance on adult advice; allow realised trust to update from adviser prediction errors or inferred fidelity; carry a cultural belief or action tendency into adulthood; and let adult knowledge be a population state generated from past learning rather than an exogenous accuracy schedule. Do not impose a direct maturation-to-fecundity reward, do not encode adult rigidity as a genotype, and do not interpret demographic growth as invasion fitness. This recommendation follows the controlling V4 research contract and is designed to avoid the close equivalents catalogued below. [VERIFIED: [`research_contract.md`](research_contract.md)]

## Operational definitions

| Term | Operational meaning for V4 | What it is not | Evidence |
|---|---|---|---|
| **Docility** | Receptivity to social influence that can yield gross adaptive benefits while exposing a boundedly rational learner to socially imposed costs. | Automatic obedience, low intelligence, or altruism itself. | [Simon 1990](https://pubmed.ncbi.nlm.nih.gov/2270480/) [VERIFIED: PubMed abstract] |
| **Deference** | A decision to yield, copy, or substitute another's judgment in a particular encounter. It may be epistemic, reputational, or norm-driven. | A private belief, source quality, or a stable personality by definition. | [Morris et al. 2026](https://doi.org/10.1016/j.cognition.2026.106472) [VERIFIED: full author manuscript and PubMed] |
| **Prestige** | Freely conferred status generated when learners grant benefits or attention to obtain access to valued models; the distribution of deference can itself become a cue to model quality. | Dominance maintained by force or threat; source accuracy itself. | [Henrich & Gil-White 2001](https://doi.org/10.1016/S1090-5138(00)00071-4) [VERIFIED: publisher full text] |
| **Social-learning schedule** | Age- or stage-dependent allocation among vertical, oblique, horizontal, and individual learning. | A single lifelong copying probability. | [Lehmann et al. 2013](https://doi.org/10.1111/evo.12040) [VERIFIED: publisher abstract/full PDF] |
| **Developmental plasticity in social learning** | A programme that changes reliance on social information as a function of earlier learning experience. | Random fixed individual heterogeneity or an imposed monotone decay in copying. | [van den Berg et al. 2024](https://doi.org/10.1038/s41467-024-49530-4) [VERIFIED: official article and PDF] |
| **Demographic filtering** | Enrichment of adaptive behaviour in older age classes because survival depends on behaviour, even without superior older-person learning. | Proof that older advisers are intrinsically wiser. | [Deffner & McElreath 2022](https://doi.org/10.1371/journal.pone.0267204) [VERIFIED: full text] |
| **Informational cascade** | A sequential state in which observed earlier actions make it optimal for a later agent to ignore its own private signal. | Any correlated group behaviour or any majority preference. | [Bikhchandani et al. 1992](https://doi.org/10.1086/261849) [VERIFIED: publisher abstract] |
| **Herd behaviour** | Convergent actions; unlike a cascade, it does not imply that private information has become behaviorally irrelevant. | A synonym for informational cascade. | [Çelen & Kariv 2004](https://doi.org/10.1257/0002828041464461) [VERIFIED: AEA article] |
| **Belief rigidity / conservatism** | Reduced updating or openness to new cultural traits or disconfirming evidence. It can emerge culturally, developmentally, or metacognitively. | Political conservatism as such, or guaranteed irrationality. | [Ghirlanda et al. 2006](https://doi.org/10.1086/508696); [Acerbi et al. 2009](https://doi.org/10.1073/pnas.0908889106); [Rollwage et al. 2018](https://doi.org/10.1016/j.cub.2018.10.053) [VERIFIED: primary papers] |
| **Adviser fidelity / trust** | Estimated probability that a source's advice is helpful or accurate, potentially changing with experience and inferred volatility. | Prestige, authority, or a fixed true advice variance. | [Behrens et al. 2008](https://doi.org/10.1038/nature07538); [Diaconescu et al. 2014](https://doi.org/10.1371/journal.pcbi.1003810) [VERIFIED: primary papers] |
| **Private belief** | An internal estimate or attitude about the state or norm. | Public action, stated compliance, or a belief about what others believe. | [Gavrilets et al. 2026](https://pmc.ncbi.nlm.nih.gov/articles/PMC12913015/) [VERIFIED: full text] |
| **Second-order belief** | A belief about others' attitudes or approval. | The observed population action frequency. | [Gavrilets et al. 2026](https://pmc.ncbi.nlm.nih.gov/articles/PMC12913015/) [VERIFIED: full text] |
| **Cumulative culture / knowledge** | Adaptive non-genetic information that can accumulate across generations beyond what isolated individual learning would produce. | Any stable tradition or within-generation consensus. | [Lehmann et al. 2013](https://doi.org/10.1111/evo.12040); [Maisonneuve et al. 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC11813578/) [VERIFIED: primary papers] |

## Essential-reference map

Publication dates distinguish online-first from issue dates where both are available. All 13 essential references were published on or before the 2026-10-30 cutoff. [VERIFIED: Crossref, PubMed, and publisher records in the evidence ledger]

### 1. Simon (1990): docility as a net-benefit channel vulnerable to a social tax

**Record.** Herbert A. Simon, *A Mechanism for Social Selection and Successful Altruism*, *Science* 250(4988):1665–1668, published **1990-12-21**, DOI [10.1126/science.2270480](https://doi.org/10.1126/science.2270480), PMID 2270480. [VERIFIED: [PubMed](https://pubmed.ncbi.nlm.nih.gov/2270480/) and Crossref]

**Mechanism.** Docility is adaptive receptivity to social influence under bounded rationality. Social influence can induce genuinely costly altruistic conduct, but selection can sustain it only while the gross fitness benefit of docility exceeds the induced cost. [VERIFIED: PubMed abstract]

**V4 implication.** The natural parameter is not a direct reward for deference. It is an information-acquisition benefit paired with a possible cost from accepting bad or socially costly advice. A direct `+c*d` term would erase Simon's upper-bound logic. [INFERENCE grounded in Simon 1990]

**Boundary.** This is a conceptual evolutionary mechanism, not an age-structured learning model, an empirical estimate, or evidence that docility is genetically separable from cognitive ability. [VERIFIED: article scope]

### 2. Henrich and Gil-White (2001): prestige as an information-access exchange

**Record.** Joseph Henrich and Francisco J. Gil-White, *The evolution of prestige: freely conferred deference as a mechanism for enhancing the benefits of cultural transmission*, *Evolution and Human Behavior* 22(3):165–196, issue **May 2001**, DOI [10.1016/S1090-5138(00)00071-4](https://doi.org/10.1016/S1090-5138(00)00071-4). [VERIFIED: [publisher record](https://www.sciencedirect.com/science/article/pii/S1090513800000714) and Crossref]

**Mechanism.** Learners preferentially seek successful or knowledgeable models and confer attention or benefits to gain prolonged access. The aggregate distribution of freely conferred deference becomes an inexpensive cue for later learners. Prestige and dominance have different proposed causal bases. [VERIFIED: publisher full text]

**V4 implication.** Prestige should be modelled, if at all, as an endogenous cue generated by other learners' choices and possibly traded for teaching access. Treating adult age or social rank as equivalent to accuracy would hard-code a contested prediction. [VERIFIED: mechanism; INFERENCE for model use]

**Forward test.** Three- and four-year-olds preferentially learned from adults who had received bystander attention, with stronger within-domain transfer, but a Tsimane' field study found only weak evidence linking ethnomedicinal knowledge to prestige and no age–prestige association. [VERIFIED: [Chudek et al. 2012](https://doi.org/10.1016/j.evolhumbehav.2011.05.005); [Reyes-García et al. 2008](https://doi.org/10.1016/j.evolhumbehav.2008.02.002)]

### 3. Kaplan et al. (2000): embodied capital and delayed life history

**Record.** Hillard Kaplan, Kim Hill, Jane Lancaster, and A. Magdalena Hurtado, *A theory of human life history evolution: Diet, intelligence, and longevity*, *Evolutionary Anthropology* 9(4):156–185, **2000**, DOI [10.1002/1520-6505(2000)9:4<156::AID-EVAN5>3.0.CO;2-7](https://doi.org/10.1002/1520-6505%282000%299%3A4%3C156%3A%3AAID-EVAN5%3E3.0.CO%3B2-7). The authoritative metadata inspected in this session gives year but not a reliable day-level publication date. [VERIFIED: [Wiley record](https://onlinelibrary.wiley.com/doi/10.1002/1520-6505%282000%299%3A4%3C156%3A%3AAID-EVAN5%3E3.0.CO%3B2-7) and Crossref]

**Mechanism.** The embodied-capital account links a difficult, skill-intensive foraging niche to investment in learning and cognition, delayed productivity, intergenerational provisioning, and longevity. [VERIFIED: full paper abstract and article text]

**V4 implication.** A maturation trade-off mediated by acquired competence is already established theory. V4 can study whether deference changes knowledge acquisition and hence later performance, but a prescribed `beta_max(tau)` preparation bonus would merely restate the embodied-capital premise and violates the V4 contract. [VERIFIED: Kaplan mechanism and `research_contract.md`; INFERENCE on equivalence]

### 4. Bikhchandani, Hirshleifer, and Welch (1992): private evidence can disappear from actions

**Record.** *A Theory of Fads, Fashion, Custom, and Cultural Change as Informational Cascades*, *Journal of Political Economy* 100(5):992–1026, published **1992-10-01**, DOI [10.1086/261849](https://doi.org/10.1086/261849). [VERIFIED: [publisher record](https://www.journals.uchicago.edu/doi/abs/10.1086/261849) and Crossref]

**Mechanism.** Sequential agents observe predecessors' actions but not their private signals. Once public actions are sufficiently imbalanced, following can be rational even against one's private signal. Later actions then add no independent information, producing conformity that is fragile to new public evidence. [VERIFIED: publisher abstract and paper record]

**V4 implication.** Adult consensus is not equivalent to multiple independent samples. A model that lets juveniles average adult actions as independent evidence will systematically overstate information quality. Track signal dependence or a shared cultural lineage. [INFERENCE grounded in Bikhchandani et al. 1992 and Anderson & Holt 1997]

### 5. Ghirlanda, Enquist, and Nakamaru (2006): cultural evolution can select its own transmission rules

**Record.** *Cultural Evolution Develops Its Own Rules: The Rise of Conservatism and Persuasion*, *Current Anthropology* 47(6):1027–1034, **December 2006**, DOI [10.1086/508696](https://doi.org/10.1086/508696). [VERIFIED: [publisher record](https://www.journals.uchicago.edu/doi/abs/10.1086/508696) and Crossref]

**Mechanism.** In a copying model where openness itself can be transmitted, cultural dynamics favour individuals who are difficult to influence and effective at influencing others, driving rapid conservatism without requiring a genetic conservatism trait. [VERIFIED: publisher abstract and author manuscript]

**V4 implication.** Endogenous adult rigidity can emerge from cultural transmission. Encoding an adult-rigidity genotype would pre-empt this result and is forbidden by the V4 contract. [VERIFIED: Ghirlanda mechanism and `research_contract.md`]

### 6. Acerbi, Enquist, and Ghirlanda (2009): development can either entrench or preserve openness

**Record.** *Cultural evolution and individual development of openness and conservatism*, *PNAS* 106(45):18931–18935; online **2009-10-26**, issue date **2009-11-10**, DOI [10.1073/pnas.0908889106](https://doi.org/10.1073/pnas.0908889106), PMCID PMC2776418. [VERIFIED: [PNAS](https://doi.org/10.1073/pnas.0908889106), PubMed, and Crossref]

**Mechanism.** Social learning changes both cultural traits and preferences governing later copying. The model tends toward conservative individuals, but gradual enculturation by many models and a larger repertoire that takes time to acquire can maintain openness. [VERIFIED: full text]

**V4 implication.** A monotone decline in deference with calendar time is a special case, not a novel general mechanism. V4 should allow evidence-contingent reopening or increasing trust when adult advice proves reliable. [INFERENCE grounded in Acerbi et al. 2009]

### 7. Lehmann, Wakano, and Aoki (2013): learning order and stage duration coevolve

**Record.** *On optimal learning schedules and the marginal value of cumulative cultural evolution*, *Evolution* 67(5):1435–1445; online **2013-01-23**, issue date **2013-05-01**, DOI [10.1111/evo.12040](https://doi.org/10.1111/evo.12040). [VERIFIED: [Oxford Academic](https://academic.oup.com/evolut/article/67/5/1435/6851462), PubMed, and Crossref]

**Mechanism.** Individuals may pass through infant, juvenile, and adult stages; learning takes time away from other life-history components. Under conditions supporting cumulative culture, the evolutionarily stable sequence uses oblique social learning in infancy and a mixture of individual and horizontal social learning in juveniles. Oblique learning raises population information in the reported model, while horizontal learning does not. [VERIFIED: abstract and full PDF]

**V4 implication.** Endogenous learning schedules and stage lengths are existing theory. Novelty cannot rest on allowing deference to change with age or on coevolving a generic maturation time with social learning. [VERIFIED: mechanism; INFERENCE on equivalence]

### 8. Holte and Ohmann (2021): environmental change can reverse the value of costly childhood

**Record.** *Childhood in social learning models with changing environments: Implications for human evolution*, *BioSystems* 210:104555; online **2021-09-30**, issue **December 2021**, DOI [10.1016/j.biosystems.2021.104555](https://doi.org/10.1016/j.biosystems.2021.104555), PMID 34601073. [VERIFIED: PubMed, Crossref, and author-posted full text]

**Mechanism.** Across-generation simulations compare observation with innovation under a childhood cost. Social observation can generate greater resource acquisition despite a substantial childhood burden in sufficiently stable environments; the advantage shrinks and reverses when environmental change makes inherited knowledge unreliable. [VERIFIED: PubMed abstract and author-posted full text]

**V4 implication.** Stable/noisy/biased advice scenarios are not enough; the experiment needs an explicit timescale ratio between environmental change, cultural turnover, trust updating, and maturation. [INFERENCE grounded in Holte & Ohmann 2021]

### 9. Deffner and McElreath (2022): age structure creates filtering, not a universal elder advantage

**Record.** *When does selection favor learning from the old? Social learning in age-structured populations*, *PLOS ONE* 17(4):e0267204, published **2022-04-15**, DOI [10.1371/journal.pone.0267204](https://doi.org/10.1371/journal.pone.0267204), PMCID PMC9012401. [VERIFIED: [PLOS](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0267204), PMC, and Crossref]

**Mechanism.** Age structure does not remove Rogers' paradox: social learning can evolve without raising mean population fitness. Survival-dependent demographic filtering can enrich adaptive behaviour among older people. In individual-based simulations, copy-old evolves only when social learning is erroneous; copy-young can compromise between individual and social information under other conditions. [VERIFIED: full text]

**V4 implication.** Source age, source information quality, and survival filtering must be separate. The adult pool should become informative endogenously through selection and learning, not because the code labels adults accurate. [INFERENCE grounded in Deffner & McElreath 2022]

### 10. van den Berg, Vu, and Molleman (2024): unpredictable social value selects learned heterogeneity

**Record.** *Unpredictable benefits of social information can lead to the evolution of individual differences in social learning*, *Nature Communications* 15:5138, published **2024-06-15**, DOI [10.1038/s41467-024-49530-4](https://doi.org/10.1038/s41467-024-49530-4), PMCID PMC11180142. [VERIFIED: [official article](https://www.nature.com/articles/s41467-024-49530-4), PubMed, and Crossref]

**Mechanism.** When the usefulness of social information varies unpredictably between individuals or contexts, selection favours developmental programmes that update reliance on social learning from experience. Identical flexible programmes can then produce persistent individual differences. Low uncertainty instead favours rigid social or individual learning. [VERIFIED: official article and full PDF]

**V4 implication.** A heritable fixed `d` competing with a plastic strategy is already close to this model. The non-equivalent move is to study how a heritable juvenile prior or learning rate changes coupled cultural-demographic feedback and invasion, not simply to rediscover individual heterogeneity. [INFERENCE grounded in van den Berg et al. 2024]

### 11. Maisonneuve, Lehmann, and Mullon (2025): teaching and learning schedules coevolve

**Record.** *The coevolution of learning schedules and teaching enhances cumulative knowledge and drives a teacher–innovator syndrome*, *Proceedings of the Royal Society B* 292(2040):20242470, published **2025-02-12**, DOI [10.1098/rspb.2024.2470](https://doi.org/10.1098/rspb.2024.2470), PMCID PMC11813578. [VERIFIED: [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC11813578/), PubMed, and Crossref]

**Mechanism.** Time allocated to vertical, oblique, and individual learning coevolves with parental teaching effort. Teaching can accelerate vertical transfer, free time for individual innovation, raise cumulative knowledge, and generate a teacher–innovator association; sufficiently disruptive selection can produce transient producer/scrounger polymorphism and knowledge cycles. [VERIFIED: full text]

**V4 implication.** Endogenous adult knowledge plus teaching capacity is an existing combination. If V4 uses unlimited tutor access and no teaching effort, it must say so. If it adds teaching, novelty cannot be claimed merely from making adult knowledge endogenous. [INFERENCE grounded in Maisonneuve et al. 2025]

### 12. Gavrilets, Karl, and Gelfand (2026): action, attitude, and beliefs about others diverge

**Record.** *The cultural evolution of pluralistic ignorance*, *PNAS* 123(7):e2522998123; online **2026-02-13**, issue **2026-02-17**, DOI [10.1073/pnas.2522998123](https://doi.org/10.1073/pnas.2522998123), PMCID PMC12913015. [VERIFIED: [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC12913015/), PNAS/Crossref metadata]

**Mechanism.** A dynamic model separates public action, private attitude, and second-order belief, combining material payoff, conformity, cognitive dissonance, social projection, and cultural tightness. Pluralistic ignorance can arise from lagged attitude and belief updating even without deception or silence; loose and tight societies exhibit different transient and persistent mismatches. [VERIFIED: full text]

**V4 implication.** Public copying must not overwrite private belief automatically. A minimal V4 model can omit norm expression costs, but it should state whether an observed action is evidence of belief, strategic compliance, or both. [INFERENCE grounded in Gavrilets et al. 2026]

### 13. Morris, Shaw, and Liberman (2026): deference is evaluated against relative knowledge, not authority alone

**Record.** *Calibrated deference: Children's evaluations of responses to disagreement across knowledge gaps*, *Cognition* 272:106472; accepted **2026-01-28**, epub **2026-03-06**, issue **July 2026**, DOI [10.1016/j.cognition.2026.106472](https://doi.org/10.1016/j.cognition.2026.106472), PMID 41795475. [VERIFIED: [PubMed](https://pubmed.ncbi.nlm.nih.gov/41795475/), [full author manuscript](https://repositories.cdlib.org/content/qt1xk634dg/qt1xk634dg_noSplash_6bfde20069d9c64e8a75d202744c5e55.pdf), and Crossref]

**Mechanism and finding.** Across five studies with 1,289 children aged 4–12, children evaluated whether a character should defer after correction or persist. They tended to prefer deference when a teacher or peer likely knew more, but preferred persistence against an inexpert peer or a teacher lacking relevant access. Sensitivity was imperfect and continued developing. [VERIFIED: abstract and full manuscript]

**V4 implication.** The empirical target is calibrated, domain-specific deference. This paper measures children's evaluations of others, not their own belief updates, demographic outcomes, or inherited traits; it should constrain interpretation without being treated as a parameter estimate. [VERIFIED: study design; INFERENCE for scope]

## Mechanism matrix

| Mechanism | Representative primary evidence | Learner state | Source/adult state | Environmental dynamics | Demography / selection | Main result | Existing-equivalence warning for V4 |
|---|---|---|---|---|---|---|---|
| Net-benefit docility | Simon 1990 | Receptivity plus bounded rationality | Social influence | Complex environment implicit | Fitness accounting conceptual | Docility can carry socially imposed costs only below its gross benefit | Do not add a direct benefit of `d`; benefit must flow through information or behaviour accuracy. |
| Prestige-biased access | Henrich & Gil-White 2001; Chudek et al. 2012; Atkisson et al. 2012 | Model-choice bias | Skill/success plus received deference | Often static or task shifts | Evolutionary argument; lab learning outcomes | Deference distributions can guide whom to learn from | Prestige is already an endogenous social cue; age and accuracy cannot be collapsed. |
| Embodied-capital life history | Kaplan et al. 2000 | Acquired productive skill | Provisioning/older producers | Difficult extractive niche | Delayed reproduction and longevity | Learning investment can justify extended dependence | A direct `tau` fecundity reward is a close restatement and is barred by contract. |
| Sequential informational cascade | Bikhchandani et al. 1992; Anderson & Holt 1997; Çelen & Kariv 2004 | Private signal and posterior belief | Predecessors' public actions | Fixed hidden state per sequence | Payoff to correct choice, no biological demography | Correlated public actions can suppress private information | Counting actions as independent adult evidence silently recreates/strengthens cascades. |
| Cultural evolution of openness | Ghirlanda et al. 2006; Acerbi et al. 2009 | Openness / preference | Model traits and persuasion | Cultural repertoire and enculturation | Cultural dynamics; developmental timing | Transmission can generate conservatism or preserve openness | Adult rigidity need not be genetic; monotone `d(t)` is not novel. |
| Evolving learning schedule | Aoki et al. 2012; Lehmann et al. 2013 | Allocation among social/individual modes | Previous generation and peers | Social information stock | Stage lengths and schedules coevolve | Social-before-individual can support cumulative culture | Age-varying social learning plus maturation is established theory. |
| Childhood under environmental change | Holte & Ohmann 2021 | Observation vs innovation | Inherited social knowledge | Explicitly changing environments | Childhood cost and lifetime resources | Rapid change can reverse the social-learning advantage | Must compare timescales; stable advice alone is insufficient. |
| Demographic filtering by age | Deffner & McElreath 2022 | Adaptive/maladaptive behaviour and strategy | Age classes | Temporal/spatial change | Age-structured survival and reproduction | Older classes can be enriched for adaptive behaviour without universal elder wisdom | Endogenous adult quality via survival filtering already exists. |
| Experience-dependent social-learning plasticity | van den Berg et al. 2024 | Flexible developmental programme and realised reliance | Social-information payoff | Individual/context uncertainty | Evolution of programmes | Unpredictability generates persistent heterogeneity | A plastic `d` updated from experience is established; couple it to new feedback rather than relabel it. |
| Coevolving teaching and learning | Maisonneuve et al. 2025 | Vertical/oblique/individual allocation | Teaching effort and knowledge | Knowledge obsolescence | Lineage fitness, demography, mutation–selection | Teaching frees time for innovation and can produce producer/scrounger structure | Endogenous teaching plus adult knowledge is established. |
| Lagged private/public norm dynamics | Gavrilets et al. 2026 | Private attitude and second-order belief | Population actions/norms | Changing material benefit and tightness | Cultural dynamics, not biological invasion | Pluralistic ignorance arises from different update rates | Separate action, belief, and perceived norm; one state cannot identify the mechanism. |
| Calibrated epistemic deference | Morris et al. 2026 | Evaluation of warranted belief revision | Teacher/peer with manipulated access | One-shot factual disagreement | Developmental experiment, no fitness | Children sometimes favour defiance of an uninformed authority | Authority preference is conditional and cannot be a universal copying rule. |
| Learned adviser fidelity | Behrens et al. 2008; Diaconescu et al. 2014, 2020 | Reward estimates, fidelity, volatility, relative precision | Helpful/misleading adviser | Stable and volatile blocks | Trial payoff, no population demography | Humans update source fidelity and arbitrate social/private information | Fixed advice variance misses empirically supported trust learning. |
| Confirmation-weighted updating | Rollwage et al. 2018; Kappes et al. 2020 | Confidence and metacognitive sensitivity | Disagreeing opinion/evidence | Post-decision evidence | No population demography | Disconfirming evidence can receive less weight, especially with reduced metacognitive insight | Rigidity can arise in evidence integration, not only inherited deference or adult genotype. |

## Thematic synthesis and forward trace

### A. Docility, prestige, and calibrated authority

The theoretical chain is not “defer to elders.” Simon's docility supplies an adaptive channel for social information and a vulnerability to induced costs. Henrich and Gil-White add a model-selection mechanism in which freely conferred deference purchases access and becomes an indirect signal. Chudek et al. experimentally show that young children use bystander attention as such a cue, and Atkisson et al. show adult prestige-biased learning in a novel arrowhead task. Yet the Tsimane' evidence did not support a simple age–prestige mapping and only weakly supported a knowledge–prestige link; Morris et al. show that children can favour persistence against an uninformed teacher. [VERIFIED: [Chudek et al. 2012](https://doi.org/10.1016/j.evolhumbehav.2011.05.005); [Atkisson et al. 2012](https://doi.org/10.1177/147470491201000309); [Reyes-García et al. 2008](https://doi.org/10.1016/j.evolhumbehav.2008.02.002); [Morris et al. 2026](https://doi.org/10.1016/j.cognition.2026.106472)]

**Connection to a V4 mechanism.** Adult status may be a noisy prior on source quality. Direct prediction-error feedback should be able to override it. The clean test is a prestige/age prior crossed with realised advice fidelity, not an adult-age coefficient embedded inside accuracy. [INFERENCE grounded in the primary studies above]

### B. Developmental learning schedules and maturation

Aoki, Wakano, and Lehmann (2012) formalize evolutionarily stable learning schedules in discrete generations; Lehmann et al. (2013) add explicit infant, juvenile, and adult stages and coevolving stage lengths; Fogarty, Creanza, and Feldman (2019) show that demographic structure changes cultural outcomes; Deffner and McElreath (2020, 2022) connect population regulation, life history, and age-biased learning; Ammar, Fogarty, and Kandler (2023) show that memory changes the value of social learning; van den Berg et al. (2024) evolve developmental plasticity; and Maisonneuve et al. (2025) coevolve teaching with learning allocation. [VERIFIED: [Aoki et al. 2012](https://doi.org/10.1016/j.tpb.2012.01.006); [Fogarty et al. 2019](https://doi.org/10.1371/journal.pcbi.1006821); [Deffner & McElreath 2020](https://doi.org/10.1098/rstb.2019.0492); [Ammar et al. 2023](https://doi.org/10.1073/pnas.2310033120)]

**Connection to a V4 mechanism.** The developmental novelty threshold is high. V4 should not claim novelty for juvenile social learning, a decreasing copying schedule, social-before-individual learning, endogenous stage duration, or an adult knowledge state alone. A more defensible contribution is to ask how an inherited juvenile prior or trust-learning rate changes adult cultural quality and demographic filtering, while adult rigidity remains culturally emergent. [INFERENCE grounded in the forward chain and V4 contract]

### C. Conflicting evidence, correlated signals, and cascades

Bikhchandani et al. provide the canonical sequential model; Anderson and Holt observed rational cascades in most laboratory periods where the public imbalance made them possible; Çelen and Kariv elicited beliefs to distinguish a cascade from mere herd behaviour. These studies establish two modeling requirements: social observations are often statistically dependent, and public actions can stop revealing private evidence. [VERIFIED: [Anderson & Holt 1997](https://econweb.ucsd.edu/~jandreon/Econ264/papers/Holt%20Anderson%20AER%201997.pdf); [Çelen & Kariv 2004](https://doi.org/10.1257/0002828041464461)]

**Connection to a V4 mechanism.** Adult advice should contain an endogenous shared cultural component plus source-specific error. Independent adult noise and a common inherited belief must be separate. This makes “more adults agree” informative only to the extent that their evidence lineages are independent. [INFERENCE grounded in cascade theory]

### D. Belief rigidity and reinforcement learning of trust

Behrens et al. (2008) show that participants learn adviser fidelity with prediction errors and adjust to volatility using associative-learning machinery. Diaconescu et al. (2014) find that hierarchical models tracking adviser accuracy and the volatility of adviser intentions explain behaviour better than constant-rate alternatives; their 2020 work supports precision-weighted arbitration between social and individual learning. Hertz, Bell, and Raihani (2021) find immediate advice following is stronger than observational copying, conditional on trust, and reinforcement-learning fits divide participants into sustained social reliance versus reversion to trial-and-error. Pereg et al. (2024) distinguish informed advice-taking from a stable baseline bias to follow advice. [VERIFIED: [Behrens et al. 2008](https://doi.org/10.1038/nature07538); [Diaconescu et al. 2014](https://doi.org/10.1371/journal.pcbi.1003810); [Diaconescu et al. 2020](https://doi.org/10.7554/eLife.54051); [Hertz et al. 2021](https://doi.org/10.1098/rspb.2021.1414); [Pereg et al. 2024](https://doi.org/10.1038/s41539-024-00214-0)]

Rigidity need not be a low learning rate applied uniformly. Rollwage et al. find that radical belief endorsement is associated with lower metacognitive insight and smaller confidence shifts after disconfirming evidence in a perceptual task. Kappes et al. find that participants underuse the strength of others' disconfirming opinions while using confirming opinion strength, with a corresponding neural asymmetry. At the same time, belief perseverance is not universal: Anglin's four studies found participants generally moved with empirical evidence even when it challenged prior views, although evidence-quality evaluation could be biased. [VERIFIED: [Rollwage et al. 2018](https://doi.org/10.1016/j.cub.2018.10.053); [Kappes et al. 2020](https://doi.org/10.1038/s41593-019-0549-2); [Anglin 2019](https://doi.org/10.1016/j.jesp.2019.02.004)]

**Connection to a V4 mechanism.** A minimal learner needs two separable quantities: a baseline bias or prior to accept adult advice and an experience-dependent estimate of source fidelity. If rigidity is included, it should be tested as asymmetric evidence weighting or uncertainty-dependent learning, not assigned to adults as a separate inherited trait. [INFERENCE grounded in the primary studies and V4 contract]

## Existing-equivalence warnings

1. **Static or age-decaying deference is already covered.** Acerbi et al. model developmental conservatism; Lehmann et al. evolve age-dependent learning schedules; van den Berg et al. evolve experience-dependent reliance. A new exponential `d(t)` or a fixed/plastic strategy comparison is not a substantive novelty. [VERIFIED: cited primary models]
2. **Delayed maturation plus learning benefit is already embodied-capital theory.** Kaplan et al., Aoki et al., and Lehmann et al. connect learning investment to delayed production or life-history allocation. A prescribed fecundity bonus for longer `tau` is both non-novel and outside the V4 contract. [VERIFIED: cited primary models and `research_contract.md`]
3. **Adult knowledge endogeneity plus teaching is already modeled.** Maisonneuve et al. let knowledge, learning schedules, and teaching coevolve. V4 must add a distinct question—such as erroneous advice, trust learning, or demographic invasion—not merely an adult knowledge variable. [VERIFIED: Maisonneuve et al. 2025]
4. **Copy-old and demographic filtering are already modeled.** Deffner and McElreath derive when older age classes are more adaptive and when copy-old or copy-young evolves. Adult age cannot serve as V4's novel source-quality mechanism. [VERIFIED: Deffner & McElreath 2022]
5. **Cascades already explain conformity from rational evidence aggregation.** A model where juvenile private information is overwhelmed by correlated adult actions is an informational-cascade model unless it adds a materially different feedback. [VERIFIED: Bikhchandani et al. 1992]
6. **Cultural conservatism does not require a rigidity gene.** Ghirlanda et al. and Acerbi et al. obtain conservatism from cultural dynamics. An adult rigidity genotype would confound inherited juvenile deference with a known emergent cultural process. [VERIFIED: cited primary models]
7. **Volatility-aware trust learning is established.** Behrens et al. and Diaconescu et al. already model learned adviser fidelity and volatility. The novel unit must be the demographic/cultural feedback and invasion comparison, not the trust updater itself. [VERIFIED: cited primary studies]
8. **Public conformity is not private belief change.** Gavrilets et al. explicitly separate action, attitude, and second-order belief. A single cultural state cannot adjudicate cascades, pluralistic ignorance, or true belief revision. [VERIFIED: Gavrilets et al. 2026]

## Negative and null evidence that must survive model selection

- Social learning can evolve without improving mean population fitness; age structure does not remove Rogers' paradox. [VERIFIED: Deffner & McElreath 2022]
- A copy-old strategy is conditional rather than universal, and copy-young may be favoured as a compromise between fresh individual evidence and social information. [VERIFIED: Deffner & McElreath 2022]
- A long, costly childhood paired with social observation loses its advantage and can become disadvantageous when environments change rapidly. [VERIFIED: Holte & Ohmann 2021]
- Prestige is not a validated proxy for age or expertise in every setting: the Tsimane' field test found no age association and only weak knowledge evidence. [VERIFIED: Reyes-García et al. 2008]
- Prestige-biased learning can be domain-sensitive rather than a global halo. [VERIFIED: Chudek et al. 2012]
- Children do not uniformly endorse authority deference; they can prefer persistence when the teacher lacks relevant knowledge. [VERIFIED: Morris et al. 2026]
- Cascade conformity is fragile because later matching actions may contain no new private information. [VERIFIED: Bikhchandani et al. 1992]
- Uncertainty does not always produce plasticity: van den Berg et al. report rigid social or individual learning when uncertainty about social-information value is low. [VERIFIED: van den Berg et al. 2024]
- Advice does not have a single persistent effect: in Hertz et al., some learners maintained social reliance whereas others returned to trial-and-error; higher paranoia reduced immediate advice following. [VERIFIED: Hertz et al. 2021]
- Strong belief perseverance and correction backfire should not be assumed. Anglin found broad evidence-responsive updating despite some biased quality judgments, and the later correction literature has not found backfire to be a general response. [VERIFIED: Anglin 2019; [Wood & Porter 2019](https://doi.org/10.1007/s11109-018-9443-y)]
- Socially improved adaptation does not by itself prove higher invasion fitness, fixation, or an evolutionarily stable strategy. This is a distinction required by the V4 contract and by the frequency-dependent results in the learning literature. [VERIFIED: `research_contract.md`; Deffner & McElreath 2022]

## Empirical-to-model connections

| Empirical result | Minimal model object | Predeclared comparison | Interpretation limit |
|---|---|---|---|
| Bystander attention shifts children's model choice, strongest within domain. | Source-specific prestige prior, indexed by domain. | Prestige prior present/absent crossed with equal realised fidelity. | Does not show prestige is accurate or fitness-enhancing. |
| Children override an uninformed teacher when they have privileged knowledge. | Relative precision of private and adult evidence. | High/low private precision × high/low adult fidelity × authority label. | The study measures evaluation of third-party responses, not participants' own updating. |
| Humans infer changing adviser intentions and volatility. | Latent adviser-fidelity estimate and adaptive learning rate or precision. | Stable helpful, stable harmful, and switching adviser regimes. | Neural/computational fit does not identify a heritable parameter. |
| Sequential actions can trigger cascades. | Shared cultural-error component and observation order/dependence. | Independent adult signals versus copied/correlated adult signals at identical marginal accuracy. | Consensus size alone is not evidence independence. |
| Older classes can be adaptively enriched by survival. | Behaviour-dependent juvenile/adult survival with explicit stage transition. | Adult-source accuracy emergent versus externally fixed. | Enrichment is not proof of age causation or teaching. |
| Rapid environmental change reverses inherited-knowledge value. | Environmental hazard or autocorrelation timescale. | Environment half-life relative to trust-learning and maturation times. | A scenario result is not a historical inference about humans. |
| Advice following includes informed and baseline components. | Inherited prior/bias separated from learned fidelity. | Same prior with different feedback; same feedback with different prior. | Stable test–retest bias is not genetic heritability. |
| Public and private states can lag. | Separate private belief, expressed action, and optionally perceived norm. | Forced expression versus private update only. | A two-state demographic model can still have cultural states; do not call them demographic stages. |

## Ranked research gaps

### 1. Demography coupled to learned source fidelity under evidence conflict — highest priority

Existing models separately provide age-structured demography, flexible social-learning programmes, cascade dynamics, and adviser-fidelity learning. I found no primary paper in the traced set that jointly asks whether an inherited **juvenile** prior or learning-rate parameter invades when adult advice quality is itself produced by the resident culture and when social and private evidence can conflict. [MEDIUM confidence: broad targeted search plus forward citation tracing; absence claims remain provisional]

**Executable gap:** compare a fixed-deference baseline, a fidelity-learning juvenile, and a private-only learner in the same two-stage demographic environment; hold private accuracy fixed; make adult cultural quality shared at the resident equilibrium; compute demographic growth and rare-mutant invasion separately.

### 2. Identifiability of epistemic trust versus public conformity

Cascade, prestige, and pluralistic-ignorance models can produce the same observed action for different reasons. Many models and experiments observe choices but cannot identify whether the learner privately updated, complied for social reasons, or treated prestige as a prior. [HIGH confidence: mechanisms explicitly contrasted in Bikhchandani et al. 1992, Henrich & Gil-White 2001, and Gavrilets et al. 2026]

**Executable gap:** store private belief and public action separately and include conditions with no expression payoff, expression cost, and source-accuracy feedback. If V4 omits expression incentives, it must restrict conclusions to epistemic copying.

### 3. Independence-aware social evidence across generations

Classic cascades show why repeated actions from a shared information lineage are not independent; cumulative-culture models track knowledge stocks but seldom expose an explicit learner estimate of evidence dependence. [MEDIUM confidence: direct mechanism match, but the wider literature was not exhaustively enumerated]

**Executable gap:** compare equal marginal adult accuracy with independent adult signals, a common inherited cultural error, and mixtures of common plus idiosyncratic error. Test whether deference responds to apparent consensus and whether population culture becomes locked in.

### 4. Reopening after early enculturation

The openness literature often generates conservatism, while adviser-learning work allows rapid updating under volatility. Less is known about when a developmentally social learner can reopen a culturally entrenched belief after adult evidence reverses, especially across a maturation boundary. [MEDIUM confidence: synthesis of Acerbi et al. 2009, Diaconescu et al. 2014, and van den Berg et al. 2024]

**Executable gap:** reverse adult advice fidelity before versus after maturation and compare symmetric learning, confirmation-weighted learning, and uncertainty-gated learning.

### 5. Empirical calibration from developmental behaviour to biological fitness

The empirical deference and trust studies measure choices, evaluations, confidence, or task rewards; the evolutionary models specify survival and reproduction. Direct longitudinal estimates connecting childhood source trust to adult knowledge, mortality, and reproductive output are not present in the essential or forward-traced set. [MEDIUM confidence: negative evidence from the scoped review, not proof of global absence]

**Consequence:** V4 must remain a hypothetical mechanism study. It may establish mathematical possibility, boundary conditions, and invasion results under declared assumptions, but not a historical adaptation account or human parameter estimate.

## Full-text and cutoff audit

| Essential reference | Within cutoff? | Full text inspected? | Access note |
|---|---:|---:|---|
| Simon 1990 | Yes | Abstract only | Official PubMed abstract and metadata inspected; publisher full text was not openly available in the sources accessed. |
| Henrich & Gil-White 2001 | Yes | Yes | Publisher HTML/PDF content accessible. |
| Kaplan et al. 2000 | Yes | Yes | Publisher metadata plus a full article copy indexed by search; authoritative day-level publication date was not established, so only year is reported. |
| Bikhchandani et al. 1992 | Yes | Abstract plus working-paper/lab follow-up | Official publisher abstract inspected; final publisher full text was access-restricted. |
| Ghirlanda et al. 2006 | Yes | Yes, author manuscript | Official abstract plus author-posted manuscript; publisher final full text access-restricted. |
| Acerbi et al. 2009 | Yes | Yes | PNAS/PMC full text. |
| Lehmann et al. 2013 | Yes | Yes | Oxford Academic PDF indexed and inspected. |
| Holte & Ohmann 2021 | Yes | Yes, author-posted | PubMed abstract and author-posted CC BY copy; publisher page itself was access-restricted. |
| Deffner & McElreath 2022 | Yes | Yes | PLOS/PMC full text. |
| van den Berg et al. 2024 | Yes | Yes | Nature Communications open-access PDF/PMC. |
| Maisonneuve et al. 2025 | Yes | Yes | PMC full text. |
| Gavrilets et al. 2026 | Yes | Yes | PNAS/PMC full text; published 2026-02-13. |
| Morris et al. 2026 | Yes | Yes | Free author manuscript, PubMed, and publisher metadata; epub 2026-03-06, July issue. |

**Future-dated exclusion:** none of the essential references is later than 2026-10-30. Search results published after the cutoff were not used to substantiate the review. [VERIFIED: publication records in the evidence ledger]

## Method and confidence

The review began from the 13 mandated identifiers and verified metadata against Crossref, PubMed/Europe PMC/PMC, and official publisher records. It then followed citations forward and searched four targeted primary-study domains: docility/prestige, developmental learning schedules, evidence conflict/cascades, and belief rigidity/adviser learning. Search-provider results were treated as discovery aids; substantive claims above link to primary papers or official metadata. [VERIFIED: `evidence/literature_sources.json`]

**High-confidence findings:** mechanisms and publication metadata for the 13 essential references; existence and broad results of the named forward primary studies.  
**Medium-confidence findings:** ranked gaps and claims about what the combined literature has not yet integrated, because no finite search proves global absence.  
**Low-confidence items:** none are used as model-selection facts. Unverified historical or biological adaptation claims are explicitly excluded.

