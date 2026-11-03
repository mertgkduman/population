import unittest
from dataclasses import replace

from v7.experiments.cumulative_dag import ARMS, Settings, heldout_two_edge_test, pair, run


class CumulativeDagTests(unittest.TestCase):
    def test_stock_population_time_and_blank_births_close(self):
        for arm in ARMS:
            world = run(82900, arm)
            self.assertLess(world.result()["max_residual"], 1e-7)
            self.assertLessEqual(world.result()["max_person_work"], 4)
            prior = 10
            for row in world.history:
                self.assertEqual(row["N"], prior + row["births"] - row["deaths"] - row["removals"])
                self.assertEqual(row["N"], row["F"] + row["A"])
                self.assertEqual(row["realized"], row["offered"])
                prior = row["N"]

    def test_paid_blank_newborn_and_prospective_cap(self):
        cfg = replace(Settings(), horizon=1, maturity=1, birth_probability=1.0)
        world = run(82900, "private_only", cfg)
        children = [p for p in world.people.values() if p.parent]
        self.assertEqual(len(children), 10)
        self.assertTrue(all(p.age == 0 and not p.receipts and not p.private_progress for p in children))
        capped = run(82900, "private_only", replace(cfg, population_cap=10))
        self.assertEqual(capped.status, "cap_censored")
        self.assertEqual(len(capped.people), 10)

    def test_retention_ablation_clears_all_learned_state(self):
        world = run(82900, "no_retention")
        self.assertTrue(all(not p.receipts and not p.private_progress for p in world.people.values()))
        self.assertEqual(world.result()["functional"], 0)

    def test_scramble_has_actual_different_prerequisite_shape(self):
        canonical = run(82900, "transmission_innovation_retention")
        scrambled = run(82900, "causal_prerequisite_scramble")
        self.assertNotEqual(canonical.prereqs, scrambled.prereqs)
        self.assertEqual(len([m for m, ps in canonical.prereqs.items() if not ps]), 2)
        self.assertEqual(len([m for m, ps in scrambled.prereqs.items() if not ps]), 3)

    def test_matched_independent_populations_never_pool_and_match_work(self):
        shared, independent = pair(82900)
        self.assertIsNot(shared.people, independent.people)
        self.assertIsNot(shared.receipts, independent.receipts)
        self.assertEqual(len(shared.history), len(independent.history))
        for a, b in zip(shared.history, independent.history):
            self.assertEqual(a["offered"], b["offered"])
            self.assertEqual(a["realized"], b["realized"])
            self.assertEqual(a["realized"], a["offered"])

    def test_heldout_retains_no_source_or_records_paid_edges(self):
        result = heldout_two_edge_test(run(82900, "transmission_innovation_retention"))
        if result["status"] == "passed":
            self.assertTrue(result["blank_recipients"])
            self.assertTrue(result["two_actual_paid_edges_per_module"])
            self.assertEqual(len(result["edges"]), 16)
            self.assertEqual(result["physical_tests"][0]["physical_performance"], "success")
            self.assertEqual(result["physical_tests"][1]["physical_performance"], "failure")
        else:
            self.assertEqual(result["status"], "no_baseline_full_program")


if __name__ == "__main__":
    unittest.main()
