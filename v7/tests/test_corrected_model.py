"""Regression coverage for the versioned no-teacher local overlay."""
from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from v7.experiments.corrected_model import CorrectedEcologyRun
from v7.experiments.model import AsocialPolicy, Individual, KeyedRNG, OrdinarySocialPolicy


def _run(seed: int, policy=OrdinarySocialPolicy) -> CorrectedEcologyRun:
    return CorrectedEcologyRun(seed, policy, depth=3, chi=.75, q_theta=.005,
                               burn_in=0, measurement=1, label="overlay-test")


def _person(run: CorrectedEcologyRun) -> Individual:
    return next(iter(run.population.values()))


def test_teacher_none_exposes_only_private_for_all_ages_and_policies() -> None:
    for age in (0, 4, 5, 37):
        for policy in (OrdinarySocialPolicy, AsocialPolicy):
            run = _run(88000 + age + (1 if policy is AsocialPolicy else 0), policy)
            person = _person(run); person.age = age
            observation, context = run._local_observation(person, "food", None)
            decision = person.policy.decide(observation, run.OPERATION_CAP, KeyedRNG(str(run.seed), f"D{run.depth}", run.season))
            assert observation.feasible_actions == ("private",)
            assert observation.advice is None
            assert dict(observation.action_values) == {"private": 2.0}
            assert decision.chosen_action == "private"
            assert context[2] == context[1]


def test_no_teacher_actual_attempt_uses_private_not_hidden_z() -> None:
    for seed in range(88100, 88200):
        run = _run(seed); person = _person(run)
        _observation, (z, private, tutor) = run._local_observation(person, "food", None)
        before = person.energy
        run._local_attempt(person, "food", "teacher", (z, private, tutor), None)
        delta = person.energy - before
        assert (delta > 0) == (private == z)


def test_private_cue_accuracy_is_empirical_not_hidden_oracle() -> None:
    trials = []
    for seed in range(88200, 88700):
        run = _run(seed); z, private, tutor = run._local_state(_person(run), "food", None)
        assert tutor == private
        trials.append(private == z)
    accuracy = sum(trials) / len(trials)
    assert .75 <= accuracy <= .85


def test_teacher_present_path_delegates_to_frozen_base() -> None:
    run = _run(88700)
    person = _person(run)
    teacher = next(candidate for candidate in run.population.values() if candidate.identity != person.identity)
    # Same keyed draws on fresh replicas make this an exact delegation check.
    corrected = _run(88700); base = _run(88700)
    corrected_person = _person(corrected); base_person = _person(base)
    corrected_teacher = next(candidate for candidate in corrected.population.values() if candidate.identity != corrected_person.identity)
    base_teacher = next(candidate for candidate in base.population.values() if candidate.identity != base_person.identity)
    assert corrected._local_state(corrected_person, "food", corrected_teacher) == super(CorrectedEcologyRun, base)._local_state(base_person, "food", base_teacher)


def test_no_teacher_resource_ledger_and_time_parity() -> None:
    run = _run(88701, AsocialPolicy)
    result = run.run()
    assert result["max_time_tokens_used"] <= run.TIME_TOKENS
    assert result["ledger_residual_max"] <= 1e-8


def test_frozen_base_bytes_and_overlay_source_are_identified() -> None:
    manifest = json.loads((ROOT / "evidence" / "core_freeze" / "manifest.json").read_text())
    for relative, expected in manifest["source_sha256"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected
    overlay = ROOT / "experiments" / "corrected_model.py"
    assert len(hashlib.sha256(overlay.read_bytes()).hexdigest()) == 64


class CorrectedNoTeacherTests(unittest.TestCase):
    """unittest discovery wrapper retains every regression assertion above."""
    def test_all_ages_private_only(self) -> None: test_teacher_none_exposes_only_private_for_all_ages_and_policies()
    def test_actual_attempt_no_hidden_z(self) -> None: test_no_teacher_actual_attempt_uses_private_not_hidden_z()
    def test_empirical_private_accuracy(self) -> None: test_private_cue_accuracy_is_empirical_not_hidden_oracle()
    def test_teacher_present_delegation(self) -> None: test_teacher_present_path_delegates_to_frozen_base()
    def test_resource_ledger_parity(self) -> None: test_no_teacher_resource_ledger_and_time_parity()
    def test_base_hashes_and_overlay_hash(self) -> None: test_frozen_base_bytes_and_overlay_source_are_identified()
