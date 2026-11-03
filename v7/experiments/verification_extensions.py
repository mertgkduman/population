"""Evidence checks for the non-core V7 confirmation extension."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from v7.experiments.run_experiments import ROOT


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rows(path: Path) -> list[dict[str, str]]:
    with gzip.open(path, "rt", newline="") as handle:
        return list(csv.DictReader(handle))


def _archived_replay(archive_path: Path) -> str:
    """Run the fixed sentinel from extracted frozen bytes, never live imports."""
    with tempfile.TemporaryDirectory(prefix="v7-freeze-") as directory:
        root = Path(directory) / "v7"
        root.mkdir()
        with tarfile.open(archive_path, "r:gz") as archive:
            archive.extractall(root, filter="data")
        program = (
            "from v7.experiments.run_experiments import _regime, _run_cell; "
            "row=_run_cell({**_regime(4), 'seed':71999, 'policy':'vector_0_0', "
            "'stage':'archive_replay', 'graph_variant':0}); print(row['replay_digest'])"
        )
        environment = {**os.environ, "PYTHONPATH": directory}
        completed = subprocess.run([sys.executable, "-B", "-c", program], cwd=directory, env=environment,
                                   text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return completed.stdout.strip()


def verify_confirmation() -> dict[str, Any]:
    output, freeze_dir = ROOT / "experiments/output", ROOT / "evidence/core_freeze"
    manifest = json.loads((output / "run_manifest.json").read_text())
    # The frozen core uses a single manifest filename.  Preserve this completed
    # confirmation registration before restoring the tracked discovery manifest.
    (output / "confirmation_run_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    freeze = json.loads((freeze_dir / "manifest.json").read_text())
    holdout = output / "holdout.csv.gz"
    rows = _rows(holdout)
    source_match = {relative: _sha(ROOT / relative) == digest for relative, digest in freeze["source_sha256"].items()}
    archive_match: dict[str, bool] = {}
    with tarfile.open(freeze_dir / "source.tar.gz", "r:gz") as archive:
        for relative, digest in freeze["source_sha256"].items():
            member = archive.extractfile(relative)
            archive_match[relative] = member is not None and hashlib.sha256(member.read()).hexdigest() == digest
    archive_replay = _archived_replay(freeze_dir / "source.tar.gz")
    expected = 9 * 6 * 24 + 3 * 24
    checks = {
        "confirmation_manifest_complete": manifest.get("stage") == "confirmation" and manifest.get("status") == "complete" and manifest.get("outcomes_read") is True,
        "raw_row_count": len(rows) == expected,
        "fresh_seed_partition": {int(row["seed"]) for row in rows} == set(range(72001, 72025)),
        "unseen_graph": {row["graph_variant"] for row in rows} == {"1"},
        "frozen_sources": all(source_match.values()),
        "archived_sources": all(archive_match.values()),
        "archived_sentinel_replay": archive_replay == freeze["replay"]["replay_digest"],
        "raw_hash_bound": manifest.get("output_sha256", {}).get("holdout.csv.gz") == _sha(holdout),
        "terminal_statuses_complete": all(row["status"] in {"running", "extinct", "cap_censored"} for row in rows),
    }
    return {"stage": "confirmation-extension-verification", "status": "passed" if all(checks.values()) else "failed",
            "checks": checks, "row_count": len(rows), "source_match": source_match, "archive_match": archive_match,
            "archive_replay_digest": archive_replay, "holdout_sha256": _sha(holdout), "claim_limit": "Checks registration, hashes, raw completeness, and terminal retention only; it does not establish a substantive behavioral claim."}


def main() -> None:
    result = verify_confirmation()
    evidence = ROOT / "evidence/confirmation_verification.json"
    evidence.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
