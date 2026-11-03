import unittest
from v7.experiments.recovery_comparator_v2 import MarginalCostPlanner,TimeAwareCorrectedRun
from v7.experiments.model import KeyedRNG,PolicyObservation
class ComparatorV2Tests(unittest.TestCase):
 def test_hardware_and_common_cost(self):
  p=MarginalCostPlanner();d=p.decide(PolicyObservation.contract_fixture(),128,KeyedRNG.fixture('x'));self.assertGreaterEqual(d.operation_count,p.COMMON_OP+1);self.assertEqual((p.QUERY_ACC,p.VERIFY_ACC),(.8,.9))
 def test_time_adapter_ledger(self):
  r=TimeAwareCorrectedRun(82401,MarginalCostPlanner,depth=1,burn_in=0,measurement=2);o=r.run();self.assertLessEqual(o['max_time_tokens_used'],12);self.assertLessEqual(o['ledger_residual_max'],1e-8)
