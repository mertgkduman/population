"""Rebuild machine-readable summaries from simulation outputs (no p-values)."""
import csv,json,numpy as np
from scipy.stats import t
from pathlib import Path
from run_experiments import ROOT
r=list(csv.DictReader(open(ROOT/'sweep.csv')));s=list(csv.DictReader(open(ROOT/'stochastic.csv')))
summary={'optima':[],'environment_seed_contrasts':[],'history_convergence':{},'labels':{'growth':'r400 finite-horizon log growth; N400 same ordering at fixed initial N','uncertainty':'95% Student-t interval for paired mean across random environment histories only; deterministic within each history'}}
for model in sorted({x['model'] for x in r}):
 for scenario in sorted({x['scenario'] for x in r}):
  a=[x for x in r if x['model']==model and x['scenario']==scenario];best=max(a,key=lambda x:float(x['rT']));ties=[x for x in a if abs(float(x['rT'])-float(best['rT']))<1e-8]
  summary['optima'].append({'model':model,'scenario':scenario,'d_range':[min(float(x['d']) for x in ties),max(float(x['d']) for x in ties)],'tau_range':[min(float(x['tau']) for x in ties),max(float(x['tau']) for x in ties)],'N':float(best['N']),'rT':float(best['rT']),'ties':len(ties),'d_inactive':model in ('private','oracle','rl')})
for phase in ['exploratory','confirmatory']:
 for tau in [1.,3.,8.]:
  a={(int(x['seed']),float(x['d'])):float(x['rT']) for x in s if x['phase']==phase and x['model']=='fixed' and float(x['tau'])==tau};diff=np.array([a[seed,1]-a[seed,0] for seed in sorted({x[0] for x in a})]);half=t.ppf(.975,len(diff)-1)*diff.std(ddof=1)/np.sqrt(len(diff))
  summary['environment_seed_contrasts'].append({'phase':phase,'tau':tau,'paired_d1_minus_d0_mean':diff.mean(),'CI95':[diff.mean()-half,diff.mean()+half],'positive_histories':int(sum(diff>0)),'n':len(diff)})
for model in sorted({x['model'] for x in r}):
 a={(x['d'],x['tau']):float(x['belief_A']) for x in r if x['model']==model and x['scenario']=='stable'};b={(x['d'],x['tau']):float(x['belief_A']) for x in r if x['model']==model and x['scenario']=='wrong_history'}
 summary['history_convergence'][model]=max(abs(a[k]-b[k]) for k in a)
(ROOT/'findings.json').write_text(json.dumps(summary,indent=2)+'\n')
print('analysis complete')
