"""Predeclared pilot, main factorial, refinements, stochastic replication, and selection."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json,gzip,csv,time,platform,hashlib
from pathlib import Path
from datetime import datetime,timezone
from dataclasses import asdict,replace
import numpy as np
import scipy
from scipy.linalg import eigvals
from model import *
ROOT=Path(__file__).resolve().parent
MODELS={'fixed':{},'public_only':{'internalize':False},'memoryless':{'H':1},'private':{'policy':'private'},'oracle':{'policy':'oracle'},'rl':{'policy':'rl'}}
SCENARIOS=['stable','shock','periodic','wrong_history','no_payoff']
def envfn(name):
    if name=='shock':return lambda t:1 if t<150 else -1
    if name=='periodic':return lambda t:1 if t<120 else (-1 if int((t-120)/60)%2==0 else 1)
    return lambda t:1

def cfg(model,scenario,**kw):
    args=dict(MODELS[model]);args.update(kw)
    if scenario=='wrong_history':args['initial_adult_correct']=.2
    if scenario=='no_payoff':args['payoff']=False
    return Config(**args)

def plain(x):
    if isinstance(x,dict):return {k:plain(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [plain(v) for v in x]
    if isinstance(x,np.ndarray):return plain(x.tolist())
    if isinstance(x,np.generic):return plain(x.item())
    if isinstance(x,float):return round(x,8) if np.isfinite(x) else None
    return x

def save(name,obj):
    (ROOT/name).write_text(json.dumps(plain(obj),indent=2,allow_nan=False)+'\n')
def table(name,rows):
    with (ROOT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def outcomes(r,c,ds,taus,scenario):
    T=c.T;n=r['N'];rT=np.log(n[:,-1]/n[:,0])/T
    maturity=maturation_survival(c,ds,taus,r['advice'][:,-1])
    rec=np.full(len(ds),np.nan)
    if scenario=='shock':
        start=np.searchsorted(r['t'],150)
        for i in range(len(ds)):
            for j in range(start,len(r['t'])-4):
                if np.all(r['belief_A'][i,j:j+5]>=.75):rec[i]=r['t'][j]-150;break
    out={k:r[k][:,-1] for k in ('N','belief_A','public_F','dogmatism','confidence')}
    out.update(rT=rT,survival=maturity,recovery=rec,long_run_growth=np.log(n[:,-1]/n[:,-21])/(r['t'][-1]-r['t'][-21]))
    return out

def main():
    rid=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');start=time.time()
    pilot=[]
    for name in ('fixed','public_only'):
      for scenario in ('stable','shock'):
        ds,taus=np.meshgrid(np.linspace(0,1,7),np.geomspace(.5,12,7),indexing='ij');c=cfg(name,scenario)
        r=run(c,ds.ravel(),taus.ravel(),envfn(scenario),points=81)
        pilot.append({'model':name,'scenario':scenario,'N_min':r['N'].min(),'N_max':r['N'].max(),'finite':bool(np.isfinite(r['states']).all())})
    save('pilot.json',pilot);print('PILOT',pilot,flush=True)
    dvals=np.linspace(0,1,17);tvals=np.geomspace(.5,12,19);DD,TT=np.meshgrid(dvals,tvals,indexing='ij');ds=DD.ravel();taus=TT.ravel();contexts=[];rows=[];eqs={};invrows=[];unique=0
    for name in MODELS:
      for scenario in SCENARIOS:
        c=cfg(name,scenario);inactive=name in ('private','oracle','rl');dr=np.zeros(len(tvals)) if inactive else ds;tr=tvals if inactive else taus
        r=run(c,dr,tr,envfn(scenario),points=81);unique+=len(dr)
        if inactive:
            r={k:(np.tile(v,(len(dvals),)+(1,)*(v.ndim-1)) if k!='t' else v) for k,v in r.items()}
        met=outcomes(r,c,ds,taus,scenario);met['delta_rT']=(met['rT'].reshape(len(dvals),len(tvals))-met['rT'][:len(tvals)]).ravel();met['invasion']=np.full(len(ds),np.nan)
        if scenario in ('stable','wrong_history','no_payoff'):
            x,q,res,selfrate,residual=equilibrium(c,.5,3,wrong=scenario=='wrong_history');persistent=x.sum()>1e-6 and residual<1e-8 and abs(selfrate)<1e-7
            eqs[name+'_'+scenario]={'N':float(x.sum()),'q':q,'resource_factor':res,'self_invasion':selfrate,'residual':residual,'persistent':persistent,'resident_d':.5,'resident_tau':3}
            if persistent:
                rates=[float(np.max(eigvals(generator(c,float(d),float(tau),q,res)).real)) for d,tau in zip(dr,tr)]
                met['invasion']=np.tile(rates,len(dvals)) if inactive else np.asarray(rates)
        cid=name+'_'+scenario
        np.savez_compressed(ROOT/(cid+'.npz'),d=ds,tau=taus,**r)
        keys=['F','A','N','B','D','M','DF','DA','belief_F','belief_A','public_F','advice','confidence','dogmatism','per_capita','private_sampling','override']
        contexts.append({'id':cid,'model':name,'scenario':scenario,'config':asdict(c),'metrics':met,'series':{k:r[k] for k in keys},'resident':eqs.get(cid),'d_inactive':inactive})
        for i,(d,tau) in enumerate(zip(ds,taus)):
            row={'run_id':rid,'model':name,'scenario':scenario,'d':d,'tau':tau,**{k:v[i] for k,v in met.items()}};rows.append(row)
        print('MAIN',cid,'N',float(met['N'].max()),'elapsed',round(time.time()-start,1),flush=True)
    table('sweep.csv',rows);save('resident_equilibria.json',eqs)
    refinements=[]
    for scenario in ('stable','shock'):
        DD,TT=np.meshgrid(np.linspace(0,1,33),np.geomspace(.5,12,37),indexing='ij');c=cfg('fixed',scenario)
        rr=run(c,DD.ravel(),TT.ravel(),envfn(scenario),points=81);mm=outcomes(rr,c,DD.ravel(),TT.ravel(),scenario);i=int(np.argmax(mm['rT']))
        refinements.append({'scenario':scenario,'cells':DD.size,'d_opt':DD.ravel()[i],'tau_opt':TT.ravel()[i],'rT_opt':mm['rT'][i],'tau_boundary':bool(i%37 in (0,36))})
        np.savez_compressed(ROOT/('refined_'+scenario+'.npz'),d=DD.ravel(),tau=TT.ravel(),**mm)
    save('refinement.json',refinements)
    # independent environmental seeds: common telegraph path for all candidate traits
    stoch=[];d9,t9=np.meshgrid([0.,.5,1.],[1.,3.,8.],indexing='ij')
    for phase,seeds in [('exploratory',range(100,120)),('confirmatory',range(1000,1020))]:
      for seed in seeds:
        rng=np.random.default_rng(seed);switches=np.cumsum(np.maximum(1,np.rint(rng.exponential(70,100))));fun=lambda t,s=switches:1 if np.searchsorted(s,t,side='right')%2==0 else -1
        for model in ('fixed','public_only','rl'):
            c=cfg(model,'stable',T=600);rr=run(c,d9.ravel(),t9.ravel(),fun,points=121)
            for i,(d,tau) in enumerate(zip(d9.ravel(),t9.ravel())):
                stoch.append({'phase':phase,'seed':seed,'model':model,'d':d,'tau':tau,'rT':np.log(rr['N'][i,-1]/100)/600,'N':rr['N'][i,-1],'mean_adult_accuracy':np.mean(rr['belief_A'][i]),'mean_persistence':np.mean(rr['dogmatism'][i])})
      print('SEEDS',phase,flush=True)
    table('stochastic.csv',stoch)
    # memory depth, feedback availability, faster adult correction, initial culture
    sens=[]
    for H in (1,3,6,9):
      for rate in (.1,.3,1.):
       for internalize in (True,False):
        c=Config(H=H,adult_rate=rate,internalize=internalize);r=run(c,[0,.5,1],[3,3,3],envfn('shock'),points=81)
        mm=outcomes(r,c,np.array([0,.5,1]),np.array([3,3,3]),'shock')
        for i,d in enumerate([0,.5,1]):sens.append({'kind':'memory_adult_rate','H':H,'adult_rate':rate,'internalize':internalize,'feedback':1,'d':d,**{k:v[i] for k,v in mm.items()}})
    for feedback in (0,.25,1):
        c=Config(policy='rl',feedback=feedback);r=run(c,[0],[3],envfn('shock'),points=81);mm=outcomes(r,c,np.array([0]),np.array([3]),'shock')
        sens.append({'kind':'rl_feedback','H':6,'adult_rate':.3,'internalize':True,'feedback':feedback,'d':0,**{k:v[0] for k,v in mm.items()}})
    table('sensitivity.csv',sens)
    payload={'run_id':rid,'ds':dvals,'taus':tvals,'t':np.linspace(0,400,81),'contexts':contexts,'hypotheses':json.loads((ROOT.parent/'evidence/predeclared_experiments.json').read_text())['hypotheses'],'evolution':{},'counts':{'main_unique_trajectories':unique,'main_view_cells':len(rows),'pilot':196,'refinement':2442,'stochastic':len(stoch),'sensitivity':len(sens)}}
    with gzip.open(ROOT/'dashboard_data.json.gz','wt') as f:json.dump(plain(payload),f,separators=(',',':'),allow_nan=False)
    save('run_manifest.json',{'run_id':rid,'timestamp':datetime.now(timezone.utc).isoformat(),'config':asdict(Config()),'counts':payload['counts'],'versions':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'runtime_seconds':time.time()-start,'label':'simulation data','seeds':{'exploratory':[100,119],'confirmatory':[1000,1019]},'solver':'deterministic Kolmogorov-demographic ODE, vectorized RK4 dt=.1; separate DOP853 verification'})
    print('DONE',payload['counts'],time.time()-start,flush=True)
if __name__=='__main__':main()
