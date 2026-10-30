"""V6: two demographic stages over private-evidence and held-conviction scores.

Numba accelerates explicit probability fluxes; it does not change the model.
Private cues move both scores. Accepted testimony moves only conviction.
All state arrays have shape (genotype, stage, private u, conviction b).
"""
from dataclasses import dataclass,asdict,replace
from functools import lru_cache
import numpy as np
from numba import njit
from scipy.linalg import eigvals

@dataclass(frozen=True)
class Config:
 H:int=3
 p:float=.65
 access:float=1.
 load:float=1.
 nu_private:float=1.
 nu_social:float=1.
 nu_adult:float=1.
 plasticity_F:float=1.
 plasticity_A:float=.1
 transmission_error:float=.05
 mu_F:float=.03
 mu_A:float=.10
 error_F:float=.25
 error_A:float=.10
 beta_base:float=.35
 beta_skill:float=.85
 query_cost:float=0.
 K:float=1000.
 S0:float=1.
 KS:float=1.
 adult_mode:str='update'
 audit_floor:float=.05
 audit_threshold:int=2
 policy:str='fixed'
 accept:bool=True
 override:bool=True
 conflict_only:bool=False
 reset:bool=False
 payoff:bool=True
 initial_correct:float=.8
 dt:float=.1
 T:float=600.

MODES={'update':0,'frozen':1,'audit':2}

def validate(c,d,tau):
 if not isinstance(c.H,(int,np.integer)) or isinstance(c.H,bool) or c.H<1:raise ValueError('positive integer H')
 if not isinstance(c.audit_threshold,(int,np.integer)) or c.audit_threshold<0:raise ValueError('audit threshold')
 for key,val in asdict(c).items():
  if isinstance(val,(int,float)) and not np.isfinite(val):raise ValueError('nonfinite '+key)
 if not .5<=c.p<1 or not 0<=c.access<=1 or not 0<=c.transmission_error<=.5 or not 0<=c.audit_floor<=1 or not 0<=c.initial_correct<=1:raise ValueError('probability')
 if any(getattr(c,k)<=0 for k in ('load','K','KS','dt','T')):raise ValueError('positive scale')
 if any(getattr(c,k)<0 for k in ('nu_private','nu_social','nu_adult','mu_F','mu_A','error_F','error_A','beta_base','beta_skill','query_cost','S0')):raise ValueError('nonnegative rate')
 if not 0<=c.plasticity_F<=1 or not 0<=c.plasticity_A<=1:raise ValueError('plasticity probability')
 if c.adult_mode not in MODES or c.policy not in ('fixed','oracle_gate'):raise ValueError('architecture')
 if np.any(~np.isfinite(d)) or np.any(~np.isfinite(tau)) or np.any(np.asarray(tau)<=0) or np.any((np.asarray(d)<0)|(np.asarray(d)>1)):raise ValueError('traits')

@lru_cache(None)
def packed(c):
 return np.array([c.nu_private*c.access/c.load,c.nu_social/c.load,c.nu_adult*c.access/c.load,c.transmission_error,c.mu_F,c.mu_A,c.error_F if c.payoff else 0,c.error_A if c.payoff else 0,c.beta_base,c.beta_skill if c.payoff else 0,c.query_cost,c.K,c.S0,c.KS,c.audit_floor,c.audit_threshold,c.policy=='oracle_gate',c.accept,c.override,c.conflict_only,c.reset,np.log(c.p/(1-c.p)),c.plasticity_F,c.plasticity_A],float)

@njit(cache=True)
def _env(x,theta,c,shared):
 n=x.shape[0];H=(x.shape[2]-1)//2;out=np.zeros((n,3))
 for i in range(n):
  A=0.;plus=0.;N=0.
  for u in range(2*H+1):
   for b in range(2*H+1):
    A+=x[i,1,u,b];N+=x[i,0,u,b]+x[i,1,u,b]
    plus+=x[i,1,u,b]*(1 if b>H else (0 if b<H else .5))
  out[i,0]=plus;out[i,1]=N;out[i,2]=A
 if shared:
  total=np.sum(out,axis=0)
  for i in range(n):out[i]=total
 for i in range(n):
  A=out[i,2];q=out[i,0]/A if A>0 else .5
  out[i,0]=c[3]+(1-2*c[3])*q
  S=c[12]/(1+out[i,1]/c[11]);out[i,1]=S/(c[13]+S);out[i,2]=(1.0 if A>0 else 0.0)
 return out

@njit(cache=True)
def _weights(u,H,d,theta,env,c):
 source=env[0];q=source if theta==1 else 1-source
 w=d
 if c[16]>0:
  private_confidence=1/(1+np.exp(-abs(u-H)*c[21]))
  w=1.0 if max(q,1-q)>private_confidence else 0.0
  if q<.5:source=1-source
 w*=env[2]
 return w,source

@njit(cache=True)
def _adult_query(b,H,mode,c):
 if mode==1:return 0.
 if mode==2:return c[2]*(1 if abs(b-H)<c[15] else c[14])
 return c[2]

@njit(cache=True)
def _rhs(x,d,tau,theta,cue_plus,c,modes,env,mutation):
 n=x.shape[0];H=(x.shape[2]-1)//2;Z=2*H+1;out=np.zeros_like(x);births=np.zeros(n)
 for i in range(n):
  m=1/tau[i]
  for u in range(Z):
   jplus=1. if u>H else (0. if u<H else .5)
   w,source=_weights(u,H,d[i],theta,env[i],c)
   act=w if c[18]>0 else 0.
   public_plus=(1-act)*jplus+act*source
   public_correct=public_plus if theta==1 else 1-public_plus
   mf=c[4]+c[6]*(1-public_correct)+c[10]*c[0]
   for b in range(Z):
    F=x[i,0,u,b];A=x[i,1,u,b]
    correct=(1 if b>H else (0 if b<H else .5)) if theta==1 else (0 if b>H else (1 if b<H else .5))
    queryA=_adult_query(b,H,modes[i],c);ma=c[5]+c[7]*(1-correct)+c[10]*queryA
    out[i,0,u,b]-=(m+mf)*F;out[i,1,u,b]-=ma*A
    if c[20]>0:out[i,1,H,H]+=m*F
    else:out[i,1,u,b]+=m*F
    births[i]+=env[i,1]*(c[8]+c[9]*correct)*A
    # Equal-quality private cues are encoded with stage-specific plasticity.
    # Query costs still use raw exposure rates, not accepted-update rates.
    for sign in (-1,1):
     prob=cue_plus if sign==1 else 1-cue_plus
     un=min(Z-1,max(0,u+sign));bn=min(Z-1,max(0,b+sign))
     fluxF=c[0]*c[22]*prob*F;fluxA=queryA*c[23]*prob*A
     out[i,0,u,b]-=fluxF;out[i,0,un,bn]+=fluxF
     out[i,1,u,b]-=fluxA;out[i,1,un,bn]+=fluxA
     # Acceptance can be experimentally separated from current public choice.
     social_weight=w if c[17]>0 else 0.
     if c[19]>0:social_weight*=1-jplus if sign==1 else jplus
     flux=c[1]*social_weight*(source if sign==1 else 1-source)*F
     out[i,0,u,b]-=flux;out[i,0,u,bn]+=flux
 total_birth=np.sum(births)
 for i in range(n):out[i,0,H,H]+=(1-mutation)*births[i]+mutation*total_birth/n
 return out

def initial(c,n=1):
 Z=2*c.H+1;x=np.zeros((n,2,Z,Z));x[:,0,c.H,c.H]=80
 h=min(2,c.H);x[:,1,c.H+h,c.H+h]=20*c.initial_correct;x[:,1,c.H-h,c.H-h]=20*(1-c.initial_correct)
 return x

def environment(c,x,theta=1,shared=False):return _env(np.asarray(x,float),theta,packed(c),shared)

def rhs(c,x,d,tau,theta=1,cue_plus=None,env=None,shared=False,modes=None,mutation=0.):
 n=len(x);dd=np.broadcast_to(np.asarray(d,float),(n,)).copy();tt=np.broadcast_to(np.asarray(tau,float),(n,)).copy()
 mm=np.full(n,MODES[c.adult_mode],dtype=np.int64) if modes is None else np.asarray(modes,dtype=np.int64)
 ee=environment(c,x,theta,shared) if env is None else np.broadcast_to(np.asarray(env,float),(n,3)).copy()
 pi=(c.p if theta==1 else 1-c.p) if cue_plus is None else cue_plus
 return _rhs(x,dd,tt,theta,pi,packed(c),mm,ee,mutation)

@njit(cache=True)
def _step(x,d,tau,theta,pi,c,modes,h,shared,mutation,fixed_env):
 def f(y):
  env=_env(y,theta,c,shared) if fixed_env.shape[0]==0 else fixed_env
  return _rhs(y,d,tau,theta,pi,c,modes,env,mutation)
 k1=f(x);k2=f(x+h*k1/2);k3=f(x+h*k2/2);k4=f(x+h*k3)
 out=x+h*(k1+2*k2+2*k3+k4)/6
 if not np.all(np.isfinite(out)) or np.min(out)<-1e-10:raise ValueError('unstable/nonfinite state; reduce dt, no clipping')
 return out

@njit(cache=True)
def _advance(x,d,tau,c,modes,start,end,dt,theta,pi,shared,mutation,fixed_env):
 t=start
 while t<end-1e-10:
  h=min(dt,end-t);x=_step(x,d,tau,theta,pi,c,modes,h,shared,mutation,fixed_env);t+=h
 return x

def metrics(c,x,d,tau,theta=1,shared=False,modes=None,env=None):
 n=len(x);Z=2*c.H+1;z=np.arange(-c.H,c.H+1);cc=(1+theta*np.sign(z))/2
 ee=environment(c,x,theta,shared) if env is None else np.broadcast_to(env,(n,3));pars=packed(c)
 modes=np.full(n,MODES[c.adult_mode],dtype=np.int64) if modes is None else np.asarray(modes)
 F=x[:,0].sum((1,2));A=x[:,1].sum((1,2));N=F+A
 div=lambda a,b:np.divide(a,b,out=np.full_like(b,np.nan),where=b>0)
 B=np.zeros(n);DF=np.zeros(n);DA=np.zeros(n);pub=np.zeros(n);conf=np.zeros(n);over=np.zeros(n);QF=pars[0]*F;QA=np.zeros(n)
 for i in range(n):
  for u in range(Z):
   jp=(1+np.sign(u-c.H))/2;w,source=_weights(u,c.H,float(d[i]),theta,ee[i],pars);wa=w if c.override else 0
   accplus=(1-wa)*jp+wa*source;acc=accplus if theta==1 else 1-accplus;fu=x[i,0,u].sum()
   conflict=jp*(1-source)+(1-jp)*source
   pub[i]+=fu*acc;conf[i]+=fu*conflict;over[i]+=fu*conflict*wa
   DF[i]+=fu*(c.mu_F+(c.error_F*(1-acc) if c.payoff else 0)+c.query_cost*pars[0])
   for b in range(Z):
    a=x[i,1,u,b];qa=_adult_query(b,c.H,int(modes[i]),pars);QA[i]+=a*qa
    DA[i]+=a*(c.mu_A+(c.error_A*(1-cc[b]) if c.payoff else 0)+c.query_cost*qa)
    B[i]+=ee[i,1]*(c.beta_base+(c.beta_skill*cc[b] if c.payoff else 0))*a
 out=dict(F=F,A=A,N=N,B=B,DF=DF,DA=DA,D=DF+DA,M=F/np.asarray(tau),per_capita=div(B-DF-DA,N),
  private_F=div((x[:,0]*cc[None,:,None]).sum((1,2)),F),private_A=div((x[:,1]*cc[None,:,None]).sum((1,2)),A),
  belief_F=div((x[:,0]*cc[None,None,:]).sum((1,2)),F),belief_A=div((x[:,1]*cc[None,None,:]).sum((1,2)),A),
  public_F=div(pub,F),advice=ee[:,0] if theta==1 else 1-ee[:,0],conflict=div(conf,F),override=div(over,conf),
  query_rate=div(QF+QA,N),query_F=div(QF,F),query_A=div(QA,A),query_cost=c.query_cost*(QF+QA),
  confidence=div((x[:,1]*abs(z)[None,None,:]).sum((1,2)),A),persistence=div((x[:,1]*(abs(z)>2)[None,None,:]).sum((1,2)),A),
  wrong_confidence=div((x[:,1]*((abs(z)>2)*(cc==0))[None,None,:]).sum((1,2)),A))
 return out

def run(c,d,tau,segments=None,points=81,x0=None,shared=False,modes=None,mutation=0.,fixed_env=None,save_states=True):
 d,tau=np.broadcast_arrays(np.atleast_1d(d).astype(float),np.atleast_1d(tau).astype(float));validate(c,d,tau)
 if not 0<=mutation<=1:raise ValueError('mutation probability')
 modes=np.full(len(d),MODES[c.adult_mode],dtype=np.int64) if modes is None else np.asarray(modes,dtype=np.int64)
 if modes.shape!=(len(d),) or np.any((modes<0)|(modes>2)):raise ValueError('adult modes')
 x=initial(c,len(d)) if x0 is None else np.asarray(x0,float).copy()
 if np.any(~np.isfinite(x)) or np.min(x)<0:raise ValueError('invalid initial density')
 # Segments: (start time, true theta ±1, actual probability of signed + private cue).
 segments=[(0.,1,c.p)] if segments is None else segments
 if segments[0][0]!=0 or any(s[1] not in (-1,1) or not 0<=s[2]<=1 for s in segments):raise ValueError('segments')
 if any(b[0]<=a[0] for a,b in zip(segments,segments[1:])):raise ValueError('segments ordered')
 ts=np.linspace(0,c.T,points);history=[];states=[];distF=[];distA=[];t=0.;j=0
 fe=np.empty((0,3)) if fixed_env is None else np.broadcast_to(np.asarray(fixed_env,float),(len(d),3)).copy()
 for target in ts:
  while t<target-1e-10:
   stop=min(target,segments[j+1][0] if j+1<len(segments) else target)
   x=_advance(x,d,tau,packed(c),modes,t,stop,c.dt,segments[j][1],segments[j][2],shared,mutation,fe);t=stop
   if j+1<len(segments) and t>=segments[j+1][0]-1e-10:j+=1
  while j+1<len(segments) and target>=segments[j+1][0]-1e-10:j+=1
  history.append(metrics(c,x,d,tau,segments[j][1],shared,modes,None if fixed_env is None else fe))
  distF.append(x[:,0].sum(axis=1));distA.append(x[:,1].sum(axis=1))
  if save_states:states.append(x.copy())
 out={k:np.stack([r[k] for r in history],axis=1) for k in history[0]};out['t']=ts
 out['distF']=np.stack(distF,axis=1);out['distA']=np.stack(distA,axis=1)
 if save_states:out['states']=np.stack(states,axis=1)
 out['final_state']=x.copy();return out

def generator(c,d,tau,env,theta=1,cue_plus=None):
 Z=2*c.H+1;n=2*Z*Z;basis=np.eye(n).reshape(n,2,Z,Z)
 return rhs(c,basis,np.full(n,d),np.full(n,tau),theta,cue_plus,env=env).reshape(n,n).T

def equilibrium(c,d,tau,initial_correct=None):
 cc=replace(c,T=800,initial_correct=c.initial_correct if initial_correct is None else initial_correct)
 x=initial(cc)
 for _ in range(6):
  x=run(cc,[d],[tau],points=2,x0=x,save_states=False)['final_state']
  residual=np.max(abs(rhs(c,x,[d],[tau])))/max(1,x.sum())
  if residual<1e-9:break
 env=environment(c,x)[0];rate=float(eigvals(generator(c,d,tau,env)).real.max())
 return dict(state=x,environment=env,N=float(x.sum()),residual=float(residual),self_rate=rate)

def survival(c,d,tau,env,theta=1,cue_plus=None):
 """Newborn maturation probability in a frozen resident information environment."""
 G=generator(c,d,tau,env,theta,cue_plus);n=G.shape[0]//2;e=np.zeros(n);e[c.H*(2*c.H+1)+c.H]=1
 return float((1/tau)*np.linalg.solve(-G[:n,:n],e).sum())


def stochastic_segments(c,rate,seed,start_theta=1):
 """Exact Poisson flip times, independent of traits; no discretized flip hazard."""
 if not np.isfinite(rate) or rate<0:raise ValueError('nonnegative environmental rate')
 if start_theta not in (-1,1):raise ValueError('initial environment')
 rng=np.random.default_rng(seed);t=0.;theta=start_theta
 out=[(0.,theta,c.p if theta==1 else 1-c.p)]
 if rate==0:return out
 while True:
  t+=rng.exponential(1/rate)
  if t>=c.T:break
  theta=-theta;out.append((float(t),theta,c.p if theta==1 else 1-c.p))
 return out
