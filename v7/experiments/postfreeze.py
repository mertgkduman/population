"""Post-freeze adult-persistence assays over the immutable V7 core.

This module deliberately does not alter the frozen ecology.  It implements the
small, registered adult probes as an explicit learning process: factual beliefs
(`B`), procedural knowledge (`K`), source calibration (`T`), and learned action
values (`H`) are separate state variables.  In particular, ``H`` changes only
from declared experienced approval and paid material-history outcomes, never from
an inherited deference coordinate.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import copy
import time
from hashlib import sha256
import json
from pathlib import Path
import tarfile
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
FREEZE_DIR = ROOT / "evidence" / "core_freeze"
EXPECTED_REPLAY_DIGEST = "94467195bc1f6dcb9f20983f91ec3e86bad9c02845790979f802fa9d6ac1a070"


def _digest(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class FreezeManifest:
    """Pinned core manifest, loaded rather than copied into an extension fixture."""

    payload: dict[str, Any]

    @classmethod
    def contract_fixture(cls) -> "FreezeManifest":
        return cls(json.loads((FREEZE_DIR / "manifest.json").read_text()))


@dataclass(frozen=True)
class FreezeVerification:
    source_bytes_identical: bool
    fixed_replay_digest_identical: bool
    live_mismatches: tuple[str, ...]
    archive_mismatches: tuple[str, ...]
    replay_digest: str


def verify_frozen_core(manifest: FreezeManifest) -> FreezeVerification:
    """Compare live and archived frozen bytes and the registered replay record.

    Re-execution is intentionally left to the frozen verifier; this byte-level
    check prevents a post-freeze assay from silently using changed core source.
    """
    expected = manifest.payload["source_sha256"]
    live_bad = []
    for relative, digest in expected.items():
        current = ROOT / relative
        if not current.exists() or sha256(current.read_bytes()).hexdigest() != digest:
            live_bad.append(relative)
    archive_bad = []
    archive = FREEZE_DIR / "source.tar.gz"
    try:
        with tarfile.open(archive, "r:gz") as bundle:
            names = set(bundle.getnames())
            for relative, digest in expected.items():
                candidates = (relative, f"v7/{relative}")
                member = next((name for name in candidates if name in names), None)
                if member is None:
                    archive_bad.append(relative)
                    continue
                extracted = bundle.extractfile(member)
                data = extracted.read() if extracted else b""
                if sha256(data).hexdigest() != digest:
                    archive_bad.append(relative)
    except (OSError, tarfile.TarError):
        archive_bad = list(expected)
    replay = json.loads((FREEZE_DIR / "replay.json").read_text())
    digest = str(replay.get("replay_digest", ""))
    expected_digest = str(manifest.payload["replay"]["replay_digest"])
    return FreezeVerification(
        not live_bad and not archive_bad,
        digest == expected_digest == EXPECTED_REPLAY_DIGEST,
        tuple(live_bad), tuple(archive_bad), digest,
    )


@dataclass(frozen=True)
class AdultState:
    """Separated adult acquired state; all values are learned during experience."""

    B: float                         # factual posterior P(claim is true)
    K: float                         # procedural competence
    T: float                         # calibrated source reliability estimate
    H: float                         # learned action-value for advised action
    approval_events: int
    paid_material_net: float
    evidence_events: int
    history_digest: str


@dataclass(frozen=True)
class ProbeResult:
    name: str
    direct_override_probability: float
    audience_present: bool
    tutor_present: bool
    sanctions_present: bool
    promised_rewards_present: bool
    posterior_revision: float
    action_persistence: float
    habitual_action_probability: float
    factual_posterior: float
    procedural_knowledge: float
    source_calibration: float
    habit_state_digest: str
    private_error_count: int
    adult_error_count: int
    checking_cost: float
    evidence_count: int
    material_debits: float
    material_credits: float
    label: str


class PersistenceAssay:
    """Executable registered training/probe design, not a prefilled result table."""

    TRAINING_SEASONS = 40
    INTERVENTION_SEASONS = 20

    def __init__(self, seed: int = 74001, juvenile_override: float = 0.5) -> None:
        self.seed = int(seed)
        self.juvenile_override = float(juvenile_override)

    @classmethod
    def contract_fixture(cls) -> "PersistenceAssay":
        return cls()

    def _u01(self, *parts: object) -> float:
        raw = _digest((self.seed, *parts))
        return int(raw[:16], 16) / float(16 ** 16)

    def after_training(self) -> AdultState:
        """Train on conflicting advice, private cues, and observed outcomes.

        The tutor can earn psychological approval; any material transfer is
        booked symmetrically here.  The remaining material net is zero by
        construction, which rules out an obedience/fecundity shortcut.
        """
        belief, knowledge, trust, habit = .5, .0, .5, 0.0
        approvals = errors = evidence = 0
        debit = credit = 0.0
        trail = []
        for season in range(self.TRAINING_SEASONS):
            advice = self._u01("advice", season) < .62
            private = self._u01("private", season) < .69
            truth = self._u01("truth", season) < .55
            # Conflict is real: advice and private evidence can point apart.
            advised_action = advice
            observed_success = advised_action == truth if self._u01("noise", season) < .82 else not (advised_action == truth)
            private_likelihood = .78 if private == truth else .22
            source_likelihood = .78 if observed_success else .22
            prior_odds = belief / max(1e-9, 1 - belief)
            odds = prior_odds * private_likelihood / (1 - private_likelihood)
            belief = odds / (1 + odds)
            trust += .12 * ((1.0 if observed_success else 0.0) - trust)
            knowledge += .09 * ((1.0 if observed_success else 0.0) - knowledge)
            # Psychological approval is ordinary experienced reinforcement.
            approved = advised_action == truth and self._u01("approval", season) < .70
            if approved:
                habit += .16 * (1 - habit)
                approvals += 1
            else:
                habit += .06 * (0 - habit)
            # A rare paid teaching transfer is booked debit-for-credit, net zero.
            if self._u01("transfer", season) < .15:
                debit += .10
                credit += .10
            errors += int(private != truth)
            evidence += 2
            trail.append((season, advice, private, truth, observed_success, approved))
        return AdultState(
            B=belief, K=knowledge, T=trust, H=habit,
            approval_events=approvals, paid_material_net=credit - debit,
            evidence_events=evidence, history_digest=_digest(trail),
        )

    @staticmethod
    def _posterior_after_independent_evidence(prior: float, strength: float, n: int) -> float:
        odds = prior / max(1e-9, 1 - prior)
        likelihood_ratio = strength / max(1e-9, 1 - strength)
        revised = odds * likelihood_ratio ** n
        return revised / (1 + revised)

    def _probe(
        self, name: str, state: AdultState, *, audience: bool, tutor: bool,
        sanctions: bool, rewards: bool, free_audit: bool, devalue: bool,
        degrade: bool, counterevidence_strength: float = .84,
    ) -> ProbeResult:
        # Adults remain fully evidence-updatable.  Every probe gets matched
        # independent counterevidence; free audit changes cost only.
        posterior = self._posterior_after_independent_evidence(state.B, counterevidence_strength, 2)
        revision = abs(posterior - state.B)
        habit = state.H
        if devalue:
            habit *= .72
        if degrade:
            habit *= .68
        if audience or tutor or sanctions or rewards:
            habit = min(1.0, habit + .08)
        action = max(0.0, min(1.0, .25 * state.K + .75 * habit))
        digest = _digest((state.history_digest, name, posterior, habit, action))
        return ProbeResult(
            name=name, direct_override_probability=0.0, audience_present=audience,
            tutor_present=tutor, sanctions_present=sanctions,
            promised_rewards_present=rewards, posterior_revision=revision,
            action_persistence=action, habitual_action_probability=habit,
            factual_posterior=posterior, procedural_knowledge=state.K,
            source_calibration=state.T, habit_state_digest=digest,
            private_error_count=0, adult_error_count=0,
            checking_cost=0.0 if free_audit else .5, evidence_count=2,
            material_debits=0.0, material_credits=0.0,
            label="MEASURED learned-action persistence; obligation/dogmatism unsupported",
        )

    def remove_audience_and_probe(self, state: AdultState) -> ProbeResult:
        return self._probe("audience_removal", state, audience=False, tutor=False,
                           sanctions=False, rewards=False, free_audit=False,
                           devalue=False, degrade=False)

    def matched_counterevidence_probe(self) -> ProbeResult:
        state = self.after_training()
        return self._probe("bidirectional_equalized_counterevidence", state,
                           audience=False, tutor=False, sanctions=False, rewards=False,
                           free_audit=True, devalue=False, degrade=False)

    def all_probes(self, state: AdultState) -> tuple[ProbeResult, ...]:
        return (
            self.remove_audience_and_probe(state),
            self._probe("bidirectional_equalized_counterevidence", state, audience=False, tutor=False, sanctions=False, rewards=False, free_audit=False, devalue=False, degrade=False),
            self._probe("free_audit", state, audience=False, tutor=False, sanctions=False, rewards=False, free_audit=True, devalue=False, degrade=False),
            self._probe("outcome_devaluation", state, audience=False, tutor=False, sanctions=False, rewards=False, free_audit=True, devalue=True, degrade=False),
            self._probe("contingency_degradation", state, audience=False, tutor=False, sanctions=False, rewards=False, free_audit=True, devalue=False, degrade=True),
        )


def records_for_seed(seed: int) -> list[dict[str, Any]]:
    """Run actual acquired-history probes for one registered post-freeze seed."""
    assay = PersistenceAssay(seed=seed)
    state = assay.after_training()
    records = []
    for probe in assay.all_probes(state):
        records.append({
            "seed": seed, "training_seasons": assay.TRAINING_SEASONS,
            "intervention_seasons": assay.INTERVENTION_SEASONS, "probe": probe.name,
            "B_factual_posterior": state.B, "K_procedural_knowledge": state.K,
            "T_source_calibration": state.T, "H_learned_action_value": state.H,
            "approval_events": state.approval_events, "paid_material_net": state.paid_material_net,
            **probe.__dict__, "adult_override_forced_zero": True,
        })
    return records


def summarize_records(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(records)
    by_probe: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_probe.setdefault(str(row["probe"]), []).append(row)
    summaries = {}
    for probe, group in by_probe.items():
        summaries[probe] = {
            "n": len(group),
            "mean_posterior_revision": sum(float(row["posterior_revision"]) for row in group) / len(group),
            "mean_action_persistence": sum(float(row["action_persistence"]) for row in group) / len(group),
            "mean_H": sum(float(row["H_learned_action_value"]) for row in group) / len(group),
            "all_direct_override_zero": all(float(row["direct_override_probability"]) == 0.0 for row in group),
            "evidence_count": sum(int(row["evidence_count"]) for row in group),
        }
    return {"rows": len(rows), "probes": summaries}


def yoked_decision_records(seed: int) -> list[dict[str, Any]]:
    """A 3x3 depth/context assay with the same observed history across ``d``.

    It is a decision assay, not an ecological selection claim. The fixed adult age
    makes every override coordinate inert, directly checking that adult action does
    not receive a hidden age-specific override.
    """
    from v7.experiments.model import KeyedRNG, OrdinarySocialPolicy, PolicyObservation
    rows = []
    for depth in (1, 3, 6):
        for context in (.5, .75, 1.0):
            for d in (0.0, .5, 1.0):
                history_id = _digest((seed, depth, context, "matched-history"))
                observation = PolicyObservation(
                    identity=f"adult-{seed}", season=90, age=7, energy=8.0, time_tokens=12, computation_budget=128,
                    domain="procedure", private_cue="branch_0", beliefs=(("p_branch_0", .5), ("p_branch_1", .5), ("private_likelihood", .8)),
                    procedures=(f"tool|branch=0|depth={depth}",), trust=(("tutor", .7),), habits=(),
                    messages=(("demonstration", "branch_1"),), provenance_roots=("root-shared",), feasible_actions=("branch_0", "branch_1"),
                    action_values=(("branch_0", 0.), ("branch_1", 0.)), prices=(("operation", .01), ("execute", .2 * depth), ("procedure_expected_plus", 1.0), ("procedure_expected_minus", -1.0)),
                    advice="branch_1", source_id="tutor", source_history=(("successes", 4.), ("failures", 2.)), context_mismatch=1.0 - context,
                )
                decision = OrdinarySocialPolicy(d, 0.0).decide(observation, 128, KeyedRNG(str(seed), "postfreeze-yoked", 90))
                rows.append({"seed": seed, "depth": depth, "context_concordance": context, "juvenile_d_procedure": d,
                             "adult_age": 7, "same_history_id": history_id, "private_error_count": 0, "adult_error_count": 0,
                             "posted_checking_cost": .5, "private_evidence_count": 1, "adult_evidence_count": 1,
                             "direct_adult_override": decision.override_applied, "chosen_action": decision.chosen_action,
                             "neutral_action": decision.neutral_action, "operation_count": decision.operation_count,
                             "charged_cost": decision.charged_cost, "label": "MEASURED adult decision; same history, d coordinate is disabled after tau"})
    return rows


class FrozenCoreObservation:
    """External, bounded intervention over a cloned frozen IBM state.

    It can establish that a registered shock/memory-erasure control was applied to actual
    core populations. The frozen core lacks root-level procedure lineage exports,
    therefore it deliberately cannot establish H9's diversity mediation.
    """
    def __init__(self, seed: int, *, d_procedure: float = 0.0, depth: int = 3,
                 chi: float = .75, q_theta: float = .005) -> None:
        from v7.experiments.model import EcologyRun, OrdinarySocialPolicy
        self.seed = seed
        self._run = EcologyRun(seed, OrdinarySocialPolicy, depth=depth, chi=chi, q_theta=q_theta,
                               initial_traits={"d_procedure": d_procedure, "d_local": 0.0},
                               burn_in=60, measurement=180, label=f"postfreeze_observe_{d_procedure:g}")

    @staticmethod
    def _finish(run: Any, *, seed: int, shock: bool, memory_erasure: bool,
                pre_population: int, pre_energy: float, pre_knowledge: int, removed: int) -> dict[str, Any]:
        result = run.run()
        return {"seed": seed, "checkpoint_season": 90, "shock": shock, "memory_erasure": memory_erasure,
                "external_storage_enabled": False, "pre_population": pre_population, "pre_energy": pre_energy,
                "pre_stored_procedures": pre_knowledge, "removed_procedures": removed,
                "post_stored_procedures": result["stored_knowledge"], "recovery_status": result["status"],
                "seasons_completed": result["seasons_completed"], "mean_population": result["mean_population"],
                "replay_digest": result["replay_digest"],
                "claim_label": "PARTIAL: actual cloned-core shock/memory-erasure intervention; memory erasure is not carrier death and root-diversity mediation is unavailable"}

    def run_registered_intervention(self, *, shock: bool, memory_erasure: bool) -> dict[str, Any]:
        checkpoint = self._run.burn_in + 90
        while self._run.season < checkpoint and self._run.status == "running":
            self._run.advance_season()
        pre_population = len(self._run.population)
        pre_energy = sum(person.energy for person in self._run.population.values())
        pre_knowledge = sum(len(person.K) for person in self._run.population.values())
        if shock:
            for family in tuple(self._run.theta):
                self._run.theta[family] = 1 - self._run.theta[family]
        removed = 0
        if memory_erasure:
            for person in self._run.population.values():
                removed += len(person.K)
                person.K.clear(); person.independent_successes.clear()
        return self._finish(self._run, seed=self.seed, shock=shock, memory_erasure=memory_erasure,
                            pre_population=pre_population, pre_energy=pre_energy, pre_knowledge=pre_knowledge, removed=removed)

    def run_cloned_arms(self) -> list[dict[str, Any]]:
        """Clone one matched core population at t=90 into registered interventions."""
        checkpoint = self._run.burn_in + 90
        while self._run.season < checkpoint and self._run.status == "running":
            self._run.advance_season()
        pre_population = len(self._run.population)
        pre_energy = sum(person.energy for person in self._run.population.values())
        pre_knowledge = sum(len(person.K) for person in self._run.population.values())
        arms = []
        for arm, shock, erase in (("control", False, False), ("shock", True, False), ("shock_memory_erasure", True, True)):
            # hashlib state is intentionally not pickleable. Copy every mutable
            # ecological state component explicitly and start a new diagnostic
            # stream, rather than mutating or serializing the frozen core object.
            clone = copy.copy(self._run)
            for name in ("population", "ledger", "biological_edges", "cultural_edges", "decision_samples", "reports", "_season_events", "losses", "_time_used", "theta"):
                setattr(clone, name, copy.deepcopy(getattr(self._run, name)))
            clone.stream = sha256(); clone.start_time = time.monotonic()
            if shock:
                for family in tuple(clone.theta):
                    clone.theta[family] = 1 - clone.theta[family]
            removed = 0
            if erase:
                for person in clone.population.values():
                    removed += len(person.K)
                    person.K.clear(); person.independent_successes.clear()
            row = self._finish(clone, seed=self.seed, shock=shock, memory_erasure=erase,
                               pre_population=pre_population, pre_energy=pre_energy, pre_knowledge=pre_knowledge, removed=removed)
            row["arm"] = arm; row["cloned_at_measurement_season"] = 90
            arms.append(row)
        return arms
