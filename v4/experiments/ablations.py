"""Decisive negative controls and full-precision evidence follow-ups."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json,gzip
import numpy as np
from dataclasses import replace
from model import *
from run_experiments import ROOT,envfn,table
rows=[]
for name,changes in [('default',{}),('reset_maturation',{'reset_maturation':True}),('no_adult_update',{'adult_rate':0}),('uninformative_private',{'p':.5}),('no_payoff',{'payoff':False}),('public_only',{'internalize':False})]:
 for scenario in ['stable','shock']:
  c=Config(**changes);rr=run(c,[0,.5,1],[3,3,3],envfn(scenario),points=81)
  for i,d in enumerate([0,.5,1]):rows.append({'ablation':name,'scenario':scenario,'d':d,'tau':3,'N':rr['N'][i,-1],'rT':np.log(rr['N'][i,-1]/100)/400,'belief_A':rr['belief_A'][i,-1],'persistence':rr['dogmatism'][i,-1],'min_postshock_accuracy':float(rr['belief_A'][i,30:].min())})
table('ablations.csv',rows)
# retain incorrect confident beliefs as a separate outcome, derived from saved distributions
with gzip.open(ROOT/'dashboard_data.json.gz','rt') as f:payload=json.load(f)
for context in payload['contexts']:
 data=np.load(ROOT/(context['id']+'.npz'));x=data['states'];H=context['config']['H'];z=np.arange(-H,H+1);theta=np.array([envfn(context['scenario'])(t) for t in data['t']]);wrong=(z[None,:]*theta[:,None]<0)&(np.abs(z)[None,:]>3)
 A=x[:,:,1].sum((2,3));mass=(x[:,:,1]*wrong[None,:,:,None]).sum((2,3));y=np.divide(mass,A,out=np.zeros_like(A),where=A>0)
 context['metrics']['wrong_high_confidence']=y[:,-1].round(8).tolist();context['series']['wrong_high_confidence']=y.round(8).tolist()
 context['metrics']['peak_wrong_confidence']=y.max(axis=1).round(8).tolist()
with gzip.open(ROOT/'dashboard_data.json.gz','wt') as f:json.dump(payload,f,separators=(',',':'))
# redo just dynamic convergence without rounding scientific precision
from evolution import dynamic_invasion
c=Config();d,t=np.meshgrid([0,.5,1],[1,3,8],indexing='ij');a,b,r=dynamic_invasion(c,d.ravel(),t.ravel(),envfn('periodic'));a2,b2,r2=dynamic_invasion(replace(c,dt=.05),d.ravel(),t.ravel(),envfn('periodic'))
(ROOT/'dynamic_convergence.json').write_text(json.dumps({'max_absolute_rate_difference':float(abs(b-b2).max()),'dt':.1,'half_dt':.05,'self_relative':float(b[4]),'half_self_relative':float(b2[4])},indent=2)+'\n')
print('ABLATIONS DONE',flush=True)
