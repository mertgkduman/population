"""Stochastic multi-context companion for V5 information-access experiments.

This script represents an actual repertoire of independent binary facts.  It is
deliberately not a demographic, selection, cooperation, or combinatorial-task
model.  Every learner has the same score capacity and opportunity budgets
within a scenario.  Prior-generation adults are the only social sources.

Run from the repository root with::

    python v5/experiments/repertoire.py

The predeclared grid writes per-run/per-generation summaries to repertoire.csv
and endpoint plus validation summaries to repertoire.json beside this file.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np


POLICIES = ("retained_update", "frozen", "confidence_audit")
ENVIRONMENTS = ("stable", "quarter_flip")


@dataclass(frozen=True)
class Config:
    context_counts: tuple[int, ...] = (4, 16, 64)
    cue_qualities: tuple[float, ...] = (0.55, 0.70, 0.90)
    deference: tuple[float, ...] = (0.0, 0.5, 1.0)
    policies: tuple[str, ...] = POLICIES
    environments: tuple[str, ...] = ENVIRONMENTS
    seeds: tuple[int, ...] = (501, 502, 503, 504, 505, 506)
    cohort_size: int = 128
    generations: int = 24
    shock_generation: int = 12
    flip_fraction: float = 0.25
    score_bound: int = 4
    juvenile_private_budget: int = 16
    juvenile_social_budget: int = 16
    founder_private_budget: int = 16
    adult_private_budget: int = 16
    audit_threshold: int = 2
    audit_floor: float = 0.05
    recovery_target: float = 0.90


CSV_FIELDS = (
    "run_id",
    "seed",
    "D",
    "p",
    "d",
    "policy",
    "environment",
    "generation",
    "shock_generation",
    "shock_applied",
    "adult_accuracy",
    "private_accuracy",
    "held_coverage",
    "private_coverage",
    "held_confidence",
    "private_confidence",
    "wrong_high_confidence",
    "knowledge_heterogeneity",
    "context_accuracy_sd",
    "context_coverage_sd",
    "juvenile_private_queries",
    "juvenile_social_encounters",
    "adult_queries",
    "teacher_accuracy",
    "teacher_accuracy_expressed",
    "teacher_coverage",
    "teacher_knowledge_heterogeneity",
    "social_testimonies",
    "accepted_social_testimonies",
    "child_conflicts",
    "child_overrides",
    "child_conflict_override_rate",
)


def validate_config(config: Config) -> None:
    if any(not isinstance(value, int) or value <= 0 for value in config.context_counts):
        raise ValueError("context counts must be positive integers")
    if any(not 0.5 < value < 1 for value in config.cue_qualities):
        raise ValueError("cue qualities must lie strictly between 0.5 and 1")
    if any(not 0 <= value <= 1 for value in config.deference):
        raise ValueError("deference must lie in [0, 1]")
    if set(config.policies) - set(POLICIES):
        raise ValueError("unknown adult policy")
    if set(config.environments) - set(ENVIRONMENTS):
        raise ValueError("unknown environment")
    if config.generations < 3 or not 1 <= config.shock_generation < config.generations:
        raise ValueError("shock generation must be internal to the run")
    if config.cohort_size <= 1 or config.score_bound < 1:
        raise ValueError("invalid cohort size or score bound")
    if not 0 < config.flip_fraction < 1:
        raise ValueError("flip fraction must lie in (0, 1)")
    if not 0 <= config.audit_floor <= 1 or config.audit_threshold < 0:
        raise ValueError("invalid audit rule")
    if not 0 < config.recovery_target <= 1:
        raise ValueError("invalid recovery target")


def make_schedule(config: Config, D: int, seed: int) -> dict[str, np.ndarray]:
    """Pre-generate common random numbers for all matched p/d/policy runs."""

    rng = np.random.default_rng(np.random.SeedSequence((20261030, seed, D)))
    N, G = config.cohort_size, config.generations
    J, S, A = (
        config.juvenile_private_budget,
        config.juvenile_social_budget,
        config.adult_private_budget,
    )
    theta0 = rng.choice(np.array([-1, 1], dtype=np.int8), size=D)
    flip_count = int(round(config.flip_fraction * D))
    flip_mask = np.zeros(D, dtype=bool)
    flip_mask[rng.permutation(D)[:flip_count]] = True
    schedule = {
        "theta0": theta0,
        "flip_mask": flip_mask,
        "founder_context": rng.integers(0, D, size=(N, config.founder_private_budget), dtype=np.int16),
        "founder_quality": rng.random((N, config.founder_private_budget)),
        "juvenile_context": rng.integers(0, D, size=(G, N, J), dtype=np.int16),
        "juvenile_quality": rng.random((G, N, J)),
        "social_context": rng.integers(0, D, size=(G, N, S), dtype=np.int16),
        "social_teacher": rng.integers(0, N, size=(G, N, S), dtype=np.int16),
        "social_accept": rng.random((G, N, S)),
        "social_override": rng.random((G, N, S)),
        "social_private_tie": rng.random((G, N, S)),
        "adult_context": rng.integers(0, D, size=(G, N, A), dtype=np.int16),
        "adult_quality": rng.random((G, N, A)),
        "adult_audit": rng.random((G, N, A)),
    }
    return schedule


def schedule_digest(schedule: dict[str, np.ndarray]) -> str:
    digest = hashlib.sha256()
    for key in sorted(schedule):
        array = np.ascontiguousarray(schedule[key])
        digest.update(key.encode("utf-8"))
        digest.update(str(array.dtype).encode("ascii"))
        digest.update(np.asarray(array.shape, dtype=np.int64).tobytes())
        digest.update(array.tobytes())
    return digest.hexdigest()


def update_score(values: np.ndarray, signs: np.ndarray, bound: int) -> np.ndarray:
    return np.clip(values.astype(np.int16) + signs.astype(np.int16), -bound, bound).astype(np.int8)


def apply_private_budget(
    u: np.ndarray,
    b: np.ndarray,
    contexts: np.ndarray,
    quality_uniforms: np.ndarray,
    theta: np.ndarray,
    p: float,
    bound: int,
    active: np.ndarray | None = None,
) -> int:
    """Apply sequential private cues to both ledgers and return query count."""

    N, budget = contexts.shape
    rows = np.arange(N)
    queries = 0
    for opportunity in range(budget):
        context = contexts[:, opportunity]
        use = np.ones(N, dtype=bool) if active is None else active[:, opportunity]
        if not np.any(use):
            continue
        selected_rows = rows[use]
        selected_contexts = context[use]
        truths = theta[selected_contexts]
        signs = np.where(quality_uniforms[use, opportunity] < p, truths, -truths).astype(np.int8)
        u[selected_rows, selected_contexts] = update_score(
            u[selected_rows, selected_contexts], signs, bound
        )
        b[selected_rows, selected_contexts] = update_score(
            b[selected_rows, selected_contexts], signs, bound
        )
        queries += int(np.sum(use))
    return queries


def apply_adult_policy(
    u: np.ndarray,
    b: np.ndarray,
    policy: str,
    contexts: np.ndarray,
    quality_uniforms: np.ndarray,
    audit_uniforms: np.ndarray,
    theta: np.ndarray,
    p: float,
    config: Config,
) -> int:
    if policy == "frozen":
        return 0
    if policy == "retained_update":
        return apply_private_budget(
            u, b, contexts, quality_uniforms, theta, p, config.score_bound
        )
    if policy != "confidence_audit":
        raise ValueError(f"unknown policy: {policy}")

    # Audit decisions are state dependent and therefore evaluated sequentially.
    N, budget = contexts.shape
    rows = np.arange(N)
    queries = 0
    for opportunity in range(budget):
        context = contexts[:, opportunity]
        conviction = np.abs(b[rows, context])
        use = (conviction < config.audit_threshold) | (
            audit_uniforms[:, opportunity] < config.audit_floor
        )
        if not np.any(use):
            continue
        selected_rows = rows[use]
        selected_contexts = context[use]
        truths = theta[selected_contexts]
        signs = np.where(
            quality_uniforms[use, opportunity] < p, truths, -truths
        ).astype(np.int8)
        u[selected_rows, selected_contexts] = update_score(
            u[selected_rows, selected_contexts], signs, config.score_bound
        )
        b[selected_rows, selected_contexts] = update_score(
            b[selected_rows, selected_contexts], signs, config.score_bound
        )
        queries += int(np.sum(use))
    return queries


def apply_social_budget(
    u: np.ndarray,
    b: np.ndarray,
    teacher_b: np.ndarray,
    contexts: np.ndarray,
    teachers: np.ndarray,
    accept_uniforms: np.ndarray,
    override_uniforms: np.ndarray,
    tie_uniforms: np.ndarray,
    d: float,
    bound: int,
) -> dict[str, int]:
    """Apply prior-generation testimony and count action-level conflicts."""

    N, budget = contexts.shape
    rows = np.arange(N)
    testimonies = accepted = conflicts = overrides = 0
    for encounter in range(budget):
        context = contexts[:, encounter]
        teacher = teachers[:, encounter]
        advice = np.sign(teacher_b[teacher, context]).astype(np.int8)
        valid = advice != 0
        testimonies += int(np.sum(valid))

        private = np.sign(u[rows, context]).astype(np.int8)
        ties = private == 0
        private[ties] = np.where(tie_uniforms[ties, encounter] < 0.5, -1, 1).astype(np.int8)
        conflict = valid & (private != advice)
        override = conflict & (override_uniforms[:, encounter] < d)
        conflicts += int(np.sum(conflict))
        overrides += int(np.sum(override))

        accept = valid & (accept_uniforms[:, encounter] < d)
        if np.any(accept):
            b[rows[accept], context[accept]] = update_score(
                b[rows[accept], context[accept]], advice[accept], bound
            )
        accepted += int(np.sum(accept))
    return {
        "social_testimonies": testimonies,
        "accepted_social_testimonies": accepted,
        "child_conflicts": conflicts,
        "child_overrides": overrides,
    }


def accuracy_matrix(scores: np.ndarray, theta: np.ndarray) -> np.ndarray:
    signs = np.sign(scores)
    return np.where(signs == 0, 0.5, (signs == theta[None, :]).astype(float))


def knowledge_metrics(scores: np.ndarray, theta: np.ndarray) -> dict[str, float]:
    accuracy = accuracy_matrix(scores, theta)
    coverage_matrix = scores != 0
    context_accuracy = np.mean(accuracy, axis=0)
    context_coverage = np.mean(coverage_matrix, axis=0)
    expressed = coverage_matrix
    expressed_count = int(np.sum(expressed))
    expressed_correct = int(np.sum((np.sign(scores) == theta[None, :]) & expressed))
    return {
        "accuracy": float(np.mean(accuracy)),
        "accuracy_expressed": (
            float(expressed_correct / expressed_count) if expressed_count else 0.5
        ),
        "coverage": float(np.mean(coverage_matrix)),
        "confidence": float(np.mean(np.abs(scores))),
        "wrong_high_confidence": float(
            np.mean((np.abs(scores) >= 3) & (np.sign(scores) != theta[None, :]))
        ),
        "knowledge_heterogeneity": float(np.mean(np.var(accuracy, axis=0))),
        "context_accuracy_sd": float(np.std(context_accuracy)),
        "context_coverage_sd": float(np.std(context_coverage)),
    }


def run_id(D: int, p: float, d: float, policy: str, environment: str, seed: int) -> str:
    p_text = f"{p:.2f}".replace(".", "p")
    d_text = f"{d:.1f}".replace(".", "p")
    return f"D{D}_p{p_text}_d{d_text}_{policy}_{environment}_s{seed}"


def simulate_run(
    config: Config,
    D: int,
    p: float,
    d: float,
    policy: str,
    environment: str,
    seed: int,
    schedule: dict[str, np.ndarray],
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, float]]:
    N, H = config.cohort_size, config.score_bound
    theta = schedule["theta0"].copy()
    u = np.zeros((N, D), dtype=np.int8)
    b = np.zeros((N, D), dtype=np.int8)

    # Common founder acquisition bootstraps all policies from observed evidence.
    founder_queries = apply_private_budget(
        u,
        b,
        schedule["founder_context"],
        schedule["founder_quality"],
        theta,
        p,
        H,
    )
    if not np.array_equal(u, b):
        raise AssertionError("founder private and held ledgers must match")

    identifier = run_id(D, p, d, policy, environment, seed)
    held = knowledge_metrics(b, theta)
    private = knowledge_metrics(u, theta)
    rows: list[dict[str, Any]] = [
        {
            "run_id": identifier,
            "seed": seed,
            "D": D,
            "p": p,
            "d": d,
            "policy": policy,
            "environment": environment,
            "generation": 0,
            "shock_generation": config.shock_generation,
            "shock_applied": False,
            "adult_accuracy": held["accuracy"],
            "private_accuracy": private["accuracy"],
            "held_coverage": held["coverage"],
            "private_coverage": private["coverage"],
            "held_confidence": held["confidence"],
            "private_confidence": private["confidence"],
            "wrong_high_confidence": held["wrong_high_confidence"],
            "knowledge_heterogeneity": held["knowledge_heterogeneity"],
            "context_accuracy_sd": held["context_accuracy_sd"],
            "context_coverage_sd": held["context_coverage_sd"],
            "juvenile_private_queries": 0.0,
            "juvenile_social_encounters": 0.0,
            "adult_queries": founder_queries / N,
            "teacher_accuracy": np.nan,
            "teacher_accuracy_expressed": np.nan,
            "teacher_coverage": np.nan,
            "teacher_knowledge_heterogeneity": np.nan,
            "social_testimonies": 0,
            "accepted_social_testimonies": 0,
            "child_conflicts": 0,
            "child_overrides": 0,
            "child_conflict_override_rate": np.nan,
        }
    ]
    max_d0_difference = 0
    max_bound = int(max(np.max(np.abs(u)), np.max(np.abs(b))))

    for generation in range(1, config.generations):
        shock_applied = environment == "quarter_flip" and generation == config.shock_generation
        if shock_applied:
            theta[schedule["flip_mask"]] *= -1

        teacher_b = b.copy()
        teacher = knowledge_metrics(teacher_b, theta)
        u = np.zeros((N, D), dtype=np.int8)
        b = np.zeros((N, D), dtype=np.int8)

        juvenile_queries = apply_private_budget(
            u,
            b,
            schedule["juvenile_context"][generation],
            schedule["juvenile_quality"][generation],
            theta,
            p,
            H,
        )
        social = apply_social_budget(
            u,
            b,
            teacher_b,
            schedule["social_context"][generation],
            schedule["social_teacher"][generation],
            schedule["social_accept"][generation],
            schedule["social_override"][generation],
            schedule["social_private_tie"][generation],
            d,
            H,
        )
        adult_queries = apply_adult_policy(
            u,
            b,
            policy,
            schedule["adult_context"][generation],
            schedule["adult_quality"][generation],
            schedule["adult_audit"][generation],
            theta,
            p,
            config,
        )

        if d == 0:
            difference = int(np.max(np.abs(u.astype(np.int16) - b.astype(np.int16))))
            max_d0_difference = max(max_d0_difference, difference)
            if difference != 0:
                raise AssertionError("d=0 must preserve u=b exactly")
        max_bound = max(max_bound, int(np.max(np.abs(u))), int(np.max(np.abs(b))))
        if max_bound > H:
            raise AssertionError("score bound exceeded")

        held = knowledge_metrics(b, theta)
        private = knowledge_metrics(u, theta)
        conflict_rate = (
            social["child_overrides"] / social["child_conflicts"]
            if social["child_conflicts"]
            else np.nan
        )
        rows.append(
            {
                "run_id": identifier,
                "seed": seed,
                "D": D,
                "p": p,
                "d": d,
                "policy": policy,
                "environment": environment,
                "generation": generation,
                "shock_generation": config.shock_generation,
                "shock_applied": shock_applied,
                "adult_accuracy": held["accuracy"],
                "private_accuracy": private["accuracy"],
                "held_coverage": held["coverage"],
                "private_coverage": private["coverage"],
                "held_confidence": held["confidence"],
                "private_confidence": private["confidence"],
                "wrong_high_confidence": held["wrong_high_confidence"],
                "knowledge_heterogeneity": held["knowledge_heterogeneity"],
                "context_accuracy_sd": held["context_accuracy_sd"],
                "context_coverage_sd": held["context_coverage_sd"],
                "juvenile_private_queries": juvenile_queries / N,
                "juvenile_social_encounters": float(config.juvenile_social_budget),
                "adult_queries": adult_queries / N,
                "teacher_accuracy": teacher["accuracy"],
                "teacher_accuracy_expressed": teacher["accuracy_expressed"],
                "teacher_coverage": teacher["coverage"],
                "teacher_knowledge_heterogeneity": teacher["knowledge_heterogeneity"],
                **social,
                "child_conflict_override_rate": conflict_rate,
            }
        )

    summary = summarize_run(config, rows)
    checks = {
        "max_d0_u_b_difference": float(max_d0_difference),
        "max_absolute_score": float(max_bound),
        "founder_query_count_per_adult": float(founder_queries / N),
    }
    return rows, summary, checks


def finite_or_none(value: float) -> float | None:
    return float(value) if np.isfinite(value) else None


def summarize_run(config: Config, rows: list[dict[str, Any]]) -> dict[str, Any]:
    first = rows[0]
    last = rows[-1]
    shock = config.shock_generation
    pre_window = rows[max(0, shock - 3) : shock]
    shock_row = rows[shock]
    post_rows = rows[shock:]
    pre_accuracy = float(np.mean([row["adult_accuracy"] for row in pre_window]))
    pre_coverage = float(np.mean([row["held_coverage"] for row in pre_window]))

    summary: dict[str, Any] = {
        "run_id": first["run_id"],
        "seed": first["seed"],
        "D": first["D"],
        "p": first["p"],
        "d": first["d"],
        "policy": first["policy"],
        "environment": first["environment"],
        "founder_accuracy": first["adult_accuracy"],
        "founder_coverage": first["held_coverage"],
        "pre_shock_accuracy": pre_accuracy,
        "pre_shock_coverage": pre_coverage,
        "end_accuracy": last["adult_accuracy"],
        "end_private_accuracy": last["private_accuracy"],
        "end_coverage": last["held_coverage"],
        "end_wrong_high_confidence": last["wrong_high_confidence"],
        "total_adult_queries_post_founder": float(sum(row["adult_queries"] for row in rows[1:])),
        "mean_conflict_override_rate": finite_or_none(
            float(
                np.nanmean(
                    np.asarray([row["child_conflict_override_rate"] for row in rows[1:]], dtype=float)
                )
            )
        ),
    }

    if first["environment"] == "quarter_flip":
        shock_accuracy = float(shock_row["adult_accuracy"])
        lost = pre_accuracy - shock_accuracy
        recovered = float(last["adult_accuracy"] - shock_accuracy)
        target = shock_accuracy + config.recovery_target * lost
        recovery_generation = next(
            (int(row["generation"]) for row in post_rows if row["adult_accuracy"] >= target),
            None,
        )
        summary.update(
            {
                "shock_accuracy": shock_accuracy,
                "shock_private_accuracy": float(shock_row["private_accuracy"]),
                "teacher_accuracy_at_shock": finite_or_none(float(shock_row["teacher_accuracy"])),
                "accuracy_drop": float(lost),
                "recovery_fraction_end": finite_or_none(recovered / lost) if lost > 0 else None,
                "recovery_generation_90": recovery_generation,
                "post_shock_mean_accuracy": float(
                    np.mean([row["adult_accuracy"] for row in post_rows])
                ),
            }
        )
    else:
        summary.update(
            {
                "shock_accuracy": None,
                "shock_private_accuracy": None,
                "teacher_accuracy_at_shock": None,
                "accuracy_drop": None,
                "recovery_fraction_end": None,
                "recovery_generation_90": None,
                "post_shock_mean_accuracy": None,
            }
        )
    return summary


def nested_quality_check(config: Config, schedule: dict[str, np.ndarray]) -> bool:
    qualities = sorted(config.cue_qualities)
    arrays = (
        schedule["founder_quality"],
        schedule["juvenile_quality"],
        schedule["adult_quality"],
    )
    for array in arrays:
        counts = [int(np.sum(array < p)) for p in qualities]
        if counts != sorted(counts):
            return False
    return True


def no_signal_check(config: Config) -> dict[str, Any]:
    D, N = config.context_counts[0], config.cohort_size
    theta = np.ones(D, dtype=np.int8)
    u = np.zeros((N, D), dtype=np.int8)
    b = np.zeros((N, D), dtype=np.int8)
    zero_contexts = np.zeros((N, 0), dtype=np.int16)
    zero_uniforms = np.zeros((N, 0), dtype=float)
    queries = apply_private_budget(u, b, zero_contexts, zero_uniforms, theta, 0.7, config.score_bound)
    metrics = knowledge_metrics(b, theta)
    passed = (
        queries == 0
        and np.count_nonzero(u) == 0
        and np.count_nonzero(b) == 0
        and metrics["accuracy"] == 0.5
        and metrics["coverage"] == 0.0
    )
    return {
        "passed": bool(passed),
        "queries": queries,
        "accuracy": metrics["accuracy"],
        "coverage": metrics["coverage"],
    }


def aggregate_summaries(summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    group_keys = ("D", "p", "d", "policy", "environment")
    metric_keys = (
        "founder_accuracy",
        "founder_coverage",
        "pre_shock_accuracy",
        "pre_shock_coverage",
        "shock_accuracy",
        "accuracy_drop",
        "end_accuracy",
        "end_private_accuracy",
        "end_coverage",
        "end_wrong_high_confidence",
        "recovery_fraction_end",
        "recovery_generation_90",
        "post_shock_mean_accuracy",
        "total_adult_queries_post_founder",
        "mean_conflict_override_rate",
    )
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for summary in summaries:
        groups[tuple(summary[key] for key in group_keys)].append(summary)

    aggregates: list[dict[str, Any]] = []
    for key, values in sorted(groups.items(), key=lambda item: item[0]):
        row: dict[str, Any] = dict(zip(group_keys, key))
        row["n_seeds"] = len(values)
        for metric in metric_keys:
            observed = np.asarray(
                [value[metric] for value in values if value[metric] is not None], dtype=float
            )
            row[f"{metric}_n"] = int(observed.size)
            row[f"{metric}_mean"] = float(np.mean(observed)) if observed.size else None
            row[f"{metric}_sd"] = (
                float(np.std(observed, ddof=1)) if observed.size > 1 else (0.0 if observed.size else None)
            )
        aggregates.append(row)
    return aggregates


def write_csv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False, allow_nan=False)
        handle.write("\n")


def run_grid(config: Config) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    validate_config(config)
    rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    schedule_hashes: list[dict[str, Any]] = []
    nested_checks: list[bool] = []
    max_d0_difference = 0.0
    max_absolute_score = 0.0
    founder_queries: set[float] = set()
    founder_metrics: dict[tuple[int, int, float], set[tuple[float, float]]] = defaultdict(set)
    policy_query_ranges: dict[str, list[float]] = defaultdict(list)

    for D in config.context_counts:
        for seed in config.seeds:
            schedule = make_schedule(config, D, seed)
            schedule_hashes.append(
                {"D": D, "seed": seed, "sha256": schedule_digest(schedule)}
            )
            nested_checks.append(nested_quality_check(config, schedule))
            if int(np.sum(schedule["flip_mask"])) != int(round(config.flip_fraction * D)):
                raise AssertionError("flip count mismatch")
            for p in config.cue_qualities:
                for d in config.deference:
                    for policy in config.policies:
                        for environment in config.environments:
                            run_rows, summary, checks = simulate_run(
                                config, D, p, d, policy, environment, seed, schedule
                            )
                            rows.extend(run_rows)
                            summaries.append(summary)
                            max_d0_difference = max(
                                max_d0_difference, checks["max_d0_u_b_difference"]
                            )
                            max_absolute_score = max(
                                max_absolute_score, checks["max_absolute_score"]
                            )
                            founder_queries.add(checks["founder_query_count_per_adult"])
                            founder_metrics[(D, seed, p)].add(
                                (summary["founder_accuracy"], summary["founder_coverage"])
                            )
                            for row in run_rows[1:]:
                                policy_query_ranges[policy].append(float(row["adult_queries"]))

    founder_common = all(len(values) == 1 for values in founder_metrics.values())
    query_ranges = {
        policy: {
            "min": float(min(values)),
            "max": float(max(values)),
        }
        for policy, values in policy_query_ranges.items()
    }

    # Matched environments must be identical before the scheduled truth change.
    pre_shock_pairs: dict[tuple[Any, ...], dict[str, tuple[float, ...]]] = defaultdict(dict)
    private_d_groups: dict[tuple[Any, ...], list[tuple[float, float]]] = defaultdict(list)
    for row in rows:
        if row["generation"] < config.shock_generation:
            key = (
                row["seed"], row["D"], row["p"], row["d"], row["policy"], row["generation"]
            )
            pre_shock_pairs[key][row["environment"]] = (
                float(row["adult_accuracy"]),
                float(row["private_accuracy"]),
                float(row["held_coverage"]),
            )
        if row["policy"] in ("frozen", "retained_update"):
            key = (
                row["seed"],
                row["D"],
                row["p"],
                row["policy"],
                row["environment"],
                row["generation"],
            )
            private_d_groups[key].append(
                (float(row["private_accuracy"]), float(row["private_coverage"]))
            )
    pre_shock_max_difference = max(
        max(abs(a - b) for a, b in zip(pair["stable"], pair["quarter_flip"]))
        for pair in pre_shock_pairs.values()
    )
    private_d_max_difference = max(
        max(
            max(value[index] for value in values) - min(value[index] for value in values)
            for index in (0, 1)
        )
        for values in private_d_groups.values()
    )
    invariant_payload = {
        "d0_u_equals_b": {
            "passed": max_d0_difference == 0,
            "maximum_absolute_difference": max_d0_difference,
        },
        "no_signal": no_signal_check(config),
        "founder_learning": {
            "passed": founder_common
            and founder_queries == {float(config.founder_private_budget)},
            "common_across_matched_d_policy_environment": founder_common,
            "query_counts_per_adult_observed": sorted(founder_queries),
            "starts_from_fixed_accuracy": False,
        },
        "matched_cue_quality": {
            "passed": all(nested_checks),
            "description": "Common uniform cue draws give nested correct-cue sets as p increases.",
        },
        "matched_environment_pre_shock": {
            "passed": pre_shock_max_difference == 0,
            "maximum_metric_difference": pre_shock_max_difference,
            "description": "Stable and quarter-flip runs are exactly paired through generation 11.",
        },
        "private_ledger_independent_of_d_when_queries_unconditional": {
            "passed": private_d_max_difference == 0,
            "maximum_accuracy_or_coverage_difference": private_d_max_difference,
            "description": "Frozen and retained-update private ledgers are identical across d under common private draws; audit is excluded because its query eligibility depends on b.",
        },
        "score_bounds": {
            "passed": max_absolute_score <= config.score_bound,
            "maximum_absolute_score": max_absolute_score,
            "bound": config.score_bound,
        },
        "adult_query_policy": {
            "passed": query_ranges["frozen"] == {"min": 0.0, "max": 0.0}
            and query_ranges["retained_update"]
            == {
                "min": float(config.adult_private_budget),
                "max": float(config.adult_private_budget),
            }
            and 0 <= query_ranges["confidence_audit"]["min"]
            <= query_ranges["confidence_audit"]["max"]
            <= config.adult_private_budget,
            "observed_queries_per_adult": query_ranges,
        },
    }
    if not all(
        block["passed"]
        for block in invariant_payload.values()
        if isinstance(block, dict) and "passed" in block
    ):
        raise AssertionError(f"validation invariant failed: {invariant_payload}")

    payload = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_scope": "Independent binary-fact repertoire with cultural testimony; no demography, fitness weighting, selection, cooperation, social norms, or combinatorial reasoning.",
        "predeclared_parameters": asdict(config),
        "common_random_numbers": {
            "description": "Within each D/seed block, all p, d, adult-policy, and environment comparisons reuse context choices, teacher choices, cue uniforms, acceptance uniforms, override uniforms, tie draws, and audit uniforms. Cue correctness is nested across p. State-dependent audit eligibility and endogenous teacher signs still differ by policy.",
            "schedule_hashes": schedule_hashes,
        },
        "metric_definitions": {
            "adult_accuracy": "Mean held-belief correctness across organisms and contexts; b=0 scores 0.5.",
            "private_accuracy": "Mean private-ledger correctness across organisms and contexts; u=0 scores 0.5.",
            "held_coverage": "Fraction of organism-context held scores with b nonzero.",
            "private_coverage": "Fraction of organism-context private scores with u nonzero.",
            "knowledge_heterogeneity": "Mean across contexts of the within-cohort variance in correctness scores 0, 0.5, or 1.",
            "teacher_accuracy": "Prior-generation held accuracy scored against truth at the current generation; this drops immediately at a true-state shock.",
            "teacher_accuracy_expressed": "Accuracy among nonzero prior-generation held signs only.",
            "child_conflict_override_rate": "Overrides divided by encounters where a nonzero adult sign conflicts with the child's private action; u=0 private actions use a pre-generated fair tie break.",
            "recovery_fraction_end": "(end accuracy - shock accuracy)/(pre-shock mean accuracy - shock accuracy), reported only when the initial shock loss is positive.",
            "recovery_generation_90": "First shock-or-later generation reaching 90% of the lost pre-shock held accuracy.",
        },
        "invariants": invariant_payload,
        "run_summaries": summaries,
        "aggregates": aggregate_summaries(summaries),
    }
    return rows, payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Directory for repertoire.csv and repertoire.json",
    )
    parser.add_argument(
        "--self-test-only",
        action="store_true",
        help="Run lightweight deterministic invariants without the full grid",
    )
    return parser.parse_args()


def lightweight_self_test(config: Config) -> dict[str, Any]:
    validate_config(config)
    schedule = make_schedule(config, config.context_counts[0], config.seeds[0])
    rows, summary, checks = simulate_run(
        config,
        config.context_counts[0],
        config.cue_qualities[1],
        0.0,
        "retained_update",
        "quarter_flip",
        config.seeds[0],
        schedule,
    )
    result = {
        "no_signal": no_signal_check(config),
        "nested_quality": nested_quality_check(config, schedule),
        "d0_u_equals_b": checks["max_d0_u_b_difference"] == 0,
        "bounded": checks["max_absolute_score"] <= config.score_bound,
        "row_count": len(rows),
        "summary_has_recovery": "recovery_fraction_end" in summary,
    }
    if not all(
        value if isinstance(value, bool) else value.get("passed", True)
        for value in result.values()
        if isinstance(value, (bool, dict))
    ):
        raise AssertionError(result)
    return result


def main() -> None:
    args = parse_args()
    config = Config()
    if args.self_test_only:
        print(json.dumps(lightweight_self_test(config), indent=2))
        return
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows, payload = run_grid(config)
    csv_path = args.output_dir / "repertoire.csv"
    json_path = args.output_dir / "repertoire.json"
    write_csv(csv_path, rows)
    write_json(json_path, payload)
    print(
        json.dumps(
            {
                "csv": str(csv_path),
                "json": str(json_path),
                "generation_rows": len(rows),
                "runs": len(payload["run_summaries"]),
                "aggregates": len(payload["aggregates"]),
                "invariants": payload["invariants"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
