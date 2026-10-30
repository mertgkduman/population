"""Independent next-generation / eigenvalue sign and low-density normalized growth."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json,numpy as np
from scipy.linalg import eigvals
from model import *
from run_experiments import ROOT
c=Config();xr,q,s,_,_=equilibrium(c,1,3.19222305);rows=[]
for d,tau in [(0,3),(1,.74655056),(1,3.19222305),(1,8)]:
 G=generator(c,d,tau,q,s);n=G.shape[0]//2;J=G[:n,:n];A=G[n:,n:];M=G[n:,:n];b=G[:n,n:].sum(axis=0);e=np.zeros(n);e[c.H]=1
 R0=float(b@np.linalg.solve(-A,M@np.linalg.solve(-J,e)));rate=float(eigvals(G).real.max())
 rows.append({'d':d,'tau':tau,'R0':R0,'invasion':rate,'sign_agreement':bool(abs(rate)<1e-8 or (R0>1)==(rate>0))})
# Low-density growth with endogenous culture: renormalization retains log scale.
low=[]
for d,tau in [(0,3),(1,.74655056),(1,3.19222305)]:
 x=initial(c);x/=x.sum();logs=0.;fun=lambda t:1
 for i in range(6000):
  def f(y):
   q,_=environment(c,y,1);return rhs(c,y,[d],[tau],1,(q,np.array([c.S0/(c.KS+c.S0)])))
  h=.1;k1=f(x);k2=f(x+h*k1/2);k3=f(x+h*k2/2);k4=f(x+h*k3);x+=h*(k1+2*k2+2*k3+k4)/6
  mass=x.sum();x/=mass
  if i>=4000:logs+=np.log(mass)
 low.append({'d':d,'tau':tau,'low_density_asymptotic_rate_estimate':logs/200,'burn_in':400,'measurement_window':200})
(ROOT/'reproductive_value.json').write_text(json.dumps({'resident_d':1,'resident_tau':3.19222305,'benchmarks':rows,'low_density':low},indent=2)+'\n')
print('REPRODUCTIVE VALUE DONE',flush=True)
