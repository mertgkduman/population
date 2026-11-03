"""Coherent fixed-proposition learning and inherited juvenile override control.

Training truth is fixed within a history. Posterior log odds avoid numerical
certainty caused by rounding probabilities. All evidence has stated conditional
accuracy; source testimony is counted once, not once per repeated assertion.
"""
from dataclasses import dataclass,field,replace
from hashlib import sha256
from math import exp,log

ACCURACY=.8
ARMS=('baseline','audience_removal','free_audit','independent_reliable_evidence')
def u(*key):return int.from_bytes(sha256(repr(key).encode()).digest()[:8],'big')/2**64
def probability(L):return 1/(1+exp(-L)) if L>=0 else exp(L)/(1+exp(L))
def evidence(L,signal,q):return L+(1 if signal else -1)*log(q/(1-q))
def forecast(L,h):
    if h==0:return L
    p=h+(1-2*h)*probability(L)
    return log(p/(1-p))
def sensor(truth,q,*key):return truth if u(*key)<q else 1-truth
@dataclass
class State:
    L:float=0.
    Q:list=field(default_factory=lambda:[0.,0.])
    K:set=field(default_factory=set)
    trust_yes:int=1
    trust_no:int=1
    credit:float=100.
    teacher:int=0

def choose(state,audience=True):
    # Expected physical payoff plus learned action value and possible approval.
    b=probability(state.L)
    value=[.6*(1-2*b)+state.Q[0],.6*(2*b-1)+state.Q[1]]
    if audience:value[state.teacher]+=.1
    return max((0,1),key=lambda a:(value[a],a))
def update_value(s,a,reward):s.Q[a]=.85*s.Q[a]+.15*reward

def train(seed,d,h):
    truth=seed%2;s=State();s.teacher=sensor(truth,.7,seed,'source-conviction')
    s.L=evidence(s.L,s.teacher,.7)  # Single-root statement, available to all d.
    rows=[]
    for episode in range(40):
        s.L=forecast(s.L,h)
        private=sensor(truth,.8,seed,'training-private',episode)
        s.L=evidence(s.L,private,.8)
        neutral=choose(s);conflict=neutral!=s.teacher
        override=conflict and u(seed,'juvenile-override',episode)<d
        action=s.teacher if override else neutral
        feedback=sensor(truth,.8,seed,'training-feedback',episode)
        reward=1. if action==feedback else -1.
        approval=.1 if action==s.teacher else 0.
        cost=.1;s.credit+=reward-cost
        update_value(s,action,reward-cost+approval)
        s.L=evidence(s.L,action if reward>0 else 1-action,.8)
        s.trust_yes+=int(s.teacher==feedback);s.trust_no+=int(s.teacher!=feedback)
        if reward>0:s.K.add(action)  # Paid successful practice, not evaluator truth.
        rows.append({'phase':'training','seed':seed,'d':d,'hazard':h,'episode':episode,'truth':truth,'private':private,
                     'teacher':s.teacher,'neutral':neutral,'conflict':conflict,'override':override,'action':action,
                     'feedback':feedback,'material_receipt':reward,'practice_cost':cost,'psychological_approval':approval,
                     'L':s.L,'B':probability(s.L),'H0':s.Q[0],'H1':s.Q[1],'K':sorted(s.K),
                     'T':s.trust_yes/(s.trust_yes+s.trust_no),'credit':s.credit})
        assert s.credit>=0
    return s,rows

def adult(seed,d,h,initial,arm,change):
    s=replace(initial,Q=list(initial.Q),K=set(initial.K))
    truth=(1-seed%2) if change else seed%2
    rows=[];q=.95 if arm=='independent_reliable_evidence' else .8
    for step in range(20):
        L_before=s.L;H_before=list(s.Q);credit_before=s.credit
        s.L=forecast(s.L,h)
        private=sensor(truth,.8,seed,'adult-private',step)
        audit=sensor(truth,q,seed,'adult-audit',step)
        s.L=evidence(evidence(s.L,private,.8),audit,q)
        cost=0. if arm=='free_audit' else .1
        audience=arm!='audience_removal'
        action=choose(s,audience)
        feedback=sensor(truth,.8,seed,'adult-feedback',step)
        reward=1. if action==feedback else -1.
        approval=.1 if audience and action==s.teacher else 0.
        s.credit+=reward-cost
        update_value(s,action,reward-cost+approval)
        s.L=evidence(s.L,action if reward>0 else 1-action,.8)
        s.trust_yes+=int(s.teacher==feedback);s.trust_no+=int(s.teacher!=feedback)
        rows.append({'phase':'adult','seed':seed,'juvenile_d':d,'hazard':h,'arm':arm,'environment_change':change,
                     'step':step,'truth':truth,'private':private,'audit':audit,'audit_accuracy':q,'feedback':feedback,
                     'L_before':L_before,'L':s.L,'B':probability(s.L),'H0_before':H_before[0],'H1_before':H_before[1],
                     'H0':s.Q[0],'H1':s.Q[1],'K':sorted(s.K),'T':s.trust_yes/(s.trust_yes+s.trust_no),
                     'action':action,'action_correct':action==truth,'posterior_correct':(s.L>=0)==bool(truth),
                     'material_receipt':reward,'audit_cost':cost,'psychological_approval':approval,
                     'credit_before':credit_before,'credit':s.credit,'adult_inherited_override':0.})
        assert s.K==initial.K and abs(s.credit-(credit_before+reward-cost))<1e-9 and s.credit>=0
    return rows
