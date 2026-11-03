from __future__ import annotations
import unittest
from v7.experiments.recovery_causal import adult_trajectory, wilson


class RecoveryCausalTests(unittest.TestCase):
    def test_adult_has_twenty_sequential_updates_each_direction(self) -> None:
        for direction in (1, -1):
            rows = adult_trajectory(84001, direction)
            self.assertEqual([row["step"] for row in rows], list(range(1, 21)))
            self.assertTrue(all(row["direct_adult_inherited_override"] == 0.0 for row in rows))
            self.assertTrue(all(row["likelihood_strength"] == .8 for row in rows))
            self.assertTrue(all({"B_factual_belief", "K_acquired_procedure", "H_learned_action_value", "T_source_trust"} <= set(row) for row in rows))

    def test_wilson_uses_explicit_denominator(self) -> None:
        value = wilson(3, 24)
        self.assertEqual(value["n"], 24)
        self.assertGreater(value["half_width"], 0.0)
        self.assertIsNone(wilson(0, 0)["half_width"])
