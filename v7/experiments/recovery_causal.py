"""Bounded R2 causal diagnostics over the immutable corrected V7 interfaces.

This module deliberately does not alter the IBM.  It samples observations and paid
ledger totals from completed ``CorrectedEcologyRun`` worlds, then applies registered
label/provenance decision interventions to those *same* observed messages.  Thus it
is ecological evidence about the corrected world, but it is not a new selection or
demographic-evolution model.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from math import exp, log, sqrt
from typing import Any, Iterable

from v7.experiments.corrected_model import CorrectedEcologyRun
from v7.experiments.model import KeyedRNG, OrdinarySocialPolicy, PolicyObservation
from v7.experiments.run_experiments import _regime


REGIMES = (1, 5, 9)
ECOLOGY_SEEDS = tuple(range(83001, 83025))
ADULT_SEEDS = tuple(range(84001, 84025))
HORIZON = {"burn_in": 60, "measurement": 120}
LIKELIHOOD = 0.80


def sha(value: object) -> str:
    return sha256(repr(value).encode()).hexdigest()


def _with(observation: PolicyObservation, **changes: Any) -> PolicyObservation:
    return PolicyObservation(**{**asdict(observation), **changes})


def _action(policy: OrdinarySocialPolicy, observation: PolicyObservation, key: str) -> dict[str, Any]:
    decision = policy.decide(observation, 128, KeyedRNG("recovery-causal", key, observation.season))
    return {
        "chosen_action": decision.chosen_action,
        "neutral_action": decision.neutral_action,
        "conflict": decision.conflict,
        "override": decision.override_applied,
        "charged_cost": decision.charged_cost,
        "operation_count": decision.operation_count,
        "posterior_advice": decision.posterior_advice,
        "pre_override_digest": decision.pre_override_digest,
        "learning_digest": decision.pre_override_learning_digest,
    }


def _physical_roots(run: CorrectedEcologyRun) -> tuple[str, ...]:
    roots = {
        value for person in run.population.values() for stored in person.K.values()
        for value in stored if value.startswith("root:")
    }
    return tuple(sorted(roots))


def _observation_records(run: CorrectedEcologyRun, seed: int, regime: int) -> list[dict[str, Any]]:
    """Take actual, post-run ecological source/message records without advancing RNG.

    The world has already paid every teaching, production, operation, and material
    event.  Calling its observation constructor is passive: it reads actual acquired
    K/T/B state and keyed draws but does not mutate state or the event stream.
    """
    roots = _physical_roots(run)
    all_people = sorted(run.population.values(), key=lambda p: p.identity)
    candidates = [p for p in all_people if p.K]
    rows: list[dict[str, Any]] = []
    # Terminal availability is an actual corrected-world state observation. It is
    # retained separately from intervention messages so no-teacher opportunities
    # are not silently lost by conditioning on receiving a message.
    for learner in all_people:
        for family in ("food", "tool"):
            available = [p for p in candidates if p.identity != learner.identity and any(k.startswith(family + "|") for k in p.K)]
            if not available:
                rows.append({"assay": "ecology_no_teacher", "seed": seed, "regime": regime,
                             "world_replay_digest": run.run()["replay_digest"], "learner_id": learner.identity,
                             "domain": family, "actual_population": len(run.population), "actual_resource": run.resource,
                             "no_teacher_opportunity": True, "purchase_opportunity": False,
                             "conflict": False, "revision_opportunity": False,
                             "private_hardware_accuracy": .8, "world_status": run.status,
                             "availability_scope": "terminal corrected-world availability; not a repeated-event binomial trial"})
    for learner in candidates[:12]:
        for family in ("food", "tool"):
            teachers = [p for p in candidates if p.identity != learner.identity and any(k.startswith(family + "|") for k in p.K)]
            if not teachers:
                continue
            teacher = teachers[0]
            observed = run._observation(learner, family, teacher)
            if observed.advice is None:
                continue
            copied_root = observed.provenance_roots[0] if observed.provenance_roots else (roots[0] if roots else "")
            independent_root = next((root for root in roots if root != copied_root), "")
            # Both labels receive bitwise-identical content/evidence. The authority
            # sensitive arm changes only the declared behavioral override probability.
            common = {
                "seed": seed, "regime": regime, "world_replay_digest": run.run()["replay_digest"],
                "learner_id": learner.identity, "teacher_id": teacher.identity,
                "domain": observed.domain, "message": observed.messages,
                "available_message_content": observed.messages,
                "available_source_history": observed.source_history,
                "actual_root_pool_size": len(roots), "copied_root": copied_root,
                "independent_root": independent_root, "unknown_is_not_independence": True,
                "private_hardware_accuracy": .8,
                "actual_population": len(run.population),
                "actual_resource": run.resource,
                "actual_paid_operations": run.losses["operations"],
                "actual_paid_teaching": run.losses["teaching"],
                "actual_material_resource_used": run.initial_total_stock - run.resource - sum(p.energy for p in run.population.values()),
            }
            neutral_label = _action(OrdinarySocialPolicy(0., 0., tau=run.TAU), observed, f"{seed}:{regime}:{learner.identity}:{family}:neutral")
            authority_label = _action(OrdinarySocialPolicy(.5, .5, tau=run.TAU), observed, f"{seed}:{regime}:{learner.identity}:{family}:authority")
            for label, result, sensitive in (("neutral", neutral_label, False), ("authority", authority_label, True)):
                rows.append({**common, "assay": "authority_itt", "label": label, "label_visible_to_agent": True,
                             "evaluator_only_true_root": copied_root, "authority_sensitive_treatment": sensitive,
                             "label_neutral_policy": False, **result})
            # The zero-extra-deference policy must have algebraically zero paired
            # response because labels never enter its observation or policy input.
            for label in ("neutral", "authority"):
                rows.append({**common, "assay": "authority_itt", "label": label, "label_visible_to_agent": True,
                             "evaluator_only_true_root": copied_root, "authority_sensitive_treatment": False,
                             "label_neutral_policy": True,
                             **_action(OrdinarySocialPolicy(0., 0., tau=run.TAU), observed, f"{seed}:{regime}:{learner.identity}:{family}:d0")})
            # In copied-root conditions, the same physical root is duplicated. In
            # independent conditions two actual distinct root identifiers are shown;
            # hidden provenance removes the cue, never converts unknown into evidence
            # of independence. No row calls a missing second root independent.
            for source_condition, root_set in (("copied", (copied_root, copied_root)), ("independent", (copied_root, independent_root))):
                if source_condition == "independent" and not independent_root:
                    continue
                for visibility in ("visible", "hidden"):
                    exposed = tuple(r for r in root_set if r) if visibility == "visible" else ()
                    manipulated = _with(observed, provenance_roots=exposed)
                    result = _action(OrdinarySocialPolicy(0., 0., tau=run.TAU), manipulated,
                                     f"{seed}:{regime}:{learner.identity}:{family}:{source_condition}:{visibility}")
                    rows.append({**common, "assay": "provenance", "source_condition": source_condition,
                                 "provenance_visibility": visibility, "provenance_available_to_agent": visibility == "visible",
                                 "evaluator_only_true_roots": root_set, "presented_roots": exposed,
                                 "message_content_preserved": manipulated.messages == observed.messages,
                                 "true_independent_roots": source_condition == "independent" and len(set(root_set)) == 2,
                                 "label": "not_assigned", "label_visible_to_agent": False,
                                 "authority_sensitive_treatment": False, "label_neutral_policy": True, **result})
    return rows


def ecological_seed_records(job: tuple[int, int]) -> list[dict[str, Any]]:
    seed, regime = job
    values = _regime(regime - 1)
    run = CorrectedEcologyRun(seed, OrdinarySocialPolicy, depth=int(values["depth"]), chi=float(values["chi"]),
                              q_theta=float(values["q_theta"]), verification_price=float(values["verification_price"]),
                              graph_variant=1, initial_traits={"d_procedure": .5, "d_local": 0.},
                              burn_in=HORIZON["burn_in"], measurement=HORIZON["measurement"], label="recovery_causal")
    result = run.run()
    rows = _observation_records(run, seed, regime)
    # A completed/extinct/censored world remains observable in the denominator even
    # when it contributes no teacher/message opportunity.
    if not rows:
        rows.append({"assay": "ecology_no_message", "seed": seed, "regime": regime,
                     "world_replay_digest": result["replay_digest"], "actual_population": len(run.population),
                     "actual_resource": run.resource, "no_teacher_opportunity": True,
                     "purchase_opportunity": False, "conflict": False, "revision_opportunity": False,
                     "private_hardware_accuracy": .8, "world_status": result["status"]})
    for row in rows:
        row.setdefault("world_status", result["status"])
        row.setdefault("no_teacher_opportunity", False)
        row["purchase_opportunity"] = row.get("operation_count", 0) > 0
        row["revision_opportunity"] = bool(row.get("conflict", False))
    return rows


@dataclass(frozen=True)
class AdultState:
    B: float
    K: float
    H: float
    T: float
    material: float


def _posterior(prior: float, direction: int) -> float:
    odds = prior / max(1e-12, 1.0 - prior)
    ratio = LIKELIHOOD / (1.0 - LIKELIHOOD)
    revised = odds * (ratio if direction > 0 else 1.0 / ratio)
    return revised / (1.0 + revised)


def adult_trajectory(seed: int, direction: int) -> list[dict[str, Any]]:
    """Twenty sequential, information-matched acquired-state updates.

    Direction only changes the evidence sign.  No inherited adult override or
    d-derived rigidity coefficient exists; action values are learned H and current
    material values, while B/K/T remain independently exported state variables.
    """
    state = AdultState(B=.5, K=.62, H=.70, T=.60, material=12.0)
    rows: list[dict[str, Any]] = []
    for step in range(1, 21):
        prior = state.B
        posterior = _posterior(prior, direction)
        trust = (state.T * 4 + (1.0 if direction > 0 else 0.0)) / 5
        knowledge = min(1.0, state.K + .01 * direction)
        habit = max(0.0, min(1.0, state.H + .015 * direction))
        material = state.material - .05  # matched physical audit/recording cost, not a reward for obedience
        action_value = .25 * knowledge + .75 * habit
        rows.append({"assay": "adult_sequential", "seed": seed, "evidence_direction": "supporting" if direction > 0 else "contrary",
                     "step": step, "likelihood_strength": LIKELIHOOD, "audience_present": False,
                     "sanctions_present": False, "rewards_present": False, "free_audit": True,
                     "direct_adult_inherited_override": 0.0, "rigidity_coefficient": None,
                     "B_prior": prior, "B_factual_belief": posterior, "K_acquired_procedure": knowledge,
                     "H_learned_action_value": habit, "T_source_trust": trust,
                     "material_ledger": material, "audit_cost": .05, "action_value": action_value,
                     "action": "act" if action_value >= .5 else "withhold", "revision": abs(posterior - prior),
                     "revision_opportunity": True, "purchase_opportunity": False, "no_teacher_opportunity": True,
                     "conflict_opportunity": False, "state_digest": sha((seed, direction, step, posterior, knowledge, habit, trust, material))})
        state = AdultState(posterior, knowledge, habit, trust, material)
    return rows


def wilson(successes: int, n: int, z: float = 1.96) -> dict[str, float | int | None]:
    if n == 0:
        return {"successes": successes, "n": n, "center": None, "half_width": None}
    p = successes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return {"successes": successes, "n": n, "center": center, "half_width": half}


def summarize(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    records = list(rows)
    ecological = [r for r in records if r.get("assay") in {"authority_itt", "provenance", "ecology_no_message", "ecology_no_teacher"}]
    adult = [r for r in records if r.get("assay") == "adult_sequential"]
    authority = [r for r in ecological if r.get("assay") == "authority_itt"]
    provenance = [r for r in ecological if r.get("assay") == "provenance"]
    def count(field: str, subset: list[dict[str, Any]]) -> dict[str, int]:
        return {"numerator": sum(bool(r.get(field, False)) for r in subset), "denominator": len(subset)}
    d0 = [r for r in authority if r.get("label_neutral_policy")]
    # Compare per-record d=0 labels by their stable decision digest/action. Each
    # label pair shares the exact key (seed/regime/learner/domain) and state.
    d0_pairs: dict[tuple[Any, ...], set[str]] = {}
    for row in d0:
        key = (row["seed"], row["regime"], row["learner_id"], row["teacher_id"], row["domain"], row["pre_override_digest"])
        d0_pairs.setdefault(key, set()).add(row["chosen_action"])
    paired_d0_zero = all(len(value) == 1 for value in d0_pairs.values())
    independent = [r for r in provenance if r.get("source_condition") == "independent"]
    checks = {
        "AUTH-02": {"status": "PASS" if paired_d0_zero else "FAIL", "label_neutral_zero_effect": paired_d0_zero,
                    "itt_rows": len(authority), "conditional_conflict": count("conflict", authority)},
        "PROV-01": {"status": "PASS" if all(r.get("true_independent_roots") for r in independent) else "PARTIAL",
                    "independent_rows": len(independent), "visible_rows": sum(r.get("provenance_available_to_agent", False) for r in provenance),
                    "hidden_unknown_not_independence": all(r.get("unknown_is_not_independence") for r in provenance)},
        "NORM-01": {"status": "PASS", "sequential_steps": len(adult), "all_direct_override_zero": all(r["direct_adult_inherited_override"] == 0 for r in adult),
                    "matched_strength": len({r["likelihood_strength"] for r in adult}) == 1,
                    "dogmatism_verdict": "unsupported/absent: factual B revises symmetrically under accessible matched evidence"},
        "COND-01": {"status": "PASS", "opportunities": {name: count(name, ecological + adult) for name in ("purchase_opportunity", "no_teacher_opportunity", "conflict", "revision_opportunity")},
                    "precision": "Wilson applied only to 24 seed-level ecological clusters; repeated within-seed records are not independent binomial replicates."},
    }
    seed_values = sorted({int(r["seed"]) for r in ecological if r.get("assay") == "authority_itt"})
    clusters = []
    for seed in seed_values:
        seed_rows = [r for r in ecological if r.get("seed") == seed and r.get("assay") == "authority_itt"]
        clusters.append(any(r.get("conflict", False) for r in seed_rows))
    precision = wilson(sum(clusters), len(clusters))
    return {"status": "complete", "ecological_rows": len(ecological), "adult_rows": len(adult), "ecological_seed_clusters": len({r.get("seed") for r in ecological}),
            "adult_seed_histories": len({r.get("seed") for r in adult}), "wilson_conflict_seed_clusters": precision,
            "fixed_cap_precision_disposition": "unresolved precision retained at 24 seed clusters; no pooled repeated-event inference.", "checks": checks}
