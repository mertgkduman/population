"""Predeclared pilot and factorial V5 experiments. All outputs are simulation data."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json,gzip,csv,time,platform,hashlib
from pathlib import Path
from datetime import datetime,timezone
from dataclasses import asdict,replace
import numpy as np
import scipy,numba
from scipy.linalg import eigvals
from model import *
ROOT=Path(__file__).resolve().parent
MODELS={'retained':{},'frozen':{'adult_mode':'frozen'},'audit':{'adult_mode':'audit'},'reset':{'reset':True},'oracle':{'policy':'oracle_gate'}}
SCENARIOS={'stable':{},'clean':{'p':.85},'noisy':{'p':.55},'sparse':{'access':.2},'load':{'load':5.},'truth_reversal':{},'misinformation':{},'wrong_history':{'initial_correct':.2},'no_cost':{'query_cost':0.},'neutral':{'payoff':False,'query_cost':0.}}
def config(model,scenario,**kw):return Config(**(MODELS[model]|SCENARIOS[scenario]|kw))
def segments(c,scenario):
 if scenario=='truth_reversal':return [(0,1,c.p),(150,-1,1-c.p)]
 if scenario=='misinformation':return [(0,1,c.p),(150,1,.15),(210,1,c.p)]
 return [(0,1,c.p)]
def clean(o):
 if isinstance(o,dict):return {k:clean(v) for k,v in o.items()}
 if isinstance(o,(list,tuple)):return [clean(v) for v in o]
 if isinstance(o,np.ndarray):return clean(o.tolist())
 if isinstance(o,np.generic):return clean(o.item())
 if isinstance(o,float):return round(o,9) if np.isfinite(o) else None
 return o
def save(name,data):
 (ROOT/name).write_text(json.dumps(clean(data),indent=2,allow_nan=False)+'\n')
def table(name,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with (ROOT/name).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def outcomes(r,c):
 out={k:r[k][:,-1] for k in ('N','private_F','private_A','belief_F','belief_A','public_F','advice','confidence','persistence','wrong_confidence','query_rate','query_A','query_cost','override','conflict')}
 out['rT']=np.log(r['N'][:,-1]/r['N'][:,0])/c.T
 idx=int(np.searchsorted(r['t'],max(0.,c.T-100.)))
 out['tail_growth']=np.log(r['N'][:,-1]/r['N'][:,idx])/(r['t'][-1]-r['t'][idx])
 out['peak_wrong_confidence']=r['wrong_confidence'].max(axis=1)
 out['cumulative_query_cost']=np.trapezoid(r['query_cost'],r['t'],axis=1)
 return out

def main():
 start=time.time();rid=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 ds,taus=np.meshgrid(np.linspace(0,1,5),np.geomspace(.5,12,5),indexing='ij');pilot=[]
 for model in ('retained','frozen'):
  for scenario in ('stable','noisy','truth_reversal','misinformation'):
   c=config(model,scenario);r=run(c,ds.ravel(),taus.ravel(),segments(c,scenario),points=21)
   pilot.append({'model':model,'scenario':scenario,'min_state':r['states'].min(),'finite':bool(np.isfinite(r['states']).all()),'max_N':r['N'].max()})
 save('pilot.json',pilot);print('PILOT',len(pilot)*25,'elapsed',time.time()-start,flush=True)
 dvals=np.linspace(0,1,13);tvals=np.geomspace(.5,12,15);D,T=np.meshgrid(dvals,tvals,indexing='ij');ds=D.ravel();taus=T.ravel()
 # A common retained+updating resident per scenario; all candidate architectures encounter it.
 residents={}
 for scenario in SCENARIOS:
  if scenario in ('truth_reversal','misinformation'):continue
  c=config('retained',scenario);eq=equilibrium(c,.5,3)
  residents[scenario]={k:v for k,v in eq.items() if k!='state'}|{'d':.5,'tau':3.,'architecture':'retained'}
 save('residents.json',residents)
 contexts=[];rows=[];unique=0
 for model in MODELS:
  for scenario in SCENARIOS:
   c=config(model,scenario);inactive=model=='oracle';dr=np.zeros(len(tvals)) if inactive else ds;tr=tvals if inactive else taus
   r=run(c,dr,tr,segments(c,scenario),points=81,save_states=False);unique+=len(dr)
   if inactive:r={k:np.tile(v,(len(dvals),)+(1,)*(v.ndim-1)) if k!='t' else v for k,v in r.items()}
   met=outcomes(r,c);met['delta_rT']=(met['rT'].reshape(len(dvals),len(tvals))-met['rT'][:len(tvals)]).ravel()
   met['invasion']=np.full(len(ds),np.nan);met['survival']=np.empty(len(ds))
   envfinal=environment(c,r['final_state'],segments(c,scenario)[-1][1]);th=segments(c,scenario)[-1][1];pi=segments(c,scenario)[-1][2]
   for i,(d,tau) in enumerate(zip(dr,tr)):
    met['survival'][i]=survival(c,float(d),float(tau),envfinal[i],th,pi)
   if inactive:met['survival']=np.tile(met['survival'][:len(tvals)],len(dvals))
   if scenario in residents:
    eq=residents[scenario]
    if eq['N']>1e-6 and eq['residual']<1e-8 and abs(eq['self_rate'])<1e-7:
     rates=[float(eigvals(generator(c,float(d),float(tau),eq['environment'])).real.max()) for d,tau in zip(dr,tr)]
     met['invasion']=np.tile(rates,len(dvals)) if inactive else np.array(rates)
   cid=model+'_'+scenario;np.savez_compressed(ROOT/(cid+'.npz'),d=ds,tau=taus,**r)
   series={k:v for k,v in r.items() if k not in ('t','distF','distA','final_state')}
   contexts.append({'id':cid,'model':model,'scenario':scenario,'config':asdict(c),'segments':segments(c,scenario),'d_inactive':inactive,'resident':residents.get(scenario),'metrics':met,'series':series,'distF':r['distF'],'distA':r['distA']})
   for i,(d,tau) in enumerate(zip(ds,taus)):rows.append({'run_id':rid,'label':'simulation data','model':model,'scenario':scenario,'d':d,'tau':tau,**{k:v[i] for k,v in met.items()}})
   print('MAIN',cid,'maxN',float(met['N'].max()),'elapsed',round(time.time()-start,1),flush=True)
 # Baseline-relative transient metrics, not a universal arbitrary accuracy target.
 by={c['id']:c for c in contexts};times=r['t'];at=np.searchsorted(times,150)
 for cx in contexts:
  q=np.asarray(cx['series']['belief_A']);n=len(q);rec=np.full(n,np.nan);debt=np.zeros(n)
  if cx['scenario'] in ('truth_reversal','misinformation'):
   base=np.asarray(by[cx['model']+'_stable']['series']['belief_A']);target=.5+.5*(base[:,-1]-.5)
   debt=np.trapezoid(np.maximum(0,base[:,at:]-q[:,at:]),times[at:],axis=1)
   for i in range(n):
    for j in range(at,len(times)-4):
     if np.all(q[i,j:j+5]>=target[i]):rec[i]=times[j]-150;break
  cx['metrics']['recovery']=rec;cx['metrics']['accuracy_debt']=debt
  rr=[r for r in rows if r['model']==cx['model'] and r['scenario']==cx['scenario']]
  for i,row in enumerate(rr):row['recovery']=rec[i];row['accuracy_debt']=debt[i]
 table('sweep.csv',rows)
 payload={'schema_version':1,'run_id':rid,'label':'simulation data','ds':dvals,'taus':tvals,'t':times,'scores':list(range(-Config().H,Config().H+1)),'contexts':contexts,'counts':{'pilot':200,'main_unique_trajectories':unique,'main_view_cells':len(rows)},'hypotheses':[
 {'id':'H1','claim':'Scarce or noisy private evidence can alter the matched deference benefit.','status':'measured; inspect source scenarios'},
 {'id':'H2','claim':'Freezing may preserve knowledge or save queries; compare retained private learning and auditing.','status':'measured; architecture is imposed'},
 {'id':'H3','claim':'Misleading cues and true environmental reversal can reward opposite retention responses.','status':'measured with separate scenarios'},
 {'id':'H4','claim':'Identical observations without truth feedback cannot identify misinformation versus real change.','status':'independent exact-state control'},
 {'id':'H5','claim':'Shared-culture selection need not agree with isolated abundance.','status':'conditional invasion and competition'},
 {'id':'H6','claim':'Current override and persistent acceptance may have different causal effects.','status':'factorial ablation'}]}
 with gzip.open(ROOT/'dashboard_data.json.gz','wt') as f:json.dump(clean(payload),f,separators=(',',':'),allow_nan=False)
 manifest={'run_id':rid,'timestamp':datetime.now(timezone.utc).isoformat(),'counts':payload['counts'],'config':asdict(Config()),'models':MODELS,'scenarios':SCENARIOS,'versions':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'numba':numba.__version__},'runtime_seconds':time.time()-start,'solver':'RK4 dt=.1, exact segment boundaries; independent DOP853 verification','units':{'time':'model_time','population':'continuous_density','rates':'1/model_time','query_cost':'hazard per private query','load':'effective exposure divisor'}}
 save('run_manifest.json',manifest);print('DONE',manifest,flush=True)
if __name__=='__main__':main()
