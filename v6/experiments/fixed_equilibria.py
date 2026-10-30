"""Fixed-environment equilibrium controls; verify full cognitive-state residuals."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import csv,json
from pathlib import Path
from dataclasses import replace
import numpy as np
from model import *
ROOT=Path(__file__).resolve().parent
def main():
    d,tau=np.meshgrid([0.,.5,1.],[.5,3.,12.],indexing='ij');d=d.ravel();tau=tau.ravel();rows=[]
    for eta in [0.,.1,1.]:
        c=Config(T=800,plasticity_A=eta);x=initial(c,len(d));elapsed=0
        for _ in range(6):
            x=run(c,d,tau,points=2,x0=x,save_states=False)['final_state'];elapsed+=c.T
            residual=np.max(abs(rhs(c,x,d,tau)),axis=(1,2,3))/np.maximum(1,x.sum((1,2,3)))
            if np.all(residual<1e-9):break
        vals=metrics(c,x,d,tau);mirrored=x[:,:,::-1,::-1]
        symmetry=np.max(abs(rhs(c,mirrored,d,tau,theta=-1)[:,:,::-1,::-1]-rhs(c,x,d,tau)),axis=(1,2,3))
        for i in range(len(d)):
            rows.append({'eta_A':eta,'d':d[i],'tau':tau[i],'N_star':float(vals['N'][i]),'adult_accuracy':float(vals['belief_A'][i]),'full_relative_residual':float(residual[i]),'equilibrium_confirmed':bool(residual[i]<1e-8),'negative_truth_abundance':float(mirrored[i].sum()),'mirror_rhs_error':float(symmetry[i]),'integration_time':elapsed})
        print('fixed equilibria eta',eta,'max residual',float(residual.max()),flush=True)
    with (ROOT/'fixed_equilibria.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (ROOT/'fixed_equilibria.json').write_text(json.dumps({'label':'simulation data','rows':rows,'interpretation':'Fixed truth only. Opposite truths have identical abundance and mirrored cognitive states. Unconverged rows must not be called confirmed equilibria.'},indent=2)+'\n')
if __name__=='__main__':main()
