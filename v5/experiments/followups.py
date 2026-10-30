"""Causal factorial, source-condition maps, and held-out histories for V5."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
from dataclasses import asdict,replace
import numpy as np
from model import *
from run_experiments import ROOT,config,segments,save,table,outcomes


def mechanisms():
 rows=[];dd,tt=np.meshgrid([0,.5,1],[1.,3.,8.],indexing='ij');dd=dd.ravel();tt=tt.ravel()
 for scenario in ('stable','noisy','sparse','truth_reversal','misinformation','wrong_history','no_cost'):
  for variant,args in [('both',{}),('action_only',{'accept':False}),('storage_only',{'override':False}),('neither',{'accept':False,'override':False}),('conflict_storage',{'conflict_only':True})]:
   c=config('retained',scenario,**args);r=run(c,dd,tt,segments(c,scenario),save_states=False)
   met=outcomes(r,c);met.pop("tail_growth",None)
   for i in range(len(dd)):rows.append(dict(scenario=scenario,variant=variant,d=dd[i],tau=tt[i],**{k:float(v[i]) for k,v in met.items()}))
 table('mechanisms.csv',rows);save('mechanisms.json',{'label':'simulation data','definition':'accept and public override are independently switched; individual learning and retention are identical. Conflict-only limits social memory updates to disagreement.','rows':rows})
 print('mechanisms',len(rows),flush=True)


def sources():
 ps=np.linspace(.51,.95,9);accesses=np.geomspace(.05,1,9);rows=[]
 d=np.array([0.,1.,0.,1.,0.,1.]);tau=np.full(6,3.);modes=np.repeat([0,1,2],2)
 for cost in (0.,.02):
  for p in ps:
   for a in accesses:
    c=Config(p=float(p),access=float(a),query_cost=cost);r=run(c,d,tau,modes=modes,points=41,save_states=False)
    met=outcomes(r,c);met.pop("tail_growth",None)
    for i in range(6):rows.append(dict(p=p,access=a,cost=cost,mode=['retained','frozen','audit'][i//2],d=d[i],tau=3.,**{k:float(v[i]) for k,v in met.items()}))
 table('source_conditions.csv',rows)
 contrasts=[]
 for cost in (0.,.02):
  for mode in ('retained','frozen','audit'):
   for p in ps:
    for a in accesses:
     match=[r for r in rows if r['cost']==cost and r['mode']==mode and r['p']==p and r['access']==a]
     x,y=sorted(match,key=lambda x:x['d']);contrasts.append(dict(cost=cost,mode=mode,p=p,access=a,delta_rT=y['rT']-x['rT'],delta_N=y['N']-x['N'],private_N=x['N'],social_N=y['N'],delta_accuracy=y['belief_A']-x['belief_A'],query_A_private=x['query_A'],query_A_social=y['query_A']))
 save('source_conditions.json',{'p_grid':ps,'access_grid':accesses,'tau':3.,'costs':[0,.02],'contrasts':contrasts,'scope':'Each cell changes externally supplied source quality/access. Its displayed difference is a within-cell matched d contrast, not an isolated effect across cells.'})
 print('source_conditions',len(rows),flush=True)


def histories():
 rows=[];paths=[];d,tau=np.meshgrid([0.,.5,1.],[1.,3.,8.],indexing='ij');d=d.ravel();tau=tau.ravel()
 for phase,seeds in [('explore',range(700,712)),('confirm',range(1700,1712))]:
  for seed in seeds:
   rng=np.random.default_rng(seed);switch=[];t=0.
   while True:
    t+=rng.exponential(70)
    if t>=600:break
    switch.append(float(t))
   for world in ('real_changes','channel_changes'):
    seg=[(0.,1,.65)];sign=1
    for t in switch:
     sign=-sign;seg.append((t,sign if world=='real_changes' else 1,.65 if sign==1 else .35))
    paths.append(dict(phase=phase,seed=seed,world=world,segments=seg))
    for model in ('retained','frozen','audit'):
     c=config(model,'stable',T=600.);r=run(c,d,tau,seg,points=61,save_states=False);met=outcomes(r,c);met.pop("tail_growth",None)
     for i in range(len(d)):rows.append(dict(phase=phase,seed=seed,world=world,model=model,d=d[i],tau=tau[i],**{k:float(v[i]) for k,v in met.items()}))
 table('histories.csv',rows);save('history_paths.json',paths)
 summary=[]
 for phase in ('explore','confirm'):
  for world in ('real_changes','channel_changes'):
   for model in ('retained','frozen','audit'):
    for ta in (1.,3.,8.):
     selected=[r for r in rows if r['phase']==phase and r['world']==world and r['model']==model and r['tau']==ta]
     dif=[]
     for seed in sorted(set(r['seed'] for r in selected)):
      pair={r['d']:r for r in selected if r['seed']==seed};dif.append(pair[1.]['rT']-pair[0.]['rT'])
     summary.append(dict(phase=phase,world=world,model=model,tau=ta,n=len(dif),mean=float(np.mean(dif)),se=float(np.std(dif,ddof=1)/np.sqrt(len(dif))),positive=sum(x>0 for x in dif)))
 save('histories_summary.json',{'paired_delta':'r600(d1)-r600(d0)','scope':'Across environmental paths only; not demographic stochasticity. Each true-change/channel-change pair has identical signed cue statistics and event times, but truth-dependent demographic filtering remains active. All begin in +1 with aligned majority, so finite-horizon phase effects remain.','rows':summary})
 print('histories',len(rows),flush=True)


def sensitivity():
 rows=[]
 for H in (1,2,4,6):
  for model in ('retained','frozen','audit'):
   for scenario in ('stable','noisy','truth_reversal','misinformation'):
    c=config(model,scenario,H=H);r=run(c,[0.,1.],[3.,3.],segments(c,scenario),save_states=False);m=outcomes(r,c);m.pop("tail_growth",None)
    for i,d in enumerate((0.,1.)):rows.append(dict(H=H,model=model,scenario=scenario,d=d,**{k:float(v[i]) for k,v in m.items()}))
 table('sensitivity.csv',rows);save('sensitivity.json',rows);print('sensitivity',len(rows),flush=True)

if __name__=='__main__':
 mechanisms();sources();histories();sensitivity()
