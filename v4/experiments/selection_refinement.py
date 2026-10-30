"""Follow up coarse mutation-grid boundary: solve the tau invasion-gradient root."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json
import numpy as np
from scipy.optimize import brentq
from scipy.linalg import eigvals
from model import *
from run_experiments import ROOT
c=Config()
def info(tau):
 x,q,s,rr,res=equilibrium(c,1,tau);return x,q,s

def grad(tau):
 x,q,s=info(tau);h=.001*tau
 fun=lambda t:float(eigvals(generator(c,1,t,q,s)).real.max())
 return (fun(tau+h)-fun(tau-h))/(2*h)
scan=[(t,grad(t)) for t in np.geomspace(.2,6,13)]
roots=[]
for (a,ga),(b,gb) in zip(scan,scan[1:]):
 if ga*gb<0:
  t=brentq(grad,a,b,xtol=1e-5);x,q,s=info(t);ds,ts=np.meshgrid(np.linspace(0,1,21),np.geomspace(.2,12,61),indexing='ij');rates=np.array([eigvals(generator(c,d,tau,q,s)).real.max() for d,tau in zip(ds.ravel(),ts.ravel())]);imax=int(rates.argmax())
  roots.append({'d':1,'tau':t,'gradient':grad(t),'N':x.sum(),'advice':q,'max_tested_invasion':rates[imax],'best_tested_mutant':[ds.ravel()[imax],ts.ravel()[imax]],'local_gradient_left':grad(t*.98),'local_gradient_right':grad(t*1.02),'tested_mutants':len(rates)})
(ROOT/'selection_refinement.json').write_text(json.dumps({'scan':scan,'candidates':roots,'interpretation':'finite-difference singular maturation candidate at d boundary; no analytic ESS proof'},indent=2,default=float)+'\n')
print(roots,flush=True)
