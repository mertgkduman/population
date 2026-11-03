"""Red contract tests for immutable-core post-freeze persistence assays."""
import importlib
import unittest


class PostFreezeContractTests(unittest.TestCase):
    def _api(self):
        try:
            return importlib.import_module("v7.experiments.postfreeze")
        except ModuleNotFoundError as error:
            self.fail(f"Slice 3A post-freeze implementation is absent: {error}")

    def test_frozen_core_bytes_and_fixed_replay_are_identical(self):
        """Core source and replay must verify before an extension result is admissible."""
        api = self._api()
        manifest = api.FreezeManifest.contract_fixture()
        result = api.verify_frozen_core(manifest)
        self.assertTrue(result.source_bytes_identical)
        self.assertTrue(result.fixed_replay_digest_identical)

    def test_adult_persistence_has_zero_direct_override_but_retains_learned_history(self):
        """Adult persistence is learned H/obligation, never a direct d effect."""
        assay = self._api().PersistenceAssay.contract_fixture()
        state = assay.after_training()
        probe = assay.remove_audience_and_probe(state)
        self.assertEqual(probe.direct_override_probability, 0.0)
        self.assertFalse(probe.audience_present)
        self.assertFalse(probe.tutor_present)
        self.assertNotEqual(probe.habit_state_digest, "")

    def test_counterevidence_revision_is_not_aliased_with_habit_persistence(self):
        """NORM-01: belief revision and action persistence are separately observable."""
        probe = self._api().PersistenceAssay.contract_fixture().matched_counterevidence_probe()
        self.assertNotEqual(probe.posterior_revision, probe.action_persistence)

    def test_yoked_adult_d_coordinates_share_history_and_cannot_override(self):
        """Post-tau 3x3 probes hold observed history/evidence fixed across d."""
        rows = self._api().yoked_decision_records(74001)
        self.assertEqual(len(rows), 27)
        for depth in (1, 3, 6):
            for context in (.5, .75, 1.0):
                group = [row for row in rows if row["depth"] == depth and row["context_concordance"] == context]
                self.assertEqual(len({row["same_history_id"] for row in group}), 1)
                self.assertTrue(all(not row["direct_adult_override"] for row in group))

    def test_training_has_no_material_obedience_bonus(self):
        """Approval is reinforcement; all modelled transfers debit and credit equally."""
        state = self._api().PersistenceAssay(74004).after_training()
        self.assertEqual(state.paid_material_net, 0.0)
        self.assertGreater(state.approval_events, 0)

    def test_executed_probe_rows_export_separated_acquired_state_and_evidence(self):
        """A real seed run, rather than a constructor fixture, exports all five probes."""
        rows = self._api().records_for_seed(74001)
        self.assertEqual({row["probe"] for row in rows}, {
            "audience_removal", "bidirectional_equalized_counterevidence", "free_audit",
            "outcome_devaluation", "contingency_degradation",
        })
        for row in rows:
            self.assertFalse(row["direct_override_probability"])
            self.assertGreater(row["B_factual_posterior"], 0.0)
            self.assertGreater(row["H_learned_action_value"], 0.0)
            self.assertEqual(row["evidence_count"], 2)
            self.assertEqual(row["adult_error_count"], 0)
