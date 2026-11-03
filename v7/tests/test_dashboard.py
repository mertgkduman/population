"""Contract checks for the corrected-only offline research dashboard."""
from pathlib import Path
import gzip, json, unittest

ROOT=Path(__file__).resolve().parents[1]

class DashboardContractTests(unittest.TestCase):
    def test_replay_cache_has_observed_cells_and_parity(self):
        with gzip.open(ROOT/'experiments/output/corrected/dashboard_replays.json.gz','rt') as f: d=json.load(f)
        self.assertEqual(len(d['cells']),81)
        self.assertTrue(d['parity']['all_digest_and_summary_match'])
        self.assertIn('unobserved_vs_observed_focal_digest',d['parity'])
        self.assertTrue(all(x['observed']['focal'] and x['observed']['focal']['agent_has_evaluator_truth'] is False for x in d['cells']))
        self.assertTrue(any(x['observed']['edges'] for x in d['cells']))
    def test_builder_fails_closed_on_canonical_contract(self):
        source=(ROOT/'build_dashboard.py').read_text()
        self.assertIn('FAIL CLOSED: 81 digest-checked passive replays required',source)
        self.assertIn('all_digest_and_summary_match',source)
        self.assertIn('FAIL CLOSED: canonical registry SHA mismatch',source)
        self.assertIn('FAIL CLOSED: dashboard input hash/byte mismatch',source)
        self.assertIn("final_controls.json",source)
    def test_page_is_inline_and_corrected_only(self):
        page=(ROOT/'research_dashboard.html').read_text()
        self.assertNotIn('<script src=',page)
        self.assertIn('plotly.js v4.1.1',page)
        self.assertIn('corrected_overlay',page)
        self.assertIn('Adult belief/action control',page)
        self.assertIn('Execution-priced planner control',page)
        self.assertIn('Carrier-retention intervention',page)
        self.assertIn('P(actual truth)',page)
        self.assertIn('DecompressionStream',page)
        self.assertLess(len(page.encode()),8_000_000)

if __name__=='__main__': unittest.main()
