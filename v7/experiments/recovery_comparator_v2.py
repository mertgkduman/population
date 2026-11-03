"""R1a v2: bounded marginal-cost comparator through a time-aware overlay."""
from __future__ import annotations
from math import log
from v7.experiments.corrected_model import CorrectedEcologyRun
from v7.experiments.model import OrdinarySocialPolicy, PolicyObservation, PolicyDecision, KeyedRNG, _logit,_logistic,_map,posterior_advice_probability,validate_policy_observation

class MarginalCostPlanner(OrdinarySocialPolicy):
    QUERY_ACC,VERIFY_ACC,COMMON_OP= .8,.9,2
    def __init__(self):super().__init__();self.queries=self.verifies=self.conflicts=0
    def signal(self,o,p,a):
        prob=p*a+(1-p)*(1-a); hi=_logistic(_logit(p)+log(a/(1-a)));lo=_logistic(_logit(p)-log(a/(1-a)))
        return prob*max(v for _,v in self._q0_with_posterior(o,hi))+(1-prob)*max(v for _,v in self._q0_with_posterior(o,lo))
    def decide(self,o:PolicyObservation,cap:int,rng:KeyedRNG)->PolicyDecision:
        o=validate_policy_observation(o);prices=_map(o.prices);p=posterior_advice_probability(o);base=max(v for _,v in self._q0(o))
        # Common deliberation is charged for every option. Incremental costs are
        # only posted fee, information primitive work, and the paid final arbitration.
        feasible=o.time_tokens>=2
        choices=[(None,base)]
        if feasible:
            for name,acc,ops in (("query",self.QUERY_ACC,1),("verify",self.VERIFY_ACC,2)):
                choices.append((name,self.signal(o,p,acc)-prices.get(name,0.)-prices.get("operation",0.)*(ops+1)))
        chosen,value=max(choices,key=lambda x:(x[1],str(x[0])))
        d=self._decision(o,cap,rng,allow_override=False,social=True,information_action=chosen,information_value=value-base,computation_operations=self.COMMON_OP)
        self.conflicts+=int(d.conflict);self.queries+=int(chosen=="query");self.verifies+=int(chosen=="verify");return d

class TimeAwareCorrectedRun(CorrectedEcologyRun):
    """Small adapter: policies see actual remaining tokens, not nominal 12.

    Core `EcologyRun._observation` / `_local_observation` construct observations
    with `TIME_TOKENS` despite paid messages already reserving tokens. This overlay
    replaces only that field; it leaves world transitions and task execution intact.
    """
    def _remaining(self,p):return max(0,self.TIME_TOKENS-self._time_used.get(p.identity,0))
    def _observation(self,p,f,t):
        o=super()._observation(p,f,t);return PolicyObservation(**{**o.__dict__,"time_tokens":self._remaining(p)})
    def _local_observation(self,p,f,t):
        o,c=super()._local_observation(p,f,t);return PolicyObservation(**{**o.__dict__,"time_tokens":self._remaining(p)}),c
    def run(self):
        result=super().run(); policies=[p.policy for p in self.population.values() if isinstance(p.policy,MarginalCostPlanner)]
        result.update(query_purchases=sum(p.queries for p in policies),verify_purchases=sum(p.verifies for p in policies),conflict_opportunities=sum(p.conflicts for p in policies),no_teacher_opportunities=getattr(self,"no_teacher_counter",0));return result
    def _observation(self,p,f,t):
        if t is None:self.no_teacher_counter=getattr(self,"no_teacher_counter",0)+1
        o=super(TimeAwareCorrectedRun,self)._observation(p,f,t);return PolicyObservation(**{**o.__dict__,"time_tokens":self._remaining(p)})
