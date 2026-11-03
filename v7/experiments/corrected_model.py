"""Versioned overlay fixing only the frozen no-teacher local oracle.

The frozen V7 core remains byte-identical.  This subclass changes exactly the
three methods whose teacher=None path could expose hidden local state through a
phantom ``teacher`` action; all teacher-present behavior delegates to the base.
"""
from __future__ import annotations

from v7.experiments.model import EcologyRun, Individual, PolicyObservation


class CorrectedEcologyRun(EcologyRun):
    """EcologyRun with private-only local behavior when no teacher exists."""

    # .8 * 3 - .2 * 2 = 2.0; spell the evaluated value to keep serialized
    # registrations stable across floating-point representations.
    LOCAL_PRIVATE_EXPECTED_VALUE = 2.0

    def _local_state(self, person: Individual, family: str, teacher: Individual | None) -> tuple[int, int, int]:
        z, private, tutor = super()._local_state(person, family, teacher)
        # The base only reaches the phantom path when teacher is absent.  Preserve
        # all actual-teacher context behavior byte-for-byte through super().
        return (z, private, private) if teacher is None else (z, private, tutor)

    def _local_observation(self, person: Individual, family: str, teacher: Individual | None) -> tuple[PolicyObservation, tuple[int, int, int]]:
        observation, context = super()._local_observation(person, family, teacher)
        if teacher is not None:
            return observation, context
        # There is no advice channel to arbitrate.  Expose only an actual private
        # action and its .8*3-.2*2 expected value; never leave a tie for a phantom
        # teacher action to win lexicographically.
        return PolicyObservation(**{**observation.__dict__,
                                    "feasible_actions": ("private",),
                                    "action_values": (("private", self.LOCAL_PRIVATE_EXPECTED_VALUE),),
                                    "advice": None,
                                    "messages": (), "provenance_roots": (),
                                    "source_id": None, "source_history": ()}), context

    def _local_attempt(self, person: Individual, family: str, choice: str,
                       context: tuple[int, int, int], teacher: Individual | None) -> float:
        if teacher is None:
            # Route physical execution through the sampled private cue, not the
            # base helper's absent-tutor channel.  The third context component is
            # already private under _local_state, but this explicit force makes the
            # no-oracle invariant robust to callers that pass "teacher".
            choice = "private"
            context = (context[0], context[1], context[1])
        return super()._local_attempt(person, family, choice, context, teacher)
