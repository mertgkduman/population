"""Registered runner for V7 Slice 3A post-freeze assays.

The runner creates its registration before opening outcomes and writes a separate
post-freeze namespace. It never rewrites the frozen core run manifest.
"""
from __future__ import annotations

import argparse
import csv
import gzip
from hashlib import sha256
import json
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from v7.experiments.postfreeze import (
    EXPECTED_REPLAY_DIGEST, FREEZE_DIR, FreezeManifest, FrozenCoreObservation,
    records_for_seed, summarize_records, verify_frozen_core, yoked_decision_records,
)
from v7.experiments.verification_extensions import _archived_replay
from v7.experiments.run_experiments import _regime, _run_cell

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "experiments" / "output"
EVIDENCE = ROOT / "evidence"
SEEDS = tuple(range(74001, 74025))
PROBES = ("audience_removal", "bidirectional_equalized_counterevidence", "free_audit", "outcome_devaluation", "contingency_degradation")


def _sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _write_csv_gz(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = sorted({key for row in rows for key in row})
    with gzip.open(path, "wt", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)


def _seed_records(seed: int) -> list[dict[str, Any]]:
    return records_for_seed(seed) + yoked_decision_records(seed)


def _live_replay() -> str:
    return str(_run_cell({**_regime(4), "seed": 71999, "policy": "vector_0_0", "stage": "postfreeze_live_replay", "graph_variant": 0})["replay_digest"])


def verify_freeze(manifest_path: Path) -> dict[str, Any]:
    manifest = FreezeManifest(json.loads(manifest_path.read_text()))
    byte_check = verify_frozen_core(manifest)
    archive_replay = _archived_replay(FREEZE_DIR / "source.tar.gz")
    live_replay = _live_replay()
    expected = manifest.payload["replay"]["replay_digest"]
    checks = {
        "live_and_archive_source_bytes": byte_check.source_bytes_identical,
        "registered_replay_record": byte_check.fixed_replay_digest_identical,
        "archive_replay": archive_replay == expected == EXPECTED_REPLAY_DIGEST,
        "live_replay": live_replay == expected == EXPECTED_REPLAY_DIGEST,
    }
    return {"stage": "postfreeze-freeze-verification", "status": "passed" if all(checks.values()) else "failed",
            "checks": checks, "expected_replay": expected, "archive_replay": archive_replay, "live_replay": live_replay,
            "live_mismatches": byte_check.live_mismatches, "archive_mismatches": byte_check.archive_mismatches}


def _registration() -> dict[str, Any]:
    manifest = FreezeManifest.contract_fixture().payload
    return {
        "stage": "postfreeze-registration", "registered_at": datetime.now(timezone.utc).isoformat(),
        "seeds": list(SEEDS), "workers_cap": 4, "trajectory_cap_global": 12000,
        "training_seasons": 40, "intervention_seasons_per_probe": 20, "probes": list(PROBES),
        "adult_direct_override": 0.0, "core_freeze_sha256": _sha(FREEZE_DIR / "manifest.json"),
        "core_replay_digest": manifest["replay"]["replay_digest"], "source_sha256": _sha(Path(__file__)),
        "yoked_assay": {"depths": [1, 3, 6], "contexts": [.5, .75, 1.0], "juvenile_d": [0., .5, 1.], "same_history_only_d_changes": True},
        "optional_bundle_module": "NOT_MODELED: no separately validated institutional evaluator/teaching-access mechanism; no fabricated hitchhiking outcome.",
        "h9_observation": "Registered separately; actual intervention can establish manipulation but is PARTIAL for root-diversity mediation.",
        "claim_limit": "Learned action persistence is not obligation, dogmatism, demographic selection, or a full IBM optimality result.",
    }


def run_assays(workers: int = 4) -> dict[str, Any]:
    if not 1 <= workers <= 4:
        raise ValueError("workers must be in 1..4")
    freeze = verify_freeze(FREEZE_DIR / "manifest.json")
    if freeze["status"] != "passed":
        raise RuntimeError(f"frozen-core verification failed: {freeze}")
    OUTPUT.mkdir(parents=True, exist_ok=True); EVIDENCE.mkdir(parents=True, exist_ok=True)
    registration = _registration()
    _write_json(OUTPUT / "postfreeze_registration.json", registration)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        nested = list(pool.map(_seed_records, SEEDS, chunksize=1))
    rows = [row for group in nested for row in group]
    persistence = [row for row in rows if "probe" in row]
    yoked = [row for row in rows if "same_history_id" in row]
    _write_csv_gz(OUTPUT / "persistence.csv.gz", persistence)
    _write_csv_gz(OUTPUT / "postfreeze_yoked.csv.gz", yoked)
    summary = {
        "stage": "postfreeze-assays", "status": "complete", "seed_count": len(SEEDS), "actual_rows": len(persistence),
        "yoked_rows": len(yoked), "persistence": summarize_records(persistence),
        "adult_override_all_zero": all(not row["direct_override_probability"] for row in persistence),
        "matched_evidence_all_probes": all(row["evidence_count"] == 2 for row in persistence),
        "material_transfer_net_zero": all(abs(float(row["paid_material_net"])) < 1e-12 for row in persistence),
        "dogmatism_verdict": "NULL/unsupported: factual posterior is updated under matched accessible counterevidence; action persistence is reported separately.",
        "normative_obligation_verdict": "UNSUPPORTED: no acquired injunction/countermand/generalization state is implemented.",
        "h4_bundle_verdict": registration["optional_bundle_module"], "freeze": freeze,
        "outputs": {"persistence.csv.gz": _sha(OUTPUT / "persistence.csv.gz"), "postfreeze_yoked.csv.gz": _sha(OUTPUT / "postfreeze_yoked.csv.gz")},
    }
    _write_json(OUTPUT / "postfreeze_summary.json", summary)
    _write_json(EVIDENCE / "postfreeze_freeze_verification.json", freeze)
    return summary


def _h9_seed_regime(job: tuple[int, int, float]) -> list[dict[str, Any]]:
    seed, regime, d_procedure = job
    values = _regime(regime - 1)
    observer = FrozenCoreObservation(seed, d_procedure=d_procedure, depth=int(values["depth"]),
                                     chi=float(values["chi"]), q_theta=float(values["q_theta"]))
    rows = observer.run_cloned_arms()
    for row in rows:
        row.update({"regime_label": regime, "depth": values["depth"], "chi": values["chi"], "q_theta": values["q_theta"], "juvenile_d_procedure": d_procedure})
    return rows


def run_h9_observation(workers: int = 4) -> dict[str, Any]:
    """Run a bounded post-freeze H9 manipulation, capped to one worker.

    Three predeclared regimes and 24 seeds are used; every intervention is a fresh
    cloned-core run with no external storage. The result stays PARTIAL because the
    frozen core does not expose physical independent root lineages.
    """
    if not 1 <= workers <= 4:
        raise ValueError("workers must be in 1..4")
    registration = {"stage": "postfreeze-h9-registration", "seeds": list(SEEDS), "regimes": [1, 5, 9],
                    "shock_season": 90, "recovery_horizon": 180, "external_storage": False,
                    "policy_arms": [0.0], "arms": ["control", "shock", "shock_memory_erasure"], "source_sha256": _sha(Path(__file__)),
                    "claim_limit": "PARTIAL: this bounded diagnostic is actual d=0 only; memory erasure is not carrier death, and root diversity / d-by-shock mediation are unavailable from frozen-core interfaces."}
    _write_json(OUTPUT / "postfreeze_h9_registration.json", registration)
    jobs = [(seed, regime, d) for regime in registration["regimes"] for d in registration["policy_arms"] for seed in SEEDS]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows = [row for group in pool.map(_h9_seed_regime, jobs, chunksize=1) for row in group]
    _write_csv_gz(OUTPUT / "postfreeze_h9_observation.csv.gz", rows)
    result = {"stage": "postfreeze-h9-observation", "status": "complete_partial", "rows": len(rows),
              "all_no_external_storage": all(not row["external_storage_enabled"] for row in rows),
              "claim_limit": registration["claim_limit"], "output_sha256": _sha(OUTPUT / "postfreeze_h9_observation.csv.gz")}
    _write_json(OUTPUT / "postfreeze_h9_summary.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-freeze", action="store_true")
    parser.add_argument("--manifest", type=Path, default=FREEZE_DIR / "manifest.json")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--h9-observation", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if args.verify_freeze:
        result = verify_freeze(args.manifest)
    elif args.h9_observation:
        result = run_h9_observation(args.workers)
    elif args.run:
        result = run_assays(args.workers)
    else:
        parser.error("choose --verify-freeze, --run, or --h9-observation")
    print(json.dumps(result, indent=2, sort_keys=True))
    if result.get("status") == "failed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
