"""Execution-priced one-decision EVI and durable world-level decision counters.

This is a comparator under shared Q0, not a full-horizon optimal learner. Twelve
abstract deliberation units are paid on every option, including no purchase.
"""
from collections import Counter
from dataclasses import replace
from math import log
from v7.experiments.corrected_model import CorrectedEcologyRun
from v7.experiments.model import OrdinarySocialPolicy,_map,_logit,_logistic,posterior_advice_probability,validate_policy_observation

class ExecutionPlanner(OrdinarySocialPolicy):
    DELIBERATION=12
    def expected_after(self,obs,p,accuracy):
        positive=p*accuracy+(1-p)*(1-accuracy)
        ratio=log(accuracy/(1-accuracy))
        hi=_logistic(_logit(p)+ratio);lo=_logistic(_logit(p)-ratio)
        return positive*max(v for _,v in self._q0_with_posterior(obs,hi))+(1-positive)*max(v for _,v in self._q0_with_posterior(obs,lo))
    def decide(self,obs,cap,rng):
        obs=validate_policy_observation(obs);prices=_map(obs.prices);p=posterior_advice_probability(obs)
        base=max(v for _,v in self._q0(obs));options=[(None,base)]
        physical_tokens=(round(prices.get('execute',0.)/.2)+1) if {'branch_0','branch_1'}.issubset(obs.feasible_actions) else 1
        for name,accuracy,extra_ops in [('query',.8,1),('verify',.9,2)]:
            if obs.time_tokens < physical_tokens+1 or cap < 1+self.DELIBERATION+extra_ops+1:continue
            # World execution debits exactly one information token. With enough
            # remaining tokens the same sole physical task still executes; there
            # is no additional production from idle tokens in this world.
            fee=prices[name]+prices.get('operation',0.)*(extra_ops+1)
            options.append((name,self.expected_after(obs,p,accuracy)-fee))
        choice,value=max(options,key=lambda x:(x[1],str(x[0])))
        return self._decision(obs,cap,rng,allow_override=False,social=True,information_action=choice,
                              information_value=value-base,computation_operations=self.DELIBERATION)

class CountedExecutionWorld(CorrectedEcologyRun):
    def __init__(self,*args,**kwargs):
        self.decision_counts=Counter();super().__init__(*args,**kwargs)
    def _make_policy(self,traits=()):
        policy=super()._make_policy(traits);original=policy.decide
        def observed(obs,cap,rng):
            out=original(obs,cap,rng)
            self.decision_counts['all_initial_decisions']+=1
            self.decision_counts['teacher_present']+=int(obs.advice is not None)
            self.decision_counts['no_teacher']+=int(obs.advice is None)
            self.decision_counts['initial_conflicts']+=int(out.conflict)
            self.decision_counts['query_purchases']+=int(out.information_action=='query')
            self.decision_counts['verify_purchases']+=int(out.information_action=='verify')
            return out
        policy.decide=observed
        return policy
    def _remaining(self,p):return max(0,self.TIME_TOKENS-getattr(self,'_time_used',{}).get(p.identity,0))
    def _observation(self,p,f,t):return replace(super()._observation(p,f,t),time_tokens=self._remaining(p))
    def _local_observation(self,p,f,t):
        obs,ctx=super()._local_observation(p,f,t)
        return replace(obs,time_tokens=self._remaining(p)),ctx
    def run(self):
        result=super().run();result.update({f'count_{k}':v for k,v in self.decision_counts.items()})
        result['count_definition']='Whole-world initial arbitration requests; includes dead and newborn actors; post-query re-arbitration not a new opportunity.'
        return result
