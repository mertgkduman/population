import unittest
from dataclasses import replace

from v7.experiments.cumulative_dag import Settings, pair


class MatchedCumulativeDagTests(unittest.TestCase):
    def test_separate_populations_realize_exact_same_ex_ante_offer(self):
        shared, independent = pair(82924)
        self.assertIsNot(shared.people, independent.people)
        self.assertIsNot(shared.receipts, independent.receipts)
        self.assertEqual(len(shared.history), len(independent.history))
        for left, right in zip(shared.history, independent.history):
            self.assertEqual(left["offered"], right["offered"])
            self.assertEqual(left["realized"], right["realized"])
            self.assertEqual(left["realized"], left["offered"])
            self.assertLessEqual(left["max_person_work"], 4)
            self.assertLessEqual(right["max_person_work"], 4)

    def test_pair_does_not_delete_births_to_match(self):
        cfg = replace(Settings(), horizon=3, maturity=1, birth_probability=1.0)
        shared, independent = pair(82924, cfg)
        self.assertGreater(shared.births, 0)
        self.assertGreater(independent.births, 0)
        self.assertEqual(shared.removals, 0)
        self.assertEqual(independent.removals, 0)


if __name__ == "__main__":
    unittest.main()
