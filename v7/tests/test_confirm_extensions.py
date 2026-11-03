"""Unit contracts for the post-freeze precision scheduler."""
from __future__ import annotations

import unittest

from v7.experiments.confirm_extensions import DepthAwareReliabilityPolicy, _precision
from v7.experiments.model import KeyedRNG, PolicyObservation


def row(seed: int, policy: str, energy: float, population: float, status: str = "running") -> dict[str, str]:
    return {"seed": str(seed), "policy": policy, "regime": "0", "net_energy_per_agent_season": str(energy),
            "mean_population": str(population), "status": status}


class ConfirmationPrecisionTests(unittest.TestCase):
    def test_paired_energy_uses_seed_matched_differences(self) -> None:
        rows = [row(1, "vector_0_0", 1.0, 20), row(2, "vector_0_0", 1.0, 20),
                row(1, "candidate_b_resource_rational", 2.0, 20), row(2, "candidate_b_resource_rational", 2.0, 20),
                row(1, "feature_trust", 1.5, 20), row(2, "feature_trust", 1.5, 20)]
        audit = _precision(rows, expected_seeds=[1, 2])
        record = next(item for item in audit["records"] if item["kind"] == "paired_net_energy" and item["policy"] == "feature_trust" and item["baseline"] == "vector_0_0")
        self.assertEqual(record["n"], 2)
        self.assertEqual(record["net_energy_paired_mcse"], 0.0)

    def test_unstored_trial_denominators_remain_unresolved(self) -> None:
        rows = [row(1, "vector_0_0", 1.0, 20), row(2, "vector_0_0", 1.0, 20),
                row(1, "candidate_b_resource_rational", 1.0, 20), row(2, "candidate_b_resource_rational", 1.0, 20)]
        audit = _precision(rows, expected_seeds=[1, 2])
        within = next(item for item in audit["records"] if item["kind"] == "within_policy")
        self.assertIn("UNRESOLVED", within["other_trial_level_proportions"])

    def test_depth_aware_control_corrects_complete_procedure_noise(self) -> None:
        base = PolicyObservation.contract_fixture()
        procedure = PolicyObservation(**{**base.__dict__, "private_cue": "branch_0", "beliefs": (("p_branch_0", .5), ("p_branch_1", .5), ("private_likelihood", .8)),
            "feasible_actions": ("branch_0", "branch_1"), "action_values": (("branch_0", 0.), ("branch_1", 0.)), "advice": "branch_1",
            "prices": (("operation", .01), ("execute", 1.2), ("procedure_expected_plus", 2.), ("procedure_expected_minus", -1.)),
            "source_history": (("successes", 0.), ("failures", 1.))})
        decision = DepthAwareReliabilityPolicy().decide(procedure, 128, KeyedRNG.fixture("depth-aware"))
        # At D=6, the failure likelihood is evaluated as 1-.9^7 versus 1-.5^7,
        # not as a generic raw-success fraction.
        self.assertLess(decision.posterior_advice, .5)
        self.assertEqual(decision.operation_count, 5)
        no_offer = PolicyObservation(**{**procedure.__dict__, "messages": (), "provenance_roots": (), "advice": None, "source_id": None, "source_history": ()})
        self.assertEqual(DepthAwareReliabilityPolicy().decide(no_offer, 128, KeyedRNG.fixture("no-offer")).operation_count, 1)


if __name__ == "__main__":
    unittest.main()
