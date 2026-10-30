"""Check whether a coarse maturation boundary hides a local invasion optimum."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json
import numpy as np
from scipy.linalg import eigvals
from scipy.optimize import brentq
from model import *
from run_experiments import ROOT,config
out=[]
for scenario in ('stable','noisy','sparse'):
 c=config('retained',scenario)
 def gradient(tau):
  eq=equilibrium(c,1.,float(tau));h=tau*1e-3
  return float((eigvals(generator(c,1.,tau+h,eq['environment'])).real.max()-eigvals(generator(c,1.,tau-h,eq['environment'])).real.max())/(2*h))
 taus=[.2,.35,.5,.75,1.5,3.,6.,12.];gr=[gradient(t) for t in taus];roots=[]
 for a,b,ga,gb in zip(taus,taus[1:],gr,gr[1:]):
  if ga*gb<0:
   root=float(brentq(gradient,a,b,xtol=1e-5));eq=equilibrium(c,1.,root)
   candidates=[(float(d),float(t),float(eigvals(generator(c,d,t,eq['environment'])).real.max())) for d in np.linspace(0,1,9) for t in np.geomspace(.2,12,25)]
   best=max(candidates,key=lambda x:x[2]);roots.append({'tau':root,'sign_change':[ga,gb],'N':eq['N'],'max_sampled_invader':best,'mutants_tested':len(candidates),'main_domain':.5<=root<=12})
 out.append({'scenario':scenario,'d':1.,'scan_tau':taus,'gradient':gr,'roots':roots,'primary_domain':[.5,12],'scope':'Finite-difference rare-mutant gradient under a matched resident cultural environment; numerical candidates, not an ESS proof. Expanded lower bound .2 is separately labeled.'})
 print(scenario,list(zip(taus,gr)),roots,flush=True)
(ROOT/'selection_refinement.json').write_text(json.dumps(out,indent=2)+'\n')
