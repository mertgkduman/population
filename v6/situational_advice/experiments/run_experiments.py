"""Predeclared V6 factorial; actual numerical trajectories, not synthetic plots."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import csv,gzip,hashlib,json,platform,time
from dataclasses import asdict,replace
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import scipy,numba
from model import Config,run,stochastic_segments,equilibrium
from invasion import run_invasion

ROOT=Path(__file__).resolve().parent
SEEDS=list(range(71001,71009));PRECISIONS=[.55,.7,.85];KAPPAS=[0.,.01,.05,.2]
FIELDS=['F','A','N','B','D','DF','DA','M','per_capita','private_F','belief_A','public_F','local_private','local_advice']
PLOT_FIELDS=['F','A','N','B','D','M','private_F','belief_A','public_F','local_advice']
def clean(o):
    if isinstance(o,dict):return {k:clean(v) for k,v in o.items()}
    if isinstance(o,(list,tuple)):return [clean(v) for v in o]
    if isinstance(o,np.ndarray):return clean(o.tolist())
    if isinstance(o,np.generic):return clean(o.item())
    if isinstance(o,float):return round(o,9) if np.isfinite(o) else None
    return o
def save(path,value):Path(path).write_text(json.dumps(clean(value),indent=2,allow_nan=False)+'\n')
def context_id(pA,k):return 'local_p'+str(pA).replace('.','p')+'_k'+str(k).replace('.','p')
def recovery(r,segments,burn=200):
    ts=r['t'];n=r['N'].shape[0];hits=np.zeros(n);wait=np.zeros(n);events=0
    for j,(start,_,_) in enumerate(segments[1:],1):
        if start<burn:continue
        end=segments[j+1][0] if j+1<len(segments) else ts[-1]+1e-9
        ii=np.where((ts>=start)&(ts<end))[0];events+=1
        for cell in range(n):
            good=ii[r['belief_A'][cell,ii]>=.75]
            if len(good):hits[cell]+=1;wait[cell]+=ts[good[0]]-start
    fraction=hits/events if events else np.full(n,np.nan)
    conditional=np.divide(wait,hits,out=np.full(n,np.nan),where=hits>0)
    return fraction,conditional,events
def summarize(r,segments):
    t=r['t'];i=np.searchsorted(t,200);span=t[-1]-t[i]
    avg=lambda k:np.trapezoid(r[k][:,i:],t[i:],axis=1)/span
    out={'mean_N':avg('N'),'adult_accuracy':avg('belief_A'),'private_accuracy':avg('private_F'),'public_accuracy':avg('public_F'),'local_private_accuracy':avg('local_private'),'local_advice_accuracy':avg('local_advice'),'wrong_confidence':avg('wrong_confidence'),'mean_per_capita':avg('per_capita'),'N_T':r['N'][:,-1],
         'r_T':np.log(r['N'][:,-1]/r['N'][:,0])/t[-1], 'tail_growth':np.log(r['N'][:,-1]/r['N'][:,i])/span}
    mean=out['mean_N']
    out['abundance_cv']=np.sqrt(np.trapezoid((r['N'][:,i:]-mean[:,None])**2,t[i:],axis=1)/span)/mean
    out['recovery_fraction'],out['recovery_time'],_=recovery(r,segments)
    return out
def main():
    start=time.time();rid=datetime.now(timezone.utc).strftime('v6-local-%Y%m%dT%H%M%SZ')
    ds=np.linspace(0,1,9);taus=np.geomspace(.5,12,11);D,TT=np.meshgrid(ds,taus,indexing='ij');d=D.ravel();tau=TT.ravel()
    rows=[];contexts=[];paths={};times=np.linspace(0,600,151)
    pilot=[]
    published=ROOT.parent/'published';published.mkdir(exist_ok=True)
    pd,pt=np.meshgrid(np.linspace(0,1,5),np.geomspace(.5,12,5),indexing='ij')
    for pA in PRECISIONS:
        c=Config(context_A=pA,T=60)
        r=run(c,pd.ravel(),pt.ravel(),stochastic_segments(c,.05,SEEDS[0]),points=16)
        pilot.append({'p_A':pA,'min_state':float(r['states'].min()),'finite':bool(np.isfinite(r['states']).all())})
    save(ROOT/'pilot.json',pilot)
    for pA in PRECISIONS:
      for k in KAPPAS:
        c=Config(context_A=pA);cid=context_id(pA,k);raw={key:[] for key in FIELDS};ms={};invlogs=[];resN=[];context_paths=[]
        for seed in SEEDS:
            seg=stochastic_segments(c,k,seed);context_paths.append(seg)
            r=run(c,d,tau,seg,points=len(times),save_states=False)
            stats=summarize(r,seg)
            lg,rn=run_invasion(c,d,tau,seg,times)
            j=np.searchsorted(times,200);absolute=(lg[:,-1]-lg[:,j])/(times[-1]-times[j]);resident=np.log(rn[-1]/rn[j])/(times[-1]-times[j])
            stats['invasion_absolute']=absolute;stats['invasion_relative']=absolute-resident
            invlogs.append(lg);resN.append(rn)
            for key in raw:raw[key].append(r[key])
            for key,value in stats.items():ms.setdefault(key,[]).append(value)
            for i in range(len(d)):rows.append({'run_id':rid,'label':'simulation data','model':cid.split('_k')[0],'scenario':'k'+cid.split('_k')[1],'context_id':cid,'eta_A':.1,'p_A':pA,'kappa':k,'seed':seed,'d':d[i],'tau':tau[i],**{key:float(value[i]) for key,value in stats.items()}})
            print(cid,'seed',seed,'switches',len(seg)-1,'elapsed',round(time.time()-start,1),flush=True)
        raw={key:np.array(value) for key,value in raw.items()};ms={key:np.array(value) for key,value in ms.items()}
        np.savez_compressed(ROOT/(cid+'.npz'),d=d,tau=tau,t=times,seeds=SEEDS,invasion_log=np.array(invlogs),resident_N=np.array(resN),**raw,**{'outcome_'+key:value for key,value in ms.items()})
        n=len(SEEDS)
        def moments(a):
            valid=np.isfinite(a);count=valid.sum(0);mean=np.divide(np.where(valid,a,0).sum(0),count,out=np.full(a.shape[1:],np.nan),where=count>0)
            variance=np.divide(np.where(valid,(a-mean)**2,0).sum(0),count-1,out=np.zeros(a.shape[1:]),where=count>1)
            return mean,np.sqrt(variance),count
        metrics={}
        for key,value in ms.items():
            mean,sd,count=moments(value);metrics[key]=mean;metrics[key+'_se']=np.divide(sd,np.sqrt(count),out=np.full_like(sd,np.nan),where=count>0);metrics[key+'_n']=count
        metrics['delta_N']=metrics['mean_N']-np.tile(metrics['mean_N'][:len(taus)],len(ds))
        delta=ms['mean_N']-np.tile(ms['mean_N'][:,:len(taus)],(1,len(ds)))
        metrics['delta_N_se']=delta.std(0,ddof=1)/np.sqrt(n)
        metrics['private_accuracy']=metrics['local_private_accuracy'];metrics['local_advice']=metrics['local_advice_accuracy']
        series={key:{'sample':raw['local_private' if key=='private_F' else key][0]} for key in PLOT_FIELDS}
        np.savez_compressed(published/(cid+'.npz'),d=d,tau=tau,t=times,seeds=SEEDS,**{key:val[0] for key,val in raw.items()},**{'outcome_'+key:value for key,value in ms.items()})
        cx={'id':cid,'eta_A':.1,'p_A':pA,'kappa':k,'config':asdict(c),'metrics':metrics,'series':series,'paths':context_paths,'resident':{'d':.5,'tau':3.,'same_plasticity':True},'seeds':SEEDS}
        contexts.append(cx);paths[cid]={str(seed):seg for seed,seg in zip(SEEDS,context_paths)}
        save(ROOT/'progress.json',{'completed_contexts':[x['id'] for x in contexts],'elapsed':time.time()-start})
    with (ROOT/'sweep.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    save(ROOT/'environment_paths.json',paths)
    payload={'schema_version':2,'run_id':rid,'label':'simulation data','ds':ds,'taus':taus,'t':times,'scores':list(range(-Config().H,Config().H+1)),'seeds':SEEDS,'contexts':contexts,'burn_in':200,'observations':'map mean/SE over 8 histories; plot trajectories use one actual history; illustrative trajectory uses seed 71001; no stochastic extinction'}
    with gzip.open(ROOT/'dashboard_data.json.gz','wt') as f:json.dump(clean(payload),f,separators=(',',':'),allow_nan=False)
    manifest={'run_id':rid,'timestamp':datetime.now(timezone.utc).isoformat(),'config':asdict(Config()),'ds':ds,'taus':taus,'adult_context_precision':PRECISIONS,'kappa':KAPPAS,'seeds':SEEDS,'burn_in':200,'main_trajectories':len(contexts)*len(d)*len(SEEDS),'mutant_trajectories':len(contexts)*len(d)*len(SEEDS),'pilot_trajectories':75,'runtime_seconds':time.time()-start,'solver':'RK4 dt=.1; steps split exactly at all Poisson events and output times','versions':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'numba':numba.__version__},'units':{'time':'model_time','density':'continuous_population_density','kappa':'1/model_time','plasticity':'probability of encoding a cue','growth':'1/model_time'},'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'model.py',ROOT/'invasion.py',Path(__file__)]}}
    save(ROOT/'run_manifest.json',manifest);print('DONE',rid,'seconds',time.time()-start,flush=True)
if __name__=='__main__':main()
