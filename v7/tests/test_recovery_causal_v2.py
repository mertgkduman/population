import unittest
from v7.experiments.recovery_causal_v2 import adult_arm
class R2V2Tests(unittest.TestCase):
 def test_cloned_arms_are_twenty_steps_and_separate(self):
  rows=adult_arm(83101,'free_audit',1)
  self.assertEqual([r['step'] for r in rows],list(range(1,21)))
  self.assertTrue(all(r['free_audit'] and not r['direct_adult_inherited_override'] for r in rows))
  self.assertNotEqual(adult_arm(83101,'baseline',1)[0]['free_audit'],rows[0]['free_audit'])
