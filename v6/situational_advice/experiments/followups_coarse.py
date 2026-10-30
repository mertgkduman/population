"""Predeclared controls and held-out, dense-deference tests; no parameter retuning."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json,time
from pathlib import Path
from dataclasses import replace
import numpy as np
from model import *
from run_experiments import clean,summarize
ROOT=Path(__file__).resolve().parent

def main():
 start=time.time();rows=[];held=[];ds=np.linspace(0,1,33);tau=np.full(len(ds),3.)
 # Dense d at declared tau=3 and fixed local precisions, using independent histories.
 for pA in [.55,.7,.85]:
  for k in [0.,.01,.05,.2]:
   samples=[]
   for seed in range(74001,74017):
    c=Config(context_A=pA);seg=stochastic_segments(c,k,seed);r=run(c,ds,tau,seg,points=31,save_states=False)
    values=summarize(r,seg)['mean_N'];samples.append(values)
   a=np.array(samples);mean=a.mean(0);sd=a.std(0,ddof=1)
   held.append({'p_A':pA,'kappa':k,'tau':3.,'ds':ds,'mean_N':mean,'se_N':sd/4,'samples':a,'best_d':float(ds[mean.argmax()]),'seed_range':[74001,74016]})
   print('dense heldout',pA,k,'best d',ds[mean.argmax()],'seconds',round(time.time()-start,1),flush=True)
 for label,changes in [('full',{}),('clean_fact',{'decode_context':False}),('action_only',{'accept':False}),('memory_only',{'override':False}),('equal_context',{'context_A':.9})]:
  for k in [0.,.2]:
   a=[]
   for seed in range(74001,74005):
    c=Config(**changes);r=run(c,ds,tau,stochastic_segments(c,k,seed),points=31,save_states=False);a.append(summarize(r,stochastic_segments(c,k,seed))['mean_N'])
   a=np.array(a);rows.append({'model':label,'kappa':k,'tau':3.,'p_A':c.context_A,'ds':ds,'mean_N':a.mean(0),'se_N':a.std(0,ddof=1)/2,'best_d':float(ds[a.mean(0).argmax()])})
   print('ablation',label,k,'seconds',round(time.time()-start,1),flush=True)
 out={'label':'simulation data','held_out':held,'ablations':rows,'notes':'Held-out d refinement uses fixed tau=3. It does not establish the joint d/tau optimum. Integration dt=.1, displayed averages every20 time units, no alteration of demographic assumptions.','runtime_seconds':time.time()-start}
 (ROOT/'followups_coarse.json').write_text(json.dumps(clean(out),indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
