#!/usr/bin/env python3
"""Evidence-preserving V7 synthesis.

This module is deliberately outside the frozen ``v7.experiments`` core.  It
recomputes report quantities from immutable raw exports and writes only
derived reporting artifacts.
"""

from __future__ import annotations

import argparse
import ast
import csv
import gzip
import hashlib
import json
import math
import statistics
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
V7 = ROOT / "v7"
OUT = V7 / "experiments" / "output"
CORRECTED_OUT = OUT / "corrected"
EVIDENCE = V7 / "evidence"
CORRECTED_EVIDENCE = EVIDENCE / "corrected"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_rows_from(directory: Path, name: str) -> list[dict[str, str]]:
    with gzip.open(directory / f"{name}.csv.gz", "rt", newline="") as handle:
        return list(csv.DictReader(handle))


def read_rows(name: str) -> list[dict[str, str]]:
    return read_rows_from(OUT, name)


def read_corrected_rows(name: str) -> list[dict[str, str]]:
    return read_rows_from(CORRECTED_OUT, name)


def f(row: dict[str, str], field: str) -> float:
    return float(row[field])


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return statistics.fmean(values) if values else math.nan


def mcse(values: Iterable[float]) -> float:
    values = list(values)
    if len(values) < 2:
        return math.nan
    return statistics.stdev(values) / math.sqrt(len(values))


def paired(rows: list[dict[str, str]], policy: str, reference: str, field: str) -> dict[str, Any]:
    by = {(r["seed"], r["regime"], r["policy"]): f(r, field) for r in rows}
    diffs = [
        by[(seed, regime, policy)] - by[(seed, regime, reference)]
        for seed, regime, pol in by
        if pol == policy and (seed, regime, reference) in by
    ]
    return {"n_pairs": len(diffs), "mean_delta": mean(diffs), "paired_mcse": mcse(diffs),
            "min_delta": min(diffs), "max_delta": max(diffs)}


def build_summary(records: list[dict[str, Any]]) -> dict[str, int]:
    """Unconditional finite-run denominator; zero outcomes never disappear."""
    return {
        "unconditional_denominator": len(records),
        "extinction_count": sum(r.get("terminal") == "extinct" for r in records),
        "cap_censored_count": sum(r.get("terminal") == "cap_censored" for r in records),
        "no_birth_count": sum(bool(r.get("no_birth_censored", False)) for r in records),
    }


def validate_result_record(record: dict[str, Any]) -> bool:
    """Reject untraceable, non-finite, or asymptotic claims from finite assays."""
    claim = str(record.get("claim", "")).strip()
    evidence = str(record.get("evidence", "")).strip()
    limit = str(record.get("claim_limit", "")).lower()
    if not claim or not evidence:
        raise ValueError("claim and evidence pointer are required")
    banned = {"ess", "fixation", "asymptotic invasion", "stable polymorphism"}
    if any(term in claim.lower() for term in banned) and "not " not in limit:
        raise ValueError("finite evidence cannot support an asymptotic claim")
    for value in record.values():
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("non-finite value in result record")
    return True


def classify_intermediate_generator(points: list[dict[str, float]], tolerance: float = 1e-9) -> dict[str, Any]:
    """Classify a synthetic response surface without declaring a unique optimum."""
    if not points:
        raise ValueError("at least one point is required")
    top = max(p["value"] for p in points)
    compatible = [p for p in points if p["value"] >= top - tolerance]
    interior = [p for p in compatible if 0.0 < p["d_local"] < 1.0 and 0.0 < p["d_procedure"] < 1.0]
    return {"top_value": top, "compatible_points": compatible,
            "classification": "intermediate-compatible" if interior else "boundary-compatible"}


def artifact_inventory() -> dict[str, dict[str, Any]]:
    names = ["discovery", "holdout", "depth_reliability_control", "evolution",
             "persistence", "postfreeze_yoked", "cumulative_assay", "postfreeze_h9_observation"]
    return {name: {"path": str((OUT / f"{name}.csv.gz").relative_to(ROOT)),
                   "rows": len(read_rows(name)), "sha256": sha256(OUT / f"{name}.csv.gz")}
            for name in names}


def corrected_artifact_inventory() -> dict[str, dict[str, Any]]:
    """Inventory fresh overlay outputs without conflating them with frozen raw."""
    names = {
        "discovery": "discovery",
        "holdout": "holdout",
        "depth_reliability_control": "depth_reliability_control",
        "evolution": "corrected_evolution",
        "h9": "corrected_h9",
    }
    inventory = {}
    for name, filename in names.items():
        path = CORRECTED_OUT / f"{filename}.csv.gz"
        inventory[name] = {
            "path": str(path.relative_to(ROOT)),
            "rows": len(read_rows_from(CORRECTED_OUT, filename)),
            "sha256": sha256(path),
        }
    return inventory


def corrected_data_quality(inventory: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Fail-closed grain, coverage, finiteness, and manifest reconciliation."""
    datasets = {
        "discovery": read_corrected_rows("discovery"),
        "holdout": read_corrected_rows("holdout"),
        "depth_reliability_control": read_corrected_rows("depth_reliability_control"),
        "evolution": read_rows_from(CORRECTED_OUT, "corrected_evolution"),
        "h9": read_rows_from(CORRECTED_OUT, "corrected_h9"),
    }
    checks: list[dict[str, Any]] = []

    def record(check_id: str, passed: bool, evidence: dict[str, Any]) -> None:
        checks.append({"id": check_id, "status": "passed" if passed else "failed",
                       "evidence": evidence})

    expected_rows = {"discovery": 504, "holdout": 1368,
                     "depth_reliability_control": 288, "h9": 216}
    for name, expected in expected_rows.items():
        observed = len(datasets[name])
        record(f"{name}-row-count", observed == expected,
               {"expected": expected, "observed": observed,
                "sha256": inventory[name]["sha256"]})

    keys = {
        "discovery": ("seed", "regime", "policy"),
        "holdout": ("seed", "regime", "policy"),
        "depth_reliability_control": ("seed", "regime", "policy"),
        "evolution": ("seed", "regime", "directed_pair", "arm"),
        "h9": ("seed", "regime", "arm"),
    }
    for name, fields in keys.items():
        rows = datasets[name]
        tuples = [tuple(row[field] for field in fields) for row in rows]
        record(f"{name}-grain-unique", len(tuples) == len(set(tuples)),
               {"grain": list(fields), "rows": len(tuples),
                "unique_keys": len(set(tuples))})

    seed_expectations = {
        "discovery": set(range(77001, 77005)),
        "holdout": set(range(78001, 78025)),
        "depth_reliability_control": set(range(78501, 78525)),
        "h9": set(range(78601, 78625)),
    }
    for name, expected in seed_expectations.items():
        observed = {int(row["seed"]) for row in datasets[name]}
        record(f"{name}-seed-partition", observed == expected,
               {"expected_min": min(expected), "expected_max": max(expected),
                "observed_min": min(observed), "observed_max": max(observed),
                "observed_distinct": len(observed)})

    metric_fields = {
        "discovery": ("mean_population", "net_energy_per_agent_season"),
        "holdout": ("mean_population", "net_energy_per_agent_season"),
        "depth_reliability_control": ("mean_population", "net_energy_per_agent_season"),
        "evolution": ("living_descendants", "ledger_residual_max"),
        "h9": ("mean_population", "post_stored_procedures"),
    }
    for name, fields in metric_fields.items():
        finite = all(math.isfinite(float(row[field])) for row in datasets[name] for field in fields)
        record(f"{name}-finite-metrics", finite,
               {"fields": list(fields), "values_checked": len(datasets[name]) * len(fields)})

    results = {
        "discovery": (CORRECTED_EVIDENCE / "discovery_result.json", "sha256"),
        "holdout": (CORRECTED_EVIDENCE / "holdout_result.json", "sha256"),
        "depth_reliability_control": (CORRECTED_EVIDENCE / "depth_control_result.json", "sha256"),
        "evolution": (CORRECTED_EVIDENCE / "corrected_evolution_result.json", "raw_sha256"),
        "h9": (CORRECTED_EVIDENCE / "corrected_h9_result.json", "sha256"),
    }
    for name, (path, field) in results.items():
        document = json.loads(path.read_text())
        record(f"{name}-result-hash", document[field] == inventory[name]["sha256"],
               {"result_manifest": str(path.relative_to(ROOT)),
                "manifest_sha256": document[field], "recomputed_sha256": inventory[name]["sha256"]})

    evolution_rows = datasets["evolution"]
    evolution_count_ok = (576 <= len(evolution_rows) <= 2304 and
                          (len(evolution_rows) - 576) % 192 == 0)
    record("evolution-fixed-batch-volume", evolution_count_ok,
           {"observed_rows": len(evolution_rows), "allowed": "576 + k*192, 0<=k<=9"})

    registration = json.loads((CORRECTED_EVIDENCE / "discovery_registration.json").read_text())
    source_matches = {}
    for relative, expected in registration["source_sha256"].items():
        actual = sha256(V7 / relative)
        source_matches[relative] = {"expected": expected, "actual": actual,
                                    "matches": expected == actual}
    record("registered-source-identity", all(item["matches"] for item in source_matches.values()),
           source_matches)

    evolution_registration = json.loads(
        (CORRECTED_EVIDENCE / "corrected_evolution_registration.json").read_text())
    evolution_source_matches = {}
    for relative, expected in evolution_registration["overlay_source_sha256"].items():
        path = V7 / "experiments" / relative
        actual = sha256(path)
        evolution_source_matches[relative] = {"expected": expected, "actual": actual,
                                              "matches": expected == actual}
    record("evolution-registered-source-identity",
           all(item["matches"] for item in evolution_source_matches.values()),
           evolution_source_matches)

    freeze_path = CORRECTED_EVIDENCE / "freeze_variant" / "manifest.json"
    record("evolution-freeze-parent",
           evolution_registration["corrected_ecology_freeze_manifest_sha256"] == sha256(freeze_path),
           {"registered": evolution_registration["corrected_ecology_freeze_manifest_sha256"],
            "recomputed": sha256(freeze_path)})

    return {"schema_version": 1,
            "status": "passed" if all(c["status"] == "passed" for c in checks) else "failed",
            "datasets": {name: {"rows": item["rows"], "sha256": item["sha256"]}
                         for name, item in inventory.items()},
            "checks": checks}


def tiny_exact_summary() -> dict[str, Any]:
    path = OUT / "kernel.json"
    kernel = json.loads(path.read_text())
    exact = kernel["exact"]
    return {
        "path": str(path.relative_to(ROOT)), "sha256": sha256(path),
        "exact_enumerated_value": exact["exact_value"], "exact_first_action": exact["exact_first_action"],
        "restricted_monte_carlo_value": exact["restricted_value"],
        "restricted_monte_carlo_mcse": exact["mcse"], "restricted_replicates": exact["restricted_replicates"],
        "exact_minus_restricted": exact["exact_value"] - exact["restricted_value"],
        "upper_bound_holds_in_matched_toy": exact["upper_bound_holds"], "scope": exact["scope"],
        "task_economics": kernel["task_economics"],
    }


def frozen_local_no_teacher_audit() -> dict[str, Any]:
    """Execute the frozen no-tutor local path and retain the defect as evidence."""
    from v7.experiments.model import AsocialPolicy, EcologyRun, KeyedRNG

    # This fixed audit seed makes the private cue wrong while the phantom tutor is
    # exactly correct, so the behavioral truth leak is visible in one record.
    run = EcologyRun(71901, AsocialPolicy, burn_in=0, measurement=1, label="defect-audit")
    person = run.population[sorted(run.population)[0]]
    z, private, tutor = run._local_state(person, "food", None)
    observation, _ = run._local_observation(person, "food", None)
    decision = person.policy.decide(observation, run.OPERATION_CAP,
                                    KeyedRNG(str(run.seed), "D1", run.season))
    confirmed = observation.advice is None and decision.chosen_action == "teacher" and tutor == z
    return {
        "status": "CONFIRMED_FROZEN_DEFECT" if confirmed else "NOT_REPRODUCED",
        "source": "v7/experiments/model.py", "source_sha256": sha256(V7 / "experiments" / "model.py"),
        "audit_seed": run.seed,
        "teacher": None, "feasible_actions": list(observation.feasible_actions),
        "q0_values": [list(item) for item in decision.q0_values], "neutral_action": decision.neutral_action,
        "chosen_action": decision.chosen_action, "latent_local_state_z": z,
        "private_signal": private, "phantom_tutor_signal": tutor,
        "phantom_tutor_equals_hidden_state": tutor == z,
        "mechanism": "No advice leaves private/teacher Q0 tied at zero; lexical tie-break selects teacher. With no teacher, local-state construction sets the synthetic tutor signal equal to hidden z.",
        "scientific_impact": "Asocial local comparisons are invalid. Other ecology/holdout/lineage results are descriptive under an unquantified no-teacher-local contamination until replay exports exposure counts or a corrected frozen variant is run.",
        "repair_boundary": "Do not edit frozen/archive bytes or cached primary data; future corrected variant must remove teacher action without a teacher or route it to the private cue and rerun affected ecology evidence.",
    }


def corrected_local_no_teacher_audit() -> dict[str, Any]:
    """Exercise the same adversarial path through the versioned correction."""
    from v7.experiments.corrected_model import CorrectedEcologyRun
    from v7.experiments.model import AsocialPolicy, KeyedRNG

    run = CorrectedEcologyRun(71901, AsocialPolicy, burn_in=0, measurement=1,
                              label="corrected-defect-audit")
    person = run.population[sorted(run.population)[0]]
    z, private, tutor = run._local_state(person, "food", None)
    observation, context = run._local_observation(person, "food", None)
    decision = person.policy.decide(observation, run.OPERATION_CAP,
                                    KeyedRNG(str(run.seed), "D1", run.season))
    before = person.energy
    run._local_attempt(person, "food", "teacher", context, None)
    payoff_positive = person.energy > before
    repaired = (
        observation.advice is None
        and observation.feasible_actions == ("private",)
        and dict(observation.action_values) == {"private": 2.0}
        and decision.chosen_action == "private"
        and tutor == private
        and payoff_positive == (private == z)
    )
    return {
        "status": "CORRECTED_PATH_VALIDATED" if repaired else "CORRECTION_FAILED",
        "source": "v7/experiments/corrected_model.py",
        "source_sha256": sha256(V7 / "experiments" / "corrected_model.py"),
        "base_source_sha256": sha256(V7 / "experiments" / "model.py"),
        "audit_seed": run.seed,
        "teacher": None,
        "feasible_actions": list(observation.feasible_actions),
        "action_values": [list(item) for item in observation.action_values],
        "chosen_action": decision.chosen_action,
        "latent_local_state_z": z,
        "private_signal": private,
        "unused_tutor_placeholder": tutor,
        "placeholder_equals_private": tutor == private,
        "executed_success_matches_private_cue": payoff_positive == (private == z),
        "scope": "No-teacher local path only; teacher-present behavior delegates to the frozen base.",
    }


VECTOR_TRAITS = {
    "vector_0_0": (0.0, 0.0), "vector_0_0_5": (0.0, 0.5), "vector_0_1": (0.0, 1.0),
    "vector_0_5_0": (0.5, 0.0), "vector_0_5_0_5": (0.5, 0.5), "vector_0_5_1": (0.5, 1.0),
    "vector_1_0": (1.0, 0.0), "vector_1_0_5": (1.0, 0.5), "vector_1_1": (1.0, 1.0),
}
SCALAR_POLICIES = ["vector_0_0", "scalar_0_25", "vector_0_5_0_5", "scalar_0_75", "vector_1_1"]
COMPARATORS = ["asocial_access_off", "feature_trust", "candidate_b_resource_rational"]


def discovery_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    means: dict[tuple[str, str], float] = {}
    by_policy_regime: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_policy_regime[(row["regime"], row["policy"])].append(row)
    for key, group in by_policy_regime.items():
        means[key] = mean(f(r, "mean_population") for r in group)

    effects = []
    primary_mean_population_contrasts = []
    for regime in map(str, range(1, 10)):
        by = {(r["seed"], r["policy"]): f(r, "mean_population") for r in rows if r["regime"] == regime}
        for local in (0.0, 0.5, 1.0):
            p0 = next(p for p, d in VECTOR_TRAITS.items() if d == (0.0, local))
            p1 = next(p for p, d in VECTOR_TRAITS.items() if d == (1.0, local))
            ds = [by[(seed, p1)] - by[(seed, p0)] for seed in {s for s, p in by}]
            effects.append({"regime": int(regime), "coordinate": "d_procedure", "fixed_d_local": local,
                            "contrast": "1-0", "n_pairs": len(ds), "mean_delta_N": mean(ds), "paired_mcse": mcse(ds)})
        for proc in (0.0, 0.5, 1.0):
            p0 = next(p for p, d in VECTOR_TRAITS.items() if d == (proc, 0.0))
            p1 = next(p for p, d in VECTOR_TRAITS.items() if d == (proc, 1.0))
            ds = [by[(seed, p1)] - by[(seed, p0)] for seed in {s for s, p in by}]
            effects.append({"regime": int(regime), "coordinate": "d_local", "fixed_d_procedure": proc,
                            "contrast": "1-0", "n_pairs": len(ds), "mean_delta_N": mean(ds), "paired_mcse": mcse(ds)})

        for label, policy in (("procedure_only", "vector_1_0"),
                              ("local_only", "vector_0_1"),
                              ("scalar_diagonal", "vector_1_1")):
            ds = [by[(seed, policy)] - by[(seed, "vector_0_0")]
                  for seed in {seed for seed, _policy in by}]
            primary_mean_population_contrasts.append({
                "regime": int(regime), "contrast": label,
                "candidate": policy, "reference": "vector_0_0",
                "n_pairs": len(ds), "mean_delta_N": mean(ds),
                "paired_mcse": mcse(ds), "min_delta_N": min(ds), "max_delta_N": max(ds),
            })

    classes = {"vector": list(VECTOR_TRAITS), "scalar": SCALAR_POLICIES, "comparators": COMPARATORS}
    optima = []
    for regime in map(str, range(1, 10)):
        for name, policies in classes.items():
            top = max(policies, key=lambda p: means[(regime, p)])
            compatible = []
            for policy in policies:
                if policy == top:
                    compatible.append(policy)
                    continue
                by = {(r["seed"], r["policy"]): f(r, "mean_population") for r in rows if r["regime"] == regime}
                diffs = [by[(seed, top)] - by[(seed, policy)] for seed in {s for s, p in by}]
                if mean(diffs) <= 2.0 * mcse(diffs):
                    compatible.append(policy)
            boundary = "not_applicable"
            if name == "vector":
                d = VECTOR_TRAITS[top]
                boundary = "corner" if all(x in (0.0, 1.0) for x in d) else (
                    "edge" if any(x in (0.0, 1.0) for x in d) else "interior")
            elif name == "scalar":
                boundary = "boundary" if top in {"vector_0_0", "vector_1_1"} else "interior"
            optima.append({"regime": int(regime), "class": name, "sample_mean_top": top,
                           "mean_population": means[(regime, top)], "two_mcse_compatible": compatible,
                           "sampled_boundary_class": boundary,
                           "claim_limit": "exploratory sampled-grid compatibility, not an optimum or equivalence set"})
    return {"rows": len(rows), "seeds_per_cell": 4, "effects": effects,
            "primary_mean_population_contrasts": primary_mean_population_contrasts,
            "class_specific_grid": optima,
            "design_limit": "Exploratory L9 design aliases interactions; tau=5 was fixed, not optimized."}


def holdout_summary(rows: list[dict[str, str]], depth_rows: list[dict[str, str]],
                    diagnostic_policies: Iterable[str] | None = None) -> dict[str, Any]:
    contrasts = []
    for regime in map(str, range(1, 10)):
        group = [r for r in rows if r["regime"] == regime]
        for policy in sorted({r["policy"] for r in group} - {"vector_0_0"}):
            result = paired(group, policy, "vector_0_0", "net_energy_per_agent_season")
            population = paired(group, policy, "vector_0_0", "mean_population")
            births = paired(group, policy, "vector_0_0", "birth_flux")
            deaths = paired(group, policy, "vector_0_0", "death_flux")
            result.update(population_mean_delta=population["mean_delta"],
                          population_paired_mcse=population["paired_mcse"],
                          birth_flux_mean_delta=births["mean_delta"],
                          birth_flux_paired_mcse=births["paired_mcse"],
                          death_flux_mean_delta=deaths["mean_delta"],
                          death_flux_paired_mcse=deaths["paired_mcse"])
            result.update(regime=int(regime), policy=policy, reference="ordinary_social/vector_0_0")
            contrasts.append(result)
    dcontrol = []
    for regime in ("1", "5", "9"):
        result = paired([r for r in depth_rows if r["regime"] == regime],
                        "depth_aware_reliability_d0", "ordinary_social", "net_energy_per_agent_season")
        result["regime"] = int(regime)
        dcontrol.append(result)
    available = {r["policy"] for r in rows}
    diagnostics = list(diagnostic_policies or ("vector_0_0", "vector_0_5_0"))
    diagnostics = [policy for policy in diagnostics if policy in available]
    rate_diagnostics = []
    for regime in map(str, range(1, 10)):
        for policy in diagnostics:
            group = [r for r in rows if r["regime"] == regime and r["policy"] == policy]
            if not group:
                continue
            rate_diagnostics.append({"regime": int(regime), "policy": policy,
                **{field: {"mean": mean(f(r, field) for r in group), "across_seed_mcse": mcse(f(r, field) for r in group)}
                   for field in ("cultural_action_accuracy", "override_rate", "revision_rate")}})
    statuses = defaultdict(int)
    for row in rows:
        statuses[row["status"]] += 1
    return {"rows": len(rows), "status_counts": dict(statuses),
            "extinction_count": statuses.get("extinct", 0),
            "cap_censored_count": statuses.get("cap_censored", 0), "contrasts": contrasts, "depth_aware_control": dcontrol,
            "rate_diagnostics": rate_diagnostics,
            "rate_precision": "UNRESOLVED: exported rates lack event-level numerator/denominator counts; MCSE is across seeds only, never Bernoulli pseudo-replication."}


def selection_summary(rows: list[dict[str, str]], *, seed_start: int = 73001,
                      seed_max: int = 73096) -> dict[str, Any]:
    groups: dict[tuple[str, str, str], dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        groups[(row["seed"], row["regime"], row["directed_pair"])][row["arm"]] = row
    # Reconstruct the preregistered fixed-batch precision rule from raw rows:
    # initial 24 seeds, then only wholly complete consecutive blocks of eight.
    accepted: set[tuple[str, str, str]] = set()
    for regime in sorted({r["regime"] for r in rows}, key=int):
        for directed in sorted({r["directed_pair"] for r in rows if r["regime"] == regime}):
            blocks = [range(seed_start, seed_start + 24),
                      *[range(start, start + 8) for start in range(seed_start + 24, seed_max + 1, 8)]]
            for block in blocks:
                keys = [(str(seed), regime, directed) for seed in block]
                if all(set(groups.get(key, {})) == {"mutant", "neutral_tag"} for key in keys):
                    accepted.update(keys)
                else:
                    break
    pairs = [groups[key] for key in sorted(accepted)]
    paid_pairs = [arms for arms in pairs
                  if not any(row.get("no_birth_censored") == "True" for row in arms.values())]
    contrasts: dict[tuple[str, str], list[float]] = defaultdict(list)
    for arms in paid_pairs:
        mutant, neutral = arms["mutant"], arms["neutral_tag"]
        contrasts[(mutant["regime"], mutant["directed_pair"])].append(
            f(mutant, "living_descendants") - f(neutral, "living_descendants"))
    summaries = [{"regime": int(k[0]), "directed_pair": k[1], "n_pairs": len(v),
                  "mean_delta_living_descendants": mean(v), "paired_mcse": mcse(v),
                  "zero_delta_count": sum(x == 0 for x in v)} for k, v in sorted(contrasts.items())]
    no_birth = sum(r["no_birth_censored"] == "True" for r in rows)
    return {"registered_raw_rows": len(rows), "completed_batch_rows": 2 * len(pairs),
            "excluded_incomplete_batch_rows": len(rows) - 2 * len(pairs), "paid_birth_rows": len(rows) - no_birth,
            "no_birth_censored": no_birth,
            "cap_censored": sum(r["cap_censored"] == "True" for r in rows),
            "extinction_rows": sum(r["extinct"] == "True" for r in rows),
            "paired_paid_birth_pairs": len(paid_pairs),
            "contrasts": summaries,
            "claim_limit": "80-season paired living-descendant endpoint only; not significance, equivalence, invasion, fixation, ESS, stable polymorphism, or direct competition."}


def extension_summary(persistence: list[dict[str, str]], cumulative: list[dict[str, str]],
                      h9: list[dict[str, str]]) -> dict[str, Any]:
    probes = sorted({r["probe"] for r in persistence})
    persistence_by_probe = {}
    for probe in probes:
        group = [r for r in persistence if r["probe"] == probe]
        persistence_by_probe[probe] = {
            "n_seeds": len(group),
            "mean_action_persistence": mean(f(r, "action_persistence") for r in group),
            "across_seed_mcse": mcse(f(r, "action_persistence") for r in group),
            "mean_factual_revision": mean(f(r, "posterior_revision") for r in group),
        }
    cumulative_by_arm = {}
    for arm in sorted({r["arm"] for r in cumulative}):
        group = [r for r in cumulative if r["arm"] == arm]
        cumulative_by_arm[arm] = {
            "n_seeds": len(group), "total_work_values": sorted({f(r, "total_work") for r in group}),
            "material_debit_values": sorted({f(r, "material_debit") for r in group}),
            "mean_functional_score": mean(f(r, "mean_heldout_functional_score") for r in group),
            "mean_useful_depth": mean(f(r, "mean_useful_depth") for r in group),
            "two_edge_procedures": sum(int(float(r["two_edge_functional_procedures"])) for r in group),
            "upper_bound_only": all(r["upper_bound_only"] == "True" for r in group),
        }
    h9_by_regime_arm = []
    for regime in sorted({r["regime"] for r in h9}, key=int):
        for arm in sorted({r["arm"] for r in h9 if r["regime"] == regime}):
            group = [r for r in h9 if r["regime"] == regime and r["arm"] == arm]
            h9_by_regime_arm.append({
                "regime": int(regime), "arm": arm, "rows": len(group),
                "mean_population": mean(f(r, "mean_population") for r in group),
                "population_across_seed_mcse": mcse(f(r, "mean_population") for r in group),
                "mean_post_stored_procedures": mean(f(r, "post_stored_procedures") for r in group),
                "post_stored_procedures_across_seed_mcse": mcse(
                    f(r, "post_stored_procedures") for r in group),
                "removed_procedures": sum(int(float(r["removed_procedures"])) for r in group),
            })
    return {
        "persistence": {"rows": len(persistence), "probes": persistence_by_probe,
            "claim_limit": "Separate generic reinforcement/action-habit process. It is not the frozen IBM, private-belief dogmatism, an obligation mechanism, or a 20-update intervention."},
        "cumulative": {"rows": len(cumulative), "arms": cumulative_by_arm,
            "claim_limit": "Corrected equal aggregate-work cognitive assay only. The pooled upper bound is not a feasible individual-budget comparator; no demographic cumulative-culture or H2 inference."},
        "h9": {"rows": len(h9), "regime_arms": h9_by_regime_arm,
            "claim_limit": "d=0 shock plus K erasure only; memory erasure is not carrier death, root diversity is unavailable, and no d-by-shock causal mediation was run."},
    }


def hypothesis_ledger() -> list[dict[str, str]]:
    return [
        {"id": "H1", "status": "PARTIAL; EXPLORATORY RESPONSE SURFACE", "evidence": "corrected/discovery.csv.gz; corrected freeze manifest",
         "finding": "Fresh corrected discovery shows regime-dependent procedure/local effects and frequent local-override population costs, but four seeds per cell and aliased L9 interactions do not identify a unique continuous optimum."},
        {"id": "H2", "status": "UNRESOLVED BY STRONG COMPARATOR", "evidence": "corrected/holdout.csv.gz; corrected/depth_reliability_control.csv.gz",
         "finding": "Corrected selected vectors have small regime-dependent contrasts against ordinary social learning. The final execution-priced bounded planner has fresh matched costs/counts but does not beat ordinary in its three sentinels. These algorithm-class comparisons do not establish a distinct authority advantage over general learning."},
        {"id": "H3", "status": "PARTIAL", "evidence": "persistence.csv.gz",
         "finding": "The final fixed-proposition assay uses actual training, cloned adult states and static/switching priors. Information-equalized d changes no factual posterior; H can differ through reinforcement. Prior inertia is not identified as irrational dogmatism or obligation."},
        {"id": "H4", "status": "NOT_MODELED", "evidence": "v7/evidence/handoffs/06-postfreeze.json",
         "finding": "No institutional teaching-access/evaluator bundle was implemented."},
        {"id": "H5", "status": "PARTIAL; FINITE ONLY", "evidence": "corrected/discovery.csv.gz; corrected/corrected_evolution.csv.gz",
         "finding": "Corrected ecology and paired T=80 descendants can describe regime-dependent finite outcomes; no attractor, direct competition, rare-mutant exponent, or asymptotic selection assay ran."},
        {"id": "H6", "status": "PARTIAL", "evidence": "persistence.csv.gz; postfreeze_yoked.csv.gz",
         "finding": "B/K/T/H are exported separately, adult direct override is off, and corrected asocial sentinels are estimable; ecological competence-independence was not identified."},
        {"id": "H7", "status": "UNRESOLVED; METAREASONING EQUIVALENCE NOT TESTED", "evidence": "corrected/holdout.csv.gz; v7/experiments/model.py",
         "finding": "The final execution-priced bounded EVI comparator fixes marginal costs, observes actual remaining time and retains world-level purchase counts, but remains a one-decision algorithm under common Q0. No global-planner/general-RL equivalence or specialized-adaptation result is established."},
        {"id": "H8", "status": "PARTIAL; PROVENANCE-SATURATION TEST NOT RUN", "evidence": "kernel.json; v7/evidence/executed_checks.json",
         "finding": "R4 now executes the independent/copied by visible/hidden-provenance cognitive factorial with acquired tutor histories and exact likelihood enumeration. Ecological cross-root attribution and a provenance-saturation fitness experiment remain untested."},
        {"id": "H9", "status": "DIAGNOSTIC PARTIAL; CAUSAL CLAIM NOT TESTED", "evidence": "corrected/corrected_h9.csv.gz",
         "finding": "The corrected primary diagnostic remains shock/K erasure at d0. Additional closed-resource and naive-restart controls now test actual carrier death/removal and costed artifacts. They do not test root diversity by deference mediation or prove monoculture debt."},
    ]


CHECK_STATUS = {
    "AUTH-01": "partial", "AUTH-02": "passed", "AUTH-03": "passed", "INHERIT-01": "partial",
    "FOUNDER-01": "partial", "COMP-01": "partial", "BUDGET-01": "partial", "TASK-01": "partial",
    "ACCUM-01": "partial", "ACCUM-02": "passed", "PROV-01": "partial", "CLASS-01": "partial",
    "MATURITY-01": "partial", "LEDGER-01": "passed", "TEACH-01": "partial", "GROWTH-01": "passed",
    "INVASION-01": "partial", "INVASION-02": "partial", "NORM-01": "partial", "NORM-02": "partial",
    "RNG-01": "partial", "HIDDEN-01": "partial", "RISK-01": "not_run", "COND-01": "partial",
    "EXPORT-01": "passed",
}

CHECK_BASIS = {
    "AUTH-01": "Kernel isolation is consistent with conflict-only override, but the registered ecological decision-level bitwise B/K/T/H/budget audit was not exported.",
    "AUTH-02": "R4 crosses genuinely randomized uninformative labels with label-neutral, generic-source and imposed authority-sensitive policies, identical acquired tutor histories and common draws. Unconditional and conflict contrasts are exported. This is a mechanism assay, not evolved authority sensitivity.",
    "AUTH-03": "R4 runs the full joint-exposure memory-acceptance (0/1) by immediate override (0/.5) factorial with blank states, acquired B/K/T/H, actual budgets, actions and twenty adult reuse steps; adults have zero inherited override. Memory intervention changes storage, not cognitive capacity.",
    "INHERIT-01": "Births blank B/K/T/H and transmit genotype only; no cross-fostering/full relabel audit.",
    "FOUNDER-01": "Blank initialization is tested in fixtures, not all registered founder cultures and failed burn-ins.",
    "COMP-01": "ExactTinyPOMDP validates only a restricted two-episode toy; IBM Q0 is greedy, FeatureTrust is action-blind, and Candidate B is approximate with mismatched evaluated/executed query accuracy. The overlay repairs the asocial local oracle but does not create a strong general-RL or optimal-planning comparator.",
    "BUDGET-01": "The final resource_control enforces4 tokens/person and closed energy/resource budgets with24 equal-realized-work pairs. The final execution_planner charges12 common abstract deliberation units and actual incremental fees. Global-optimal learner matching and the old pooled upper bound remain unsupported.",
    "TASK-01": "Tiny and cognitive landscapes have partial alternatives/coverage; full ensemble and causal prerequisite robustness are incomplete.",
    "ACCUM-01": "The R4 eight-node DAG adds actual branching/recombination, receipt genealogies, held-out physical tests and fresh exactly equal-work pairs. Its solo-protocol energy bound excludes independent completion. Paid two-edge transfer passes23/24; private-only/no-retention/no-bootstrap controls produce no complete programs. Prerequisite scramble has identical endpoints and no separate modification-disabled control ran, so full causal-ablations criterion remains partial.",
    "ACCUM-02": "The final carrier_control removes all people, restarts ten blank agents with audited external energy, disables innovation, and tests costed artifacts on/off over24 fresh pairs. Off retains no recipe; recovered on-origins trace to paid artifacts. This is an intervention, not natural growth.",
    "PROV-01": "R4 blank tutors acquire independent .8 private histories; copied testimony shares an actual physical root. Exact enumeration verifies same-root duplication invariance and independent versus explicit hidden-mixture posteriors. The broader ecological merged-root implementation and attribution remain partial.",
    "CLASS-01": "Schema and grid classes are explicit; sampled-grid classification is descriptive and not a general surface recovery test.",
    "MATURITY-01": "Age threshold tau=5 and adult genetic override off are tested; full life-course confound audit is incomplete.",
    "LEDGER-01": "Material/time ledgers and residual checks pass across frozen and fresh corrected exports.",
    "TEACH-01": "Teacher eligibility is age-neutral, but the never-updated ranking key resolves by identity and the lexical-first K offer creates a second order artifact; updated performance selection is absent.",
    "GROWTH-01": "Mean N and per-agent-season net resource are exported separately with no scalar-growth relabeling.",
    "INVASION-01": "Fresh corrected paired neutral-tag finite descendants ran, but not rare-mutant growth or direct competition.",
    "INVASION-02": "Fresh corrected finite directional contrasts ran; no ESS, fixation, or stable-polymorphism identification.",
    "NORM-01": "The final belief_control trains blank learners on a fixed proposition, clones actual states, and gives matched-direction evidence/audience/cost controls under static/switching priors. Factual updating is likelihood-aware; no irrational dogmatism is established. Full normative/source-asymmetry probes remain absent.",
    "NORM-02": "Audience/reward probes exist in a separate process; obligation and novel-context injunction were not modeled.",
    "RNG-01": "Frozen and corrected replay identities/source snapshots pass, but common-random-number verification is narrower than full registered event identity audits.",
    "HIDDEN-01": "The frozen behavioral path fails because a phantom tutor equals hidden z. The separately registered three-method overlay passes the same adversarial no-teacher probe, while broader policy/world truth-firewall coverage remains partial.",
    "RISK-01": "No low-density random-projection or branching-growth validation was run.",
    "COND-01": "Primary denominators are preserved. execution_planner adds actual whole-world initial-arbitration purchase/no-teacher/conflict counts, including dead actors; real juvenile label controls retain opportunity denominators. Independent information-history and demographic-ITT claims remain limited.",
    "EXPORT-01": "Reporting tests recompute frozen and corrected hashes, row counts, corrected paired contrasts, all 25 statuses, finite-claim guards, and both frozen-defect/corrected-path probes.",
}


def executed_checks(inventory: dict[str, dict[str, Any]],
                    corrected_inventory: dict[str, dict[str, Any]] | None = None,
                    software_test: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    registered = json.loads((EVIDENCE / "predeclared_checks.json").read_text())["checks"]
    claims = {item["id"]: item["claim_guarded"] for item in registered}
    test_hash = sha256(V7 / "tests" / "test_reporting.py")
    source_hash = sha256(V7 / "synthesize_results.py")
    test_command = "python -m unittest discover -s v7/tests -p 'test_*.py'"
    defect_path = EVIDENCE / "frozen_local_no_teacher_defect.json"
    corrected_path = EVIDENCE / "corrected_local_no_teacher_audit.json"
    quality_path = EVIDENCE / "data_quality.json"
    records = []
    for check_id in CHECK_STATUS:
        evidence = [{"path": "v7/tests/test_reporting.py", "sha256": test_hash},
                    {"path": "v7/synthesize_results.py", "sha256": source_hash}]
        if defect_path.exists() and check_id in {"COMP-01", "HIDDEN-01", "COND-01", "EXPORT-01"}:
            evidence.append({"path": str(defect_path.relative_to(ROOT)), "sha256": sha256(defect_path)})
        if corrected_path.exists() and check_id in {"COMP-01", "HIDDEN-01", "COND-01", "EXPORT-01"}:
            evidence.append({"path": str(corrected_path.relative_to(ROOT)), "sha256": sha256(corrected_path)})
        if quality_path.exists() and check_id in {"LEDGER-01", "GROWTH-01", "RNG-01", "COND-01", "EXPORT-01"}:
            evidence.append({"path": str(quality_path.relative_to(ROOT)), "sha256": sha256(quality_path)})
        for extra in {
            "ACCUM-02": ["carrier_control/registration.json", "carrier_control/summary.json"],
            "ACCUM-01": ["cumulative_dag/registration.json", "cumulative_dag/summary.json", "cumulative_dag_matched/summary.json"],
            "BUDGET-01": ["resource_control/summary.json", "execution_planner/summary.json"],
            "COMP-01": ["execution_planner/registration.json", "execution_planner/summary.json"],
            "NORM-01": ["belief_control/registration.json", "belief_control/summary.json"],
            "AUTH-02": ["information_controls/registration.json", "information_controls/summary.json"],
            "AUTH-03": ["information_controls/registration.json", "information_controls/summary.json"],
            "PROV-01": ["information_controls/summary.json"],
            "COND-01": ["execution_planner/summary.json"],
        }.get(check_id, []):
            ep = EVIDENCE / extra
            if ep.exists():
                evidence.append({"path": str(ep.relative_to(ROOT)), "sha256": sha256(ep)})
        command = "python v7/synthesize_results.py --verify-only" if check_id == "EXPORT-01" else test_command
        records.append({
            "id": check_id, "scientific_status": CHECK_STATUS[check_id], "claim_guarded": claims[check_id],
            "basis": CHECK_BASIS[check_id], "command": command, "evidence": evidence,
            "raw_artifact_hashes": {
                "frozen_invalidated": {k: v["sha256"] for k, v in inventory.items()},
                "corrected_primary": {k: v["sha256"] for k, v in (corrected_inventory or {}).items()},
            },
            "software_test_result": ({"exit_code": software_test["returncode"],
                                      "status": software_test["status"]}
                                     if software_test else {"status": "not_recorded_in_this_call"}),
        })
    return records


def build_evidence_summary() -> dict[str, Any]:
    frozen_inventory = artifact_inventory()
    corrected_inventory = corrected_artifact_inventory()
    corrected_freeze_path = CORRECTED_EVIDENCE / "freeze_variant" / "manifest.json"
    corrected_freeze = json.loads(corrected_freeze_path.read_text())
    corrected_holdout_rows = read_corrected_rows("holdout")
    corrected_evolution_rows = read_rows_from(CORRECTED_OUT, "corrected_evolution")
    corrected_evolution_result = json.loads(
        (CORRECTED_EVIDENCE / "corrected_evolution_result.json").read_text())
    corrected_h9_rows = read_rows_from(CORRECTED_OUT, "corrected_h9")
    selected_diagnostics = ["vector_0_0", *corrected_freeze["frozen_vectors"]]
    corrected_selection = selection_summary(
        corrected_evolution_rows, seed_start=79001, seed_max=79096)
    registered_selection_contrasts = corrected_evolution_result["summary"]["paired_contrasts"]
    corrected_selection.update({
        "runner_status": corrected_evolution_result["status"],
        "registered_precision_rule": (
            "all 12 paired descendant MCSE values <=0.25 and all 24 arm-level "
            "establishment Wilson half-widths <=0.10"
        ),
        "runner_unresolved": corrected_evolution_result.get("unresolved", []),
        "gate_status": corrected_evolution_result["gates"]["status"],
        "maximum_paired_descendant_mcse": max(
            item["paired_descendant_difference_mcse"]
            for item in registered_selection_contrasts.values()),
        "maximum_establishment_wilson_half_width": max(
            item["max_establishment_wilson_half_width"]
            for item in registered_selection_contrasts.values()),
    })
    return {
        "schema_version": 1, "generated_utc": datetime.now(timezone.utc).isoformat(),
        "primary_evidence": "corrected_overlay",
        "scientific_verdict": "PARTIAL_WITH_CORRECTED_PRIMARY_AND_FROZEN_INVALIDATION",
        "software_reproducibility_verdict": "PASS_PENDING_FINAL_TEST_RECORD",
        "core_freeze": {"replay_digest": "94467195bc1f6dcb9f20983f91ec3e86bad9c02845790979f802fa9d6ac1a070",
                        "verification": "v7/evidence/postfreeze_freeze_verification.json"},
        "frozen_inventory": frozen_inventory,
        "corrected_inventory": corrected_inventory,
        "corrected_freeze": corrected_freeze,
        "corrected_freeze_sha256": sha256(corrected_freeze_path),
        "tiny_exact": tiny_exact_summary(),
        "frozen_local_no_teacher_defect": frozen_local_no_teacher_audit(),
        "corrected_local_no_teacher_audit": corrected_local_no_teacher_audit(),
        "data_quality": corrected_data_quality(corrected_inventory),
        "discovery": discovery_summary(read_corrected_rows("discovery")),
        "holdout": holdout_summary(
            corrected_holdout_rows,
            read_corrected_rows("depth_reliability_control"),
            diagnostic_policies=selected_diagnostics,
        ),
        "selection": corrected_selection,
        "extensions": extension_summary(read_rows("persistence"), read_rows("cumulative_assay"),
                                        corrected_h9_rows),
        "hypotheses": hypothesis_ledger(),
        "interpretive_limits": [
            "d=0 is ordinary social learning, not asocial or fully deferential.",
            "tau=5 is a fixed age threshold and differs from V1-V6 exponential maturation means; tau was not optimized.",
            "The IBM Q0 is a greedy whole-procedure posterior proxy without a two-episode continuation term; ExactTinyPOMDP is a separate reduced toy.",
            "FeatureTrust predicts reward from source features without action input; Candidate B remains approximate and charges a declared procedure opportunity proxy.",
            "The procedural teacher-ranking key is never updated, leaving an identity-order tie; the offer is the lexical first eligible K sequence, not chosen from updated B or predicted performance.",
            "Population N, per-agent-season net resource, and conditional finite descendants are different estimands.",
            "Frozen no-tutor local decisions contain a confirmed phantom-oracle defect; their ecology and lineage exports are invalidated rather than mixed with the fresh corrected-primary results.",
            "The corrected overlay changes only the three no-teacher local methods; it does not repair lexical teacher selection, action-blind FeatureTrust, Candidate-B evaluator/execution mismatch, or missing purchase/event counts.",
            "Corrected outcomes remain finite, conditional simulation results and do not identify significance, equivalence, biological adaptation, invasion fitness, ESS, fixation, or stable polymorphism.",
        ],
    }


def num(value: float, digits: int = 6) -> str:
    return "NA" if not math.isfinite(value) else f"{value:.{digits}f}"


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines.extend("| " + " | ".join(str(x) for x in row) + " |" for row in rows)
    return "\n".join(lines)


def render_results(s: dict[str, Any]) -> str:
    h = s["holdout"]
    selected = [x for x in h["contrasts"] if x["policy"] == "vector_0_5_0"]
    primary_n = s["discovery"]["primary_mean_population_contrasts"]
    grid = s["discovery"]["class_specific_grid"]
    selection = s["selection"]["contrasts"]
    h9 = s["extensions"]["h9"]["regime_arms"]
    selected_net_range = (min(x["mean_delta"] for x in selected),
                          max(x["mean_delta"] for x in selected))
    selected_n_range = (min(x["population_mean_delta"] for x in selected),
                        max(x["population_mean_delta"] for x in selected))
    lifecycle = [x for x in h["contrasts"]
                 if x["policy"] == "vector_0_5_0" or x["policy"] == "asocial_access_off"]
    return f"""# V7 Results: Costly Cultural Competence

## Scientific verdict

**PARTIAL, WITH A CORRECTED OVERLAY AS PRIMARY EVIDENCE.** An adversarial audit invalidated the original frozen ecology because a no-teacher local path could use hidden `z`. The original bytes and raw exports remain a reproducible failure trail. A separately registered three-method overlay removes that path, passed the same adversarial probe, was frozen before candidate holdout, and generated fresh discovery, holdout, depth-control, H9, and finite-lineage data.

In the corrected nine-regime holdout, selected vector `(d_procedure=.5,d_local=0)` minus ordinary spans {num(selected_net_range[0])} to {num(selected_net_range[1])} in net stock change per agent-season and {num(selected_n_range[0],3)} to {num(selected_n_range[1],3)} in mean population. These small, sign-changing net-resource differences are **not** an equivalence result or proof of no fitness/performance effect. The net metric is a regulated endpoint-stock residual divided by agent-seasons; values near zero are expected near stock balance and cannot substitute for population, births/deaths, or T=80 descendants.

The strongest defensible result is conditional: local override is often associated with lower exploratory mean N, the held-out selected vectors remain close to ordinary on net resource but not identical on every outcome, the repaired asocial sentinels exceed ordinary on both N and net resource in the three tested regimes, and the implemented learned/metareasoning heuristics have lower net resource than ordinary. The asocial comparison applies to this simple task and its priced cultural-access route; it is not evidence that asociality generally improves demography. None establishes biological adaptation, a unique optimum, specialized authority cognition, general-RL necessity, or Bayes-optimal planning.

## What was known, changed, and observed

- `d=0` is ordinary social learning; `asocial_access_off` separately removes cultural access while retaining private hardware. The corrected no-teacher path exposes only the private action at its actual expected value `2.0`.
- The IBM Q0 is a greedy whole-procedure posterior proxy over enumerated returns. It has no two-episode future-learning continuation. `ExactTinyPOMDP` is a separate reduced two-episode theta/z oracle and bounds only its matched tiny restricted policy.
- FeatureTrust is an action-blind reward heuristic. Candidate B is a current-decision approximation whose query evaluator uses source calibration but whose executed query draw uses fixed `.80`; purchase counts were not exported, so realized information-use frequency is unavailable. It is not verified optimal, nonmyopic, or fully resource-rational.
- Teacher eligibility is recorded and age-neutral, but the procedural ranking key is never updated and therefore resolves by identity; the offered procedure is the lexical first eligible K sequence—not one selected from updated B or predicted performance. Teacher/content order is therefore a live rival explanation.
- Births inherit genotype only and begin with blank acquired B/K/T/H; adult direct genetic override is off at fixed `tau=5`. Tau was not optimized and is not the V1–V6 exponential maturation mean.
- The fresh corrected holdout has 1,368 rows, 24 seeds per cell, and no extinction/cap events. Every comparison is conditional on the implemented task and policy classes.

### Frozen defect and bounded correction

`v7/evidence/frozen_local_no_teacher_defect.json` reproduces the original hidden oracle. `v7/evidence/corrected_local_no_teacher_audit.json` shows that the overlay removes `teacher` from feasible actions, makes the placeholder equal the private cue, and physically executes that cue. Teacher-present methods delegate to the frozen base. Registration-time source snapshots, a pre-holdout freeze, fresh seed partitions, and matching live/result hashes provide the durable controls against cached rescoring or favorable retuning. File-mode changes used operationally during workers were not captured in a durable artifact and are not part of this evidentiary claim.

### Exact reduced benchmark versus stochastic estimate

The separate two-episode tiny oracle has enumerated Bellman value {num(s['tiny_exact']['exact_enumerated_value'])} and selects `{s['tiny_exact']['exact_first_action']}` first. The matched restricted policy's stochastic estimate is {num(s['tiny_exact']['restricted_monte_carlo_value'])} ± {num(s['tiny_exact']['restricted_monte_carlo_mcse'])} MCSE over {s['tiny_exact']['restricted_replicates']} replicates; the observed exact-minus-restricted difference is {num(s['tiny_exact']['exact_minus_restricted'])}. The exact value has enumeration/numerical, not Monte Carlo, uncertainty. The MCSE belongs only to the restricted simulation. This confirms the upper-bound relation inside the matched tiny toy and says nothing about full-IBM optimality or an ecological advantage.

## Corrected exploratory discovery: d=0 to d=1 effects on mean N

The corrected 504-row grid uses four paired seeds per cell. Procedure-only is `(0,0)->(1,0)`, local-only is `(0,0)->(0,1)`, and scalar diagonal is `(0,0)->(1,1)`. MCSE is across the four paired seed differences. The L9 environmental design aliases interactions, so these are exploratory contrasts, not tests of a continuous response surface.

{md_table(['regime','contrast','candidate','mean ΔN','paired MCSE','range','n'], [[e['regime'],e['contrast'],e['candidate'],num(e['mean_delta_N'],4),num(e['paired_mcse'],4),f"{num(e['min_delta_N'],3)}..{num(e['max_delta_N'],3)}",e['n_pairs']] for e in primary_n])}

### Class-specific sampled tops, ties, and boundaries

The objective in this table is **mean population**, separately within vector, scalar-restriction, and comparator classes. “Compatible” means within two paired MCSE of the sample-mean top on the sampled grid; it is not a confidence set, equivalence set, continuous optimum, or ESS. Candidate freezing used a different predeclared objective—pooled discovery net resource—and selected vectors `(.5,0)` and `(1,0)` plus scalar `.25`; it did not choose a joint interior point.

{md_table(['regime','class','sample-mean top','mean N','within 2 MCSE','boundary'], [[g['regime'],g['class'],g['sample_mean_top'],num(g['mean_population'],3),', '.join(g['two_mcse_compatible']),g['sampled_boundary_class']] for g in grid])}

## Corrected fresh held-out policy contrasts

Rows are within-seed candidate-minus-ordinary contrasts. Both outcomes are shown because mean N and net stock change per agent-season are different estimands. Asocial access-off was registered only at regimes 1, 5, and 9.

{md_table(['regime','candidate','Δ mean N','N MCSE','Δ net stock/agent-season','net MCSE','n'], [[x['regime'],x['policy'],num(x['population_mean_delta'],3),num(x['population_paired_mcse'],3),num(x['mean_delta']),num(x['paired_mcse']),x['n_pairs']] for x in h['contrasts']])}

Whole-run birth/death flux can compensate while mean N or retained stock differs. For the focal selected vector and the registered asocial sentinels, the paired lifecycle diagnostics are:

{md_table(['regime','candidate','Δ births','birth MCSE','Δ deaths','death MCSE'], [[x['regime'],x['policy'],num(x['birth_flux_mean_delta'],3),num(x['birth_flux_paired_mcse'],3),num(x['death_flux_mean_delta'],3),num(x['death_flux_paired_mcse'],3)] for x in lifecycle])}

The fresh 288-row depth-aware source-calibration control remains numerically close to ordinary at the three sentinels. It is a routine-capacity calibration control, not an optimized policy or causal explanation:

{md_table(['regime','mean Δ net resource','paired MCSE','n'], [[x['regime'],num(x['mean_delta']),num(x['paired_mcse']),x['n_pairs']] for x in h['depth_aware_control']])}

Revision, override, and action-accuracy diagnostics use variation across the 24 independent seeds for MCSE. Wilson precision remains **UNRESOLVED** because event numerator/denominator counts were not exported; treating recorded rates as independent Bernoulli trials would be pseudo-replication.

## Corrected finite paired lineage assay

The fresh raw export contains {s['selection']['registered_raw_rows']} arm rows; {s['selection']['completed_batch_rows']} belong to complete fixed batches and {s['selection']['excluded_incomplete_batch_rows']} are retained but excluded from precision. Paid-birth rows: {s['selection']['paid_birth_rows']}; no-birth censored: {s['selection']['no_birth_censored']}; cap-censored: {s['selection']['cap_censored']}; finite-extinction arm rows: {s['selection']['extinction_rows']}. Contrasts are mutant minus neutral-tag living descendants at T=80:

{md_table(['regime','directed pair','mean Δ descendants','paired MCSE','zero Δ','n paid pairs'], [[x['regime'],x['directed_pair'],num(x['mean_delta_living_descendants'],3),num(x['paired_mcse'],3),x['zero_delta_count'],x['n_pairs']] for x in selection])}

Runner precision status: **{s['selection']['runner_status']}**. The registered stop rule required {s['selection']['registered_precision_rule']}. The realized maxima were {num(s['selection']['maximum_paired_descendant_mcse'],3)} for paired descendant MCSE and {num(s['selection']['maximum_establishment_wilson_half_width'],3)} for arm-level Wilson half-width. A status of `UNRESOLVED` means the maximum registered seeds were exhausted without meeting both criteria; it does not license a result-dependent extension or removal of a noisy contrast.

These are finite conditional carrier outcomes—not p-values, equivalence tests, direct competition, rare-mutant asymptotic invasion, fixation, ESS, stable polymorphism, or proof of an attractor.

## Post-freeze mechanisms and negative controls

- **Adult persistence/H3:** 120 rows from a separate generic reinforcement process show learned action-value persistence alongside factual revision. The probe metadata says 20 intervention seasons, but the code does not simulate 20 sequential intervention updates. The “bidirectional” label does not implement symmetric evidence directions. This is action habit, not private-belief dogmatism; dogmatism is NULL/unsupported and obligation is unsupported.
- **Adult yoked access/H6:** 648 same-history decisions confirm direct adult genetic override is zero at age 7. This is a decision assay, not a demographic or selection effect.
- **Cumulative cognitive assay:** the corrected 144 fresh rows use seeds 74601–74624 and equal aggregate work 360/material 3.6 per arm. It remains cognitive-only. Its ideal pooled upper bound can assign private work above the per-person budget and compensating negative safe work, so it is not a feasible individual-budget comparator. Similar shuffled-prerequisite performance weakens a prerequisite-causality interpretation.
- **H9:** fresh corrected d=0 cloned states receive a theta shock and optional K/independent-success erasure. The mixed N/K summaries below are diagnostic only; this is not carrier death, root-diversity loss, d-by-shock mediation, or functional recovery time.

{md_table(['regime','arm','mean N','N MCSE','mean post K','K MCSE','K removed'], [[x['regime'],x['arm'],num(x['mean_population'],3),num(x['population_across_seed_mcse'],3),num(x['mean_post_stored_procedures'],3),num(x['post_stored_procedures_across_seed_mcse'],3),x['removed_procedures']] for x in h9])}

## Hypotheses

{md_table(['hypothesis','status','finding'], [[x['id'],x['status'],x['finding']] for x in s['hypotheses']])}

## What survived controls—and what did not

Mechanically verified: frozen replay `94467195...a070`; corrected replay `{s['corrected_freeze']['replay']['replay_digest']}`; frozen-source preservation; corrected source snapshots; raw hashes/row counts; blank acquired birth state; adult override-off at age 5+; ledger closure; paired births; and report recomputation from raw gzip. The corrected no-teacher path, not the frozen one, is the primary ecology implementation.

Supported only conditionally: corrected simulated outcome contrasts for the implemented policies, environments, costs, and finite horizons. Unsupported: biological adaptation, a unique continuous optimum, no-advantage/equivalence claims from near-zero net stock, generalized RL, Bayes-optimal or fully resource-rational planning, private-belief dogmatism, obligation, deference-caused demographic cumulative culture, carrier-loss/root-diversity fragility, institutional mechanisms, or asymptotic selection.

No substantive behavioral mechanism was shown to be necessary. The three-method overlay is necessary for software-valid no-teacher behavior, but the remaining outcome contrasts do not isolate cultural access cost, lexical content order, override, acquired belief, and demographic feedback from one another. In particular, lower performance of the implemented FeatureTrust/Candidate-B heuristics does not prove that stronger action-conditional learning or planning is unnecessary.

## Estimands and formulas

- `mean_population`: arithmetic mean of `population_next` over every simulated season, including burn-in (normally all 240 seasons).
- `net_energy_per_agent_season = (resource_final + sum(living_energy_final) - initial_total_stock) / sum_t population_next_t` over the full horizon including burn-in. It is a retained-stock residual per agent-season, not population N, birth/death balance, task performance, or lineage fitness.
- Held-out contrasts: within-seed candidate minus ordinary, then mean and sample-SD/√n across independent seeds.
- Selection contrast: within seed/regime/directed-pair mutant minus neutral-tag living descendants at season 80.
- Rate diagnostics: mean and sample-SD/√24 across seeds only.

All tables are regenerated from raw gzip exports by `python v7/synthesize_results.py --write`. Frozen invalidated values remain in the project manifest and failure audit, not mixed into corrected primary tables.
"""


def render_verification(s: dict[str, Any], checks: list[dict[str, Any]]) -> str:
    counts = {status: sum(c["scientific_status"] == status for c in checks) for status in ("passed", "partial", "not_run")}
    rows = [[c["id"], c["scientific_status"], c["basis"]] for c in checks]
    corrected = s["corrected_inventory"]
    frozen = s["frozen_inventory"]
    return f"""# V7 Verification

## Outcome

Software/replay verification: **PASS WITH ONE EXPECTED FROZEN-DEFECT FAILURE AND A PASSING CORRECTED-PATH REGRESSION**. Scientific requirement completion remains **PARTIAL** ({counts['passed']} passed, {counts['partial']} partial, {counts['not_run']} not run across all 25 predeclared checks). The frozen failure is preserved; only the fresh corrected-overlay outputs are primary ecology evidence.

## Executed commands

```text
python -m unittest discover -s v7/tests -p 'test_*.py'
python v7/synthesize_results.py --verify-only
python v7/experiments/run_postfreeze.py --verify-freeze --manifest v7/evidence/core_freeze/manifest.json
python v7/experiments/run_corrected_experiments.py --stage discovery
python v7/experiments/run_corrected_experiments.py --stage freeze
python v7/experiments/run_corrected_experiments.py --stage holdout
python v7/experiments/run_corrected_experiments.py --stage depth-control
python v7/experiments/run_corrected_experiments.py --stage h9
python v7/experiments/run_corrected_evolution.py --max-seed 96
```

The frozen check reproduced `94467195bc1f6dcb9f20983f91ec3e86bad9c02845790979f802fa9d6ac1a070`; frozen bytes were deliberately not repaired. Corrected discovery has a registration-time source snapshot, and freeze `{s['corrected_freeze_sha256']}` with replay `{s['corrected_freeze']['replay']['replay_digest']}` was written before holdout. Final live source hashes match the registrations and result records. Operational file-mode guards were not durably captured, so verification does not claim them. `frozen_local_no_teacher_defect.json` and `corrected_local_no_teacher_audit.json` retain both sides of the audit.

## Corrected primary export parity

{md_table(['artifact','rows','sha256'], [[name,item['rows'],item['sha256']] for name,item in corrected.items()])}

Machine data-quality status: **{s['data_quality']['status'].upper()}** across {len(s['data_quality']['checks'])} grain, row-count, seed, finiteness, result-hash, batch-volume, and registered-source checks.

## Frozen invalidated archive parity

{md_table(['artifact','rows','sha256'], [[name,item['rows'],item['sha256']] for name,item in frozen.items()])}

## Predeclared scientific checks

{md_table(['ID','status','evidence-based disposition'], rows)}

Machine-readable records, including commands, exit status, evidence paths/hashes, corrected and frozen raw hashes, and claim consequences, are in `v7/evidence/executed_checks.json`. Wilson precision for action/revision/success rates remains unresolved because event numerators/denominators were not exported; their MCSE is across seeds only.
"""


def render_manuscript() -> str:
    return """# Manuscript Outline: Costly Cultural Competence V7

## Working title

**Correcting a Hidden-Oracle Control in a Costly Cultural-Learning IBM**

## Paper-level claim

V7 separates inherited juvenile conflict override from acquired factual belief, procedures, source calibration, and learned action value. An adversarial audit found a hidden oracle in the frozen no-teacher local path, invalidating its ecology. A separately registered three-method overlay repaired only that path and generated fresh evidence. The corrected results are regime- and estimand-dependent: local override often lowers exploratory mean N; selected vectors remain numerically close to ordinary on a retained-stock metric; repaired asocial sentinels are higher than ordinary in the three registered regimes under implemented pricing; and finite T=80 descendant contrasts do not identify asymptotic selection.

## Abstract structure

1. Problem: cultural-learning models often conflate inherited policy, acquired content, source reliability, and behavior.
2. Audit/correction: reproduce the frozen oracle; preserve frozen bytes/raw; snapshot and freeze the minimal corrected overlay before fresh holdout.
3. Method: paid information/computation, blank newborn acquired state, age-neutral teacher eligibility, fixed juvenile threshold, 504-row discovery, 1,368-row holdout, depth control, reduced exact benchmark, and paired finite descendants.
4. Result: report mean N, retained-stock, and T=80 descendants separately, with paired seed MCSE and unconditional zero/cap/no-birth denominators.
5. Interpretation: conclusions apply only to implemented policies and finite environments; no biological adaptation, equivalence, optimality, or ESS claim follows.

## Figures and tables

1. Construct diagram: genotype d → juvenile conflict override; acquired B/K/T/H; blank birth; lexical-first eligible K offer flagged.
2. Corrected discovery regime map: procedure-only, local-only, and scalar-diagonal mean-N contrasts; class-specific sampled tops/ties/boundaries.
3. Corrected holdout forest plots: paired Δ mean N and Δ retained-stock/agent-season versus ordinary; asocial sentinels distinct.
4. Adult/developmental checks: override off at tau=5 and generic action habit versus factual revision.
5. Corrected finite-lineage table: raw/completed-batch/paid-birth/no-birth/cap/extinction denominators and T=80 paired living descendants.
6. Frozen-invalidated versus corrected-primary provenance and H1–H9/check ledgers.

## Methods sections

- Frozen core, invalidating probe, corrected overlay, registration-time snapshots, seed partitions, and pre-holdout freeze.
- Task/reward equations and exact tiny-world scope.
- Ordinary, vector/scalar, action-blind FeatureTrust, and approximate Candidate B policy classes.
- Resource ledgers, birth state, teacher eligibility, and lexical offer limitation.
- Discovery L9 aliasing, distinct N/retained-stock estimands, held-out pairing, across-seed MCSE, and unresolved event-rate Wilson counts.
- Finite selection endpoint and why it is not invasion/ESS.
- Separate post-freeze persistence, cumulative cognitive, and H9 diagnostics.

## Discussion order

1. Why typed observation boundaries were insufficient and the frozen path was invalidated.
2. Why minimal correction plus fresh data is stronger than rescoring or silently rewriting the archive.
3. Why near-zero retained-stock contrast is not equivalence, fitness, or performance.
4. Why action-blind reward prediction and approximate EVI do not test strong general RL or optimal planning.
5. Why action habit is not private-belief dogmatism, d=0 is social, and H9 is not carrier/root-diversity manipulation.
6. What a stronger study must export and experimentally manipulate.

## Claims permitted

- Construct-separated implementation, reproducible invalidation, and a minimal source-snapshotted correction.
- Corrected conditional contrasts for mean N, retained stock per agent-season, and finite descendants.
- Exploratory regime dependence and sampled class-specific compatibility without a global optimum.
- Partial generic learned-action persistence with factual revision.

## Claims prohibited

General policy benefit or absence of benefit, first-model novelty, biological adaptation, specialized authority cognition, generalized reinforcement learning, full Bayes-optimal/resource-rational planning, dogmatism, docility, obligation, cumulative demographic complexity, carrier-loss/root-diversity fragility, equivalence, invasion fitness, ESS, fixation, or stable polymorphism.

The literature audit is targeted rather than systematic; novelty language must remain qualified.
"""


def render_readme() -> str:
    return """# V7 Costly Cultural Competence

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
"""


def render_gaps() -> str:
    return """# Research Gaps and Next Steps

## Highest-priority scientific gaps

1. Extend verified final world-level purchase/no-teacher/conflict counts to the full historical selection flow and independent-information provenance; preserve seed-cluster precision rather than pool correlated decisions.
2. Replace lexical-first teacher content with a preregistered content-selection rule, retaining lexical order as a negative control.
3. Extend the execution-priced one-decision comparator to a flexible, provenance-aware learned policy with equally priced training and a longer planning horizon. The final bounded comparator does not establish global RL equivalence.
4. Extend the completed R4 role-label and memory-acceptance × conflict-override assays into shared ecological competition. An imposed authority-sensitive positive control does not establish evolution of specialized cognition.
5. Generalize the completed eight-node DAG beyond its declared solo-acquisition protocol; add a modification-disabled comparator and policies sensitive to scrambled prerequisites. The current positive accumulation control does not establish that extra deference causes accumulation.
6. If selection is the target, run direct competition/rare-mutant assays with ancestry-aware uncertainty. Do not infer ESS or stable polymorphism from T=80 descendants.
7. Cross the implemented carrier-loss/artifact controls with actual root diversity, environmental shock and inherited d. The naive-restart memory assay is not a test of deference-mediated monoculture debt.
8. Independently replicate the corrected overlay outcomes before treating discovery-selected boundaries or asocial sentinels as robust scientific patterns.

## Dashboard handoff: eight honest views

| View | Supported fields | Coverage | Required replay or gap |
|---|---|---|---|
| Decision microscope | representative actions, rewards, features, operation counts | partial | Observationally replay the frozen corrected overlay to export one real interaction's private signal, offer, conflict, pre/post B/K/T/H, Q0 components, and evaluator truth; require unchanged replay digest and never synthesize fields. |
| Policy map | corrected policy, regime, mean N, retained-stock metric, revision/override/action rates | corrected primary/partial | Keep rate Wilson precision and no-teacher exposure counts gray/missing. |
| Regime map | corrected nine regimes, exploratory and holdout cells | corrected primary/partial | Display L9 aliasing, discovery/holdout split, selection objective, and sampled-class boundaries. |
| Life course | corrected juvenile/adult aggregate counts, fixed tau=5 | partial | Replay corrected age-indexed B/K/T/H, exposure, conflict, and energy records. |
| Genealogy | biological/cultural edge totals and finite descendant trajectories | partial | Export edge-level teacher/root/procedure genealogy before claiming provenance mixtures. |
| Intervention | persistence probes, corrected H9 arms, cumulative arms | supported with construct limits | Label separate-process versus corrected-core interventions; do not call H9 carrier death. |
| Evolution | corrected born ID, parent, pair, T=80 descendants, frequency trajectory | finite/partial | Gray out invasion exponent, ESS, fixation, and stable-polymorphism fields. |
| Research ledger | H1–H9, 25 checks, commands, hashes | supported | Surface PARTIAL/NOT RUN alongside PASS; never collapse to a software green check. |

## Source formulas

- Mean N: arithmetic mean of `population_next` over the entire simulated horizon, including burn-in (normally 240 seasons).
- Net resource: `(resource_final + sum(living_energy_final) - initial_total_stock) / sum_t population_next_t` over the full horizon including burn-in; a near-zero regulated stock residual is not equivalent population, performance, or fitness.
- Held-out contrast: candidate minus ordinary within seed/regime; uncertainty is SD of paired seed differences divided by √n.
- Finite selection: mutant minus neutral-tag living descendants at season 80 within seed/regime/directed pair.
- Rates: seed-level exported proportions summarized across seeds; no event-level binomial intervals without counts.

## Original replay diagnostics and final-control scope

No-teacher local-event count/chosen channel; Candidate-B query/verification purchase counts; decision-level private signal and outcome; teacher offer and eligible-set order; conflict indicator; pre/post B, K, T, H; action-conditional Q0 components; per-decision time/material debits; revision and cultural-success numerators/denominators; exact procedure/root lineage; newborn cohort acquisition histories; recovery-time event; carrier death and root-diversity state.

Several of these diagnostics are now supplied by separately registered final controls and passive replays; others remain absent. See `final_controls.md` and the canonical reporting registry. Never impute an unavailable diagnostic or promote source-ID distinctness to statistical independence.
"""


EXPECTED_RAW = {
    "discovery": (504, "eeb791fdb8df6f3053479aa90de23e6821f4e5c9f9fe07ade4ada01802064098"),
    "holdout": (1368, "d46e4ebb6e9dc377e83c04f438452d723dac9eaa198828fb0723d9946bdf87bb"),
    "depth_reliability_control": (288, "48755d193b57fc4d4818882c8f8b3522837a51ae60bfffe5ce630d06ae718e2b"),
    "evolution": (1242, "8c3a9dc1cc7efb3890d5a56a6248c58d53dce2d632ba2986823f0fdf7e9d7dc9"),
    "persistence": (120, "90f787821b5ef91d509e066c6c7f97c413bbfabb48bd9a33086f1e18ae522c99"),
    "postfreeze_yoked": (648, "0cdee387a81264e08a08942c9fbc1a056cd57025b178102d3aadef2ae09c2c47"),
    "cumulative_assay": (144, "20da7626013cc43a430604847115ccd421a12cb385c58aca60dd665615def599"),
    "postfreeze_h9_observation": (216, "325c2ecb42e68e1a334759d24bd510e9ad693c4ad2736306deacff09a092cbb4"),
}


def verify_summary(summary: dict[str, Any]) -> None:
    for name, (rows, digest) in EXPECTED_RAW.items():
        observed = summary["frozen_inventory"][name]
        if observed["rows"] != rows or observed["sha256"] != digest:
            raise RuntimeError(f"raw artifact parity failure: {name}: {observed}")
    if summary["tiny_exact"]["sha256"] != "355f59bf240b86511a7a789f30491024cf439ed6adebe5a0a6790b1cfceb9d63":
        raise RuntimeError("tiny exact/kernel artifact parity failure")
    if summary["frozen_local_no_teacher_defect"]["status"] != "CONFIRMED_FROZEN_DEFECT":
        raise RuntimeError("registered frozen local no-teacher defect did not reproduce; reporting must be re-audited")
    if summary["corrected_local_no_teacher_audit"]["status"] != "CORRECTED_PATH_VALIDATED":
        raise RuntimeError("corrected local no-teacher path failed its adversarial regression")
    expected_corrected = {
        "discovery": (504, "ae2e130c08df484d6f6605d59f489886ecc025dcdbec4c89049c7d0306381341"),
        "holdout": (1368, "5956bde27a901f99f6520d3c5d227a6da1069fa3f86d586785ae6f46b383e5e0"),
        "depth_reliability_control": (288, "3badd2572da962f2b48cea6066bed72aed5f2490a0cf7dc15bfc0064c9e041d6"),
        "h9": (216, "058a9ac5fe86dc3c5628039659d05fdd645a0290772879d01ae9002f0feae4a4"),
    }
    for name, (rows, digest) in expected_corrected.items():
        observed = summary["corrected_inventory"][name]
        if (observed["rows"], observed["sha256"]) != (rows, digest):
            raise RuntimeError(f"corrected artifact parity failure: {name}: {observed}")
    selected = [x for x in summary["holdout"]["contrasts"] if x["policy"] == "vector_0_5_0"]
    if (len(selected) != 9 or min(x["mean_delta"] for x in selected) > -0.0009
            or max(x["mean_delta"] for x in selected) < 0.0014):
        raise RuntimeError("corrected held-out selected-vector parity failure")
    sel = summary["selection"]
    if len(sel["contrasts"]) != 12 or sel["completed_batch_rows"] % 192 != 0:
        raise RuntimeError("corrected selection contrast/batch coverage failure")
    if sel["registered_raw_rows"] != summary["corrected_inventory"]["evolution"]["rows"]:
        raise RuntimeError("corrected selection raw denominator mismatch")
    if sel["paid_birth_rows"] + sel["no_birth_censored"] != sel["registered_raw_rows"]:
        raise RuntimeError("selection unconditional denominator failure")
    if summary["data_quality"]["status"] != "passed":
        failed = [x for x in summary["data_quality"]["checks"] if x["status"] != "passed"]
        raise RuntimeError(f"corrected data-quality failure: {failed}")
    if set(CHECK_STATUS) != {x["id"] for x in json.loads((EVIDENCE / "predeclared_checks.json").read_text())["checks"]}:
        raise RuntimeError("predeclared check coverage failure")


def run_tests() -> dict[str, Any]:
    command = ["python", "-m", "unittest", "discover", "-s", "v7/tests", "-p", "test_*.py"]
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return {"command": " ".join(command), "returncode": proc.returncode,
            "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip(),
            "status": "passed" if proc.returncode == 0 else "failed"}


def write_outputs(summary: dict[str, Any]) -> None:
    frozen_inventory = summary["frozen_inventory"]
    corrected_inventory = summary["corrected_inventory"]
    defect_path = EVIDENCE / "frozen_local_no_teacher_defect.json"
    corrected_audit_path = EVIDENCE / "corrected_local_no_teacher_audit.json"
    quality_path = EVIDENCE / "data_quality.json"
    defect_path.write_text(json.dumps(summary["frozen_local_no_teacher_defect"], indent=2) + "\n")
    corrected_audit_path.write_text(json.dumps(summary["corrected_local_no_teacher_audit"], indent=2) + "\n")
    quality_path.write_text(json.dumps(summary["data_quality"], indent=2) + "\n")
    tests = run_tests()
    checks = executed_checks(frozen_inventory, corrected_inventory, tests)
    import sys
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from v7.final_controls import build as build_controls, report as render_controls
    controls = build_controls()
    controls_report = render_controls(controls)
    controls_readme = """

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
"""
    reports = {
        V7 / "results.md": render_results(summary) + controls_report,
        V7 / "verification.md": render_verification(summary, checks) + "\n\n## Final controls\n\nSee `final_controls.md`, canonical `experiments/output/corrected_primary_registry.json`, and registrations under `evidence/{execution_planner,resource_control,carrier_control,belief_control,information_controls,cumulative_dag,cumulative_dag_matched}`. All source/config hashes are checked by `final_controls.py`; these controls do not promote global-RL, dogmatism, or adaptation claims.\n",
        V7 / "manuscript_outline.md": render_manuscript(),
        V7 / "README.md": render_readme() + controls_readme,
        V7 / "final_controls.md": controls_report,
        V7 / "research_gaps_and_next_steps.md": render_gaps(),
    }
    for path, content in reports.items():
        path.write_text(content, encoding="utf-8")

    ledger_doc = {"schema_version": 1, "scientific_verdict": summary["scientific_verdict"], "hypotheses": summary["hypotheses"]}
    (EVIDENCE / "hypothesis_ledger.json").write_text(json.dumps(ledger_doc, indent=2) + "\n")
    checks_doc = {"schema_version": 1, "scientific_verdict": summary["scientific_verdict"],
                  "status_vocabulary": ["passed", "partial", "not_run"], "checks": checks}
    (EVIDENCE / "executed_checks.json").write_text(json.dumps(checks_doc, indent=2) + "\n")

    base_revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    spike_files = [ROOT / ".planning" / "spikes" / f"{n:03d}-{slug}" / "README.md" for n, slug in [
        (15, "behavioral-kernel"), (16, "procedures-cost"), (17, "local-context"),
        (18, "learned-persistence"), (19, "finite-selection")]]
    generated_paths = [*reports, EVIDENCE / "hypothesis_ledger.json", EVIDENCE / "executed_checks.json",
                       defect_path, corrected_audit_path, quality_path,
                       ROOT / ".planning" / "spikes" / "MANIFEST.md", *spike_files]
    final_review = EVIDENCE / "final_scientific_review.md"
    if final_review.exists():
        generated_paths.append(final_review)
    generated_files = {}
    for path in generated_paths:
        generated_files[str(path.relative_to(ROOT))] = {"sha256": sha256(path), "bytes": path.stat().st_size}
    frozen_source_files = [V7 / "experiments" / "model.py", V7 / "experiments" / "exact.py",
                    V7 / "experiments" / "run_experiments.py", V7 / "experiments" / "analyze_results.py",
                    V7 / "experiments" / "verify.py", V7 / "experiments" / "config.json",
                    V7 / "parameter_schema.json"]
    corrected_source_files = [V7 / "experiments" / "corrected_model.py",
                              V7 / "experiments" / "run_corrected_experiments.py",
                              V7 / "experiments" / "corrected_evolution.py",
                              V7 / "experiments" / "run_corrected_evolution.py"]
    authored_source_files = [V7 / "synthesize_results.py", V7 / "tests" / "test_reporting.py",
                             V7 / "tests" / "test_corrected_model.py", V7 / "dashboard_template.html",
                             V7 / "build_dashboard.py", V7 / "browser_verify.js"]
    corrected_evidence_files = sorted(path for path in CORRECTED_EVIDENCE.rglob("*") if path.is_file())
    corrected_execution_records = [path for path in [
        CORRECTED_OUT / "corrected_evolution_checkpoint.jsonl",
        CORRECTED_OUT / "corrected_evolution_gates.json",
        CORRECTED_OUT / "corrected_evolution_summary.json",
    ] if path.is_file()]
    manifest = {
        "schema_version": 1, "project": "V7 costly cultural competence", "canonical_reporting_registry": "v7/experiments/output/corrected_primary_registry.json", "final_controls_signature": controls["signature"], "scientific_verdict": summary["scientific_verdict"],
        "primary_evidence": "corrected_overlay",
        "base_revision_before_reporting_commit": base_revision,
        "frozen_core_replay_digest": summary["core_freeze"]["replay_digest"],
        "corrected_overlay_replay_digest": summary["corrected_freeze"]["replay"]["replay_digest"],
        "corrected_freeze_manifest_sha256": summary["corrected_freeze_sha256"],
        "frozen_core_files": {str(p.relative_to(ROOT)): sha256(p) for p in frozen_source_files},
        "corrected_source_files": {str(p.relative_to(ROOT)): sha256(p) for p in corrected_source_files},
        "authored_source_files": {str(p.relative_to(ROOT)): sha256(p) for p in authored_source_files},
        "raw_exports": {"corrected_primary": corrected_inventory,
                        "frozen_invalidated": frozen_inventory},
        "corrected_registration_and_result_evidence": {
            str(p.relative_to(ROOT)): {"sha256": sha256(p), "bytes": p.stat().st_size}
            for p in corrected_evidence_files},
        "additional_control_sources": controls["sources"],
        "corrected_execution_records": {
            str(p.relative_to(ROOT)): {"sha256": sha256(p), "bytes": p.stat().st_size}
            for p in corrected_execution_records},
        "generated_files": generated_files,
        "reference_files": {str(p.relative_to(ROOT)): sha256(p) for p in [
            EVIDENCE / "literature_sources.json", V7 / "literature_map.md", V7 / "mathematical_model.md",
            V7 / "constructs_and_estimands.md", V7 / "research_contract.md", OUT / "kernel.json",
            OUT / "run_manifest.json", OUT / "representative_trajectories.json.gz"]},
        "generation_command": "python v7/synthesize_results.py --write",
        "data_quality_status": summary["data_quality"]["status"],
        "interpretation": summary["interpretive_limits"],
    }
    (V7 / "project_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    handoff_files = [*reports, V7 / "project_manifest.json", EVIDENCE / "hypothesis_ledger.json",
                     EVIDENCE / "executed_checks.json", defect_path, corrected_audit_path, quality_path,
                     ROOT / ".planning" / "spikes" / "MANIFEST.md", *spike_files]
    if final_review.exists():
        handoff_files.append(final_review)
    handoff = {
        "slice": "3B-results-synthesis", "status": "complete" if tests["status"] == "passed" else "test_failure",
        "primary_evidence": "corrected_overlay",
        "canonical_reporting_registry": "v7/experiments/output/corrected_primary_registry.json",
        "dashboard_source_contract": "v7/experiments/output/summary.json",
        "final_controls_signature": controls["signature"],
        "scientific_verdict": summary["scientific_verdict"], "software_test": tests,
        "corrected_inventory": corrected_inventory,
        "frozen_invalidated_inventory": frozen_inventory,
        "raw_row_counts": {name: item["rows"] for name, item in corrected_inventory.items()},
        "raw_sha256": {name: item["sha256"] for name, item in corrected_inventory.items()},
        "generated_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in handoff_files},
        "core_freeze_replay_digest": summary["core_freeze"]["replay_digest"],
        "corrected_freeze_manifest_sha256": summary["corrected_freeze_sha256"],
        "corrected_replay_digest": summary["corrected_freeze"]["replay"]["replay_digest"],
        "data_quality_status": summary["data_quality"]["status"],
        "check_status_counts": {status: sum(c["scientific_status"] == status for c in checks)
                                for status in ("passed", "partial", "not_run")},
        "checks": [{"id": c["id"], "scientific_status": c["scientific_status"],
                    "basis": c["basis"]} for c in checks],
        "corrected_holdout_contrasts": summary["holdout"]["contrasts"],
        "corrected_selection_contrasts": summary["selection"]["contrasts"],
        "selection_denominators": {k: summary["selection"][k] for k in
            ("registered_raw_rows", "completed_batch_rows", "excluded_incomplete_batch_rows",
             "paid_birth_rows", "no_birth_censored", "cap_censored", "extinction_rows",
             "paired_paid_birth_pairs")},
        "selection_precision": {k: summary["selection"][k] for k in
            ("runner_status", "registered_precision_rule", "maximum_paired_descendant_mcse",
             "maximum_establishment_wilson_half_width", "runner_unresolved")},
        "frozen_local_no_teacher_defect": summary["frozen_local_no_teacher_defect"],
        "corrected_local_no_teacher_audit": summary["corrected_local_no_teacher_audit"],
        "limitations": summary["interpretive_limits"] + [
            "Wilson precision for action/revision/success rates is unresolved without exported event counts.",
            "Candidate-B information-purchase counts were not exported.",
            "Independent final scientific review is a separate reviewer-owned artifact.",
        ],
    }
    handoff_path = EVIDENCE / "handoffs" / "07-results.json"
    handoff_path.write_text(json.dumps(handoff, indent=2) + "\n")
    if tests["status"] != "passed":
        raise RuntimeError(f"reporting test suite failed: {tests['stderr']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--verify-only", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()
    summary = build_evidence_summary()
    verify_summary(summary)
    if args.write:
        write_outputs(summary)
        print("wrote V7 corrected-primary synthesis reports and evidence; frozen and corrected parity verified")
    else:
        print(json.dumps({"status": "verified", "scientific_verdict": summary["scientific_verdict"],
                          "primary_evidence": summary["primary_evidence"],
                          "corrected_inventory": summary["corrected_inventory"],
                          "frozen_invalidated_inventory": summary["frozen_inventory"]}, indent=2))


if __name__ == "__main__":
    main()
