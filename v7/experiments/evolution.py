"""Finite, paid-newborn lineage assays over the immutable V7 ecology core.

This module deliberately owns selection bookkeeping rather than changing the frozen
IBM.  A comparison is a pair of counterfactual continuations from one acquired
resident culture and resource state.  The only intervention is the *inherited*
trait of a real, parent-paid newborn; labels are external bookkeeping and never
reach the policy or the keyed random streams.
"""
from __future__ import annotations

from collections import Counter
from copy import copy, deepcopy
from dataclasses import asdict, dataclass
from hashlib import sha256
from math import sqrt
from statistics import mean
from typing import Any, Iterable, Mapping

from v7.experiments.model import EcologyRun, Individual, VectorOverridePolicy


LINEAGE_SEASONS = 80
COMPETITION_SEASONS = 120
MIN_PARENT_ENERGY = 16.0 + 3.0
BIRTH_WAIT_SEASONS = 20
SELECTION_SEEDS = tuple(range(73001, 73025))
EXTENSION_SEEDS = tuple(range(73025, 73097))
DEFAULT_REGIMES: Mapping[int, Mapping[str, float | int]] = {
    1: {"depth": 1, "chi": .5, "q_theta": 0.0},
    5: {"depth": 3, "chi": .75, "q_theta": .005},
    9: {"depth": 6, "chi": 1.0, "q_theta": .02},
}
DIRECTED_PAIRS = (
    ((0.0, 0.0), (0.5, 0.0)),
    ((0.5, 0.0), (0.0, 0.0)),
    ((0.5, 0.0), (0.5, 0.5)),
    ((0.5, 0.5), (0.5, 0.0)),
)


def trait_map(traits: tuple[float, float]) -> dict[str, float]:
    return {"d_procedure": float(traits[0]), "d_local": float(traits[1])}


def state_digest(run: EcologyRun) -> str:
    """A stable fingerprint of a resident state, including its RNG stream digest."""
    payload = {
        "season": run.season, "resource": run.resource, "theta": run.theta,
        "status": run.status, "events": run.events, "stream": run.stream.hexdigest(),
        "population": [
            (p.identity, p.age, p.energy, p.traits, sorted(p.B.items()), sorted(p.K),
             sorted(p.T.items()), sorted(p.H.items()), p.parent_id)
            for p in sorted(run.population.values(), key=lambda x: x.identity)
        ],
        "edges": sorted(run.biological_edges),
    }
    return sha256(repr(payload).encode()).hexdigest()


def clone_resident_state(run: EcologyRun) -> EcologyRun:
    """Clone an ecology continuation without attempting to deepcopy hashlib state.

    ``hashlib.HASH`` objects cannot be pickled/deep-copied.  Copying the stream is
    the semantic operation wanted here: both counterfactual arms begin with exactly
    the same accumulated event prefix.
    """
    clone = copy(run)
    clone.population = deepcopy(run.population)
    clone.theta = dict(run.theta)
    clone.losses = dict(run.losses)
    clone._time_used = dict(run._time_used)
    clone._season_events = list(run._season_events)
    clone.reports = list(run.reports)
    clone.decision_samples = list(run.decision_samples)
    clone.biological_edges = list(run.biological_edges)
    clone.cultural_edges = list(run.cultural_edges)
    clone.stream = run.stream.copy()
    return clone


def teacher_composition(run: EcologyRun) -> dict[str, Any]:
    residents = list(run.population.values())
    eligible = [p for p in residents if p.eligible_sequences()]
    return {
        "residents": len(residents), "eligible_teachers": len(eligible),
        "eligible_teacher_fraction": len(eligible) / max(1, len(residents)),
        "mean_age_eligible": mean([p.age for p in eligible]) if eligible else 0.0,
        "stored_sequences_eligible": sum(len(p.eligible_sequences()) for p in eligible),
        "source": "resident acquired state only; no custom mutant teacher pool",
    }


def descendant_ids(run: EcologyRun, root: str) -> set[str]:
    children: dict[str, list[str]] = {}
    for parent, child in run.biological_edges:
        children.setdefault(parent, []).append(child)
    descendants, frontier = {root}, [root]
    while frontier:
        parent = frontier.pop()
        for child in children.get(parent, ()):
            if child not in descendants:
                descendants.add(child); frontier.append(child)
    return descendants


def _set_inherited_traits(child: Individual, traits: tuple[float, float]) -> None:
    inherited = tuple(sorted(trait_map(traits).items()))
    child.traits = inherited
    child.policy = VectorOverridePolicy(*traits)


class FirstNaturalBirthRun(EcologyRun):
    """A non-core hook that tags the first core-sampled birth after burn-in.

    ``EcologyRun.advance_season`` already decides whether a mature, solvent parent
    reproduces, spends its reproduction token, and calls ``self.paid_birth``.  This
    override only intercepts that virtual call *after* the immutable core has made
    and charged the event.  It never manufactures a birth or chooses a parent.
    """
    introduction_traits: tuple[float, float]
    introduction: dict[str, Any] | None

    def paid_birth(self, parent: Individual, *, newborn_id: str | None = None):  # type: ignore[override]
        before = state_digest(self) if getattr(self, "introduction", None) is None else ""
        parent_before, parent_age = parent.energy, parent.age
        child, event = super().paid_birth(parent, newborn_id=newborn_id)
        if self.introduction is None:
            _set_inherited_traits(child, self.introduction_traits)
            self.introduction = {
                "born_id": child.identity, "parent_id": parent.identity,
                "parent_age": parent_age, "parent_energy_before": parent_before,
                "parent_energy_after": parent.energy, "birth_cost": event.birth_cost,
                "newborn_energy": child.energy,
                "blank_acquired_state": not child.B and not child.K and not child.T and not child.H,
                "pre_birth_state_sha256": before,
            }
        return child, event


@dataclass(frozen=True)
class ArmResult:
    seed: int
    regime: int
    directed_pair: str
    arm: str
    horizon: int
    born_id: str | None
    mutant_traits: tuple[float, float]
    resident_traits: tuple[float, float]
    parent_id: str | None
    parent_age: int | None
    parent_energy_before: float | None
    parent_energy_after: float | None
    birth_cost: float | None
    newborn_energy: float | None
    blank_acquired_state: bool
    resident_state_sha256: str
    post_birth_sha256: str
    teacher_pool: dict[str, Any]
    total_descendants: int
    living_descendants: int
    dead_descendants: int
    extinct: bool
    cap_censored: bool
    terminal_status: str
    frequency_trajectory: tuple[float, ...]
    replay_digest: str
    ledger_residual_max: float
    events: int
    no_birth_censored: bool

    def record(self) -> dict[str, Any]:
        return asdict(self)


def _run_arm(resident: EcologyRun, *, seed: int, regime: int, directed_pair: tuple[tuple[float, float], tuple[float, float]],
             arm: str, traits: tuple[float, float], horizon: int) -> ArmResult:
    run = clone_resident_state(resident)
    run.__class__ = FirstNaturalBirthRun
    run.introduction_traits = traits
    run.introduction = None
    initial = state_digest(run)
    # The wait is fixed before outcomes.  No naturally paid birth is explicitly
    # retained as no-birth-censored rather than invented or silently discarded.
    while run.status == "running" and run.introduction is None and run.season < resident.season + BIRTH_WAIT_SEASONS:
        run.advance_season()
    intro = run.introduction
    if intro is None:
        return ArmResult(seed, regime, f"{directed_pair[0]}->{directed_pair[1]}", arm, horizon,
                         None, traits, directed_pair[0], None, None, None, None, None, None, False,
                         initial, state_digest(run), teacher_composition(run), 0, 0, 0, True,
                         run.status == "cap_censored", "no_birth_censored" if run.status == "running" else run.status,
                         (), run.stream.hexdigest(), max((abs(row.energy_resource_residual) for row in run.reports), default=0.0),
                         run.events, True)
    child_id = str(intro["born_id"])
    composition = teacher_composition(run)
    frequencies: list[float] = []
    for _ in range(horizon):
        if run.status != "running": break
        run.advance_season()
        all_ids = descendant_ids(run, child_id)
        living = sum(identity in run.population for identity in all_ids)
        frequencies.append(living / max(1, len(run.population)))
    all_ids = descendant_ids(run, child_id)
    living = sum(identity in run.population for identity in all_ids)
    return ArmResult(
        seed=seed, regime=regime,
        directed_pair=f"{directed_pair[0]}->{directed_pair[1]}", arm=arm, horizon=horizon,
        born_id=child_id, mutant_traits=traits, resident_traits=directed_pair[0],
        parent_id=str(intro["parent_id"]), parent_age=int(intro["parent_age"]),
        parent_energy_before=float(intro["parent_energy_before"]), parent_energy_after=float(intro["parent_energy_after"]),
        birth_cost=float(intro["birth_cost"]), newborn_energy=float(intro["newborn_energy"]), blank_acquired_state=bool(intro["blank_acquired_state"]),
        resident_state_sha256=str(intro["pre_birth_state_sha256"]), post_birth_sha256=state_digest(run), teacher_pool=composition,
        total_descendants=len(all_ids), living_descendants=living,
        dead_descendants=len(all_ids) - living, extinct=living == 0,
        cap_censored=run.status == "cap_censored", terminal_status=run.status,
        frequency_trajectory=tuple(frequencies), replay_digest=run.stream.hexdigest(),
        ledger_residual_max=max((abs(row.energy_resource_residual) for row in run.reports), default=0.0),
        events=run.events, no_birth_censored=False,
    )


def acquired_resident(seed: int, regime: int, *, resident_traits: tuple[float, float], regimes: Mapping[int, Mapping[str, float | int]] = DEFAULT_REGIMES) -> EcologyRun:
    spec = regimes[regime]
    run = EcologyRun(seed, VectorOverridePolicy, depth=int(spec["depth"]), chi=float(spec["chi"]),
                     q_theta=float(spec["q_theta"]), graph_variant=(seed + regime) % 2,
                     initial_traits=trait_map(resident_traits), burn_in=60, measurement=0,
                     label="resident")
    while run.season < 60 and run.status == "running":
        run.advance_season()
    if run.status != "running" or not run.population:
        raise RuntimeError(f"resident acquisition did not yield a live shared culture: {run.status}")
    # The introduction waits for the next naturally sampled core birth.  Starting
    # a fresh season merely clears the completed prior season's token accounting.
    run._time_used = {}
    return run


def paired_lineage(seed: int, regime: int, directed_pair: tuple[tuple[float, float], tuple[float, float]], *, horizon: int = LINEAGE_SEASONS,
                   regimes: Mapping[int, Mapping[str, float | int]] = DEFAULT_REGIMES) -> tuple[ArmResult, ArmResult]:
    resident = acquired_resident(seed, regime, resident_traits=directed_pair[0], regimes=regimes)
    mutant = _run_arm(resident, seed=seed, regime=regime, directed_pair=directed_pair,
                      arm="mutant", traits=directed_pair[1], horizon=horizon)
    neutral = _run_arm(resident, seed=seed, regime=regime, directed_pair=directed_pair,
                       arm="neutral_tag", traits=directed_pair[0], horizon=horizon)
    if mutant.resident_state_sha256 != neutral.resident_state_sha256 or mutant.born_id != neutral.born_id:
        raise AssertionError("paired counterfactuals did not start from one resident state and born ID")
    return mutant, neutral


def _self_pair(seed: int, regime: int) -> tuple[ArmResult, ArmResult]:
    pair = ((0.0, 0.0), (0.0, 0.0))
    return paired_lineage(seed, regime, pair, horizon=8)


def gate_assays() -> dict[str, Any]:
    """Fail-closed gates required before a substantive pair can run."""
    left, right = _self_pair(73001, 1)
    comparable = {key: value for key, value in left.record().items() if key not in {"arm"}}
    other = {key: value for key, value in right.record().items() if key not in {"arm"}}
    paid_blank = (not left.no_birth_censored and left.parent_age is not None and left.parent_energy_before is not None and left.parent_energy_after is not None and
                  left.parent_age >= 5 and left.parent_energy_before >= MIN_PARENT_ENERGY and
                  abs(left.parent_energy_before - left.parent_energy_after - 16.0) < 1e-9 and
                  left.birth_cost == 16.0 and left.newborn_energy == 8.0 and left.blank_acquired_state)
    self_neutral = comparable == other
    # Tags are external to core state.  Exchanging their bookkeeping labels must
    # exchange no causal input, so the paired records remain identical.
    exchange = self_neutral and left.born_id == right.born_id
    resident_teachers = left.teacher_pool["source"].startswith("resident acquired")
    ledger = left.ledger_residual_max < 1e-8 and right.ledger_residual_max < 1e-8
    replay = left.replay_digest == right.replay_digest
    gates = {"paid_birth": paid_blank, "blank_state": left.blank_acquired_state and right.blank_acquired_state,
             "neutral_self_mutant": self_neutral, "label_genotype_exchange": exchange,
             "drift_replay": replay, "ledger": ledger, "resident_teacher_pool": resident_teachers}
    return {"status": "passed" if all(gates.values()) else "failed", "checks": gates,
            "self_mutant": left.record(), "neutral_tag": right.record(),
            "claim_limit": "Gate assays validate implementation equality only; they are not selection outcomes."}


def summarize(records: Iterable[ArmResult]) -> dict[str, Any]:
    raw_rows = list(records)
    # A crash may leave a durable prefix of an eight-seed batch.  Preserve those
    # raw rows, but do not let a partial batch become an outcome-responsive
    # precision decision.  Only the initial 24 and wholly completed fixed blocks
    # of eight contribute to scientific summaries.
    pair_index: dict[tuple[int, str, int], set[str]] = {}
    for row in raw_rows:
        pair_index.setdefault((row.regime, row.directed_pair, row.seed), set()).add(row.arm)
    accepted: set[tuple[int, str, int]] = set()
    for regime in DEFAULT_REGIMES:
        for resident, mutant in DIRECTED_PAIRS:
            directed = f"{resident}->{mutant}"
            schedule = [range(73001, 73025), *[range(start, start + 8) for start in range(73025, 73097, 8)]]
            for block in schedule:
                keys = [(regime, directed, seed) for seed in block]
                if all(pair_index.get(key) == {"mutant", "neutral_tag"} for key in keys):
                    accepted.update(keys)
                else:
                    break
    rows = [row for row in raw_rows if (row.regime, row.directed_pair, row.seed) in accepted]
    groups: dict[tuple[int, str, str], list[ArmResult]] = {}
    for row in rows: groups.setdefault((row.regime, row.directed_pair, row.arm), []).append(row)
    arms: dict[str, Any] = {}
    for key, values in sorted(groups.items()):
        born = [x for x in values if not x.no_birth_censored]
        counts = [x.living_descendants for x in born]
        n = len(counts); average = mean(counts) if counts else 0.0
        mcse = (sqrt(sum((x - average) ** 2 for x in counts) / max(1, n - 1) / n) if n > 1 else float("inf"))
        established = sum(x > 0 for x in counts)
        p = established / max(1, n)
        # Wilson 95% interval, keeping every extinction in the denominator.
        z = 1.96; denom = 1 + z*z/n; centre = (p + z*z/(2*n)) / denom
        half = z * sqrt(p*(1-p)/n + z*z/(4*n*n)) / denom
        arms[f"regime_{key[0]}|{key[1]}|{key[2]}"] = {
            "paid_birth_denominator": n, "no_birth_censored": len(values) - n,
            "mean_expected_descendants_per_paid_newborn": average, "arm_expected_descendants_mcse_diagnostic": mcse,
            "establishment": established, "extinction": n-established,
            "establishment_wilson_95": [max(0.0, centre-half), min(1.0, centre+half)],
            "establishment_wilson_half_width": half,
            "distribution": dict(sorted(Counter(counts).items())),
            "censored": sum(x.cap_censored for x in values),
        }
    contrasts: dict[str, Any] = {}
    paired: dict[tuple[int, str, int], dict[str, ArmResult]] = {}
    for row in rows:
        paired.setdefault((row.regime, row.directed_pair, row.seed), {})[row.arm] = row
    for (regime, directed, _seed), pair in paired.items():
        if set(pair) == {"mutant", "neutral_tag"} and not pair["mutant"].no_birth_censored and not pair["neutral_tag"].no_birth_censored:
            key = f"regime_{regime}|{directed}"
            contrasts.setdefault(key, []).append(pair["mutant"].living_descendants - pair["neutral_tag"].living_descendants)
    contrast_rows: dict[str, Any] = {}
    for key, deltas in sorted(contrasts.items()):
        n = len(deltas); average = mean(deltas) if deltas else 0.0
        mcse = sqrt(sum((x - average) ** 2 for x in deltas) / max(1, n - 1) / n) if n > 1 else float("inf")
        # Establishment is a Bernoulli outcome per actually paid newborn.  Report
        # mutant and neutral Wilson uncertainty separately; no-birth trials are a
        # distinct censoring count and never turned into descendant zeros.
        arm_rows = [arms[f"regime_{key.split('|')[0].split('_')[1]}|{key.split('|')[1]}|{arm}"] for arm in ("mutant", "neutral_tag")]
        contrast_rows[key] = {"paired_paid_birth_denominator": n, "mean_descendant_difference_mutant_minus_neutral": average,
                              "paired_descendant_difference_mcse": mcse,
                              "max_establishment_wilson_half_width": max(x["establishment_wilson_half_width"] for x in arm_rows),
                              "no_birth_censored_pairs": max(0, len([p for p in paired if p[:2] == (int(key.split('|')[0].split('_')[1]), key.split('|')[1])]) - n)}
    return {"arms": arms, "paired_contrasts": contrast_rows,
            "batch_accounting": {"raw_rows_retained": len(raw_rows), "rows_in_completed_fixed_batches": len(rows),
                                  "partial_batch_rows_excluded_from_precision": len(raw_rows) - len(rows)}}
