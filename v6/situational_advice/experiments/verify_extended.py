"""Noisy-context self-invasion, integration/observation refinement and publication parity."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
from pathlib import Path
from dataclasses import replace
import json,gzip
import numpy as np
from model import *
from invasion import run_invasion
from run_experiments import summarize
ROOT=Path(__file__).resolve().parent
def main():
    checks=[]
    def check(name,ok,detail=None):checks.append({'name':name,'pass':bool(ok),'detail':detail})
    c=Config();d=np.array([0.,.5,1.]);tau=np.array([.5,3.,12.]);seg=stochastic_segments(c,.2,71003)
    a=run(c,d,tau,seg,points=151,save_states=False);b=run(replace(c,dt=.05),d,tau,seg,points=151,save_states=False)
    for key in ['N','B','D','local_private','local_advice','belief_A']:
        scaled=float(np.max(abs(a[key]-b[key])/np.maximum(1,abs(b[key]))));check(key+' full-horizon step halving',scaled<5e-6,scaled)
    l1,r1=run_invasion(c,np.array([.5]),np.array([3.]),seg,a['t']);err=float(np.max(abs(l1[0]-np.log(r1/100))))
    check('noisy-context resident against itself is relatively neutral',err<1e-11,err)
    coarse=run(c,d,tau,seg,points=31,save_states=False);fine=summarize(a,seg)['mean_N'];cc=summarize(coarse,seg)['mean_N'];delta=float(np.max(abs(cc-fine)))
    from followups import abundance_run
    exact=abundance_run(c,d,tau,seg);match=float(np.max(abs(exact['N']-a['N'])))
    check('refined heldout 4-unit averaging uses identical core',match<1e-11,{'initial_20_vs_4_N_difference':delta,'refined_core_error':match,'current_interval':4,'initial_miss_preserved':'extended_initial.json'})
    payload=json.loads(gzip.decompress((ROOT/'dashboard_data.json.gz').read_bytes()))
    grouped={}
    for ctx in payload['contexts']:
        cfg=ctx['config'];check(ctx['id']+' local quality/ability fixed',cfg['context_A']<cfg['context_F']==.9 and cfg['p']==.65 and cfg['plasticity_F']==1 and cfg['plasticity_A']==.1)
        with np.load(ROOT/(ctx['id']+'.npz')) as raw,np.load(ROOT.parent/'published'/(ctx['id']+'.npz')) as pub:
            check(ctx['id']+' displayed sample equals full raw values',all(np.array_equal(pub[k],raw[k][0,:,::2]) for k in ['N','F','A','B','D','M','local_private','belief_A','public_F','local_advice']) and np.array_equal(pub['t'],raw['t'][::2]))
            check(ctx['id']+' all seed outcomes retained exactly',all(np.array_equal(pub[k],raw[k],equal_nan=True) for k in pub.files if k.startswith('outcome_')))
            grouped.setdefault(ctx['kappa'],[]).append(raw['outcome_mean_N'][:,:11].copy())
    check('d=0 demographic maps identical across all adult precisions',all(all(np.array_equal(v[0],a) for a in v[1:]) for v in grouped.values()))
    out={'pass':all(x['pass'] for x in checks),'checks':checks,'note':'Derived probability target5e-6; full-precision NPZ reference parity is exact. Display sampling is a subset, never interpolated data.'};(ROOT/'extended_verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[x for x in checks if not x['pass']]},indent=2))
    if not out['pass']:raise SystemExit(1)
if __name__=='__main__':main()
