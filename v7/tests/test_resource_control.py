import unittest
from dataclasses import replace
from v7.experiments.resource_control import Settings,run,pair

class PhysicalControlTests(unittest.TestCase):
    def test_closed_stocks_population_and_person_time(self):
        for arm in ['transmission_innovation','no_transmission','prerequisite_scramble','carrier_loss_storage_off','carrier_loss_storage_on']:
            world=run(82600,arm)
            self.assertLess(world.result()['max_residual'],1e-7)
            self.assertLessEqual(world.result()['max_person_work'],4)
            prior=10
            for row in world.history:
                self.assertEqual(row['N'],prior+row['births']-row['deaths']-row['removals'])
                self.assertEqual(row['N'],row['F']+row['A']);prior=row['N']
    def test_paid_birth_snapshot_blankness_and_operational_cap(self):
        cfg=replace(Settings(),horizon=1,maturity=1,birth_probability=1.)
        world=run(82600,'no_transmission',cfg)
        children=[p for p in world.people.values() if p.parent]
        self.assertEqual(len(children),10)
        self.assertTrue(all(p.age==0 and not p.recipe and not p.roots and not p.progress for p in children))
        capped=run(82600,'no_transmission',replace(cfg,population_cap=10))
        self.assertEqual(capped.status,'cap_censored')
        self.assertEqual(len(capped.people),10)
    def test_matched_work_and_independent_objects(self):
        a,b=pair(82500)
        self.assertIsNot(a.people,b.people)
        self.assertEqual(len(a.history),len(b.history))
        for x,y in zip(a.history,b.history):
            self.assertEqual(x['offered'],y['offered'])
            self.assertEqual(x['realized'],x['offered'])
            self.assertEqual(y['realized'],y['offered'])
    def test_no_carrier_no_storage_no_innovation_retains_no_recipe(self):
        world=run(82600,'carrier_loss_storage_off',no_innovation=True)
        if world.post_loss is not None:self.assertEqual(world.post_loss,0)
        self.assertFalse(world.storage)
        self.assertTrue(all(not p.recipe for p in world.people.values()))

if __name__=='__main__':unittest.main()
