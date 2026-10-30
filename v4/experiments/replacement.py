"""Explicit two-genotype test following an invasion/abundance discrepancy."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json,numpy as np
from model import *
from evolution import competition
from run_experiments import ROOT,plain
c=Config();r,*_=equilibrium(c,1,3.19222305);frac=.001
x=np.concatenate([r*(1-frac),r*frac]);out=competition(c,np.array([1.,1.]),np.array([3.19222305,.74655056]),lambda t:1,T=12000,mutation=0,x0=x)
out['initial_resident_N']=float(r.sum());out['interpretation']='Explicit competition with shared teachers and resource, zero mutation; no imposed trait replacement.'
(ROOT/'replacement.json').write_text(json.dumps(plain(out),separators=(',',':'))+'\n')
print('REPLACEMENT',out['final'],out['N'][-1],flush=True)
