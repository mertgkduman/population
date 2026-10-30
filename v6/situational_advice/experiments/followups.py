"""Predeclared controls and held-out, dense-deference tests; no parameter retuning."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json,time
from pathlib import Path
from dataclasses import replace
import numpy as np
from model import *
from run_experiments import clean
from model import _advance,packed
ROOT=Path(__file__).resolve().parent

def abundance_run(c,d,tau,segments,points=151):
 x=initial(c,len(d));ts=np.linspace(0,c.T,points);N=[];t=0.;j=0
 modes=np.zeros(len(d),dtype=np.int64);fixed=np.empty((0,3))
 for target in ts:
  while t<target-1e-10:
   stop=min(target,segments[j+1][0] if j+1<len(segments) else target)
   x=_advance(x,d,tau,packed(c),modes,t,stop,c.dt,segments[j][1],segments[j][2],False,0.,fixed);t=stop
   if j+1<len(segments) and t>=segments[j+1][0]-1e-10:j+=1
  N.append(x.sum((1,2,3)))
 return {'t':ts,'N':np.array(N).T}
def average_N(r):
 at=np.searchsorted(r['t'],200)
 return np.trapezoid(r['N'][:,at:],r['t'][at:],axis=1)/(r['t'][-1]-r['t'][at])

def main():
 start=time.time();rows=[];held=[];ds=np.linspace(0,1,33);tau=np.full(len(ds),3.)
 # Dense d at declared tau=3 and fixed local precisions, using independent histories.
 for pA in [.55,.7,.85]:
  for k in [0.,.01,.05,.2]:
   samples=[]
   for seed in range(74001,74017):
    c=Config(context_A=pA);seg=stochastic_segments(c,k,seed);r=abundance_run(c,ds,tau,seg)
    values=average_N(r);samples.append(values)
   a=np.array(samples);mean=a.mean(0);sd=a.std(0,ddof=1)
   held.append({'p_A':pA,'kappa':k,'tau':3.,'ds':ds,'mean_N':mean,'se_N':sd/4,'samples':a,'best_d':float(ds[mean.argmax()]),'seed_range':[74001,74016]})
   print('dense heldout',pA,k,'best d',ds[mean.argmax()],'seconds',round(time.time()-start,1),flush=True)
 for label,changes in [('full',{}),('clean_fact',{'decode_context':False}),('action_only',{'accept':False}),('memory_only',{'override':False}),('equal_context',{'context_A':.9})]:
  for k in [0.,.2]:
   a=[]
   for seed in range(74001,74005):
    c=Config(**changes);r=abundance_run(c,ds,tau,stochastic_segments(c,k,seed));a.append(average_N(r))
   a=np.array(a);rows.append({'model':label,'kappa':k,'tau':3.,'p_A':c.context_A,'ds':ds,'mean_N':a.mean(0),'se_N':a.std(0,ddof=1)/2,'best_d':float(ds[a.mean(0).argmax()])})
   print('ablation',label,k,'seconds',round(time.time()-start,1),flush=True)
 out={'label':'simulation data','held_out':held,'ablations':rows,'notes':'Held-out d refinement uses fixed tau=3. It does not establish the joint d/tau optimum. Integration dt=.1, refined averages every4 time units; abundance-only observation uses the identical demographic integrator, no alteration of demographic assumptions.','runtime_seconds':time.time()-start}
 (ROOT/'followups.json').write_text(json.dumps(clean(out),indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
