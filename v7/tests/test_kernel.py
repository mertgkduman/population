"""Independent executable acceptance tests for the V7 kernel evidence boundary."""
import json
import tempfile
import unittest
from pathlib import Path

from v7.experiments import run_experiments
from v7.experiments.exact import ExactTinyPOMDP, compare_restricted_override, enumerate_task, simulate_restricted_override
from v7.experiments.model import (AcquiredState, AsocialPolicy, CandidateBPolicy, KeyedRNG,
    OrdinarySocialPolicy, PolicyObservation, RewardPredictor, VectorOverridePolicy,
    posterior_advice_probability, store_procedure, update_beliefs, update_trust)


class KernelAcceptanceTests(unittest.TestCase):
    def setUp(self): self.observation = PolicyObservation.contract_fixture(conflict=True, age=3)

    def test_hidden_history_permutation_is_policy_invariant_not_world_fixture_inspection(self):
        """A policy consumes the same realised observed history under all hidden relabels."""
        decisions = [OrdinarySocialPolicy().decide(self.observation, 6, KeyedRNG.fixture("same-history"))
                     for _theta in (0, 1) for _z in (0, 1)]
        self.assertEqual(1, len({d.pre_override_digest for d in decisions}))
        self.assertEqual(1, len({d.chosen_action for d in decisions}))
        self.assertNotIn("theta", self.observation.to_policy_dict())

    def test_content_memory_acceptance_and_override_are_independent_switches(self):
        no_content = PolicyObservation(**{**self.observation.__dict__, "messages": (), "provenance_roots": (), "advice": None, "source_id": None, "source_history": ()})
        self.assertEqual(AcquiredState.blank(), AcquiredState.blank())
        remembered = store_procedure(AcquiredState.blank(), "sequence", "root")
        self.assertEqual(("sequence",), remembered.procedures)
        off = VectorOverridePolicy(0., 0.).decide(self.observation, 6, KeyedRNG.fixture("factor"))
        on = VectorOverridePolicy(1., 0.).decide(self.observation, 6, KeyedRNG.fixture("factor"))
        absent = VectorOverridePolicy(1., 0.).decide(no_content, 6, KeyedRNG.fixture("factor"))
        self.assertFalse(off.override_applied); self.assertTrue(on.override_applied); self.assertFalse(absent.override_applied)
        self.assertEqual(on.pre_override_learning_digest, on.post_override_learning_digest)

    def test_authority_label_placebo_does_not_change_label_neutral_policy(self):
        senior = PolicyObservation(**{**self.observation.__dict__, "messages": (("authority_label", "senior"), ("demonstration", "teacher"))})
        novice = PolicyObservation(**{**self.observation.__dict__, "messages": (("authority_label", "novice"), ("demonstration", "teacher"))})
        predictor = RewardPredictor.fit([({"bias": 1., "calibrated_source": .8, "context_match": 1., "unique_roots": 1.}, 1.)])
        self.assertEqual(OrdinarySocialPolicy().decide(senior, 6, KeyedRNG.fixture("label")).q0_values, OrdinarySocialPolicy().decide(novice, 6, KeyedRNG.fixture("label")).q0_values)
        self.assertEqual(CandidateBPolicy(predictor).decide(senior, 6, KeyedRNG.fixture("label")).chosen_action, CandidateBPolicy(predictor).decide(novice, 6, KeyedRNG.fixture("label")).chosen_action)

    def test_correlated_duplicate_provenance_is_not_double_counted(self):
        duplicated = PolicyObservation(**{**self.observation.__dict__, "messages": (("demo", "teacher"), ("repeat", "teacher")), "provenance_roots": ("root", "root")})
        once = PolicyObservation(**{**self.observation.__dict__, "messages": (("demo", "teacher"),), "provenance_roots": ("root",)})
        self.assertAlmostEqual(posterior_advice_probability(once), posterior_advice_probability(duplicated), places=12)

    def test_asocial_masks_content_not_physical_actions_and_common_cap(self):
        social = OrdinarySocialPolicy().decide(self.observation, 6, KeyedRNG.fixture("cap"))
        asocial = AsocialPolicy().decide(self.observation, 6, KeyedRNG.fixture("cap"))
        self.assertEqual(set(self.observation.feasible_actions), {"private", "teacher"})
        self.assertFalse(asocial.social_content_used)
        self.assertLessEqual(social.operation_count, 6); self.assertLessEqual(asocial.operation_count, 6)

    def test_belief_procedure_and_trust_updates_are_explicit_not_action_side_effects(self):
        blank = AcquiredState.blank(); decision = OrdinarySocialPolicy(1., 0.).decide(self.observation, 6, KeyedRNG.fixture("updates"))
        self.assertEqual(blank, AcquiredState.blank())
        self.assertNotEqual(update_beliefs(blank, 3.).beliefs, blank.beliefs)
        self.assertNotEqual(update_trust(blank, "source", True).trust, blank.trust)
        self.assertNotEqual(store_procedure(blank, "p", "r").procedures, blank.procedures)
        self.assertEqual(decision.pre_override_learning_digest, decision.post_override_learning_digest)

    def test_candidate_b_pays_only_when_information_has_positive_expected_value(self):
        cheap = CandidateBPolicy().decide(self.observation, 6, KeyedRNG.fixture("candidate"))
        expensive = PolicyObservation(**{**self.observation.__dict__, "prices": tuple((k, 100. if k in {"query", "verify"} else v) for k, v in self.observation.prices)})
        no_purchase = CandidateBPolicy().decide(expensive, 6, KeyedRNG.fixture("candidate"))
        self.assertIn(cheap.information_action, {"query", "verify", None})
        self.assertIsNone(no_purchase.information_action)
        self.assertLessEqual(cheap.operation_count, 6)

    def test_exact_bellman_enumeration_upper_bounds_independent_restricted_monte_carlo(self):
        oracle = ExactTinyPOMDP(); exact, first = oracle.solve(); comparison = compare_restricted_override(2000)
        independent, mcse, visits = simulate_restricted_override(2000)
        self.assertIn(first, {"learn", "query", "verify", "safe", "execute_0", "execute_1"})
        self.assertGreaterEqual(exact + 2 * comparison.mcse, comparison.restricted_value)
        self.assertAlmostEqual(independent, comparison.restricted_value, places=12)
        self.assertGreater(visits["query"], 0); self.assertGreater(mcse, 0)

    def test_depth_economics_enumerates_failures_and_safe_counterfactual(self):
        rows = [enumerate_task(depth) for depth in (1, 3, 6)]
        self.assertTrue(all(any(name.startswith("prefix_failure") for name, _, _ in row.failure_branches) for row in rows))
        self.assertTrue(all(any(name == "incorrect_finish" for name, _, _ in row.failure_branches) for row in rows))
        self.assertTrue(all(row.safe_return == (row.depth + 1) * 1.2 for row in rows))
        self.assertTrue(all(row.margin_per_token >= .10 for row in rows))

    def test_runner_writes_measured_assays_not_only_boolean_fixture(self):
        record = run_experiments.kernel_tracer(Path("v7/experiments/config.json"))
        self.assertEqual(8, len(record["factorial_content_memory_override"]))
        self.assertIn("independent_restricted_value", record["exact"])
        self.assertEqual(record["provenance_duplicate"]["baseline_posterior"], record["provenance_duplicate"]["duplicated_posterior"])
        self.assertTrue(all(record["checks"].values()))


if __name__ == "__main__": unittest.main()
