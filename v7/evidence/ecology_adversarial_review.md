# V7 ecology adversarial code review

**Review mode:** read-only causal-validity review of the actual event path. Unit-fixture success and status JSON were not treated as scientific evidence.

**Primary reviewed snapshot:** the Slice 2A ecology handoff's own certified sources:

| File | SHA-256 reviewed |
|---|---|
| `v7/experiments/model.py` | `917efd403bad23f01d09ad0f2c67230918511b0bbe6b6bc2a5d0df883decab4e` |
| `v7/experiments/exact.py` | `b12e05f469610f3d1788ec311e71bdc72d4dbb2239d4942b0bc682812f2c57ed` |
| `v7/experiments/run_experiments.py` | `88fc96e68a5732a24758d734b0ac3a6d5e275269a4a95393be2af79a3cdc4d10` |
| `v7/experiments/verify.py` | `bbdc5ca26a18e33fc3f7bffd90540b652d51b374af9bc3178fedebce626e5902` |
| `v7/tests/test_kernel.py` | `c2350e9973ea256d16a077d1d19ae15b9c6e65ef834b06a18c2674de29f1034b` |
| `v7/tests/test_ecology.py` | `5eb9708fc4d705150a0b7d8cc818a1136a708169c4db0cb4500cdc83d90336e9` |

The governing prompt hash was `53da30dfa2cf639a34e84fd131f5bad87d9efe1db5b9c48c98f4baf8550ac644`; the PLAN hash was `c1b3f7e5b94d880e866e44170732f31be147e5130042ef3ee29fadd827ffac31`. `model.py` changed after this snapshot while `/root/v7_ecology_repair` was active. Consequently, line references below describe the certified `917efd...` snapshot, not an assertion about an unreviewed later edit.

## Verdict

The `passed` Slice 2A handoff does **not** establish a mature V7 ecology. It establishes that two deterministic sentinels ran for 240 seasons and that a stock identity computed from the same internal loss counters was numerically near zero. In the certified event path, the policy cannot evaluate the procedure actually offered, conflict is teacher-versus-private source choice rather than conflicting actions, the neutral value is disconnected from the IBM payoff, provenance is not a physical lineage, the event ledger cannot reconstruct the accounting identity, and the exact model does not share the ecology contract.

Therefore:

- revoke the scientific meaning of `TASK-01`, `LEDGER-01`, `TEACH-01`, `GROWTH-01`, `COMP-01`, `PROV-01`, and the ecology-level `AUTH-*` claims for this source hash;
- do not launch Slice 2B discovery/holdout from handoff `03-ecology-gates.json` as currently certified;
- retain the existing outputs only as debugging/replay fixtures; and
- rerun gates on the repaired hash using actual event-path assertions.

The parent-identified defects already under repair—truth-independent cue/advice, unused `d_local`, single-coin pseudo-depth, unused `B`, noncausal verification, global-energy reward fitting, maturity age two, factory policy inheritance, and unbounded in-memory ledger—are accepted here and not re-litigated as new findings. The blockers below are additional or sharpen their causal consequences.

## BLOCKERS

### E-01 — The policy does not observe the advised procedure, and “conflict” is not an action conflict

In the certified path, `_observation` emits `advice="teacher"`, a message containing only the family name, and provenance entries chosen as the first two keys of the teacher's entire `K`. `_teach` later and independently chooses the first eligible sequence for the family. Thus the policy never evaluates the branch/sequence that will actually be executed (`model.py:350-373,398-407`).

`PolicyDecision.conflict` consequently means “neutral source label differs from the string `teacher`,” not “my preferred procedure/local act conflicts with the tutor's recommended procedure/local act.” The action set contains `private` and `teacher`, rather than executable actions. The kernel output makes the mismatch visible: the asocial policy chooses the string `teacher` despite having `advice=null`; the ecology event loop silently treats that as the private branch when no teacher exists.

Worse, the message is already exposed before override, yet choosing `teacher` calls `_teach`, which copies the procedure into `K`. Extra override therefore changes memory acquisition on the same exposed content. That violates the contract that an override without new evidence cannot update `B/K/T` and makes downstream competence a direct effect of `d`, not only a mediated execution effect.

**Minimal repair:** make the observation contain the actual offered procedure and its provenance; make feasible actions actual procedures/local applications plus safe work; compute and log the learner's pre-advice planned action; expose content/memory acceptance independently of execution; apply override only to a genuine action conflict; and guarantee identical acquisition on yoked histories when only override changes.

**Required gate:** replay one frozen interaction through ordinary and forced-override policies. Pre-override `B/K/T`, available content, offered sequence, Q0, and budgets must match. Only executed action may differ at override time; `K` may differ later only through separately logged new evidence or practice outcomes.

### E-02 — Q0 is not the IBM's material value function

The observation posts a hard-coded `correct_reward=3`, `incorrect_loss=2`, and zero execution price for every depth (`model.py:359-373`). The actual task pays depth-specific rewards `3.6/9.1/22.1`, consumes `D+1` time/material steps, competes with safe work, and can be resource constrained (`model.py:375-433`). Q0 omits all of those quantities, the learner's actual stored alternatives, and the offered sequence's observable content.

The policy therefore cannot be interpreted as a common authority-neutral material evaluator. Differences between neutral and override choices are relative to a fictional payoff, not the ecology in which the action is executed. Candidate B and feature trust inherit the same mismatch.

**Minimal repair:** construct Q0 inputs from the exact same transition/reward contract used by `_attempt`: sequence-specific posterior success, correct depth reward, reached-step material/time costs, safe-work opportunity cost, resource scarcity rule, and two-episode continuation. If an approximation is necessary, name it and compare it with an exact tiny instance; do not call a hard-coded source-choice score the IBM's material Q0.

### E-03 — There is no physical provenance DAG and source reliability double-counts descendants

The field named `provenance_roots` is populated with procedure strings from `teacher.K`, not immutable physical trial/innovation root IDs (`model.py:364`). Independent discoveries of the same procedure collapse to one apparent root; copied descendants cannot be traced to their original observation; the roots can even refer to a different family than the offered sequence. `PROV-01` only duplicates a hand-built string in a fixture, so it does not exercise ecology transmission.

Teacher reputation is global across both families. It is incremented for the teacher's own outcomes and again for learner outcomes after teaching (`model.py:423-429`). Subsequent learners then treat these correlated downstream outcomes as source-history observations. This conflates food/tool competence, teacher skill, procedure quality, learner skill, and descendant reuse; it can amplify a lineage as if it supplied independent evidence.

**Minimal repair:** give every private physical attempt/innovation a unique root; store procedure lineage as immutable parent/root sets; transmit the actual offered lineage; union unique roots at merges; maintain family/sequence-specific teacher history; and decide explicitly whether downstream learner outcomes update teacher reliability. If they do, model their conditional dependence rather than counting them as independent source trials.

**Required gates:** same-root duplication invariance through two transmission generations; two independent roots with identical content remain two roots; a food outcome does not change tool reliability; copying a copied procedure does not create a new physical root.

### E-04 — Exact/planner evidence is not parity evidence for the IBM

`ExactTinyPOMDP` uses time/operation budgets `3/6`, reward `3`, loss `2`, and its own learn/query/verify transitions. Ecology uses `12/128`, depth rewards, resource scaling, procedures, teaching, and demography. The exact restricted simulator always buys learn+query+verify, but omits the execution operation price that the Bellman execute value charges (`exact.py:118-153,159-181`). No forward simulation of the exact policy is compared with Bellman state/action visitation. The reported comparison merely shows that an adaptive toy policy exceeds a deliberately fixed toy policy.

Task economics also disagrees with itself. The reward rule divides by `p_plus^D`, but `enumerate_task` applies `D` prefix hazards and another finish hazard, yielding `p_plus^(D+1)` (`exact.py:20-47`). Its measured depth-one margin is `0.077` per token, below the declared `0.10`; nevertheless `TASK-01` passes because the test and runner require only *some* depth to clear the threshold, not every primary depth or two positive-net procedures. The IBM then ignores this enumerated path and uses one terminal success coin.

**Minimal repair:** choose one explicit prerequisite/finish stochastic contract and use it in reward calibration, enumeration, IBM execution, and exact comparison. Share action names, time/operation prices, likelihoods, and utility. Forward-simulate the exact policy and compare values plus visitation/state distributions. Charge identical execution costs. Enforce the declared criterion per depth and enumerate at least two viable procedures plus matched-work private discovery.

### E-05 — Culture and adaptation are driven by lexicographic/order artifacts

Once an individual has any stored sequence for a family, the private path takes the first matching dictionary key. It does not compare alternatives, use `B`, or innovate again (`model.py:498-500`). If both branches are stored, lexical branch order controls behavior. After structural change, this creates permanent lock-in that can masquerade as persistence, dogmatism, or cumulative culture.

Teacher selection is similarly deterministic: agents are processed lexicographically; a teacher is eligible only if its used-time counter is zero; the highest global success fraction wins, with identity as tie-break (`model.py:350-357,468-480`). A later-ID agent can teach an early-ID learner before acting, while an early-ID agent is generally unavailable to later learners after acting. Only one teaching interaction is allowed despite charging one of twelve tokens. These mechanics create identity/order-specific access, teacher monopolies, and lineage growth not caused by policy traits.

Only the `food` structure flips; `tool` remains fixed (`model.py:521-523`). Family and volatility are therefore confounded.

**Minimal repair:** let the common policy choose among all known/innovated/offered sequences using observable evidence and actual costs; preserve exploration after acquisition; use an explicit keyed event schedule or random matching independent of identity sort; enforce teacher capacity using charged tokens rather than `used==0`; keep family-specific histories; and vary structural change symmetrically or declare a preplanned asymmetry.

**Required gates:** invariance to renaming individual IDs and procedure labels; event-order/timestep sensitivity; both task families can change under the same declared process; after a change, a learner with both branches can select either based on evidence rather than key order.

### E-06 — The resource identity is self-confirming, not reconstructible from ledger events

`_charge` debits only available energy but allows the full action to proceed. An energy-poor agent can therefore receive full teaching/query/computation benefits after paying partially or nothing (`model.py:392-396,401-407,482-493`). The emitted teaching and information events record the nominal full debit, not the amount actually paid. Maintenance, base decision operation charges, terminal death energy, and ordinary reproduction time have no complete reconstructible ledger events. Reproduction consumes no time token.

The seasonal residual is calculated from actual stocks and the same mutable `self.losses` counters modified alongside those stocks (`model.py:463-528`). It can be zero even when event rows are false or missing. `LEDGER-01` verifies this side-counter identity; it never independently replays the event ledger. `LedgerEvent.transfer_residual` is not used by the ecology gate.

**Minimal repair:** make affordability part of action feasibility or scale/cancel the outcome consistently; record the actual paid amount; emit events for every maintenance, operation, production, teaching, birth, death sink, and transfer; charge reproduction time; stream events instead of retaining them all; and reconstruct stock changes independently from the event stream. The simulator's internal loss accumulator may be a diagnostic, not the oracle used to verify itself.

### E-07 — Context mismatch leaks the true ecological parameter

The policy receives `context_mismatch=1-chi` exactly (`model.py:373`). `chi` is the generative tutor/learner concordance condition, not an observed mismatch in this event path. There are no tutor and learner context observations from which mismatch could be inferred. This gives the learner privileged knowledge of a scenario parameter while the truth-firewall fixture never varies the real policy-visible construction.

**Minimal repair:** generate private tutor and learner observations from latent local context, expose only those observations and learned source/context history, and let the learner estimate mismatch. An oracle may know `chi`; ordinary policies may not unless the experiment explicitly supplies calibrated metadata to all policies.

### E-08 — Paid-newborn controls are not traceable paired births

`paired_paid_newborns` creates two actual birth events from two different highest-energy parents, discards the second event ID, and returns one synthetic pair ID in both `PaidNewborn.birth_event_id` fields (`model.py:448-459`). Parent traits and histories need not match. The helper bypasses maturity and reproduction-time eligibility. The unit birth test uses an external parent not in `run.population`, so it does not validate the real population stock path.

**Minimal repair:** retain both actual birth IDs plus a separate pair ID; require age-five eligibility and reproduction time; randomize mutant/neutral tag assignment within an explicit parent/state block; preserve parent traits; and verify each birth against the streamed stock ledger. If two different parents are required, condition/block on parent state and do not call them the same counterfactual birth.

## IMPORTANT claim limits

### I-01 — The certified gates test liveness, not the predeclared constructs

The kernel “hidden permutation” loops over names `_theta/_z` without changing any world or observation. The factorial separately calls `store_procedure` on a detached state rather than running acquisition through an event. `BUDGET-01` checks only that reported operations are below six. `FOUNDER-01` checks blank initialization, not paid acquisition. `MATURITY-01` checks one fixture action, not earlier-eligibility emulation. `CLASS-01` validates an observation object, not stochastic-interior versus conditional-policy versus polymorphism classification.

Ecology `GROWTH-01` requires one seed per policy to survive, reproduce, and change population; it does not establish extinction-inclusive growth. `TEACH-01` checks nonzero edge/time counts, not correct payment or information. `TASK-01` reads the disconnected analytic toy. A passing unit suite cannot upgrade these to causal evidence.

### I-02 — The verifier does not bind every scientific dependency

The ecology source manifest binds `model.py`, `run_experiments.py`, `verify.py`, and `test_ecology.py`, but not `exact.py`, even though current task economics and production rewards import it. The verifier rereads old kernel economics rather than proving that the running ecology used a matching exact contract. Any repaired gate must hash all code/config files that affect transitions, payoffs, and policies and invalidate the old `passed` handoff.

### I-03 — Current scope supports no substantive V7 claim

Discovery, holdout, culture ablations, carrier loss, descendant lineages, competition, and persistence are explicitly unrun. The only defensible description of existing results is “two debugging sentinels completed under a provisional ecology.” Do not describe them as evidence for ordinary social learning, selective deference, cumulative culture, demographic selection, or a strong resource-rational comparator.

## Minimal repair and re-gating order

1. Define one actual task transition contract—prerequisites, finish, local context, sequence content, rewards, safe alternative—and share it across IBM, Q0, exact enumeration, and tests.
2. Separate content exposure/storage from action conflict; log the actual offered and planned sequences; make `d_procedure` and `d_local` act on their respective genuine conflicts only.
3. Implement physical provenance and family-specific observable reliability histories before any teaching comparison.
4. Replace side-counter accounting with an independently replayable streamed ledger and make insufficient resources/time prevent or consistently scale an action.
5. Remove identity/lexical ordering from procedure and teacher choice; add rename/order invariance tests.
6. Repair exact forward parity and enforce task adequacy at every declared depth.
7. Repair real-parent age-five paid births with distinct event IDs and paired tag assignment.
8. Re-run actual-path gates, regenerate evidence/handoffs on the new complete source hash set, and only then decide whether Slice 2B may begin.

## Required re-review evidence

The repair is ready for adversarial re-review when it provides:

- the repaired source/config/test hashes;
- one decision replay showing observable offered sequence, private plan, posterior/Q0 components, actual conflict domain, override, evidence updates, and realized event costs;
- an independent event-ledger replay that reconstructs per-agent energy, resource stock, time, births, and deaths;
- exact versus forward-simulation value and visitation parity under one shared tiny task contract;
- source-lineage traces over two teaching generations;
- ID/procedure-label/event-order permutation checks; and
- paid-newborn records with two real birth IDs, a separate pair ID, eligible parents, blank acquired state, and preserved traits.

Until those exist, all substantive ecological and evolutionary contrasts remain **blocked**, not merely uncertain.

---

## Interim repair re-review — requested stable snapshot

This is a read-only re-review of the repair agent's requested snapshot. It supersedes the initial findings only where explicitly stated. It is not a PASS decision and does not certify later bytes.

| File | SHA-256 reviewed |
|---|---|
| `v7/experiments/model.py` | `96e2ae2f269f11de2ce024647fa37197522a551c500ccde95fcea037664fad69` |
| `v7/experiments/exact.py` | `965e2c93e5d405c2f476a08ec89465d2d643be9300bdc9d1ab779bea0a3e0b00` |
| `v7/tests/test_ecology.py` | `4e33a6185cd8d174ce063b954b192f1738a2b4d006e54ea0e2f62c01bdec9c8c` |
| `v7/experiments/run_experiments.py` | `88fc96e68a5732a24758d734b0ac3a6d5e275269a4a95393be2af79a3cdc4d10` |
| `v7/experiments/verify.py` | `bbdc5ca26a18e33fc3f7bffd90540b652d51b374af9bc3178fedebce626e5902` |

The named ecology unit suite passed 12/12 on this snapshot. That is regression evidence only; the tests do not exercise the causal failures below. During report finalization, the live model/runner/verifier moved again (`model.py` `4e19538a...`, runner `ae43019c...`, verifier `08e02a30...`). Those later bytes are deliberately unreviewed and require the parent's planned post-repair retake.

### Repairs observed on `96e2ae2...`

- Private structural cues are now generated from `theta` through a noisy observation, and a separate fast local `z` path exists.
- Procedure execution uses a shared `D+1` branch sampler, physical outcomes update `B`, feature-trust fitting is individual-local, maturity is age five, and newborn policies inherit traits while acquired `B/K/T/H` remains blank.
- Both procedure and local override coordinates reach physical action paths; an information purchase triggers a re-decision; the recent event window and replay digest are bounded/deterministic.

These are meaningful corrections. They do not by themselves validate the scientific gates.

### Remaining BLOCKERS on `96e2ae2...`

#### R-01 — Extra override is still confounded with procedure-content acquisition

The pre-decision procedure observation contains a family-labelled offer but not the actual offered sequence. The learner receives/stores that sequence only through `_teach`, which is called after `chosen_action == "teacher"`. Therefore changing `d_procedure` changes whether content is acquired and can enter `K`, not merely whether a commonly exposed procedure is executed. This violates the required separation between ordinary social learning/content access and extra authority override.

**Minimum safeguard:** expose and charge the same concrete sequence before arbitration in yoked comparisons; hold content receipt/storage opportunity fixed; let `d_procedure` change only the conflicting execution decision. Assert identical pre-action observation, `B/K/T`, budget, and offered sequence across `d`, with only action allowed to differ.

#### R-02 — The material decision, exact task, and IBM still do not share a utility contract

Q0 treats the offered branch as a binary `reward` versus `-2` choice. It does not integrate the branch-dependent `p+=.90`/`p-=.50` multi-step outcomes, prefix failures/salvage/material costs, the learner's actual known procedures, or resource scarcity. More decisively, the IBM's `_safe_work` spends one token for `1.2`, while TASK-01 compares a procedure against `(D+1)*1.2`; unused tokens cannot produce the claimed same-work counterfactual. The ecology therefore structurally favors the long procedure relative to its reported comparator.

The exact oracle also remains a separate `time=3`, `operations=6`, reward-3 toy; the restricted forward path buys every information action and omits the execute operation charge paid by the Bellman value. Its upper-bound check is not parity evidence for the ecology.

**Minimum safeguard:** use one depth-specific expected-payoff adapter in Q0 and execution; make safe work repeat for the same tokens or debit the same explicit opportunity cost; run one matched exact-policy forward check with identical prices/caps and visitation counts. Do not use COMP-01/TASK-01 as ecology evidence until then.

#### R-03 — The local information update does not use the purchased signal's direction

After query/verification, the code observes a bit about true `z`/`theta`, but the local update always increases the single `local:{family}` scalar regardless of whether the bit supports the private or tutor action. The refreshed observation contains the original keyed private/tutor signals, not the purchased bit. Thus the paid signal cannot rationally reverse the action in its indicated direction. Separately, `_local_attempt` updates the teacher's local success/failure record whenever a teacher exists even when the learner chose `private`; subsequent advice reliability is contaminated by private-action outcomes.

**Minimum safeguard:** condition the posterior on whether the purchased bit matches each candidate action and retain that evidence for re-decision; credit teacher calibration only for the tutor recommendation actually evaluated/executed. Add opposite-signal tests that force opposite posterior movement.

#### R-04 — The certified “ordinary social” sentinel evolves nonzero override traits

Every normal birth mutates every inherited `d` coordinate by `+/-0.05` (clipped), including births in the run labelled `ordinary_social`. Consequently the 240-season ordinary sentinel is not a fixed `(0,0)` reliability-sensitive learner after the first births. Its survival, teaching, and growth cannot certify the zero-extra-authority baseline.

**Minimum safeguard:** disable trait mutation in validity sentinels and fixed-policy comparisons; enable it only in an explicitly labelled evolutionary assay with a declared mutation kernel. Export the realized trait distribution per run.

#### R-05 — LEDGER-01 remains a same-state identity, not an event replay

Maintenance, ordinary base decision charges, and terminal death energy are not represented as complete events. Information events do not encode every separately charged component. Seasonal closure subtracts the same mutable loss counters used while mutating stocks, so a near-zero residual cannot show that the streamed events are complete or truthful. The bounded deque fixes memory growth but not reconstructibility.

**Minimum safeguard:** emit actual paid deltas for every stock-changing operation and reconstruct the seasonal identity from the event stream in a separate function/test. Reject or explicitly scale unaffordable actions rather than granting full information/action after partial payment.

#### R-06 — Source/provenance evidence remains mis-scoped

Procedure observations collect roots across all of a teacher's `K`, not just the offered family/sequence; local observations manufacture a root from teacher identity rather than a physical observation. Learned trust is stored under `teacher:{id}:{family}`, while `source_calibration` looks up the bare source ID and therefore ignores it. These paths can weight advice with unrelated or fictitious evidence. This is a truth-firewall/source-lineage failure even though the policy no longer receives raw `theta/z`.

**Minimum safeguard:** pass only physical roots attached to the offered content; use a family-specific source key consistently for storage and lookup; treat a local message as a message, not a physical root. Test that tool roots cannot move a food posterior and that a private local action cannot update tutor reliability.

#### R-07 — The ecology handoff does not bind a live scientific dependency

`model.py` imports task rewards/outcomes from `exact.py`, but the ecology `source_paths` and manifest omit `exact.py`. The verifier also reads task economics from the old kernel output rather than proving parity with the live ecology dependency. The `passed` handoff can therefore survive a change to its reward/transition implementation.

**Minimum safeguard:** hash `exact.py` in the ecology manifest/handoff, recompute economics from the same live dependency, and fail closed on any mismatch.

### IMPORTANT claim limits

- A no-teacher observation still leaves the symbolic `teacher` action feasible; tie-breaking can report `chosen_action="teacher"` even though the event loop executes the private branch. Decision-event action labels are therefore not yet trustworthy estimands.
- Teacher choice requests `T["outcome:{family}"]`, but no actual path writes that key, reducing selection to identity order. Do not infer source-sensitive teacher choice or lineage advantage from current edge counts.
- `paired_paid_newborns` uses two different parents, suppresses mutation in both arms, and replaces the two real event IDs with one synthetic field. It is not yet a paired self-mutant/neutral counterfactual and must not support INVASION claims.
- Only `food` undergoes structural change on this snapshot. Any food/tool contrast mixes domain with volatility.

### Snapshot verdict

**BLOCKER:** the repair materially improves the implementation, but source hash `96e2ae2...` still does not identify extra authority separately from content acquisition, does not implement the reported same-token material comparator, and does not provide reconstructible/source-valid evidence. Keep discovery and all ecology/selection claims blocked. Reassess the later committed repair using actual-path assertions; do not infer closure from the passing fixture suite or the stale `passed` handoff.

---

## Final fixed-source causal retake — core commit `d049551`

**Audit base:** repair commit `d0495519368ae07865418c0b3db104361858e4b9`, with documentation-only HEAD `f934e6baec10f3671b31d1e57fe8bdef40d6f971`.

| File | SHA-256 reviewed |
|---|---|
| `v7/experiments/model.py` | `4c87a8a3857ae05cdb71aad35064c3312feba500259e1509dc4ef5b95cdc331c` |
| `v7/experiments/exact.py` | `965e2c93e5d405c2f476a08ec89465d2d643be9300bdc9d1ab779bea0a3e0b00` |
| `v7/experiments/run_experiments.py` | `ae43019cc1b20301374c76c0ea8bc624c0c7c7f1af7ca51b12a5234e8e9f7e62` |
| `v7/experiments/verify.py` | `08e02a30c9e6bf9a604c5923d9a9382dbfda94f7b16640b580f98f8fe4895838` |
| `v7/tests/test_ecology.py` | `1937587067db07afd4657bbdebd6020f47dbc2fa2f2a0f6771c18f8a4bb0c2c1` |

### Verdict: **BLOCKER**

The repair closes most mechanical defects, but four small wiring/value defects still invalidate the core ordinary-learning and procedural-payoff baselines. They are directly reproducible and must be fixed before discovery. This verdict does **not** demand Slice 2B/2C long-run, selection, or evolutionary work now.

### Closed critical findings

| Construct | Result | Actual-path evidence |
|---|---|---|
| Truth firewall and world-linked cues | PASS, subject to private-use failure below | `theta`/`z` remain evaluator-side; noisy sensors generate policy-visible cues (`model.py:382-419,393-398`). |
| Both override coordinates | PASS | `_decision` selects `d_procedure` versus `d_local`; procedure actions are actual `branch_0/1`, local actions are `private/teacher` (`model.py:145-171,400-434`). |
| Content versus override | PASS | Paid `_teach` now occurs before arbitration, exposes the concrete offered sequence, does not copy `K`, and later override changes action only (`model.py:485-496,598-605,631-642`). |
| D-step physical kernel | PASS for terminal-frequency parity | IBM and analytic enumeration call the same `sample_task_outcome`; the 4,096-draw parity error is `0.005713` (`exact.py:29-65`; `run_experiments.py:173-190`). Value parity still fails below. |
| Fixed ordinary control | PASS | Normal births copy traits exactly; hidden mutation was removed (`model.py:538-552`). |
| Normal demography/newborn state | PASS | Ecological fertility begins at age five, parent pays 16, child starts with energy 8 and blank acquired state while inheriting traits (`model.py:538-552,647-660`). The paired invasion helper remains a Slice 2C issue, not evidence now. |
| Energy/resource replay | PASS for stock deltas | Charge, production, regeneration, birth, and death deltas independently reconstruct the seasonal stock residual (`model.py:364-368,460-483,547-550,568-580,649-680`). |
| Source hash binding | PASS | Ecology artifacts now bind `exact.py` and the verifier checks all listed current hashes (`run_experiments.py:186-193`; `verify.py:57-63`). |

### Remaining core blockers

#### F-01 — Private evidence and learned `B` are ignored whenever no teacher is available

With `advice=None`, `_q0_with_posterior` leaves both branch values at their zero placeholders (`model.py:150-157`). `_observation` nevertheless supplies a world-linked private cue and both branch actions (`model.py:400-419`). The result is a lexical tie: ordinary and access-off agents always choose `branch_1`, regardless of `theta`, cue, or arbitrarily strong learned `B`. The later action path then executes that branch (`model.py:638-642`). Thus the asocial comparator lacks the supposedly common private hardware, and prior physical learning does not control behavior in the exact condition where it is needed.

**Observed probe:** for each `theta in {0,1}` and both `B={branch0:.99,branch1:.01}` and its reverse, Q0 was `(('branch_0',0),('branch_1',0))` and `chosen_action='branch_1'`.

**Minimal fix:** compute branch posterior/value from private cue plus normalized branch beliefs whether or not advice exists. Social evidence should update the same branch posterior, not activate an otherwise dormant evaluator. Add an actual-path assertion that reversing a strong private posterior reverses the no-teacher/asocial action under identical hardware and budget.

#### F-02 — New evidence moves the wrong state variables

For a procedure, an opposite verification signal increases only `B[other_branch]`; `_observation` rereads only `B[offered_branch]`, so the offered posterior and re-decision remain unchanged (`model.py:408-419,621-630`). In the probe, a strong opposite signal changed `B[branch_1]` to `.9` while offered `p_advice`, posterior `.2`, and action were identical.

For local conflict, `_local_attempt` updates the single variable interpreted as `p_advice` with raw success regardless of which action was executed (`model.py:435-447`). A correct private action against a wrong tutor raised `p_advice` from `.5` to `.625`, exactly backwards. These errors defeat the otherwise-correct paid EVI/re-decision path.

**Minimal fix:** represent each binary posterior once (or renormalize both branches) and apply signed likelihood evidence. In local disagreement, tutor success should support tutor advice and private success should oppose it; agreement is not relative-source evidence. Add opposite-signal and private-versus-tutor outcome assertions that require opposite posterior/action movement.

#### F-03 — Learned teacher trust is written under a key the policy never reads

Following a teacher updates `T['teacher:{id}:{family}']` (`model.py:495,527-531`), but observations set `source_id` to the bare teacher ID (`model.py:418,432`) and `source_calibration` looks up that exact ID (`model.py:133-136`). Changing learned family-specific trust from `.01` to `.99` therefore left calibration exactly `.5`. Procedure provenance is now correctly restricted to the offered physical root, but learned trust remains behaviorally inaccessible; local messages also still invent `local-root:{teacher}:{family}` rather than using no physical root (`model.py:421-434`).

**Minimal fix:** use one family-specific source key for both write and read; pass only physical outcome roots, leaving local message roots empty unless a real trial supports them. Assert that changing only learned trust changes Q0, while unrelated-family trust and message repetition do not.

#### F-04 — Exact task costs and same-token safe work are not the individual's realized payoff

`sample_task_outcome` correctly returns prefix, finish, salvage, material, and `-2` incorrect-finish values (`exact.py:29-65`). `_attempt`, however, clips negative `net+material` to zero before production and never debits the individual (`model.py:498-532`). A forced depth-1 incorrect finish produced individual energy delta `0.0` although the exact branch value is `-2.0`. Q0 separately uses a binary correct reward/incorrect loss minus fixed material (`model.py:150-157,410-412`), not the expected whole-procedure value under `p_plus` versus `p_minus`.

The opportunity-cost comparison is also not realized: `_safe_work` spends one token for `1.2` (`model.py:534-536`), while TASK-01 calls the safe counterfactual `(D+1)*1.2`; at depth 3 the probe observed one token/`1.2` versus reported safe return `4.8`. Terminal-frequency parity therefore does not establish payoff or same-budget parity.

**Minimal fix:** define one whole-procedure expected-value adapter from the enumerated terminal values and use it in Q0. Apply sampled negative and positive net values to individual energy through ledger events. Either permit `D+1` safe-work tokens in the physical counterfactual or compare against the actual one-token opportunity set. Gate empirical terminal **value** as well as frequency. The tiny POMDP may remain an explicitly reduced benchmark; do not label its upper bound as a full-IBM bound.

### Reproduction commands and assertions

The committed suite and verifier both pass but miss the blockers:

```bash
python -m unittest v7.tests.test_ecology -v
# 13 tests: OK
python -m v7.experiments.verify --stage ecology-gates \
  --predeclared v7/evidence/predeclared_checks.json \
  --executed v7/evidence/executed_checks.json \
  --manifest v7/experiments/output/run_manifest.json
# ecology-gates verification: PASS (measured validity sentinels)
```

Minimal assertions for the next fix round:

```python
# No-teacher/private learning: must not be a lexical constant.
assert decide(B0=.99, B1=.01, teacher=None).chosen_action == "branch_0"
assert decide(B0=.01, B1=.99, teacher=None).chosen_action == "branch_1"

# Directional evidence and accessible trust.
assert posterior_after(opposite_signal) < posterior_before
assert p_advice_after(private_success_tutor_wrong) < p_advice_before
assert calibration(T_family=.99) > calibration(T_family=.01)

# Shared payoff contract.
assert individual_delta(forced_terminal="incorrect_finish", depth=1) == -2.0
assert safe_counterfactual_tokens(depth=3) == 4
assert safe_counterfactual_return(depth=3) == 4.8
```

### Prudent claim limits

At this hash it is defensible to claim a typed truth firewall, paid pre-decision content exposure, two distinct override domains, a shared D-step terminal sampler, exact trait copying in normal births, and independently replayed energy/resource stocks. It is **not** yet defensible to claim a valid ordinary/asocial learning comparator, directionally rational EVI, lifetime learned trust, whole-procedure material Q0, or task-value parity. Discovery, holdout, accumulation, selection, invasion, polymorphism, and persistence remain appropriately pending their declared later slices after these four core fixes close.

---

## Targeted F-01–F-04 regression retake — HEAD `76ce1a0`

**Scope:** only the four blockers from the preceding fixed-source audit and their direct regressions. No new model scope or later-stage outcome requirement was introduced.

| File | SHA-256 reviewed |
|---|---|
| `v7/experiments/model.py` | `8fc29507bf03f6bbd58e6a565dac15ad08d4b50fc36900d786839e63488bd503` |
| `v7/experiments/exact.py` | `681a585ac2842a0b9803d7f1b881e17984542ee9dcf6bbd1f7f8308c133646c0` |
| `v7/experiments/run_experiments.py` | `23585d1a1dc7d591007333cb15f21b1fd0188e65e3831666c038ad20f4c9a615` |
| `v7/experiments/verify.py` | `116f2858add1b8643553819fe3ff138fb3eb78ba26628f0a90af7ab143d31ce0` |
| `v7/tests/test_kernel.py` | `ec986b012922812f685c578fb1ade944223e8b7fd11fe4435ad841bc336adf13` |
| `v7/tests/test_ecology.py` | `727df68123737258b6f894b1be1f92fde261d8731d4759f96c48e21e3262549b` |

### Classification

**F-01–F-04 targeted verdict: PASS.** All four previously demonstrated causal failures are resolved on the frozen hash.

**Discovery readiness: PARTIAL.** One known finite-computation comparator defect remains and must be repaired in Slice 2B before discovery; it does not reopen F-01–F-04 or require new scientific mechanisms.

### Original blocker resolution

| Finding | Status | Regression evidence |
|---|---|---|
| F-01 private evidence/`B` ignored without teacher | **RESOLVED** | Ecology observations now carry normalized `p_branch_0/1` and a branch-valued private cue; ordinary and asocial policies use the same `branch_posteriors` path even with no advice (`model.py:137-172,180-214,435-458`). Reversing `.99/.01` beliefs reversed both policies from `branch_0` to `branch_1`. |
| F-02 evidence moved wrong variables | **RESOLVED** | Procedure verification renormalizes both branch weights and the refreshed observation changes Q0/re-decision (`model.py:675-687`). In the prior probe, an opposite signal moved offered posterior `.8 -> .307692`, Q0 preference `branch_0 -> branch_1`, and the chosen action flipped. Local private success against a wrong tutor now moves `p_advice .5 -> .2` (`model.py:474-488`). |
| F-03 learned trust unread/mis-keyed | **RESOLVED** | Both procedure and local observations use `teacher:{id}:{family}`, matching the written `T` key, while local messages carry no invented physical root (`model.py:435-471,529-540,580-584`). Trust `.01 -> .99` changed calibration `.336667 -> .663333`; the offered root remained the actual `root:t`. |
| F-04 exact/task payoff and safe counterfactual mismatch | **RESOLVED** | Q0 uses cached whole-procedure expectations under `p_plus` and `p_minus`; reward calibration uses all `D+1` hazards (`model.py:180-193,435-451`; `exact.py:20-51`). Attempts reserve `D+1` tokens, realize sampled net gains/losses, and update normalized `B` with terminal-specific Bayes likelihoods; safe work uses the same tokens (`model.py:542-590`). Reproductions gave incorrect finish `-2.0`, depth-1 correct finish `+3.8`, and depth-3 safe work `4 tokens / +4.8`. |

Neutral testimony is also genuinely neutral after the likelihood fix: social Bayes weighting multiplies the advised hypothesis by `R` and the alternative by `1-R`, rather than penalizing both at `R=.5` (`model.py:164-172`). Passing regression tests confirm that changing the procedure posterior changes Q0 and the selected branch (`test_ecology.py:172-186`).

### Commands rerun

```bash
python -m unittest v7.tests.test_kernel v7.tests.test_ecology -v
# Ran 28 tests: OK

python -m v7.experiments.verify --stage ecology-gates \
  --predeclared v7/evidence/predeclared_checks.json \
  --executed v7/evidence/executed_checks.json \
  --manifest v7/experiments/output/run_manifest.json
# ecology-gates verification: PASS (measured validity sentinels)
```

The standalone kernel verifier was not treated as a separate failure: the live `executed_checks.json` is intentionally the successor ecology-stage envelope rather than a kernel-stage input. Kernel behavior was exercised by the combined 28-test run, including `kernel_tracer` and its recorded checks.

### Remaining direct issue before discovery

#### P-01 — Feature-trust training consumes uncharged, policy-specific computation

Every season, every `FeatureTrustPolicy`/`CandidateBPolicy` individual calls `RewardPredictor.fit` from scratch over as many as 64 own history rows for as many as 40 optimization passes (`model.py:218-231,392-394,638`). At saturation this is roughly 2,560 row-updates per individual-season, while the decision reports and pays only its small inference/information operation count. This gives the resource-rational comparators undeclared computation and creates unnecessary discovery-scale cost.

**Required minimal Slice 2B preparation:** replace refitting with a declared bounded incremental LMS update on the focal individual's newest realized reward. Count the fixed multiply/add/update operations against the same computation cap and ledger price used by all policies. Add assertions that one new observation causes only the declared number of updates, no population/global outcome is read, and training plus decision operations cannot exceed or evade the common budget. Discovery remains paused until this is done.

### Allowed approximation and claim limits

- The whole-procedure Q0 is a transparent posterior proxy based on enumerated `p_plus/p_minus` returns. It is adequate as the common authority-neutral evaluator for these gates, but is not a proof of globally optimal control under resource depletion or demography.
- `ExactTinyPOMDP` remains a deliberately reduced two-episode benchmark. Its upper-bound statement applies only to its own matched restricted policy class, never to the full IBM.
- Long-run accumulation, holdout performance, selection, invasion, polymorphism, and persistence remain unmeasured later-stage questions. Their absence is not a regression failure here.

**Bottom line:** F-01 through F-04 are closed on HEAD `76ce1a0`. The repaired core validity path may advance only after P-01's charged incremental predictor update is implemented; no substantive discovery claim is authorized by this regression retake alone.


## Closure pointer (final V7 evidence)

This is a historical pre-discovery review. P-01 was subsequently addressed with a charged incremental update (regression: `test_feature_predictor_is_focal_incremental_lms_and_charged_under_common_cap`). A later no-teacher truth leak invalidated the original frozen ecology; do not read this earlier retake as validation of those results. The corrected overlay, fresh runs, comparator limitations, and final scientific dispositions are recorded in `final_scientific_review.md`, `../results.md`, and `../verification.md`.
