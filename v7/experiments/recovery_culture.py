"""R1b minimal demographic cultural-accumulation sensitivity model.

This is an additional coupled model, not a replacement for corrected V7 ecology.
Blank newborns inherit a genetic learning rate only; procedures are acquired through
paid private trials, paid teaching, or explicitly paid durable storage.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any

ARMS = ("transmission_innovation", "no_transmission", "equal_work_independent",
        "prerequisite_shuffle", "carrier_loss_storage_off", "carrier_loss_storage_on")
HORIZON, POP_CAP, START_POP = 18, 40, 8
PRIVATE_ACCURACY, WORK_BUDGET = .80, 4
PRIVATE_COST, TEACH_COST, STORAGE_WRITE, STORAGE_READ, STORAGE_MAINT = 1.0, .5, .5, .5, .1

def _u01(*parts: object) -> float:
    return int.from_bytes(sha256(repr(parts).encode()).digest()[:8], "big") / 2**64

@dataclass
class Person:
    ident: str
    age: int = 0
    energy: float = 5.0
    genes: float = 1.0
    knowledge: set[str] = field(default_factory=set)
    parent: str | None = None
    teacher: str | None = None

def prerequisites(shuffled: bool) -> dict[str, tuple[str, ...]]:
    # Functional causal modules; shuffled is a viable different dependency graph,
    # not an invalid recipe.  Final production requires all three modules.
    return {"prepare": (), "shape": ("prepare",), "finish": ("shape",)} if not shuffled else {"prepare": ("shape",), "shape": (), "finish": ("prepare",)}

def functional(knowledge: set[str], graph: dict[str, tuple[str, ...]]) -> bool:
    return all(name in knowledge and set(req).issubset(knowledge) for name, req in graph.items())

def run_cell(seed: int, arm: str, *, no_innovation_after_loss: bool = False) -> dict[str, Any]:
    if arm not in ARMS: raise ValueError("unregistered recovery culture arm")
    graph = prerequisites(arm == "prerequisite_shuffle")
    people = {f"founder-{i}": Person(f"founder-{i}") for i in range(START_POP)}
    storage: set[str] = set(); work = private = teaching = write = read = maintenance = 0.0
    innovations = transmissions = births = deaths = 0; removed_carriers = 0; immediate_loss = 0
    loss_season = HORIZON // 2; post_loss_count = None
    for season in range(HORIZON):
        if season == loss_season and arm.startswith("carrier_loss"):
            carriers = [p for p in people.values() if p.knowledge]
            removed_carriers = len(carriers)
            immediate_loss = sum(len(p.knowledge) for p in carriers)
            for p in carriers: del people[p.ident]
            if arm == "carrier_loss_storage_off": storage.clear()
            post_loss_count = sum(len(p.knowledge) for p in people.values()) + len(storage)
        for person in list(sorted(people.values(), key=lambda p: p.ident)):
            person.age += 1
            if person.energy <= 0: del people[person.ident]; deaths += 1; continue
            remaining = WORK_BUDGET
            # Storage maintenance is separately costed, and unavailable in off arms.
            if arm == "carrier_loss_storage_on" and storage and remaining >= STORAGE_MAINT:
                person.energy -= STORAGE_MAINT; work += STORAGE_MAINT; maintenance += STORAGE_MAINT; remaining -= STORAGE_MAINT
            # Each person solves independently in equal-work/no-transmission arms;
            # no pooled budget or knowledge transfer exists.
            missing = [x for x, req in graph.items() if x not in person.knowledge and set(req).issubset(person.knowledge)]
            donor = next((q for q in people.values() if q.ident != person.ident and q.knowledge), None)
            if arm in {"transmission_innovation", "prerequisite_shuffle", "carrier_loss_storage_on"} and donor and missing and remaining >= TEACH_COST:
                candidate = next((x for x in missing if x in donor.knowledge), None)
                if candidate is not None:
                    person.knowledge.add(candidate); person.teacher = donor.ident; person.energy -= TEACH_COST; donor.energy -= TEACH_COST
                    work += 2 * TEACH_COST; teaching += 2 * TEACH_COST; remaining -= TEACH_COST; transmissions += 1
            if arm == "carrier_loss_storage_on" and missing and remaining >= STORAGE_READ:
                candidate = next((x for x in missing if x in storage), None)
                if candidate is not None:
                    person.knowledge.add(candidate); person.energy -= STORAGE_READ; work += STORAGE_READ; read += STORAGE_READ; remaining -= STORAGE_READ
            missing = [x for x, req in graph.items() if x not in person.knowledge and set(req).issubset(person.knowledge)]
            can_innovate = not (no_innovation_after_loss and season >= loss_season and arm.startswith("carrier_loss"))
            if missing and remaining >= PRIVATE_COST and can_innovate:
                candidate = missing[0]; person.energy -= PRIVATE_COST; work += PRIVATE_COST; private += PRIVATE_COST; remaining -= PRIVATE_COST
                if _u01("innovation", seed, season, person.ident, candidate) < PRIVATE_ACCURACY:
                    person.knowledge.add(candidate); innovations += 1
                    if arm == "carrier_loss_storage_on":
                        person.energy -= STORAGE_WRITE; work += STORAGE_WRITE; write += STORAGE_WRITE; storage.add(candidate)
            person.energy += 2.0 if functional(person.knowledge, graph) else .65
            if person.age >= 3 and person.energy >= 8 and len(people) < POP_CAP and _u01("birth", seed, season, person.ident) < .18:
                person.energy -= 3; child = Person(f"child-{season}-{person.ident}", parent=person.ident, genes=person.genes)
                # Newborn is blank: no K, teacher and parent are separately logged.
                people[child.ident] = child; births += 1
        if not people: break
    functional_people = sum(functional(p.knowledge, graph) for p in people.values())
    return {"seed": seed, "arm": arm, "horizon": HORIZON, "population_cap": POP_CAP, "private_accuracy": PRIVATE_ACCURACY,
            "population": len(people), "births": births, "deaths": deaths, "functional_people": functional_people,
            "knowledge_items": sum(len(p.knowledge) for p in people.values()), "innovations": innovations, "transmissions": transmissions,
            "work_paid": round(work, 6), "private_work": private, "teaching_work": teaching, "storage_write_work": write,
            "storage_read_work": read, "storage_maintenance_work": maintenance, "biological_carriers": len(people),
            "cultural_carriers": sum(bool(p.knowledge) for p in people.values()), "removed_carriers": removed_carriers,
            "immediate_knowledge_loss": immediate_loss, "knowledge_immediately_after_loss": post_loss_count,
            "knowledge_end": sum(len(p.knowledge) for p in people.values()) + len(storage), "storage_items_end": len(storage),
            "blank_newborn_inheritance": all(not p.knowledge for p in people.values() if p.parent is not None and p.age == 0),
            "no_innovation_after_loss": no_innovation_after_loss,
            "claim_limit": "Minimal coupled demographic sensitivity model; bounded horizon/cap, no selection or primary-IBM replacement claim."}
