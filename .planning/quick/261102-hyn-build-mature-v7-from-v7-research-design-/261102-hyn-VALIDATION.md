---
phase: quick-261102-hyn
slug: build-mature-v7-from-v7-research-design
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-11-02
---

# V7 quick-full — Validation Strategy

This is the fail-closed test-availability and evidence map for `261102-hyn-PLAN.md`. Scientific stages may produce null, PARTIAL, unsupported, NOT_TESTED, or UNRESOLVED verdicts; those are valid outcomes. A failed construct/accounting gate blocks downstream claims and runs.

## Test Infrastructure

| Property | Value |
|---|---|
| Framework | Python standard-library `unittest`; local Node/Chrome harness for the offline dashboard |
| Config | `v7/experiments/config.json` with JSON-schema validation from `v7/parameter_schema.json` |
| Quick kernel command | `OPENBLAS_NUM_THREADS=1 python -m unittest discover -s v7/tests -p 'test_kernel.py' -v` |
| Quick ecology command | `OPENBLAS_NUM_THREADS=1 python -m unittest discover -s v7/tests -p 'test_ecology.py' -v` |
| Quick post-freeze command | `OPENBLAS_NUM_THREADS=1 python -m unittest discover -s v7/tests -p 'test_postfreeze.py' -v` |
| Quick reporting command | `OPENBLAS_NUM_THREADS=1 python -m unittest discover -s v7/tests -p 'test_reporting.py' -v` |
| Full evidence command | `python v7/experiments/verify.py --stage final --manifest v7/experiments/output/run_manifest.json --executed v7/evidence/executed_checks.json` |
| Feedback target | Unit/gate commands under 60 seconds; bounded scientific runs execute separately and are verified from immutable outputs |

## Wave 0 Test Availability

Slice `1A-wave0-contract` runs before production implementation and creates all four files below with at least one deliberately failing test per mapped behavior. No external test package is installed.

| Test file | Availability before execution | Created by | Required before |
|---|---|---|---|
| `v7/tests/test_kernel.py` | MISSING — Wave 0 | Task 1 Slice 1A | Slice 1B |
| `v7/tests/test_ecology.py` | MISSING — Wave 0 | Task 1 Slice 1A | Slice 2A |
| `v7/tests/test_postfreeze.py` | MISSING — Wave 0 | Task 1 Slice 1A | Slice 3A |
| `v7/tests/test_reporting.py` | MISSING — Wave 0 | Task 1 Slice 1A | Slice 3B |

Wave 0 completion is recorded in `v7/evidence/handoffs/01-wave0.json` with test-file hashes and failing-direction names. Slice 1B must refuse to start if any file or named failing direction is missing.

## Task and Slice Verification Map

| Task / slice | Authored files | Automated evidence command | Fails when | Blocks |
|---|---:|---|---|---|
| 1 / 1A Wave 0 + contract | 8 | `python -c "from pathlib import Path; names=['test_kernel.py','test_ecology.py','test_postfreeze.py','test_reporting.py']; assert all((Path('v7/tests')/n).is_file() for n in names)"` | Any required test file/failing direction or fixed contract field is absent | All production code |
| 1 / 1B kernel + exact | 5 | `python v7/experiments/verify.py --stage kernel --predeclared v7/evidence/predeclared_checks.json --executed v7/evidence/executed_checks.json` | Any kernel blocker fails, exact policy is beaten, or safe-work economics gate fails | All ecology |
| 2 / 2A ecology validity | 5 | `python v7/experiments/verify.py --stage ecology-gates --manifest v7/experiments/output/run_manifest.json` | Task economics, energy/census/teaching ledger, demography/cap, stream/hash, or neutral viability fails | Discovery and holdout |
| 2 / 2B discovery + confirmation | 4 | `python v7/experiments/verify.py --stage confirmation --manifest v7/experiments/output/run_manifest.json` | Seed partition/freeze/cap/precision rule, culture controls, or holdout provenance fails | Evolution and post-freeze work |
| 2 / 2C neutral + substantive selection | 4 | `python v7/experiments/verify.py --stage neutral-selection --manifest v7/experiments/output/run_manifest.json` before `--stage selection` | Paid-birth, self-mutant, neutral drift, exchange, resident teacher composition, or neutral ledger fails | Substantive resident-mutant and competition runs |
| 3 / 3A post-freeze assays | 4 | `python v7/experiments/run_postfreeze.py --verify-freeze --manifest v7/evidence/core_freeze/manifest.json` plus `test_postfreeze.py` | Any frozen byte/replay differs, direct adult override remains active, or construct states alias | Persistence/norm/hitchhiking claims and synthesis |
| 3 / 3B results synthesis | 2 | `python -m unittest discover -s v7/tests -p 'test_reporting.py' -v` | A verdict lacks evidence/claim limit, extinct/censored run is omitted, or displayed record cannot be recomputed | Dashboard/portal |
| 3 / 3C dashboard + portal | 8 | `python v7/build_dashboard.py --verify && node v7/browser_verify.js && python scripts/verify_pages.py` | Any data mismatch, external request, V1–V6 hash drift, broken export/link, or V7 `docs/` addition exceeds 8,000,000 bytes | Completion |

Each slice runs in a fresh context, first validates the predecessor handoff, and writes the next handoff atomically. No slice authors more than 15 files.

## Predeclared Check Map

| Check IDs | Test/evidence owner | Earliest runnable slice | Pass evidence | Failure blocks |
|---|---|---|---|---|
| `AUTH-01`, `AUTH-02`, `AUTH-03` | `test_kernel.py`; kernel decision replay | 1B | `executed_checks.json`, `kernel.json` | Authority/deference claims and ecology |
| `HIDDEN-01`, `RNG-01` | `test_kernel.py`; hidden-label/unused-draw replay digests | 1B | `kernel.json` | All causal comparisons |
| `PROV-01`, `BUDGET-01`, `CLASS-01` | `test_kernel.py`; forced-history/provenance fixtures | 1B | `executed_checks.json` | Evidence/intermediate-policy claims |
| `INHERIT-01`, `FOUNDER-01`, `MATURITY-01` | `test_kernel.py`; newborn/founder/emulation fixtures | 1B | `executed_checks.json` | Culture, demography, selection |
| `COMP-01` | `test_kernel.py`; `exact.py` state/action values | 1B | `kernel.json` | Specialized-authority claims and ecology |
| `TASK-01` | `test_kernel.py` then `test_ecology.py`; exact same-token safe-work enumeration at D=1/3/6 | 1B, reaffirmed 2A | task-economics table in `kernel.json` and handoff 03 | All ecology/accumulation |
| `LEDGER-01`, `TEACH-01`, `GROWTH-01` | `test_ecology.py`; neutral ecology sentinels | 2A | handoff 03 and `executed_checks.json` | Discovery, holdout, selection |
| `ACCUM-01`, `ACCUM-02` | `test_ecology.py`; matched-work/carrier-loss runs | 2B | holdout records and check evidence | Accumulation claims only; null allowed |
| `INVASION-01`, `INVASION-02` | `test_ecology.py`; neutral paid-birth stage | 2C before substantive stage | handoff 05 neutral-gate section | Substantive selection/evolution claims |
| `RISK-01`, `COND-01` | `test_ecology.py`; tiny growth oracle and ITT/denominator audit | 2B | `executed_checks.json` | Multiplicative-risk/conditional causal claims |
| `NORM-01`, `NORM-02` | `test_postfreeze.py`; matched evidence, devaluation/degradation/countermand/generalization | 3A | persistence records and handoff 06 | Dogmatism/normative labels; learned persistence/null may remain |
| `EXPORT-01` | `test_reporting.py`, dashboard/browser/portal verifier | 3B–3C | export/browser/publication reports | Dissemination and completion |

## Practical Precision and Cap Validation

All rules are fixed before holdout outcomes. Begin at 24 fresh paired seeds and add eight at a time through 96 only when the primary contrast misses its row's target.

| Primary estimand | Precision target | Validation |
|---|---|---|
| Net energy yield | paired MCSE `<=0.10` energy/agent-season | Recompute from seed-level paired rows |
| Held-out success, action/revision, extinction, establishment | Wilson 95% half-width `<=0.10` | Recompute numerator/denominator including extinction |
| Useful depth | MCSE `<=0.25` prerequisite levels | Seed-level paired contrasts |
| Recovery time | MCSE `<=2` seasons with nonrecovery retained under the declared censoring rule | Censoring/endpoint audit |
| Mean population | MCSE `<=5` individuals | Seed-level unconditional mean |
| Expected descendants | MCSE `<=0.25` descendants per paid initial newborn, zeros included | Raw descendant-count audit |

At 96 seeds, any missed target is `UNRESOLVED`. P-value proximity, effect direction, and policy rank are forbidden stopping inputs. The verifier injects synthetic near-threshold p-values and sign reversals to prove the same seed schedule is chosen.

## Fixed Bounds and Storage Validation

| Bound | Fixed value | Failing direction |
|---|---:|---|
| Ecology | 60 burn-in + 180 measurement seasons | Run exceeds horizon or omits terminal status |
| H9 | shock at measurement 90; censor at 180 | Recovery after censor enters primary mean |
| Lineage / direct competition | 80 / 120 seasons | Run continues or relabels finite statistic |
| Persistence | 40 training + 20 per intervention | Direct adult override active or horizon changes |
| Population / events / trajectory wall time | 512 / 1,500,000 / 120 s | Birth is silently suppressed or cap-hit run omitted |
| Total trajectories / workers / wall time | 12,000 / 4 / 12 h | Outcome-responsive reallocation or unrecorded work |
| Decision sample / representative histories | 10,000 records / exactly 24 histories | Unbounded event retention or post-outcome representative selection |
| Experiment output / site payload | 256 MiB / 8,000,000 decimal bytes of V7 `docs/` additions | Silent truncation or site cap exceeded |

## Manual-Only Verifications

All scientific and artifact requirements have automated checks. Human interpretation may review figures and prose, but it cannot turn a failed automated gate into a pass.

## Validation Sign-Off

- [x] Every task has an `<automated>` command.
- [x] Wave 0 creates every referenced test before its dependent slice.
- [x] Every predeclared check maps to a test/evidence path and blocking consequence.
- [x] Fail-closed ordering places task/ledger/demography gates before discovery and neutral-selection gates before substantive selection.
- [x] Precision, horizon, compute, population, event, raw-storage, and site-size rules are outcome-independent and bounded.
- [x] Post-freeze validation checks runnable source bytes and fixed replay digests.
- [x] No watch mode or external service is used.

**Approval:** planning architecture complete; Wave 0 execution pending.
