"""Finite two-episode Bayes-adaptive oracle and transparent task economics.

The oracle enumerates posterior states over hidden procedure bit ``theta`` and fast
local-context bit ``z``.  It never receives a realized world during planning: hidden
worlds appear only inside expectation/integration and independent Monte Carlo checks.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from math import ceil
from random import Random
from typing import Callable, Iterable

from v7.experiments.model import KeyedRNG, OrdinarySocialPolicy, PolicyObservation

P_PLUS, SAFE_YIELD, STEP_COST, SALVAGE, INCORRECT_FINISH_LOSS = .90, 1.20, .20, .20, 2.0


def correct_finish_reward(depth: int) -> float:
    if depth not in {1, 3, 6}: raise ValueError("V7 primary depths are 1, 3, and 6")
    # The physical contract has D prerequisite hazards plus the finish hazard;
    # calibrate before any policy outcomes so adequacy is not a tuning artifact.
    # There are D prerequisites *and* one terminal finish hazard.  The denominator
    # therefore uses D+1 successes; this is the outcome-blind calibration required
    # for the depth-one .10-per-token adequacy gate.
    return ceil(((depth + 1) * (SAFE_YIELD + .30) + depth * STEP_COST) / P_PLUS**(depth + 1) * 10) / 10


@dataclass(frozen=True)
class TaskEconomics:
    depth: int; reward: float; safe_return: float; procedure_return: float; margin_per_token: float
    failure_branches: tuple[tuple[str, float, float], ...]


@lru_cache(maxsize=32)
def enumerate_task(depth: int, step_probability: float = P_PLUS) -> TaskEconomics:
    """Enumerate every failed prefix and finish, including material and salvage costs."""
    if not 0. < step_probability < 1.: raise ValueError("step probability must lie strictly between zero and one")
    reward, safe = correct_finish_reward(depth), (depth + 1) * SAFE_YIELD
    branches: list[tuple[str, float, float]] = []
    expected, survival = 0., 1.
    for completed in range(depth):
        probability = survival * (1 - step_probability)
        # The failed attempt has paid its material charge; only completed prefixes salvage.
        value = -(completed + 1) * STEP_COST + completed * SALVAGE
        branches.append((f"prefix_failure_{completed + 1}", probability, value)); expected += probability * value
        survival *= step_probability
    # The finish is an actual risky physical event, not omitted from the accounting.
    correct_probability, incorrect_probability = survival * step_probability, survival * (1 - step_probability)
    correct_value, incorrect_value = reward - depth * STEP_COST, -INCORRECT_FINISH_LOSS - depth * STEP_COST + depth * SALVAGE
    branches.extend((("correct_finish", correct_probability, correct_value), ("incorrect_finish", incorrect_probability, incorrect_value)))
    expected += correct_probability * correct_value + incorrect_probability * incorrect_value
    return TaskEconomics(depth, reward, safe, expected, (expected - safe) / (depth + 1), tuple(branches))


def task_economics_table(depths: Iterable[int] = (1, 3, 6)) -> list[TaskEconomics]: return [enumerate_task(d) for d in depths]


def sample_task_outcome(depth: int, step_probability: float, uniform: Callable[[int], float]) -> tuple[str, int, float]:
    """Shared physical D-step kernel used by IBM and empirical parity checks.

    ``uniform(step)`` is a keyed independent draw.  Returned value is the exact
    terminal branch name, completed prerequisite count, and material payoff before
    resource conversion.  It deliberately has no access to theta or policy state.
    """
    for step in range(depth):
        if uniform(step) >= step_probability:
            completed = step
            return f"prefix_failure_{step + 1}", completed, -(completed + 1) * STEP_COST + completed * SALVAGE
    if uniform(depth) < step_probability:
        return "correct_finish", depth, correct_finish_reward(depth) - depth * STEP_COST
    return "incorrect_finish", depth, -INCORRECT_FINISH_LOSS - depth * STEP_COST + depth * SALVAGE


World = tuple[int, int]  # theta, z
WORLDS: tuple[World, ...] = ((0, 0), (0, 1), (1, 0), (1, 1))


@dataclass(frozen=True)
class TinyState:
    episode: int
    posterior: tuple[float, float, float, float]
    time_left: int
    operations_left: int
    learned: bool = False
    queried: bool = False
    verified: bool = False


@dataclass(frozen=True)
class ExactComparison:
    exact_value: float; restricted_value: float; mcse: float; upper_bound_holds: bool
    exact_first_action: str; restricted_replicates: int


@dataclass
class ExactTinyPOMDP:
    """Enumerated finite POMDP with learn/query/verify/execute/safe actions."""
    episodes: int = 2
    time_budget: int = 3
    operation_budget: int = 6
    delta: float = .97
    z_flip: float = .35
    private_accuracy: float = .80
    source_accuracy: float = .75
    verify_accuracy: float = .90
    operation_price: float = .01
    action_visits: dict[str, float] = field(default_factory=dict)

    @staticmethod
    def target(world: World) -> int: return world[0] ^ world[1]
    def initial_state(self) -> TinyState: return TinyState(0, (.25, .25, .25, .25), self.time_budget, self.operation_budget)
    def _norm(self, weights: list[float]) -> tuple[float, float, float, float]:
        total = sum(weights); return tuple(w / total for w in weights)  # type: ignore[return-value]
    def _signal_probability(self, action: str, world: World, outcome: int) -> float:
        theta, z = world
        if action == "learn": return self.private_accuracy if outcome == theta else 1 - self.private_accuracy
        if action == "query": return self.source_accuracy if outcome == self.target(world) else 1 - self.source_accuracy
        if action == "verify": return self.verify_accuracy if outcome == z else 1 - self.verify_accuracy
        if action.startswith("execute_"):
            success = int(action[-1]) == self.target(world); return 1.0 if outcome == int(success) else 0.0
        raise ValueError(action)
    def _observe(self, posterior: tuple[float, ...], action: str, outcome: int) -> tuple[float, float, float, float]:
        return self._norm([p * self._signal_probability(action, w, outcome) for p, w in zip(posterior, WORLDS)])
    def _outcome_probability(self, posterior: tuple[float, ...], action: str, outcome: int) -> float:
        return sum(p * self._signal_probability(action, w, outcome) for p, w in zip(posterior, WORLDS))
    def _advance_context(self, posterior: tuple[float, ...]) -> tuple[float, float, float, float]:
        moved = [0.] * 4
        for index, (theta, z) in enumerate(WORLDS):
            for next_index, candidate in enumerate(WORLDS):
                if candidate[0] == theta:
                    moved[next_index] += posterior[index] * (1 - self.z_flip if candidate[1] == z else self.z_flip)
        return tuple(moved)  # type: ignore[return-value]
    def feasible_actions(self, state: TinyState) -> tuple[str, ...]:
        actions = ["safe", "execute_0", "execute_1"]
        if state.time_left >= 1 and state.operations_left >= 2 and not state.learned: actions.append("learn")
        if state.time_left >= 1 and state.operations_left >= 1 and not state.queried: actions.append("query")
        if state.time_left >= 1 and state.operations_left >= 3 and not state.verified: actions.append("verify")
        return tuple(actions)
    def _execute_value(self, posterior: tuple[float, ...], action: str) -> float:
        success = self._outcome_probability(posterior, action, 1)
        return success * 3.0 + (1 - success) * -2.0 - .20 - self.operation_price
    def _next_episode(self, state: TinyState, posterior: tuple[float, ...]) -> TinyState | None:
        if state.episode + 1 >= self.episodes: return None
        return TinyState(state.episode + 1, self._advance_context(posterior), self.time_budget, self.operation_budget)
    def _key(self, state: TinyState) -> tuple: return (state.episode, tuple(round(p, 12) for p in state.posterior), state.time_left, state.operations_left, state.learned, state.queried, state.verified)
    def solve(self) -> tuple[float, str]:
        @lru_cache(maxsize=None)
        def value(key: tuple) -> float:
            state = TinyState(key[0], key[1], key[2], key[3], key[4], key[5], key[6])
            options: dict[str, float] = {}
            for action in self.feasible_actions(state):
                if action in {"safe", "execute_0", "execute_1"}:
                    immediate = SAFE_YIELD if action == "safe" else self._execute_value(state.posterior, action)
                    if action == "safe": next_value = value(self._key(n)) if (n := self._next_episode(state, state.posterior)) else 0.
                    else:
                        next_value = sum(self._outcome_probability(state.posterior, action, outcome) * (value(self._key(n)) if (n := self._next_episode(state, self._observe(state.posterior, action, outcome))) else 0.) for outcome in (0, 1))
                    options[action] = immediate + self.delta * next_value
                else:
                    op, cost = {"learn": (2, .10), "query": (1, .10), "verify": (3, .20)}[action]
                    next_base = TinyState(state.episode, state.posterior, state.time_left - 1, state.operations_left - op, state.learned or action == "learn", state.queried or action == "query", state.verified or action == "verify")
                    options[action] = -cost - self.operation_price * op + sum(self._outcome_probability(state.posterior, action, outcome) * value(self._key(TinyState(next_base.episode, self._observe(state.posterior, action, outcome), next_base.time_left, next_base.operations_left, next_base.learned, next_base.queried, next_base.verified))) for outcome in (0, 1))
            return max(options.values())
        start = self.initial_state(); first_values = {a: self._action_value(start, a, value) for a in self.feasible_actions(start)}
        return value(self._key(start)), max(first_values, key=first_values.get)
    def _action_value(self, state: TinyState, action: str, value: Callable[[tuple], float]) -> float:
        # Mirrors solve for first-action evidence reporting without exposing hidden world.
        if action == "safe":
            n = self._next_episode(state, state.posterior); return SAFE_YIELD + self.delta * (value(self._key(n)) if n else 0.)
        if action.startswith("execute"):
            continuation = sum(self._outcome_probability(state.posterior, action, outcome) * (value(self._key(n)) if (n := self._next_episode(state, self._observe(state.posterior, action, outcome))) else 0.) for outcome in (0, 1))
            return self._execute_value(state.posterior, action) + self.delta * continuation
        op, cost = {"learn": (2, .10), "query": (1, .10), "verify": (3, .20)}[action]
        nxt = TinyState(state.episode, state.posterior, state.time_left-1, state.operations_left-op, action == "learn", action == "query", action == "verify")
        return -cost - self.operation_price * op + sum(self._outcome_probability(state.posterior, action, o) * value(self._key(TinyState(nxt.episode, self._observe(state.posterior, action, o), nxt.time_left, nxt.operations_left, nxt.learned, nxt.queried, nxt.verified))) for o in (0, 1))


def _bernoulli(rng: Random, probability: float) -> int: return int(rng.random() < probability)


def simulate_restricted_override(replicates: int = 4000, seed: int = 117) -> tuple[float, float, dict[str, int]]:
    """Independent forward simulation of a restricted ordinary/social override policy.

    It samples realized worlds only after the policy contract is fixed, runs the same
    information actions/costs/caps as the oracle, and evaluates the actual utility.
    """
    rng, policy, returns, visits = Random(seed), OrdinarySocialPolicy(1.0, 1.0), [], {a: 0 for a in ("learn", "query", "verify", "safe", "execute_0", "execute_1")}
    for replicate in range(replicates):
        theta, z, total = rng.randrange(2), rng.randrange(2), 0.
        for episode in range(2):
            # The restricted controller consumes the same finite information menu in a fixed, non-EVI order.
            learn = _bernoulli(rng, .8 if theta else .2); query = _bernoulli(rng, .75 if (theta ^ z) else .25); verify = _bernoulli(rng, .9 if z else .1)
            visits["learn"] += 1; visits["query"] += 1; visits["verify"] += 1; total -= .10 + .10 + .20 + .01 * 6
            advice = f"execute_{query}"
            observation = PolicyObservation(f"r{replicate}", episode, 3, 8., 3, 6, "procedure", "supports_advice" if learn == query else "supports_private", (("p_advice", .5), ("private_likelihood", .8)), (), (("tutor", .75),), (), (("message", advice),), (f"root-{episode}",), ("execute_0", "execute_1", "safe"), (("execute_0", 0.), ("execute_1", 0.), ("safe", SAFE_YIELD)), (("operation", .01), ("correct_reward", 3.), ("incorrect_loss", 2.)), advice, "tutor", (("successes", 6.), ("failures", 2.)), 0.)
            decision = policy.decide(observation, 6, KeyedRNG.fixture(f"restricted-{replicate}-{episode}")); action = decision.chosen_action
            visits[action] = visits.get(action, 0) + 1
            if action == "safe": total += SAFE_YIELD
            else: total += (3.0 if action == f"execute_{theta ^ z}" else -2.0) - .20
            z = z if rng.random() >= .35 else 1-z
        returns.append(total)
    mean = sum(returns) / len(returns); variance = sum((x-mean)**2 for x in returns) / (len(returns)-1)
    return mean, (variance / len(returns)) ** .5, visits


def compare_restricted_override(replicates: int = 4000) -> ExactComparison:
    oracle = ExactTinyPOMDP(); exact, first_action = oracle.solve(); restricted, mcse, _ = simulate_restricted_override(replicates)
    return ExactComparison(exact, restricted, mcse, exact + 2 * mcse >= restricted, first_action, replicates)
