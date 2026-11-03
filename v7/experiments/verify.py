"""Fail-closed verifier of measured V7 kernel evidence, not status booleans alone."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KERNEL_REQUIRED = {"AUTH-01", "AUTH-02", "AUTH-03", "HIDDEN-01", "RNG-01", "PROV-01", "BUDGET-01", "INHERIT-01", "FOUNDER-01", "MATURITY-01", "COMP-01", "TASK-01", "CLASS-01"}
ECOLOGY_REQUIRED = {"TASK-01", "LEDGER-01", "TEACH-01", "GROWTH-01", "CAP-01", "REPLAY-01", "NEUTRAL-VIABILITY-01"}

def _fail(message: str) -> None: raise SystemExit(message)
def _sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()

def verify_kernel(predeclared: Path, executed: Path) -> None:
    declared = {entry["id"] for entry in json.loads(predeclared.read_text())["checks"]}
    if KERNEL_REQUIRED - declared: _fail(f"predeclared checks missing: {sorted(KERNEL_REQUIRED-declared)}")
    evidence = json.loads(executed.read_text())
    if evidence.get("stage") != "kernel" or evidence.get("status") != "passed": _fail("kernel execution evidence is absent or failed")
    failed = [name for name in KERNEL_REQUIRED if evidence.get("checks", {}).get(name, {}).get("status") != "passed"]
    if failed: _fail(f"kernel blockers not passed: {failed}")
    output_path = ROOT / "experiments/output/kernel.json"
    if not output_path.is_file(): _fail("measured kernel output is absent")
    record = json.loads(output_path.read_text())
    if record.get("stage") != "kernel" or not all(record.get("checks", {}).get(name) is True for name in KERNEL_REQUIRED): _fail("measured kernel checks failed")
    # Bind the evidence to actual, current sources so copied status JSON cannot certify another kernel.
    for relative, digest in record.get("source_sha256", {}).items():
        path = ROOT / relative
        if not path.is_file() or _sha(path) != digest: _fail(f"source hash mismatch: {relative}")
    factorial = record.get("factorial_content_memory_override", [])
    if len(factorial) != 8 or len({(x["content"], x["accept_memory"], x["override"]) for x in factorial}) != 8: _fail("content/memory/override factorial is incomplete")
    placebo = record.get("authority_label_placebo", {})
    if placebo.get("senior", {}).get("q0_values") != placebo.get("novice", {}).get("q0_values"): _fail("authority-label placebo changed a label-neutral Q0")
    provenance = record.get("provenance_duplicate", {})
    if abs(provenance.get("baseline_posterior", -1) - provenance.get("duplicated_posterior", 1)) > 1e-12: _fail("same-root testimony was double counted")
    if len({row.get("digest") for row in record.get("hidden_history_permutation", [])}) != 1: _fail("hidden-history permutation affected policy output")
    decisions = record.get("decisions", {})
    if not decisions or any(item.get("operation_count", 10**9) > 6 for item in decisions.values()): _fail("common operation cap is not evidenced")
    exact = record.get("exact", {})
    if not (exact.get("upper_bound_holds") and exact.get("exact_value", -1e9) + 2*exact.get("mcse", 1e9) >= exact.get("independent_restricted_value", 1e9)): _fail("Bellman upper bound or independent simulation failed")
    if exact.get("restricted_replicates", 0) < 1000 or exact.get("exact_first_action") not in {"learn", "query", "verify", "safe", "execute_0", "execute_1"}: _fail("tiny-world enumeration is not sufficiently evidenced")
    economics = record.get("task_economics", [])
    if {row.get("depth") for row in economics} != {1, 3, 6}: _fail("depth economics incomplete")
    for row in economics:
        names = {branch[0] for branch in row.get("failure_branches", [])}
        if "incorrect_finish" not in names or not any(name.startswith("prefix_failure_") for name in names): _fail("economics omitted a failure branch")
        if row.get("safe_return") != (row["depth"] + 1) * 1.2: _fail("same-token safe comparison is wrong")
    if not record.get("pending_for_slice_2a"): _fail("pending acquisition/ledger scope is not disclosed")


def verify_ecology_gates(predeclared: Path, manifest: Path, executed: Path) -> None:
    declared = {entry["id"] for entry in json.loads(predeclared.read_text())["checks"]}
    if {"TASK-01", "LEDGER-01", "TEACH-01", "GROWTH-01"} - declared: _fail("predeclared ecology blockers are absent")
    if not manifest.is_file() or not executed.is_file(): _fail("ecology manifest or executed evidence is absent")
    run, evidence = json.loads(manifest.read_text()), json.loads(executed.read_text())
    if run.get("stage") != "ecology-gates" or evidence.get("stage") != "ecology-gates" or run.get("status") != "passed" or evidence.get("status") != "passed": _fail("ecology gates have not passed")
    failed = [name for name in ECOLOGY_REQUIRED if evidence.get("checks", {}).get(name, {}).get("status") != "passed"]
    if failed: _fail(f"ecology blockers not passed: {failed}")
    if run.get("substantive_discovery") is not False: _fail("Slice 2A manifest incorrectly contains substantive discovery")
    for relative, digest in run.get("source_sha256", {}).items():
        path = ROOT / relative
        if not path.is_file() or _sha(path) != digest: _fail(f"ecology source hash mismatch: {relative}")
    horizons, caps = run.get("horizons", {}), run.get("caps", {})
    if horizons != {"burn_in": 60, "measurement": 180} or caps.get("population") != 512 or caps.get("events") != 1_500_000 or caps.get("wall_seconds") != 120: _fail("frozen ecology horizons/caps are wrong")
    sentinels = run.get("sentinels", [])
    if len(sentinels) != 2 or {row.get("policy") for row in sentinels} != {"ordinary_social", "asocial_access_off"}: _fail("ordinary/asocial validity sentinels are incomplete")
    for row in sentinels:
        if row.get("seasons_completed") != 240 or row.get("status") != "running" or row.get("population", 0) <= 0: _fail("neutral viability sentinel did not complete")
        if not row.get("population_identity_holds") or row.get("max_seasonal_ledger_residual", 1) > 1e-8: _fail("population/energy ledger did not close")
        if row.get("events", 10**12) >= caps["events"] or row.get("max_population", 10**12) > caps["population"] or row.get("decision_records", 10**12) > caps["decision_records"] or row.get("max_time_tokens_used", 10**12) > 12: _fail("a frozen resource/storage/time cap was exceeded")
    ordinary = next(row for row in sentinels if row["policy"] == "ordinary_social")
    asocial = next(row for row in sentinels if row["policy"] == "asocial_access_off")
    if ordinary.get("cultural_edges", 0) <= 0 or ordinary.get("teacher_time", 0) <= 0 or asocial.get("cultural_edges") != 0: _fail("teaching/access-off gate is not evidenced")
    if ordinary.get("replay_digest") != run.get("replay_digest"): _fail("fixed replay digest is not reproducible")
    economics = json.loads((ROOT / "experiments/output/kernel.json").read_text()).get("task_economics", [])
    if {row.get("depth") for row in economics} != {1, 3, 6} or any(row.get("margin_per_token", -1) < .1 for row in economics): _fail("a primary-depth task lacks the predeclared margin")
    parity = run.get("task_kernel_parity", {})
    if parity.get("trials", 0) < 4096 or parity.get("max_absolute_error", 1.) >= .025: _fail("IBM/exact shared D-step kernel parity is absent or failed")

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--stage", required=True, choices=("kernel", "ecology-gates")); parser.add_argument("--predeclared", required=True, type=Path); parser.add_argument("--executed", required=True, type=Path); parser.add_argument("--manifest", type=Path); args = parser.parse_args()
    if args.stage == "kernel":
        verify_kernel(args.predeclared, args.executed); print("kernel verification: PASS (measured evidence)")
    else:
        if args.manifest is None: _fail("--manifest is required for ecology-gates")
        verify_ecology_gates(args.predeclared, args.manifest, args.executed); print("ecology-gates verification: PASS (measured validity sentinels)")
if __name__ == "__main__": main()
