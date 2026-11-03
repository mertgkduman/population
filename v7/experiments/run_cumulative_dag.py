"""Preregister, pilot, and confirm the eight-node cumulative-DAG fixture."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import argparse
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
# Permit the documented direct invocation as well as ``python -m``.
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from v7.experiments.cumulative_dag import ARMS, Settings, heldout_two_edge_test, pair, run
EVIDENCE = REPO / "v7/evidence/cumulative_dag"
OUTPUT = REPO / "v7/experiments/output/cumulative_dag"
SEEDS = tuple(range(82901, 82925))
REPRESENTATIVE_SEEDS = (82901, 82902)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def csv_gz(path: Path, rows: list[dict]) -> None:
    columns = sorted(set().union(*(row.keys() for row in rows)))
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=columns, extrasaction="raise")
    writer.writeheader(); writer.writerows(rows)
    path.write_bytes(gzip.compress(out.getvalue().encode(), mtime=0))


def source_files() -> list[Path]:
    return [REPO / "v7/experiments/cumulative_dag.py", Path(__file__),
            REPO / "v7/tests/test_cumulative_dag.py", REPO / "v7/cumulative_dag.md"]


def configuration() -> dict:
    return {
        "settings": asdict(Settings()), "fresh_seed_blocks": list(SEEDS), "pilot_seed_blocks": list(REPRESENTATIVE_SEEDS),
        "representative_full_dag_seeds": list(REPRESENTATIVE_SEEDS), "arms": list(ARMS),
        "paired_comparator": "transmission+innovation+retention versus isolated private-only populations; each receives min(N_shared,N_independent)*4 ex-ante offered work each season; no people/resources/knowledge pool.",
        "fidelity": "fixed 1.0 before outcomes", "horizon_and_caps_fixed_before_outcomes": True,
        "solo_protocol_bound": "Eight private discoveries require >=64 tokens. At most 8 safe-harvest tokens remain from 72 lifetime tokens, supplying 8+1.5*8=20 energy, below maintenance 9 plus learning 12.8 =21.8. This is only a bound under this declared physical acquisition protocol, not a cognitive impossibility theorem.",
        "hypotheses": [
            "Closed resource/living-energy, demographic identity, and person-time caps close exactly.",
            "Retention plus paid social transmission can construct the eight-node DAG beyond the declared solo protocol bound; this validates reusable-learning mechanics only.",
            "No bootstrap innovation, cleared learned state, causal prerequisite change, and independent solver controls remain literal measured comparators.",
            "A held-out test passes only after an actual baseline object is paid across source->B->C edges to blank recipients and survives physical valid-order versus violation/error probes.",
        ],
        "source_sha256": {str(p.relative_to(REPO)): sha(p) for p in source_files()},
    }


def register(config: dict, allow_heldout_correction: bool = False) -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    registration = EVIDENCE / "registration.json"
    if registration.exists():
        old = json.loads(registration.read_text())
        if old["config"] != config:
            old_without_source = {k: v for k, v in old["config"].items() if k != "source_sha256"}
            new_without_source = {k: v for k, v in config.items() if k != "source_sha256"}
            amendment = EVIDENCE / "source_amendment.json"
            if old_without_source != new_without_source:
                raise RuntimeError("frozen cumulative-DAG registration differs; refusing outcome-dependent change")
            if amendment.exists():
                final_freeze = EVIDENCE / "source_before_confirmation.json"
                if final_freeze.exists():
                    frozen = json.loads(final_freeze.read_text())
                    if frozen["source_sha256"] != config["source_sha256"]:
                        if (EVIDENCE / "summary.json").exists():
                            correction = EVIDENCE / "heldout_functional_correction.json"
                            if not allow_heldout_correction or correction.exists():
                                raise RuntimeError("source changed after completed confirmation")
                            # Preserve every initial raw result before replacing
                            # the held-out test bookkeeping.  The correction makes
                            # the already-declared test physical: it evaluates the
                            # actual DAG ordering/parameters and debits test work,
                            # energy, and four-resource success withdrawal.
                            for name in ("summary.json",):
                                path = EVIDENCE / name
                                (EVIDENCE / f"{path.stem}_before_heldout_correction{path.suffix}").write_bytes(path.read_bytes())
                            prior_heldout = OUTPUT / "heldout.csv.gz"
                            if prior_heldout.exists():
                                (OUTPUT / "heldout_before_heldout_correction.csv.gz").write_bytes(prior_heldout.read_bytes())
                            dump(correction, {"status": "functional_heldout_correction_before_reconfirmation", "reason": "Initial held-out report labelled a valid order from receipt coverage without mechanically evaluating its prerequisite order/parameters or debiting physical test work and resource withdrawal. The corrected test leaves population dynamics, seed blocks, arms, and thresholds unchanged.", "original_source_sha256": frozen["source_sha256"], "amended_source_sha256": config["source_sha256"], "scientific_configuration_unchanged": True})
                            with tarfile.open(EVIDENCE / "source_heldout_corrected.tar.gz", "w:gz") as archive:
                                for path in source_files():
                                    archive.add(path, arcname=str(path.relative_to(REPO)))
                            return
                        repair = EVIDENCE / "source_runtime_correction.json"
                        if repair.exists():
                            repaired = json.loads(repair.read_text())
                            if repaired["amended_source_sha256"] != config["source_sha256"]:
                                raise RuntimeError("source changed after the one allowed failed-run correction")
                            return
                        dump(repair, {"status": "runtime_correction_before_completed_confirmation", "reason": "First confirmation stopped before a summary when an energy-depleted held-out B lacked a module; guard now retains that failed paid transfer instead of raising KeyError.", "original_source_sha256": frozen["source_sha256"], "amended_source_sha256": config["source_sha256"], "scientific_configuration_unchanged": True})
                        with tarfile.open(EVIDENCE / "source_runtime_corrected.tar.gz", "w:gz") as archive:
                            for path in source_files():
                                archive.add(path, arcname=str(path.relative_to(REPO)))
                        return
                    return
                # The first pilot was preserved above.  Archive the corrected,
                # mechanically equivalent source one final time before a broad
                # result exists; this branch cannot alter scientific settings.
                dump(final_freeze, {"status": "final_source_archived_before_confirmation", "source_sha256": config["source_sha256"], "scientific_configuration_unchanged": True})
                with tarfile.open(EVIDENCE / "source_before_confirmation.tar.gz", "w:gz") as archive:
                    for path in source_files():
                        archive.add(path, arcname=str(path.relative_to(REPO)))
                return
            # The two-seed pilot exposed only a reporting-gate bug: the check
            # mistook a later-trained descendant for a nonblank newborn.  The
            # model, seeds, arms, and all scientific settings are identical.
            # Preserve the original freeze and archive this mechanical amendment
            # before any 24-seed confirmation is allowed to start.
            original_gates = EVIDENCE / "gates_pilot.json"
            if original_gates.exists():
                (EVIDENCE / "gates_pilot_pre_amendment.json").write_bytes(original_gates.read_bytes())
            dump(amendment, {"status": "source_amendment_before_confirmation", "reason": "Pilot newborn_blank_gate inspected all living descendants rather than birth events; corrected gate now checks the recorded birth receipt count.", "original_source_sha256": old["config"]["source_sha256"], "amended_source_sha256": config["source_sha256"], "scientific_configuration_unchanged": True})
            with tarfile.open(EVIDENCE / "source_amended.tar.gz", "w:gz") as archive:
                for path in source_files():
                    archive.add(path, arcname=str(path.relative_to(REPO)))
        return
    dump(registration, {"registered_at": datetime.now(timezone.utc).isoformat(), "status": "registered_before_confirmation", "config": config, "python": sys.version})
    with tarfile.open(EVIDENCE / "source.tar.gz", "w:gz") as archive:
        for path in source_files():
            archive.add(path, arcname=str(path.relative_to(REPO)))


def checks(world) -> dict:
    result = world.result()
    return {"stock_gate": result["max_residual"] < 1e-7, "time_gate": result["max_person_work"] <= 4,
            "population_gate": all(row["N"] == row["F"] + row["A"] for row in world.history),
            "newborn_blank_gate": all(event["cultural_receipts_inherited"] == 0 for event in world.events if event["kind"] == "birth"),
            "work_exact": all(row["realized"] == row["offered"] for row in world.history),
            "receipt_objects": all(r["owner_id"] == r["learner_id"] and r["receipt_id"] in r["procedure_id"] for r in world.receipts.values())}


def execute(seeds: tuple[int, ...], label: str) -> dict:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    endpoint_rows: list[dict] = []
    season_rows: list[dict] = []
    heldout_rows: list[dict] = []
    representative: dict[str, dict] = {}
    gate_rows: list[dict] = []
    for seed in seeds:
        worlds = {}
        for arm in ARMS:
            world = run(seed, arm); worlds[arm] = world
            endpoint_rows.append({"phase": label, **world.result()})
            season_rows.extend({"phase": label, "seed": seed, "arm": arm, **row} for row in world.history)
            gate_rows.append({"phase": label, "seed": seed, "arm": arm, **checks(world)})
            if arm == "transmission_innovation_retention":
                held = heldout_two_edge_test(world)
                heldout_rows.append({"phase": label, "seed": seed, "status": held["status"],
                                     "two_actual_paid_edges_per_module": held.get("two_actual_paid_edges_per_module", False),
                                     "edge_count": len(held["edges"]), "physical_tests": json.dumps(held["physical_tests"], sort_keys=True),
                                     "failure_count": len(held.get("failures", []))})
                if seed in REPRESENTATIVE_SEEDS:
                    representative[str(seed)] = {"result": world.result(), "receipts": list(world.receipts.values()),
                                                  "events": world.events, "heldout": held}
        shared, independent = pair(seed)
        for arm, world in (("paired_transmission_innovation_retention", shared), ("paired_independent_private_only", independent)):
            endpoint_rows.append({"phase": label + "_paired", **world.result(), "arm": arm})
            season_rows.extend({"phase": label + "_paired", "seed": seed, "arm": arm, **row} for row in world.history)
            gate_rows.append({"phase": label + "_paired", "seed": seed, "arm": arm, **checks(world)})
        for a, b in zip(shared.history, independent.history):
            if a["offered"] != b["offered"] or a["realized"] != b["realized"] or a["realized"] != a["offered"]:
                raise AssertionError("paired ex-ante work schedule did not execute exactly")
    suffix = "pilot" if label == "pilot" else ""
    postfix = f"_{suffix}" if suffix else ""
    csv_gz(OUTPUT / f"endpoints{postfix}.csv.gz", endpoint_rows)
    csv_gz(OUTPUT / f"seasons{postfix}.csv.gz", season_rows)
    csv_gz(OUTPUT / f"heldout{postfix}.csv.gz", heldout_rows)
    dump(EVIDENCE / f"gates{postfix}.json", gate_rows)
    for seed, dag in representative.items():
        (OUTPUT / f"full_dag_seed{seed}{postfix}.json.gz").write_bytes(gzip.compress(json.dumps(dag, sort_keys=True).encode(), mtime=0))
    return {"endpoints": endpoint_rows, "heldout": heldout_rows, "gates": gate_rows, "representative": representative}


def mean_mcse(values: list[float]) -> dict:
    return {"n": len(values), "mean": statistics.fmean(values),
            "seed_mcse": statistics.stdev(values) / len(values) ** 0.5 if len(values) > 1 else None}


def summarize(data: dict, config: dict) -> dict:
    rows = [r for r in data["endpoints"] if r["phase"] == "confirmation"]
    result = {"status": "complete", "interpretation": "Additional causal-DAG validation fixture. Any positive cumulative performance demonstrates the specified reusable-learning/work assumptions, not childhood deference, authority adaptation, novelty, or a changed primary V7 effect.",
              "denominators": {"fresh_seed_blocks": len(SEEDS), "all_statuses_retained": True,
                               "extinct_censored_infeasible_retained": True},
              "gates": {name: all(row[name] for row in data["gates"]) for name in ("stock_gate", "time_gate", "population_gate", "newborn_blank_gate", "work_exact", "receipt_objects")},
              "status_counts": {status: sum(r["status"] == status for r in rows) for status in sorted({r["status"] for r in rows})},
              "arm_summaries": {}, "heldout": {"n": len(data["heldout"]), "status_counts": {}, "paid_two_edge_passes": 0},
              "source_sha256": config["source_sha256"]}
    for arm in ARMS:
        arm_rows = [r for r in rows if r["arm"] == arm]
        result["arm_summaries"][arm] = {"functional_end": mean_mcse([float(r["functional"]) for r in arm_rows]),
                                         "innovations": mean_mcse([float(r["innovations"]) for r in arm_rows]),
                                         "copies": mean_mcse([float(r["copies"]) for r in arm_rows]),
                                         "recombinations": mean_mcse([float(r["recombinations"]) for r in arm_rows]),
                                         "mean_population": mean_mcse([float(r["mean_population"]) for r in arm_rows])}
    result["heldout"]["status_counts"] = {status: sum(r["status"] == status for r in data["heldout"]) for status in sorted({r["status"] for r in data["heldout"]})}
    result["heldout"]["paid_two_edge_passes"] = sum(r["status"] == "passed" and r["two_actual_paid_edges_per_module"] for r in data["heldout"])
    result["raw_sha256"] = {str(p.relative_to(REPO)): sha(p) for p in OUTPUT.iterdir() if p.is_file() and "pilot" not in p.name}
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true", help="Run the preregistered two-seed gate pilot only.")
    parser.add_argument("--confirm", action="store_true", help="Run all preregistered 24 fresh seed blocks.")
    parser.add_argument("--reconfirm-functional-gate", action="store_true", help="One transparent rerun after a held-out physical-test bookkeeping correction.")
    args = parser.parse_args()
    if sum((args.pilot, args.confirm, args.reconfirm_functional_gate)) != 1:
        parser.error("choose exactly one of --pilot or --confirm")
    config = configuration(); register(config, allow_heldout_correction=args.reconfirm_functional_gate)
    if args.pilot:
        data = execute(REPRESENTATIVE_SEEDS, "pilot")
        dump(EVIDENCE / "pilot_summary.json", {"status": "pilot_complete_no_effect_tuning", "gate_pass": all(all(v for v in row.values() if isinstance(v, bool)) for row in data["gates"]), "seed_blocks": list(REPRESENTATIVE_SEEDS)})
        print(json.dumps(json.loads((EVIDENCE / "pilot_summary.json").read_text()), indent=2)); return
    data = execute(SEEDS, "confirmation")
    summary = summarize(data, config)
    dump(EVIDENCE / "summary.json", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
