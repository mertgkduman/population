"""Local optimum refinement and cost/memory adversarial sensitivity, after main grids."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import csv,json
from dataclasses import replace
import numpy as np
from scipy.optimize import minimize_scalar
from model import *
from run_experiments import ROOT,config,segments,save,table,outcomes
rows=[]
for H in (2,4,6,8):
 for cost in (0.,.02):
  for model in ('retained','frozen','audit'):
   d,tau=np.meshgrid([0.,.5,1.],[1.,3.,8.],indexing='ij');d=d.ravel();tau=tau.ravel()
   c=config(model,'noisy',H=H,query_cost=cost);r=run(c,d,tau,points=2,save_states=False)
   for i in range(len(d)):rows.append(dict(H=H,query_cost=cost,model=model,d=d[i],tau=tau[i],N=r['N'][i,-1],accuracy=r['belief_A'][i,-1],query_A=r['query_A'][i,-1],rT=np.log(r['N'][i,-1]/100)/400))
table('cost_memory.csv',rows);save('cost_memory.json',{'purpose':'Disentangle query-cost savings from finite-score retention under noisy p=.55; same p and capacity within each matched comparison. Exploratory adversarial extension after main result.','rows':rows});print('costmemory',len(rows),flush=True)
main=list(csv.DictReader(open(ROOT/'sweep.csv')));refined=[]
for model,scenario in [('retained','stable'),('frozen','stable'),('audit','stable'),('retained','noisy'),('frozen','noisy'),('audit','noisy'),('retained','sparse'),('audit','sparse')]:
 rr=[r for r in main if r['model']==model and r['scenario']==scenario];best=max(rr,key=lambda r:float(r['rT']));taus=sorted(set(float(r['tau']) for r in rr));old=float(best['tau']);j=taus.index(old)
 c=config(model,scenario)
 def objective(tau):
  z=run(c,[1.],[float(tau)],points=2,save_states=False);return -float(z['N'][0,-1])
 lo=taus[max(0,j-1)];hi=taus[min(len(taus)-1,j+1)]
 opt=minimize_scalar(objective,bounds=(lo,hi),method='bounded',options={'xatol':1e-5})
 candidates=[(lo,objective(lo)),(float(opt.x),float(opt.fun)),(hi,objective(hi))];ta,val=min(candidates,key=lambda x:x[1])
 r=run(c,[1.,.999],[ta,ta],points=2,save_states=False);half=run(replace(c,dt=.05),[1.,.999],[ta,ta],points=2,save_states=False)
 refined.append(dict(model=model,scenario=scenario,d=1.,tau=ta,N=-val,local_bracket=[lo,hi],tau_domain_boundary=abs(ta-.5)<1e-5 or abs(ta-12)<1e-5,d_boundary=True,d_slope=(r['N'][0,-1]-r['N'][1,-1])/.001,step_halving_N_difference=float(abs(r['N'][0,-1]-half['N'][0,-1])),scope='Local abundance/r400 refinement after coarse full-domain map; not an evolutionary optimum.'))
 print('refined',model,scenario,ta,flush=True)
(ROOT/'refinement.json').write_text(json.dumps(refined,indent=2)+'\n')
