---
quick_id: 261102-hyn
phase: quick-261102-hyn
plan: 01
wave: 1
mode: quick-full
type: execute
autonomous: true
depends_on: []
files_modified:
  - v7/research_contract.md
  - v7/mathematical_model.md
  - v7/parameter_schema.json
  - v7/experiments/config.json
  - v7/experiments/model.py
  - v7/experiments/exact.py
  - v7/experiments/run_experiments.py
  - v7/experiments/analyze_results.py
  - v7/experiments/verify.py
  - v7/experiments/postfreeze.py
  - v7/experiments/run_postfreeze.py
  - v7/synthesize_results.py
  - v7/tests/test_kernel.py
  - v7/tests/test_ecology.py
  - v7/tests/test_postfreeze.py
  - v7/tests/test_reporting.py
  - v7/dashboard_template.html
  - v7/build_dashboard.py
  - v7/browser_verify.js
  - publication/versions.json
  - scripts/build_pages.py
  - scripts/verify_pages.py
  - README.md
generated_outputs:
  - v7/README.md
  - v7/results.md
  - v7/verification.md
  - v7/manuscript_outline.md
  - v7/project_manifest.json
  - v7/evidence/executed_checks.json
  - v7/evidence/hypothesis_ledger.json
  - v7/evidence/core_freeze/manifest.json
  - v7/evidence/core_freeze/source.tar.gz
  - v7/evidence/core_freeze/replay.json
  - v7/evidence/handoffs/01-wave0.json
  - v7/evidence/handoffs/02-kernel.json
  - v7/evidence/handoffs/03-ecology-gates.json
  - v7/evidence/handoffs/04-confirmation.json
  - v7/evidence/handoffs/05-selection.json
  - v7/evidence/handoffs/06-postfreeze.json
  - v7/evidence/handoffs/07-results.json
  - v7/evidence/handoffs/08-portal.json
  - v7/experiments/output/kernel.json
  - v7/experiments/output/discovery.csv.gz
  - v7/experiments/output/holdout.csv.gz
  - v7/experiments/output/evolution.csv.gz
  - v7/experiments/output/persistence.csv.gz
  - v7/experiments/output/decision_events.json.gz
  - v7/experiments/output/representative_trajectories.json.gz
  - v7/experiments/output/summary.json
  - v7/experiments/output/run_manifest.json
  - v7/index.html
  - v7/research_dashboard.html
  - v7/dashboard_build.json
  - v7/browser_verification.json
  - v7/export_verification.json
  - publication/build_report.json
  - publication/verification.json
  - docs/index.html
  - docs/apps/v7.html
  - docs/downloads/v7/all.zip
  - docs/downloads/v7/all.signature
  - docs/downloads/v7/index.html
  - docs/downloads/v7/manifest.json
  - docs/payload/v7/part-000.bin
execution_slices:
  - id: 1A-wave0-contract
    task: 1
    depends_on: []
    authored_files: 8
    handoff: v7/evidence/handoffs/01-wave0.json
  - id: 1B-kernel-exact
    task: 1
    depends_on: [1A-wave0-contract]
    authored_files: 5
    handoff: v7/evidence/handoffs/02-kernel.json
  - id: 2A-ecology-validity
    task: 2
    depends_on: [1B-kernel-exact]
    authored_files: 5
    handoff: v7/evidence/handoffs/03-ecology-gates.json
  - id: 2B-discovery-confirmation
    task: 2
    depends_on: [2A-ecology-validity]
    authored_files: 4
    handoff: v7/evidence/handoffs/04-confirmation.json
  - id: 2C-neutral-selection
    task: 2
    depends_on: [2B-discovery-confirmation]
    authored_files: 4
    handoff: v7/evidence/handoffs/05-selection.json
  - id: 3A-postfreeze-assays
    task: 3
    depends_on: [2C-neutral-selection]
    authored_files: 4
    handoff: v7/evidence/handoffs/06-postfreeze.json
  - id: 3B-results-synthesis
    task: 3
    depends_on: [3A-postfreeze-assays]
    authored_files: 2
    handoff: v7/evidence/handoffs/07-results.json
  - id: 3C-dashboard-portal
    task: 3
    depends_on: [3B-results-synthesis]
    authored_files: 8
    handoff: v7/evidence/handoffs/08-portal.json
estimate:
  tokens: 45000
  raw_tokens: 45000
  tasks: 3
  confidence: low
  basis: "maximum fresh-context slice; aggregate projection 170000 tokens across eight sequential slices"
must_haves:
  truths:
    - "A typed, truth-firewalled behavioral kernel shows that d=(0,0) remains a fully capable ordinary social learner, extra deference acts only on a logged conflict, and the exact tiny-world planner weakly upper-bounds restricted override policies under matched information and utility."
    - "Two acquired-competence task families at depths 1, 3, and 6 run inside a variable-population, finite-resource IBM with paid learning, teaching, computation, production, and birth events; no fixed census, expert reseeding, factual inheritance, or truth leakage is used."
    - "The compact discovery, holdout, culture, and paid-newborn lineage experiments preserve ordinary-social, scalar/vector, asocial, feature-trust, exact-tiny, and equally budgeted resource-rational comparisons, include every extinction, and never label finite descendant establishment as asymptotic invasion or ESS."
    - "The primary inherited override is juvenile-window only, adult learning capacity remains unchanged, and adult persistence probes disable direct adult override so learned habit, belief revision, obligation, and dogmatism are not conflated."
    - "At least 24 fresh held-out seeds are evaluated after a recorded core freeze; the bounded batch-of-eight precision rule stops at 96 and records unresolved contrasts rather than chasing significance."
    - "Every stochastic stage has frozen horizons and run/population/event/time/storage caps; streamed hashes and summaries cover every run, while only a prespecified representative set retains full histories and every cap hit is censored and unresolved."
    - "Task-economics, resource-ledger/demography, and paid-newborn neutral-selection gates pass before their respective substantive ecology or evolutionary runs can start."
    - "Post-freeze persistence code lives outside the frozen core, and final verification proves byte-identical core sources plus identical fixed-replay digests."
    - "All eight required offline dashboard views replay actual exported records with units, denominators, uncertainty, observation/interpolation status, seed, source revision, transmission rule, and metric definitions; the local versioned portal includes V7 without altering V1-V6 scientific artifacts or deploying publicly."
    - "Reports distinguish preregistered from exploratory analyses and accept null, endpoint, conditional-corner, polymorphic, comparator-equivalent, extinction-prone, and exact-planner-dominant outcomes."
  artifacts:
    - path: "v7/experiments/model.py"
      provides: "Typed hidden/observed state boundary, Candidate A IBM, Candidate B and other core policies, ledgers, keyed randomness, founder acquisition, demography, and lineage"
    - path: "v7/experiments/postfreeze.py"
      provides: "Approval, habit, low-value bundle, optional obligation, and dogmatism-probe extensions over immutable frozen-core interfaces"
    - path: "v7/experiments/exact.py"
      provides: "Enumerated D=1 and factored D=3 tiny-world dynamic-programming benchmark and solution-landscape audit"
    - path: "v7/experiments/output/run_manifest.json"
      provides: "Immutable seed registry, source/config hashes, fixed horizons, run/population/event/time/storage caps, censoring rules, streamed digests, and run counts"
    - path: "v7/evidence/core_freeze/manifest.json"
      provides: "Runnable frozen-core source archive hashes, interpreter/dependency metadata, public interface hashes, and replay digest"
    - path: "v7/evidence/executed_checks.json"
      provides: "Executed status and evidence pointers for every machine-readable predeclared check"
    - path: "v7/evidence/hypothesis_ledger.json"
      provides: "H1-H9 preregistration status, decisive tests, rival explanations, verdicts, contradictions, and limitations"
    - path: "v7/results.md"
      provides: "Reproducible findings separated into analytic consequences, observed results, interpretation, nulls, and unknowns"
    - path: "v7/research_dashboard.html"
      provides: "Self-contained offline V7 dashboard with the eight required data-backed views and exports"
    - path: "docs/apps/v7.html"
      provides: "Compact local versioned-portal integration using offline assets and externalized local payload"
  key_links:
    - from: "v7/experiments/model.py"
      to: "v7/experiments/exact.py"
      via: "The same action, observation, utility, likelihood, operation-price, and tiny-world transition contracts feed exact and restricted policies"
      pattern: "PolicyObservation|PolicyDecision|B_comp|operation"
    - from: "v7/experiments/run_experiments.py"
      to: "v7/experiments/output/run_manifest.json"
      via: "Every core discovery, freeze, held-out, and evolution run is registered before outcomes are analyzed"
      pattern: "discovery|holdout|freeze|precision|seed"
    - from: "v7/experiments/run_postfreeze.py"
      to: "v7/experiments/output/run_manifest.json"
      via: "Post-freeze runs append a separately namespaced immutable partition without changing frozen core records"
      pattern: "postfreeze|persistence|core_freeze_sha256"
    - from: "v7/evidence/predeclared_checks.json"
      to: "v7/evidence/executed_checks.json"
      via: "Verification preserves each check ID and records pass/fail/not-applicable evidence without rewriting the preimplementation artifact"
      pattern: "AUTH-01|HIDDEN-01|LEDGER-01|INVASION-01|EXPORT-01"
    - from: "v7/evidence/core_freeze/manifest.json"
      to: "v7/experiments/postfreeze.py"
      via: "The extension imports stable frozen interfaces without modifying core files; final replay must reproduce the freeze digest byte-for-byte"
      pattern: "source_sha256|interface_sha256|replay_sha256"
    - from: "v7/experiments/output/summary.json"
      to: "v7/research_dashboard.html"
      via: "The dashboard build embeds compact summaries and representative actual trajectories; export verification recomputes every displayed aggregate"
      pattern: "decision_microscope|policy_map|regime_map|research_ledger"
    - from: "publication/versions.json"
      to: "docs/apps/v7.html"
      via: "The local site builder treats V7 as a distinct version and externalizes its compact payload while retaining earlier source hashes"
      pattern: "v7"
---

<objective>
Build and execute the mature V7 research program as a bounded, reproducible local investigation: first prove the construct-separated behavioral kernel, then run acquired-procedure ecology and paid-newborn selection, then test post-freeze learned persistence and publish the resulting evidence into an offline eight-view dashboard and local portal.

Purpose: Replace the V7 primary model with individual histories while keeping the V1–V6 ODE artifacts immutable; determine what survives fully social d=0, feature-trust, exact-tiny, and equally budgeted approximate-planner controls without manufacturing a preferred result.

Output: Executable Candidate A/Candidate B source, deterministic and stochastic evidence, at least 24-seed held-out confirmation, extinction-inclusive lineage assays, post-freeze persistence probes, results/verification/manuscript artifacts, and a compact local V7 portal entry. No public deployment.
</objective>

<execution_context>
@/hpc/home/mg551/.codex/gsd-core/workflows/execute-plan.md
@/hpc/home/mg551/.codex/gsd-core/templates/summary.md
</execution_context>

<context>
@V7_RESEARCH_DESIGN_AND_WORK_PROMPT.md
@v7/model_candidates.md
@v7/constructs_and_estimands.md
@v7/evidence/model_recommendation.md
@v7/evidence/adversarial_design_review.md
@v7/evidence/predeclared_checks.json
@v7/literature_map.md
@v7/audit_v6.md
@.planning/PROJECT.md
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/quick/261102-hyn-build-mature-v7-from-v7-research-design-/261102-hyn-RESEARCH.md
@.planning/quick/261102-hyn-build-mature-v7-from-v7-research-design-/261102-hyn-VALIDATION.md
@v6/build_dashboard.py
@v6/browser_verify.js
@scripts/build_pages.py
@scripts/verify_pages.py
</context>

<scientific_contract>

## Interfaces and information boundary

- `WorldState` owns hidden structural bits `theta`, actual local condition `z`, actual source competence, future change times, resource pool, and evaluator labels. It is never passed to an ordinary policy.
- Frozen `PolicyObservation` contains only serialized observed history: identity/time/age, energy and remaining time/operation budgets, decision domain, private cue, current `B/K/T/H` summaries, message type/content/provenance, observable source history, feasible actions, stated costs, and advice. A policy-input schema validator rejects unknown truth-bearing fields.
- Frozen `PolicyDecision` records neutral `Q0` values, neutral action, recommendation, conflict flag, chosen action, operation count, charged cost, and override key/draw when applicable. An override with no new evidence cannot update `B`, `K`, or `T`.
- `Policy.decide(observation, operation_cap, keyed_rng) -> PolicyDecision` is shared by asocial access-off, fully social `(0,0)`, scalar override, vector override, feature-trust, Candidate B resource-rational, and post-freeze habit policies. The exact planner uses the same observations/actions/utility through a separately named oracle solver; it integrates hidden-state hypotheses but never receives realized truth.
- `KeyedRNG` addresses draws by `(namespace, replicate, graph, season, entity, event_type, ordinal)`. Environment, observation, innovation, demography, task outcome, and override namespaces are distinct; adding an unused draw cannot change later shared events.
- Immutable ledger records use one event ID to join agent/time debits, teacher and learner time, material/resource flow, computation operations, physical outcome, births/deaths, and biological/cultural edges. Transfers cancel, teacher cost is explicit, and every source/sink appears once.

## Primary model and fixed numerical choices

- Candidate A is a discrete-event, overlapping-generation variable-population IBM. Candidate B is the serious provenance-aware resource-rational metareasoner with no deference trait. V7 introduces no new ODE; V1–V6 remain byte-preserved comparison artifacts.
- Each run has two task families and common prerequisite depth `D in {1,3,6}`. Defaults are `p_plus=.90`, `p_minus=.50`, safe work net yield `h_safe=1.2` per token, prerequisite material cost `c_step=.20`, incorrect finish `2`, and salvage `.2` per reached node. Before any policy outcome is generated, set the correct-finish physical reward by the neutral depth rule `h_H(D)=ceil_0.1{[(D+1)(h_safe+.30)+D*c_step]/p_plus^D}`, giving `3.6`, `9.1`, and `22.1` for depths `1`, `3`, and `6`. Exact enumeration then compares actual expected net return, including failure, salvage, material, computation, and all `D+1` production tokens, against `D+1` repeated safe-work events; each primary depth must contain at least one complex procedure exceeding that full counterfactual by `.10` energy per token and at least two positive-net procedures. Calibration may adjust task graph/reward constants only by this outcome-blind economics rule, never by a `d`, cultural, authority, or selection result. Useful prefixes, nonzero matched-work private discovery, label/prerequisite robustness, and no-op-pruned depth remain hard gates.
- Reusable structure changes at `q_theta in {0,.005,.02}`; local state is redrawn per episode. All ages/traits share sensor accuracy `rho=.80`; tutor/learner context concordance is ecological `chi in {.50,.75,1}`. Reversed-access and equal-access probes manipulate observation timing/currentness, not hardware.
- Every individual-season has `B_time=12` indivisible time tokens. Every decision has `B_comp=128` primitive operations charged at a common price. The common `Q0` uses a two-episode horizon and `delta=.97`. Private trials, queries, both sides of teaching, verification, each production step, computation, transfers, rest, and reproduction consume declared opportunities and resources.
- The main inherited override is active only for `age < tau`, with fixed `tau=5`; learning, evidence encoding, memory, sensors, and source calibration remain identical at every age. A separately labeled lifelong-override robustness assay may run after the main result. Adult persistence probes force direct override to zero after training and remove the audience/tutor/sanction/reward as declared, so persistence cannot be a direct adult genetic `d` effect. Adult plasticity is never imposed lower.
- Start 64 naive founders, all with empty `B/K/T/H`, and acquire competence through a 60-season burn-in under the same costs. Blank, sparse-private, learned, alternative/wrong, and failed/extinct acquisitions remain recorded. Teaching eligibility is age-neutral and requires a stored sequence plus two independently attempted successes. No expert, correct procedure, fixed census, replacement newborn, immortal library, truth-conditioned teacher selection, or factual genetic inheritance exists.
- Environmental capacity starts at `K_R=1600`, regeneration `g_R=.08`, conversion efficiency `.75`, maintenance `.6` plus the declared mild age term, `C_birth=16`, `E0=8`, reserve `3`, `b_max=.5`, and the declared baseline/senescent mortality. These demographic values may be calibrated only for ordinary-social/asocial neutral viability and ledger closure on the four discovery seeds, never to favor an override coordinate.
- Freeze all execution bounds before discovery: ecology uses 60 founder-burn-in seasons plus 180 measurement seasons; H9 shocks at measurement season 90 and censors recovery at season 180; paid-newborn lineage assays use `T=80`; direct competition uses 120 seasons; persistence uses 40 training seasons plus 20 seasons per intervention; yoked assays use at most 2,000 decision opportunities per cell. A trajectory stops and is retained as cap-censored when population exceeds 512, processed events exceed 1,500,000, or wall time exceeds 120 seconds. Use at most four local workers, 12 wall-clock hours, and 12,000 launched trajectories for the complete task; exhaustion marks every not-run/unfinished contrast `UNRESOLVED` and cannot reallocate budget based on direction or significance.

## Compact experiment budget

- Kernel: enumerate the `D=1` tiny world and a factored `D=3` check; compare state/action values and visitation frequencies against paired simulation until discrepancy is within prespecified Monte Carlo error. Run the content × memory acceptance × override assay, authority-label placebo, identical-history hidden-truth permutation, provenance duplication, common-budget, inheritance, maturity-emulation, and V6 bridge checks before ecology.
- Discovery uses exactly four paired seeds `71001..71004`, two task families, 14 unique policies (the nine `{0,.5,1}^2` vector cells including ordinary-social `(0,0)`, scalar `.25` and `.75`, asocial, feature-trust, and Candidate B), and the following nine-run L9 ecological design rather than all 27/81 combinations: levels of `(D, verification/production ratio, chi, q_theta)` follow rows `(1,1,1,1)`, `(1,2,2,2)`, `(1,3,3,3)`, `(2,1,2,3)`, `(2,2,3,1)`, `(2,3,1,2)`, `(3,1,3,2)`, `(3,2,1,3)`, `(3,3,2,1)`. Map levels to `D={1,3,6}`, cost `{.1,.5,1.5}`, `chi={.5,.75,1}`, and `q_theta={0,.005,.02}`. State plainly that main effects are screened and interactions are aliased. Preserve the required depth × context and access-crossover interactions in a lightweight 3×3 yoked decision assay at fixed medium verification cost/slow change, not by expanding all life histories.
- Tune only neutral viability/task adequacy and the feature-trust/Candidate-B approximation hyperparameters on those four discovery seeds. Freeze code hash, config, primary outcomes, at most two vector candidates, the best scalar bridge, comparator hyperparameters, censoring rules, and the hypothesis ledger before reading holdout outcomes.
- Holdout uses fresh seeds `72001..72024` on unseen branch/graph permutations for ordinary social, feature-trust, Candidate B, the frozen scalar, and at most two frozen vectors across the nine regimes; asocial access and adjacent-value confirmation use the three predeclared sentinel regimes. For each primary contrast, compute paired-seed MCSE/intervals at 24 seeds and add fixed batches of eight (`72025..72096`) only until the relevant predeclared practical target is met: net-energy MCSE `<=.10` energy/agent-season; held-out success, action, revision, extinction, or establishment Wilson 95% half-width `<=.10`; useful-depth MCSE `<=.25` prerequisite levels; recovery-time MCSE `<=2` seasons; mean-population MCSE `<=5` individuals; or extinction-inclusive expected-descendant MCSE `<=.25` descendants per paid initial newborn. Stop at 96 and mark unmet targets `UNRESOLVED`; never use p-value proximity, effect sign, or preferred-policy rank to extend or stop.
- Evolution is precommitted before outcomes to at most three interpretable regimes and at most four directed resident-mutant pairs per regime. Seeds start `73001..73024`, with the same contrast-specific bounded precision rule. The default mutant and matched neutral tag arise from actual resident births: the resident parent pays `C_birth`, both newborns receive normal `E0` and blank acquired state, and mutants use the resident-dominated reachable teacher/resource environment. Report all zeros/extinctions, descendant-count distributions, establishment, time to lineage loss/fixation, direct frequency change, reciprocal/endpoint/nearby competitors, culture initial conditions, and direct competition. Call these finite lineage establishment/expected-descendant results, never asymptotic invasion, Lyapunov growth, fixation proof, or ESS.
- After the core code/config/policy set is hash-frozen, persistence seeds `74001..74024` train approval-linked action habits with identical age-independent learning. Test audience removal, free audit, bidirectional information equalization, outcome devaluation, and contingency degradation. In the same capped regimes, run a bundled useful-procedure/low-value-component assay against separable transmission and cheap component verification, with all teacher access/material effects paid. Report learned action persistence or cultural hitchhiking only when its discriminating controls pass. Enable an explicit acquired obligation state and use the stronger normative-commitment label only if countermand and novel-context generalization distinguish it from habit while factual beliefs revise adequately. Use dogmatism only for deficient/source-asymmetric factual revision under accessible matched evidence and conditioned priors. Null/failed strong assays remain published.

## Outputs and claims

- Primary outcomes are fixed by investigation: net energy for yoked override; held-out functional performance/useful depth for accumulation; extinction-inclusive expected descendants for selection; audience-removed action contrast for persistence; evidence-equalized factual revision for dogmatism; censored recovery for H9. Other metrics are diagnostics.
- The dashboard contains exactly the eight required data-backed views: decision microscope, two-domain policy map, environmental regime map, life-course/cohort player, cultural genealogy, intervention panel, evolution panel, and research ledger. It labels observed versus interpolated cells (interpolation is display-only), conditional versus unconditional denominators, uncertainty, extinction/censoring, and the three generators of intermediate behavior.
- Process full event streams online into typed counters, t-digests/histograms where declared, and SHA-256 replay digests; do not retain unbounded per-event JSON. Keep at most 10,000 stratified decision records (16 MiB compressed) and exactly 24 prespecified full histories (64 MiB compressed: nine regime sentinels, six policy comparisons, three selection, three persistence, and three neutral/cap/failure cases). Cap all experiment outputs at 256 MiB and per-run summary tables at 128 MiB; a byte-cap hit closes the partition with a cap record and marks affected contrasts censored/unresolved rather than silently dropping rows. The standalone local dashboard may read the bounded raw artifacts, but its compressed scientific payload is at most 4,000,000 bytes and all new `docs/` V7 files together are at most 8,000,000 decimal bytes because the existing site is already 986.7 MB. Full source and raw evidence remain outside the published site. Every export contains config/source hashes, seed, task graph, cultural transmission rule, metric definition, units, and cap status. No external requests, secrets, backend, database, public push, deployment command, or publication workflow is used.

## Bounded execution slices and handoffs

- Execute the eight frontmatter slices sequentially in fresh executor contexts. A slice may author no more than 15 files; generated evidence is separately declared and bounded above. Each slice begins by verifying its predecessor handoff hashes and ends by atomically writing its own handoff JSON with source/config/input/output hashes, commands, check statuses, cap usage, unresolved items, and the exact next-slice preconditions.
- Slice 1A creates all four test files before production code and fixes the contract/config. Slice 1B implements and proves the kernel. Slice 2A adds task economics, resource/demography, and runs only validity sentinels; substantive discovery is forbidden until `TASK-01`, `LEDGER-01`, `TEACH-01`, `GROWTH-01`, and cap/replay tests pass. Slice 2B runs discovery/confirmation and writes the runnable core freeze. Slice 2C first runs only paid-newborn self-mutant, drift, label/genotype exchange, resident-teacher-composition, and neutral-ledger checks; substantive resident-mutant/competition runs are forbidden until `INVASION-01` and `INVASION-02` pass.
- Slice 3A adds only `postfreeze.py`/`run_postfreeze.py` and their tests, importing stable core interfaces without editing any frozen core file. Slice 3B synthesizes results from immutable core and post-freeze outputs. Slice 3C builds/verifies the offline dashboard and local portal. Final verification re-hashes every live core byte against `core_freeze/source.tar.gz`, extracts/runs the archived snapshot, and requires both live and archived fixed sentinel replays to equal `core_freeze/replay.json`; any source or replay drift fails the release.

</scientific_contract>

<tasks>

<task type="tracer" tdd="true">
  <name>Task 1: Prove the truth-firewalled behavioral kernel end to end</name>
  <files>v7/research_contract.md, v7/mathematical_model.md, v7/parameter_schema.json, v7/experiments/config.json, v7/experiments/model.py, v7/experiments/exact.py, v7/experiments/run_experiments.py, v7/experiments/verify.py, v7/tests/test_kernel.py, v7/tests/test_ecology.py, v7/tests/test_postfreeze.py, v7/tests/test_reporting.py</files>
  <generated_outputs>v7/experiments/output/kernel.json, v7/evidence/executed_checks.json, v7/evidence/handoffs/01-wave0.json, v7/evidence/handoffs/02-kernel.json</generated_outputs>
  <read_first>V7_RESEARCH_DESIGN_AND_WORK_PROMPT.md, v7/model_candidates.md, v7/constructs_and_estimands.md, v7/evidence/model_recommendation.md, v7/evidence/adversarial_design_review.md, v7/evidence/predeclared_checks.json, v6/experiments/model.py, v6/situational_advice/experiments/model.py</read_first>
  <behavior>
    - Identical policy-visible histories and random keys with different hidden `theta/z` produce identical ordinary-policy choices, operation counts, and pre-override state digests.
    - Fully social `(0,0)` queries, updates beliefs/source estimates, stores and teaches acquired procedures, and rationally follows advice when `Q0` favors it; access-off asocial remains a distinct policy.
    - Changing `d` changes only a logged recommendation conflict; a forced override without evidence does not mutate `B`, `K`, or `T`.
    - Same-root testimony duplication leaves the provenance-aware physical-evidence posterior invariant, and authority-label permutation leaves label-neutral policies invariant.
    - Exact D=1 values weakly upper-bound restricted overrides under the same observations/utility, and simulated action values/visitation agree within the declared Monte Carlo tolerance.
    - Newborn acquired state is blank, founder competence traces to paid events, and forced common histories give equal sensors, capabilities, budgets, and balances across traits.
    - At each depth, exact neutral task enumeration includes the full same-token safe-work counterfactual and passes only when at least one complex procedure exceeds it by `.10` energy/token without consulting a `d` outcome.
  </behavior>
  <action>Run Slice 1A in a fresh context: write the governing contract/config and create failing test skeletons for all three tasks before production code, then emit the Wave-0 handoff. Run Slice 1B in a new context after validating that handoff: implement the typed interfaces, fixed primitives/caps, keyed randomness, separate core `B/K/T` state, provenance DAG, event/resource ledgers, ordinary social kernel, scalar/vector override, feature-trust, Candidate B, and exact tiny-world solver. Use the outcome-blind depth-aware reward formula and exact safe-work comparison for TASK-01. Cover AUTH-01..03, HIDDEN-01, PROV-01, BUDGET-01, INHERIT-01, FOUNDER-01, COMP-01, TASK-01, CLASS-01, RNG-01, and MATURITY-01. The tracer runs from a versioned tiny-world config through an ordinary-social conflict, exact comparison, immutable decision export, and executed-check record. Reproduce the fixed-source affine endpoint, equal-quality/no-effect neutral, and action-versus-memory V6 bridge fixtures needed to prove separation; never edit V1–V6. Keep `predeclared_checks.json` immutable. Do not proceed to ecology unless every pre-ecology blocker passes; emit the kernel handoff with hashes/check results or a failed/redesign stop.</action>
  <verify>
    <automated>OPENBLAS_NUM_THREADS=1 python -m unittest discover -s v7/tests -p 'test_kernel.py' -v &amp;&amp; OPENBLAS_NUM_THREADS=1 python v7/experiments/run_experiments.py --stage kernel --config v7/experiments/config.json &amp;&amp; python v7/experiments/verify.py --stage kernel --predeclared v7/evidence/predeclared_checks.json --executed v7/evidence/executed_checks.json</automated>
  </verify>
  <done>The tiny-world tracer executes from config to evidence; exact/value, truth-firewall, fully-social-zero, action/state separation, provenance, common-budget, founder/newborn, depth-aware safe-work economics, RNG, and selected V6 bridge checks pass with measured evidence, or execution halts with the failed blocker explicitly recorded and no ecological claims.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Run the frozen procedure, context, culture, demography, and paid-lineage program</name>
  <files>v7/experiments/model.py, v7/experiments/run_experiments.py, v7/experiments/analyze_results.py, v7/experiments/verify.py, v7/tests/test_ecology.py</files>
  <generated_outputs>v7/experiments/output/discovery.csv.gz, v7/experiments/output/holdout.csv.gz, v7/experiments/output/evolution.csv.gz, v7/experiments/output/decision_events.json.gz, v7/experiments/output/representative_trajectories.json.gz, v7/experiments/output/summary.json, v7/experiments/output/run_manifest.json, v7/evidence/executed_checks.json, v7/evidence/hypothesis_ledger.json, v7/evidence/core_freeze/manifest.json, v7/evidence/core_freeze/source.tar.gz, v7/evidence/core_freeze/replay.json, v7/evidence/handoffs/03-ecology-gates.json, v7/evidence/handoffs/04-confirmation.json, v7/evidence/handoffs/05-selection.json</generated_outputs>
  <read_first>v7/research_contract.md, v7/mathematical_model.md, v7/experiments/output/kernel.json, v7/evidence/executed_checks.json, v7/model_candidates.md, v7/constructs_and_estimands.md</read_first>
  <precondition>All Task 1 pre-ecology blocker IDs are recorded as passed against the exact source/config hashes that this task will freeze.</precondition>
  <behavior>
    - Every season closes `N(t+1)=N(t)+births-deaths` exactly and the environmental/individual energy ledger within numerical tolerance, including both sides of teaching and all birth costs.
    - Founder cultures are acquired under equal declared opportunities; failed/extinct burn-ins are retained, no carrier means no access, and held-out content follows cultural exposure rather than genotype or biological parent.
    - The nine ecological regimes cover every level of depth, verification cost, context match, and structural volatility three times; the report states that interactions are aliased and uses the separate 3×3 yoked assay for depth × context.
    - Discovery uses only seeds 71001..71004; a hash-stamped runnable freeze precedes any 72001+ holdout read; expansion follows only the outcome-blind contrast-specific MCSE/absolute targets and stops unresolved at 96.
    - Culture comparisons match per-person/total work and distinguish transmission+innovation, transmission-only, innovation-only, no-transmission, prerequisite-shuffled, and carrier-loss conditions.
    - Paid mutant and neutral newborns enter the real resident culture/resources with blank acquired state; all extinctions and zero descendants remain in the evolutionary summaries.
    - Ecology sentinels pass task economics, ledger, teaching, demographic growth/censoring, stream/storage, and cap tests before discovery; neutral paid-newborn/self-mutant/drift/exchange gates pass before any substantive resident-mutant run.
    - Every run honors the frozen horizon/population/event/wall-time/output caps and contributes streamed aggregate/replay hashes even when it terminates extinct or cap-censored.
  </behavior>
  <action>Run three fresh-context slices with atomic handoffs. Slice 2A expands the tracer into the two-family IBM, finite resource/production/maintenance/failure accounting, costly optional reproduction, variable births/deaths, separate biological/cultural genealogies, endogenous age-neutral teaching, depth-aware task economics, source-aware acquisition, caps, and streamed hashes. It runs only ordinary/asocial validity sentinels and must pass TASK-01, LEDGER-01, TEACH-01, GROWTH-01, storage/cap/replay, and neutral-viability gates before writing the ecology-gates handoff; failure blocks every substantive cell. Slice 2B validates that handoff, tunes only neutral viability/task adequacy and feature-trust/Candidate-B approximation settings on seeds 71001..71004, runs the 504 discovery cells, freezes candidates/outcomes/hyperparameters/horizons, executes at least 24 fresh holdout seeds plus unseen graphs, the targeted 3×3 yoked interaction/access probes, accumulation ablations, carrier-loss checks, and only target-triggered batches through 96. It writes a runnable source archive, manifest, fixed-replay digest, and confirmation handoff. Slice 2C validates the freeze, then runs only paid actual-birth self-mutant, matched neutral-tag, drift, label/genotype exchange, resident-teacher composition, and neutral-ledger assays; `INVASION-01/02` must pass before any of the precommitted substantive resident-mutant pairs or direct competitions launch. Then run no more than three regimes/four directed pairs with reciprocal, nearby/endpoint, multiple-culture, and direct-competition controls. Include finite establishment, expected descendants with zeros, full distributions, extinction, frequency changes, censoring, and conditional denominators; never use asymptotic invasion/ESS language. Enforce all trajectory/runtime/storage caps and record unrun/cap-censored work as UNRESOLVED. Record H1, H2, H5, H6, H7, H8, and H9 without favorable-result requirements.</action>
  <verify>
    <automated>OPENBLAS_NUM_THREADS=1 python -m unittest discover -s v7/tests -p 'test_ecology.py' -v &amp;&amp; python v7/experiments/verify.py --stage core --manifest v7/experiments/output/run_manifest.json --predeclared v7/evidence/predeclared_checks.json --executed v7/evidence/executed_checks.json</automated>
  </verify>
  <done>Task-world/ledger/demographic gates pass before discovery, paid-newborn neutral gates pass before substantive selection, and all permitted discovery/freeze/holdout/culture/evolution runs are reproducible from bounded manifests; all extinctions/cap hits are retained, practical precision decisions are auditable, and claims remain limited to measured finite estimands and the declared policy class.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Test post-freeze learned persistence and deliver the verified offline V7 evidence portal</name>
  <files>v7/experiments/postfreeze.py, v7/experiments/run_postfreeze.py, v7/synthesize_results.py, v7/tests/test_postfreeze.py, v7/tests/test_reporting.py, v7/dashboard_template.html, v7/build_dashboard.py, v7/browser_verify.js, publication/versions.json, scripts/build_pages.py, scripts/verify_pages.py, README.md</files>
  <generated_outputs>v7/experiments/output/persistence.csv.gz, v7/experiments/output/summary.json, v7/experiments/output/run_manifest.json, v7/evidence/executed_checks.json, v7/evidence/hypothesis_ledger.json, v7/results.md, v7/verification.md, v7/manuscript_outline.md, v7/README.md, v7/project_manifest.json, v7/index.html, v7/research_dashboard.html, v7/dashboard_build.json, v7/browser_verification.json, v7/export_verification.json, publication/build_report.json, publication/verification.json, docs/index.html, docs/apps/v7.html, docs/downloads/v7/all.zip, docs/downloads/v7/all.signature, docs/downloads/v7/index.html, docs/downloads/v7/manifest.json, docs/payload/v7/part-000.bin, v7/evidence/handoffs/06-postfreeze.json, v7/evidence/handoffs/07-results.json, v7/evidence/handoffs/08-portal.json</generated_outputs>
  <read_first>v7/experiments/output/run_manifest.json, v7/experiments/output/summary.json, v7/evidence/hypothesis_ledger.json, v7/evidence/executed_checks.json, v7/literature_map.md, v7/constructs_and_estimands.md, v6/build_dashboard.py, v6/browser_verify.js, publication/versions.json, scripts/build_pages.py, scripts/verify_pages.py, README.md</read_first>
  <precondition>The Task 2 runnable core archive, manifest, and replay digest exist; all core blocker gates pass; and the selected policy/regime list is immutable before approval/habit outcomes are opened.</precondition>
  <behavior>
    - Adult probes retain common sensory/update capacity, set direct inherited override to zero, remove each current social consequence explicitly, and export factual posterior, action, approval expectation, habit, and optional obligation separately.
    - Learned action persistence is reported independently of dogmatism; normative commitment appears only after devaluation/degradation, countermand, and novel-context obligation probes discriminate the stronger construct.
    - Every displayed dashboard aggregate exactly recomputes from immutable exports and every one of the eight views exposes units, denominators, uncertainty/censoring, seed/config/source metadata, and exact data download.
    - The standalone dashboard makes no HTTP(S) request; the V7 scientific payload is at most 4,000,000 bytes, all V7 additions to `docs/` total at most 8,000,000 decimal bytes, the complete site remains below 1 GB, and earlier scientific source/result hashes are unchanged.
    - Results, verification, and the manuscript outline label analytic consequences, observed stochastic results, interpretation, rivals, nulls, unresolved contrasts, and novelty limits separately.
    - No Task 3 action modifies a frozen core file; live-core hashes, archived-source hashes, and live/archive sentinel replay digests all equal the Task 2 freeze manifest.
  </behavior>
  <action>Run three fresh-context slices without editing `model.py`, `exact.py`, `run_experiments.py`, `analyze_results.py`, `verify.py`, or frozen config. Slice 3A first proves live core bytes and a fixed sentinel replay equal the runnable Task 2 archive, then implements only `postfreeze.py`/`run_postfreeze.py` against stable core interfaces. With seeds 74001..74024 and the relevant practical precision targets, train the declared approval-linked habit and perform audience removal, free audit, bidirectional evidence equalization, outcome devaluation, and contingency degradation while direct adult override is disabled. In the same three frozen regimes, cross useful-plus-low-value bundled versus separable transmission and paid versus free component verification with message/work-matched controls and separate teaching/access ledgers. Attempt obligation only through acquired-state, countermand, and generalization assays; publish null/PARTIAL/unsupported/unresolved results when probes do not discriminate it. Measure dogmatism only by matched accessible evidence and revision ratios. Slice 3B validates the post-freeze handoff, uses `synthesize_results.py` to record H3/H4 and synthesize all H1-H9, maps provenance compression to H8, and generates results/verification/manuscript/manifest artifacts with explicit unknowns and cap statuses. Slice 3C validates the synthesis handoff, builds the eight actual-data views and exact exports, then integrates V7 locally while keeping the V7 addition to `docs/` at or below 8,000,000 bytes and V1–V6 hashes unchanged. Use local assets, safe DOM rendering, fixed download names, and blocked HTTP(S). Final verification extracts and executes the core archive and rejects any live/archive byte or replay-digest drift. Never invoke GitHub preparation, push, deployment, remote API, or database commands.</action>
  <verify>
    <automated>OPENBLAS_NUM_THREADS=1 python -m unittest discover -s v7/tests -p 'test_postfreeze.py' -v &amp;&amp; OPENBLAS_NUM_THREADS=1 python -m unittest discover -s v7/tests -p 'test_reporting.py' -v &amp;&amp; python v7/experiments/run_postfreeze.py --verify-freeze --manifest v7/evidence/core_freeze/manifest.json &amp;&amp; python v7/build_dashboard.py --verify &amp;&amp; node v7/browser_verify.js &amp;&amp; python scripts/verify_pages.py</automated>
  </verify>
  <done>The post-freeze assays have construct-valid labels or explicit nulls; all H1-H9 entries have auditable verdicts; reproducible reports and manifests exist; all eight offline views and exports pass browser/data parity; the local portal exposes V7 compactly; V1–V6 remain unchanged; and no public deployment or remote integration occurred.</done>
</task>

</tasks>

<threat_model>

## Trust boundaries

| Boundary | Description |
|---|---|
| Local config/data → simulator/analyzer | JSON, CSV, gzip, and NPZ content can be malformed, non-finite, schema-incompatible, or inconsistent with recorded hashes. |
| Evaluator truth → ordinary policy | The simulator must score hidden state while ordinary policies must be capability-limited to typed observations. |
| Simulation exports → offline HTML/JavaScript | Data-derived text and download metadata cross into a browser context with no backend and no authorized network. |
| V7 build → versioned portal | Generated V7 assets join a near-limit local Pages tree while V1–V6 scientific artifacts must remain immutable. |

## STRIDE threat register

| Threat ID | Category | Component | Severity | Disposition | Mitigation plan |
|---|---|---|---|---|---|
| T-261102-hyn-01 | Tampering | Configs, manifests, compressed outputs | high | mitigate | Validate schemas/enums/shapes/finite values, record SHA-256 before analysis, make the freeze manifest append-only in behavior, and recompute display aggregates from hashed exports. |
| T-261102-hyn-02 | Information disclosure | `WorldState` to `PolicyObservation` boundary | critical | mitigate | Separate dataclasses/modules, reject unknown policy-input fields, serialize every policy call, run hidden-truth permutation/replay tests, and keep oracle capability in a named exact-only interface. |
| T-261102-hyn-03 | Tampering | Random streams and selection summaries | high | mitigate | Use namespaced identity-keyed RNG, unused-draw invariance digests, immutable seed partitions, pre-outcome freeze hashes, and extinction-inclusive denominators. |
| T-261102-hyn-04 | Spoofing | Source competence/provenance | high | mitigate | Select teachers only from observable acquired histories, use immutable physical-root IDs and provenance set union, prohibit evaluator competence in ordinary selection, and retain failed founders. |
| T-261102-hyn-05 | Elevation of privilege | Offline dashboard data to DOM/export | medium | mitigate | Parse data without `eval`, validate fields, render data-derived labels with text-safe DOM APIs, use fixed sanitized download names, and block all HTTP(S) in the browser test. |
| T-261102-hyn-06 | Denial of service | Experiment expansion and dashboard payload | medium | mitigate | Enforce fixed horizons, 12,000 trajectories, population/event/time/output caps, the nine-regime design, batches through 96, streamed summaries/hashes, exactly 24 full histories, V7 `docs/` additions at most 8,000,000 bytes, and unresolved/censored status at every cap. |
| T-261102-hyn-07 | Repudiation | Scientific claims and generated figures | high | mitigate | Preserve predeclared checks, emit per-seed records/config/source hashes, link every verdict/plot to exact data and denominators, and separate preregistered from exploratory results. |
| T-261102-hyn-08 | Tampering | Local portal integration | medium | mitigate | Hash V1–V6 source/result artifacts before and after, isolate V7 paths, enforce file/site size caps, verify all local links/archives, and never run deployment/push tooling. |

No package-manager install, external secret, authentication surface, backend, database, or public endpoint is introduced; package-legitimacy and schema-push gates are therefore not applicable.

</threat_model>

<source_audit>

| SOURCE | ID | Feature/requirement | Task | Status | Notes |
|---|---|---|---|---|---|
| GOAL | V7 | Execute the V7 brief through bounded staged investigations, held-out tests, and a local offline dashboard | 1–3 | COVERED | Kernel → ecology/evolution → post-freeze persistence/reporting. |
| GOAL | Preserve | Preserve V1–V6 and prohibit public deployment | 1,3 | COVERED | Read-only bridge fixtures plus source-hash gate; no remote command. |
| REQ | — | No formal REQ IDs exist in the deliberately minimal version index | — | N/A | This quick task is not a milestone phase; there is no omitted REQUIREMENTS.md assignment. |
| RESEARCH | R-01 | Candidate A small age-structured finite-resource IBM with individual histories | 1,2 | COVERED | V7 primary; no new ODE. |
| RESEARCH | R-02 | Candidate B provenance-aware resource-rational metareasoner and exact/feature-trust controls | 1,2 | COVERED | Same observations, utility, cap, price, and discovery-only tuning. |
| RESEARCH | R-03 | Fully social d=0 and content/memory/override separation | 1 | COVERED | Hard pre-ecology gate and yoked factorial. |
| RESEARCH | R-04 | Acquired founder competence, provenance, non-needle procedures, genuine accumulation | 1,2 | COVERED | Includes failed cultures and causal ablations. |
| RESEARCH | R-05 | Variable demography, energy/teacher budgets, paid newborn lineage tests, extinction | 2 | COVERED | Finite lineage claims only. |
| RESEARCH | R-06 | Adult persistence/dogmatism/norm construct separation | 3 | COVERED | Juvenile override window, adult override removal, unchanged adult plasticity, strong probes. |
| RESEARCH | R-07 | Four discovery seeds, fresh holdout, bounded precision, keyed randomness | 1,2,3 | COVERED | Exact seed partitions and stop cap specified. |
| RESEARCH | R-08 | Eight-view offline dashboard, exact exports, compact local portal | 3 | COVERED | All view names and size/offline gates specified. |
| CONTEXT | U-01 | User authorized full implementation with multiple completed specialist reviews and no public deployment | 1–3 | COVERED | Plan consumes existing reviews; sequential shared-checkout execution is self-contained. |
| CONTEXT | U-02 | Use installed Sol/Terra role models and no Astra | — | COVERED | Planning does not alter model routing or introduce Astra. |
| CONTEXT | U-03 | Group five investigations into three tasks; kernel gates before ecology; habit after core freeze | 1–3 | COVERED | Exact ordering and preconditions are explicit. |
| CONTEXT | U-04 | Compact two-family, depth 1/3/6 design with roughly nine regimes rather than a giant sweep | 2 | COVERED | L9 screen plus lightweight targeted interaction assay. |
| CONTEXT | U-05 | Same-cost founders, no fixed census/reseeding/truth leakage, paid actual-birth lineage controls | 1,2 | COVERED | Model/event/selection contracts specify each safeguard. |
| CONTEXT | U-06 | At least 24 holdout seeds and bounded precision rule; neutral/comparator tuning only on four discovery seeds | 2,3 | COVERED | Batches of eight to 96, unresolved at cap, no significance chasing. |
| CONTEXT | U-07 | Primary override age policy and removal in adult probes; adult plasticity not imposed lower | 1,3 | COVERED | Juvenile `age<tau` primary window, lifelong robustness only, adult override off in persistence assays. |
| CONTEXT | U-08 | Obligation/dogmatism labels require distinct strong assays; nulls acceptable | 3 | COVERED | Habit language is the default unless the stronger tests pass. |
| CONTEXT | U-09 | No external API or database integration; schema push irrelevant | 3 | COVERED | Reasoned `COVERAGE.md` declaration and local-file architecture. |
| CONTEXT | U-10 | Scope comes from the live working tree, not cached phase paths | 1–3 | COVERED | File list and portal interfaces were derived from the current checkout. |
| RESEARCH | RES-01 | Empirical calibration, procedure-world, and authority-cue questions are resolved before execution | 1–3 | COVERED | RESEARCH.md records decisions and empirical claim limits. |
| RESEARCH | VAL-01 | Validation Architecture has a task/check/test-availability and fail-closed ordering artifact | 1–3 | COVERED | `261102-hyn-VALIDATION.md` maps Wave 0 and every predeclared check. |

</source_audit>

<verification>

1. Kernel verification fails closed before ecology on any hidden-state leak, bundled d=0 channel, unequal budget, exact-planner violation, founder/newborn smuggling, provenance double count, or non-needle failure.
2. Core verification recomputes ledgers and all predeclared blocker IDs, audits run/freeze/seed partitions, checks every extinct record is present, and rejects survivor-only or asymptotic-selection labels.
3. Final verification recomputes displayed values from raw/summary exports, checks hypothesis/claim language against gate outcomes, executes the browser offline/export suite, verifies portal links/size/hashes, and confirms V1–V6 scientific bytes did not change.
4. The executor creates `.planning/quick/261102-hyn-build-mature-v7-from-v7-research-design-/261102-hyn-SUMMARY.md` with exact commands, run counts, statuses, unresolved contrasts, and artifact hashes.

</verification>

<success_criteria>

- Candidate A and Candidate B run reproducibly with the exact typed interfaces and budgets above; all required pre-ecology gates pass before population claims.
- The compact fixed discovery/holdout/evolution/persistence programs execute with at least 24 fresh held-out seeds and recorded bounded precision decisions.
- Every stage honors the frozen horizons and run/population/event/time/storage caps, and every cap hit is retained as censored/unresolved with streamed evidence hashes.
- Every fresh-context slice authors at most 15 files and produces a verified handoff; post-freeze work leaves the runnable frozen core byte-identical and replay-identical.
- Every required comparator/control, founder/culture condition, energy/teacher debit, extinction, paid newborn, and construct distinction is present in outputs and verification.
- Reports answer what was already known, what V7 changed, what happened, what survives strong ordinary-learning controls, which generator explains intermediate behavior, whether dogmatism was generated/imposed/absent, and what novelty remains plausible.
- The standalone dashboard and local portal provide all eight views and reproducible downloads with no external request or public deployment, while earlier versions remain immutable.

</success_criteria>

<output>
Create `.planning/quick/261102-hyn-build-mature-v7-from-v7-research-design-/261102-hyn-SUMMARY.md` when done.
</output>
