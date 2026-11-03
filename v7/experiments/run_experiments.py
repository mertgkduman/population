"""Kernel evidence runner.  It writes measurements, not a predeclared-pass fixture."""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import os
import sys
import tarfile
import tempfile
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, stdev

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path: sys.path.insert(0, str(REPOSITORY_ROOT))

from v7.experiments.exact import ExactTinyPOMDP, compare_restricted_override, enumerate_task, sample_task_outcome, simulate_restricted_override, task_economics_table
from v7.experiments.model import (AcquiredState, AsocialPolicy, CandidateBPolicy, EcologyRun, FeatureTrustPolicy,
    IndividualKernelState, KeyedRNG, OrdinarySocialPolicy, PolicyObservation, RewardPredictor,
    VectorOverridePolicy, observable_reward_features, posterior_advice_probability, select_observable_teacher,
    store_procedure, update_beliefs, update_trust, validate_policy_observation)

ROOT = Path(__file__).resolve().parents[1]
def _sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json_atomic(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def _with(observation: PolicyObservation, **change: object) -> PolicyObservation:
    return PolicyObservation(**{**observation.__dict__, **change})


def _trained_predictor() -> RewardPredictor:
    # Fixed kernel fixture, not an ecology training pass.  Discovery comparators
    # start blank and may only learn through their own paid incremental LMS events.
    return RewardPredictor((("bias", .05), ("calibrated_source", .55), ("context_match", .20), ("unique_roots", .04)))


def kernel_tracer(config: Path) -> dict:
    observation = PolicyObservation.contract_fixture(conflict=True, age=3)
    predictor = _trained_predictor()
    ordinary = OrdinarySocialPolicy().decide(observation, 6, KeyedRNG.fixture("kernel-tracer"))
    forced = VectorOverridePolicy(1., 0.).decide(observation, 6, KeyedRNG.fixture("kernel-tracer"))
    asocial = AsocialPolicy().decide(observation, 6, KeyedRNG.fixture("kernel-tracer"))
    feature = FeatureTrustPolicy(predictor).decide(observation, 6, KeyedRNG.fixture("feature"))
    candidate = CandidateBPolicy(predictor).decide(observation, 6, KeyedRNG.fixture("candidate"))

    # 2x2x2: content exposure, memory acceptance (explicit K update), behavioural override.
    factorial = []
    for content in (False, True):
        for accept_memory in (False, True):
            for override in (False, True):
                state = AcquiredState.blank()
                if content and accept_memory: state = store_procedure(state, "learned-sequence", "root-a")
                decision = VectorOverridePolicy(1. if override else 0., 0.).decide(observation if content else _with(observation, messages=(), provenance_roots=(), advice=None, source_id=None, source_history=()), 6, KeyedRNG.fixture(f"factor-{content}-{accept_memory}-{override}"))
                factorial.append({"content": content, "accept_memory": accept_memory, "override": override,
                                  "beliefs": state.beliefs, "procedures": state.procedures,
                                  "action": decision.chosen_action, "override_applied": decision.override_applied})

    # Label is observable but is not a predictor feature, likelihood, or policy parameter.
    label_a = _with(observation, messages=(("authority_label", "senior"), ("demonstration", "teacher")))
    label_b = _with(observation, messages=(("authority_label", "novice"), ("demonstration", "teacher")))
    placebo_a = FeatureTrustPolicy(predictor).decide(label_a, 6, KeyedRNG.fixture("placebo"))
    placebo_b = FeatureTrustPolicy(predictor).decide(label_b, 6, KeyedRNG.fixture("placebo"))
    duplicate = _with(observation, messages=(("demonstration", "teacher"), ("repeat", "teacher")), provenance_roots=("trial-root-1", "trial-root-1"))
    duplicated_posterior = posterior_advice_probability(duplicate)
    baseline_posterior = posterior_advice_probability(observation)
    history_permutation = [{"latent_theta": theta, "latent_z": z,
                            "digest": OrdinarySocialPolicy().decide(observation, 6, KeyedRNG.fixture("permuted-history")).pre_override_digest}
                           for theta in (0, 1) for z in (0, 1)]

    founder = IndividualKernelState.naive_founder("founder", {"d_procedure": 0., "d_local": 0.})
    newborn = founder.newborn("newborn")
    # Explicit evidence transitions are checked independently of decisions.
    updated_b = update_beliefs(AcquiredState.blank(), 4.)
    updated_t = update_trust(AcquiredState.blank(), "tutor", True)
    exact = compare_restricted_override(4000)
    restricted_value, restricted_mcse, visits = simulate_restricted_override(4000)
    oracle = ExactTinyPOMDP(); exact_value, first_action = oracle.solve()
    economics = task_economics_table()
    policies = {"ordinary": ordinary, "forced": forced, "asocial": asocial, "feature": feature, "candidate_b": candidate}
    checks = {
        "AUTH-01": ordinary.social_content_used and not ordinary.override_applied and ordinary.posterior_advice != asocial.posterior_advice,
        "AUTH-02": forced.post_override_learning_digest == forced.pre_override_learning_digest,
        "AUTH-03": len({(row["content"], row["accept_memory"], row["override"], tuple(row["procedures"]), row["action"]) for row in factorial}) >= 4,
        "HIDDEN-01": len({row["digest"] for row in history_permutation}) == 1,
        "RNG-01": KeyedRNG.fixture("stable").draw("override", entity=7, ordinal=2) == KeyedRNG.fixture("stable").draw("override", entity=7, ordinal=2),
        "PROV-01": abs(duplicated_posterior - baseline_posterior) < 1e-12,
        "BUDGET-01": all(d.operation_count <= 6 and d.operation_count <= observation.computation_budget for d in policies.values()),
        "INHERIT-01": newborn.acquired == AcquiredState.blank() and newborn.policy_traits == founder.policy_traits,
        "FOUNDER-01": founder.acquired == AcquiredState.blank() and select_observable_teacher((founder,)) is None,
        "MATURITY-01": VectorOverridePolicy(1., 1.).decide(PolicyObservation.contract_fixture(True, 5), 6, KeyedRNG.fixture("adult")).chosen_action != "teacher",
        "COMP-01": exact.upper_bound_holds and abs(restricted_value - exact.restricted_value) < 1e-12 and exact_value == exact.exact_value,
        "TASK-01": all(row.failure_branches and row.procedure_return > 0 and row.margin_per_token >= .10 for row in economics),
        "CLASS-01": validate_policy_observation(observation) == observation,
    }
    return {"stage": "kernel", "config_sha256": _sha(config),
            "source_sha256": {str(p.relative_to(ROOT)): _sha(p) for p in [ROOT / "experiments/model.py", ROOT / "experiments/exact.py", Path(__file__), Path(__file__).with_name("verify.py")]},
            "decisions": {name: d.__dict__ for name, d in policies.items()},
            "factorial_content_memory_override": factorial,
            "authority_label_placebo": {"senior": placebo_a.__dict__, "novice": placebo_b.__dict__, "features": predictor.features, "weights": predictor.weights},
            "provenance_duplicate": {"baseline_posterior": baseline_posterior, "duplicated_posterior": duplicated_posterior, "unique_roots": 1},
            "hidden_history_permutation": history_permutation,
            "explicit_state_updates": {"B": updated_b.__dict__, "T": updated_t.__dict__, "K": store_procedure(AcquiredState.blank(), "p", "r").__dict__},
            "exact": {**exact.__dict__, "independent_restricted_value": restricted_value, "independent_restricted_mcse": restricted_mcse, "restricted_visits": visits, "scope": "Matched two-episode tiny-world information, utility, time, and operation contract only; no full-IBM upper-bound claim."},
            "task_economics": [row.__dict__ for row in economics], "checks": checks,
            "pending_for_slice_2a": ["Teacher acquisition, query, and production transfers have posted kernel prices but their population ledger entries and paid event implementations are intentionally pending Slice 2A.", "The kernel establishes no ecology, demography, selection, accumulation, or founder-acquisition result."],
            "interface": {"stable": ["PolicyObservation", "PolicyDecision", "WorldState", "KeyedRNG", "update_beliefs", "update_trust", "store_procedure", "TaskEconomics"], "operation_cap": 6, "tiny_world": "two episode theta/z posterior Bellman model"}}


def run_kernel(config: Path) -> dict:
    record = kernel_tracer(config); output, evidence, handoffs = ROOT / "experiments/output", ROOT / "evidence", ROOT / "evidence/handoffs"
    output.mkdir(parents=True, exist_ok=True); handoffs.mkdir(parents=True, exist_ok=True)
    (output / "kernel.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    status = "passed" if all(record["checks"].values()) else "failed"
    executed = {"stage": "kernel", "status": status, "source_sha256": record["source_sha256"], "config_sha256": record["config_sha256"], "checks": {key: {"status": "passed" if value else "failed", "evidence": "v7/experiments/output/kernel.json"} for key, value in record["checks"].items()}, "pending": record["pending_for_slice_2a"]}
    (evidence / "executed_checks.json").write_text(json.dumps(executed, indent=2, sort_keys=True) + "\n")
    handoff = {"slice": "1B-kernel-exact", "status": status, "claim_scope": "Measured kernel-contract checks only. The exact upper bound is limited to the matched two-episode tiny world; it is not an IBM, ecology, demography, selection, or cultural-accumulation result.", "predecessor": "v7/evidence/handoffs/01-wave0.json", "kernel_output_sha256": _sha(output / "kernel.json"), "executed_checks_sha256": _sha(evidence / "executed_checks.json"), "source_sha256": record["source_sha256"], "config_sha256": record["config_sha256"], "checks": executed["checks"], "pending_for_slice_2a": record["pending_for_slice_2a"], "next_interface": "Slice 2A must use the stable policy/update/task interfaces, charge all acquisition/production transfers in a linked ledger, and must not infer any ecology gate from this kernel evidence."}
    (handoffs / "02-kernel.json").write_text(json.dumps(handoff, indent=2, sort_keys=True) + "\n")
    return record


def _validate_kernel_predecessor() -> dict:
    """Validate immutable predecessor *artifacts*, whose source snapshot predates 2A.

    Slice 2A intentionally extends model.py, so calling the current-source kernel
    verifier after that edit would mistake legitimate successor work for a bad
    predecessor.  The handoff binds the old source digest and the two measured files;
    this function verifies those exact artifacts without asserting the successor has
    old source bytes.
    """
    handoff = ROOT / "evidence/handoffs/02-kernel.json"
    kernel = ROOT / "experiments/output/kernel.json"
    executed = ROOT / "evidence/executed_checks.json"
    if not all(path.is_file() for path in (handoff, kernel, executed)):
        raise RuntimeError("Slice 2A requires the complete 02-kernel handoff and measured evidence")
    record, current_checks = json.loads(handoff.read_text()), json.loads(executed.read_text())
    # Slice evidence replaces executed_checks.json at each stage, but preserves the
    # full previous document verbatim. Reconstitute its canonical prior bytes for a
    # repeatable handoff check on re-run.
    checks = current_checks
    while checks.get("stage") != "kernel" and isinstance(checks.get("predecessor_kernel"), dict):
        checks = checks["predecessor_kernel"]
    checks_sha = hashlib.sha256((json.dumps(checks, indent=2, sort_keys=True) + "\n").encode()).hexdigest()
    if record.get("status") != "passed" or record.get("kernel_output_sha256") != _sha(kernel) or record.get("executed_checks_sha256") != checks_sha:
        raise RuntimeError("kernel predecessor handoff hashes/status do not match measured artifacts")
    required = {"AUTH-01", "AUTH-02", "AUTH-03", "HIDDEN-01", "RNG-01", "PROV-01", "BUDGET-01", "INHERIT-01", "FOUNDER-01", "MATURITY-01", "COMP-01", "TASK-01", "CLASS-01"}
    if checks.get("stage") != "kernel" or any(checks.get("checks", {}).get(name, {}).get("status") != "passed" for name in required):
        raise RuntimeError("kernel predecessor did not pass every pre-ecology blocker")
    return {"handoff": str(handoff.relative_to(ROOT.parent)), "handoff_sha256": _sha(handoff),
            "kernel_output_sha256": _sha(kernel), "executed_checks_sha256": checks_sha,
            "predecessor_source_sha256": record.get("source_sha256", {})}


def ecology_gates(config: Path) -> dict:
    predecessor = _validate_kernel_predecessor()
    # These are only ordinary/asocial validity sentinels.  They do not enumerate a
    # policy grid, tune a policy, write discovery cells, or make an ecological claim.
    sentinels: list[dict] = []
    for policy_name, policy in (("ordinary_social", OrdinarySocialPolicy), ("asocial_access_off", AsocialPolicy)):
        run = EcologyRun(71001, policy, depth=3, chi=.75, q_theta=.005, label=policy_name)
        summary = run.run()
        summary["max_population"] = max(report.population_next for report in run.reports)
        summary["min_population"] = min(report.population_next for report in run.reports)
        summary["population_identity_holds"] = all(report.population_next == report.population_prior + report.births - report.deaths for report in run.reports)
        summary["max_seasonal_ledger_residual"] = max(abs(report.energy_resource_residual) for report in run.reports)
        sentinels.append(summary)
    replay_a = EcologyRun(71001, OrdinarySocialPolicy, depth=3, chi=.75, q_theta=.005, label="ordinary_social").run()
    economics = [row.__dict__ for row in task_economics_table()]
    # Independent keyed draws through the exact shared D-step kernel.  This is a
    # contract/parity diagnostic, not a policy discovery experiment.
    expected = dict((name, probability) for name, probability, _value in enumerate_task(3, .9).failure_branches)
    observed: dict[str, int] = {name: 0 for name in expected}
    for replicate in range(4096):
        rng = KeyedRNG("task-parity", "D3", 0)
        terminal, _reached, _value = sample_task_outcome(3, .9, lambda step, r=replicate: rng.draw("task_outcome", entity=r, ordinal=step, event_type="parity"))
        observed[terminal] += 1
    empirical = {name: count / 4096 for name, count in observed.items()}
    parity = {"depth": 3, "trials": 4096, "expected": expected, "empirical": empirical,
              "max_absolute_error": max(abs(empirical[name] - expected[name]) for name in expected)}
    ordinary, asocial = sentinels
    checks = {
        "TASK-01": all(row["procedure_return"] > 0 and row["safe_return"] == (row["depth"] + 1) * 1.2 and row["failure_branches"] and row["margin_per_token"] >= .10 for row in economics) and parity["max_absolute_error"] < .025,
        "LEDGER-01": all(row["population_identity_holds"] and row["max_seasonal_ledger_residual"] <= 1e-8 for row in sentinels),
        "TEACH-01": ordinary["teacher_time"] > 0 and ordinary["learner_time"] > 0 and ordinary["cultural_edges"] > 0 and asocial["cultural_edges"] == 0,
        "GROWTH-01": all(row["status"] == "running" and row["population"] > 0 and row["biological_edges"] > 0 and row["max_population"] != 64 for row in sentinels),
        "CAP-01": all(row["seasons_completed"] == 240 and row["events"] < EcologyRun.EVENT_CAP and row["decision_records"] <= 10_000 and row["max_population"] <= EcologyRun.POPULATION_CAP and row["max_time_tokens_used"] <= 12 for row in sentinels),
        "REPLAY-01": ordinary["replay_digest"] == replay_a["replay_digest"],
        "NEUTRAL-VIABILITY-01": ordinary["status"] == "running" and asocial["status"] == "running" and ordinary["population"] > 0 and asocial["population"] > 0,
    }
    source_paths = [ROOT / "experiments/model.py", ROOT / "experiments/exact.py", Path(__file__), Path(__file__).with_name("verify.py"), ROOT / "tests/test_ecology.py"]
    return {"stage": "ecology-gates", "status": "passed" if all(checks.values()) else "failed",
            "substantive_discovery": False, "predecessor": predecessor, "config_sha256": _sha(config),
            "source_sha256": {str(path.relative_to(ROOT)): _sha(path) for path in source_paths},
            "task_economics": economics, "task_kernel_parity": parity, "sentinels": sentinels, "replay": replay_a,
            "checks": checks, "unresolved": ["Discovery, holdout, candidate tuning, selection, and post-freeze work are intentionally unrun in Slice 2A."],
            "next_preconditions": ["All ecology-gates checks must remain passed against these source/config hashes.", "Slice 2B may tune only declared neutral-viability/task-adequacy and comparator approximation parameters on discovery seeds."]}


def run_ecology_gates(config: Path) -> dict:
    record = ecology_gates(config)
    output, evidence, handoffs = ROOT / "experiments/output", ROOT / "evidence", ROOT / "evidence/handoffs"
    manifest = {"stage": "ecology-gates", "status": record["status"], "substantive_discovery": False,
                "horizons": {"burn_in": 60, "measurement": 180},
                "caps": {"population": 512, "events": 1_500_000, "wall_seconds": 120, "decision_records": 10_000},
                "sentinels": record["sentinels"], "task_kernel_parity": record["task_kernel_parity"], "replay_digest": record["replay"]["replay_digest"],
                "source_sha256": record["source_sha256"], "config_sha256": record["config_sha256"]}
    _write_json_atomic(output / "run_manifest.json", manifest)
    previous = json.loads((evidence / "executed_checks.json").read_text())
    while previous.get("stage") != "kernel" and isinstance(previous.get("predecessor_kernel"), dict):
        previous = previous["predecessor_kernel"]
    executed = {"stage": "ecology-gates", "status": record["status"], "predecessor_kernel": previous,
                "source_sha256": record["source_sha256"], "config_sha256": record["config_sha256"],
                "checks": {name: {"status": "passed" if passed else "failed", "evidence": "v7/experiments/output/run_manifest.json"} for name, passed in record["checks"].items()},
                "unresolved": record["unresolved"]}
    _write_json_atomic(evidence / "executed_checks.json", executed)
    handoff = {"slice": "2A-ecology-validity", "status": record["status"], "claim_scope": "Validity sentinels only; no policy-grid discovery, holdout, selection, or persistence result was launched.",
               "predecessor": record["predecessor"], "manifest_sha256": _sha(output / "run_manifest.json"),
               "executed_checks_sha256": _sha(evidence / "executed_checks.json"), "source_sha256": record["source_sha256"],
               "config_sha256": record["config_sha256"], "checks": executed["checks"], "cap_usage": {"launched_trajectories": 3, "trajectory_cap": 12000, "workers": 1, "wall_hours": 0.01},
               "unresolved": record["unresolved"], "next_preconditions": record["next_preconditions"]}
    _write_json_atomic(handoffs / "03-ecology-gates.json", handoff)
    if record["status"] != "passed": raise SystemExit("ecology validity gates failed; substantive discovery remains blocked")
    return record


# Slice 2B.  These functions deliberately retain every terminal status in the raw
# CSV: an extinction/cap is a result row, never a dropped failed job.
L9_ROWS = ((1, 1, 1, 1), (1, 2, 2, 2), (1, 3, 3, 3), (2, 1, 2, 3), (2, 2, 3, 1), (2, 3, 1, 2), (3, 1, 3, 2), (3, 2, 1, 3), (3, 3, 2, 1))
LEVELS = {"depth": (1, 3, 6), "verification_price": (.1, .5, 1.5), "chi": (.5, .75, 1.), "q_theta": (0., .005, .02)}
POLICIES = ("vector_0_0", "vector_0_0_5", "vector_0_1", "vector_0_5_0", "vector_0_5_0_5", "vector_0_5_1", "vector_1_0", "vector_1_0_5", "vector_1_1", "scalar_0_25", "scalar_0_75", "asocial_access_off", "feature_trust", "candidate_b_resource_rational")


def _regime(index: int) -> dict:
    d, cost, chi, volatility = L9_ROWS[index]
    return {"regime": index + 1, "depth": LEVELS["depth"][d - 1], "verification_price": LEVELS["verification_price"][cost - 1], "chi": LEVELS["chi"][chi - 1], "q_theta": LEVELS["q_theta"][volatility - 1]}


def _policy_spec(name: str) -> tuple[object, dict[str, float]]:
    vectors = {"vector_0_0": (0., 0.), "vector_0_0_5": (0., .5), "vector_0_1": (0., 1.), "vector_0_5_0": (.5, 0.), "vector_0_5_0_5": (.5, .5), "vector_0_5_1": (.5, 1.), "vector_1_0": (1., 0.), "vector_1_0_5": (1., .5), "vector_1_1": (1., 1.)}
    if name in vectors:
        a, b = vectors[name]; return VectorOverridePolicy, {"d_procedure": a, "d_local": b}
    if name == "scalar_0_25": return VectorOverridePolicy, {"d_procedure": .25, "d_local": .25}
    if name == "scalar_0_75": return VectorOverridePolicy, {"d_procedure": .75, "d_local": .75}
    if name == "asocial_access_off": return AsocialPolicy, {"d_procedure": 0., "d_local": 0.}
    if name == "feature_trust": return FeatureTrustPolicy, {"d_procedure": 0., "d_local": 0.}
    if name == "candidate_b_resource_rational": return CandidateBPolicy, {"d_procedure": 0., "d_local": 0.}
    raise ValueError(f"unknown predeclared policy {name}")


def _run_cell(job: dict) -> dict:
    factory, traits = _policy_spec(job["policy"])
    run = EcologyRun(job["seed"], factory, depth=job["depth"], chi=job["chi"], q_theta=job["q_theta"], verification_price=job["verification_price"], graph_variant=job.get("graph_variant", 0), initial_traits=traits, label=job["policy"])
    result = run.run()
    result.update({key: value for key, value in job.items() if key not in result})
    # A compact, prespecified actual trace/genealogy subset is retained only for
    # registered representative jobs, never selected after seeing their outcomes.
    if job.get("retain_history"):
        result["representative"] = {"reports": [report.__dict__ for report in run.reports], "biological_edges": run.biological_edges, "cultural_edges": run.cultural_edges, "decision_events": list(run.decision_samples)}
    return result


def _write_csv_gz(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row if key != "representative"})
    with gzip.open(path, "wt", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader(); writer.writerows(rows)


def _run_registered(jobs: list[dict], workers: int) -> list[dict]:
    if workers < 1 or workers > 4: raise ValueError("worker count is frozen to 1..4")
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(_run_cell, jobs, chunksize=1))


def _source_hashes() -> dict[str, str]:
    paths = [ROOT / "experiments/model.py", ROOT / "experiments/exact.py", Path(__file__), ROOT / "experiments/verify.py", ROOT / "experiments/analyze_results.py", ROOT / "experiments/config.json", ROOT / "parameter_schema.json"]
    return {str(path.relative_to(ROOT)): _sha(path) for path in paths if path.is_file()}


def _write_manifest(value: dict) -> None: _write_json_atomic(ROOT / "experiments/output/run_manifest.json", value)


def pilot(config: Path) -> dict:
    """Bounded pre-batch runtime pilot for the two expensive comparator paths."""
    jobs = [{**_regime(4), "seed": 71001, "policy": policy, "stage": "pilot", "graph_variant": 0} for policy in ("feature_trust", "candidate_b_resource_rational")]
    started = datetime.now(timezone.utc).isoformat(); rows = _run_registered(jobs, 2)
    record = {"stage": "pilot", "status": "complete", "started_at": started, "source_sha256": _source_hashes(), "config_sha256": _sha(config), "workers": 2, "rows": [{key: value for key, value in row.items() if key != "representative"} for row in rows], "claim_scope": "Performance-only pilot; no discovery comparison or tuning result."}
    _write_json_atomic(ROOT / "experiments/output/pilot.json", record)
    return record


def discovery(config: Path, workers: int = 4) -> dict:
    if _sha(config) != _sha(ROOT / "experiments/config.json"): raise ValueError("discovery must use the frozen repository config")
    declared = json.loads(config.read_text())["discovery"]
    if tuple(declared["policies"]) != POLICIES or tuple(declared["verification_production_cost"]) != LEVELS["verification_price"] or tuple(map(tuple, declared["l9_rows"])) != L9_ROWS:
        raise ValueError("the registered L9 costs, policies, or rows diverge from the frozen config")
    jobs = [{**_regime(regime), "seed": seed, "policy": policy, "stage": "discovery", "graph_variant": 0,
             "retain_history": (regime * 4 + (seed - 71001)) < 24 and policy == "vector_0_0"}
            for regime in range(9) for policy in POLICIES for seed in range(71001, 71005)]
    manifest = {"stage": "discovery", "status": "registered", "registered_at": datetime.now(timezone.utc).isoformat(), "source_sha256": _source_hashes(), "config_sha256": _sha(config), "horizons": {"burn_in": 60, "measurement": 180}, "caps": {"workers": workers, "trajectories": 12000, "population": 512, "events": 1500000, "wall_seconds": 120, "raw_bytes": 256000000, "representative_histories": 24}, "discovery": {"seeds": list(range(71001, 71005)), "policies": list(POLICIES), "l9_rows": [list(row) for row in L9_ROWS], "cells": len(jobs), "interaction_note": "L9 main-effect screen; interactions are aliased."}, "jobs": jobs, "outcomes_read": False}
    _write_manifest(manifest)  # registration precedes every outcome.
    rows = _run_registered(jobs, workers)
    _write_csv_gz(ROOT / "experiments/output/discovery.csv.gz", rows)
    representatives = [row["representative"] | {"seed": row["seed"], "policy": row["policy"], "regime": row["regime"]} for row in rows if "representative" in row]
    with gzip.open(ROOT / "experiments/output/representative_trajectories.json.gz", "wt") as handle: json.dump(representatives, handle, sort_keys=True)
    manifest.update({"status": "complete", "outcomes_read": True, "completed_at": datetime.now(timezone.utc).isoformat(), "output_sha256": {"discovery.csv.gz": _sha(ROOT / "experiments/output/discovery.csv.gz"), "representative_trajectories.json.gz": _sha(ROOT / "experiments/output/representative_trajectories.json.gz")}, "terminal_counts": {status: sum(row["status"] == status for row in rows) for status in sorted({row["status"] for row in rows})}})
    _write_manifest(manifest)
    return manifest


def freeze_core(config: Path) -> dict:
    """Freeze the post-discovery executable core before any 72001+ outcome."""
    from v7.experiments.analyze_results import aggregate, read_rows
    discovery_path = ROOT / "experiments/output/discovery.csv.gz"
    if not discovery_path.is_file(): raise RuntimeError("cannot freeze before the registered discovery export exists")
    rows, aggregates = read_rows(discovery_path), None
    if len(rows) != 504 or {int(row["seed"]) for row in rows} != set(range(71001, 71005)): raise RuntimeError("discovery partition is incomplete")
    aggregates = aggregate(rows)
    # A transparent deterministic rule chooses up to two vectors by mean observed
    # net energy, and the fixed scalar bridge by its corresponding mean.
    by_policy: dict[str, list[float]] = {}
    for row in rows: by_policy.setdefault(row["policy"], []).append(float(row["net_energy_per_agent_season"]))
    vectors = sorted((name for name in by_policy if name.startswith("vector_")), key=lambda name: (-mean(by_policy[name]), name))[:2]
    scalar = max((name for name in by_policy if name.startswith("scalar_")), key=lambda name: (mean(by_policy[name]), name))
    core = [ROOT / "experiments/model.py", ROOT / "experiments/exact.py", Path(__file__), ROOT / "experiments/analyze_results.py", ROOT / "experiments/verify.py", ROOT / "experiments/config.json", ROOT / "parameter_schema.json"]
    freeze = ROOT / "evidence/core_freeze"; freeze.mkdir(parents=True, exist_ok=True)
    archive = freeze / "source.tar.gz"
    with tarfile.open(archive, "w:gz") as bundle:
        for path in core:
            info = bundle.gettarinfo(str(path), arcname=str(path.relative_to(ROOT)))
            info.mtime = 0; info.uid = info.gid = 0; info.uname = info.gname = ""
            with path.open("rb") as handle: bundle.addfile(info, handle)
    replay = _run_cell({**_regime(4), "seed": 71999, "policy": "vector_0_0", "stage": "freeze_replay", "graph_variant": 0})
    replay_record = {"seed": 71999, "policy": "vector_0_0", "regime": 5, "replay_digest": replay["replay_digest"], "source_sha256": _source_hashes()}
    _write_json_atomic(freeze / "replay.json", replay_record)
    manifest = {"stage": "core-freeze", "status": "frozen", "frozen_at": datetime.now(timezone.utc).isoformat(), "source_sha256": _source_hashes(), "config_sha256": _sha(config), "source_archive_sha256": _sha(archive), "discovery_sha256": _sha(discovery_path), "candidate_rule": "top two vector policies by discovery mean net_energy_per_agent_season; lexical tiebreak; best scalar by same rule", "frozen_vectors": vectors, "frozen_scalar": scalar, "comparators": ["vector_0_0", "feature_trust", "candidate_b_resource_rational", "asocial_access_off"], "primary_outcomes": ["net_energy_per_agent_season", "mean_population", "evidence_accuracy", "adult_stored_knowledge", "revision_rate", "override_rate", "cultural_action_accuracy", "extinction_inclusive_status"], "precision": {"net_energy_mcse": .1, "mean_population_mcse": 5., "proportion_wilson_half_width": .1, "maximum_seeds": 96, "batch": 8}, "replay": replay_record, "claim_limit": "Candidate B and Q0 are bounded approximations; ExactTinyPOMDP is a reduced matched benchmark, not full IBM optimal control."}
    _write_json_atomic(freeze / "manifest.json", manifest)
    _write_json_atomic(ROOT / "experiments/output/discovery_aggregates.json", {"aggregates": aggregates})
    return manifest


def confirmation(config: Path, workers: int = 4) -> dict:
    freeze = json.loads((ROOT / "evidence/core_freeze/manifest.json").read_text())
    if freeze.get("status") != "frozen" or freeze.get("config_sha256") != _sha(config): raise RuntimeError("holdout requires the immutable pre-outcome core freeze")
    policies = ["vector_0_0", "feature_trust", "candidate_b_resource_rational", freeze["frozen_scalar"], *freeze["frozen_vectors"]]
    policies = list(dict.fromkeys(policies))
    jobs = [{**_regime(regime), "seed": seed, "policy": policy, "stage": "holdout", "graph_variant": 1,
             "retain_history": len(policies) == 0} for regime in range(9) for policy in policies for seed in range(72001, 72025)]
    # Access-off is predeclared only for three sentinel regimes.
    jobs += [{**_regime(regime), "seed": seed, "policy": "asocial_access_off", "stage": "holdout_access_sentinel", "graph_variant": 1, "retain_history": False} for regime in (0, 4, 8) for seed in range(72001, 72025)]
    manifest = {"stage": "confirmation", "status": "registered", "registered_at": datetime.now(timezone.utc).isoformat(), "freeze_manifest_sha256": _sha(ROOT / "evidence/core_freeze/manifest.json"), "source_sha256": _source_hashes(), "config_sha256": _sha(config), "seeds": list(range(72001, 72025)), "graph_variant": 1, "policies": policies, "access_sentinel_regimes": [1, 5, 9], "jobs": len(jobs), "outcomes_read": False}
    _write_manifest(manifest)
    rows = _run_registered(jobs, workers)
    _write_csv_gz(ROOT / "experiments/output/holdout.csv.gz", rows)
    from v7.experiments.analyze_results import aggregate
    aggregates = aggregate(rows)
    _write_json_atomic(ROOT / "experiments/output/holdout_aggregates.json", {"aggregates": aggregates, "precision_rule": "At 24 seeds, any target not met is UNRESOLVED pending only predeclared fixed batches of eight; no effect sign/rank/p-value can select extension."})
    manifest.update({"status": "complete", "outcomes_read": True, "completed_at": datetime.now(timezone.utc).isoformat(), "output_sha256": {"holdout.csv.gz": _sha(ROOT / "experiments/output/holdout.csv.gz")}, "unresolved": "Precision-extension scheduler not yet run; all contrasts are explicitly provisional at 24 seeds."})
    _write_manifest(manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--stage", required=True, choices=("kernel", "ecology-gates", "pilot", "discovery", "freeze", "confirmation")); parser.add_argument("--config", required=True, type=Path); parser.add_argument("--workers", type=int, default=4); args = parser.parse_args()
    if args.stage == "kernel": record = run_kernel(args.config)
    elif args.stage == "ecology-gates": record = run_ecology_gates(args.config)
    elif args.stage == "pilot": record = pilot(args.config)
    elif args.stage == "discovery": record = discovery(args.config, args.workers)
    elif args.stage == "freeze": record = freeze_core(args.config)
    else: record = confirmation(args.config, args.workers)
    if "checks" in record and not all(record["checks"].values()): raise SystemExit("kernel tracer has failed checks")
if __name__ == "__main__": main()
