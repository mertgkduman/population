"""Pre-register, freeze, execute, and verify R4 information/memory controls."""
from __future__ import annotations

import csv, gzip, hashlib, io, json, sys, tarfile
from datetime import datetime, timezone
from pathlib import Path

from v7.experiments.information_controls import (INFO_SEEDS, MEMORY_SEEDS, PILOT_INFO_SEED, PILOT_MEMORY_SEED, TUTOR_ACCURACY,
    exact_benchmark, information_rows, memory_rows)

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "v7/evidence/information_controls"
OUTPUT = ROOT / "v7/experiments/output/information_controls"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_csv(path: Path, rows: list[dict]) -> None:
    columns = sorted({key for row in rows for key in row}); buf = io.StringIO(); writer = csv.DictWriter(buf, fieldnames=columns); writer.writeheader()
    for row in rows: writer.writerow({key: json.dumps(value, sort_keys=True) if isinstance(value, (dict, list, tuple)) else value for key, value in row.items()})
    path.write_bytes(gzip.compress(buf.getvalue().encode(), mtime=0))


def registration() -> dict:
    files = [Path(__file__), ROOT / "v7/experiments/information_controls.py", ROOT / "v7/tests/test_information_controls.py"]
    return {"stage": "R4 information authority provenance and memory acceptance controls", "attempt_id": "attempt_003_clean_confirmation", "status": "registered_before_outcomes",
            "information_seeds": list(INFO_SEEDS), "memory_seeds": list(MEMORY_SEEDS), "fixed_cap": 24,
            "private_accuracy": .8, "tutor_private_observations": 3, "tutor_majority_accuracy": TUTOR_ACCURACY,
            "information_factorial": ["independent/copied true root", "visible/hidden provenance", "peer/authority uninformative label", "three inherited policies"],
            "memory_factorial": ["memory_acceptance=0/1", "juvenile_d=0/.5", "40 fixed-proposition training episodes", "20 adult reuse episodes"],
            "hidden_provenance": "exact .5 prior mixture of independent and copied generating structures; never automatic independence",
            "claim_limit": "Mechanism-positive-control cognitive assays only: no demographic, selection, historical-adaptation, or novelty claim. Equal-information optimum cannot be beaten by extra override in expected payoff.",
            "source_sha256": {str(path.relative_to(ROOT)): sha(path) for path in files}}


def freeze(config: dict) -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True); OUTPUT.mkdir(parents=True, exist_ok=True)
    reg = EVIDENCE / "registration.json"
    if reg.exists():
        old = json.loads(reg.read_text()); assert old["config"] == config, "registered config/source differs"
        return
    dump(reg, {"registered_at": datetime.now(timezone.utc).isoformat(), "python": sys.version, "config": config})
    with tarfile.open(EVIDENCE / "source.tar.gz", "w:gz") as archive:
        for relative in config["source_sha256"]:
            path = ROOT / relative; info = archive.gettarinfo(str(path), arcname=relative); info.mtime = 0; info.uid = info.gid = 0; info.uname = info.gname = ""
            with path.open("rb") as handle: archive.addfile(info, handle)


def gates(info: list[dict], memory: list[dict], exact: dict) -> dict:
    tutors = [r for r in info if r["assay"] == "tutor_acquisition"]
    children = [r for r in info if r["assay"] == "authority_provenance_child"]
    training = [r for r in memory if r["assay"] == "memory_training"]
    adults = [r for r in memory if r["assay"] == "adult_memory_reuse"]
    sensitive = [r for r in children if r["policy"] == "authority_sensitive"]
    # The gate is policy-mechanism identification, not a one-seed realised-rate
    # claim: common draws can legitimately yield zero pilot overrides.
    label_effect = bool(sensitive) and all(r["override_probability"] == (.5 if r["role_label"] == "authority" else 0.0) for r in sensitive)
    neutral_zero = all(not r["override"] for r in children if r["policy"] == "label_neutral_d0")
    tutor_observations = [x for r in tutors for x in r["private_evidence_history"]]
    return {"all_blank_tutors": all(r["initial_belief_blank"] for r in tutors), "paid_tutor_training": all(r["paid_training_cost"] == .3 for r in tutors),
            "empirical_tutor_private_accuracy": sum(x == r["truth"] for r in tutors for x in r["private_evidence_history"]) / len(tutor_observations),
            "real_independent_and_shared_roots": all(len(set(r["public_message_roots"])) == (2 if r["provenance_structure"] == "independent" else 1) for r in children),
            "hidden_is_explicit_mixture": all(r["hidden_structure_prior_independent"] == .5 for r in children if not r["provenance_visible"]),
            "exact_q_tutor": exact["q_tutor_enumerated"] == exact["q_tutor_formula"] == TUTOR_ACCURACY,
            "copy_duplicate_invariance": exact["visible_copy_duplicate_invariant"], "authority_positive_control_label_effect": label_effect,
            "neutral_d0_no_override": neutral_zero, "all_memory_blank": all(r["episode"] == 0 and r["B_before"] == .5 and r["K_before"] == 0 for r in training if r["episode"] == 0),
            "memory_crossed": len({(r["memory_acceptance"], r["juvenile_d"]) for r in training}) == 4,
            "adult_actual_twenty_steps": all(sum(1 for r in adults if r["seed"] == seed and r["memory_acceptance"] == memory_acceptance and r["juvenile_d"] == d) == 20 for seed, memory_acceptance, d in {(r["seed"], r["memory_acceptance"], r["juvenile_d"]) for r in adults}),
            "adult_direct_override_zero": all(r["direct_adult_inherited_override"] == 0.0 for r in adults),
            "adult_memory_reuse_separate": all(r["stored_memory_reused"] == bool(r["memory_acceptance"]) for r in adults),
            "same_receipt_cost": all(r["receipt_cost"] == .1 for r in training + adults),
            "all_gates_pass": False}


def main() -> None:
    config = registration(); freeze(config)  # source/config/archive before any fresh output
    # A fixed one-block pilot executes after the registration/archive, and its
    # gates are recorded before the independent 24-block confirmation below.
    pilot_exact = exact_benchmark()
    pilot_info = information_rows(PILOT_INFO_SEED); pilot_memory = memory_rows(PILOT_MEMORY_SEED)
    pilot_gates = gates(pilot_info, pilot_memory, pilot_exact)
    pilot_gates["all_gates_pass"] = all(value for key, value in pilot_gates.items() if key not in {"all_gates_pass", "empirical_tutor_private_accuracy"})
    assert pilot_gates["all_gates_pass"], pilot_gates
    dump(EVIDENCE / "pilot_summary.json", {"status": "passed_before_confirmation", "information_seed": PILOT_INFO_SEED,
                                             "memory_seed": PILOT_MEMORY_SEED, "gates": pilot_gates})
    exact = exact_benchmark(); info = [row for seed in INFO_SEEDS for row in information_rows(seed)]; memory = [row for seed in MEMORY_SEEDS for row in memory_rows(seed)]
    result_gates = gates(info, memory, exact); result_gates["all_gates_pass"] = all(value for key, value in result_gates.items() if key not in {"all_gates_pass", "empirical_tutor_private_accuracy"})
    assert result_gates["all_gates_pass"], result_gates
    write_csv(OUTPUT / "authority_provenance_raw.csv.gz", info); write_csv(OUTPUT / "memory_acceptance_raw.csv.gz", memory); dump(OUTPUT / "exact_enumeration.json", exact)
    child_rows = [row for row in info if row["assay"] == "authority_provenance_child"]
    conflict_rows = [row for row in child_rows if row["conflict"]]
    summary = {"status": "complete", "information_rows": len(info), "memory_rows": len(memory), "independent_seed_blocks": 24,
               "pilot": {"information_seed": PILOT_INFO_SEED, "memory_seed": PILOT_MEMORY_SEED, "gates_passed_before_confirmation": pilot_gates["all_gates_pass"]},
               "authority_counts": {"unconditional_rows": len(child_rows), "conflict_rows": len(conflict_rows),
                                    "by_policy_role": {f"{policy}:{role}": sum(1 for row in child_rows if row["policy"] == policy and row["role_label"] == role)
                                                       for policy in ("label_neutral_d0", "generic_source_dhalf", "authority_sensitive") for role in ("peer", "authority")}},
               "gates": result_gates, "exact": {k: v for k, v in exact.items() if k != "histories"},
               "raw_sha256": {str(p.relative_to(ROOT)): sha(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()},
               "claim_limit": config["claim_limit"], "optimal_baseline_consequence": "With equal information and utility, an extra override cannot improve expected payoff over the optimal policy; observed override loss/null is a mathematical dominance consequence, not novelty."}
    dump(EVIDENCE / "summary.json", summary); dump(EVIDENCE / "gates.json", result_gates); print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__": main()
