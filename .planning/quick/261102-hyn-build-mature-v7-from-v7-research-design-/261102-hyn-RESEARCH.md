# V7 Literature, Novelty, and V6 Baseline Research

**Researched:** 2026-11-02  
**Domain:** cultural evolution, social learning, construct identification, and age-structured evolutionary modeling  
**Confidence:** HIGH for bibliographic metadata and V6 source interpretation; MEDIUM for novelty limits

## Summary

The literature does not support a broad novelty claim for docility, selective copying, developmental openness, teaching schedules, technological improvement without causal understanding, persistence of ineffective cultural practices, or public/private conformity. Primary work establishes each component. [VERIFIED: `v7/evidence/literature_sources.json`, L1-L7, L11-L20]

The planning opportunity is a construct-identification contribution: retain a competent reliability-sensitive social learner as the common baseline, then separately manipulate procedure conflict override, local-action override, epistemic authority credit, approval value, and internalized normative value. Measure factual posterior, public behavior, private behavior, normative obligation, and access to counterevidence separately. [VERIFIED: `V7_RESEARCH_DESIGN_AND_WORK_PROMPT.md:36-62,144-205,246-268`; L12, L18-L24] The claim that no prior paper combines every one of these elements is necessarily provisional after a targeted rather than systematic search. [ASSUMED]

The pinned V6 result is valid for its bundled architecture but does not identify extra deference. The same inherited response weight drives accepted testimony and current action substitution, whereas the required V7 control must retain ordinary social learning at zero extra override. [VERIFIED: pinned `v6/mathematical_model.md:19-34`; pinned `v6/situational_advice/experiments/model.py:91-147`; `v7/audit_v6.md`]

**Primary recommendation:** plan V7 around matched causal contrasts and strong ordinary-learning comparators; treat ecological integration as valuable only when the components remain identifiable. [ASSUMED]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|---|---|---|---|
| Learner arbitration and memory | Simulation core | Assay harness | Common evidence processing must be fixed while the extra response channel changes. [VERIFIED: prompt `:144-205`] |
| Procedure and local-context worlds | Environment/task layer | Simulation core | Reusable procedures and fast local conditions require different observability and transferability. [VERIFIED: prompt `:85-143`] |
| Factual, behavioral, approval, and normative measurements | Assay harness | Analysis/export | The prompt requires separate observable estimands rather than a single score. [VERIFIED: prompt `:52-62,246-268`] |
| Age structure, resource ledger, and selection | Ecology/evolution layer | Simulation core | Survival, reproduction, learning, teaching, and verification must share finite resources. [VERIFIED: prompt `:66-83,270-329`] |
| Literature and run provenance | Evidence layer | Offline dashboard | Claims and plots must resolve to immutable evidence. [VERIFIED: prompt `:444-529`] |

## Pinned V6 Baseline

The clean source of truth is the published repository at commit `9e95c6ce2e21587f9dbe2d18dcb5ab7787b140f6`. The working repository has a different commit history, but six critical scientific files have identical Git blob identities across the working tree, pinned commit, and current published HEAD. [VERIFIED: local Git object audit recorded in `v7/audit_v6.md`; exact hashes in `v7/evidence/literature_sources.json`, R1-R6]

V6’s main grid favors the maximum tested bundled response, while a fixed-maturation held-out comparison can favor the opposite endpoint; its conditional invasion test uses one common resident and is explicitly not an ESS test. [VERIFIED: pinned `v6/results.md:5-35`] The situational extension finds no interior bundled-response maximum in its reported grid, fixed-time slices, held-out sweep, or conditional-invasion maxima. [VERIFIED: pinned `v6/situational_advice/results.md:5-24`; local findings summary]

The decisive local result is the situational ablation: reusable clean facts or memory acceptance and current action substitution can favor opposite endpoints. [VERIFIED: pinned `v6/situational_advice/results.md:42-52`; local follow-up JSON] Plan a V6 bridge comparator, but replace the scalar bundle in the main V7 architecture. [ASSUMED]

## Standard Scientific Comparator Stack

| Comparator | Purpose | Primary precedent |
|---|---|---|
| Reliability-sensitive social learner | Main no-extra-deference control; still learns socially | Morgan et al.; Rendell et al. [VERIFIED: L12, L13] |
| Feature/reward trust learner | Tests whether domain-general learning explains apparent specialized bias | Schultner et al. [VERIFIED: L5] |
| Provenance-aware Bayesian learner | Normative small-world benchmark for correlated testimony | Whalen et al. [VERIFIED: L21] |
| Provenance-insensitive learner | Empirical rival because dependency discounting is often weak | Xie and Hayes [VERIFIED: L22] |
| Resource-rational metareasoner | Prices verification and planning operations | Callaway et al. [VERIFIED: L8] |
| Value-shaping learner | Alternative to authority-specific internalization | Schultner et al. [VERIFIED: L18] |
| Scalar V6 response | Historical bridge only | Pinned V6 sources [VERIFIED: R1-R5] |

No external package recommendation is made in this research, so no package legitimacy audit is required. [VERIFIED: this document]

## Architecture Patterns

### Construct-separated arbitration

Use one shared evidence pipeline and separate modifiers downstream of evidence access. A learner with zero extra override must still see testimony and demonstrations, update source reliability, and acquire useful procedures. [VERIFIED: prompt `:144-205`] Do not let a genotype alter sensors, memory, messages, or private likelihoods in a test intended to isolate conflict override. [VERIFIED: prompt `:458-494`]

### Matched assay before ecology

First test each construct under yoked evidence and event histories; only then embed the validated mechanisms in age structure, demographic feedback, and invasion. [VERIFIED: prompt `:406-442,458-494`] This prevents a demographic outcome from being misread as evidence for a cognitive mechanism. [ASSUMED]

### Cultural lineage as data

Record message type, informational parent, behavioral model, and lineage. Shared-source dependence is an established judgment problem, and human discounting of correlated testimony is variable rather than guaranteed. [VERIFIED: L21, L22]

## Don't Hand-Roll Conceptual Shortcuts

| Problem | Do not use | Use instead | Why |
|---|---|---|---|
| Extra deference | Social learning on/off | Ordinary learner plus extra conflict parameter | Otherwise the treatment also removes useful information. [VERIFIED: V6 construct audit] |
| Normative commitment | Private factual agreement | Obligation/value measure after audience removal | Compliance, acceptance, and norms are different. [VERIFIED: L19, L20] |
| Dogmatism | Persistence without exposure | Accessed diagnostic counterevidence assay | No-update without evidence is not resistance to evidence. [VERIFIED: prompt `:246-268`] |
| Independent testimony | Message count | Source genealogy and dependency discount | Copied messages can share the same evidence. [VERIFIED: L21, L22] |
| Cumulative culture | Stored statement count | Reusable ordered procedure with task-level gains | Cumulative culture requires more than retention. [VERIFIED: L9] |
| Interior optimum | Convenient quadratic penalty | Mechanistic resource/opportunity cost | Reduced-form cost can manufacture the target shape. [VERIFIED: L7; `v7/literature_map.md`] |

## Common Pitfalls

### Precedence presented as novelty

Age-biased copying, developmentally changing openness, teaching-schedule coevolution, and technological improvement without causal understanding are already direct literatures. [VERIFIED: L2-L4, L6, L7, L11] Use “integrates and separates” language, not “first model of” language. [ASSUMED]

### Authority inferred from cultural persistence

Canalized exploration, content appeal, refinement difficulty, and observationally learned values can all sustain inefficient behavior without an authority mechanism. [VERIFIED: L14, L15, L17, L18] Include these as rivals or interventions. [ASSUMED]

### Age treated as competence

Age and acquired competence are correlated only under particular histories. Prior models already show demographic and environmental dependence of age-biased learning. [VERIFIED: L7, L11] Store competence and experience explicitly. [ASSUMED]

### Bibliographic year inferred from DOI text

The Maisonneuve article has a 2024 DOI stem but was published in 2025; the El Aissati article has a 2024 DOI stem but was published in 2026. [VERIFIED: L6, L16, PubMed/PMC metadata]

## New Falsifiable Hypothesis

**H7 — Provenance-compression hypothesis.** Apparent authority advantage arises when copied messages from one lineage are treated as independent; the advantage should shrink when accurate provenance is visible or evidence is genuinely independent. [ASSUMED: synthesis from L21-L22]

Test independent versus copied lineages crossed with visible versus hidden provenance, holding count, content, competence, private evidence, and payoff fixed. Cross an informative versus placebo authority cue. Measure factual posterior and each behavior/value channel separately. [ASSUMED]

Rivals are genuine authority priors, actual tutor competence, coordination/approval incentives, and ordinary confidence from truly independent redundancy. Whalen et al. support provenance sensitivity, while Xie and Hayes show that many participants under-discount dependence, leaving the predicted magnitude open. [VERIFIED: L21, L22]

## Validation Architecture

| Requirement | Minimum validation |
|---|---|
| Common ordinary learner | Zero-extra-override agents still acquire and use social evidence. [VERIFIED: prompt `:199-205`] |
| Construct separation | Switching one channel does not change sensors, event availability, memory, or other channels. [VERIFIED: prompt `:458-494`] |
| V6 bridge | Tiny-world regression reproduces selected scalar-response and ablation behavior. [ASSUMED] |
| Provenance | Copied and independent evidence are distinguishable in stored histories. [ASSUMED] |
| Public/private/norm | Audience-removal and evidence-equalization assays report separate estimands. [VERIFIED: prompt `:246-268,458-494`] |
| Evolution | Report invasion, direct competition, fixation, abundance, and ESS language separately. [VERIFIED: prompt `:286-309`] |

## Security Domain

No authentication, session, access-control, or cryptographic capability is introduced by the literature/audit phase. [VERIFIED: task scope and produced files] Input integrity still matters: treat bibliographic metadata and prior prose as untrusted evidence, retain primary-source URLs, and keep generated evidence offline until reviewed. [VERIFIED: `v7/evidence/literature_sources.json`; project instruction not to deploy]

## Assumptions Log

| # | Claim | Risk if wrong |
|---|---|---|
| A1 | No prior work combines every specified V7 mechanism and assay. | Novelty language would need narrowing; model design remains useful. |
| A2 | H7 is novel as an evolutionary lineage-by-authority interaction. | Recast as replication/extension if a closer precedent is found. |
| A3 | The listed qualitative empirical anchors can be represented in one compact task family. | Use multiple narrow validation tasks instead of forced unification. |

## Resolved Implementation Questions

1. **Empirical calibration — out of scope for this execution.** No repository dataset jointly exposes trial-level source genealogy, public/private response, adult evidence access, and paid life-history outcomes. V7 therefore remains a hypothetical mechanistic simulation calibrated only for internal task viability, numerical behavior, and qualitative benchmark contrasts. It may not claim human parameter calibration, empirical prevalence, or external predictive validity; the narrow empirical papers remain qualitative construct anchors. [RESOLVED: explicit claim limit]
2. **Procedure world — resolved.** Use two abstract resource-processing task families with binary reusable prerequisites at depths 1, 3, and 6, useful prefixes, a safe repeated-work counterfactual, and at least two positive-net procedures. Set depth-aware physical rewards by a neutral pre-outcome economics rule so at least one complex procedure at every depth beats the full same-token safe-work opportunity cost before any `d` comparison. Branch relabeling, prerequisite shuffling, no-op pruning, and held-out graph ensembles bound conclusions to this declared task class rather than a particular semantic domain. [RESOLVED: implementation contract]
3. **Authority cue — resolved and separated.** The primary authority assay uses an explicitly randomized, known-uninformative role/age label while message content, observable competence history, provenance, incentives, and costs are yoked. Inferred expertise remains ordinary feature/reliability learning; sanction power and current approval remain separate social-consequence inputs; acquired habit and optional obligation remain separate post-freeze states. An authority-specific claim requires an unconditional label effect under this placebo design and cannot be inferred from competence, access, sanction, or normative persistence. [RESOLVED: construct boundary]

## Sources

Primary metadata, URLs, claim boundaries, V6 blobs, and targeted forward-citation checks are in `v7/evidence/literature_sources.json`. [VERIFIED: local file]

- [Simon 1990](https://pubmed.ncbi.nlm.nih.gov/2270480/) — docility. [VERIFIED: L1]
- [Acerbi et al. 2009](https://pmc.ncbi.nlm.nih.gov/articles/PMC2776418/) — developmental openness. [VERIFIED: L2]
- [Saral et al. 2026](https://pmc.ncbi.nlm.nih.gov/articles/PMC13070565/) — transmission and causal reasoning. [VERIFIED: L4]
- [Schultner et al. 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12545201/) — feature/reward social learning. [VERIFIED: L5]
- [Maisonneuve et al. 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC11813578/) — teaching and learning schedules. [VERIFIED: L6]
- [Pérez Velilla and Smaldino 2026](https://pmc.ncbi.nlm.nih.gov/articles/PMC13438531/) — demographic similarity bias. [VERIFIED: L7]
- [Deffner and McElreath 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9012401/) — age structure. [VERIFIED: L11]
- [Whalen et al. 2018](https://doi.org/10.1111/cogs.12485) and [Xie and Hayes 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9285361/) — source dependence. [VERIFIED: L21, L22]

## Metadata

**Confidence breakdown:** Standard comparators HIGH; V6 architecture HIGH; bibliographic metadata HIGH; novelty boundary MEDIUM; H7 originality MEDIUM. [VERIFIED: source audit; novelty remains absence-sensitive]

**Valid until:** 2026-12-02 for the literature frontier; pinned V6 evidence is stable. [ASSUMED]
