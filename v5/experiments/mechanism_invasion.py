"""Separate immediate action override from internalization in the same resident culture."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
from scipy.linalg import eigvals
from model import *
from run_experiments import config,save,table
rows=[]
for scenario in ('stable','noisy','sparse'):
 for rd in (0.,1.):
  c=config('retained',scenario);eq=equilibrium(c,rd,3.)
  for name,flags in [('both',{}),('action_only',{'accept':False}),('storage_only',{'override':False}),('neither',{'accept':False,'override':False})]:
   for d in (0.,.25,.5,.75,1.):
    cm=replace(c,**flags);rate=float(eigvals(generator(cm,d,3.,eq['environment'])).real.max())
    rows.append(dict(scenario=scenario,resident_d=rd,resident_N=eq['N'],variant=name,mutant_d=d,tau=3.,invasion=rate))
table('mechanism_invasion.csv',rows);save('mechanism_invasion.json',{'scope':'Each mutant uses the same declared resident adult culture/resources. Tests immediate conflict override separately from persistent acceptance; lower monomorphic N is not automatically negative invasion fitness.','rows':rows})
for row in rows:
 if row['mutant_d']==1. and row['variant']=='action_only':print(row,flush=True)
