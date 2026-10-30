"""Predeclared held-out paths and a within-adult learning diagnostic."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json,time
from dataclasses import replace
from pathlib import Path
import numpy as np
from model import *
from run_experiments import clean,summarize
from invasion import run_invasion
ROOT=Path(__file__).resolve().parent
def main():
    start=time.time();held=[];ds=np.array([0.,.5,1.]);tau=np.full(3,3.)
    for k in [0.,.01,.2]:
        samples=[];relative=[]
        for seed in range(68001,68017):
            c=Config();seg=stochastic_segments(c,k,seed);r=run(c,ds,tau,seg,points=151,save_states=False);stats=summarize(r,seg)
            lg,rn=run_invasion(c,ds,tau,seg,r['t']);j=50
            rate=(lg[:,-1]-lg[:,j])/400-np.log(rn[-1]/rn[j])/400
            held.append({'kappa':k,'seed':seed,'d':ds,'tau':tau,'mean_N':stats['mean_N'],'adult_accuracy':stats['adult_accuracy'],'invasion_relative':rate})
            samples.append(stats['mean_N']);relative.append(rate)
        np.savez_compressed(ROOT/('heldout_k'+str(k)+'.npz'),d=ds,tau=tau,seeds=np.arange(68001,68017),mean_N=np.array(samples),invasion_relative=np.array(relative))
        print('heldout',k,'seconds',round(time.time()-start,1),flush=True)
    cohort=[]
    for eta in [0.,.1,1.]:
        c=Config(T=200,plasticity_A=eta,mu_F=0,mu_A=0,error_F=0,error_A=0,beta_base=0,beta_skill=0,nu_social=0)
        x=np.zeros_like(initial(c));x[0,1,c.H+2,c.H+2]=20
        r=run(c,[.5],[3],segments=[(0,-1,1-c.p)],points=201,x0=x)
        good=np.flatnonzero(r['belief_A'][0]>=.75)
        cohort.append({'eta_A':eta,'t':r['t'],'adult_accuracy':r['belief_A'][0],'N':r['N'][0],'first_accuracy_75':float(r['t'][good[0]]) if len(good) else None})
    # Observable averaging, distinct from solver-step convergence.
    c=Config();seg=stochastic_segments(c,.2,68001);coarse=run(c,ds,tau,seg,points=151,save_states=False);fine=run(c,ds,tau,seg,points=1201,save_states=False)
    a=summarize(coarse,seg);b=summarize(fine,seg)
    resolution={key:{'coarse':a[key],'fine':b[key],'max_abs_difference':float(np.max(abs(a[key]-b[key])))} for key in ['mean_N','adult_accuracy','private_accuracy']}
    out={'label':'simulation data','held_out_seeds':list(range(68001,68017)),'held_out':held,'cohort':cohort,'observation_resolution':resolution,'runtime_seconds':time.time()-start,'interpretation':'Cohort removes replacement and mortality; plasticity is imposed. Held-out tests use new environmental paths. Four-time-unit averages and first-passage times have sampling limitations.'}
    (ROOT/'followups.json').write_text(json.dumps(clean(out),indent=2,allow_nan=False)+'\n');print('DONE followups',flush=True)
if __name__=='__main__':main()
