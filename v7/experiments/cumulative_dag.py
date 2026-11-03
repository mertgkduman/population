"""Closed-resource eight-module causal-procedure DAG validation fixture.

This module is deliberately separate from the V7 deference model.  It asks a
much narrower engineering/scientific question: can a finite, demographically
open population accumulate a procedure whose eight private discoveries cannot
be completed by one individual under the declared physical protocol?  It does
not model authority, childhood deference, genetic selection, or a knowledge
income bonus.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
from typing import Any


def uniform(*key: object) -> float:
    return int.from_bytes(sha256(repr(key).encode()).digest()[:8], "big") / 2**64


@dataclass(frozen=True)
class Settings:
    horizon: int = 60
    start_population: int = 10
    lifespan: int = 18
    maturity: int = 3
    time_cap: int = 4
    resource_cap: float = 800.0
    resource_initial: float = 600.0
    regeneration: float = 0.06
    conversion: float = 0.75
    maintenance: float = 0.5
    discovery_work: int = 8
    private_accuracy: float = 0.8
    work_cost: float = 0.2
    birth_cost: float = 6.0
    newborn_energy: float = 4.0
    birth_probability: float = 0.12
    population_cap: int = 256
    safe_harvest_resources: float = 2.0
    full_harvest_resources: float = 4.0


MODULES = tuple(f"m{i}" for i in range(8))
CANONICAL_PREQS = {
    "m0": (), "m1": (), "m2": ("m0",), "m3": ("m1",),
    "m4": ("m2",), "m5": ("m3",), "m6": ("m4", "m5"), "m7": ("m6",),
}
# A genuinely different causal graph: three roots, a convergent middle, and
# different depth/parent relationships, rather than a name permutation.
SCRAMBLED_PREQS = {
    "m0": (), "m1": (), "m2": (), "m3": ("m0", "m1"),
    "m4": ("m2",), "m5": ("m3",), "m6": ("m4", "m5"), "m7": ("m6",),
}
ARMS = (
    "transmission_innovation_retention",
    "private_only",
    "transmission_only_no_bootstrap_innovation",
    "no_retention",
    "causal_prerequisite_scramble",
)


@dataclass
class Person:
    ident: str
    age: int = 0
    energy: float = 8.0
    parent: str | None = None
    receipts: dict[str, str] = field(default_factory=dict)
    private_progress: dict[str, int] = field(default_factory=dict)
    program_roots: tuple[str, ...] = ()


class World:
    """A single closed-resource population with receipts as its only culture."""

    def __init__(self, seed: int, arm: str, cfg: Settings = Settings()) -> None:
        if arm not in ARMS:
            raise ValueError(f"unknown arm {arm}")
        self.seed, self.arm, self.cfg = seed, arm, cfg
        self.prereqs = SCRAMBLED_PREQS if arm == "causal_prerequisite_scramble" else CANONICAL_PREQS
        self.context = "scrambled" if arm == "causal_prerequisite_scramble" else "canonical"
        self.people = {f"f{i}": Person(f"f{i}") for i in range(cfg.start_population)}
        self.resource = cfg.resource_initial
        self.initial = self.resource + sum(p.energy for p in self.people.values())
        self.regenerated = self.sinks = 0.0
        self.births = self.deaths = self.removals = 0
        self.status = "running"
        self.season = -1
        self.receipt_no = 0
        self.receipts: dict[str, dict[str, Any]] = {}
        self.events: list[dict[str, Any]] = []
        self.history: list[dict[str, Any]] = []
        self.total_work = 0
        self.innovations = self.copies = self.recombinations = self.modifications = 0
        self.physical_failures = self.private_attempts = 0
        self.n_before = self.b_before = self.d_before = self.r_before = 0

    def _receipt_id(self) -> str:
        self.receipt_no += 1
        return f"{self.arm}:{self.seed}:r{self.receipt_no:06d}"

    def charge(self, p: Person, value: float) -> bool:
        if value < 0 or p.energy + 1e-12 < value:
            return False
        p.energy -= value
        self.sinks += value
        return True

    def remove(self, ident: str, cause: str) -> None:
        p = self.people.pop(ident)
        assert p.energy >= -1e-10
        self.sinks += p.energy
        if cause == "removal":
            self.removals += 1
        else:
            self.deaths += 1

    def begin(self, season: int) -> None:
        self.season = season
        self.n_before, self.b_before = len(self.people), self.births
        self.d_before, self.r_before = self.deaths, self.removals
        gain = self.cfg.regeneration * (self.cfg.resource_cap - self.resource)
        assert gain >= -1e-9
        self.resource += gain
        self.regenerated += gain
        for p in list(self.people.values()):
            p.age += 1
            self.charge(p, min(p.energy, self.cfg.maintenance))
            if p.energy <= 1e-12 or p.age > self.cfg.lifespan:
                self.remove(p.ident, "death")
        self.snapshot = tuple(sorted(self.people))

    def allocate(self, offered: int) -> None:
        assert 0 <= offered <= len(self.snapshot) * self.cfg.time_cap
        self.remaining = {ident: 0 for ident in self.snapshot}
        self.used = {ident: 0 for ident in self.snapshot}
        ordered = sorted(self.snapshot, key=lambda i: uniform("allocation", self.seed, self.season, i))
        for n in range(offered):
            self.remaining[ordered[n % len(ordered)]] += 1
        self.allocated = dict(self.remaining)
        self.offered = offered

    def spend(self, p: Person) -> None:
        assert p.ident in self.remaining and self.remaining[p.ident] > 0
        self.remaining[p.ident] -= 1
        self.used[p.ident] += 1
        self.total_work += 1

    def harvest(self, p: Person, full: bool = False) -> None:
        """A paid physical withdrawal; the sole route by which energy enters people."""
        self.spend(p)
        requested = self.cfg.full_harvest_resources if full else self.cfg.safe_harvest_resources
        drawn = min(self.resource, requested)
        self.resource -= drawn
        p.energy += self.cfg.conversion * drawn
        self.sinks += (1.0 - self.cfg.conversion) * drawn
        self.events.append({"kind": "harvest", "season": self.season, "person": p.ident,
                            "work": 1, "drawn_resource": drawn, "energy_credit": self.cfg.conversion * drawn,
                            "full_recipe": full})

    def _public_candidate(self, p: Person) -> str:
        # This public catalogue order does not reveal true parameters or prerequisites.
        return next(m for m in MODULES if m not in p.receipts)

    def _owns_prereqs(self, p: Person, module: str) -> bool:
        return all(parent in p.receipts for parent in self.prereqs[module])

    def _record_receipt(self, p: Person, module: str, parameter: str, kind: str,
                        donor: Person | None = None, donor_receipt: str | None = None,
                        fidelity: float = 1.0, private_outcome: bool | None = None) -> str:
        rid = self._receipt_id()
        parent_ids = [p.receipts[m] for m in self.prereqs[module] if m in p.receipts]
        inherited_root = None
        if donor_receipt:
            inherited_root = self.receipts[donor_receipt]["source_innovation_root"]
        record = {
            "receipt_id": rid, "procedure_id": f"procedure:{rid}", "module": module,
            "module_parameter": parameter, "prerequisites": list(self.prereqs[module]),
            "parent_procedure_ids": parent_ids, "source_innovation_root": inherited_root or rid,
            "immediate_teacher_id": donor.ident if donor else None,
            "immediate_donor_receipt_id": donor_receipt, "owner_id": p.ident, "learner_id": p.ident,
            "genetic_parent_id": p.parent, "season": self.season, "kind": kind,
            "pupil_time_debit": 1, "teacher_time_debit": 1 if donor else 0,
            "pupil_energy_debit": self.cfg.work_cost, "teacher_energy_debit": self.cfg.work_cost if donor else 0.0,
            "fidelity": fidelity, "private_candidate_correct": private_outcome,
            "physical_feedback": "success", "functional_at_acquisition": self._owns_prereqs(p, module),
        }
        self.receipts[rid] = record
        self.events.append({"kind": kind, "receipt_id": rid, "season": self.season,
                            "learner": p.ident, "teacher": donor.ident if donor else None,
                            "module": module, "fidelity": fidelity})
        p.receipts[module] = rid
        return rid

    def private_step(self, p: Person) -> None:
        self.spend(p)
        assert self.charge(p, self.cfg.work_cost)
        module = self._public_candidate(p)
        progress = p.private_progress.get(module, 0) + 1
        p.private_progress[module] = progress
        self.events.append({"kind": "private_work", "season": self.season, "person": p.ident,
                            "module": module, "work": 1, "energy_debit": self.cfg.work_cost})
        if progress < self.cfg.discovery_work:
            return
        p.private_progress[module] = 0
        self.private_attempts += 1
        # The agent sees only this physical outcome, never the hidden parameter.
        candidate_correct = uniform("private_candidate", self.seed, self.season, p.ident, module, self.private_attempts) < self.cfg.private_accuracy
        physical_success = candidate_correct and self._owns_prereqs(p, module)
        self.events.append({"kind": "private_physical_test", "season": self.season, "person": p.ident,
                            "module": module, "candidate_correct": candidate_correct,
                            "prerequisites_present": self._owns_prereqs(p, module), "success": physical_success})
        if physical_success:
            parameter = f"{self.context}:{module}:theta"
            self._record_receipt(p, module, parameter, "physical_innovation", private_outcome=True)
            self.innovations += 1
        else:
            self.physical_failures += 1

    def copy_step(self, pupil: Person, donor: Person, module: str) -> bool:
        donor_rid = donor.receipts[module]
        if (self.remaining[pupil.ident] <= 0 or self.remaining[donor.ident] <= 0 or
                pupil.energy + 1e-12 < self.cfg.work_cost or donor.energy + 1e-12 < self.cfg.work_cost):
            return False
        self.spend(pupil); self.spend(donor)
        assert self.charge(pupil, self.cfg.work_cost) and self.charge(donor, self.cfg.work_cost)
        parameter = self.receipts[donor_rid]["module_parameter"]
        self._record_receipt(pupil, module, parameter, "paid_copy", donor, donor_rid, fidelity=1.0)
        self.copies += 1
        return True

    def donor_for(self, pupil: Person) -> tuple[Person, str] | None:
        candidates: list[tuple[float, Person, str]] = []
        for donor_id in self.snapshot:
            if donor_id == pupil.ident or donor_id not in self.people:
                continue
            donor = self.people[donor_id]
            for module in donor.receipts:
                if module not in pupil.receipts and self.remaining.get(donor_id, 0) > 0:
                    candidates.append((uniform("donor", self.seed, self.season, pupil.ident, donor_id, module), donor, module))
        return min(candidates, default=None, key=lambda x: x[0])[1:] if candidates else None

    def maybe_recombine(self, p: Person) -> None:
        if set(p.receipts) != set(MODULES) or p.program_roots:
            return
        roots = tuple(sorted({self.receipts[rid]["source_innovation_root"] for rid in p.receipts.values()}))
        p.program_roots = roots
        if len(roots) > 1:
            self.recombinations += 1
            self.events.append({"kind": "recombination", "season": self.season, "person": p.ident,
                                "module_receipt_ids": [p.receipts[m] for m in MODULES], "source_roots": list(roots),
                                "note": "ledger event only; final paid module acquisition created no free skill"})

    def actions(self) -> None:
        # First reserve a real harvest opportunity for each active person.  Further
        # actions cannot use more than their central allocation.
        for ident in self.snapshot:
            if ident in self.people and self.remaining[ident]:
                self.harvest(self.people[ident], full=False)
        allow_copy = self.arm in {"transmission_innovation_retention", "causal_prerequisite_scramble"}
        allow_innovation = self.arm in {"transmission_innovation_retention", "private_only", "causal_prerequisite_scramble", "no_retention"}
        while any(self.remaining.values()):
            made = False
            for ident in self.snapshot:
                if ident not in self.people or self.remaining[ident] <= 0:
                    continue
                p = self.people[ident]
                if set(p.receipts) == set(MODULES):
                    self.harvest(p, full=True); made = True; continue
                if allow_copy:
                    target = self.donor_for(p)
                    if target is not None and self.copy_step(p, target[0], target[1]):
                        self.maybe_recombine(p); made = True; continue
                if allow_innovation and p.energy >= self.cfg.work_cost:
                    self.private_step(p); self.maybe_recombine(p); made = True; continue
                # Paid, nonproductive physical attempt prevents invented time or energy.
                self.harvest(p, full=False); made = True
            if not made:
                break
        assert all(self.used[i] <= self.allocated[i] <= self.cfg.time_cap for i in self.snapshot)

    def finish(self) -> dict[str, Any]:
        for ident in self.snapshot:
            if ident not in self.people:
                continue
            p = self.people[ident]
            if p.age >= self.cfg.maturity and p.energy >= self.cfg.birth_cost and uniform("birth", self.seed, self.season, ident) < self.cfg.birth_probability:
                if len(self.people) + 1 > self.cfg.population_cap:
                    self.status = "cap_censored"
                    break
                p.energy -= self.cfg.birth_cost
                self.sinks += self.cfg.birth_cost - self.cfg.newborn_energy
                cid = f"{ident}/b{self.season}"
                self.people[cid] = Person(cid, energy=self.cfg.newborn_energy, parent=ident)
                self.births += 1
                self.events.append({"kind": "birth", "season": self.season, "parent": ident, "child": cid,
                                    "genetic_parent_id": ident, "cultural_receipts_inherited": 0,
                                    "energy_debit": self.cfg.birth_cost, "newborn_energy": self.cfg.newborn_energy})
        if self.arm == "no_retention":
            # Explicit learned-state ablation: exact same sensors and work hardware,
            # but no receipt or private-progress state survives a season.
            for p in self.people.values():
                p.receipts.clear(); p.private_progress.clear(); p.program_roots = ()
            self.events.append({"kind": "retention_clear", "season": self.season})
        if not self.people:
            self.status = "extinct"
        stock = self.resource + sum(p.energy for p in self.people.values())
        residual = self.initial + self.regenerated - self.sinks - stock
        assert abs(residual) < 1e-7, residual
        assert self.n_before + self.births - self.b_before - (self.deaths - self.d_before) - (self.removals - self.r_before) == len(self.people)
        assert self.resource >= -1e-10 and all(p.energy >= -1e-10 for p in self.people.values())
        row = {"season": self.season, "N": len(self.people), "F": sum(p.age < self.cfg.maturity for p in self.people.values()),
               "A": sum(p.age >= self.cfg.maturity for p in self.people.values()), "resource": self.resource,
               "stock": stock, "residual": residual, "offered": self.offered, "realized": sum(self.used.values()),
               "max_person_work": max(self.used.values(), default=0), "births": self.births - self.b_before,
               "deaths": self.deaths - self.d_before, "removals": self.removals - self.r_before,
               "innovations": self.innovations, "copies": self.copies,
               "functional_people": sum(set(p.receipts) == set(MODULES) for p in self.people.values())}
        self.history.append(row)
        return row

    def result(self) -> dict[str, Any]:
        return {"seed": self.seed, "arm": self.arm, "status": self.status if self.status != "running" else "complete_horizon",
                "population": len(self.people), "mean_population": sum(r["N"] for r in self.history) / len(self.history),
                "functional": sum(set(p.receipts) == set(MODULES) for p in self.people.values()),
                "knowledge_items": sum(len(p.receipts) for p in self.people.values()), "work": self.total_work,
                "births": self.births, "deaths": self.deaths, "removals": self.removals,
                "innovations": self.innovations, "copies": self.copies, "recombinations": self.recombinations,
                "modifications": self.modifications, "private_attempts": self.private_attempts,
                "physical_failures": self.physical_failures, "max_residual": max((abs(r["residual"]) for r in self.history), default=0.0),
                "max_person_work": max((r["max_person_work"] for r in self.history), default=0),
                "seasons_completed": len(self.history), "event_hash": sha256(repr(self.events).encode()).hexdigest(),
                "solo_private_minimum_work": len(MODULES) * self.cfg.discovery_work,
                "solo_lifetime_work_ceiling": self.cfg.lifespan * self.cfg.time_cap,
                "solo_harvest_reserved_energy": 8 + 1.5 * 8,
                "solo_required_maintenance_learning_energy": self.cfg.lifespan * self.cfg.maintenance + len(MODULES) * self.cfg.discovery_work * self.cfg.work_cost}


def run(seed: int, arm: str, cfg: Settings = Settings()) -> World:
    world = World(seed, arm, cfg)
    for season in range(cfg.horizon):
        world.begin(season)
        if not world.people:
            break
        world.allocate(len(world.snapshot) * cfg.time_cap)
        world.actions()
        world.finish()
        if world.status != "running":
            break
    return world


def pair(seed: int, cfg: Settings = Settings()) -> tuple[World, World]:
    """Independent populations with the same ex-ante feasible person-time offer."""
    shared = World(seed, "transmission_innovation_retention", cfg)
    independent = World(seed, "private_only", cfg)
    for season in range(cfg.horizon):
        shared.begin(season); independent.begin(season)
        if not shared.people or not independent.people:
            shared.status = independent.status = "work_infeasible"
            break
        offered = min(len(shared.snapshot), len(independent.snapshot)) * cfg.time_cap
        shared.allocate(offered); independent.allocate(offered)
        shared.actions(); independent.actions()
        a, b = shared.finish(), independent.finish()
        if a["realized"] != offered or b["realized"] != offered:
            shared.status = independent.status = "work_infeasible"
            break
        if shared.status != "running" or independent.status != "running":
            if shared.status == "running": shared.status = "paired_stop_other_arm"
            if independent.status == "running": independent.status = "paired_stop_other_arm"
            break
    return shared, independent


def heldout_two_edge_test(world: World) -> dict[str, Any]:
    """Paid source→B→C transfer of a real baseline object plus physical probes."""
    sources = [p for p in world.people.values() if set(p.receipts) == set(MODULES)]
    if not sources:
        return {"seed": world.seed, "status": "no_baseline_full_program", "edges": [], "physical_tests": []}
    source = sorted(sources, key=lambda p: p.ident)[0]
    # Keep the actual source person's live energy; recipients are explicitly blank.
    people = {"source": Person(source.ident, energy=source.energy, receipts=dict(source.receipts)),
              "B": Person("heldout_B", energy=8.0), "C": Person("heldout_C", energy=8.0)}
    edges: list[dict[str, Any]] = []
    energy_debits = {key: 0.0 for key in people}
    work = {key: 0 for key in people}
    current_time = {key: 0 for key in people}
    copied_parameters: dict[tuple[str, str], str] = {("source", module): world.receipts[source.receipts[module]]["module_parameter"] for module in MODULES}
    resource = world.cfg.resource_initial
    failures: list[str] = []
    for module in MODULES:
        for teacher_key, pupil_key in (("source", "B"), ("B", "C")):
            teacher, pupil = people[teacher_key], people[pupil_key]
            if module not in teacher.receipts:
                # A depleted or incomplete first edge is an observed failed
                # two-edge test, never grounds for inventing a donor object.
                failures.append("missing_transfer_source")
                continue
            if current_time[teacher_key] >= 4 or current_time[pupil_key] >= 4:
                # Start the next paid testing season with no free reset of energy.
                current_time = {key: 0 for key in people}
            if teacher.energy < world.cfg.work_cost or pupil.energy < world.cfg.work_cost:
                failures.append("insufficient_teacher_or_pupil_energy")
                continue
            teacher.energy -= world.cfg.work_cost; pupil.energy -= world.cfg.work_cost
            energy_debits[teacher_key] += world.cfg.work_cost; energy_debits[pupil_key] += world.cfg.work_cost
            current_time[teacher_key] += 1; current_time[pupil_key] += 1
            work[teacher_key] += 1; work[pupil_key] += 1
            from_rid = teacher.receipts[module]
            copied = f"heldout:{world.seed}:{teacher_key}:{pupil_key}:{module}"
            pupil.receipts[module] = copied
            copied_parameters[(pupil_key, module)] = copied_parameters[(teacher_key, module)]
            edges.append({"edge_id": copied, "from": teacher.ident, "to": pupil.ident, "module": module,
                          "source_receipt_id": from_rid, "fidelity": 1.0, "teacher_work": 1, "pupil_work": 1,
                          "teacher_energy_debit": world.cfg.work_cost, "pupil_energy_debit": world.cfg.work_cost})
    valid_order = ("m1", "m0", "m3", "m2", "m5", "m4", "m6", "m7")
    seen: set[str] = set()
    order_prerequisites_hold = True
    for module in valid_order:
        order_prerequisites_hold = order_prerequisites_hold and set(world.prereqs[module]).issubset(seen)
        seen.add(module)
    parameters_hold = all(copied_parameters.get(("C", module)) == f"{world.context}:{module}:theta" for module in MODULES)
    valid = set(people["C"].receipts) == set(MODULES) and not failures and order_prerequisites_hold and parameters_hold
    physical_tests: list[dict[str, Any]] = []
    for name, order, parameter_error in (("unseen_valid_parallel_order", valid_order, False), ("prerequisite_violation", ("m7",), False), ("parameter_error", valid_order, True)):
        if current_time["C"] >= 4:
            current_time = {key: 0 for key in people}
        if people["C"].energy < world.cfg.work_cost:
            failures.append("insufficient_test_executor_energy")
            physical_tests.append({"name": name, "order": list(order), "valid": False, "resource_request": 0.0, "physical_performance": "not_run_insufficient_energy", "work": 0, "energy_debit": 0.0})
            continue
        people["C"].energy -= world.cfg.work_cost; energy_debits["C"] += world.cfg.work_cost
        current_time["C"] += 1; work["C"] += 1
        trial_seen: set[str] = set()
        prereq_ok = True
        for module in order:
            prereq_ok = prereq_ok and set(world.prereqs[module]).issubset(trial_seen)
            trial_seen.add(module)
        parameter_ok = not parameter_error and all(copied_parameters.get(("C", module)) == f"{world.context}:{module}:theta" for module in order)
        success = valid and prereq_ok and parameter_ok and tuple(order) == valid_order
        request = world.cfg.full_harvest_resources if success else 0.0
        drawn = min(resource, request); resource -= drawn
        people["C"].energy += world.cfg.conversion * drawn
        physical_tests.append({"name": name, "order": list(order), "valid": success, "resource_request": request,
                               "resource_drawn": drawn, "physical_performance": "success" if success else "failure",
                               "work": 1, "energy_debit": world.cfg.work_cost, "energy_credit": world.cfg.conversion * drawn,
                               "prerequisites_hold": prereq_ok, "parameters_hold": parameter_ok})
    return {"seed": world.seed, "status": "passed" if valid else "failed_paid_transfer", "source_person_id": source.ident,
            "source_is_baseline_acquired": True, "blank_recipients": True, "edges": edges, "work": work,
            "energy_debits": energy_debits, "physical_tests": physical_tests, "failures": failures,
            "two_actual_paid_edges_per_module": sum(e["from"] == source.ident and e["to"] == "heldout_B" for e in edges) == 8 and sum(e["to"] == "heldout_C" for e in edges) == 8}
