from dataclasses import replace
import unittest
from v7.experiments.execution_planner import ExecutionPlanner,CountedExecutionWorld
from v7.experiments.model import PolicyObservation,KeyedRNG
class ExecutionPlannerTests(unittest.TestCase):
    def test_information_cannot_prevent_physical_action(self):
        obs=replace(PolicyObservation.contract_fixture(),time_tokens=1)
        self.assertIsNone(ExecutionPlanner().decide(obs,128,KeyedRNG.fixture('t')).information_action)
    def test_deliberation_is_common_sunk_cost(self):
        class Free(ExecutionPlanner):DELIBERATION=0
        obs=PolicyObservation.contract_fixture();rng=KeyedRNG.fixture('t')
        a,b=ExecutionPlanner().decide(obs,128,rng),Free().decide(obs,128,rng)
        self.assertEqual(a.information_action,b.information_action)
        self.assertAlmostEqual(a.charged_cost-b.charged_cost,.12)
    def test_durable_world_counters_and_actual_budgets(self):
        world=CountedExecutionWorld(82700,ExecutionPlanner,depth=3,burn_in=0,measurement=8)
        r=world.run();self.assertLessEqual(r['max_time_tokens_used'],12);self.assertLess(r['ledger_residual_max'],1e-8)
        self.assertEqual(r['count_teacher_present']+r['count_no_teacher'],r['count_all_initial_decisions'])
        self.assertLessEqual(r['count_query_purchases']+r['count_verify_purchases'],r['count_all_initial_decisions'])
if __name__=='__main__':unittest.main()
