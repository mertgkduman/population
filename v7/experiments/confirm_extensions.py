"""Post-freeze, non-core confirmation precision audit.

This module deliberately lives outside the frozen executable core.  It never changes
the registered 24-seed holdout export: if (and only if) a *practical precision*
target is missed, it registers an entire predeclared batch before launching it.
Effect signs, ranks, and p-values are absent from the scheduling decision.
"""
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
from statistics import mean
from typing import Any
from math import exp, log

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from v7.experiments.analyze_results import mcse, read_rows, wilson_half_width
from v7.experiments.model import CandidateBPolicy, EcologyRun, OrdinarySocialPolicy, PolicyDecision, PolicyObservation
from v7.experiments.run_experiments import ROOT, _policy_spec, _regime, _run_cell


OUTPUT = ROOT / "experiments/output"
FREEZE = ROOT / "evidence/core_freeze/manifest.json"
MANIFEST = OUTPUT / "confirmation_precision_manifest.json"
EXPORT = OUTPUT / "precision_extension.csv.gz"
SUMMARY = OUTPUT / "confirmation_precision.json"
REPRESENTATIVE_INDEX = OUTPUT / "representative_history_index.json"
CALIBRATION_MANIFEST = OUTPUT / "depth_reliability_control_manifest.json"
CALIBRATION_EXPORT = OUTPUT / "depth_reliability_control.csv.gz"
CALIBRATION_SUMMARY = OUTPUT / "depth_reliability_control.json"
PRIMARY_BASELINES = ("vector_0_0", "candidate_b_resource_rational")
MAX_SEED = 72096
BATCH = 8


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def _write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = sorted({key for row in rows for key in row})
    with gzip.open(path, "wt", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _as_float(row: dict[str, str], field: str) -> float:
    return float(row[field])


def _precision(rows: list[dict[str, str]], *, expected_seeds: list[int]) -> dict[str, Any]:
    """Audit targets using only fields that actually exist in the raw export.

    A rate stored without its trial numerator/denominator is intentionally *not*
    rebranded as a Bernoulli proportion.  Terminal extinction is a true run-level
    Bernoulli observation and therefore receives a Wilson interval.
    """
    # Access-off is intentionally registered only in three sentinel regimes.  It is
    # a negative control, not a nine-regime primary precision estimand, so absent
    # cells must never manufacture a batch-extension request.
    policies = sorted({row["policy"] for row in rows if row["policy"] != "asocial_access_off"})
    regimes = sorted({int(row["regime"]) for row in rows})
    records: list[dict[str, Any]] = []
    for regime in regimes:
        by_policy = {policy: [row for row in rows if row["policy"] == policy and int(row["regime"]) == regime]
                     for policy in policies}
        for policy, group in by_policy.items():
            seeds = {int(row["seed"]) for row in group}
            population = [_as_float(row, "mean_population") for row in group]
            extinct = sum(row["status"] == "extinct" for row in group)
            records.append({
                "kind": "within_policy",
                "regime": regime,
                "policy": policy,
                "n": len(group),
                "registered_seed_count": len(expected_seeds),
                "missing_seeds": sorted(set(expected_seeds) - seeds),
                "mean_population_mcse": mcse(population),
                "mean_population_target": 5.0,
                "mean_population_target_met": bool(mcse(population) is not None and mcse(population) <= 5.0),
                "extinction_count": extinct,
                "extinction_wilson_half_width": wilson_half_width(extinct, len(group)),
                "extinction_target": 0.1,
                "extinction_target_met": bool(wilson_half_width(extinct, len(group)) is not None and wilson_half_width(extinct, len(group)) <= .1),
                "other_trial_level_proportions": "UNRESOLVED: core holdout CSV exports rates but not trial-level numerators/denominators.",
            })
        for policy in policies:
            if policy in PRIMARY_BASELINES:
                continue
            for baseline in PRIMARY_BASELINES:
                left = {int(row["seed"]): row for row in by_policy[policy]}
                right = {int(row["seed"]): row for row in by_policy.get(baseline, [])}
                paired = sorted(set(left) & set(right))
                differences = [_as_float(left[seed], "net_energy_per_agent_season") - _as_float(right[seed], "net_energy_per_agent_season") for seed in paired]
                records.append({
                    "kind": "paired_net_energy",
                    "regime": regime,
                    "policy": policy,
                    "baseline": baseline,
                    "n": len(differences),
                    "net_energy_paired_mcse": mcse(differences),
                    "net_energy_target": 0.1,
                    "net_energy_target_met": bool(mcse(differences) is not None and mcse(differences) <= .1),
                    "missing_pair_seeds": sorted(set(expected_seeds) - set(paired)),
                })
    return {"records": records, "all_practical_targets_met": all(
        record.get("mean_population_target_met", True)
        and record.get("extinction_target_met", True)
        and record.get("net_energy_target_met", True)
        for record in records
    )}


def _batch_jobs(seeds: list[int], policies: list[str]) -> list[dict[str, Any]]:
    jobs = [
        {**_regime(regime), "seed": seed, "policy": policy, "stage": "precision_extension",
         "graph_variant": 1, "retain_history": False}
        for regime in range(9) for policy in policies for seed in seeds
    ]
    jobs.extend(
        {**_regime(regime), "seed": seed, "policy": "asocial_access_off", "stage": "precision_access_sentinel",
         "graph_variant": 1, "retain_history": False}
        for regime in (0, 4, 8) for seed in seeds
    )
    return jobs


def _run_jobs(jobs: list[dict[str, Any]], workers: int) -> list[dict[str, Any]]:
    if workers < 1 or workers > 4:
        raise ValueError("worker count is frozen to 1..4")
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(_run_cell, jobs, chunksize=1))


def _check_core_freeze() -> dict[str, str]:
    freeze = json.loads(FREEZE.read_text())
    mismatches = {}
    for relative, expected in freeze["source_sha256"].items():
        actual = _sha(ROOT / relative)
        if actual != expected:
            mismatches[relative] = actual
    if mismatches:
        raise RuntimeError(f"live frozen core drifted: {mismatches}")
    return freeze["source_sha256"]


def build_representative_index() -> dict[str, Any]:
    """Index the already-retained actual histories without re-running the IBM.

    The source gzip remains the authoritative record.  This compact index makes the
    seasonal founder/adult/newborn counts, resource/flux, acquired-state summaries,
    decisions, and the two real genealogy edge sets dashboard-addressable without
    manufacturing person-level state that the frozen run did not export.
    """
    source = OUTPUT / "representative_trajectories.json.gz"
    with gzip.open(source, "rt") as handle:
        histories = json.load(handle)
    if len(histories) != 24:
        raise RuntimeError("the frozen discovery representative set must contain exactly 24 histories")
    index = []
    for ordinal, history in enumerate(histories, start=1):
        reports = history["reports"]
        final = reports[-1] if reports else {}
        action_counts: dict[str, int] = {}
        for event in history["decision_events"]:
            action = str(event.get("chosen_action", "unknown"))
            action_counts[action] = action_counts.get(action, 0) + 1
        index.append({
            "history_id": f"discovery-{ordinal:02d}", "source": "representative_trajectories.json.gz",
            "seed": history["seed"], "policy": history["policy"], "regime": history["regime"],
            "seasons": len(reports), "terminal_status": final.get("status"), "terminal_replay_digest": final.get("replay_digest"),
            "final_actual_population": final.get("population_next"), "final_actual_founders": final.get("founders"),
            "final_actual_adults": final.get("adults"), "final_actual_newborns": final.get("newborns"),
            "final_actual_resource": final.get("resource"), "final_actual_acquired_procedures": final.get("stored_knowledge"),
            "final_actual_adult_belief_accuracy": final.get("adult_evidence_accuracy"),
            "birth_flux": sum(report["births"] for report in reports), "death_flux": sum(report["deaths"] for report in reports),
            "decision_event_count": len(history["decision_events"]), "actual_action_counts": action_counts,
            "biological_genealogy_edge_count": len(history["biological_edges"]),
            "cultural_genealogy_edge_count": len(history["cultural_edges"]),
            "report_fields": sorted(final), "decision_fields": sorted(history["decision_events"][0]) if history["decision_events"] else [],
        })
    result = {
        "stage": "representative-history-index", "status": "complete", "history_count": len(index),
        "source_sha256": _sha(source), "histories": index,
        "capacity_status": "All 24 predesignated frozen-core discovery histories are already retained; no later-stage full-history slots remain. No extra histories were launched.",
        "claim_limit": "Individual B/K/T/H maps and source provenance values were not exported by the frozen core and are therefore not inferred here.",
    }
    _atomic_json(REPRESENTATIVE_INDEX, result)
    return result


class DepthAwareReliabilityPolicy(OrdinarySocialPolicy):
    """d=0 social learner with a public, depth-aware execution-noise likelihood.

    It sees the same observable teacher success/failure counters as every other
    policy.  Depth is reconstructed from the posted execution price, not a hidden
    task value.  The five charged operations bound the likelihood calculation; this
    makes it a conservative routine-capacity control rather than free inference.
    """
    EXTRA_OPERATIONS = 4

    @staticmethod
    def _depth(observation: PolicyObservation) -> int:
        execute = dict(observation.prices).get("execute", 0.0)
        depth = int(round(execute / .2))
        return depth if depth in {1, 3, 6} else 0

    def _posterior(self, observation: PolicyObservation) -> tuple[dict[str, float], float]:
        if observation.domain != "procedure" or observation.advice not in {"branch_0", "branch_1"}:
            return {}, .5
        beliefs = dict(observation.beliefs)
        values = {"branch_0": max(1e-12, beliefs.get("p_branch_0", .5)), "branch_1": max(1e-12, beliefs.get("p_branch_1", .5))}
        if observation.private_cue in values:
            accuracy = max(1e-9, min(1 - 1e-9, beliefs.get("private_likelihood", .8)))
            values[observation.private_cue] *= accuracy
            values["branch_1" if observation.private_cue == "branch_0" else "branch_0"] *= 1 - accuracy
        history = dict(observation.source_history)
        successes, failures, depth = history.get("successes", 0.0), history.get("failures", 0.0), self._depth(observation)
        if depth:
            p_plus, p_minus = .9 ** (depth + 1), .5 ** (depth + 1)
            log_odds = successes * log(p_plus / p_minus) + failures * log((1 - p_plus) / (1 - p_minus))
            reliability = 1 / (1 + exp(-max(-40., min(40., log_odds))))
        else:
            reliability = .5
        advised = observation.advice
        values[advised] *= reliability
        values["branch_1" if advised == "branch_0" else "branch_0"] *= 1 - reliability
        total = sum(values.values())
        return {key: value / total for key, value in values.items()}, reliability

    def decide(self, observation: PolicyObservation, operation_cap: int, keyed_rng: Any) -> PolicyDecision:
        # No-offer procedure episodes have no social likelihood to recalibrate;
        # preserve the ordinary d=0 action rather than invent a branch posterior.
        if observation.domain != "procedure" or observation.advice not in {"branch_0", "branch_1"}:
            return OrdinarySocialPolicy(0., 0.).decide(observation, operation_cap, keyed_rng)
        if operation_cap < 1 + self.EXTRA_OPERATIONS:
            raise ValueError("depth-aware reliability control requires its declared bounded operation budget")
        posterior, reliability = self._posterior(observation)
        prices = dict(observation.prices)
        plus, minus = prices.get("procedure_expected_plus", 0.), prices.get("procedure_expected_minus", 0.)
        q0 = tuple(sorted((branch, probability * plus + (1 - probability) * minus) for branch, probability in posterior.items()))
        neutral = max(q0, key=lambda item: (item[1], item[0]))[0]
        learning = hashlib.sha256(repr((observation.beliefs, observation.procedures, observation.trust, observation.provenance_roots)).encode()).hexdigest()
        digest = hashlib.sha256(repr((q0, neutral, observation.messages, observation.provenance_roots, reliability)).encode()).hexdigest()
        return PolicyDecision(q0, neutral, observation.advice, observation.advice is not None and neutral != observation.advice,
                              neutral, 1 + self.EXTRA_OPERATIONS, prices.get("operation", 0.) * (1 + self.EXTRA_OPERATIONS),
                              False, None, None, bool(observation.messages), digest, learning, learning,
                              posterior.get(observation.advice or "", .5), None, 0.)


def _control_cell(job: dict[str, Any]) -> dict[str, Any]:
    factories = {"ordinary_social": OrdinarySocialPolicy, "candidate_b_resource_rational": CandidateBPolicy,
                 "depth_aware_reliability_d0": DepthAwareReliabilityPolicy}
    if job["policy"] in factories:
        factory, traits = factories[job["policy"]], {"d_procedure": 0., "d_local": 0.}
    else:
        factory, traits = _policy_spec(job["policy"])
    run = EcologyRun(job["seed"], factory, depth=job["depth"], chi=job["chi"], q_theta=job["q_theta"],
                     verification_price=job["verification_price"], graph_variant=1, initial_traits=traits,
                     label=job["policy"])
    result = run.run()
    result.update(job)
    return result


def run_depth_reliability_control(workers: int = 4) -> dict[str, Any]:
    """Run the frozen, exploratory H7/miscalibration control in a new partition."""
    core_hashes = _check_core_freeze()
    freeze = json.loads(FREEZE.read_text())
    frozen_vector = freeze["frozen_vectors"][0]
    seeds, regimes, policies = list(range(72501, 72525)), [0, 4, 8], ["ordinary_social", "candidate_b_resource_rational", "depth_aware_reliability_d0", frozen_vector]
    jobs = [{**_regime(regime), "seed": seed, "policy": policy, "stage": "exploratory_depth_reliability_control", "graph_variant": 1, "retain_history": False}
            for regime in regimes for policy in policies for seed in seeds]
    prior = json.loads(CALIBRATION_MANIFEST.read_text()) if CALIBRATION_MANIFEST.exists() else None
    manifest = {"stage": "exploratory-depth-reliability-control", "status": "registered", "registered_at": (prior or {}).get("registered_at", datetime.now(timezone.utc).isoformat()),
                "outcomes_read": False, "source_sha256": core_hashes, "extension_sha256": _sha(Path(__file__)), "freeze_manifest_sha256": _sha(FREEZE),
                "seeds": seeds, "regimes": [1, 5, 9], "policies": policies, "jobs": jobs,
                "predeclared_question": "Does depth-aware correction for publicly observed complete-procedure execution noise remove a result attributable to naive teacher-success calibration?",
                "likelihood_assumptions": "Teacher sequence quality is stationary across the public success/failure history and complete executions are conditionally independent given sequence quality. Structural change is not observed by the learner; q_theta remains an ecology parameter, so this control does not claim robustness to nonstationary teacher competence.",
                "claim_limit": "Exploratory post-freeze strong control, separate from frozen primary confirmation; it neither changes primary candidates nor establishes latent truth access."}
    if prior is not None:
        manifest["prior_failed_attempt"] = {"source_sha256": prior.get("extension_sha256"), "status": prior.get("status"),
                                            "outcomes_read": prior.get("outcomes_read"), "reason": "No-offer procedure observations produced no advised branch posterior; repaired before any CSV export."}
        manifest["rerun_registered_at"] = datetime.now(timezone.utc).isoformat()
    _atomic_json(CALIBRATION_MANIFEST, manifest)
    if workers < 1 or workers > 4:
        raise ValueError("worker count is frozen to 1..4")
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(_control_cell, jobs, chunksize=1))
    _write_rows(CALIBRATION_EXPORT, rows)
    terminal = {name: sum(row["status"] == name for row in rows) for name in sorted({row["status"] for row in rows})}
    summary = {"stage": manifest["stage"], "status": "complete", "rows": len(rows), "terminal_counts": terminal,
               "output_sha256": _sha(CALIBRATION_EXPORT), "claim_limit": manifest["claim_limit"],
               "result_status": "Measured rows only; interpretation requires the full contrast table and cannot revise the primary frozen confirmation."}
    _atomic_json(CALIBRATION_SUMMARY, summary)
    manifest.update({"status": "complete", "outcomes_read": True, "completed_at": datetime.now(timezone.utc).isoformat(),
                     "output_sha256": summary["output_sha256"], "terminal_counts": terminal})
    _atomic_json(CALIBRATION_MANIFEST, manifest)
    return summary


def run_precision_scheduler(workers: int = 4) -> dict[str, Any]:
    """Execute strictly predeclared batches based only on uncertainty targets."""
    core_hashes = _check_core_freeze()
    holdout = OUTPUT / "holdout.csv.gz"
    if not holdout.is_file():
        raise RuntimeError("the atomic 24-seed holdout export is not available")
    # Persist the design and source binding before reading the completed holdout
    # export or registering any added trajectories.  The eventual policy list is
    # checked against this binding instead of selected by an observed effect.
    manifest = {
        "stage": "confirmation_precision_extension",
        "status": "registered",
        "registered_at": datetime.now(timezone.utc).isoformat(),
        "outcomes_read": False,
        "source_of_initial_rows": "v7/experiments/output/holdout.csv.gz",
        "source_sha256": core_hashes,
        "freeze_manifest_sha256": _sha(FREEZE),
        "holdout_sha256": _sha(holdout),
        "required_policies": ["vector_0_0", "feature_trust", "candidate_b_resource_rational"],
        "access_sentinel_regimes": [1, 5, 9],
        "seed_cap": MAX_SEED,
        "batch_size": BATCH,
        "stopping_rule": "Only fixed practical precision targets decide whether to add the next full batch; no effect sign, rank, or p-value is read by this scheduler.",
        "registered_batches": [],
    }
    _atomic_json(MANIFEST, manifest)
    initial = read_rows(holdout)
    policies = list(dict.fromkeys(row["policy"] for row in initial if row["policy"] != "asocial_access_off"))
    if not {"vector_0_0", "candidate_b_resource_rational"}.issubset(policies):
        raise RuntimeError("required ordinary-social/Candidate-B baselines are absent")
    extension: list[dict[str, Any]] = read_rows(EXPORT) if EXPORT.exists() else []
    manifest["policies"] = policies
    _atomic_json(MANIFEST, manifest)
    while True:
        all_rows = initial + extension
        observed_seeds = sorted({int(row["seed"]) for row in all_rows})
        audit = _precision(all_rows, expected_seeds=observed_seeds)
        if audit["all_practical_targets_met"] or max(observed_seeds, default=72000) >= MAX_SEED:
            break
        next_start = max(observed_seeds) + 1
        seeds = list(range(next_start, min(MAX_SEED, next_start + BATCH - 1) + 1))
        jobs = _batch_jobs(seeds, policies)
        # This is the registration boundary: nothing in this batch has run yet.
        manifest["registered_batches"].append({"seeds": seeds, "jobs": jobs, "registered_at": datetime.now(timezone.utc).isoformat()})
        _atomic_json(MANIFEST, manifest)
        produced = _run_jobs(jobs, workers)
        extension.extend(produced)
        _write_rows(EXPORT, extension)
    final_rows = initial + extension
    final_seeds = sorted({int(row["seed"]) for row in final_rows})
    audit = _precision(final_rows, expected_seeds=final_seeds)
    unresolved = [] if audit["all_practical_targets_met"] else [
        "UNRESOLVED at the predeclared 96-seed cap: one or more practical targets remain unmet.",
        "UNRESOLVED: trial-level success/action/revision proportions cannot be Wilson-audited because frozen core rows retain rates rather than Bernoulli numerators/denominators.",
    ]
    # No claim is made for assays requiring intervention hooks that the archived core
    # does not expose.  Their absence is a scoped result, not simulated evidence.
    partial_assays = {
        "yoked_depth_context_access": "PARTIAL: no observational intervention hook in the frozen core; not run rather than altering core behavior.",
        "culture_ablations_and_carrier_loss": "NOT_RUN: no pre-freeze registered carrier-removal/storage intervention exists in the frozen core.",
        "H9_environment_shock": "NOT_RUN: shock mechanics are not implemented in the frozen core; no proxy was substituted.",
    }
    result = {"stage": "confirmation_precision_extension", "status": "complete" if audit["all_practical_targets_met"] else "unresolved_at_cap",
              "n_initial_rows": len(initial), "n_extension_rows": len(extension), "seed_range": [min(final_seeds), max(final_seeds)],
              "audit": audit, "unresolved": unresolved, "partial_assays": partial_assays,
              "claim_limit": "Finite, extinction-inclusive simulation precision only; no asymptotic invasion, ESS, or unexported trial-level proportion claim."}
    _atomic_json(SUMMARY, result)
    manifest.update({"status": result["status"], "outcomes_read": True, "completed_at": datetime.now(timezone.utc).isoformat(),
                     "extension_rows": len(extension), "output_sha256": _sha(EXPORT) if EXPORT.exists() else None,
                     "summary_sha256": _sha(SUMMARY), "unresolved": unresolved})
    _atomic_json(MANIFEST, manifest)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("precision", "representatives", "depth-reliability-control"), required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    result = build_representative_index() if args.stage == "representatives" else (run_depth_reliability_control(args.workers) if args.stage == "depth-reliability-control" else run_precision_scheduler(args.workers))
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
