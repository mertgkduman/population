#!/usr/bin/env python3
"""Digest-checked passive corrected replays for the V7 offline dashboard.

The observer adds no random draw and never changes simulator/policy state.  It
only copies already-created public observations, decisions, outcomes, edges, and
aggregate person state, so this cache is a bounded derived view, not an experiment.
"""
from __future__ import annotations
import csv, gzip, hashlib, json, sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parent; OUT=ROOT/'experiments'/'output'/'corrected'
if str(ROOT.parent) not in sys.path: sys.path.insert(0,str(ROOT.parent))
from v7.experiments.corrected_model import CorrectedEcologyRun
from v7.experiments.run_corrected_experiments import run_cell
from v7.experiments.run_experiments import _policy_spec,_regime

VECTORS=('vector_0_0','vector_0_0_5','vector_0_1','vector_0_5_0','vector_0_5_0_5','vector_0_5_1','vector_1_0','vector_1_0_5','vector_1_1')
MAX_NODES,MAX_EDGES=150,300
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def amap(values:Any)->dict[str,float]:return {str(k):float(v) for k,v in values}

class PassiveCorrectedRun(CorrectedEcologyRun):
    """A passive observation wrapper for all founder and newborn policies."""
    def __init__(self,*args:Any,**kwargs:Any)->None:
        # This precedes super(): founders are created through _make_policy there.
        self._observer={'decisions':[],'focal':None,'pending':{},'edges':[],'nodes':{},'cohorts':[],'edge_events':[]}
        super().__init__(*args,**kwargs)
    def _node(self,identity:str,kind:str,birth_time:int|None=None)->None:
        nodes=self._observer['nodes']
        if identity not in nodes and len(nodes)<MAX_NODES:nodes[identity]={'id':identity,'kind':kind,'birth_time':birth_time,'blank_acquired_state_at_birth':kind=='newborn'}
    def _edge(self,source:str,target:str,kind:str,*,family:str|None=None,event:str|None=None)->None:
        if len(self._observer['edges'])>=MAX_EDGES:return
        self._node(source,'founder' if source.startswith('founder-') else 'newborn');self._node(target,'founder' if target.startswith('founder-') else 'newborn')
        self._observer['edges'].append({'source':source,'target':target,'type':kind,'season':self.season,'family':family,'event':event,'metadata':'not retained'})
    def _make_policy(self,traits:tuple[tuple[str,float],...]=())->Any:
        policy=super()._make_policy(traits)
        if getattr(policy,'_v7_dashboard_passive_wrapped',False):return policy
        original=policy.decide
        def observed_decide(obs:Any,cap:int,rng:Any,_original:Any=original)->Any:
            decision=_original(obs,cap,rng)
            record={'learner_id':obs.identity,'season':obs.season,'age':obs.age,'domain':obs.domain,'private_cue':obs.private_cue,'advice':obs.advice,'source_id':obs.source_id,'messages':[list(x) for x in obs.messages],'source_history':[list(x) for x in obs.source_history],'procedures_before':list(obs.procedures),'beliefs_before':amap(obs.beliefs),'trust_before':amap(obs.trust),'habits_before':amap(obs.habits),'q0_values':[list(x) for x in decision.q0_values],'neutral_action':decision.neutral_action,'chosen_action':decision.chosen_action,'conflict':decision.conflict,'override_applied':decision.override_applied,'charged_cost':decision.charged_cost,'operation_count':decision.operation_count,'agent_has_evaluator_truth':False,'evaluator_overlay':'theta/z evaluator-only; unavailable to policy'}
            self._observer['decisions'].append(record);self._observer['pending'][obs.identity]=record
            if self._observer['focal'] is None and obs.source_id and obs.age<self.TAU and decision.conflict:self._observer['focal']=record
            return decision
        policy.decide=observed_decide;policy._v7_dashboard_passive_wrapped=True
        return policy
    def _event(self,kind:str,**values:Any)->Any:
        event=super()._event(kind,**values)
        if kind in {'teaching','local_advice'} and values.get('teacher_id') and values.get('learner_id'):self._edge(str(values['teacher_id']),str(values['learner_id']),'cultural_contact',event=kind)
        elif kind=='birth' and event.biological_edge:self._edge(event.biological_edge[0],event.biological_edge[1],'biological_birth',event='birth')
        return event
    def _teach(self,teacher:Any,learner:Any,family:str)->str|None:
        offered=super()._teach(teacher,learner,family)
        if offered:self._observer['edge_events'].append({'kind':'procedure_offer','season':self.season,'teacher':teacher.identity,'learner':learner.identity,'family':family,'offered':offered})
        return offered
    def _local_message(self,teacher:Any,learner:Any,family:str)->None:
        super()._local_message(teacher,learner,family);self._observer['edge_events'].append({'kind':'local_recommendation','season':self.season,'teacher':teacher.identity,'learner':learner.identity,'family':family})
    def _finish(self,person:Any,payoff:float,physical:str,family:str,teacher:Any|None)->None:
        record=self._observer['pending'].pop(person.identity,None)
        if not record:return
        record.update({'physical_delayed_payoff':payoff,'physical_outcome':physical,'family':family,'teacher_present':teacher is not None,'beliefs_after':dict(person.B),'procedures_after':sorted(person.K),'trust_after':dict(person.T),'habits_after':dict(person.H)})
        if teacher is not None and len(person.K)>len(record['procedures_before']):self._edge(teacher.identity,person.identity,'guided_acquisition',family=family,event='positive_physical_K_addition')
    def _attempt(self,person:Any,family:str,sequence:str|None,from_teacher:Any|None,selected_branch:int|None=None)->float:
        payoff=super()._attempt(person,family,sequence,from_teacher,selected_branch);self._finish(person,payoff,'procedure_attempt',family,from_teacher);return payoff
    def _local_attempt(self,person:Any,family:str,choice:str,context:tuple[int,int,int],teacher:Any|None)->float:
        payoff=super()._local_attempt(person,family,choice,context,teacher);self._finish(person,payoff,'local_attempt',family,teacher);return payoff
    def advance_season(self)->Any:
        before={p.identity:p.age for p in self.population.values()};report=super().advance_season();people=list(self.population.values())
        self._observer['cohorts'].append({'season':report.season,'population':report.population_next,'births':report.births,'deaths':report.deaths,'adults':sum(p.age>=self.TAU for p in people),'juveniles':sum(p.age<self.TAU for p in people),'mean_age':sum(p.age for p in people)/max(1,len(people)),'mean_K':sum(len(p.K) for p in people)/max(1,len(people)),'mean_B':sum(sum(p.B.values())/max(1,len(p.B)) for p in people)/max(1,len(people)),'mean_T':sum(sum(p.T.values())/max(1,len(p.T)) for p in people)/max(1,len(people)),'mean_H':sum(sum(p.H.values())/max(1,len(p.H)) for p in people)/max(1,len(people)),'mean_energy':sum(p.energy for p in people)/max(1,len(people)),'source_use':sum(1 for r in self._observer['decisions'] if r['season']==report.season and r['source_id'] is not None),'matured':sum(1 for p in people if before.get(p.identity)==self.TAU-1 and p.age>=self.TAU),'stage_D_pre':sum(1 for age in before.values() if age<self.TAU)})
        for identity in self.population:self._node(identity,'founder' if identity.startswith('founder-') else 'newborn',report.season if identity not in before else None)
        return report
    def observed(self)->dict[str,Any]:
        fallback=next((r for r in self._observer['decisions'] if r['source_id']),None);focal=self._observer['focal'] or fallback
        return {'focal':focal,'focal_label':'teacher-present juvenile conflict' if self._observer['focal'] else 'actual teacher-present event; no juvenile conflict observed','nodes':list(self._observer['nodes'].values()),'edges':self._observer['edges'],'cohorts':self._observer['cohorts']}

def read_csv()->dict[tuple[int,str],dict[str,str]]:
    with gzip.open(OUT/'discovery.csv.gz','rt',newline='') as h:rows=list(csv.DictReader(h))
    return {(int(r['regime']),r['policy']):r for r in rows if int(r['seed'])==77001 and r['policy'] in VECTORS}
def job(regime:int,policy:str)->dict[str,Any]:return {**_regime(regime-1),'seed':77001,'policy':policy,'stage':'dashboard_observational_replay','graph_variant':0}
def run_one(item:tuple[int,str])->dict[str,Any]:
    regime,policy=item;spec=job(regime,policy);factory,traits=_policy_spec(policy)
    run=PassiveCorrectedRun(77001,factory,depth=spec['depth'],chi=spec['chi'],q_theta=spec['q_theta'],verification_price=spec['verification_price'],graph_variant=0,initial_traits=traits,label=policy);result=run.run()
    aggregate=[{'season':x.season,'population':x.population_next,'births':x.births,'deaths':x.deaths,'adults':x.adults,'newborns':x.newborns,'stored_knowledge':x.stored_knowledge,'resource':x.resource,'adult_evidence_accuracy':x.adult_evidence_accuracy,'teacher_time':x.teacher_time_debit,'learner_time':x.learner_time_debit} for x in run.reports]
    observed=run.observed()
    # The graph is a declared bounded representative subset, while all 81 cells
    # retain their actual cohort traces for click-through playback.
    if (regime,policy) not in {(1,'vector_0_0'),(5,'vector_0_5_0'),(9,'vector_1_1')}:
        observed['nodes']=[];observed['edges']=[]
    return {'regime':regime,'policy':policy,'seed':77001,'params':{k:spec[k] for k in ('depth','chi','q_theta','verification_price')},'summary':result,'series':aggregate,'observed':observed}
def main()->None:
    expected=read_csv();items=sorted(expected)
    with ProcessPoolExecutor(max_workers=4) as pool:values=list(pool.map(run_one,items,chunksize=1))
    for value in values:
        exp=expected[(value['regime'],value['policy'])]
        if value['summary']['replay_digest']!=exp['replay_digest'] or abs(value['summary']['mean_population']-float(exp['mean_population']))>1e-12 or abs(value['summary']['net_energy_per_agent_season']-float(exp['net_energy_per_agent_season']))>1e-12:raise RuntimeError(f"replay parity failed {value['regime']} {value['policy']}")
    plain=run_cell(job(1,'vector_0_0'));shadow=next(v for v in values if v['regime']==1 and v['policy']=='vector_0_0')['summary']
    if plain['replay_digest']!=shadow['replay_digest']:raise RuntimeError('passive observer changed replay digest')
    payload={'schema_version':2,'kind':'derived_observational_replays_not_primary_evidence','corrected_discovery_sha256':sha(OUT/'discovery.csv.gz'),'source_sha256':sha(Path(__file__)),'cells':values,'parity':{'cells':len(values),'seed':77001,'all_digest_and_summary_match':True,'unobserved_vs_observed_focal_digest':shadow['replay_digest']}}
    path=OUT/'dashboard_replays.json.gz'
    with gzip.open(path,'wt') as h:json.dump(payload,h,separators=(',',':'))
    print(json.dumps({'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path),'cells':len(values)}))
if __name__=='__main__':main()
