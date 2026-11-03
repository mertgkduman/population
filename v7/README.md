# V7 Costly Cultural Competence

V7 is an evidence-preserving study of juvenile cultural override under explicit information, computation, and material costs. Its scientific verdict is **PARTIAL**. A hidden oracle invalidated the frozen no-teacher local path; the repository preserves that failure and uses a separately registered, minimal corrected overlay with fresh seeds as the primary ecology/lineage evidence.

## Reproduce the reporting layer

```bash
python v7/synthesize_results.py --verify-only
python v7/synthesize_results.py --write
python -m unittest discover -s v7/tests -p 'test_*.py'
python v7/experiments/run_postfreeze.py --verify-freeze --manifest v7/evidence/core_freeze/manifest.json
```

`synthesize_results.py` reads frozen and corrected gzip exports, checks grain/seed/hash parity, recomputes paired summaries and across-seed MCSE, and writes derived reports. The frozen core/config/raw are never rewritten. Corrected sources were snapshotted at registration, frozen before holdout, and verified by live/result hash identity. Operational file-mode guards were not durably recorded and are not used as evidence.

## Reading order

1. `results.md` — scientific result and limits.
2. `verification.md` — all 25 predeclared checks and raw hashes.
3. `manuscript_outline.md` — defensible paper narrative.
4. `research_gaps_and_next_steps.md` — bounded follow-up agenda and dashboard handoff.
5. `project_manifest.json` — machine-readable artifact inventory.
6. `evidence/hypothesis_ledger.json` and `evidence/executed_checks.json` — machine-readable claim status.
7. `evidence/frozen_local_no_teacher_defect.json` and `evidence/corrected_local_no_teacher_audit.json` — executable failure/repair pair.
8. `evidence/data_quality.json` and `evidence/corrected/` — corrected grain, registrations, source snapshots, freeze, and result hashes.

## Non-negotiable interpretation limits

- `d=0` is ordinary social learning; asocial access is a separate comparator.
- `tau=5` is a fixed age threshold, not a fitted V1–V6 maturation mean.
- IBM Q0 is a greedy posterior proxy; the two-episode exact solver is a separate reduced toy.
- Procedural teacher choice effectively resolves by identity and content is lexical-first eligible K, not chosen from current belief or updated performance.
- Population N, net resource per agent-season, and finite living descendants are distinct outcomes.
- Rate MCSE is computed across independent seeds; event-level Wilson precision is unresolved.
- FeatureTrust is action-blind; Candidate B has approximate costs and a query evaluator/execution mismatch.
- Reproducibility is not validity: the frozen defect is retained and invalidated; correction does not upgrade unresolved biological or asymptotic claims.

`build_dashboard.py` is fail-closed: it will not build until handoff 07 identifies `corrected_overlay` as primary evidence and supplies all corrected inventory/contrast fields.


## Open the final offline explorer and reproduce controls

Read [the executive research summary](executive_summary.md). Open [research_dashboard.html](research_dashboard.html) directly in a modern browser. Download [the complete V7 source/data ZIP](full_v7_research_project.zip). The local portal is `../docs/index.html` (older versions require a local static server for split payloads).

```bash
python -m v7.experiments.run_execution_planner
python -m v7.experiments.run_resource_control
python -m v7.experiments.run_carrier_control
python -m v7.experiments.run_belief_control
python -m v7.experiments.run_information_controls
python v7/replay_registered.py --control cumulative_dag
python v7/replay_registered.py --control cumulative_dag_matched
python v7/synthesize_results.py --write
python v7/build_registry.py
python v7/build_dashboard.py --output v7/research_dashboard.html --source-zip v7/full_v7_research_project.zip
node v7/browser_verify.js
python v7/verify_artifacts.py --refresh-package
```

The first seven commands rerun the registered controls (DAG replays write temporary outputs and compare exact bytes because their historical registration CLIs reject later disclosed corrections); reporting and dashboard generation use saved data. Registrations reject changed source/config. The primary corrected 81-cell replay cache is derived, not81 independent replications; policy maps average four seeds/cell. Final controls have24 independent paired seed blocks. `experiments/output/corrected_primary_registry.json` indexes all primary registrations and accepted controls while preserving the invalidated original registry. Older recovery drafts are retained with explicit source-audit limits. See `final_controls.md` for equations, checks, model distinctions, and findings.
