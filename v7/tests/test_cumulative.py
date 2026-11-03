"""Contracts for the corrected separate V7 §5.1 cognitive assay."""
import unittest
class CumulativeAssayTests(unittest.TestCase):
    def test_blank_newborn_budget_and_private_evidence_are_real(self):
        from v7.experiments.cumulative import Learner, ProcedureProgram, PRIVATE_ACCURACY, VERIFY_COST
        learner, program = Learner.blank("newborn"), ProcedureProgram.contract_fixture()
        for identifier in program.order("water"): learner = program.private_verify(learner, identifier, 74601)
        self.assertEqual(PRIVATE_ACCURACY, .8); self.assertLessEqual(learner.private_verifications, 2); self.assertLessEqual(learner.private_work, 2 * VERIFY_COST)
    def test_paid_teaching_and_two_edge_function_are_observed(self):
        from v7.experiments.cumulative import run_cell
        rows = [run_cell(seed=s, arm="transmission_innovation") for s in range(74601, 74625)]
        self.assertTrue(all(r["teacher_work_debits"] == r["learner_work_debits"] for r in rows)); self.assertTrue(all(r["total_work"] == 360 for r in rows)); self.assertGreater(sum(r["two_edge_functional_procedures"] for r in rows), 0)
    def test_all_six_controls_have_equal_ledgers_and_viable_evaluation(self):
        from v7.experiments.cumulative import ARMS, run_cell
        rows = [run_cell(seed=74602, arm=a) for a in ARMS]
        self.assertEqual({r["total_work"] for r in rows}, {360}); self.assertEqual({r["material_debit"] for r in rows}, {3.6}); self.assertTrue(all(r["mean_heldout_functional_score"] in {0.0, .5, 1.0} for r in rows)); self.assertTrue(next(r for r in rows if r["arm"] == "matched_total_work_independent_upper_bound")["upper_bound_only"])
