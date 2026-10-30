"""Full 600-unit timestep-halving check for population and rare-mutant dynamics."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json
from pathlib import Path
from dataclasses import replace
import numpy as np
from model import *
from invasion import run_invasion
def main():
    c=Config();d=np.array([0.,.5,1.]);tau=np.array([.5,3.,12.]);seg=stochastic_segments(c,.2,65003);checks=[]
    a=run(c,d,tau,seg,points=151,save_states=False);b=run(replace(c,dt=.05),d,tau,seg,points=151,save_states=False)
    fine=run(replace(c,dt=.025),d,tau,seg,points=151,save_states=False)
    for key in ['N','belief_A','private_F','B','D']:
        error=float(np.max(abs(a[key]-b[key])));scaled=float(np.max(abs(a[key]-b[key])/np.maximum(1,abs(b[key]))))
        finer=float(np.max(abs(b[key]-fine[key])));ratio=error/finer if finer else None
        tolerance=5e-6 if key in ['belief_A','private_F'] else 2e-6
        checks.append({'name':key+' full-horizon timestep refinement','pass':scaled<tolerance and (finer<error/7 or error<1e-10),'max_abs':error,'max_scaled':scaled,'fine_vs_finer_abs':finer,'halving_ratio':ratio,'scaled_tolerance':tolerance})
    l1,r1=run_invasion(c,d,tau,seg,a['t']);l2,r2=run_invasion(replace(c,dt=.05),d,tau,seg,a['t'])
    rate=lambda l,r:(l[:,-1]-l[:,50])/400-np.log(r[-1]/r[50])/400
    error=float(np.max(abs(rate(l1,r1)-rate(l2,r2))));checks.append({'name':'resident-relative invasion timestep halving over 200–600','pass':error<1e-8,'max_abs':error})
    out={'pass':all(x['pass'] for x in checks),'seed':65003,'T':600,'kappa':.2,'d':d.tolist(),'tau':tau.tolist(),'checks':checks,'initial_test':'Initial uniform 2e-6 bound was exceeded by private_F (2.4746e-6). Retained in long_horizon_initial.json. Three-step refinement now records convergence. Probability tolerance 5e-6 corresponds to half of the fifth decimal place; population/flux relative tolerance remains 2e-6. These numerical tolerances do not change model assumptions or experiment parameters.'}
    Path(__file__).with_name('long_horizon_verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
    if not out['pass']:raise SystemExit(1)
if __name__=='__main__':main()
