"""R1a matched bounded comparator over the immutable corrected ecology interface.

The comparator is deliberately a one-decision, action-conditional information
planner.  It has no hidden state access and is not called optimal or general RL.
"""
from __future__ import annotations

from math import log

from v7.experiments.model import (KeyedRNG, OrdinarySocialPolicy, PolicyDecision,
                                  PolicyObservation, _logit, _logistic, _map,
                                  posterior_advice_probability, validate_policy_observation)


class MatchedActionConditionalPolicy(OrdinarySocialPolicy):
    """Bounded query/verify comparator with execution-matched signal accuracies.

    ``query`` is .80 both in this expectation and in ``EcologyRun`` execution;
    ``verify`` is .90 in both.  The ecology performs the actual one-token debit,
    posted material charge, common production, and operation charging.
    """
    QUERY_ACCURACY = .80
    VERIFY_ACCURACY = .90
    EXPECTATION_OPERATIONS = 12  # two binary posterior/action evaluations

    @staticmethod
    def _posterior_after(posterior: float, accuracy: float, signal_supports_advice: bool) -> float:
        return _logistic(_logit(posterior) + (1 if signal_supports_advice else -1) * log(accuracy / (1 - accuracy)))

    def _signal_value(self, observation: PolicyObservation, posterior: float, accuracy: float) -> float:
        """Expected post-signal physical action value before paid information costs."""
        positive = posterior * accuracy + (1.0 - posterior) * (1.0 - accuracy)
        yes = self._posterior_after(posterior, accuracy, True)
        no = self._posterior_after(posterior, accuracy, False)
        return positive * max(v for _, v in self._q0_with_posterior(observation, yes)) + (1.0 - positive) * max(v for _, v in self._q0_with_posterior(observation, no))

    def decide(self, observation: PolicyObservation, operation_cap: int, keyed_rng: KeyedRNG) -> PolicyDecision:
        observation = validate_policy_observation(observation)
        prices = _map(observation.prices)
        posterior = posterior_advice_probability(observation)
        base = self._q0(observation)
        base_value = max(v for _, v in base)
        # Every selected information action faces its actual posted price, one
        # actual ecology time token, and its computation charge.  The utility is
        # the same physical Q0 utility used by residents, never an added d reward.
        common = prices.get("time_opportunity", 0.) + prices.get("operation", 0.) * self.EXPECTATION_OPERATIONS
        options = [(None, base_value),
                   ("query", self._signal_value(observation, posterior, self.QUERY_ACCURACY) - prices.get("query", 0.) - common),
                   ("verify", self._signal_value(observation, posterior, self.VERIFY_ACCURACY) - prices.get("verify", 0.) - common)]
        choice, value = max(options, key=lambda pair: (pair[1], str(pair[0])))
        return self._decision(observation, operation_cap, keyed_rng, allow_override=False,
                              social=True, information_action=choice,
                              information_value=value - base_value,
                              computation_operations=self.EXPECTATION_OPERATIONS)


def comparator_contract() -> dict[str, object]:
    return {
        "name": "matched_action_conditional_bounded_planner",
        "query_expected_accuracy": MatchedActionConditionalPolicy.QUERY_ACCURACY,
        "query_executed_accuracy": .80,
        "verify_expected_accuracy": MatchedActionConditionalPolicy.VERIFY_ACCURACY,
        "verify_executed_accuracy": .90,
        "private_hardware_accuracy": .80,
        "interface_limit": "One-decision action-conditional EVI; no Bellman continuation, no general/optimal-RL claim.",
        "cost_parity": "Common 12-token and 128-operation caps; ecology charges selected query/verify time and posted price, common production, and operation price.",
    }
