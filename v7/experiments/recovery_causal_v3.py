"""R3: randomized visible role labels and acquired-state adult diagnostics."""
from __future__ import annotations
from dataclasses import asdict
from hashlib import sha256
from math import log
from typing import Any
from v7.experiments.corrected_model import CorrectedEcologyRun
from v7.experiments.model import KeyedRNG, OrdinarySocialPolicy, PolicyDecision, PolicyObservation
from v7.experiments.run_experiments import _regime

SEEDS=tuple(range(83201,83225)); ADULT_SEEDS=tuple(range(84101,84125)); REGIMES=(1,5,9); TAU=5; ACC=.8
def key(value:object)->str:return sha256(repr(value).encode()).hexdigest()
def amend(obs:PolicyObservation,**change:Any)->PolicyObservation:return PolicyObservation(**{**asdict(obs),**change})
def decide(obs:PolicyObservation,dp:float,dl:float,stream:str)->PolicyDecision:return OrdinarySocialPolicy(dp,dl,tau=TAU).decide(obs,128,KeyedRNG('r3',stream,obs.season))

class LabelRecorder(OrdinarySocialPolicy):
    """Adds a real randomized role-label message before the live policy sees it."""
    def __init__(self, sink:list[dict[str,Any]], dp:float=.5, dl:float=.5):super().__init__(dp,dl,tau=TAU);self.sink=sink
    def decide(self,obs:PolicyObservation,cap:int,rng:KeyedRNG)->PolicyDecision:
        label='authority' if KeyedRNG('r3-label',obs.identity,obs.season).draw('observation',entity=obs.identity,event_type='role-label')<.5 else 'peer'
        labelled=amend(obs,messages=tuple(obs.messages)+(('role_label',label),))
        out=super().decide(labelled,cap,rng)
        self.sink.append({'observation':labelled,'label':label,'live':out})
        return out
class LabelRun(CorrectedEcologyRun):
    def __init__(self,*args:Any,**kw:Any)->None:self.records:list[dict[str,Any]]=[];super().__init__(*args,**kw)
    def _make_policy(self,traits:tuple[tuple[str,float],...]=())->LabelRecorder:
        t=dict(traits);return LabelRecorder(self.records,t.get('d_procedure',.5),t.get('d_local',.5))

def juvenile(seed_regime:tuple[int,int])->dict[str,Any]:
    seed,regime=seed_regime;v=_regime(regime-1);args=dict(depth=int(v['depth']),chi=float(v['chi']),q_theta=float(v['q_theta']),verification_price=float(v['verification_price']),graph_variant=1,initial_traits={'d_procedure':.5,'d_local':.5},burn_in=60,measurement=120,label='recovery_causal_v3')
    live=LabelRun(seed,OrdinarySocialPolicy,**args);result=live.run();base=CorrectedEcologyRun(seed,OrdinarySocialPolicy,**args).run(); rows=[]
    counters={'all_decisions':len(live.records),'actual_purchase_requests':0,'actual_no_teacher':0,'actual_conflicts':0}
    for i,record in enumerate(live.records):
        obs:PolicyObservation=record['observation']; d_live:PolicyDecision=record['live']; counters['actual_purchase_requests']+=int(bool(d_live.information_action));counters['actual_no_teacher']+=int(obs.advice is None);counters['actual_conflicts']+=int(d_live.conflict)
        if obs.age>=TAU or obs.advice is None:continue
        # Assigned label was actually passed into the live typed observation. The
        # paired swapped label is an otherwise identical decision counterfactual.
        for label in ('peer','authority'):
            labelled=amend(obs,messages=tuple((m for m in obs.messages if m[0]!='role_label'))+(('role_label',label),))
            for trait,dp,dl in (('d0',0.,0.),('applicable_dhalf',.5 if obs.domain=='procedure' else 0.,.5 if obs.domain=='local' else 0.)):
                # Holding this stream fixed across the two labels makes a label
                # contrast immune to an independent override draw.
                d=decide(labelled,dp,dl,f'{seed}:{regime}:{i}:{trait}')
                rows.append({'assay':'juvenile_role_label','seed':seed,'regime':regime,'opportunity_id':i,'assigned_label':record['label'],'tested_label':label,'label_was_live_assigned':label==record['label'],'role_label_visible_message':labelled.messages[-1],'age':obs.age,'domain':obs.domain,'trait':trait,'d_procedure':dp,'d_local':dl,'B':obs.beliefs,'K':obs.procedures,'T':obs.trust,'H':obs.habits,'message_without_label':tuple(m for m in labelled.messages if m[0]!='role_label'),'source_history':obs.source_history,'common_override_rng_stream':f'{seed}:{regime}:{i}:{trait}','private_hardware_accuracy':.8,'actual_replay_digest':result['replay_digest'],'unobserved_replay_digest':base['replay_digest'],'passive_digest_parity':result['replay_digest']==base['replay_digest'],'counterfactual_projected_cost':d.charged_cost,'counterfactual_projected_operations':d.operation_count,'counterfactual_purchase_request':bool(d.information_action),'world_loss_operations_repeated_total':live.losses['operations'],'world_loss_teaching_repeated_total':live.losses['teaching'],'world_material_resource_used_repeated_total':live.initial_total_stock-live.resource-sum(p.energy for p in live.population.values()),'actual_all_decision_count':counters['all_decisions'],'actual_purchase_requests_counter':counters['actual_purchase_requests'],'actual_no_teacher_counter':counters['actual_no_teacher'],'actual_conflict_counter':counters['actual_conflicts'],'conflict':d.conflict,'override':d.override_applied,'chosen_action':d.chosen_action,'neutral_action':d.neutral_action,'pre_override_digest':d.pre_override_digest})
    if not rows:rows=[{'assay':'juvenile_absence','seed':seed,'regime':regime,'actual_replay_digest':result['replay_digest'],'unobserved_replay_digest':base['replay_digest'],'passive_digest_parity':result['replay_digest']==base['replay_digest'],'absence_reason':'no age<5 teacher-present observation','actual_all_decision_count':counters['all_decisions'],'actual_purchase_requests_counter':counters['actual_purchase_requests'],'actual_no_teacher_counter':counters['actual_no_teacher'],'actual_conflict_counter':counters['actual_conflicts']}]
    return {'rows':rows,'parity':result['replay_digest']==base['replay_digest']}

def posterior(p:float,signal:int)->float:
    odds=p/max(1e-12,1-p);ratio=ACC/(1-ACC);odds*=ratio if signal else 1/ratio;return odds/(1+odds)
def training(seed:int,trait:str)->tuple[dict[str,Any],list[dict[str,Any]]]:
    """Forty paid stochastic episodes from empty K/H; all draws are keyed."""
    B=.5;K=0.;H=0.;T=.5;material=8.;trace=[];dp=.5 if trait=='dhalf' else 0.
    for e in range(1,41):
        rng=KeyedRNG(str(seed),'r3-training',e);truth=int(rng.draw('environment',entity='truth')>=.5);private=truth if rng.draw('observation',entity='private',event_type='private-signal')<ACC else 1-truth;adv_acc=.70;advice=truth if rng.draw('observation',entity='tutor',event_type='advice')<adv_acc else 1-truth;conflict=private!=advice;follow=conflict and rng.draw('override',entity=trait,event_type='juvenile-conflict')<dp;action=advice if follow else private;success=action==truth;practice_cost=.10;receipt=1. if success else -1.;approval=.10 if action==advice else 0.;material+=receipt-practice_cost;B=posterior(B,private);T=(4*T+float(advice==truth))/5
        # K only changes after a paid, successful physical procedural episode.
        if success and rng.draw('innovation',entity='practice',event_type='procedural-store')<.35:K=1.
        H=max(-1.,min(1.,.85*H+.15*(receipt+approval)))
        trace.append({'assay':'adult_training','seed':seed,'trait':trait,'episode':e,'truth':truth,'private_signal':private,'private_accuracy':ACC,'advice':advice,'advice_reliability':adv_acc,'conflict':conflict,'juvenile_override':follow,'action':action,'success':success,'B':B,'K':K,'H':H,'T':T,'practice_cost_debit':practice_cost,'material_receipt':receipt,'approval_receipt':approval,'material_ledger':material})
    return {'B':B,'K':K,'H':H,'T':T,'material':material,'history_digest':key(trace)},trace
def adult_updates(seed:int,trait:str,base:dict[str,Any],arm:str,direction:int)->list[dict[str,Any]]:
    B,K,H,T,material=(base[x] for x in ('B','K','H','T','material'));rows=[]; audience=arm!='audience_removal';free=arm=='free_audit';reliable=arm=='reliable_evidence'
    for step in range(1,21):
        rng=KeyedRNG(str(seed),f'r3-adult-{trait}-{arm}-{direction}',step); truth=int(direction>0);signal=truth if rng.draw('observation',entity='audit',event_type='adult-evidence')<ACC else 1-truth; prior=B;B=posterior(B,signal);audit=0. if free else .10; experienced_reward=1. if signal==truth else -1.; social=.05 if audience and experienced_reward>0 else 0.; material+=experienced_reward+social-audit; H=max(-1.,min(1.,.9*H+.1*(experienced_reward+social)));T=(4*T+float(signal==truth))/5 if reliable else T
        rows.append({'assay':'adult_acquired_arm','seed':seed,'trait':trait,'arm':arm,'evidence_direction':'supporting' if direction>0 else 'contrary','step':step,'cloned_training_history':base['history_digest'],'audience_present':audience,'free_audit':free,'reliable_evidence_feedback':reliable,'likelihood_strength':ACC,'direct_adult_inherited_override':0.,'rigidity_coefficient':None,'truth':truth,'signal':signal,'experienced_material_reward':experienced_reward,'B_prior':prior,'B_factual_belief':B,'K_acquired_procedure':K,'H_learned_action_value':H,'T_source_trust':T,'audit_debit':audit,'social_receipt':social,'material_ledger':material,'revision':abs(B-prior),'action':'act' if H>=0 else 'withhold'})
    return rows
