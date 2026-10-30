"""Shared-culture rare-mutant and explicit inheritance experiments."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json
from dataclasses import replace
import numpy as np
from scipy.linalg import eigvals
from numba import njit
from model import *
from model import _rhs,_env
from run_experiments import ROOT,config,save,table

STRATEGIES=[('private',0.,'retained'),('social',1.,'retained'),('frozen',1.,'frozen'),('audit',1.,'audit')]

def architecture_invasion():
 rows=[];resident_rows=[]
 for scenario in ('stable','noisy','sparse','load','no_cost','wrong_history'):
  for name,d,model in STRATEGIES:
   c=config(model,scenario);eq=equilibrium(c,d,3.)
   resident_rows.append(dict(scenario=scenario,resident=name,**{k:v for k,v in eq.items() if k!='state'}))
   valid=eq['residual']<1e-8 and abs(eq['self_rate'])<1e-7 and eq['N']>1e-6
   for mname,md,mmodel in STRATEGIES:
    cm=config(mmodel,scenario);rate=float(eigvals(generator(cm,md,3.,eq['environment'])).real.max()) if valid else None
    rows.append(dict(scenario=scenario,resident=name,mutant=mname,resident_d=d,mutant_d=md,tau=3.,rate=rate,resident_N=eq['N']))
 save('architecture_residents.json',resident_rows);table('architecture_invasion.csv',rows);print('architecture invasion',len(rows),flush=True)
 return rows

def pairwise():
 rows=[]
 for scenario in ('stable','noisy','sparse','load'):
  c=config('retained',scenario)
  for axis,values in [('d',np.linspace(0,1,9)),('tau',np.geomspace(.5,12,9))]:
   for rv in values:
    rd,rt=(rv,3.) if axis=='d' else (1.,rv);eq=equilibrium(c,rd,rt)
    for mv in values:
     md,mt=(mv,3.) if axis=='d' else (1.,mv)
     valid=eq['residual']<1e-8 and abs(eq['self_rate'])<1e-7
     rate=float(eigvals(generator(c,md,mt,eq['environment'])).real.max()) if valid else None
     rows.append(dict(scenario=scenario,axis=axis,resident=rv,mutant=mv,rate=rate,residual=eq['residual'],self_rate=eq['self_rate']))
 table('pairwise.csv',rows);print('pairwise',len(rows),flush=True);return rows

def competition():
 out=[]
 for scenario in ('stable','noisy','sparse','load','no_cost'):
  c=config('retained',scenario,T=2000.)
  d,tau=np.meshgrid([0.,.5,1.],[.5,3.,8.],indexing='ij');d=d.ravel();tau=tau.ravel()
  x=initial(c,len(d))/len(d);r=run(c,d,tau,x0=x,shared=True,mutation=.001,points=101,save_states=False)
  freq=r['N']/r['N'].sum(axis=0);out.append(dict(kind='d_tau',scenario=scenario,d=d,tau=tau,mutation=.001,t=r['t'],N=r['N'].sum(axis=0),frequency=freq,mean_d=d@freq,mean_tau=tau@freq,advice=r['advice'][0],claims='Explicit genetic inheritance of d,tau, uniform mutation. Finite-time frequencies, not an ESS proof.'))
  d=np.array([0.,1.,1.,1.]);tau=np.full(4,3.);modes=np.array([0,0,1,2]);x=initial(c,4)/4
  r=run(c,d,tau,x0=x,shared=True,modes=modes,mutation=0,points=101,save_states=False);freq=r['N']/r['N'].sum(axis=0)
  out.append(dict(kind='architectures',scenario=scenario,names=[x[0] for x in STRATEGIES],d=d,tau=tau,mutation=0,t=r['t'],N=r['N'].sum(axis=0),frequency=freq,mean_d=d@freq,mean_tau=tau@freq,advice=r['advice'][0],claims='Additional inherited architecture comparison at matched tau=3; policies are specified, not emergent dogmatism. Shared teachers/resources, equal initial frequencies, no mutation.'))
 save('competition.json',out);print('competition',len(out),flush=True);return out

@njit(cache=True)
def _repeat_env(e,n):
 out=np.empty((n,3))
 for i in range(n):out[i]=e[0]
 return out

@njit(cache=True)
def _rare_slice(R,Y,d,tau,c,start,end,dt,theta,pi,measure):
 modes=np.zeros(len(d),np.int64);rmodes=np.zeros(1,np.int64);rd=np.array([.5]);rt=np.array([3.]);logs=np.zeros(len(d));t=start
 while t<end-1e-10:
  h=min(dt,end-t)
  e1=_env(R,theta,c,False);E1=_repeat_env(e1,len(d))
  a=_rhs(R,rd,rt,theta,pi,c,rmodes,e1,0.);b=_rhs(Y,d,tau,theta,pi,c,modes,E1,0.)
  r2=R+h*a/2;y2=Y+h*b/2;e2=_env(r2,theta,c,False);E2=_repeat_env(e2,len(d))
  a2=_rhs(r2,rd,rt,theta,pi,c,rmodes,e2,0.);b2=_rhs(y2,d,tau,theta,pi,c,modes,E2,0.)
  r3=R+h*a2/2;y3=Y+h*b2/2;e3=_env(r3,theta,c,False);E3=_repeat_env(e3,len(d))
  a3=_rhs(r3,rd,rt,theta,pi,c,rmodes,e3,0.);b3=_rhs(y3,d,tau,theta,pi,c,modes,E3,0.)
  r4=R+h*a3;y4=Y+h*b3;e4=_env(r4,theta,c,False);E4=_repeat_env(e4,len(d))
  a4=_rhs(r4,rd,rt,theta,pi,c,rmodes,e4,0.);b4=_rhs(y4,d,tau,theta,pi,c,modes,E4,0.)
  R=R+h*(a+2*a2+2*a3+a4)/6;Y=Y+h*(b+2*b2+2*b3+b4)/6
  if np.min(R)<-1e-10 or np.min(Y)<-1e-10:raise ValueError('negative rare state')
  for j in range(len(d)):
   mass=np.sum(Y[j])
   if not np.isfinite(mass) or mass<=0:raise ValueError('invalid rare mass')
   if measure:logs[j]+=np.log(mass)
   Y[j]/=mass
  t+=h
 return R,Y,logs

def dynamic_run(seed,world,dt=.1,T=1000.,burn=300.):
 c=Config(dt=dt);eq=equilibrium(c,.5,3.);R=eq['state'];d,tau=np.meshgrid([0.,.5,1.],[1.,3.,8.],indexing='ij');d=d.ravel();tau=tau.ravel();Y=np.repeat(R/R.sum(),len(d),axis=0)
 rng=np.random.default_rng(seed);switch=[];t=0.
 while True:
  t+=rng.exponential(70)
  if t>=T:break
  switch.append(t)
 endpoints=sorted(set([0.,burn,T]+switch));logs=np.zeros(len(d));startN=None
 for start,end in zip(endpoints,endpoints[1:]):
  sign=1 if np.searchsorted(switch,start+1e-8)%2==0 else -1;theta=sign if world=='real_changes' else 1;pi=.65 if sign==1 else .35
  if start==burn:startN=R.sum()
  R,Y,inc=_rare_slice(R,Y,d,tau,packed(c),start,end,dt,theta,pi,start>=burn);logs+=inc
 resident_growth=np.log(R.sum()/startN)/(T-burn);rates=logs/(T-burn)
 return rates,resident_growth,d,tau

def dynamic():
 rows=[]
 for world in ('real_changes','channel_changes'):
  for seed in [2700,2701,2702,2703,2704,2705,3700,3701,3702,3703,3704,3705]:
   rate,res,d,tau=dynamic_run(seed,world)
   for i in range(len(d)):rows.append(dict(world=world,seed=seed,phase='explore' if seed<3000 else 'confirm',d=d[i],tau=tau[i],rate=rate[i],resident_rate=res,relative_rate=rate[i]-res))
 a,ra,_,_=dynamic_run(2700,'real_changes');b,rb,_,_=dynamic_run(2700,'real_changes',dt=.05)
 (ROOT/'dynamic_convergence.json').write_text(json.dumps({'max_absolute_difference':float(np.max(abs(a-b))),'self_relative':float(a[4]-ra),'half_self_relative':float(b[4]-rb),'dt':.1,'half_dt':.05},indent=2)+'\n')
 table('dynamic_invasion.csv',rows);print('dynamic',len(rows),flush=True);return rows

if __name__=='__main__':
 a=architecture_invasion();p=pairwise();c=competition();dy=dynamic()
 save('selection.json',{'architecture_invasion':a,'pairwise':p,'competition':c,'dynamic_invasion':dy,'resident_definition':'Homogeneous resident supplies all adult advice and resource limitation to each rare mutant. Mutant teacher contribution is excluded at rarity.','dynamic_definition':'Finite-window log growth after burn300 toT1000; self-relative rate is zero although finite-window resident net growth may not be zero.'})
