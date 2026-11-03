"""Contract tests for evidence-preserving synthesis and exports."""
import importlib
import math
import unittest


class ReportingContractTests(unittest.TestCase):
    def _api(self):
        try:
            # Reporting API lives outside the immutable frozen core.
            return importlib.import_module("v7.synthesize_results")
        except ModuleNotFoundError as error:
            self.fail(f"Slice 3B reporting implementation is absent: {error}")

    def test_extinct_and_cap_censored_runs_remain_in_unconditional_denominators(self):
        """No survivor-only report may silently erase extinction or cap censoring."""
        summary = self._api().build_summary([
            {"run_id": "alive", "terminal": "complete", "descendants": 2},
            {"run_id": "extinct", "terminal": "extinct", "descendants": 0},
            {"run_id": "capped", "terminal": "cap_censored", "descendants": 0,
             "no_birth_censored": True},
        ])
        self.assertEqual(summary["unconditional_denominator"], 3)
        self.assertEqual(summary["extinction_count"], 1)
        self.assertEqual(summary["cap_censored_count"], 1)
        self.assertEqual(summary["no_birth_count"], 1)

    def test_claim_requires_evidence_pointer_and_finite_selection_claim_limit(self):
        """Finite establishment cannot be exported as asymptotic invasion or ESS."""
        record = {"claim": "finite descendant expansion", "evidence": "run_manifest.json", "claim_limit": "not asymptotic invasion or ESS"}
        api = self._api()
        self.assertTrue(api.validate_result_record(record))
        with self.assertRaises(ValueError):
            api.validate_result_record({"claim": "ESS", "evidence": "finite-lineage.csv"})

    def test_untraceable_and_nonfinite_records_are_rejected(self):
        api = self._api()
        with self.assertRaises(ValueError):
            api.validate_result_record({"claim": "number without source"})
        with self.assertRaises(ValueError):
            api.validate_result_record({"claim": "finite", "evidence": "raw.csv", "estimate": math.inf})

    def test_intermediate_generator_classifier_keeps_ties_and_boundaries(self):
        api = self._api()
        result = api.classify_intermediate_generator([
            {"d_local": 0.0, "d_procedure": 0.0, "value": 0.9},
            {"d_local": 0.5, "d_procedure": 0.5, "value": 1.0},
            {"d_local": 1.0, "d_procedure": 1.0, "value": 1.0},
        ])
        self.assertEqual(result["classification"], "intermediate-compatible")
        self.assertEqual(len(result["compatible_points"]), 2)

    def test_actual_exports_recompute_corrected_denominators_and_main_range(self):
        summary = self._api().build_evidence_summary()
        self.assertEqual(summary["primary_evidence"], "corrected_overlay")
        self.assertEqual(summary["frozen_inventory"]["holdout"]["rows"], 1368)
        self.assertEqual(
            summary["frozen_inventory"]["holdout"]["sha256"],
            "d46e4ebb6e9dc377e83c04f438452d723dac9eaa198828fb0723d9946bdf87bb",
        )
        self.assertEqual(
            summary["corrected_inventory"]["holdout"]["sha256"],
            "5956bde27a901f99f6520d3c5d227a6da1069fa3f86d586785ae6f46b383e5e0",
        )
        selected = [x for x in summary["holdout"]["contrasts"] if x["policy"] == "vector_0_5_0"]
        self.assertEqual(len(selected), 9)
        self.assertLessEqual(min(x["mean_delta"] for x in selected), -0.0009)
        self.assertGreaterEqual(max(x["mean_delta"] for x in selected), 0.0014)
        self.assertLess(min(x["population_mean_delta"] for x in selected), 0.0)
        self.assertGreater(max(x["population_mean_delta"] for x in selected), 0.0)
        for contrast in summary["holdout"]["contrasts"]:
            for field in ("mean_delta", "paired_mcse", "population_mean_delta",
                          "population_paired_mcse", "birth_flux_mean_delta",
                          "birth_flux_paired_mcse", "death_flux_mean_delta",
                          "death_flux_paired_mcse"):
                self.assertTrue(math.isfinite(contrast[field]), (contrast, field))
        self.assertEqual(summary["tiny_exact"]["restricted_replicates"], 4000)
        self.assertGreater(summary["tiny_exact"]["exact_enumerated_value"], summary["tiny_exact"]["restricted_monte_carlo_value"])
        self.assertGreater(summary["tiny_exact"]["restricted_monte_carlo_mcse"], 0.0)
        self.assertEqual(summary["selection"]["registered_raw_rows"], summary["corrected_inventory"]["evolution"]["rows"])
        self.assertEqual(summary["selection"]["completed_batch_rows"] % 192, 0)
        self.assertEqual(len(summary["selection"]["contrasts"]), 12)
        self.assertEqual(
            summary["selection"]["paid_birth_rows"] + summary["selection"]["no_birth_censored"],
            summary["selection"]["registered_raw_rows"],
        )
        precision_met = (
            summary["selection"]["maximum_paired_descendant_mcse"] <= 0.25
            and summary["selection"]["maximum_establishment_wilson_half_width"] <= 0.10
        )
        self.assertEqual(summary["selection"]["runner_status"] == "complete", precision_met)
        self.assertEqual(summary["holdout"]["extinction_count"], 0)
        self.assertEqual(summary["holdout"]["cap_censored_count"], 0)
        self.assertEqual(summary["data_quality"]["status"], "passed")
        defect = summary["frozen_local_no_teacher_defect"]
        self.assertEqual(defect["status"], "CONFIRMED_FROZEN_DEFECT")
        self.assertEqual(defect["chosen_action"], "teacher")
        self.assertTrue(defect["phantom_tutor_equals_hidden_state"])
        self.assertNotEqual(defect["private_signal"], defect["latent_local_state_z"])

    @unittest.expectedFailure
    def test_desired_frozen_no_teacher_local_path_has_no_teacher_action_or_hidden_oracle(self):
        """Expected failure retains the required behavior for a future corrected variant."""
        defect = self._api().frozen_local_no_teacher_audit()
        self.assertNotIn("teacher", defect["feasible_actions"])
        self.assertNotEqual(defect["phantom_tutor_signal"], defect["latent_local_state_z"])

    def test_versioned_correction_removes_teacher_action_and_executes_private_cue(self):
        repaired = self._api().corrected_local_no_teacher_audit()
        self.assertEqual(repaired["status"], "CORRECTED_PATH_VALIDATED")
        self.assertEqual(repaired["feasible_actions"], ["private"])
        self.assertEqual(repaired["chosen_action"], "private")
        self.assertTrue(repaired["placeholder_equals_private"])
        self.assertTrue(repaired["executed_success_matches_private_cue"])

    def test_every_predeclared_check_has_scientific_status_and_traceable_basis(self):
        api = self._api()
        inventory = api.artifact_inventory()
        corrected = api.corrected_artifact_inventory()
        checks = api.executed_checks(inventory, corrected)
        self.assertEqual(len(checks), 25)
        self.assertEqual({x["scientific_status"] for x in checks}, {"passed", "partial", "not_run"})
        for check in checks:
            self.assertTrue(check["command"])
            self.assertTrue(check["basis"])
            self.assertTrue(check["evidence"])
            self.assertTrue(all(item["sha256"] for item in check["evidence"]))
            for item in check["evidence"]:
                self.assertEqual(api.sha256(api.ROOT / item["path"]), item["sha256"])

    def test_corrected_discovery_reports_all_primary_mean_population_contrasts(self):
        summary = self._api().build_evidence_summary()
        contrasts = summary["discovery"]["primary_mean_population_contrasts"]
        self.assertEqual(len(contrasts), 27)
        self.assertEqual(
            {item["contrast"] for item in contrasts},
            {"procedure_only", "local_only", "scalar_diagonal"},
        )
        self.assertTrue(all(item["n_pairs"] == 4 for item in contrasts))
        self.assertEqual(len(summary["discovery"]["class_specific_grid"]), 27)

    def test_postreview_hypothesis_numbering_is_canonical_and_claim_limited(self):
        hypotheses = {item["id"]: item for item in self._api().hypothesis_ledger()}
        self.assertIn("METAREASONING EQUIVALENCE", hypotheses["H7"]["status"])
        self.assertIn("PROVENANCE-SATURATION", hypotheses["H8"]["status"])
        self.assertIn("carrier death", hypotheses["H9"]["finding"])
        self.assertIn("root diversity", hypotheses["H9"]["finding"])

    def test_reported_population_and_stock_estimands_match_frozen_source(self):
        api = self._api()
        source = (api.V7 / "experiments" / "model.py").read_text()
        self.assertIn("sum(report.population_next for report in self.reports) / max(1, len(self.reports))", source)
        self.assertIn("self.initial_total_stock", source)
        self.assertIn("sum(report.population_next for report in self.reports)", source)
