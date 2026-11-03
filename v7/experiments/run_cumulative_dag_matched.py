"""Fresh, separately registered matched-total-work DAG control.

The frozen cumulative-DAG fixture remains untouched.  This runner uses its
strict ``pair`` ledger to compare two physically separate populations under
the same ex-ante feasible total work offer each season.
"""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import statistics
import sys
import tarfile

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from v7.experiments.cumulative_dag import Settings, pair

EVIDENCE = REPO / "v7/evidence/cumulative_dag_matched"
OUTPUT = REPO / "v7/experiments/output/cumulative_dag_matched"
SEEDS = tuple(range(82925, 82949))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def csv_gz(path: Path, rows: list[dict]) -> None:
    fields = sorted(set().union(*(row.keys() for row in rows)))
    out = io.StringIO(); writer = csv.DictWriter(out, fieldnames=fields)
    writer.writeheader(); writer.writerows(rows)
    path.write_bytes(gzip.compress(out.getvalue().encode(), mtime=0))


def source_files() -> list[Path]:
    return [Path(__file__), REPO / "v7/experiments/cumulative_dag.py",
            REPO / "v7/tests/test_cumulative_dag_matched.py", REPO / "v7/cumulative_dag_matched.md"]


def config() -> dict:
    return {
        "settings": asdict(Settings()), "fresh_pair_seed_blocks": list(SEEDS), "horizon_fixed_before_outcomes": 60,
        "arms": {"shared": "transmission_innovation_retention", "independent": "private_only"},
        "work_protocol": "At season start, offer min(N_shared,N_independent)*4 tokens to each separate population. Each allocation is centrally bounded at four/person; a run is work_infeasible if either side does not realize its exact offered total. No births are deleted or otherwise forced to preserve equality.",
        "independence": "Each pair is two different World objects with distinct people, resource stock, receipts, and events. They share no culture, resources, or people.",
        "denominators": "All complete, cap-censored, extinct, work-infeasible, and paired-stop outcomes are retained for all 24 pairs.",
        "source_sha256": {str(path.relative_to(REPO)): sha(path) for path in source_files()},
    }


def register(value: dict) -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE / "registration.json"
    if path.exists():
        old = json.loads(path.read_text())["config"]
        if old != value:
            old_without_source = {key: item for key, item in old.items() if key != "source_sha256"}
            new_without_source = {key: item for key, item in value.items() if key != "source_sha256"}
            amendment = EVIDENCE / "source_runtime_correction.json"
            if old_without_source != new_without_source or amendment.exists():
                raise RuntimeError("frozen matched-control registration differs")
            # The first attempt wrote raw rows but stopped before any outcome
            # summary because an endpoint dictionary overwrote its comparison
            # arm label. Preserve those rows and archive the one mechanical
            # correction before the complete fixed-24 analysis runs.
            if OUTPUT.exists():
                for raw in OUTPUT.iterdir():
                    if raw.is_file():
                        (OUTPUT / f"{raw.stem}_pre_runtime_fix{raw.suffix}").write_bytes(raw.read_bytes())
            dump(amendment, {"status": "source_correction_before_completed_run", "reason": "Endpoint merge let World.result arm overwrite the comparison label, causing a KeyError during summary assembly; corrected merge preserves the explicit pair arm label. No seed, horizon, setting, or work protocol changed.", "original_source_sha256": old["source_sha256"], "amended_source_sha256": value["source_sha256"], "scientific_configuration_unchanged": True})
            with tarfile.open(EVIDENCE / "source_runtime_corrected.tar.gz", "w:gz") as archive:
                for source in source_files():
                    archive.add(source, arcname=str(source.relative_to(REPO)))
        return
    dump(path, {"registered_at": datetime.now(timezone.utc).isoformat(), "status": "registered_before_outcomes", "config": value, "python": sys.version})
    with tarfile.open(EVIDENCE / "source.tar.gz", "w:gz") as archive:
        for source in source_files():
            archive.add(source, arcname=str(source.relative_to(REPO)))


def mcse(values: list[float]) -> dict:
    return {"n": len(values), "mean": statistics.fmean(values),
            "seed_mcse": statistics.stdev(values) / len(values) ** .5 if len(values) > 1 else None}


def run_all() -> dict:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    endpoints: list[dict] = []
    seasons: list[dict] = []
    pair_rows: list[dict] = []
    for seed in SEEDS:
        shared, independent = pair(seed)
        assert shared.people is not independent.people
        assert shared.receipts is not independent.receipts
        exact_work = len(shared.history) == len(independent.history)
        for shared_row, independent_row in zip(shared.history, independent.history):
            equal = (shared_row["offered"] == independent_row["offered"] == shared_row["realized"] == independent_row["realized"])
            exact_work = exact_work and equal
            pair_rows.append({"seed": seed, "season": shared_row["season"], "offered_each": shared_row["offered"],
                              "realized_shared": shared_row["realized"], "realized_independent": independent_row["realized"],
                              "exact_equal": equal, "N_shared": shared_row["N"], "N_independent": independent_row["N"]})
        pair_status = "exact_work_complete" if exact_work and shared.result()["status"] == independent.result()["status"] == "complete_horizon" else "retained_noncomplete_or_infeasible"
        for label, world in (("shared_transmission_innovation_retention", shared), ("independent_private_only", independent)):
            outcome = world.result()
            endpoints.append({"seed": seed, "pair_status": pair_status, "exact_work": exact_work, **outcome, "comparison_arm": label})
            seasons.extend({"seed": seed, "arm": label, **row} for row in world.history)
    csv_gz(OUTPUT / "endpoints.csv.gz", endpoints)
    csv_gz(OUTPUT / "seasons.csv.gz", seasons)
    csv_gz(OUTPUT / "pair_work.csv.gz", pair_rows)
    return {"endpoints": endpoints, "seasons": seasons, "pairs": pair_rows}


def summarize(data: dict, frozen_config: dict) -> dict:
    endpoints = data["endpoints"]
    shared = [row for row in endpoints if row["comparison_arm"] == "shared_transmission_innovation_retention"]
    independent = [row for row in endpoints if row["comparison_arm"] == "independent_private_only"]
    by_seed_shared = {row["seed"]: row for row in shared}
    by_seed_independent = {row["seed"]: row for row in independent}
    differences = [float(by_seed_shared[seed]["functional"]) - float(by_seed_independent[seed]["functional"]) for seed in SEEDS]
    result = {
        "status": "complete", "interpretation": "Fresh matched-total-work comparator for the additional DAG fixture. It tests the specified reusable-learning/work implementation, not authority, deference, novelty, or a primary V7 selection claim.",
        "denominators": {"fresh_independent_pairs": len(SEEDS), "all_pairs_retained": True},
        "work_gate": {"all_season_rows_exact_equal": all(row["exact_equal"] for row in data["pairs"]),
                      "all_pair_endpoints_exact_work": all(row["exact_work"] for row in endpoints),
                      "n_pair_season_rows": len(data["pairs"])},
        "status_counts": {label: {status: sum(row["status"] == status for row in rows) for status in sorted({row["status"] for row in rows})} for label, rows in (("shared", shared), ("independent", independent))},
        "functional_end": {"shared": mcse([float(row["functional"]) for row in shared]), "independent": mcse([float(row["functional"]) for row in independent]), "paired_difference_shared_minus_independent": mcse(differences)},
        "source_sha256": frozen_config["source_sha256"],
        "raw_sha256": {str(path.relative_to(REPO)): sha(path) for path in OUTPUT.iterdir() if path.is_file()},
    }
    return result


def main() -> None:
    frozen = config(); register(frozen)
    data = run_all()
    dump(EVIDENCE / "summary.json", summarize(data, frozen))
    print(json.dumps(json.loads((EVIDENCE / "summary.json").read_text()), indent=2))


if __name__ == "__main__":
    main()
