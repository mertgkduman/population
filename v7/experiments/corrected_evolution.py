"""Corrected-overlay finite lineage assay; no frozen EcologyRun is simulated here."""
from __future__ import annotations

from copy import copy, deepcopy
from dataclasses import asdict
from hashlib import sha256
from math import sqrt
from statistics import mean
from typing import Any

from v7.experiments.corrected_model import CorrectedEcologyRun
from v7.experiments.evolution import ArmResult, DIRECTED_PAIRS, LINEAGE_SEASONS, MIN_PARENT_ENERGY, trait_map
from v7.experiments.model import Individual, VectorOverridePolicy

SELECTION_SEEDS = tuple(range(79001, 79025))
EXTENSION_SEEDS = tuple(range(79025, 79097))
DEFAULT_REGIMES = {1: {"depth": 1, "chi": .5, "q_theta": 0.}, 5: {"depth": 3, "chi": .75, "q_theta": .005}, 9: {"depth": 6, "chi": 1., "q_theta": .02}}
BIRTH_WAIT_SEASONS = 20


def state_digest(run: CorrectedEcologyRun) -> str:
    payload = {"season": run.season, "resource": run.resource, "theta": run.theta, "status": run.status,
               "events": run.events, "stream": run.stream.hexdigest(),
               "population": [(p.identity, p.age, p.energy, p.traits, sorted(p.B.items()), sorted(p.K), sorted(p.T.items()), sorted(p.H.items()), p.parent_id) for p in sorted(run.population.values(), key=lambda x: x.identity)],
               "edges": sorted(run.biological_edges)}
    return sha256(repr(payload).encode()).hexdigest()


def clone_resident_state(run: CorrectedEcologyRun) -> CorrectedEcologyRun:
    clone = copy(run)
    clone.population, clone.theta, clone.losses = deepcopy(run.population), dict(run.theta), dict(run.losses)
    clone._time_used, clone._season_events = dict(run._time_used), list(run._season_events)
    clone.reports, clone.decision_samples = list(run.reports), list(run.decision_samples)
    clone.biological_edges, clone.cultural_edges, clone.stream = list(run.biological_edges), list(run.cultural_edges), run.stream.copy()
    return clone


def descendants(run: CorrectedEcologyRun, root: str) -> set[str]:
    children: dict[str, list[str]] = {}
    for parent, child in run.biological_edges: children.setdefault(parent, []).append(child)
    found, frontier = {root}, [root]
    while frontier:
        for child in children.get(frontier.pop(), ()):
            if child not in found: found.add(child); frontier.append(child)
    return found


def teacher_pool(run: CorrectedEcologyRun) -> dict[str, Any]:
    eligible = [p for p in run.population.values() if p.eligible_sequences()]
    return {"residents": len(run.population), "eligible_teachers": len(eligible),
            "eligible_teacher_fraction": len(eligible)/max(1, len(run.population)),
            "mean_age_eligible": mean([p.age for p in eligible]) if eligible else 0.,
            "stored_sequences_eligible": sum(len(p.eligible_sequences()) for p in eligible),
            "source": "resident acquired state only; corrected-overlay base"}


def _set_traits(child: Individual, traits: tuple[float, float]) -> None:
    child.traits = tuple(sorted(trait_map(traits).items())); child.policy = VectorOverridePolicy(*traits)


class FirstNaturalBirthCorrected(CorrectedEcologyRun):
    introduction_traits: tuple[float, float]
    introduction: dict[str, Any] | None
    def paid_birth(self, parent: Individual, *, newborn_id: str | None = None):  # type: ignore[override]
        before = state_digest(self) if getattr(self, "introduction", None) is None else ""
        energy, age = parent.energy, parent.age
        child, event = super().paid_birth(parent, newborn_id=newborn_id)
        if self.introduction is None:
            _set_traits(child, self.introduction_traits)
            self.introduction = {"born_id": child.identity, "parent_id": parent.identity, "parent_age": age,
                "parent_energy_before": energy, "parent_energy_after": parent.energy, "birth_cost": event.birth_cost,
                "newborn_energy": child.energy, "blank_acquired_state": not child.B and not child.K and not child.T and not child.H,
                "pre_birth_state_sha256": before}
        return child, event


def acquired_resident(seed: int, regime: int, traits: tuple[float, float]) -> CorrectedEcologyRun:
    spec = DEFAULT_REGIMES[regime]
    run = CorrectedEcologyRun(seed, VectorOverridePolicy, depth=int(spec["depth"]), chi=float(spec["chi"]), q_theta=float(spec["q_theta"]), graph_variant=(seed+regime) % 2, initial_traits=trait_map(traits), burn_in=60, measurement=0, label="corrected-resident")
    while run.season < 60 and run.status == "running": run.advance_season()
    if run.status != "running" or not run.population: raise RuntimeError(f"corrected resident failed: {run.status}")
    run._time_used = {}; return run


def _arm(resident: CorrectedEcologyRun, seed: int, regime: int, pair: tuple[tuple[float,float],tuple[float,float]], arm: str, traits: tuple[float,float], horizon: int) -> ArmResult:
    run = clone_resident_state(resident); run.__class__ = FirstNaturalBirthCorrected; run.introduction_traits, run.introduction = traits, None
    initial = state_digest(run)
    while run.status == "running" and run.introduction is None and run.season < resident.season+BIRTH_WAIT_SEASONS: run.advance_season()
    intro = run.introduction; directed = f"{pair[0]}->{pair[1]}"
    if intro is None:
        return ArmResult(seed, regime, directed, arm, horizon, None, traits, pair[0], None, None, None, None, None, None, False, initial, state_digest(run), teacher_pool(run), 0, 0, 0, True, run.status == "cap_censored", "no_birth_censored" if run.status == "running" else run.status, (), run.stream.hexdigest(), max((abs(x.energy_resource_residual) for x in run.reports), default=0.), run.events, True)
    born = str(intro["born_id"]); trajectory: list[float] = []
    for _ in range(horizon):
        if run.status != "running": break
        run.advance_season(); lineage = descendants(run, born); trajectory.append(sum(x in run.population for x in lineage)/max(1, len(run.population)))
    lineage = descendants(run, born); living = sum(x in run.population for x in lineage)
    return ArmResult(seed, regime, directed, arm, horizon, born, traits, pair[0], str(intro["parent_id"]), int(intro["parent_age"]), float(intro["parent_energy_before"]), float(intro["parent_energy_after"]), float(intro["birth_cost"]), float(intro["newborn_energy"]), bool(intro["blank_acquired_state"]), str(intro["pre_birth_state_sha256"]), state_digest(run), teacher_pool(run), len(lineage), living, len(lineage)-living, living == 0, run.status == "cap_censored", run.status, tuple(trajectory), run.stream.hexdigest(), max((abs(x.energy_resource_residual) for x in run.reports), default=0.), run.events, False)


def paired_lineage(seed: int, regime: int, pair: tuple[tuple[float,float],tuple[float,float]], *, horizon: int = LINEAGE_SEASONS) -> tuple[ArmResult,ArmResult]:
    resident = acquired_resident(seed, regime, pair[0]); mutant = _arm(resident, seed, regime, pair, "mutant", pair[1], horizon); neutral = _arm(resident, seed, regime, pair, "neutral_tag", pair[0], horizon)
    if mutant.resident_state_sha256 != neutral.resident_state_sha256 or mutant.born_id != neutral.born_id: raise AssertionError("corrected paired continuations differ before trait intervention")
    return mutant, neutral


def gate_assays() -> dict[str, Any]:
    left, right = paired_lineage(79001, 1, ((0.,0.),(0.,0.)), horizon=8)
    comparable = lambda r: {k:v for k,v in r.record().items() if k != "arm"}
    paid = not left.no_birth_censored and left.parent_age is not None and left.parent_energy_before is not None and left.parent_energy_after is not None and left.parent_age >= 5 and left.parent_energy_before >= MIN_PARENT_ENERGY and abs(left.parent_energy_before-left.parent_energy_after-16.) < 1e-9 and left.blank_acquired_state
    checks = {"paid_birth": paid, "blank_state": left.blank_acquired_state and right.blank_acquired_state, "neutral_self_mutant": comparable(left) == comparable(right), "label_genotype_exchange": left.born_id == right.born_id and comparable(left) == comparable(right), "drift_replay": left.replay_digest == right.replay_digest, "ledger": left.ledger_residual_max < 1e-8 and right.ledger_residual_max < 1e-8, "resident_teacher_pool": left.teacher_pool["source"].startswith("resident acquired")}
    return {"status":"passed" if all(checks.values()) else "failed", "checks":checks, "self_mutant":left.record(), "neutral_tag":right.record(), "claim_limit":"Corrected-overlay implementation equality gates only; not selection outcomes."}


def summarize(records: list[ArmResult]) -> dict[str, Any]:
    index: dict[tuple[int,str,int], dict[str,ArmResult]] = {}
    for record in records: index.setdefault((record.regime, record.directed_pair, record.seed), {})[record.arm] = record
    # Only complete, predeclared initial / eight-seed batches enter inference.
    accepted: set[tuple[int,str,int]] = set()
    schedule = [range(79001,79025), *[range(x,x+8) for x in range(79025,79097,8)]]
    for regime in DEFAULT_REGIMES:
        for resident, mutant in DIRECTED_PAIRS:
            directed = f"{resident}->{mutant}"
            for batch in schedule:
                keys=[(regime,directed,seed) for seed in batch]
                if all(set(index.get(key,{})) == {"mutant","neutral_tag"} for key in keys): accepted.update(keys)
                else: break
    rows=[row for row in records if (row.regime,row.directed_pair,row.seed) in accepted]
    arms: dict[str,dict[str,Any]]={}
    for regime,directed,arm in sorted({(x.regime,x.directed_pair,x.arm) for x in rows}):
        values=[x for x in rows if (x.regime,x.directed_pair,x.arm)==(regime,directed,arm)]
        paid=[x for x in values if not x.no_birth_censored]; counts=[x.living_descendants for x in paid]; n=len(counts); established=sum(x>0 for x in counts); p=established/max(1,n); z=1.96; denom=1+z*z/max(1,n); centre=(p+z*z/(2*max(1,n)))/denom; half=z*sqrt(p*(1-p)/max(1,n)+z*z/(4*max(1,n)*max(1,n)))/denom
        average=mean(counts) if counts else 0.; mcse=sqrt(sum((x-average)**2 for x in counts)/max(1,n-1)/n) if n>1 else float("inf")
        arms[f"regime_{regime}|{directed}|{arm}"]={"paid_birth_denominator":n,"no_birth_censored":len(values)-n,"mean_expected_descendants_per_paid_newborn":average,"arm_expected_descendants_mcse_diagnostic":mcse,"establishment":established,"extinction":n-established,"establishment_wilson_95":[max(0.,centre-half),min(1.,centre+half)],"establishment_wilson_half_width":half,"cap_censored":sum(x.cap_censored for x in values),"distribution":{str(k):counts.count(k) for k in sorted(set(counts))}}
    contrast: dict[str,dict[str,Any]]={}
    for regime,directed,seed in accepted:
        pair=index[(regime,directed,seed)]
        if not pair["mutant"].no_birth_censored and not pair["neutral_tag"].no_birth_censored: contrast.setdefault(f"regime_{regime}|{directed}",{}).setdefault("_deltas",[]).append(pair["mutant"].living_descendants-pair["neutral_tag"].living_descendants)
    for key,value in list(contrast.items()):
        deltas=value.pop("_deltas"); n=len(deltas); average=mean(deltas) if deltas else 0.; mcse=sqrt(sum((x-average)**2 for x in deltas)/max(1,n-1)/n) if n>1 else float("inf"); regime,directed=key.split("|",1); contrast[key]={"paired_paid_birth_denominator":n,"mean_descendant_difference_mutant_minus_neutral":average,"paired_descendant_difference_mcse":mcse,"max_establishment_wilson_half_width":max(arms[f"{regime}|{directed}|{arm}"]["establishment_wilson_half_width"] for arm in ("mutant","neutral_tag")),"no_birth_censored_pairs":len([x for x in accepted if x[:2]==(int(regime.split("_")[1]),directed)])-n}
    return {"arms":arms,"paired_contrasts":contrast,"batch_accounting":{"raw_rows_retained":len(records),"rows_in_completed_fixed_batches":len(rows),"partial_batch_rows_excluded_from_precision":len(records)-len(rows)}}
