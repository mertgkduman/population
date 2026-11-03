import unittest
from v7.experiments.belief_control import train,adult,ARMS
class BeliefControlTests(unittest.TestCase):
    def test_actual_fixed_truth_and_information_equalized_d(self):
        for h in (0.,.01):
            a,ra=train(84200,0.,h);b,rb=train(84200,.5,h)
            self.assertEqual(len({r['truth'] for r in ra}),1)
            self.assertEqual(a.L,b.L)
            self.assertEqual([r['private'] for r in ra],[r['private'] for r in rb])
            self.assertAlmostEqual(a.credit,100+sum(r['material_receipt']-r['practice_cost'] for r in ra))
    def test_adult_zero_override_knowledge_fixed_and_true_twenty_steps(self):
        a,_=train(84200,.5,.01)
        for arm in ARMS:
            rows=adult(84200,.5,.01,a,arm,True)
            self.assertEqual([r['step'] for r in rows],list(range(20)))
            self.assertTrue(all(r['adult_inherited_override']==0 and r['K']==sorted(a.K) for r in rows))
    def test_matched_information_and_actual_price_audience_treatments(self):
        a,_=train(84200,.5,.01)
        base=adult(84200,.5,.01,a,'baseline',True);free=adult(84200,.5,.01,a,'free_audit',True)
        self.assertEqual([r['audit'] for r in base],[r['audit'] for r in free])
        self.assertTrue(all(r['audit_cost']==0 for r in free))
        removed=adult(84200,.5,.01,a,'audience_removal',True)
        self.assertTrue(all(r['psychological_approval']==0 for r in removed))
if __name__=='__main__':unittest.main()
