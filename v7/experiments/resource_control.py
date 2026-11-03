"""Closed-resource culture control; independent of immutable primary V7.

All gains are physical resource withdrawals. Central token reservations charge
teacher and pupil, and every individual retains a hard per-season work limit.
This tests ordinary skill transmission, not a separate authority adaptation.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from hashlib import sha256
import math

@dataclass(frozen=True)
class Settings:
    horizon: int = 60
    start_population: int = 10
    lifespan: int = 18
    maturity: int = 3
    time_cap: int = 4
    resource_cap: float = 800.
    resource_initial: float = 600.
    regeneration: float = .06
    conversion: float = .75
    maintenance: float = .5
    discovery_work: int = 8
    private_accuracy: float = .8
    work_cost: float = .2
    birth_cost: float = 6.
    newborn_energy: float = 4.
    birth_probability: float = .12
    population_cap: int = 256


def uniform(*key):
    return int.from_bytes(sha256(repr(key).encode()).digest()[:8], 'big') / 2**64

@dataclass
class Person:
    ident: str
    age: int = 0
    energy: float = 8.
    recipe: tuple[str, ...] = ()
    roots: tuple[str, ...] = ()
    progress: int = 0
    parent: str | None = None

class World:
    def __init__(self, seed, arm, cfg=Settings(), no_innovation=False):
        self.seed, self.arm, self.cfg, self.no_innovation = seed, arm, cfg, no_innovation
        self.people = {f'f{i}': Person(f'f{i}') for i in range(cfg.start_population)}
        self.resource = cfg.resource_initial
        self.initial = self.resource + sum(p.energy for p in self.people.values())
        self.regenerated = self.sinks = 0.
        self.births = self.deaths = self.removals = 0
        self.innovations = self.transmissions = self.probes = self.correct_cues = 0
        self.status = 'running'
        self.storage = {}
        self.history, self.acquisitions = [], []
        self.post_loss = None
        self.total_work = 0
        self.order = tuple(f'm{i}' for i in range(6))

    def charge(self, p, value):
        if value < 0 or p.energy + 1e-12 < value:
            return False
        p.energy -= value
        self.sinks += value
        return True

    def remove(self, ident, cause):
        p = self.people.pop(ident)
        assert p.energy >= -1e-10
        self.sinks += p.energy
        if cause == 'carrier': self.removals += 1
        else: self.deaths += 1

    def prefix_length(self, recipe):
        n = 0
        for a, b in zip(recipe, self.order):
            if a != b: break
            n += 1
        return n

    def begin(self, season):
        self.season = season
        self.n_before, self.b_before, self.d_before, self.r_before = len(self.people), self.births, self.deaths, self.removals
        addition = self.cfg.regeneration * (self.cfg.resource_cap - self.resource)
        assert addition >= -1e-9
        self.resource += addition; self.regenerated += addition
        for p in list(self.people.values()):
            p.age += 1
            self.charge(p, min(p.energy, self.cfg.maintenance))
            if p.energy <= 1e-12 or p.age > self.cfg.lifespan: self.remove(p.ident, 'death')
        if season == self.cfg.horizon // 2:
            if self.arm == 'prerequisite_scramble':
                self.order = ('m0','m2','m1','m3','m4','m5')
            if self.arm.startswith('carrier_loss'):
                for ident in [p.ident for p in self.people.values() if p.recipe]: self.remove(ident, 'carrier')
                if self.arm.endswith('off'): self.storage.clear()
                self.post_loss = sum(len(p.recipe) for p in self.people.values()) + sum(len(k) for k in self.storage)
        if self.arm.endswith('storage_on') and self.storage:
            cost = .1 * len(self.storage)
            if self.resource >= cost: self.resource -= cost; self.sinks += cost
            else: self.storage.clear()  # Unpowered storage becomes unavailable; no free surviving cache.
        self.snapshot = sorted(self.people)

    def allocate(self, offered):
        assert 0 <= offered <= len(self.people) * self.cfg.time_cap
        ids = sorted(self.people, key=lambda x: uniform('allocation',self.seed,self.season,x))
        self.remaining = {i: 0 for i in ids}; self.allocated = {i: 0 for i in ids}; self.used = {i: 0 for i in ids}
        for j in range(offered):
            ident = ids[j % len(ids)]
            self.remaining[ident] += 1; self.allocated[ident] += 1
        self.offered = offered

    def spend(self, p):
        assert self.remaining[p.ident] > 0
        self.remaining[p.ident] -= 1; self.used[p.ident] += 1; self.total_work += 1

    def produce(self, p):
        self.spend(p)
        full = len(p.recipe) == 6
        valid = self.prefix_length(p.recipe) == len(p.recipe)
        request = (4. if valid else 0.) if full else 2.
        drawn = min(self.resource, request)
        self.resource -= drawn; p.energy += self.cfg.conversion * drawn
        self.sinks += (1-self.cfg.conversion) * drawn
        if not valid:
            # A physical failure identifies the failed stage, not its correct alternative.
            n = self.prefix_length(p.recipe); p.recipe = p.recipe[:n]; p.roots = p.roots[:n]; p.progress = 0

    def acquire(self, p, recipe, roots, kind):
        p.recipe, p.roots = recipe, roots
        self.acquisitions.append({'season':self.season,'learner':p.ident,'recipe':list(recipe),'roots':list(roots),'kind':kind})
        if self.arm.endswith('storage_on') and recipe not in self.storage and self.remaining[p.ident] and p.energy >= self.cfg.work_cost:
            self.spend(p); assert self.charge(p,self.cfg.work_cost)
            self.storage[recipe] = roots

    def actions(self):
        # Reserve a real harvest first. No automatic knowledge income exists.
        for ident in self.snapshot:
            p = self.people[ident]
            if self.remaining[ident]: self.produce(p)
        can_transmit = self.arm not in {'no_transmission','independent'}
        for ident in self.snapshot:
            p = self.people[ident]
            while self.remaining[ident]:
                if len(p.recipe) == 6:
                    self.produce(p); continue
                target = len(p.recipe)
                donor = next((q for q in self.people.values()
                              if can_transmit and q.ident != ident and self.remaining.get(q.ident,0)>0
                              and len(q.recipe)>target and q.recipe[:target] == p.recipe
                              and q.energy >= self.cfg.work_cost and p.energy >= self.cfg.work_cost),None)
                if donor:
                    self.spend(p); self.spend(donor)
                    assert self.charge(p,self.cfg.work_cost) and self.charge(donor,self.cfg.work_cost)
                    self.acquire(p,donor.recipe[:target+1],donor.roots[:target+1],'teaching')
                    self.transmissions += 1; continue
                cached = next(((k,r) for k,r in self.storage.items() if k[:target] == p.recipe and len(k)>target),None)
                if self.arm.endswith('storage_on') and cached and p.energy >= self.cfg.work_cost:
                    self.spend(p); assert self.charge(p,self.cfg.work_cost)
                    self.acquire(p,cached[0][:target+1],cached[1][:target+1],'storage_read'); continue
                allowed = not (self.no_innovation and self.season >= self.cfg.horizon//2 and self.arm.startswith('carrier_loss'))
                if allowed and p.energy >= self.cfg.work_cost:
                    self.spend(p); assert self.charge(p,self.cfg.work_cost); p.progress += 1
                    if p.progress == self.cfg.discovery_work:
                        p.progress = 0; self.probes += 1
                        correct = uniform('private_cue',self.seed,self.season,ident,target) < self.cfg.private_accuracy
                        self.correct_cues += int(correct)
                        # Sensor proposes a stage; an actual physical test returns success/failure.
                        if correct:
                            recipe = p.recipe + (self.order[target],)
                            roots = p.roots + (f'private:{self.arm}:{self.seed}:{ident}:{self.season}:{target}',)
                            self.acquire(p,recipe,roots,'physical_discovery'); self.innovations += 1
                    continue
                # Equal-effort protocol may perform an unproductive safe attempt;
                # it consumes time even when resource is empty, never creates energy.
                self.produce(p)
        # A storage write has its own human token; no retroactive overrun.
        if self.arm.endswith('storage_on'):
            for ident in self.snapshot:
                p = self.people[ident]
                if p.recipe and p.recipe not in self.storage and self.remaining[ident] and p.energy >= self.cfg.work_cost:
                    self.spend(p); assert self.charge(p,self.cfg.work_cost)
                    self.storage[p.recipe] = p.roots
        assert all(self.used[i] <= self.allocated[i] <= self.cfg.time_cap for i in self.snapshot)

    def finish(self):
        for ident in self.snapshot:
            p = self.people[ident]
            if p.age >= self.cfg.maturity and p.energy >= 7 and uniform('birth',self.seed,self.season,ident)<self.cfg.birth_probability:
                if len(self.people) + 1 > self.cfg.population_cap:
                    self.status = 'cap_censored'; break
                p.energy -= self.cfg.birth_cost
                self.sinks += self.cfg.birth_cost-self.cfg.newborn_energy
                child_id = f'{ident}/b{self.season}'
                self.people[child_id] = Person(child_id,energy=self.cfg.newborn_energy,parent=ident)
                self.births += 1
        if not self.people: self.status = 'extinct'
        stock = self.resource + sum(p.energy for p in self.people.values())
        residual = self.initial + self.regenerated - self.sinks - stock
        assert abs(residual) < 1e-7, ('stock',residual)
        assert self.n_before+self.births-self.b_before-(self.deaths-self.d_before)-(self.removals-self.r_before) == len(self.people)
        assert all(p.energy>=-1e-10 for p in self.people.values()) and self.resource>=-1e-10
        assert self.births*(self.cfg.birth_cost-self.cfg.newborn_energy) <= self.initial+self.regenerated+1e-7
        row = {'season':self.season,'N':len(self.people),'F':sum(p.age<self.cfg.maturity for p in self.people.values()),
               'A':sum(p.age>=self.cfg.maturity for p in self.people.values()),'resource':self.resource,'stock':stock,
               'residual':residual,'offered':self.offered,'realized':sum(self.used.values()),
               'max_person_work':max(self.used.values(),default=0),'births':self.births-self.b_before,
               'deaths':self.deaths-self.d_before,'removals':self.removals-self.r_before}
        self.history.append(row)
        return row

    def result(self):
        return {'seed':self.seed,'arm':self.arm,'status':self.status if self.status!='running' else 'complete_horizon',
                'population':len(self.people),'mean_population':sum(r['N'] for r in self.history)/self.cfg.horizon,'loss_event_observed':self.post_loss is not None,'functional':sum(len(p.recipe)==6 and self.prefix_length(p.recipe)==6 for p in self.people.values()),
                'knowledge_items':sum(len(p.recipe) for p in self.people.values()),'work':self.total_work,
                'births':self.births,'deaths':self.deaths,'removals':self.removals,'private_probes':self.probes,
                'correct_cues':self.correct_cues,'innovations':self.innovations,'transmissions':self.transmissions,
                'post_loss_knowledge':self.post_loss,'storage_items':len(self.storage),
                'max_residual':max((abs(r['residual']) for r in self.history),default=0),
                'max_person_work':max((r['max_person_work'] for r in self.history),default=0),
                'seasons_completed':len(self.history),'lifetime_work_bound':self.cfg.lifespan*self.cfg.time_cap,
                'private_minimum_work':6*self.cfg.discovery_work,'private_learning_bound_with_harvest':self.cfg.lifespan*(self.cfg.time_cap-1)}

def run(seed,arm,cfg=Settings(),no_innovation=False):
    world = World(seed,arm,cfg,no_innovation)
    for t in range(cfg.horizon):
        world.begin(t); world.allocate(len(world.people)*cfg.time_cap); world.actions(); world.finish()
        if world.status!='running': break
    return world

def pair(seed,cfg=Settings()):
    a,b = World(seed,'transmission_innovation',cfg), World(seed,'independent',cfg)
    for t in range(cfg.horizon):
        a.begin(t); b.begin(t)
        offered = min(len(a.people),len(b.people))*cfg.time_cap
        a.allocate(offered); b.allocate(offered)
        a.actions(); b.actions(); ra,rb=a.finish(),b.finish()
        if ra['realized'] != offered or rb['realized'] != offered:
            a.status=b.status='work_infeasible'; break
        if a.status!='running' or b.status!='running':
            if a.status=='running': a.status='paired_stop_other_arm'
            if b.status=='running': b.status='paired_stop_other_arm'
            break
    return a,b
