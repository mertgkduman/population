"""Register and execute bounded finite resident-mutant lineage comparisons."""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from v7.experiments.evolution import (DEFAULT_REGIMES, DIRECTED_PAIRS, EXTENSION_SEEDS,
                                      LINEAGE_SEASONS, SELECTION_SEEDS, ArmResult,
                                      gate_assays, paired_lineage, summarize)

OUTPUT = ROOT / "v7" / "experiments" / "output"
EVIDENCE = ROOT / "v7" / "evidence"
FROZEN_CORE = ("experiments/model.py", "experiments/exact.py", "experiments/run_experiments.py",
               "experiments/analyze_results.py", "experiments/verify.py", "experiments/config.json",
               "parameter_schema.json")
CHECKPOINT = OUTPUT / "evolution_checkpoint.jsonl"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frozen_sources() -> dict[str, str]:
    return {name: sha(ROOT / "v7" / name) for name in FROZEN_CORE}


def manifest() -> dict[str, Any]:
    all_seeds = (*SELECTION_SEEDS, *EXTENSION_SEEDS)
    jobs = [{"seed": seed, "regime": regime, "resident": resident, "mutant": mutant, "arms": ["mutant", "neutral_tag"],
             "horizon": LINEAGE_SEASONS, "kind": "finite_lineage"}
            for seed in all_seeds for regime in DEFAULT_REGIMES
            for resident, mutant in DIRECTED_PAIRS]
    return {
        "stage": "2C-neutral-selection", "registered_before_outcomes": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "seed_schedule": {"initial": [SELECTION_SEEDS[0], SELECTION_SEEDS[-1]],
                          "extension_batches": [[x, x + 7] for x in range(73025, 73097, 8)],
                          "maximum": 96, "rule": "fixed batches only; expected-descendant MCSE <= .25 and Wilson half-width <= .10; otherwise UNRESOLVED at 96"},
        "regimes": DEFAULT_REGIMES, "directed_pairs": DIRECTED_PAIRS,
        "jobs": jobs, "registered_trajectories": len(jobs) * 2,
        "caps": {"workers": 4, "lineage_seasons": 80, "competition_seasons": 120,
                 "trajectory_cap": 12000, "population": 512, "events": 1500000, "wall_seconds": 120},
        "core_freeze_source_sha256": frozen_sources(),
        "claim_limit": "Finite paid-newborn lineage establishment and expected descendants only; no asymptotic invasion, fixation proof, or ESS claim.",
    }


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def write_rows(path: Path, rows: list[ArmResult]) -> None:
    records = []
    for row in rows:
        value = row.record()
        value["mutant_traits"] = json.dumps(value["mutant_traits"])
        value["resident_traits"] = json.dumps(value["resident_traits"])
        value["teacher_pool"] = json.dumps(value["teacher_pool"], sort_keys=True)
        value["frequency_trajectory"] = json.dumps(value["frequency_trajectory"])
        records.append(value)
    fields = list(records[0]) if records else ["seed", "regime", "directed_pair", "arm"]
    with gzip.open(path, "wt", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(records)


def checkpoint_record(handle: Any, pair: tuple[ArmResult, ArmResult]) -> None:
    """Durably retain compact per-arm summaries, never unbounded event histories."""
    for row in pair:
        handle.write(json.dumps(row.record(), sort_keys=True, separators=(",", ":")) + "\n")
    handle.flush()


def load_checkpoint() -> list[ArmResult]:
    if not CHECKPOINT.exists():
        return []
    from v7.experiments.evolution import ArmResult
    return [ArmResult(**json.loads(line)) for line in CHECKPOINT.read_text().splitlines() if line]


def targets_met(summary: dict[str, Any]) -> bool:
    contrasts = summary.get("paired_contrasts", {})
    return bool(contrasts) and all(value["paired_descendant_difference_mcse"] <= .25 and
                                   value["max_establishment_wilson_half_width"] <= .10
                                   for value in contrasts.values())


def run_job(job: tuple[int, int, tuple[tuple[float, float], tuple[float, float]]]) -> tuple[ArmResult, ArmResult]:
    """One paired counterfactual remains within one worker and one resident prefix."""
    return paired_lineage(*job)


def run(*, max_seed: int = 96) -> dict[str, Any]:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    registered = manifest()
    attempts = OUTPUT / "selection_attempts.json"
    if not attempts.exists():
        write_json(attempts, {"attempts": [{"status": "aborted_before_durable_rows", "launched_trajectories_conservative": 576,
                                              "reason": "pre-paired-MCSE implementation stopped before final CSV; no rows were persisted",
                                              "source_sha256": "not_persisted_before_durable-checkpoint"}]})
    write_json(OUTPUT / "selection_run_manifest.json", registered)
    gates = gate_assays()
    write_json(OUTPUT / "selection_gates.json", gates)
    if gates["status"] != "passed":
        return {"status": "blocked", "gates": gates, "manifest": registered}
    records: list[ArmResult] = load_checkpoint()
    seeds = list(SELECTION_SEEDS)
    cursor = 0
    while cursor < len(seeds):
        complete = {(row.seed, row.regime, row.directed_pair) for row in records if row.arm == "mutant"}
        precision = summarize(records).get("paired_contrasts", {})
        def needs_precision(regime: int, directed_pair: tuple[tuple[float, float], tuple[float, float]]) -> bool:
            value = precision.get(f"regime_{regime}|{directed_pair[0]}->{directed_pair[1]}")
            return value is None or (value["paired_descendant_difference_mcse"] > .25 or
                                     value["max_establishment_wilson_half_width"] > .10)
        jobs = [(seed, regime, directed_pair) for seed in seeds[cursor:]
                for regime in DEFAULT_REGIMES for directed_pair in DIRECTED_PAIRS
                if (seed, regime, f"{directed_pair[0]}->{directed_pair[1]}") not in complete
                and needs_precision(regime, directed_pair)]
        # Four workers is the frozen global ceiling.  Workers get independent
        # seed/regime/pair jobs; each job keeps both counterfactual arms together.
        with CHECKPOINT.open("a") as checkpoint, ProcessPoolExecutor(max_workers=4) as pool:
            for pair in pool.map(run_job, jobs):
                checkpoint_record(checkpoint, pair)
                records.extend(pair)
        cursor = len(seeds)
        summary = summarize(records)
        if targets_met(summary) or len(seeds) >= max_seed:
            break
        next_seed = 73001 + len(seeds)
        maximum_seed_number = 73000 + max_seed
        seeds.extend(range(next_seed, min(next_seed + 8, maximum_seed_number + 1)))
    write_rows(OUTPUT / "evolution.csv.gz", records)
    summary = summarize(records)
    status = "complete" if targets_met(summary) else "UNRESOLVED"
    result = {
        "stage": "2C-neutral-selection", "status": status, "seeds_run": [seeds[0], seeds[-1]],
        "records": len(records), "summary": summary,
        "gates": {"status": gates["status"], "checks": gates["checks"], "evidence": "v7/experiments/output/selection_gates.json"},
        "frequency_measurement": "Each lineage arm shares the resident resource/culture state at introduction and records descendant living frequency through the finite 80-season assay. A separate 120-season extension is not required unless a later direct-frequency question is specified.",
        "unresolved": ([] if status == "complete" else ["Practical precision target unmet at the declared cap; no outcome-directed extension was run."]),
        "source_sha256": {"evolution.py": sha(ROOT / "v7" / "experiments" / "evolution.py"),
                          "run_evolution.py": sha(ROOT / "v7" / "experiments" / "run_evolution.py")},
        "frozen_core_sha256": frozen_sources(),
        "raw_sha256": sha(OUTPUT / "evolution.csv.gz"),
        "claim_limit": "No asymptotic invasion, ESS, fixation, or adult genetic-rigidity claim is made.",
    }
    write_json(OUTPUT / "evolution_summary.json", result)
    handoff = {"slice": "2C-neutral-selection", "status": status, "predecessor": "v7/evidence/handoffs/04-confirmation.json",
               "gate_evidence": "v7/experiments/output/selection_gates.json", "result_evidence": "v7/experiments/output/evolution_summary.json",
               "raw": "v7/experiments/output/evolution.csv.gz", "raw_sha256": result["raw_sha256"],
               "registered_trajectories": registered["registered_trajectories"], "executed_trajectories": len(records),
               "finite_summary": summary, "unresolved": result["unresolved"], "claim_limit": result["claim_limit"],
               "core_freeze_unchanged": frozen_sources() == registered["core_freeze_source_sha256"]}
    write_json(EVIDENCE / "handoffs" / "05-selection.json", handoff)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-seed", type=int, default=96)
    parser.add_argument("--gates-only", action="store_true")
    args = parser.parse_args()
    if args.gates_only:
        value = gate_assays(); write_json(OUTPUT / "selection_gates.json", value); print(json.dumps(value, sort_keys=True)); return
    value = run(max_seed=args.max_seed)
    print(json.dumps({"status": value["status"], "records": value.get("records", 0)}, sort_keys=True))


if __name__ == "__main__":
    main()
