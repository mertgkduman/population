"""R1b v3 finite-resource, paid-work cultural accumulation sensitivity."""
from __future__ import annotations
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any

ARMS=("transmission_innovation","no_transmission","prerequisite_scramble","carrier_loss_storage_off","carrier_loss_storage_on")
HORIZON, POP_CAP, START_POP, LIFESPAN, MATURITY, TIME_CAP = 60, 256, 10, 18, 3, 4
R_CAP, R0, REGEN, CONVERSION = 800., 600., .06, .75
PRIVATE_ACCURACY, DISCOVERY_WORK, COPY_WORK = .8, 8, 1
def u(*x:object)->float:return int.from_bytes(sha256(repr(x).encode()).digest()[:8],"big")/2**64
@dataclass
class P:
    ident:str; age:int=0; energy:float=8.; k:dict[str,tuple[str,...]]=field(default_factory=dict); roots:dict[str,str]=field(default_factory=dict); progress:dict[str,int]=field(default_factory=dict)
def order(scramble:bool)->tuple[str,...]:return ("m0","m2","m1","m3","m4","m5") if scramble else tuple(f"m{i}" for i in range(6))
def ready(p:P,world:tuple[str,...])->str|None:
    return next((m for m in world if m not in p.k and all(q in p.k for q in world[:world.index(m)])),None)
def functional(p:P,world:tuple[str,...])->bool:return tuple(p.k) == world and tuple(p.k.values())[-1] == world if len(p.k)==6 else False
def harvest(p:P, resource:float, draw:float)->tuple[float,float,float]:
    actual=min(resource,draw); gain=actual*CONVERSION; return resource-actual,gain,actual-gain

def run_cell(seed:int,arm:str,*,no_innovation_after_loss:bool=False,cap:int=POP_CAP)->dict[str,Any]:
    if arm not in ARMS:raise ValueError("unregistered v3 arm")
    world=order(arm=="prerequisite_scramble"); pop={f"founder-{i}":P(f"founder-{i}") for i in range(START_POP)}; storage:dict[str,tuple[tuple[str,...],str]]={}
    resource=R0; initial=resource+sum(p.energy for p in pop.values()); external=sinks=0.; births=deaths=removals=caps=0; innovations=transmissions=0; work=private=teach=read=write=maint=0; immediate_loss=post_loss=None; status="complete_horizon"; seasons=[]
    for season in range(HORIZON):
        regen=REGEN*(R_CAP-resource);resource+=regen;external+=regen; used={}; season_start=resource+sum(p.energy for p in pop.values())
        if season==HORIZON//2 and arm.startswith("carrier_loss"):
            carriers=[p for p in pop.values() if p.k]; immediate_loss=sum(len(p.k) for p in carriers)
            for p in carriers: sinks+=p.energy;del pop[p.ident];removals+=1
            if arm=="carrier_loss_storage_off":storage.clear()
            post_loss=sum(len(p.k) for p in pop.values())+len(storage)
        for p in list(sorted(pop.values(),key=lambda x:x.ident)):
            if p.ident not in pop:continue
            p.age+=1; charge=min(.5,p.energy); p.energy-=charge;sinks+=charge;maint+=charge
            if p.energy<=0 or p.age>LIFESPAN:sinks+=max(0.,p.energy);del pop[p.ident];deaths+=1;continue
            remaining=TIME_CAP-used.get(p.ident,0); target=ready(p,world)
            # Copy is paid on both sides and can only reserve not-yet-used teacher time.
            donor=next((q for q in sorted(pop.values(),key=lambda x:x.ident) if q.ident>p.ident and target in q.k and used.get(q.ident,0)<TIME_CAP),None)
            if arm in {"transmission_innovation","carrier_loss_storage_on"} and target and donor and remaining>=COPY_WORK:
                p.k[target]=donor.k[target];p.roots[target]=donor.roots[target];p.energy-=.2;donor.energy-=.2;sinks+=.4;used[p.ident]=used.get(p.ident,0)+1;used[donor.ident]=used.get(donor.ident,0)+1;remaining-=1;teach+=2;work+=2;transmissions+=1
            target=ready(p,world)
            if arm=="carrier_loss_storage_on" and target in storage and remaining>=1:
                p.k[target],p.roots[target]=storage[target];p.energy-=.2;sinks+=.2;used[p.ident]=used.get(p.ident,0)+1;remaining-=1;read+=1;work+=1
            target=ready(p,world)
            if target and not(no_innovation_after_loss and season>=HORIZON//2 and arm.startswith("carrier_loss")):
                available=remaining
                while available and p.progress.get(target,0)<DISCOVERY_WORK:
                    p.progress[target]=p.progress.get(target,0)+1;p.energy-=.2;sinks+=.2;available-=1;used[p.ident]=used.get(p.ident,0)+1;private+=1;work+=1
                if p.progress.get(target,0)>=DISCOVERY_WORK:
                    p.progress.pop(target); innovations+=1
                    if u("discovery",seed,p.ident,target,season)<PRIVATE_ACCURACY:
                        recipe=world[:world.index(target)+1];p.k[target]=recipe;p.roots[target]=f"innovation:{seed}:{p.ident}:{target}"
                        if arm=="carrier_loss_storage_on":storage[target]=(recipe,p.roots[target]);p.energy-=.2;sinks+=.2;write+=1;work+=1
            remaining=TIME_CAP-used.get(p.ident,0)
            # All energy gain is physical harvest from finite resource. A complete
            # causal recipe earns high yield; incomplete work earns only safe yield.
            resource,gain,loss=harvest(p,resource,4. if functional(p,world) else 2.);p.energy+=gain;sinks+=loss;used[p.ident]=used.get(p.ident,0)+1;work+=1
            if p.age>=MATURITY and p.energy>=7 and u("birth",seed,season,p.ident)<.12:
                if len(pop)+1>cap: caps+=1;status="cap_censored";break
                p.energy-=6;sinks+=2;child=P(f"child-{season}-{p.ident}",energy=4.);pop[child.ident]=child;births+=1
        stock=resource+sum(p.energy for p in pop.values()); residual=(initial+external-sinks)-stock
        seasons.append({"season":season,"population":len(pop),"resource":resource,"stock":stock,"residual":residual,"work":work,"births":births,"deaths":deaths,"removals":removals,"cap":status=="cap_censored"})
        if abs(residual)>1e-7:raise RuntimeError("resource-energy accounting failure")
        if status=="cap_censored" or not pop:status="extinct" if not pop else status;break
    return {"seed":seed,"arm":arm,"status":status,"horizon":HORIZON,"population_cap":cap,"private_accuracy":PRIVATE_ACCURACY,"lifetime_work_bound":LIFESPAN*TIME_CAP,"minimum_private_discovery_work":6*DISCOVERY_WORK,"population":len(pop),"resource":resource,"births":births,"deaths":deaths,"removals":removals,"cap_events":caps,"innovations":innovations,"transmissions":transmissions,"work":work,"private_work":private,"teaching_work":teach,"storage_read":read,"storage_write":write,"maintenance_sink":maint,"functional_people":sum(functional(p,world) for p in pop.values()),"knowledge_items":sum(len(p.k) for p in pop.values()),"root_origins":sorted({r for p in pop.values() for r in p.roots.values()}),"storage_items":len(storage),"immediate_loss":immediate_loss,"post_loss_knowledge":post_loss,"no_innovation_after_loss":no_innovation_after_loss,"max_residual":max((abs(s["residual"]) for s in seasons),default=0.),"seasons":seasons,"claim_limit":"Finite resource/accounting sensitivity only; no long-run selection or primary-model replacement."}
