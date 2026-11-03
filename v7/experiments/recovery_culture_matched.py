"""Fresh R1b paired matched-work control; populations never share knowledge."""
from __future__ import annotations
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any

HORIZON, START_POP, PERSON_CAP, POP_CAP = 18, 8, 4, 256
PRIVATE_ACCURACY = .80
def u(*x: object) -> float: return int.from_bytes(sha256(repr(x).encode()).digest()[:8], "big") / 2**64
@dataclass
class P:
    ident: str; age: int = 0; energy: float = 5.; k: set[str] = field(default_factory=set)
def graph() -> dict[str, tuple[str, ...]]: return {"prepare": (), "shape": ("prepare",), "finish": ("shape",)}
def complete(p: P) -> bool: return all(x in p.k and set(req).issubset(p.k) for x, req in graph().items())
def allocate(pop: dict[str, P], total: int) -> dict[str, int]:
    left, out = total, {}
    for ident in sorted(pop):
        out[ident] = min(PERSON_CAP, left); left -= out[ident]
    if left: raise RuntimeError("offered effort exceeds individual feasible capacity")
    return out

def step(pop: dict[str, P], *, transmit: bool, seed: int, season: int, offered: int) -> dict[str, Any]:
    if offered > len(pop) * PERSON_CAP: raise RuntimeError("infeasible offered work")
    budgets = allocate(pop, offered); private = teach = safe = 0.; innovations = transmissions = births = deaths = 0; cap = False
    for person in list(sorted(pop.values(), key=lambda x: x.ident)):
        person.age += 1; remaining = budgets.get(person.ident, 0)
        if person.energy <= 0: del pop[person.ident]; deaths += 1; continue
        need = [x for x, req in graph().items() if x not in person.k and set(req).issubset(person.k)]
        # Teachers are drawn only from not-yet-processed people with reserved
        # capacity, so a teaching debit never rewrites work already realized.
        donor = next((q for q in sorted(pop.values(), key=lambda x: x.ident)
                      if q.ident > person.ident and q.k and budgets.get(q.ident, 0) >= 1), None)
        if transmit and donor and need and remaining >= 1 and budgets.get(donor.ident, 0) >= 1:
            item = next((x for x in need if x in donor.k), None)
            if item is not None:
                person.k.add(item); person.energy -= .5; donor.energy -= .5; remaining -= 1; budgets[donor.ident] -= 1; teach += 2; transmissions += 1
        need = [x for x, req in graph().items() if x not in person.k and set(req).issubset(person.k)]
        if need and remaining >= 1:
            item = need[0]; person.energy -= 1; remaining -= 1; private += 1
            if u("m-innovation", seed, season, person.ident, item) < PRIVATE_ACCURACY: person.k.add(item); innovations += 1
        # Residual individually allocated work is identical charged safe production.
        safe += remaining; person.energy += .15 * remaining
        person.energy += 2. if complete(person) else .65
        if person.age >= 3 and person.energy >= 8 and u("m-birth", seed, season, person.ident) < .18:
            if len(pop) + 1 > POP_CAP: cap = True; break
            person.energy -= 3; pop[f"child-{season}-{person.ident}"] = P(f"child-{season}-{person.ident}"); births += 1
    return {"private": private, "teaching": teach, "safe": safe, "realized": private + teach + safe, "innovations": innovations, "transmissions": transmissions, "births": births, "deaths": deaths, "cap": cap}

def run_pair(seed: int) -> dict[str, Any]:
    ti = {f"founder-{i}": P(f"founder-{i}") for i in range(START_POP)}; independent = {f"founder-{i}": P(f"founder-{i}") for i in range(START_POP)}; seasons = []; status = "complete_horizon"
    for season in range(HORIZON):
        offered = min(len(ti) * PERSON_CAP, len(independent) * PERSON_CAP)
        a = step(ti, transmit=True, seed=seed, season=season, offered=offered); b = step(independent, transmit=False, seed=seed, season=season, offered=offered)
        seasons.append({"season": season, "offered_work": offered, "ti_realized": a["realized"], "independent_realized": b["realized"], "ti_population": len(ti), "independent_population": len(independent), "ti_infeasible": a["realized"] != offered, "independent_infeasible": b["realized"] != offered})
        if a["cap"] or b["cap"]: status = "cap_censored"; break
        if not ti and not independent: status = "both_extinct"; break
        if not ti or not independent: status = "one_arm_extinct"; break
    arm = lambda pop, n: {f"{n}_population": len(pop), f"{n}_functional": sum(complete(x) for x in pop.values()), f"{n}_knowledge": sum(len(x.k) for x in pop.values())}
    return {"seed": seed, "horizon": HORIZON, "person_work_cap": PERSON_CAP, "population_cap": POP_CAP, "status": status, "seasons": seasons, "offered_work_total": sum(x["offered_work"] for x in seasons), "ti_realized_work": sum(x["ti_realized"] for x in seasons), "independent_realized_work": sum(x["independent_realized"] for x in seasons), "any_infeasible": any(x["ti_infeasible"] or x["independent_infeasible"] for x in seasons), **arm(ti, "ti"), **arm(independent, "independent"), "claim_limit": "Paired shared-effort intervention; independent populations, not competition or outcome/knowledge sharing."}
