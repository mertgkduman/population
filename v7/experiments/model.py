"""Truth-firewalled decision kernel used by the V7 IBM and tiny-world oracle.

``WorldState`` is evaluator-only. Policies derive estimates from private likelihoods,
calibrated source records, and *unique* physical provenance roots. Actions are never
evidence: B (belief), K (procedure memory), and T (source calibration) update through
separate explicit APIs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque
from hashlib import sha256
from math import exp, log
from typing import Any, Iterable, Mapping, Protocol
import time

_POLICY_FIELDS = frozenset({"identity", "season", "age", "energy", "time_tokens", "computation_budget", "domain", "private_cue", "beliefs", "procedures", "trust", "habits", "messages", "provenance_roots", "feasible_actions", "action_values", "prices", "advice", "source_id", "source_history", "context_mismatch"})
_TRUTH_FIELDS = frozenset({"theta", "z", "correct_action", "source_competence", "future_change", "evaluator_label", "resource_pool", "truth", "world"})


def _freeze_map(values: Mapping[str, float] | Iterable[tuple[str, float]]) -> tuple[tuple[str, float], ...]:
    return tuple(sorted((str(k), float(v)) for k, v in (values.items() if isinstance(values, Mapping) else values)))


def _map(values: Iterable[tuple[str, float]]) -> dict[str, float]: return dict(values)
def _clip_probability(value: float) -> float: return max(1e-9, min(1.0 - 1e-9, float(value)))
def _logit(value: float) -> float:
    value = _clip_probability(value); return log(value / (1.0 - value))
def _logistic(value: float) -> float: return 1.0 / (1.0 + exp(-max(-40.0, min(40.0, value))))


@dataclass(frozen=True)
class WorldState:
    """Evaluator-only latent state. It cannot satisfy ``Policy.decide``'s type."""
    theta: int
    z: int
    resource_pool: float = 0.0
    source_competence: tuple[tuple[str, float], ...] = ()
    future_change: int | None = None
    evaluator_labels: tuple[tuple[str, str], ...] = ()
    @classmethod
    def fixture(cls, theta: int = 0, z: int = 0) -> "WorldState": return cls(theta, z, 1600.0)


@dataclass(frozen=True)
class PolicyObservation:
    """Only observed history, likelihood summaries, feasible acts, and posted prices."""
    identity: str; season: int; age: int; energy: float; time_tokens: int; computation_budget: int
    domain: str; private_cue: str; beliefs: tuple[tuple[str, float], ...]; procedures: tuple[str, ...]
    trust: tuple[tuple[str, float], ...]; habits: tuple[tuple[str, float], ...]
    messages: tuple[tuple[str, str], ...]; provenance_roots: tuple[str, ...]
    feasible_actions: tuple[str, ...]; action_values: tuple[tuple[str, float], ...]
    prices: tuple[tuple[str, float], ...]; advice: str | None; source_id: str | None = None
    source_history: tuple[tuple[str, float], ...] = (); context_mismatch: float = 0.0
    def __post_init__(self) -> None:
        if self.domain not in {"procedure", "local"}: raise ValueError("domain must be procedure or local")
        if not self.feasible_actions or set(_map(self.action_values)) != set(self.feasible_actions): raise ValueError("action values must cover exactly feasible actions")
        if self.advice is not None and self.advice not in self.feasible_actions: raise ValueError("advice must be feasible")
        if min(self.time_tokens, self.computation_budget, self.age) < 0: raise ValueError("budgets and age must be non-negative")
    def to_policy_dict(self) -> dict[str, Any]:
        return {name: (list(value) if isinstance(value, tuple) else value) for name, value in self.__dict__.items()}
    @classmethod
    def contract_fixture(cls, conflict: bool = True, age: int = 3) -> "PolicyObservation":
        advice = "teacher" if conflict else "private"
        return cls("fixture-agent", 0, age, 8.0, 12, 128, "procedure", "supports_private", (("p_advice", .30), ("private_likelihood", .80)), ("prefix-1",), (("tutor", .75),), (), (("demonstration", "teacher"),), ("trial-root-1",), ("private", "teacher"), (("private", 1.0), ("teacher", 1.0)), (("operation", .01), ("query", .10), ("verify", .20), ("correct_reward", 3.0), ("incorrect_loss", 2.0)), advice, "tutor", (("successes", 6.0), ("failures", 2.0)), 0.0)


def validate_policy_observation(value: PolicyObservation | Mapping[str, Any]) -> PolicyObservation:
    if isinstance(value, PolicyObservation): return value
    keys, forbidden, unknown = set(value), set(value) & _TRUTH_FIELDS, set(value) - _POLICY_FIELDS
    if forbidden or unknown: raise ValueError("policy observation contains forbidden or unknown fields")
    missing = _POLICY_FIELDS - {"source_id", "source_history", "context_mismatch"} - keys
    if missing: raise ValueError(f"policy observation misses fields: {sorted(missing)}")
    return PolicyObservation(str(value["identity"]), int(value["season"]), int(value["age"]), float(value["energy"]), int(value["time_tokens"]), int(value["computation_budget"]), str(value["domain"]), str(value["private_cue"]), _freeze_map(value["beliefs"]), tuple(value["procedures"]), _freeze_map(value["trust"]), _freeze_map(value["habits"]), tuple(tuple(x) for x in value["messages"]), tuple(value["provenance_roots"]), tuple(value["feasible_actions"]), _freeze_map(value["action_values"]), _freeze_map(value["prices"]), value["advice"], value.get("source_id"), _freeze_map(value.get("source_history", ())), float(value.get("context_mismatch", 0.0)))


@dataclass(frozen=True)
class KeyedRNG:
    replicate: str = "0"; graph: str = "0"; season: int = 0
    @classmethod
    def fixture(cls, replicate: str) -> "KeyedRNG": return cls(replicate, "fixture", 0)
    def draw(self, namespace: str, *, entity: int | str, ordinal: int = 0, event_type: str = "draw") -> float:
        if namespace not in {"environment", "observation", "innovation", "demography", "task_outcome", "override"}: raise ValueError("unknown keyed RNG namespace")
        material = "|".join(map(str, (namespace, self.replicate, self.graph, self.season, entity, event_type, ordinal)))
        return int.from_bytes(sha256(material.encode()).digest()[:8], "big") / 2**64


@dataclass(frozen=True)
class LedgerEvent:
    event_id: str; kind: str; learner_id: str | None = None; teacher_id: str | None = None
    learner_time_debit: int = 0; teacher_time_debit: int = 0; learner_energy_delta: float = 0.0; teacher_energy_delta: float = 0.0; material_delta: float = 0.0; operation_charge: float = 0.0; physical_outcome: str | None = None; biological_edge: tuple[str, str] | None = None; cultural_edge: tuple[str, str] | None = None
    parent_energy_debit: float = 0.0; birth_cost: float = 0.0; newborn_energy_credit: float = 0.0
    def transfer_residual(self) -> float: return self.learner_energy_delta + self.teacher_energy_delta + self.material_delta


@dataclass(frozen=True)
class AcquiredState:
    beliefs: tuple[tuple[str, float], ...] = (); procedures: tuple[str, ...] = (); trust: tuple[tuple[str, float], ...] = (); habits: tuple[tuple[str, float], ...] = (); provenance_roots: tuple[str, ...] = (); independent_successes: int = 0
    @classmethod
    def blank(cls) -> "AcquiredState": return cls()
    @property
    def may_teach(self) -> bool: return bool(self.procedures) and self.independent_successes >= 2


# These named updates make it impossible for executing an action to silently change B/K/T.
def update_beliefs(state: AcquiredState, likelihood_ratio: float, key: str = "procedure") -> AcquiredState:
    beliefs = _map(state.beliefs); beliefs[key] = _logistic(_logit(beliefs.get(key, .5)) + log(max(likelihood_ratio, 1e-12)))
    return AcquiredState(_freeze_map(beliefs), state.procedures, state.trust, state.habits, state.provenance_roots, state.independent_successes)
def update_trust(state: AcquiredState, source: str, success: bool) -> AcquiredState:
    trust = _map(state.trust); trust[source] = (_clip_probability(trust.get(source, .5)) * 4 + float(success)) / 5
    return AcquiredState(state.beliefs, state.procedures, _freeze_map(trust), state.habits, state.provenance_roots, state.independent_successes)
def store_procedure(state: AcquiredState, procedure: str, root: str) -> AcquiredState:
    return AcquiredState(state.beliefs, tuple(sorted(set(state.procedures) | {procedure})), state.trust, state.habits, tuple(sorted(set(state.provenance_roots) | {root})), state.independent_successes)


@dataclass(frozen=True)
class IndividualKernelState:
    identity: str; age: int; policy_traits: tuple[tuple[str, float], ...]; acquired: AcquiredState = field(default_factory=AcquiredState.blank)
    @classmethod
    def naive_founder(cls, identity: str, policy_traits: Mapping[str, float]) -> "IndividualKernelState": return cls(identity, 0, _freeze_map(policy_traits), AcquiredState.blank())
    def newborn(self, identity: str) -> "IndividualKernelState": return IndividualKernelState(identity, 0, self.policy_traits, AcquiredState.blank())
def select_observable_teacher(candidates: tuple[IndividualKernelState, ...]) -> IndividualKernelState | None:
    eligible = [c for c in candidates if c.acquired.may_teach]; return min(eligible, key=lambda c: c.identity) if eligible else None


@dataclass(frozen=True)
class PolicyDecision:
    q0_values: tuple[tuple[str, float], ...]; neutral_action: str; advice: str | None; conflict: bool; chosen_action: str; operation_count: int; charged_cost: float; override_applied: bool; override_key: str | None; override_draw: float | None; social_content_used: bool; pre_override_digest: str; pre_override_learning_digest: str; post_override_learning_digest: str; posterior_advice: float = .5; information_action: str | None = None; information_value: float = 0.0
class Policy(Protocol):
    def decide(self, observation: PolicyObservation, operation_cap: int, keyed_rng: KeyedRNG) -> PolicyDecision: ...


def source_calibration(observation: PolicyObservation) -> float:
    history, trust = _map(observation.source_history), _map(observation.trust); successes, failures = history.get("successes", 0.0), history.get("failures", 0.0)
    empirical = (successes + 1) / (successes + failures + 2); prior = trust.get(observation.source_id or "", .5)
    return _clip_probability((2 * empirical + prior) / 3)
def posterior_advice_probability(observation: PolicyObservation, *, use_social: bool = True) -> float:
    beliefs = _map(observation.beliefs)
    if "p_branch_0" in beliefs:
        reference = observation.advice if observation.advice in {"branch_0", "branch_1"} else "branch_1"
        return branch_posteriors(observation, use_social=use_social)[reference]
    prior, accuracy = _clip_probability(beliefs.get("p_advice", .5)), _clip_probability(beliefs.get("private_likelihood", .80))
    log_odds = _logit(prior) + (1 if observation.private_cue in {"supports_advice", "positive"} else -1) * log(accuracy / (1 - accuracy))
    if use_social and observation.advice is not None and observation.messages:
        reliability = _clip_probability(source_calibration(observation) * max(0., 1. - observation.context_mismatch)); log_odds += len(frozenset(observation.provenance_roots)) * log(reliability / (1 - reliability))
    return _logistic(log_odds)

def branch_posteriors(observation: PolicyObservation, *, use_social: bool = True) -> dict[str, float]:
    """Normalized procedural branch beliefs, updated by the common private cue.

    Old kernel fixtures retain the p_advice representation; ecology observations
    carry p_branch_0/1 so no-teacher and asocial paths use identical hardware.
    """
    beliefs = _map(observation.beliefs)
    if "p_branch_0" not in beliefs:
        p = posterior_advice_probability(observation, use_social=use_social)
        if observation.advice in {"branch_0", "branch_1"}:
            return {observation.advice: p, "branch_1" if observation.advice == "branch_0" else "branch_0": 1-p}
        return {"branch_0": 1-p, "branch_1": p}
    values = {"branch_0": max(1e-9, beliefs.get("p_branch_0", .5)), "branch_1": max(1e-9, beliefs.get("p_branch_1", .5))}
    cue = observation.private_cue
    if cue in values:
        accuracy = _clip_probability(beliefs.get("private_likelihood", .8)); values[cue] *= accuracy; values["branch_1" if cue == "branch_0" else "branch_0"] *= 1-accuracy
    if use_social and observation.advice in values and observation.messages:
        # Both conditional likelihoods are required. Multiplying only the advised
        # branch by r would penalize even perfectly neutral (r=.5) testimony.
        reliability = source_calibration(observation)
        values[observation.advice] *= reliability
        alternative = "branch_1" if observation.advice == "branch_0" else "branch_0"
        values[alternative] *= 1-reliability
    total = sum(values.values())
    return {key: value / total for key, value in values.items()}


class OrdinarySocialPolicy:
    """d=(0,0) remains a fully social learner; only d is an extra override."""
    def __init__(self, d_procedure: float = 0.0, d_local: float = 0.0, *, tau: int = 5) -> None:
        if not 0 <= d_procedure <= 1 or not 0 <= d_local <= 1: raise ValueError("override probabilities must lie in [0,1]")
        self.d_procedure, self.d_local, self.tau = float(d_procedure), float(d_local), int(tau)
    def _q0_with_posterior(self, observation: PolicyObservation, posterior: float) -> tuple[tuple[str, float], ...]:
        values, prices = _map(observation.action_values), _map(observation.prices)
        if {"branch_0", "branch_1"}.issubset(values):
            reference = observation.advice if observation.advice in {"branch_0", "branch_1"} else "branch_1"
            posteriors = {reference: posterior, "branch_1" if reference == "branch_0" else "branch_0": 1-posterior}
            plus, minus = prices.get("procedure_expected_plus", 0.), prices.get("procedure_expected_minus", 0.)
            return _freeze_map({branch: posteriors[branch] * plus + (1-posteriors[branch]) * minus for branch in values})
        if observation.advice is not None:
            alternate = next((a for a in observation.feasible_actions if a != observation.advice), None); reward, loss = prices.get("correct_reward", 0.), prices.get("incorrect_loss", 0.)
            if alternate is not None and (reward or loss):
                values[observation.advice] = posterior * reward - (1 - posterior) * loss - prices.get("execute", 0.)
                values[alternate] = (1 - posterior) * reward - posterior * loss - prices.get("execute", 0.)
        return _freeze_map(values)
    def _q0(self, observation: PolicyObservation) -> tuple[tuple[str, float], ...]: return self._q0_with_posterior(observation, posterior_advice_probability(observation))
    def _decision(self, observation: PolicyObservation, operation_cap: int, keyed_rng: KeyedRNG, *, allow_override: bool, social: bool, information_action: str | None = None, information_value: float = 0., computation_operations: int = 0) -> PolicyDecision:
        observation = validate_policy_observation(observation)
        if operation_cap < 1 or observation.computation_budget < 1: raise ValueError("policy needs one charged operation")
        posterior = posterior_advice_probability(observation, use_social=social); q0 = self._q0(observation) if social else self._q0_with_posterior(observation, posterior); neutral = max(q0, key=lambda item: (item[1], item[0]))[0]; conflict = observation.advice is not None and neutral != observation.advice
        learning_digest = sha256(repr((observation.beliefs, observation.procedures, observation.trust, observation.provenance_roots)).encode()).hexdigest(); pre_digest = sha256(repr((q0, neutral, observation.messages, observation.provenance_roots)).encode()).hexdigest()
        probability = self.d_procedure if observation.domain == "procedure" else self.d_local; chosen, draw, applied, key = neutral, None, False, None
        if allow_override and conflict and observation.age < self.tau and probability:
            key = f"override:{observation.identity}:{observation.season}:{observation.domain}"; draw = keyed_rng.draw("override", entity=observation.identity, event_type=observation.domain)
            if draw < probability: chosen, applied = observation.advice, True
        operations = 1 + computation_operations + {"query": 1, "verify": 2}.get(information_action, 0)
        if operations > operation_cap: information_action, information_value, operations = None, 0., 1
        return PolicyDecision(q0, neutral, observation.advice, conflict, chosen, operations, _map(observation.prices).get("operation", 0.) * operations, applied, key, draw, social and bool(observation.messages), pre_digest, learning_digest, learning_digest, posterior, information_action, information_value)
    def decide(self, observation: PolicyObservation, operation_cap: int, keyed_rng: KeyedRNG) -> PolicyDecision: return self._decision(observation, operation_cap, keyed_rng, allow_override=True, social=True)
class VectorOverridePolicy(OrdinarySocialPolicy): pass
class ScalarOverridePolicy(OrdinarySocialPolicy):
    def __init__(self, d: float, *, tau: int = 5) -> None: super().__init__(d, d, tau=tau)
class AsocialPolicy(OrdinarySocialPolicy):
    """Access-off masks content, not the underlying physical action set."""
    def decide(self, observation: PolicyObservation, operation_cap: int, keyed_rng: KeyedRNG) -> PolicyDecision:
        observation = validate_policy_observation(observation); masked = PolicyObservation(**{**observation.__dict__, "messages": (), "provenance_roots": (), "advice": None, "source_id": None, "source_history": ()})
        return self._decision(masked, operation_cap, keyed_rng, allow_override=False, social=False)


@dataclass(frozen=True)
class RewardPredictor:
    """A focal-agent, bounded normalized-LMS reward predictor.

    This is deliberately not a batch learner.  An individual can update it once,
    from its newest realised payoff, after paying the declared primitive-operation
    cost.  The constants are conservative counts for four features: a dot product,
    feature-norm construction, residual/normalisation, and four LMS weight updates.
    """
    weights: tuple[tuple[str, float], ...]; features: tuple[str, ...] = ("bias", "calibrated_source", "context_match", "unique_roots")
    # A feature-wise multiply-accumulate is one declared primitive operation.
    PREDICT_OPERATIONS = 4
    LMS_UPDATE_OPERATIONS = 16
    @classmethod
    def blank(cls) -> "RewardPredictor": return cls(_freeze_map({name: 0. for name in cls(()).features}))
    @classmethod
    def fit(cls, rows: Iterable[tuple[Mapping[str, float], float]], **_ignored: object) -> "RewardPredictor":
        """Compatibility fixture constructor; ecology never invokes batch fitting.

        Keeping this narrow helper preserves old kernel fixtures while making a
        multi-row call fail loudly instead of silently reintroducing free training.
        Production callers must use :meth:`lms_update` and charge its return value.
        """
        materialized = list(rows)
        if len(materialized) > 1:
            raise ValueError("batch predictor fitting is forbidden; use one paid lms_update")
        if not materialized:
            return cls.blank()
        predictor, _ = cls.blank().lms_update(*materialized[0], cls.LMS_UPDATE_OPERATIONS)
        return predictor
    def lms_update(self, feature: Mapping[str, float], realised_payoff: float, operation_cap: int, *, rate: float = .08) -> tuple["RewardPredictor", int]:
        """Return one paid normalized-LMS update, or no update if it cannot fit.

        ``feature`` is the focal decision's already observable vector and
        ``realised_payoff`` is its physical outcome.  No history, population
        aggregate, truth field, or training pass is consulted here.
        """
        if operation_cap < self.LMS_UPDATE_OPERATIONS:
            return self, 0
        weights = _map(self.weights)
        values = {name: float(feature.get(name, 0.)) for name in self.features}
        estimate = sum(weights.get(name, 0.) * values[name] for name in self.features)
        norm = 1.0 + sum(value * value for value in values.values())
        step = rate * (float(realised_payoff) - estimate) / norm
        return RewardPredictor(_freeze_map({name: weights.get(name, 0.) + step * values[name] for name in self.features}), self.features), self.LMS_UPDATE_OPERATIONS
    def predict(self, feature: Mapping[str, float]) -> float: return sum(_map(self.weights).get(n, 0.) * float(feature.get(n, 0.)) for n in self.features)
def observable_reward_features(observation: PolicyObservation) -> dict[str, float]: return {"bias": 1., "calibrated_source": source_calibration(observation), "context_match": max(0., 1. - observation.context_mismatch), "unique_roots": min(4., float(len(frozenset(observation.provenance_roots))))}
class FeatureTrustPolicy(OrdinarySocialPolicy):
    def __init__(self, predictor: RewardPredictor | None = None) -> None: super().__init__(); self.predictor = predictor or RewardPredictor.blank()
    def _q0(self, observation: PolicyObservation) -> tuple[tuple[str, float], ...]:
        values = _map(self._q0_with_posterior(observation, posterior_advice_probability(observation)))
        if observation.advice is not None: values[observation.advice] += self.predictor.predict(observable_reward_features(observation))
        return _freeze_map(values)
    def decide(self, observation: PolicyObservation, operation_cap: int, keyed_rng: KeyedRNG) -> PolicyDecision:
        return self._decision(observation, operation_cap, keyed_rng, allow_override=False, social=True, computation_operations=RewardPredictor.PREDICT_OPERATIONS)
class CandidateBPolicy(FeatureTrustPolicy):
    """Finite-operation metareasoner buying query/verification only if EVI pays costs."""
    def decide(self, observation: PolicyObservation, operation_cap: int, keyed_rng: KeyedRNG) -> PolicyDecision:
        observation = validate_policy_observation(observation); base = self._q0(observation); base_value = max(v for _, v in base); prices, posterior = _map(observation.prices), posterior_advice_probability(observation)
        # A purchased binary signal is evaluated under its actual observation
        # probabilities.  The posted time opportunity cost is the foregone safe
        # action; it is deliberately shared by every policy in the ecology.
        def information_value(accuracy: float, price: float) -> float:
            p_positive = posterior * accuracy + (1. - posterior) * (1. - accuracy)
            high = _logistic(_logit(posterior) + log(accuracy / (1. - accuracy)))
            low = _logistic(_logit(posterior) - log(accuracy / (1. - accuracy)))
            now = p_positive * max(v for _, v in self._q0_with_posterior(observation, high)) + (1. - p_positive) * max(v for _, v in self._q0_with_posterior(observation, low))
            # This is E[max Q | signal] on the same remaining decision state.
            # Continuation is already represented in Q0; adding it only after a
            # signal would manufacture an information bonus.
            return now - price - prices.get("time_opportunity", 0.)
        verify_value = information_value(.90, prices.get("verify", 0.))
        query_value = information_value(source_calibration(observation), prices.get("query", 0.))
        choice, value = max(((None, base_value), ("verify", verify_value), ("query", query_value)), key=lambda item: item[1])
        return self._decision(observation, operation_cap, keyed_rng, allow_override=False, social=True, information_action=choice, information_value=value-base_value, computation_operations=RewardPredictor.PREDICT_OPERATIONS)


# Slice 2A ecology.  These objects deliberately keep the world-side procedure
# quality private: policy calls see only PolicyObservation and observable success
# histories.  ``K`` can contain a wrong but viable sequence, which is why no
# teacher-selection path below has access to a sequence's hidden quality.
@dataclass
class Individual:
    identity: str
    age: int
    energy: float
    policy: Policy
    traits: tuple[tuple[str, float], ...] = ()
    B: dict[str, float] = field(default_factory=dict)
    K: dict[str, tuple[str, ...]] = field(default_factory=dict)
    T: dict[str, float] = field(default_factory=dict)
    H: dict[str, float] = field(default_factory=dict)
    independent_successes: dict[str, int] = field(default_factory=dict)
    observed_successes: int = 0
    observed_failures: int = 0
    parent_id: str | None = None
    # Only this individual's newest realised reward trains a feature-trust
    # controller.  Retaining a bounded audit window does not feed training.
    reward_history: deque[tuple[dict[str, float], float]] = field(default_factory=lambda: deque(maxlen=64))

    @classmethod
    def contract_fixture(cls, B: Mapping[str, float] | None = None, K: Mapping[str, Iterable[str]] | None = None,
                         T: Mapping[str, float] | None = None, H: Mapping[str, float] | None = None) -> "Individual":
        return cls("fixture-parent", 3, 32.0, OrdinarySocialPolicy(), (), dict(B or {}),
                   {key: tuple(value) for key, value in (K or {}).items()}, dict(T or {}), dict(H or {}))

    def acquired_digest(self) -> str:
        return sha256(repr((sorted(self.B.items()), sorted(self.K.items()), sorted(self.T.items()), sorted(self.H.items()),
                            sorted(self.independent_successes.items()))).encode()).hexdigest()

    def eligible_sequences(self) -> tuple[str, ...]:
        return tuple(sorted(sequence for sequence in self.K if self.independent_successes.get(sequence, 0) >= 2))


@dataclass(frozen=True)
class PaidNewborn:
    identity: str
    energy: float
    initial_acquired_digest: str
    birth_event_id: str
    policy_traits: tuple[tuple[str, float], ...]


@dataclass(frozen=True)
class SeasonReport:
    season: int; population_prior: int; population_next: int; births: int; deaths: int
    energy_resource_residual: float; teacher_time_debit: int; learner_time_debit: int
    resource: float; events: int; status: str; replay_digest: str
    founders: int = 0; adults: int = 0; newborns: int = 0; stored_knowledge: int = 0; adult_evidence_accuracy: float | None = None


class EcologyRun:
    """A finite-resource, age-structured IBM used only for ecological validity gates.

    The simulator has two actual procedure families.  A sequence is an acquired
    executable object rather than a scalar accuracy: each has D prerequisite steps,
    useful-prefix salvage, a slow hidden structural branch, and a fresh local finish
    context.  Private attempts, teaching/query time, computation, production,
    maintenance, death, and paid births are all posted before the seasonal identity
    is checked.
    """
    RESOURCE_CAPACITY = 1600.0
    REGENERATION = .08
    CONVERSION = .75
    MAINTENANCE = .6
    BIRTH_COST = 16.0
    NEWBORN_ENERGY = 8.0
    RESERVE = 3.0
    BIRTH_MAX = .5
    TIME_TOKENS = 12
    OPERATION_CAP = 128
    POPULATION_CAP = 512
    EVENT_CAP = 1_500_000
    WALL_SECONDS = 120.0
    P_PLUS = .90
    P_MINUS = .50
    SAFE_YIELD = 1.2
    STEP_COST = .20
    SALVAGE = .20
    TAU = 5
    LEDGER_WINDOW = 4096

    def __init__(self, seed: int, policy_factory: type[Policy] | Any = OrdinarySocialPolicy,
                 *, depth: int = 3, chi: float = .75, q_theta: float = .005,
                 verification_price: float = .10, graph_variant: int = 0,
                 initial_traits: Mapping[str, float] | None = None,
                 burn_in: int = 60, measurement: int = 180, label: str = "ordinary") -> None:
        if depth not in {1, 3, 6}: raise ValueError("depth must be one of V7's predeclared procedure depths")
        if not 0.0 <= chi <= 1.0 or not 0.0 <= q_theta <= 1.0: raise ValueError("ecological probabilities are invalid")
        if verification_price <= 0 or graph_variant not in {0, 1}:
            raise ValueError("verification price must be positive and graph variant must be declared")
        self.seed, self.depth, self.chi, self.q_theta, self.verification_price, self.graph_variant, self.burn_in, self.measurement, self.label = seed, depth, chi, q_theta, float(verification_price), graph_variant, burn_in, measurement, label
        self.resource, self.season, self.events, self.status = self.RESOURCE_CAPACITY, 0, 0, "running"
        self.start_time = time.monotonic(); self.theta = {"food": 0, "tool": 1}
        self.population: dict[str, Individual] = {}
        # The canonical stream is bounded.  A capped recent window supports audit
        # diagnostics without silently retaining an unbounded event list.
        self.ledger: deque[LedgerEvent] = deque(maxlen=self.LEDGER_WINDOW)
        self.biological_edges: list[tuple[str, str]] = []
        self.cultural_edges: list[tuple[str, str]] = []
        self.stream = sha256(); self.decision_samples: deque[dict[str, Any]] = deque(maxlen=10_000)
        self.reports: list[SeasonReport] = []
        self._season_events: list[LedgerEvent] = []
        self.losses: dict[str, float] = {name: 0.0 for name in ("conversion", "maintenance", "birth", "teaching", "operations")}
        self._time_used: dict[str, int] = {}
        self.max_time_used = 0
        self.override_opportunities = self.override_applied = self.revisions = self.cultural_decisions = self.culturally_correct = 0
        self._policy_factory = policy_factory
        for index in range(64):
            identity = f"founder-{index:03d}"
            traits = _freeze_map(initial_traits or {"d_procedure": 0., "d_local": 0.})
            self.population[identity] = Individual(identity, 0, self.NEWBORN_ENERGY, self._make_policy(traits), traits)
        self.initial_total_stock = self.resource + sum(person.energy for person in self.population.values())

    @classmethod
    def contract_fixture(cls) -> "EcologyRun":
        # This is a normal, seeded burn-in—not an expert fixture.  The short
        # measurement is sufficient for ledger assertions while all founders begin blank.
        run = cls(71001, depth=3, chi=.75, q_theta=.005, burn_in=0, measurement=1, label="contract")
        for _ in range(4):
            run.advance_season()
        return run

    def _make_policy(self, traits: tuple[tuple[str, float], ...] = ()) -> Policy:
        trait = _map(traits)
        if self._policy_factory is CandidateBPolicy:
            return CandidateBPolicy()
        if self._policy_factory is FeatureTrustPolicy:
            return FeatureTrustPolicy()
        if self._policy_factory in (OrdinarySocialPolicy, VectorOverridePolicy):
            return self._policy_factory(trait.get("d_procedure", 0.), trait.get("d_local", 0.), tau=self.TAU)
        return self._policy_factory() if callable(self._policy_factory) else self._policy_factory

    def _update_own_predictor(self, person: Individual, features: Mapping[str, float], payoff: float, operations_already_used: int) -> int:
        """Perform at most one focal normalized-LMS update and charge it in-ledger."""
        if not isinstance(person.policy, FeatureTrustPolicy):
            return 0
        predictor, operations = person.policy.predictor.lms_update(features, payoff, self.OPERATION_CAP - operations_already_used)
        if not operations:
            return 0
        person.policy.predictor = predictor
        self._charge(person, .01 * operations, "operations")
        self._event("predictor_lms_update", learner_id=person.identity, operation_charge=.01 * operations,
                    physical_outcome=f"focal_normalized_lms:{operations}_operations")
        return operations

    def _rng(self, namespace: str, identity: str, ordinal: int = 0, event_type: str = "ecology") -> float:
        return KeyedRNG(str(self.seed), f"D{self.depth}", self.season).draw(namespace, entity=identity, ordinal=ordinal, event_type=event_type)

    def _event(self, kind: str, **values: Any) -> LedgerEvent:
        event = LedgerEvent(f"{self.seed}:{self.season}:{self.events:08d}", kind, **values)
        self.events += 1; self.ledger.append(event); self._season_events.append(event)
        self.stream.update(repr(event).encode())
        return event

    def _sequence(self, family: str, branch: int) -> str: return f"{family}|branch={branch}|depth={self.depth}"

    def _target_branch(self, family: str) -> int:
        """Actual alternative graph: variant one reverses the food terminal map.

        This is a transition-level unseen graph permutation, not a relabel in the
        output table: it changes which branch reaches the D-step reward kernel.
        """
        return self.theta[family] ^ int(self.graph_variant == 1 and family == "food")

    def _teacher(self, learner: Individual, family: str) -> Individual | None:
        # One teaching event per season reserves the maximum D=6 procedure episode
        # plus a possible learner-side teaching/query choice for the tutor's own
        # action. This is a real time constraint, not a teacher availability bonus.
        choices = [person for person in self.population.values() if person.identity != learner.identity and self._time_used.get(person.identity, 0) == 0 and any(key.startswith(family + "|") for key in person.eligible_sequences())]
        if not choices: return None
        # Eligibility uses acquired stored sequences and observable attempted successes only.
        return min(choices, key=lambda person: (-(person.T.get(f"outcome:{family}", .5)), person.identity))

    def _theta_cue(self, person: Individual, family: str, branch: int) -> int:
        """A common .80 sensor reports the slow structural branch, never advice."""
        correct = self._rng("observation", person.identity, event_type=f"theta-cue:{family}") < .80
        return branch if correct else 1 - branch

    def _local_state(self, person: Individual, family: str, teacher: Individual | None) -> tuple[int, int, int]:
        """Fresh z plus equal-hardware private and tutor signals.

        chi changes whether the tutor has the learner's current context (rather
        than sensor precision).  At chi=.5 the stale/opposite-context construction
        makes tutor-local correctness .5, while at chi=1 it is exactly .8.
        """
        z = int(self._rng("environment", person.identity, event_type=f"z:{family}") >= .5)
        private = z if self._rng("observation", person.identity, event_type=f"local-private:{family}") < .80 else 1-z
        shared = teacher is not None and self._rng("observation", f"{person.identity}:{teacher.identity}", event_type=f"local-link:{family}") < self.chi
        tutor_context = z if shared else 1-z
        tutor = tutor_context if teacher is not None and self._rng("observation", teacher.identity, event_type=f"local-tutor:{person.identity}:{family}") < .80 else 1-tutor_context
        return z, private, tutor

    def _observation(self, person: Individual, family: str, teacher: Individual | None) -> PolicyObservation:
        offered = next((key for key in teacher.eligible_sequences() if key.startswith(family + "|")), None) if teacher else None
        offered_branch = int(offered.split("branch=")[1].split("|")[0]) if offered else 0
        sensed = self._theta_cue(person, family, self._target_branch(family))
        private_cue = f"branch_{sensed}"
        advice = f"branch_{offered_branch}" if teacher else None
        history = (("successes", float(teacher.T.get(f"success:{family}", 0.))), ("failures", float(teacher.T.get(f"failure:{family}", 0.)))) if teacher else ()
        roots = tuple(value for value in (teacher.K.get(offered, ())[-1:] if teacher and offered else ()) if value.startswith("root:"))
        raw0, raw1 = person.B.get(f"{family}:branch=0", .5), person.B.get(f"{family}:branch=1", .5)
        scale = raw0 + raw1
        beliefs = {"p_branch_0": raw0 / scale, "p_branch_1": raw1 / scale, "private_likelihood": .80}
        exact = __import__("v7.experiments.exact", fromlist=["enumerate_task"])
        plus, minus = exact.enumerate_task(self.depth, self.P_PLUS).procedure_return, exact.enumerate_task(self.depth, self.P_MINUS).procedure_return
        prices = (("operation", .01), ("query", .05), ("verify", self.verification_price), ("execute", self.depth * self.STEP_COST),
                  ("correct_reward", __import__("v7.experiments.exact", fromlist=["correct_finish_reward"]).correct_finish_reward(self.depth)),
                  ("incorrect_loss", 2.0), ("time_opportunity", (self.depth + 1) * self.SAFE_YIELD),
                  ("procedure_expected_plus", plus), ("procedure_expected_minus", minus))
        return PolicyObservation(person.identity, self.season, person.age, person.energy, self.TIME_TOKENS,
                                 self.OPERATION_CAP, "procedure", private_cue,
                                 _freeze_map(beliefs),
                                 tuple(sorted(person.K)), tuple(sorted(person.T.items())), tuple(sorted(person.H.items())),
                                 (("procedure_offer", offered or ""),) if teacher else (), roots, ("branch_0", "branch_1"),
                                 (("branch_0", 0.0), ("branch_1", 0.0)), prices, advice, f"teacher:{teacher.identity}:{family}" if teacher else None,
                                 history, 0.0)

    def _local_observation(self, person: Individual, family: str, teacher: Individual | None) -> tuple[PolicyObservation, tuple[int, int, int]]:
        z, private, tutor = self._local_state(person, family, teacher)
        advice = "teacher" if teacher else None
        cue = "supports_advice" if teacher is not None and private == tutor else "supports_private"
        history = (("successes", teacher.T.get(f"local-success:{family}", 0.)), ("failures", teacher.T.get(f"local-failure:{family}", 0.))) if teacher else ()
        observation = PolicyObservation(person.identity, self.season, person.age, person.energy, self.TIME_TOKENS,
            self.OPERATION_CAP, "local", cue, (("p_advice", person.B.get(f"local:{family}", .5)), ("private_likelihood", .8)),
            tuple(sorted(person.K)), tuple(sorted(person.T.items())), tuple(sorted(person.H.items())),
            (("local_recommendation", family),) if teacher else (), (),
            ("private", "teacher"), (("private", 0.), ("teacher", 0.)),
            (("operation", .01), ("query", .05), ("verify", .10), ("execute", 0.), ("correct_reward", 3.), ("incorrect_loss", 2.), ("time_opportunity", self.SAFE_YIELD)),
            advice, f"teacher:{teacher.identity}:{family}" if teacher else None, history, 0.)
        return observation, (z, private, tutor)

    def _local_attempt(self, person: Individual, family: str, choice: str, context: tuple[int, int, int], teacher: Individual | None) -> float:
        z, private, tutor = context; selected = tutor if choice == "teacher" else private
        self._spend_time(person, 1); before = person.energy
        success = selected == z; self._draw_from_resource(person, 3. if success else 0., 0., time_debit=1, failure=not success)
        if not success: self._charge(person, 2., "operations")
        key, prior = f"local:{family}", person.B.get(f"local:{family}", .5)
        # Only a disagreement identifies relative local advice: success of a
        # private alternative is evidence against the tutor, not for it.
        if teacher is not None and private != tutor:
            supports_advice = (choice == "teacher" and success) or (choice == "private" and not success)
            lr = .8 / .2
            person.B[key] = _logistic(_logit(prior) + (log(lr) if supports_advice else -log(lr)))
        if teacher is not None and choice == "teacher":
            teacher.T[f"local-{'success' if success else 'failure'}:{family}"] = teacher.T.get(f"local-{'success' if success else 'failure'}:{family}", 0.) + 1
        return person.energy - before

    def _local_message(self, teacher: Individual, learner: Individual, family: str) -> None:
        """A current-situation recommendation is a paid, observable message.

        It communicates no stored procedure and does not alter B/K/T merely by
        receipt.  Its only causal route is evidence in Q0 or a logged local
        conflict override.
        """
        self._spend_time(teacher, 1); self._spend_time(learner, 1)
        paid = self._charge(teacher, .02, "teaching")
        self._event("local_advice", learner_id=learner.identity, teacher_id=teacher.identity,
                    learner_time_debit=1, teacher_time_debit=1,
                    cultural_edge=(teacher.identity, learner.identity), physical_outcome="local_message")
        self.cultural_edges.append((teacher.identity, learner.identity))

    def _draw_from_resource(self, person: Individual, gross_energy: float, material: float, *, time_debit: int, failure: bool = False) -> None:
        draw = max(0.0, gross_energy) / self.CONVERSION + material
        actual = min(self.resource, draw)
        factor = actual / draw if draw else 1.0
        earned = gross_energy * factor
        self.resource -= actual; person.energy += earned
        # Resource used but not retained as individual energy is a declared physical
        # sink: conversion loss plus consumed prerequisite material.
        self.losses["conversion"] += actual - earned
        self._event("production", learner_id=person.identity, learner_time_debit=time_debit, learner_energy_delta=earned, material_delta=-actual,
                    physical_outcome="failure" if failure else "production")

    def _spend_time(self, person: Individual, tokens: int) -> None:
        used = self._time_used.get(person.identity, 0) + tokens
        if used > self.TIME_TOKENS: raise RuntimeError("ecology event exceeded the fixed 12-token individual time budget")
        self._time_used[person.identity] = used; self.max_time_used = max(self.max_time_used, used)

    def _charge(self, person: Individual, amount: float, loss_kind: str) -> float:
        """Debit only available energy; starvation is a demographic outcome, never debt."""
        paid = min(max(0.0, person.energy), amount)
        person.energy -= paid; self.losses[loss_kind] += paid
        if paid:
            self._event(f"charge:{loss_kind}", learner_id=person.identity, learner_energy_delta=-paid, physical_outcome="paid_charge")
        return paid

    def _teach(self, teacher: Individual, learner: Individual, family: str) -> str | None:
        offered = next((key for key in teacher.eligible_sequences() if key.startswith(family + "|")), None)
        if offered is None: return None
        self._spend_time(teacher, 1); self._spend_time(learner, 1); paid = self._charge(teacher, .05, "teaching")
        self._event("teaching", learner_id=learner.identity, teacher_id=teacher.identity, learner_time_debit=1,
                    teacher_time_debit=1, cultural_edge=(teacher.identity, learner.identity),
                    physical_outcome="message")
        # Receipt is content exposure only.  K is stored only after the learner's
        # later physical success; compliance cannot overwrite memory or belief.
        self.cultural_edges.append((teacher.identity, learner.identity))
        learner.T[f"teacher:{teacher.identity}:{family}"] = (teacher.T.get(f"success:{family}", 0.) + 1.) / (teacher.T.get(f"success:{family}", 0.) + teacher.T.get(f"failure:{family}", 0.) + 2.)
        return offered

    def _attempt(self, person: Individual, family: str, sequence: str | None, from_teacher: Individual | None, selected_branch: int | None = None) -> float:
        branch = self._target_branch(family)
        # Private discovery follows the agent's own observed structural cue, not a
        # random coin once advice is absent.  Existing K competes with that evidence.
        chosen_branch = int(sequence.split("branch=")[1].split("|")[0]) if sequence else (selected_branch if selected_branch is not None else self._theta_cue(person, family, self.theta[family]))
        correct_branch = chosen_branch == branch
        chance = self.P_PLUS if correct_branch else self.P_MINUS
        exact = __import__("v7.experiments.exact", fromlist=["sample_task_outcome"])
        terminal, reached, net = exact.sample_task_outcome(self.depth, chance, lambda step: self._rng("task_outcome", person.identity, step, f"{family}:{chosen_branch}"))
        material = (reached + 1) * self.STEP_COST if terminal.startswith("prefix_failure") else self.depth * self.STEP_COST
        # A procedure episode reserves the same D+1 opportunity tokens as the
        # analytic safe-work comparator; failed branches have explicit terminal
        # salvage but do not create free extra production opportunities.
        self._spend_time(person, self.depth + 1)
        before = person.energy
        if terminal == "correct_finish":
            self._draw_from_resource(person, net, material, time_debit=self.depth + 1)
            learned = self._sequence(family, chosen_branch)
            root = f"root:{person.identity}:{self.season}:{self.events}"
            person.K.setdefault(learned, tuple((*learned.split("|"), root)))
            person.independent_successes[learned] = person.independent_successes.get(learned, 0) + 1
            person.observed_successes += 1
        else:
            self._draw_from_resource(person, 0., material, time_debit=self.depth + 1, failure=True)
            self._charge(person, -net, "operations"); person.observed_failures += 1
        success = terminal == "correct_finish"
        # Physical outcomes update the branch posterior at every age.  This is not
        # a global family score and is immediately available to the next policy call.
        key, other = f"{family}:branch={chosen_branch}", f"{family}:branch={1-chosen_branch}"
        raw, opposing = person.B.get(key, .5), person.B.get(other, .5)
        prior = raw / (raw + opposing)
        # Use the observed terminal likelihood, including D prerequisite hazards,
        # rather than treating a complete procedure as one Bernoulli trial.
        positive = {name: p for name, p, _ in exact.enumerate_task(self.depth, self.P_PLUS).failure_branches}[terminal]
        negative = {name: p for name, p, _ in exact.enumerate_task(self.depth, self.P_MINUS).failure_branches}[terminal]
        updated = _logistic(_logit(prior) + log(positive / negative))
        person.B[key], person.B[other] = updated, 1-updated
        person.T[f"{'success' if success else 'failure'}:{family}"] = person.T.get(f"{'success' if success else 'failure'}:{family}", 0.) + 1.
        if from_teacher:
            # Outcomes calibrate this learner's estimate of this teacher in-domain;
            # they are not credited as the teacher's independent competence.
            tkey = f"teacher:{from_teacher.identity}:{family}"
            old = person.T.get(tkey, .5); person.T[tkey] = (4 * old + float(success)) / 5
        return person.energy - before

    def _safe_work(self, person: Individual, tokens: int | None = None) -> None:
        tokens = self.depth + 1 if tokens is None else tokens
        self._spend_time(person, tokens)
        self._draw_from_resource(person, self.SAFE_YIELD * tokens, 0.0, time_debit=tokens)

    def paid_birth(self, parent: Individual, *, newborn_id: str | None = None) -> tuple[Individual, LedgerEvent]:
        if parent.energy < self.BIRTH_COST: raise ValueError("birth requires a real parent-paid energy cost")
        child_id = newborn_id or f"birth-{self.seed}-{self.season}-{self.events}"
        parent.energy -= self.BIRTH_COST
        # Birth copies heritable policy traits exactly; mutation is an explicit
        # future experimental operator, never a hidden factory reset or a change
        # to the d=(0,0) ecological sentinel.
        traits = _freeze_map(parent.traits)
        child = Individual(child_id, 0, self.NEWBORN_ENERGY, self._make_policy(traits), traits, parent_id=parent.identity)
        event = self._event("birth", learner_id=child_id, teacher_id=parent.identity, teacher_energy_delta=-self.BIRTH_COST,
                            learner_energy_delta=self.NEWBORN_ENERGY, parent_energy_debit=self.BIRTH_COST,
                            birth_cost=self.BIRTH_COST, newborn_energy_credit=self.NEWBORN_ENERGY,
                            biological_edge=(parent.identity, child_id), physical_outcome="birth")
        self.losses["birth"] += self.BIRTH_COST - self.NEWBORN_ENERGY
        self.population[child_id] = child; self.biological_edges.append((parent.identity, child_id))
        return child, event

    def paired_paid_newborns(self) -> tuple[PaidNewborn, PaidNewborn]:
        parents = sorted((person for person in self.population.values() if person.energy >= self.BIRTH_COST),
                         key=lambda person: (-person.energy, person.identity))
        if len(parents) < 2:
            raise ValueError("neutral paid-newborn gate has no two resident parents able to pay the declared birth cost")
        # Each arm pays a distinct, real resident birth.  The common pairing ID joins
        # counterfactual arms; it never turns two births into a free immigrant.
        first, first_event = self.paid_birth(parents[0], newborn_id=f"paired-mutant-{self.season}")
        second, _ = self.paid_birth(parents[1], newborn_id=f"paired-neutral-{self.season}")
        pair = f"paid-pair:{first_event.event_id}"
        return (PaidNewborn(first.identity, first.energy, first.acquired_digest(), pair, first.traits),
                PaidNewborn(second.identity, second.energy, second.acquired_digest(), pair, second.traits))

    def advance_season(self) -> SeasonReport:
        if self.status != "running": return self.reports[-1]
        prior_n, prior_total, prior_resource = len(self.population), sum(person.energy for person in self.population.values()), self.resource
        losses_before = sum(self.losses.values())
        self._season_events = []
        regeneration = self.REGENERATION * max(0.0, self.RESOURCE_CAPACITY - self.resource); self.resource += regeneration
        if regeneration: self._event("regeneration", material_delta=regeneration, physical_outcome="resource_regeneration")
        births = deaths = teacher_time = learner_time = 0
        self._time_used = {}
        for person in list(sorted(self.population.values(), key=lambda item: item.identity)):
            if person.identity not in self.population: continue
            self._charge(person, self.MAINTENANCE + .01 * max(0, person.age - 12), "maintenance")
            family = ("food", "tool")[(self.season + sum(map(ord, person.identity))) % 2]
            # Access-off is an intervention on cultural access, not on private
            # hardware or the task world.  It therefore cannot select a tutor or
            # create a cultural edge even when other residents are eligible.
            local_domain = (self.season + sum(map(ord, person.identity))) % 3 == 0
            if isinstance(person.policy, AsocialPolicy):
                teacher = None
            elif local_domain:
                teacher = next((candidate for candidate in sorted(self.population.values(), key=lambda p: p.identity) if candidate.identity != person.identity and self._time_used.get(candidate.identity, 0) == 0), None)
            else:
                teacher = self._teacher(person, family)
            local_context: tuple[int, int, int] | None = None
            if local_domain:
                if teacher is not None:
                    self._local_message(teacher, person, family)
                    teacher_time += 1; learner_time += 1
                observation, local_context = self._local_observation(person, family, teacher)
            else:
                # Exposure is a paid message before arbitration.  Whether the
                # learner follows its offered branch is a later action, so d cannot
                # secretly determine receipt or memory acceptance.
                offered = self._teach(teacher, person, family) if teacher is not None else None
                teacher_time += int(offered is not None); learner_time += int(offered is not None)
                observation = self._observation(person, family, teacher)
            decision = person.policy.decide(observation, self.OPERATION_CAP, KeyedRNG(str(self.seed), f"D{self.depth}", self.season))
            self._charge(person, decision.charged_cost, "operations")
            operation_total = decision.operation_count
            if decision.information_action:
                self._spend_time(person, 1)
                information_price = dict(observation.prices).get(decision.information_action, 0.0)
                paid = self._charge(person, information_price, "operations")
                # Query/verification emits a conditional noisy signal about the
                # currently offered branch/local recommendation, updates B, then
                # re-decides.  It never adds an unpaid override or forced action.
                target = (self._target_branch(family) if not local_domain else local_context[0])
                accuracy = .90 if decision.information_action == "verify" else .80
                signal = target if self._rng("observation", person.identity, 9, decision.information_action) < accuracy else 1-target
                if local_domain:
                    bkey, prior = f"local:{family}", person.B.get(f"local:{family}", .5)
                    direction = 1. if signal == local_context[2] else -1.
                    person.B[bkey] = _logistic(_logit(prior) + direction * log(accuracy / (1-accuracy)))
                else:
                    p0, p1 = person.B.get(f"{family}:branch=0", .5), person.B.get(f"{family}:branch=1", .5)
                    total = p0 + p1; weights = {0: p0 / total, 1: p1 / total}
                    weights[signal] *= accuracy; weights[1-signal] *= 1-accuracy
                    normalizer = weights[0] + weights[1]
                    person.B[f"{family}:branch=0"], person.B[f"{family}:branch=1"] = weights[0]/normalizer, weights[1]/normalizer
                self._event(decision.information_action, learner_id=person.identity, learner_time_debit=1,
                            operation_charge=decision.charged_cost,
                            physical_outcome="observed_signal")
                refreshed = self._local_observation(person, family, teacher)[0] if local_domain else self._observation(person, family, teacher)
                # Candidate B has already paid once; final arbitration is its shared
                # ordinary Q0 with no second information purchase.
                decision = person.policy._decision(refreshed, self.OPERATION_CAP - operation_total, KeyedRNG(str(self.seed), f"D{self.depth}", self.season), allow_override=False, social=True, computation_operations=RewardPredictor.PREDICT_OPERATIONS if isinstance(person.policy, FeatureTrustPolicy) else 0) if isinstance(person.policy, OrdinarySocialPolicy) else decision
                self._charge(person, decision.charged_cost, "operations")
                operation_total += decision.operation_count
            beliefs_before = tuple(sorted(person.B.items()))
            before_action = person.energy
            if local_domain and local_context is not None:
                payoff = self._local_attempt(person, family, decision.chosen_action, local_context, teacher)
            elif teacher is not None and decision.chosen_action == observation.advice:
                sequence = next((key for key in teacher.eligible_sequences() if key.startswith(family + "|")), None)
                payoff = self._attempt(person, family, sequence, teacher, int(decision.chosen_action[-1]))
            else:
                selected = int(decision.chosen_action[-1]) if decision.chosen_action.startswith("branch_") else self._theta_cue(person, family, self._target_branch(family))
                sequence = next((key for key in person.K if key.startswith(family + f"|branch={selected}|")), None)
                if sequence or self._rng("innovation", person.identity, 2, family) < .45: payoff = self._attempt(person, family, sequence, None, selected)
                else:
                    self._safe_work(person); payoff = person.energy - before_action
            features = observable_reward_features(observation)
            person.reward_history.append((features, payoff))
            predictor_operations = self._update_own_predictor(person, features, payoff, operation_total)
            operation_total += predictor_operations
            if operation_total > self.OPERATION_CAP:
                raise RuntimeError("predictor training and decision operations exceeded the common computation cap")
            self.override_opportunities += int(decision.conflict)
            self.override_applied += int(decision.override_applied)
            self.revisions += int(tuple(sorted(person.B.items())) != beliefs_before)
            if not local_domain and teacher is not None and decision.chosen_action == observation.advice:
                self.cultural_decisions += 1
                self.culturally_correct += int(int(decision.chosen_action[-1]) == self._target_branch(family))
            self.decision_samples.append({"season": self.season, "identity": person.identity, "features": features,
                                          "reward": payoff, "chosen_action": decision.chosen_action,
                                          "decision_operations": decision.operation_count,
                                          "predictor_update_operations": predictor_operations,
                                          "operations": operation_total})
            person.age += 1
            mortality = .01 + .002 * max(0, person.age - 20) + (.20 if person.energy <= 0 else 0.0)
            if self._rng("demography", person.identity, event_type="death") < mortality:
                # Residual individual energy is not silently erased with a corpse.
                # It is an explicit terminal sink in this simple no-carcass ecology.
                terminal_energy = max(0.0, person.energy)
                self.losses["maintenance"] += terminal_energy
                person.energy = 0.0
                del self.population[person.identity]; deaths += 1; self._event("death", learner_id=person.identity, learner_energy_delta=-terminal_energy, physical_outcome="death")
                continue
            fertility = self.BIRTH_MAX * max(0.0, min(1.0, (person.energy - self.BIRTH_COST - self.RESERVE) / 24.0)) if person.age >= self.TAU else 0.0
            if self._rng("demography", person.identity, 1, "birth") < fertility:
                self._spend_time(person, 1)
                self.paid_birth(person); births += 1
            if self.events >= self.EVENT_CAP or len(self.population) > self.POPULATION_CAP or time.monotonic() - self.start_time > self.WALL_SECONDS:
                self.status = "cap_censored"; break
        if self.status == "running" and not self.population: self.status = "extinct"
        if self.status == "running":
            for family in self.theta:
                if self._rng("environment", family, event_type="theta") < self.q_theta:
                    self.theta[family] = 1 - self.theta[family]
        actual = self.resource + sum(person.energy for person in self.population.values())
        # This identity is asserted on actual stocks after all births, deaths and
        # transfers.  The loss delta includes conversion/material use, maintenance,
        # paid teacher effort, operations, and C_birth-E0 for every newborn.
        season_losses = sum(self.losses.values()) - losses_before
        # Independent replay of the event stream: no mutable loss counter is used
        # in the check.  Resource movements are material_delta; agent movements are
        # learner/teacher deltas.  Conversion and mortality loss are visible as the
        # gap between the two, rather than silently cancelling in an accumulator.
        replay_delta = sum(event.material_delta + event.learner_energy_delta + event.teacher_energy_delta for event in self._season_events)
        residual = (prior_resource + prior_total + replay_delta) - actual
        self.stream.update(repr((self.season, prior_n, len(self.population), births, deaths, residual)).encode())
        adults = [person for person in self.population.values() if person.age >= self.TAU]
        adult_accuracy = (sum(person.B.get(f"{family}:branch={self._target_branch(family)}", .5) for person in adults for family in self.theta) / (2 * len(adults))) if adults else None
        report = SeasonReport(self.season, prior_n, len(self.population), births, deaths, residual, teacher_time, learner_time,
                              self.resource, self.events, self.status, self.stream.hexdigest(),
                              sum(person.parent_id is None for person in self.population.values()), len(adults),
                              sum(person.age == 0 for person in self.population.values()), sum(len(person.K) for person in self.population.values()), adult_accuracy)
        self.reports.append(report); self.season += 1
        return report

    def run(self) -> dict[str, Any]:
        horizon = self.burn_in + self.measurement
        while self.season < horizon and self.status == "running": self.advance_season()
        return {"seed": self.seed, "policy": self.label, "depth": self.depth, "burn_in": self.burn_in,
                "measurement": self.measurement, "seasons_completed": self.season, "status": self.status,
                "population": len(self.population), "events": self.events, "resource": self.resource,
                "ledger_residual_max": max((abs(report.energy_resource_residual) for report in self.reports), default=0.0),
                "teacher_time": sum(report.teacher_time_debit for report in self.reports),
                "learner_time": sum(report.learner_time_debit for report in self.reports),
                "max_time_tokens_used": self.max_time_used,
                "replay_digest": self.stream.hexdigest(), "decision_records": len(self.decision_samples),
                "biological_edges": len(self.biological_edges), "cultural_edges": len(self.cultural_edges),
                "mean_population": sum(report.population_next for report in self.reports) / max(1, len(self.reports)),
                "net_energy_per_agent_season": ((self.resource + sum(person.energy for person in self.population.values())) - self.initial_total_stock) / max(1., sum(report.population_next for report in self.reports)),
                "birth_flux": sum(report.births for report in self.reports), "death_flux": sum(report.deaths for report in self.reports),
                "stage_counts": {"juvenile": sum(person.age < self.TAU for person in self.population.values()), "adult": sum(person.age >= self.TAU for person in self.population.values())},
                "stored_knowledge": sum(len(person.K) for person in self.population.values()),
                "evidence_accuracy": (sum(person.B.get(f"{family}:branch={self._target_branch(family)}", .5) for person in self.population.values() for family in self.theta) / max(1, 2 * len(self.population))),
                "revision_rate": self.revisions / max(1, self.season * 64),
                "override_rate": self.override_applied / max(1, self.override_opportunities),
                "cultural_action_accuracy": self.culturally_correct / self.cultural_decisions if self.cultural_decisions else None,
                "verification_price": self.verification_price, "graph_variant": self.graph_variant,
                "initial_traits": dict(self.population[next(iter(self.population))].traits) if self.population else {}}
