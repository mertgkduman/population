"""R1b v2: prospectively censored demographic accumulation sensitivity model.

Unlike the archived R1b pilot, this model never suppresses a birth to maintain a
fixed census.  A paid/reproducible attempted birth that would exceed the declared
operational cap records a cap event and stops with the existing population intact.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any

ARMS = ("transmission_innovation", "no_transmission", "equal_work_independent", "prerequisite_shuffle", "carrier_loss_storage_off", "carrier_loss_storage_on")
HORIZON, POP_CAP, START_POP = 18, 256, 8
PRIVATE_ACCURACY, WORK_BUDGET = .80, 4
PRIVATE_COST, TEACH_COST, STORAGE_WRITE, STORAGE_READ, STORAGE_MAINT = 1.0, .5, .5, .5, .1
def _u01(*parts: object) -> float: return int.from_bytes(sha256(repr(parts).encode()).digest()[:8],"big") / 2**64
@dataclass
class Person:
    ident: str; age: int=0; energy: float=5.; genes: float=1.; knowledge:set[str]=field(default_factory=set); parent:str|None=None; teacher:str|None=None
def prerequisites(shuffled: bool) -> dict[str, tuple[str,...]]:
    return {"prepare":(),"shape":("prepare",),"finish":("shape",)} if not shuffled else {"prepare":("shape",),"shape":(),"finish":("prepare",)}
def functional(k:set[str], graph:dict[str,tuple[str,...]]) -> bool: return all(x in k and set(req).issubset(k) for x,req in graph.items())

def run_cell(seed:int, arm:str, *, no_innovation_after_loss:bool=False, population_cap:int=POP_CAP, start_population:int=START_POP, birth_probability:float=.18) -> dict[str,Any]:
    if arm not in ARMS: raise ValueError("unregistered v2 arm")
    graph=prerequisites(arm=="prerequisite_shuffle"); people={f"founder-{i}":Person(f"founder-{i}") for i in range(start_population)}; storage:set[str]=set()
    work=private=teaching=write=read=maintenance=0.; innovations=transmissions=births=deaths=0; cap_events=0; cap_censored=False; removed=immediate=0; post_loss=None; loss_season=HORIZON//2
    for season in range(HORIZON):
        if season==loss_season and arm.startswith("carrier_loss"):
            carriers=[p for p in people.values() if p.knowledge]; removed=len(carriers); immediate=sum(len(p.knowledge) for p in carriers)
            for p in carriers: del people[p.ident]
            if arm=="carrier_loss_storage_off": storage.clear()
            post_loss=sum(len(p.knowledge) for p in people.values())+len(storage)
        for person in list(sorted(people.values(),key=lambda p:p.ident)):
            person.age+=1
            if person.energy<=0: del people[person.ident]; deaths+=1; continue
            remaining=WORK_BUDGET
            if arm=="carrier_loss_storage_on" and storage and remaining>=STORAGE_MAINT:
                person.energy-=STORAGE_MAINT; work+=STORAGE_MAINT; maintenance+=STORAGE_MAINT; remaining-=STORAGE_MAINT
            missing=[x for x,req in graph.items() if x not in person.knowledge and set(req).issubset(person.knowledge)]
            donor=next((q for q in people.values() if q.ident!=person.ident and q.knowledge),None)
            if arm in {"transmission_innovation","prerequisite_shuffle","carrier_loss_storage_on"} and donor and missing and remaining>=TEACH_COST:
                item=next((x for x in missing if x in donor.knowledge),None)
                if item is not None:
                    person.knowledge.add(item); person.teacher=donor.ident; person.energy-=TEACH_COST; donor.energy-=TEACH_COST; work+=2*TEACH_COST; teaching+=2*TEACH_COST; remaining-=TEACH_COST; transmissions+=1
            if arm=="carrier_loss_storage_on" and missing and remaining>=STORAGE_READ:
                item=next((x for x in missing if x in storage),None)
                if item is not None: person.knowledge.add(item); person.energy-=STORAGE_READ; work+=STORAGE_READ; read+=STORAGE_READ; remaining-=STORAGE_READ
            missing=[x for x,req in graph.items() if x not in person.knowledge and set(req).issubset(person.knowledge)]
            if missing and remaining>=PRIVATE_COST and not(no_innovation_after_loss and season>=loss_season and arm.startswith("carrier_loss")):
                item=missing[0]; person.energy-=PRIVATE_COST; work+=PRIVATE_COST; private+=PRIVATE_COST; remaining-=PRIVATE_COST
                if _u01("innovation",seed,season,person.ident,item)<PRIVATE_ACCURACY:
                    person.knowledge.add(item); innovations+=1
                    if arm=="carrier_loss_storage_on": person.energy-=STORAGE_WRITE; work+=STORAGE_WRITE; write+=STORAGE_WRITE; storage.add(item)
            person.energy += 2. if functional(person.knowledge,graph) else .65
            if person.age>=3 and person.energy>=8 and _u01("birth",seed,season,person.ident)<birth_probability:
                # The birth event is feasible until it would exceed the operational
                # cap.  At that prospective event we record/stop; no agent is
                # deleted/replaced and no fixed census is maintained.
                if len(people)+1 > population_cap:
                    cap_events+=1; cap_censored=True; break
                person.energy-=3.; child=Person(f"child-{season}-{person.ident}",parent=person.ident,genes=person.genes); people[child.ident]=child; births+=1
        if cap_censored or not people: break
    return {"seed":seed,"arm":arm,"horizon":HORIZON,"population_cap":population_cap,"private_accuracy":PRIVATE_ACCURACY,"population":len(people),"status":"cap_censored" if cap_censored else ("extinct" if not people else "complete_horizon"),"cap_events":cap_events,"births":births,"deaths":deaths,"functional_people":sum(functional(p.knowledge,graph) for p in people.values()),"knowledge_items":sum(len(p.knowledge) for p in people.values()),"innovations":innovations,"transmissions":transmissions,"work_paid":round(work,6),"private_work":private,"teaching_work":teaching,"storage_write_work":write,"storage_read_work":read,"storage_maintenance_work":maintenance,"biological_carriers":len(people),"cultural_carriers":sum(bool(p.knowledge) for p in people.values()),"removed_carriers":removed,"immediate_knowledge_loss":immediate,"knowledge_immediately_after_loss":post_loss,"knowledge_end":sum(len(p.knowledge) for p in people.values())+len(storage),"storage_items_end":len(storage),"blank_newborn_inheritance":all(not p.knowledge for p in people.values() if p.parent is not None and p.age==0),"no_innovation_after_loss":no_innovation_after_loss,"claim_limit":"R1b v2 bounded demographic sensitivity; finite horizon/cap, not long-run growth, selection, or primary IBM."}
