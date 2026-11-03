"""Selection-layer regressions; frozen ecology code is exercised but never edited."""
from __future__ import annotations

import unittest


class SelectionTests(unittest.TestCase):
    def test_neutral_gates_fail_closed_and_use_a_natural_paid_birth(self):
        from v7.experiments.evolution import gate_assays
        gates = gate_assays()
        self.assertEqual("passed", gates["status"])
        self.assertTrue(all(gates["checks"].values()))
        birth = gates["self_mutant"]
        self.assertFalse(birth["no_birth_censored"])
        self.assertGreaterEqual(birth["parent_age"], 5)
        self.assertGreaterEqual(birth["parent_energy_before"], 19.0)
        self.assertEqual(16.0, birth["birth_cost"])
        self.assertEqual(8.0, birth["newborn_energy"])
        self.assertTrue(birth["blank_acquired_state"])

    def test_self_mutant_and_neutral_tag_are_bitwise_same_except_external_label(self):
        from v7.experiments.evolution import gate_assays
        gates = gate_assays()
        left = {k: v for k, v in gates["self_mutant"].items() if k != "arm"}
        right = {k: v for k, v in gates["neutral_tag"].items() if k != "arm"}
        self.assertEqual(left, right)

    def test_pair_uses_one_acquired_resident_prefix_and_preserves_blank_child(self):
        from v7.experiments.evolution import paired_lineage
        pair = ((0.0, 0.0), (0.5, 0.0))
        mutant, neutral = paired_lineage(73001, 1, pair, horizon=2)
        self.assertEqual(mutant.born_id, neutral.born_id)
        self.assertEqual(mutant.resident_state_sha256, neutral.resident_state_sha256)
        self.assertTrue(mutant.blank_acquired_state)
        self.assertTrue(neutral.blank_acquired_state)
        self.assertEqual((0.5, 0.0), mutant.mutant_traits)
        self.assertEqual((0.0, 0.0), neutral.mutant_traits)
        self.assertIn("resident acquired", mutant.teacher_pool["source"])

    def test_manifest_is_predeclared_and_bounded(self):
        from v7.experiments.run_evolution import manifest
        record = manifest()
        self.assertTrue(record["registered_before_outcomes"])
        self.assertEqual(2304, record["registered_trajectories"])
        self.assertEqual([73001, 73024], record["seed_schedule"]["initial"])
        self.assertEqual(96, record["seed_schedule"]["maximum"])
        self.assertLess(record["registered_trajectories"], record["caps"]["trajectory_cap"])


if __name__ == "__main__":
    unittest.main()
