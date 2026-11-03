import unittest
from v7.experiments.recovery_culture_v3 import run_cell

class ResourceCultureV3Tests(unittest.TestCase):
    def test_finite_resource_accounting_and_blank_births(self):
        row=run_cell(82301,"transmission_innovation")
        self.assertLessEqual(row["max_residual"],1e-7)
        self.assertEqual(row["lifetime_work_bound"],72)
        self.assertGreaterEqual(row["minimum_private_discovery_work"],48)
    def test_storage_off_and_carrier_loss(self):
        row=run_cell(82301,"carrier_loss_storage_off",no_innovation_after_loss=True)
        self.assertEqual(row["storage_items"],0)
        self.assertIsNotNone(row["post_loss_knowledge"])
