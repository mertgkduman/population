import unittest

from v7.experiments.information_controls import (TUTOR_ACCURACY, adult_reuse, exact_benchmark,
    information_rows, memory_training, public_posterior)


class InformationControlTests(unittest.TestCase):
    def test_exact_three_signal_and_copy_likelihood_benchmarks(self):
        exact = exact_benchmark()
        self.assertAlmostEqual(exact["q_tutor_enumerated"], TUTOR_ACCURACY, places=12)
        self.assertAlmostEqual(public_posterior((1, 1), "copied", True), .896, places=12)
        self.assertGreater(public_posterior((1, 1), "independent", True), .896)
        self.assertTrue(exact["visible_copy_duplicate_invariant"])

    def test_actual_histories_have_true_independent_or_shared_roots_and_hidden_mixture(self):
        rows = information_rows(83301); children = [r for r in rows if r["assay"] == "authority_provenance_child"]
        self.assertEqual(2, len([r for r in rows if r["assay"] == "tutor_acquisition"]))
        self.assertTrue(all(len(r["tutorA_private_history"]) == 3 for r in children))
        self.assertTrue(all(r["hidden_structure_prior_independent"] == .5 for r in children if not r["provenance_visible"]))
        self.assertTrue(all(len(set(r["public_message_roots"])) == (2 if r["provenance_structure"] == "independent" else 1) for r in children))

    def test_label_sensitive_is_an_unconfounded_imposed_positive_control(self):
        rows = [r for r in information_rows(83302) if r["assay"] == "authority_provenance_child"]
        d0 = [r for r in rows if r["policy"] == "label_neutral_d0"]
        self.assertTrue(all(not r["override"] for r in d0))
        for role in ("peer", "authority"):
            pair = [r for r in rows if r["policy"] == "authority_sensitive" and r["role_label"] == role]
            self.assertTrue(all(r["role_label_uninformative"] for r in pair))
            self.assertTrue(all(r["policy_is_imposed_positive_control"] for r in pair))

    def test_memory_and_override_are_distinct_and_adults_replay_acquired_state(self):
        training = memory_training(84301, 1, .5)
        self.assertEqual(list(range(40)), [r["episode"] for r in training])
        self.assertTrue(all(r["receipt_cost"] == .1 for r in training))
        self.assertTrue(all(r["accepted_memory"] is not None for r in training))
        adult = adult_reuse(84301, 1, .5, training)
        self.assertEqual(list(range(20)), [r["step"] for r in adult])
        self.assertTrue(all(r["direct_adult_inherited_override"] == 0 for r in adult))
        self.assertTrue(all(r["stored_memory_reused"] for r in adult))


if __name__ == "__main__": unittest.main()
