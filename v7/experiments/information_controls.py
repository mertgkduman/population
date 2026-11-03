"""R4 information, authority/provenance, and memory-acceptance controls.

This is deliberately a small fixed-proposition cognitive assay.  It is not an
IBM, demographic mapping, invasion experiment, or claim about evolved
authority responsiveness.  All random-looking draws are keyed, so paired
counterfactual labels and override policies consume the same realised evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from math import exp, log
from typing import Any

ACCURACY = 0.8
TUTOR_ACCURACY = 3 * ACCURACY**2 - 2 * ACCURACY**3  # majority of three
# attempt_003 clean confirmation blocks; prior 83301/84301 blocks are retained
# as attempt evidence and are never relabelled as this confirmation.
INFO_SEEDS = tuple(range(83351, 83375))
MEMORY_SEEDS = tuple(range(84351, 84375))
PILOT_INFO_SEED = 83350
PILOT_MEMORY_SEED = 84350


def keyed_uniform(*key: object) -> float:
    return int.from_bytes(sha256(repr(key).encode()).digest()[:8], "big") / 2**64


def signal(truth: int, accuracy: float, *key: object) -> int:
    return truth if keyed_uniform(*key) < accuracy else 1 - truth


def logistic(log_odds: float) -> float:
    return 1 / (1 + exp(-log_odds)) if log_odds >= 0 else exp(log_odds) / (1 + exp(log_odds))


def logit(probability: float) -> float:
    """Finite ledger representation; evidence remains unchanged at the boundary."""
    bounded = min(1 - 1e-12, max(1e-12, probability))
    return log(bounded / (1 - bounded))


def update(log_odds: float, observation: int, accuracy: float) -> float:
    return log_odds + (1 if observation else -1) * log(accuracy / (1 - accuracy))


def digest(value: object) -> str:
    return sha256(repr(value).encode()).hexdigest()


def posterior_from_likelihood(one: float, zero: float) -> float:
    """Equal-prior posterior, retaining exact finite likelihood calculations."""
    return one / (one + zero)


def message_likelihood(messages: tuple[int, int], truth: int, provenance: str) -> float:
    """Likelihood under visible provenance; copied messages have one root."""
    q = TUTOR_ACCURACY
    likelihood = lambda message: q if message == truth else 1 - q
    if provenance == "independent":
        return likelihood(messages[0]) * likelihood(messages[1])
    if provenance == "copied":
        return likelihood(messages[0]) if messages[0] == messages[1] else 0.0
    raise ValueError(provenance)


def public_posterior(messages: tuple[int, int], provenance: str, visible: bool) -> float:
    """Root-aware posterior; hidden status is a literal .5 structure mixture."""
    if visible:
        one = message_likelihood(messages, 1, provenance)
        zero = message_likelihood(messages, 0, provenance)
    else:
        one = .5 * message_likelihood(messages, 1, "independent") + .5 * message_likelihood(messages, 1, "copied")
        zero = .5 * message_likelihood(messages, 0, "independent") + .5 * message_likelihood(messages, 0, "copied")
    return posterior_from_likelihood(one, zero)


def enumerate_binary_histories() -> list[dict[str, Any]]:
    """Exact histories and likelihoods used as an executable benchmark."""
    rows: list[dict[str, Any]] = []
    for truth, history in product((0, 1), product((0, 1), repeat=3)):
        likelihood = 1.0
        for observation in history:
            likelihood *= ACCURACY if observation == truth else 1 - ACCURACY
        log_odds = 0.0
        for observation in history:
            log_odds = update(log_odds, observation, ACCURACY)
        rows.append({"truth": truth, "history": list(history), "likelihood": likelihood,
                     "posterior_truth_one": logistic(log_odds), "conviction": int(log_odds >= 0)})
    return rows


def exact_benchmark() -> dict[str, Any]:
    histories = enumerate_binary_histories()
    q = sum(r["likelihood"] for r in histories if r["conviction"] == r["truth"] and r["truth"] == 1)
    # For truth=1 this is the tutor-majority probability; symmetry supplies truth=0.
    copy_once = public_posterior((1, 1), "copied", True)
    independent_twice = public_posterior((1, 1), "independent", True)
    hidden = public_posterior((1, 1), "copied", False)
    return {"histories": histories, "q_tutor_enumerated": q, "q_tutor_formula": TUTOR_ACCURACY,
            "visible_copy_posterior": copy_once, "visible_copy_duplicate_invariant": copy_once == public_posterior((1, 1), "copied", True),
            "visible_independent_posterior": independent_twice, "hidden_mixture_posterior": hidden,
            "hidden_mixture_weight": .5}


@dataclass(frozen=True)
class Tutor:
    tutor_id: str
    truth: int
    observations: tuple[int, int, int]
    posterior: float
    conviction: int
    paid_training_cost: float
    root_id: str


def acquire_tutor(seed: int, tutor_id: str, truth: int) -> Tutor:
    observations = tuple(signal(truth, ACCURACY, "information", seed, tutor_id, "private", age) for age in range(3))
    L = 0.0
    for observation in observations:
        L = update(L, observation, ACCURACY)
    return Tutor(tutor_id, truth, observations, logistic(L), int(L >= 0), .3, f"root:{seed}:{tutor_id}")


def _child_decision(seed: int, truth: int, messages: tuple[int, int], provenance: str, visible: bool,
                    role_label: str, policy: str) -> dict[str, Any]:
    private = signal(truth, ACCURACY, "information", seed, "child", "private")
    public = public_posterior(messages, provenance, visible)
    public_L = log(public / (1 - public))
    private_L = log(ACCURACY / (1 - ACCURACY)) * (1 if private else -1)
    combined = logistic(public_L + private_L)
    neutral_action = int(combined >= .5)
    advice = messages[0]
    conflict = neutral_action != advice
    d = {"label_neutral_d0": 0.0, "generic_source_dhalf": .5,
         "authority_sensitive": .5 if role_label == "authority" else 0.0}[policy]
    # Same evidence/role comparison uses exactly this common stream; policy never
    # changes the stream or the information acquired before arbitration.
    override_draw = keyed_uniform("information", seed, provenance, visible, "common-override")
    override = conflict and override_draw < d
    action = advice if override else neutral_action
    receipt = 1.0 if action == truth else -1.0
    return {"child_private_observation": private, "child_private_accuracy": ACCURACY,
            "public_posterior": public, "private_plus_social_Q0": combined,
            "neutral_action": neutral_action, "advice": advice, "conflict": conflict,
            "override_probability": d, "common_override_draw": override_draw,
            "override": override, "action": action, "action_correct": action == truth,
            "material_receipt": receipt, "receipt_cost": .1, "payoff": receipt - .1}


def information_rows(seed: int) -> list[dict[str, Any]]:
    """Two actual tutors, then copied/independent x visible/hidden label trials."""
    truth = int(keyed_uniform("information", seed, "truth") >= .5)
    tutor_a, tutor_b = acquire_tutor(seed, "tutorA", truth), acquire_tutor(seed, "tutorB", truth)
    rows: list[dict[str, Any]] = []
    for tutor in (tutor_a, tutor_b):
        rows.append({"assay": "tutor_acquisition", "seed": seed, "truth": truth, "tutor_id": tutor.tutor_id,
                     "private_evidence_history": list(tutor.observations), "formed_private_posterior": tutor.posterior,
                     "formed_private_conviction": tutor.conviction, "paid_training_cost": tutor.paid_training_cost,
                     "physical_root_origin": tutor.root_id, "initial_belief_blank": True})
    for provenance, visible in product(("independent", "copied"), (False, True)):
        messages = (tutor_a.conviction, tutor_b.conviction) if provenance == "independent" else (tutor_a.conviction, tutor_a.conviction)
        roots = (tutor_a.root_id, tutor_b.root_id) if provenance == "independent" else (tutor_a.root_id, tutor_a.root_id)
        for role_label, policy in product(("peer", "authority"), ("label_neutral_d0", "generic_source_dhalf", "authority_sensitive")):
            decision = _child_decision(seed, truth, messages, provenance, visible, role_label, policy)
            rows.append({"assay": "authority_provenance_child", "seed": seed, "truth": truth,
                         "provenance_structure": provenance, "provenance_visible": visible,
                         "hidden_structure_prior_independent": .5 if not visible else None,
                         "role_label": role_label, "role_label_uninformative": True,
                         "policy": policy, "policy_is_imposed_positive_control": policy == "authority_sensitive",
                         "tutorA_private_history": list(tutor_a.observations), "tutorA_private_posterior": tutor_a.posterior,
                         "tutorB_private_history": list(tutor_b.observations), "tutorB_private_posterior": tutor_b.posterior,
                         "public_messages": list(messages), "public_message_roots": list(roots),
                         "public_message_confidences": [tutor_a.posterior, tutor_b.posterior if provenance == "independent" else tutor_a.posterior],
                         "copied_tutorB_private_belief_saved_separately": tutor_b.posterior,
                         "all_training_costs": tutor_a.paid_training_cost + tutor_b.paid_training_cost,
                         "child_budget_before": 10.0, "child_budget_after_receipt_cost": 9.9,
                         "pre_override_digest": digest((truth, tutor_a.observations, tutor_b.observations, messages, roots, visible)),
                         **decision})
    return rows


def _memory_initial(seed: int, memory_acceptance: int) -> dict[str, Any]:
    return {"B": 0.5, "K": 0, "T": .5, "H": [0.0, 0.0], "budget": 10.0,
            "accepted_memory": None, "source_root_memory": None, "memory_acceptance": memory_acceptance,
            "initial_blank": True}


def memory_training(seed: int, memory_acceptance: int, juvenile_d: float) -> list[dict[str, Any]]:
    """Forty actual training episodes; override is action-only and post-Q0."""
    truth = int(keyed_uniform("memory", seed, "truth") >= .5)
    state = _memory_initial(seed, memory_acceptance)
    rows: list[dict[str, Any]] = []
    for episode in range(40):
        private = signal(truth, ACCURACY, "memory", seed, "private", episode)
        testimony = signal(truth, .7, "memory", seed, "testimony", episode)
        B_before, K_before, H_before, T_before, budget_before = state["B"], state["K"], list(state["H"]), state["T"], state["budget"]
        L = logit(B_before); L = update(L, private, ACCURACY); B_after_evidence = logistic(L)
        neutral = int(B_after_evidence >= .5); conflict = neutral != testimony
        override_draw = keyed_uniform("memory", seed, "common-override", episode)
        override = conflict and override_draw < juvenile_d
        action = testimony if override else neutral
        feedback = signal(truth, ACCURACY, "memory", seed, "physical-feedback", episode)
        receipt = 1.0 if action == feedback else -1.0
        cost = .1
        state["B"] = B_after_evidence
        state["K"] = int(bool(K_before) or action == feedback)
        state["T"] = (4 * T_before + float(testimony == feedback)) / 5
        state["H"][action] = .85 * state["H"][action] + .15 * (receipt - cost)
        state["budget"] -= cost; state["budget"] += receipt
        if memory_acceptance and state["accepted_memory"] is None:
            state["accepted_memory"] = {"factual_testimony": testimony, "procedural_action": testimony, "episode": episode}
            state["source_root_memory"] = f"memory-root:{seed}"
        rows.append({"assay": "memory_training", "seed": seed, "truth": truth, "memory_acceptance": memory_acceptance,
                     "juvenile_d": juvenile_d, "episode": episode, "private": private, "testimony": testimony,
                     "feedback": feedback, "B_before": B_before, "B_after": state["B"], "K_before": K_before,
                     "K_after": state["K"], "T_before": T_before, "T_after": state["T"], "H_before": H_before,
                     "H_after": list(state["H"]), "budget_before": budget_before, "budget_after": state["budget"],
                     "neutral_action": neutral, "conflict": conflict, "override_draw_common_d": override_draw,
                     "override": override, "action": action, "material_receipt": receipt, "receipt_cost": cost,
                     "accepted_memory": state["accepted_memory"], "source_root_memory": state["source_root_memory"],
                     "pre_override_digest": digest((memory_acceptance, episode, B_before, K_before, H_before, T_before, budget_before, private, testimony))})
    return rows


def adult_reuse(seed: int, memory_acceptance: int, juvenile_d: float, training_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Twenty genuine adult updates, all with direct inherited override fixed at zero."""
    last = training_rows[-1]; truth = last["truth"]
    B, K, T, H, budget = last["B_after"], last["K_after"], last["T_after"], list(last["H_after"]), last["budget_after"]
    memory = last["accepted_memory"]; root = last["source_root_memory"]
    rows: list[dict[str, Any]] = []
    for step in range(20):
        private = signal(truth, ACCURACY, "memory", seed, "adult-private", step)
        adult_message = signal(truth, .7, "memory", seed, "adult-message", step)
        B_before, K_before, H_before, T_before, budget_before = B, K, list(H), T, budget
        L = update(logit(B), private, ACCURACY); B = logistic(L)
        neutral = int(B >= .5)
        # Receipt and message costs are identical regardless of juvenile arm/d.
        action = neutral
        feedback = signal(truth, ACCURACY, "memory", seed, "adult-feedback", step)
        receipt, cost = (1.0 if action == feedback else -1.0), .1
        H[action] = .85 * H[action] + .15 * (receipt - cost)
        T = (4 * T + float(adult_message == feedback)) / 5; budget += receipt - cost
        rows.append({"assay": "adult_memory_reuse", "seed": seed, "truth": truth, "memory_acceptance": memory_acceptance,
                     "juvenile_d": juvenile_d, "step": step, "direct_adult_inherited_override": 0.0,
                     "private": private, "adult_message": adult_message, "feedback": feedback,
                     "B_before": B_before, "B_after": B, "K_before": K_before, "K_after": K,
                     "T_before": T_before, "T_after": T, "H_before": H_before, "H_after": list(H),
                     "budget_before": budget_before, "budget_after": budget, "neutral_action": neutral, "action": action,
                     "material_receipt": receipt, "receipt_cost": cost, "stored_memory": memory,
                     "stored_memory_reused": memory is not None, "stored_source_root": root,
                     "adult_source_root_once": root, "environment_status": "fixed"})
    return rows


def memory_rows(seed: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for memory_acceptance, juvenile_d in product((0, 1), (0.0, .5)):
        training = memory_training(seed, memory_acceptance, juvenile_d)
        rows.extend(training); rows.extend(adult_reuse(seed, memory_acceptance, juvenile_d, training))
    return rows
