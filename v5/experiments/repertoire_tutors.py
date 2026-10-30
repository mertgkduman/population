"""Exploratory confidence-filtered tutor follow-up for the V5 repertoire model.

This post-main experiment compares a random prior-generation adult with a
cost-free search that samples only adults whose observable context-specific
conviction satisfies ``abs(b) >= 2``.  Correctness is never used for selection.
If no qualifying adult exists, no testimony is returned and private knowledge
is unchanged.  The experiment has no demography, fitness, or selection.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from repertoire import (
    Config,
    apply_adult_policy,
    apply_private_budget,
    knowledge_metrics,
    make_schedule,
    nested_quality_check,
    schedule_digest,
    update_score,
    validate_config,
)


TEACHER_FILTERS = ("random", "confidence_ge_2")
NEW_SEEDS = (800, 801, 802, 803, 804, 805)
FILTER_THRESHOLD = 2


CSV_FIELDS = (
    "run_id",
    "seed",
    "D",
    "p",
    "d",
    "policy",
    "environment",
    "teacher_filter",
    "generation",
    "shock_generation",
    "shock_applied",
    "adult_accuracy",
    "private_accuracy",
    "held_coverage",
    "private_coverage",
    "held_confidence",
    "wrong_high_confidence",
    "knowledge_heterogeneity",
    "juvenile_private_queries",
    "juvenile_social_encounters",
    "adult_queries",
    "teacher_accuracy",
    "teacher_accuracy_expressed",
    "teacher_coverage",
    "qualifying_pool_fraction_mean",
    "search_availability_rate",
    "qualifying_pool_wrong_share",
    "actual_endorsements",
    "correct_endorsements",
    "accepted_endorsements",
    "advice_accuracy_conditional",
    "child_conflicts",
    "child_overrides",
    "child_conflict_override_rate",
)


def experiment_config() -> Config:
    """Return the fixed post-main exploratory grid."""

    return replace(
        Config(),
        cue_qualities=(0.55, 0.70),
        seeds=NEW_SEEDS,
    )


def apply_social_with_filter(
    u: np.ndarray,
    b: np.ndarray,
    teacher_b: np.ndarray,
    contexts: np.ndarray,
    teacher_draws: np.ndarray,
    accept_uniforms: np.ndarray,
    override_uniforms: np.ndarray,
    tie_uniforms: np.ndarray,
    theta: np.ndarray,
    d: float,
    teacher_filter: str,
    bound: int,
) -> dict[str, float | int]:
    """Apply testimony selected randomly or by observable confidence only."""

    if teacher_filter not in TEACHER_FILTERS:
        raise ValueError(f"unknown teacher filter: {teacher_filter}")
    N, budget = contexts.shape
    rows = np.arange(N)
    testimonies = correct_endorsements = accepted = conflicts = overrides = 0
    availability_count = 0
    pool_fraction_sum = 0.0
    wrong_share_sum = 0.0
    wrong_share_denominator = 0

    # The same integer draw maps to all adults under random sampling and to a
    # rank within the qualifying set under confidence filtering.
    unit_draws = (teacher_draws.astype(float) + 0.5) / N
    for encounter in range(budget):
        context = contexts[:, encounter]
        selected_teacher = teacher_draws[:, encounter].astype(np.int64).copy()
        available = np.zeros(N, dtype=bool)
        wrong_share = np.zeros(N, dtype=float)
        pool_fraction = np.zeros(N, dtype=float)

        for fact in np.unique(context):
            children = np.flatnonzero(context == fact)
            candidates = np.flatnonzero(np.abs(teacher_b[:, fact]) >= FILTER_THRESHOLD)
            candidate_count = len(candidates)
            pool_fraction[children] = candidate_count / N
            if candidate_count:
                available[children] = True
                candidate_wrong = np.sign(teacher_b[candidates, fact]) != theta[fact]
                wrong_share[children] = float(np.mean(candidate_wrong))
                if teacher_filter == "confidence_ge_2":
                    ranks = np.minimum(
                        (unit_draws[children, encounter] * candidate_count).astype(int),
                        candidate_count - 1,
                    )
                    selected_teacher[children] = candidates[ranks]

        pool_fraction_sum += float(np.sum(pool_fraction))
        availability_count += int(np.sum(available))
        wrong_share_sum += float(np.sum(wrong_share[available]))
        wrong_share_denominator += int(np.sum(available))

        advice = np.sign(teacher_b[selected_teacher, context]).astype(np.int8)
        valid = advice != 0
        if teacher_filter == "confidence_ge_2":
            # Empty candidate sets return no testimony, even though the common
            # random adult may itself have a weak nonzero score.
            valid &= available
            advice[~valid] = 0
            if np.any(valid):
                selected_confidence = np.abs(
                    teacher_b[selected_teacher[valid], context[valid]]
                )
                if np.min(selected_confidence) < FILTER_THRESHOLD:
                    raise AssertionError("confidence filter selected an ineligible tutor")
        testimonies += int(np.sum(valid))
        correct_endorsements += int(np.sum(valid & (advice == theta[context])))

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

        if teacher_filter == "confidence_ge_2" and np.any((~available) & valid):
            raise AssertionError("testimony returned without a qualifying tutor")

    opportunities = N * budget
    return {
        "qualifying_pool_fraction_mean": pool_fraction_sum / opportunities,
        "search_availability_rate": availability_count / opportunities,
        "qualifying_pool_wrong_share": (
            wrong_share_sum / wrong_share_denominator if wrong_share_denominator else np.nan
        ),
        "actual_endorsements": testimonies,
        "correct_endorsements": correct_endorsements,
        "accepted_endorsements": accepted,
        "advice_accuracy_conditional": (
            correct_endorsements / testimonies if testimonies else np.nan
        ),
        "child_conflicts": conflicts,
        "child_overrides": overrides,
    }


def make_run_id(
    D: int,
    p: float,
    d: float,
    policy: str,
    environment: str,
    teacher_filter: str,
    seed: int,
) -> str:
    return (
        f"D{D}_p{p:.2f}_d{d:.1f}_{policy}_{environment}_"
        f"{teacher_filter}_s{seed}"
    ).replace(".", "p")


def simulate_run(
    config: Config,
    D: int,
    p: float,
    d: float,
    policy: str,
    environment: str,
    teacher_filter: str,
    seed: int,
    schedule: dict[str, np.ndarray],
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, float]]:
    N, H = config.cohort_size, config.score_bound
    theta = schedule["theta0"].copy()
    u = np.zeros((N, D), dtype=np.int8)
    b = np.zeros((N, D), dtype=np.int8)
    founder_queries = apply_private_budget(
        u,
        b,
        schedule["founder_context"],
        schedule["founder_quality"],
        theta,
        p,
        H,
    )
    identifier = make_run_id(D, p, d, policy, environment, teacher_filter, seed)
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
            "teacher_filter": teacher_filter,
            "generation": 0,
            "shock_generation": config.shock_generation,
            "shock_applied": False,
            "adult_accuracy": held["accuracy"],
            "private_accuracy": private["accuracy"],
            "held_coverage": held["coverage"],
            "private_coverage": private["coverage"],
            "held_confidence": held["confidence"],
            "wrong_high_confidence": held["wrong_high_confidence"],
            "knowledge_heterogeneity": held["knowledge_heterogeneity"],
            "juvenile_private_queries": 0.0,
            "juvenile_social_encounters": 0.0,
            "adult_queries": founder_queries / N,
            "teacher_accuracy": np.nan,
            "teacher_accuracy_expressed": np.nan,
            "teacher_coverage": np.nan,
            "qualifying_pool_fraction_mean": np.nan,
            "search_availability_rate": np.nan,
            "qualifying_pool_wrong_share": np.nan,
            "actual_endorsements": 0,
            "correct_endorsements": 0,
            "accepted_endorsements": 0,
            "advice_accuracy_conditional": np.nan,
            "child_conflicts": 0,
            "child_overrides": 0,
            "child_conflict_override_rate": np.nan,
        }
    ]
    max_d0_difference = 0
    max_absolute_score = int(max(np.max(np.abs(u)), np.max(np.abs(b))))

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
        social = apply_social_with_filter(
            u,
            b,
            teacher_b,
            schedule["social_context"][generation],
            schedule["social_teacher"][generation],
            schedule["social_accept"][generation],
            schedule["social_override"][generation],
            schedule["social_private_tie"][generation],
            theta,
            d,
            teacher_filter,
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
            if difference:
                raise AssertionError("d=0 must preserve u=b")
        max_absolute_score = max(
            max_absolute_score, int(np.max(np.abs(u))), int(np.max(np.abs(b)))
        )
        if max_absolute_score > H:
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
                "teacher_filter": teacher_filter,
                "generation": generation,
                "shock_generation": config.shock_generation,
                "shock_applied": shock_applied,
                "adult_accuracy": held["accuracy"],
                "private_accuracy": private["accuracy"],
                "held_coverage": held["coverage"],
                "private_coverage": private["coverage"],
                "held_confidence": held["confidence"],
                "wrong_high_confidence": held["wrong_high_confidence"],
                "knowledge_heterogeneity": held["knowledge_heterogeneity"],
                "juvenile_private_queries": juvenile_queries / N,
                "juvenile_social_encounters": float(config.juvenile_social_budget),
                "adult_queries": adult_queries / N,
                "teacher_accuracy": teacher["accuracy"],
                "teacher_accuracy_expressed": teacher["accuracy_expressed"],
                "teacher_coverage": teacher["coverage"],
                **social,
                "child_conflict_override_rate": conflict_rate,
            }
        )

    checks = {
        "max_d0_u_b_difference": float(max_d0_difference),
        "max_absolute_score": float(max_absolute_score),
        "founder_queries_per_adult": float(founder_queries / N),
    }
    return rows, summarize_run(config, rows), checks


def finite_or_none(value: float) -> float | None:
    return float(value) if np.isfinite(value) else None


def weighted_advice_accuracy(rows: list[dict[str, Any]]) -> float | None:
    total = sum(int(row["actual_endorsements"]) for row in rows)
    correct = sum(int(row["correct_endorsements"]) for row in rows)
    return correct / total if total else None


def summarize_run(config: Config, rows: list[dict[str, Any]]) -> dict[str, Any]:
    first, last = rows[0], rows[-1]
    shock = config.shock_generation
    pre_window = rows[shock - 3 : shock]
    post_rows = rows[shock:]
    data_rows = rows[1:]
    summary: dict[str, Any] = {
        key: first[key]
        for key in ("run_id", "seed", "D", "p", "d", "policy", "environment", "teacher_filter")
    }
    summary.update(
        {
            "founder_accuracy": float(first["adult_accuracy"]),
            "pre_shock_accuracy": float(np.mean([row["adult_accuracy"] for row in pre_window])),
            "end_accuracy": float(last["adult_accuracy"]),
            "end_private_accuracy": float(last["private_accuracy"]),
            "end_coverage": float(last["held_coverage"]),
            "end_wrong_high_confidence": float(last["wrong_high_confidence"]),
            "total_adult_queries_post_founder": float(
                sum(row["adult_queries"] for row in data_rows)
            ),
            "mean_candidate_pool_fraction": float(
                np.mean([row["qualifying_pool_fraction_mean"] for row in data_rows])
            ),
            "mean_search_availability": float(
                np.mean([row["search_availability_rate"] for row in data_rows])
            ),
            "mean_qualifying_pool_wrong_share": finite_or_none(
                float(
                    np.nanmean(
                        np.asarray(
                            [row["qualifying_pool_wrong_share"] for row in data_rows], dtype=float
                        )
                    )
                )
            ),
            "total_actual_endorsements": int(
                sum(row["actual_endorsements"] for row in data_rows)
            ),
            "total_accepted_endorsements": int(
                sum(row["accepted_endorsements"] for row in data_rows)
            ),
            "advice_accuracy_conditional": weighted_advice_accuracy(data_rows),
        }
    )
    if first["environment"] == "quarter_flip":
        shock_accuracy = float(rows[shock]["adult_accuracy"])
        pre_accuracy = float(summary["pre_shock_accuracy"])
        lost = pre_accuracy - shock_accuracy
        recovered = float(last["adult_accuracy"] - shock_accuracy)
        summary.update(
            {
                "shock_accuracy": shock_accuracy,
                "accuracy_drop": float(lost),
                "recovery_fraction_end": recovered / lost if lost > 0 else None,
                "post_shock_mean_accuracy": float(
                    np.mean([row["adult_accuracy"] for row in post_rows])
                ),
            }
        )
    else:
        summary.update(
            {
                "shock_accuracy": None,
                "accuracy_drop": None,
                "recovery_fraction_end": None,
                "post_shock_mean_accuracy": None,
            }
        )
    return summary


def make_filter_pairs(summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    key_fields = ("seed", "D", "p", "d", "policy", "environment")
    pair_fields = (
        "end_accuracy",
        "end_private_accuracy",
        "end_coverage",
        "end_wrong_high_confidence",
        "total_adult_queries_post_founder",
        "mean_candidate_pool_fraction",
        "mean_search_availability",
        "mean_qualifying_pool_wrong_share",
        "total_actual_endorsements",
        "total_accepted_endorsements",
        "advice_accuracy_conditional",
        "shock_accuracy",
        "accuracy_drop",
        "recovery_fraction_end",
        "post_shock_mean_accuracy",
    )
    grouped: dict[tuple[Any, ...], dict[str, dict[str, Any]]] = defaultdict(dict)
    for summary in summaries:
        grouped[tuple(summary[key] for key in key_fields)][summary["teacher_filter"]] = summary

    pairs: list[dict[str, Any]] = []
    for key, filters in sorted(grouped.items(), key=lambda item: item[0]):
        if set(filters) != set(TEACHER_FILTERS):
            raise AssertionError("incomplete teacher-filter pair")
        random = filters["random"]
        selected = filters["confidence_ge_2"]
        row: dict[str, Any] = dict(zip(key_fields, key))
        for field in pair_fields:
            random_value = random[field]
            selected_value = selected[field]
            row[f"random_{field}"] = random_value
            row[f"filtered_{field}"] = selected_value
            row[f"delta_{field}"] = (
                float(selected_value - random_value)
                if random_value is not None and selected_value is not None
                else None
            )
        pairs.append(row)
    return pairs


def aggregate_pairs(pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    group_fields = ("D", "p", "d", "policy", "environment")
    delta_fields = tuple(key for key in pairs[0] if key.startswith("delta_"))
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for pair in pairs:
        grouped[tuple(pair[key] for key in group_fields)].append(pair)
    output: list[dict[str, Any]] = []
    for key, values in sorted(grouped.items(), key=lambda item: item[0]):
        row: dict[str, Any] = dict(zip(group_fields, key))
        row["n_seeds"] = len(values)
        for field in delta_fields:
            observed = np.asarray(
                [value[field] for value in values if value[field] is not None], dtype=float
            )
            row[f"{field}_n"] = int(observed.size)
            row[f"{field}_mean"] = float(np.mean(observed)) if observed.size else None
            row[f"{field}_sd"] = (
                float(np.std(observed, ddof=1))
                if observed.size > 1
                else (0.0 if observed.size else None)
            )
        output.append(row)
    return output


def build_invariants(
    config: Config,
    rows: list[dict[str, Any]],
    checks: list[dict[str, float]],
    nested_checks: list[bool],
) -> dict[str, Any]:
    d0_pairs: dict[tuple[Any, ...], dict[str, tuple[float, ...]]] = defaultdict(dict)
    environment_pairs: dict[tuple[Any, ...], dict[str, tuple[float, ...]]] = defaultdict(dict)
    for row in rows:
        if row["d"] == 0:
            key = (
                row["seed"], row["D"], row["p"], row["policy"], row["environment"], row["generation"]
            )
            d0_pairs[key][row["teacher_filter"]] = (
                float(row["adult_accuracy"]),
                float(row["private_accuracy"]),
                float(row["held_coverage"]),
                float(row["adult_queries"]),
            )
        if row["generation"] < config.shock_generation:
            key = (
                row["seed"],
                row["D"],
                row["p"],
                row["d"],
                row["policy"],
                row["teacher_filter"],
                row["generation"],
            )
            environment_pairs[key][row["environment"]] = (
                float(row["adult_accuracy"]),
                float(row["private_accuracy"]),
                float(row["held_coverage"]),
            )
    d0_filter_difference = max(
        max(abs(a - b) for a, b in zip(pair["random"], pair["confidence_ge_2"]))
        for pair in d0_pairs.values()
    )
    pre_shock_environment_difference = max(
        max(abs(a - b) for a, b in zip(pair["stable"], pair["quarter_flip"]))
        for pair in environment_pairs.values()
    )
    max_d0_u_b = max(check["max_d0_u_b_difference"] for check in checks)
    max_score = max(check["max_absolute_score"] for check in checks)
    founder_queries = sorted({check["founder_queries_per_adult"] for check in checks})
    invariants = {
        "d0_u_equals_b": {
            "passed": max_d0_u_b == 0,
            "maximum_absolute_difference": max_d0_u_b,
        },
        "d0_teacher_filter_match": {
            "passed": d0_filter_difference == 0,
            "maximum_accuracy_coverage_or_query_difference": d0_filter_difference,
        },
        "matched_environment_pre_shock": {
            "passed": pre_shock_environment_difference == 0,
            "maximum_metric_difference": pre_shock_environment_difference,
        },
        "matched_cue_quality": {
            "passed": all(nested_checks),
            "description": "Common uniform cue draws give nested correct-cue sets across p.",
        },
        "founder_learning": {
            "passed": founder_queries == [float(config.founder_private_budget)],
            "query_counts_per_adult_observed": founder_queries,
            "starts_from_fixed_accuracy": False,
        },
        "score_bounds": {
            "passed": max_score <= config.score_bound,
            "maximum_absolute_score": max_score,
            "bound": config.score_bound,
        },
        "teacher_filter_information": {
            "passed": True,
            "selection_rule": "abs(b_context) >= 2 only",
            "uses_correctness": False,
            "no_qualifying_teacher_result": "no testimony",
            "search_cost": 0.0,
        },
    }
    if not all(block["passed"] for block in invariants.values()):
        raise AssertionError(invariants)
    return invariants


def run_grid(config: Config) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    validate_config(config)
    rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    checks: list[dict[str, float]] = []
    nested_checks: list[bool] = []
    schedule_hashes: list[dict[str, Any]] = []
    for D in config.context_counts:
        for seed in config.seeds:
            schedule = make_schedule(config, D, seed)
            schedule_hashes.append({"D": D, "seed": seed, "sha256": schedule_digest(schedule)})
            nested_checks.append(nested_quality_check(config, schedule))
            for p in config.cue_qualities:
                for d in config.deference:
                    for policy in config.policies:
                        for environment in config.environments:
                            for teacher_filter in TEACHER_FILTERS:
                                run_rows, summary, run_checks = simulate_run(
                                    config,
                                    D,
                                    p,
                                    d,
                                    policy,
                                    environment,
                                    teacher_filter,
                                    seed,
                                    schedule,
                                )
                                rows.extend(run_rows)
                                summaries.append(summary)
                                checks.append(run_checks)
    pairs = make_filter_pairs(summaries)
    payload = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "exploratory_status": "Post-main mechanism-identification follow-up prompted by observed repertoire dilution; not a preregistered confirmation.",
        "model_scope": "Independent binary-fact cultural learning only; no demography, fitness, reproduction weighting, selection, cooperation, or combinatorial reasoning.",
        "predeclared_parameters": {
            **asdict(config),
            "teacher_filters": TEACHER_FILTERS,
            "confidence_filter_threshold": FILTER_THRESHOLD,
            "confidence_filter_search_cost": 0.0,
        },
        "teacher_filter_definition": {
            "random": "One random prior-generation adult; b=0 returns no testimony.",
            "confidence_ge_2": "Uniformly sample among prior-generation adults with abs(b_context)>=2; if none exist, return no testimony. Correctness is unavailable to selection.",
            "caveat": "The confidence filter searches the full cohort without time, mortality, or opportunity cost. Candidate-pool fraction, search availability, and actual endorsements are reported so this advantage is not interpreted as free-search optimality.",
        },
        "common_random_numbers": {
            "description": "Within each D/seed block, teacher-filter pairs share truths, flip masks, sampled contexts, teacher-choice variates, cue uniforms, acceptance/override/tie uniforms, and adult audit uniforms.",
            "schedule_hashes": schedule_hashes,
        },
        "metric_definitions": {
            "qualifying_pool_fraction_mean": "Mean fraction of prior adults satisfying abs(b_context)>=2 for the encountered context, reported for both filters.",
            "search_availability_rate": "Fraction of social encounters for which at least one abs(b_context)>=2 adult exists.",
            "qualifying_pool_wrong_share": "Mean share of qualifying adults whose sign is wrong, conditional on an available pool; never used for selection.",
            "actual_endorsements": "Number of encounters returning a nonzero selected adult sign.",
            "advice_accuracy_conditional": "Correct selected signs divided by actual endorsements; absent when no endorsement is available.",
            "private_accuracy": "Raw private-ledger correctness with u=0 scored 0.5.",
            "adult_accuracy": "Held-ledger correctness with b=0 scored 0.5.",
        },
        "invariants": build_invariants(config, rows, checks, nested_checks),
        "run_summaries": summaries,
        "filter_pairs": pairs,
        "pair_aggregates": aggregate_pairs(pairs),
    }
    return rows, payload


def write_csv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, allow_nan=False)
        handle.write("\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
    )
    parser.add_argument("--self-test-only", action="store_true")
    return parser.parse_args()


def lightweight_self_test(config: Config) -> dict[str, Any]:
    schedule = make_schedule(config, 4, config.seeds[0])
    random_rows, _, random_checks = simulate_run(
        config, 4, 0.70, 0.0, "retained_update", "quarter_flip", "random", config.seeds[0], schedule
    )
    filtered_rows, _, filtered_checks = simulate_run(
        config,
        4,
        0.70,
        0.0,
        "retained_update",
        "quarter_flip",
        "confidence_ge_2",
        config.seeds[0],
        schedule,
    )
    maximum_filter_difference = max(
        abs(float(a[field]) - float(b[field]))
        for a, b in zip(random_rows, filtered_rows)
        for field in ("adult_accuracy", "private_accuracy", "held_coverage", "adult_queries")
    )
    result = {
        "d0_filter_match": maximum_filter_difference == 0,
        "d0_u_equals_b": max(
            random_checks["max_d0_u_b_difference"],
            filtered_checks["max_d0_u_b_difference"],
        )
        == 0,
        "nested_quality": nested_quality_check(config, schedule),
        "bounded": max(
            random_checks["max_absolute_score"], filtered_checks["max_absolute_score"]
        )
        <= config.score_bound,
        "generation_rows": len(random_rows) + len(filtered_rows),
    }
    if not all(value for value in result.values() if isinstance(value, bool)):
        raise AssertionError(result)
    return result


def main() -> None:
    args = parse_args()
    config = experiment_config()
    if args.self_test_only:
        print(json.dumps(lightweight_self_test(config), indent=2))
        return
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows, payload = run_grid(config)
    csv_path = args.output_dir / "repertoire_tutors.csv"
    json_path = args.output_dir / "repertoire_tutors.json"
    write_csv(csv_path, rows)
    write_json(json_path, payload)
    print(
        json.dumps(
            {
                "csv": str(csv_path),
                "json": str(json_path),
                "generation_rows": len(rows),
                "runs": len(payload["run_summaries"]),
                "filter_pairs": len(payload["filter_pairs"]),
                "pair_aggregates": len(payload["pair_aggregates"]),
                "invariants": payload["invariants"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
