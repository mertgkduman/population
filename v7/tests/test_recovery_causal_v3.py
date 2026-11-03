import unittest
from v7.experiments.recovery_causal_v3 import adult_updates,training
class R3(unittest.TestCase):
 def test_training_is_acquired_and_adult_k_is_fixed(self):
  state,trace=training(84101,'dhalf');self.assertEqual(len(trace),40);self.assertTrue(all(x['K'] in (0.,1.) for x in trace));self.assertGreater(sum(x['private_signal']==x['truth'] for x in trace),20);rows=adult_updates(84101,'dhalf',state,'free_audit',1);self.assertEqual(len(rows),20);self.assertEqual(len({r['K_acquired_procedure'] for r in rows}),1);self.assertTrue(all(r['free_audit'] for r in rows))
 def test_adult_uses_passed_acquired_state(self):
  state={'B':.5,'K':1.,'H':0.,'T':.5,'material':3.,'history_digest':'explicit-history'}
  row=adult_updates(1,'d0',state,'audience_removal',1)[0]
  self.assertEqual(row['cloned_training_history'],'explicit-history');self.assertEqual(row['B_prior'],.5);self.assertEqual(row['K_acquired_procedure'],1.);self.assertEqual(row['T_source_trust'],.5)
