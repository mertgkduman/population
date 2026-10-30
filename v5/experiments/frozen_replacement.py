"""Exploratory follow-up of slow frozen-versus-audit invasion under noisy evidence."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json
from dataclasses import replace
import numpy as np
from scipy.linalg import eigvals
from model import *
from run_experiments import ROOT,save
cases=[]
for cost in (0.,.02):
 c=Config(p=.55,query_cost=cost,adult_mode='audit');eq=equilibrium(c,1.,3.)
 for candidate in ('update','frozen','audit'):
  cm=replace(c,adult_mode=candidate);fit=float(eigvals(generator(cm,1.,3.,eq['environment'])).real.max());cases.append({'query_cost':cost,'resident':'audit','mutant':candidate,'invasion':fit,'resident_N':eq['N']})
print(cases,flush=True)
c=Config(p=.55,adult_mode='audit',T=150000.);eq=equilibrium(c,1.,3.)
x=np.concatenate([eq['state']*.999,eq['state']*.001])
r=run(c,[1.,1.],[3.,3.],x0=x,shared=True,modes=np.array([2,1]),mutation=0.,points=101,save_states=False)
freq=r['N']/r['N'].sum(axis=0)
(ROOT/'frozen_replacement.json').write_text(json.dumps({'label':'simulation data','exploratory':True,'question':'A very slow invasion may be hidden by T2000 competition. Test a 0.1% frozen lineage in the audit resident, p=.55,tau3,d1,querycost.02.','invasion_controls':cases,'t':r['t'].tolist(),'N':r['N'].sum(axis=0).tolist(),'frequency':freq.tolist(),'advice':r['advice'][0].tolist(),'final_frozen_fraction':float(freq[1,-1]),'initial_N':float(r['N'][:,0].sum()),'final_N':float(r['N'][:,-1].sum()),'scope':'Additional inherited adult policy comparison; policies were assigned. No claim of emergent dogmatism or stochastic extinction.'},indent=2)+'\n')
print('replacement',freq[:,-1],r['N'][:,-1].sum(),flush=True)
