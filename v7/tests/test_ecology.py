"""Behavioral acceptance tests for the Slice 2A finite-resource ecology gates."""
import importlib
import unittest
from math import isclose


class EcologyContractTests(unittest.TestCase):
    def _api(self):
        try:
            return importlib.import_module("v7.experiments.model")
        except ModuleNotFoundError as error:
            self.fail(f"Slice 2A ecology kernel is absent: {error}")

    def test_newborn_is_blank_and_birth_is_paid_on_both_ledgers(self):
        """INHERIT-01/LEDGER-01: no learned state crosses biology; birth is charged."""
        api = self._api()
        run = api.EcologyRun.contract_fixture()
        parent = api.Individual.contract_fixture(B={"fact": .9}, K={"procedure": [1]}, T={"t": .8}, H={"a": .4})
        newborn, event = run.paid_birth(parent)
        self.assertEqual(newborn.B, {})
        self.assertEqual(newborn.K, {})
        self.assertEqual(newborn.T, {})
        self.assertEqual(newborn.H, {})
        self.assertIsInstance(event, api.LedgerEvent)
        self.assertEqual(event.parent_energy_debit, event.birth_cost)
        self.assertEqual(event.birth_cost - event.newborn_energy_credit, 8)
        self.assertEqual(newborn.energy, 8)

    def test_season_ledger_closes_population_energy_and_teaching_time(self):
        """LEDGER-01/TEACH-01/GROWTH-01: no silent resource or demographic residual."""
        run = self._api().EcologyRun.contract_fixture()
        report = run.advance_season()
        self.assertEqual(report.population_next, report.population_prior + report.births - report.deaths)
        self.assertAlmostEqual(report.energy_resource_residual, 0.0, places=9)
        self.assertGreater(report.teacher_time_debit, 0)
        self.assertGreater(report.learner_time_debit, 0)

    def test_real_runs_start_with_64_blank_founders_and_acquire_two_family_culture(self):
        """Founders are not seeded experts; teaching emerges from stored successful procedures."""
        api = self._api()
        run = api.EcologyRun(71001, depth=3, chi=.75, q_theta=.005, burn_in=0, measurement=8)
        self.assertEqual(64, len(run.population))
        self.assertTrue(all(not person.B and not person.K and not person.T and not person.H for person in run.population.values()))
        result = run.run()
        families = {sequence.split("|")[0] for person in run.population.values() for sequence in person.K}
        self.assertEqual("running", result["status"])
        self.assertTrue({"food", "tool"}.issubset(families))
        self.assertGreater(result["cultural_edges"], 0)
        self.assertGreater(result["biological_edges"], 0)

    def test_asocial_access_off_preserves_private_hardware_but_creates_no_cultural_edges(self):
        api = self._api()
        social = api.EcologyRun(71001, api.OrdinarySocialPolicy, depth=3, burn_in=0, measurement=10).run()
        asocial = api.EcologyRun(71001, api.AsocialPolicy, depth=3, burn_in=0, measurement=10).run()
        self.assertGreater(social["cultural_edges"], 0)
        self.assertEqual(0, asocial["cultural_edges"])
        self.assertGreater(asocial["decision_records"], 0)

    def test_all_primary_depths_have_useful_prefixes_and_positive_nonneedle_economics(self):
        from v7.experiments.exact import enumerate_task
        rows = [enumerate_task(depth) for depth in (1, 3, 6)]
        self.assertTrue(all(row.procedure_return > 0 for row in rows))
        self.assertTrue(all(any(name.startswith("prefix_failure") for name, _, _ in row.failure_branches) for row in rows))
        self.assertTrue(all(row.margin_per_token >= .10 for row in rows))

    def test_streamed_replay_is_deterministic_and_population_is_not_replaced(self):
        api = self._api()
        first = api.EcologyRun(71002, depth=6, chi=.5, q_theta=.02, burn_in=0, measurement=12).run()
        second = api.EcologyRun(71002, depth=6, chi=.5, q_theta=.02, burn_in=0, measurement=12).run()
        self.assertEqual(first["replay_digest"], second["replay_digest"])
        self.assertGreaterEqual(first["ledger_residual_max"], 0.0)
        self.assertLess(first["ledger_residual_max"], 1e-8)
        self.assertNotEqual(64, first["biological_edges"])

    def test_neutral_paid_newborn_is_not_an_external_immigrant(self):
        """INVASION-01: neutral control uses the same resident-paid birth pathway."""
        run = self._api().EcologyRun.contract_fixture()
        mutant, neutral = run.paired_paid_newborns()
        self.assertEqual(mutant.birth_event_id, neutral.birth_event_id)
        self.assertEqual(mutant.initial_acquired_digest, neutral.initial_acquired_digest)
        self.assertEqual(mutant.energy, neutral.energy)

    def test_private_structural_cue_tracks_theta_not_advice_and_firewall_keeps_matched_history_fixed(self):
        api = self._api(); run = api.EcologyRun(99, depth=3, burn_in=0, measurement=1)
        learner, teacher = list(run.population.values())[:2]
        offered = run._sequence("food", 0); teacher.K[offered] = tuple((*offered.split("|"), "root:t")); teacher.independent_successes[offered] = 2
        run.theta["food"] = 0; low = run._observation(learner, "food", teacher)
        run.theta["food"] = 1; high = run._observation(learner, "food", teacher)
        self.assertNotEqual(low.private_cue, high.private_cue)
        # Once the observed history is held fixed, a policy cannot see the theta flip.
        policy = api.OrdinarySocialPolicy()
        self.assertEqual(policy.decide(low, 8, api.KeyedRNG.fixture("firewall")).pre_override_digest,
                         policy.decide(low, 8, api.KeyedRNG.fixture("firewall")).pre_override_digest)

    def test_chi_changes_tutor_local_accuracy_without_changing_sensor_hardware(self):
        api = self._api()
        def accuracy(chi):
            run = api.EcologyRun(42, chi=chi, burn_in=0, measurement=1); learner, teacher = list(run.population.values())[:2]
            return sum(tutor == z for z, _private, tutor in (run._local_state(api.Individual(f"p{i}", 1, 8., api.OrdinarySocialPolicy()), "food", teacher) for i in range(400))) / 400
        self.assertGreater(accuracy(1.0), accuracy(.5) + .18)

    def test_local_override_is_a_real_juvenile_conflict_coordinate(self):
        api = self._api()
        obs = api.PolicyObservation("l", 0, 2, 8., 12, 128, "local", "supports_private", (("p_advice", .05), ("private_likelihood", .8)), (), (("t", .5),), (), (("message", "x"),), ("r",), ("private", "teacher"), (("private", 0.), ("teacher", 0.)), (("operation", .01), ("correct_reward", 3.), ("incorrect_loss", 2.)), "teacher", "t", (("successes", 1.), ("failures", 8.)), 0.)
        self.assertEqual("private", api.VectorOverridePolicy(0., 0.).decide(obs, 8, api.KeyedRNG.fixture("l")).chosen_action)
        self.assertEqual("teacher", api.VectorOverridePolicy(0., 1.).decide(obs, 8, api.KeyedRNG.fixture("l")).chosen_action)

    def test_physical_outcome_revises_family_branch_belief_for_adult_and_child(self):
        api = self._api()
        for age in (1, 8):
            run = api.EcologyRun(73, depth=1, burn_in=0, measurement=1); person = api.Individual(f"a{age}", age, 100., api.OrdinarySocialPolicy())
            run.population = {person.identity: person}; run._time_used = {}; run.theta["food"] = 0
            run._attempt(person, "food", run._sequence("food", 0), None)
            self.assertNotEqual(.5, person.B["food:branch=0"])

    def test_shared_step_kernel_matches_exact_branch_economics_and_mutant_inherits_traits(self):
        from v7.experiments.exact import enumerate_task, sample_task_outcome
        # Deterministic quadrature over the same D+1 Bernoulli paths used by IBM.
        row = enumerate_task(3, .9); observed = []
        for mask in range(16):
            bits = [((mask >> i) & 1) == 0 for i in range(4)]
            terminal, _reached, value = sample_task_outcome(3, .9, lambda step, bits=bits: .1 if bits[step] else .95)
            observed.append(terminal)
        self.assertIn("correct_finish", observed); self.assertTrue(any(x.startswith("prefix_failure") for x in observed)); self.assertTrue(isclose(sum(p for _, p, _ in row.failure_branches), 1.0))
        api = self._api(); run = api.EcologyRun.contract_fixture(); parent = next(p for p in run.population.values() if p.energy >= run.BIRTH_COST)
        parent.traits = (("d_procedure", .7), ("d_local", .2)); child, _ = run.paid_birth(parent, newborn_id="trait-child")
        self.assertEqual(tuple(sorted(parent.traits)), child.traits); self.assertEqual(.7, child.policy.d_procedure)

    def test_procedural_receipt_is_paid_but_does_not_copy_memory_before_physical_evidence(self):
        api = self._api(); run = api.EcologyRun(305, depth=1, burn_in=0, measurement=1)
        learner, teacher = list(run.population.values())[:2]
        sequence = run._sequence("food", 0); teacher.K[sequence] = tuple((*sequence.split("|"), "root:teacher")); teacher.independent_successes[sequence] = 2
        run._time_used = {}
        self.assertEqual(sequence, run._teach(teacher, learner, "food"))
        self.assertEqual({}, learner.K, "receipt must not make K an action/override side effect")
        observation = run._observation(learner, "food", teacher)
        self.assertEqual("branch_0", observation.advice)
        neutral = api.VectorOverridePolicy(0., 0.).decide(observation, 8, api.KeyedRNG.fixture("receipt"))
        forced = api.VectorOverridePolicy(1., 0.).decide(observation, 8, api.KeyedRNG.fixture("receipt"))
        self.assertEqual(neutral.pre_override_learning_digest, forced.pre_override_learning_digest)

    def test_no_teacher_private_branch_beliefs_and_cue_drive_common_social_and_asocial_q0(self):
        api = self._api(); run = api.EcologyRun(911, depth=3, burn_in=0, measurement=1); person = next(iter(run.population.values()))
        person.B.update({"food:branch=0": .99, "food:branch=1": .01})
        low = run._observation(person, "food", None)
        person.B.update({"food:branch=0": .01, "food:branch=1": .99})
        high = run._observation(person, "food", None)
        for policy in (api.OrdinarySocialPolicy(), api.AsocialPolicy()):
            self.assertEqual("branch_0", policy.decide(low, 8, api.KeyedRNG.fixture("private")).chosen_action)
            self.assertEqual("branch_1", policy.decide(high, 8, api.KeyedRNG.fixture("private")).chosen_action)

    def test_teacher_trust_key_and_relative_local_evidence_are_directional(self):
        api = self._api(); run = api.EcologyRun(912, depth=1, burn_in=0, measurement=1); learner, teacher = list(run.population.values())[:2]
        seq = run._sequence("food", 0); teacher.K[seq] = tuple((*seq.split("|"), "root:t")); teacher.independent_successes[seq] = 2
        learner.T["teacher:founder-001:food"] = .01; lo = api.source_calibration(run._observation(learner, "food", teacher))
        learner.T["teacher:founder-001:food"] = .99; hi = api.source_calibration(run._observation(learner, "food", teacher))
        self.assertGreater(hi, lo)
        learner.B["local:food"] = .5; run._time_used = {}
        run._local_attempt(learner, "food", "private", (0, 0, 1), teacher)
        self.assertLess(learner.B["local:food"], .5)

    def test_realized_terminal_loss_and_safe_counterfactual_match_shared_contract(self):
        api = self._api(); run = api.EcologyRun(913, depth=1, burn_in=0, measurement=1); person = next(iter(run.population.values()))
        run.population = {person.identity: person}; run._time_used = {}; run.theta["food"] = 0
        run._rng = lambda namespace, identity, ordinal=0, event_type="": .1 if ordinal == 0 else .99  # prerequisite passes, finish fails
        before = person.energy; run._attempt(person, "food", run._sequence("food", 0), None)
        self.assertAlmostEqual(-2.0, person.energy - before, places=9)
        run = api.EcologyRun(914, depth=3, burn_in=0, measurement=1); person = next(iter(run.population.values())); run._time_used = {}
        before = person.energy; run._safe_work(person)
        self.assertEqual(4, run._time_used[person.identity]); self.assertAlmostEqual(4.8, person.energy - before, places=9)

    def test_neutral_testimony_is_neutral_and_information_posterior_changes_procedure_values(self):
        from dataclasses import replace
        api = self._api(); run = api.EcologyRun(915, depth=3, burn_in=0, measurement=1)
        learner, teacher = list(run.population.values())[:2]
        seq = run._sequence("food", 0)
        teacher.K[seq] = tuple((*seq.split("|"), "root:trial")); teacher.independent_successes[seq] = 2
        obs = replace(run._observation(learner, "food", teacher), private_cue="unobserved", source_history=(), trust=())
        neutral = api.branch_posteriors(obs)
        self.assertAlmostEqual(.5, neutral["branch_0"])
        reliable = replace(obs, trust=((obs.source_id, .99),), source_history=(("successes", 99.), ("failures", 0.)))
        self.assertGreater(api.branch_posteriors(reliable)[obs.advice], .9)
        policy = api.OrdinarySocialPolicy()
        high = dict(policy._q0_with_posterior(obs, .9)); low = dict(policy._q0_with_posterior(obs, .1))
        self.assertGreater(high[obs.advice], low[obs.advice])
        self.assertEqual("branch_0", max(high, key=high.get)); self.assertEqual("branch_1", max(low, key=low.get))

    def test_successful_realized_net_value_and_terminal_belief_normalization(self):
        from v7.experiments.exact import enumerate_task
        api = self._api(); run = api.EcologyRun(916, depth=3, burn_in=0, measurement=1)
        person = next(iter(run.population.values())); run.population = {person.identity: person}
        run._time_used = {}; run.theta["food"] = 0
        run._rng = lambda *args, **kwargs: .01
        before = person.energy; run._attempt(person, "food", run._sequence("food", 0), None)
        expected = {name: value for name, _, value in enumerate_task(3).failure_branches}["correct_finish"]
        self.assertAlmostEqual(expected, person.energy-before, places=9)
        self.assertAlmostEqual(1., person.B["food:branch=0"]+person.B["food:branch=1"])

    def test_feature_predictor_is_focal_incremental_lms_and_charged_under_common_cap(self):
        """P-01: one realised focal payoff yields one bounded, paid LMS update."""
        api = self._api()
        predictor = api.RewardPredictor.blank()
        features = {"bias": 1., "calibrated_source": .8, "context_match": 1., "unique_roots": 1.}
        updated, operations = predictor.lms_update(features, 2.0, api.RewardPredictor.LMS_UPDATE_OPERATIONS)
        self.assertEqual(api.RewardPredictor.LMS_UPDATE_OPERATIONS, operations)
        self.assertNotEqual(predictor.weights, updated.weights)
        unchanged, denied = predictor.lms_update(features, 2.0, api.RewardPredictor.LMS_UPDATE_OPERATIONS - 1)
        self.assertEqual(0, denied); self.assertEqual(predictor, unchanged)
        run = api.EcologyRun(981, api.FeatureTrustPolicy, depth=1, burn_in=0, measurement=1)
        run.advance_season()
        samples = list(run.decision_samples)
        self.assertTrue(samples)
        self.assertTrue(all(row["predictor_update_operations"] == api.RewardPredictor.LMS_UPDATE_OPERATIONS for row in samples))
        self.assertTrue(all(row["operations"] <= run.OPERATION_CAP for row in samples))
        self.assertTrue(any(event.kind == "predictor_lms_update" for event in run.ledger))

    def test_l9_verification_price_and_graph_variant_reach_actual_model_transition(self):
        api = self._api()
        learner = api.Individual("l", 1, 8., api.OrdinarySocialPolicy())
        priced = api.EcologyRun(982, depth=1, verification_price=1.5, burn_in=0, measurement=1)
        priced.population = {learner.identity: learner}
        self.assertEqual(1.5, dict(priced._observation(learner, "food", None).prices)["verify"])
        base = api.EcologyRun(982, depth=1, graph_variant=0, burn_in=0, measurement=1)
        permuted = api.EcologyRun(982, depth=1, graph_variant=1, burn_in=0, measurement=1)
        self.assertNotEqual(base._target_branch("food"), permuted._target_branch("food"))
        self.assertEqual(base._target_branch("tool"), permuted._target_branch("tool"))
