"""Two demographic stages with endogenous bounded cultural confidence and learned trust.
All densities are continuous; the ODE exactly averages private/testimony Bernoulli events.
"""
from dataclasses import dataclass,asdict,replace
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import eigvals

@dataclass(frozen=True)
class Config:
    H:int=6
    p:float=.65
    juvenile_rate:float=1.
    adult_rate:float=.3
    transmission_error:float=.05
    mu_F:float=.03
    mu_A:float=.10
    error_death:float=.25
    adult_error_death:float=.10
    beta_base:float=.35
    beta_skill:float=.85
    K:float=1000.
    S0:float=1.
    KS:float=1.
    feedback:float=1.
    trust_temperature:float=1.5
    internalize:bool=True
    reset_maturation:bool=False
    payoff:bool=True
    initial_adult_correct:float=.8
    policy:str='fixed'
    dt:float=.1
    T:float=400.


def validate(c,d,tau):
    if not isinstance(c.H,(int,np.integer)) or isinstance(c.H,bool):raise ValueError('H must be integer')
    for key,val in asdict(c).items():
        if isinstance(val,(int,float)) and not np.isfinite(val):raise ValueError('finite parameters required: '+key)
    if not np.all(np.isfinite(d)) or not np.all(np.isfinite(tau)):raise ValueError('finite traits required')
    if not 0<=c.initial_adult_correct<=1 or c.trust_temperature<0:raise ValueError('initial probability / temperature')
    if not 0<=c.p<=1 or not 0<=c.transmission_error<=.5 or not 0<=c.feedback<=1:raise ValueError('probability range')
    if c.H<1 or c.K<=0 or c.KS<=0 or c.dt<=0 or c.T<=0:raise ValueError('positive scales')
    if c.policy not in ('fixed','private','oracle','rl'):raise ValueError('policy')
    if np.any(np.asarray(tau)<=0) or np.any((np.asarray(d)<0)|(np.asarray(d)>1)):raise ValueError('traits')
    if any(getattr(c,k)<0 for k in ('juvenile_rate','adult_rate','mu_F','mu_A','error_death','adult_error_death','beta_base','beta_skill','S0')):raise ValueError('rates')


def shape(c):return (2*c.H+1,5 if c.policy=='rl' else 1)

def initial(c,n=1):
    Z,R=shape(c);x=np.zeros((n,2,Z,R));x[:,0,c.H,R//2]=80
    k=min(2,c.H);x[:,1,c.H+k,R//2]=20*c.initial_adult_correct;x[:,1,c.H-k,R//2]=20*(1-c.initial_adult_correct)
    return x

def shift(x,dz,dr=0):
    """Reflecting score caps: a contradictory update always moves inward."""
    y=np.zeros_like(x)
    if dz==1:y[:,1:,:]+=x[:,:-1,:];y[:,-1,:]+=x[:,-1,:]
    elif dz==-1:y[:,:-1,:]+=x[:,1:,:];y[:,0,:]+=x[:,0,:]
    else:y=x.copy()
    if dr:
        w=np.zeros_like(y)
        if dr==1:w[:,:,1:]+=y[:,:,:-1];w[:,:,-1]+=y[:,:,-1]
        else:w[:,:,:-1]+=y[:,:,1:];w[:,:,0]+=y[:,:,0]
        y=w
    return y

def correct(c,theta):return (1+theta*np.sign(np.arange(-c.H,c.H+1)))/2

def environment(c,x,theta):
    A=x[:,1].sum((1,2));N=x.sum((1,2,3));q=np.divide((x[:,1]*correct(c,theta)[None,:,None]).sum((1,2)),A,out=np.full_like(A,.5),where=A>0)
    q=c.transmission_error+(1-2*c.transmission_error)*q
    S=c.S0/(1+N/c.K);return q,S/(c.KS+S)

def choice(c,d,q):
    if c.policy=='private':return np.zeros((len(q),1))
    if c.policy=='oracle':return (np.maximum(q,1-q)>c.p)[:,None].astype(float)
    if c.policy=='rl':return np.broadcast_to(1/(1+np.exp(-c.trust_temperature*np.arange(-2,3))),(len(q),5))
    return np.asarray(d).reshape(-1,1)

def maturation_survival(c,d,tau,q):
    """Newborn probability of reaching A if final advice q stays fixed.

    This conditional quantity is not a time-varying birth-cohort forecast.
    Score does not affect juvenile mortality; only RL trust must be retained.
    Solve the transient trust occupation times, then integrate maturation flux.
    """
    d,tau,q=np.broadcast_arrays(np.atleast_1d(d),np.atleast_1d(tau),np.atleast_1d(q))
    validate(c,d,tau)
    if np.any(~np.isfinite(q)) or np.any((q<0)|(q>1)):raise ValueError('advice probability')
    w=choice(c,d,q);qa=np.maximum(q,1-q) if c.policy=='oracle' else q
    accuracy=c.p+w*(qa[:,None]-c.p)
    mortality=c.mu_F+(c.error_death*(1-accuracy) if c.payoff else np.zeros_like(accuracy))
    m=1/tau
    if c.policy!='rl':return m/(m+mortality[:,0])
    out=[]
    for i in range(len(d)):
        J=-np.diag(m[i]+mortality[i])
        for r in range(5):
            for step,prob in ((1,q[i]),(-1,1-q[i])):
                rate=c.juvenile_rate*c.feedback*prob
                J[min(4,max(0,r+step)),r]+=rate;J[r,r]-=rate
        newborn=np.zeros(5);newborn[2]=1
        out.append(m[i]*np.linalg.solve(-J,newborn).sum())
    return np.asarray(out)

def metrics(c,x,d,tau,theta=1,env=None):
    q,res=environment(c,x,theta) if env is None else env
    w=choice(c,d,q);qa=np.maximum(q,1-q) if c.policy=='oracle' else q
    acc=c.p+w*(qa[:,None]-c.p);F=x[:,0].sum((1,2));A=x[:,1].sum((1,2));N=F+A
    ac=correct(c,theta)[None,:,None];pf=np.divide((x[:,0]*acc[:,None,:]).sum((1,2)),F,out=np.full_like(F,np.nan),where=F>0)
    qF=np.divide((x[:,0]*ac).sum((1,2)),F,out=np.full_like(F,np.nan),where=F>0);qA=np.divide((x[:,1]*ac).sum((1,2)),A,out=np.full_like(A,np.nan),where=A>0)
    muF=c.mu_F+(c.error_death*(1-acc) if c.payoff else 0)
    muA=c.mu_A+(c.adult_error_death*(1-ac) if c.payoff else 0)
    birth=(x[:,1]*(c.beta_base+(c.beta_skill*ac if c.payoff else 0))*res[:,None,None]).sum((1,2))
    DF=(x[:,0]*(muF[:,None,:] if np.ndim(muF) else muF)).sum((1,2));DA=(x[:,1]*muA).sum((1,2));M=F/np.asarray(tau)
    conf=np.divide((x[:,1]*np.abs(np.arange(-c.H,c.H+1))[None,:,None]).sum((1,2)),A,out=np.full_like(A,np.nan),where=A>0)
    # fraction retaining a nonzero initial belief after three verified opposing samples
    mask=(np.abs(np.arange(-c.H,c.H+1))>3)[None,:,None]
    dog=np.divide((x[:,1]*mask).sum((1,2)),A,out=np.full_like(A,np.nan),where=A>0)
    override=np.divide((x[:,0]*w[:,None,:]*(c.p*(1-qa)+(1-c.p)*qa)[:,None,None]).sum((1,2)),F,out=np.zeros_like(F),where=F>0)
    return dict(F=F,A=A,N=N,B=birth,D=DF+DA,DF=DF,DA=DA,M=M,per_capita=np.divide(birth-DF-DA,N,out=np.zeros_like(N),where=N>0),belief_F=qF,belief_A=qA,advice=q,public_F=pf,confidence=conf,dogmatism=dog,override=override,private_sampling=np.full_like(F,c.juvenile_rate),private_choice_on_conflict=1-np.divide((x[:,0]*w[:,None,:]).sum((1,2)),F,out=np.zeros_like(F),where=F>0))

def rhs(c,x,d,tau,theta=1,env=None,mutation=None):
    q,res=environment(c,x,theta) if env is None else env
    n=len(x);w=choice(c,d,q);qa=np.maximum(q,1-q) if c.policy=='oracle' else q
    F=x[:,0];A=x[:,1];ac=correct(c,theta)[None,:,None];acc=c.p+w*(qa[:,None]-c.p)
    mf=c.mu_F+(c.error_death*(1-acc) if c.payoff else 0);ma=c.mu_A+(c.adult_error_death*(1-ac) if c.payoff else 0)
    m=1/np.asarray(tau).reshape(-1,1,1);out=np.zeros_like(x)
    out[:,0]=-(m+(mf[:,None,:] if np.ndim(mf) else mf))*F;out[:,1]=m*F-ma*A
    if c.reset_maturation:
        out[:,1]-=m*F;out[:,1,c.H,shape(c)[1]//2]+=(m*F).sum((1,2))
    B=(A*(c.beta_base+(c.beta_skill*ac if c.payoff else 0))*res[:,None,None]).sum((1,2))
    if mutation is not None:B=B@mutation
    out[:,0,c.H,shape(c)[1]//2]+=B
    if c.policy!='rl':
        learn=acc[:,0] if c.internalize else np.full(n,c.p)
        up=np.where(theta==1,learn,1-learn)[:,None,None]
        out[:,0]+=c.juvenile_rate*(up*shift(F,1)+(1-up)*shift(F,-1)-F)
    else:
        # Actual Bernoulli outcome feedback: trust is an individual cognitive state, reset at birth.
        for priv in (0,1):
          for adv in (0,1):
            prob=((c.p if priv else 1-c.p)*(q if adv else 1-q))[:,None,None]
            for follow,weight in ((False,1-w),(True,w)):
                action=adv if follow else priv;stored=action if c.internalize else priv
                dz=int(theta*(2*stored-1));dr=2*adv-1
                mass=F*prob*weight[:,None,:]
                out[:,0]+=c.juvenile_rate*((1-c.feedback)*shift(mass,dz)+c.feedback*shift(mass,dz,dr)-mass)
    u=c.p if theta==1 else 1-c.p
    out[:,1]+=c.adult_rate*(u*shift(A,1)+(1-u)*shift(A,-1)-A)
    return out

def rkstep(c,x,d,tau,t,theta_fn,env=None,mutation=None,h=None):
    h=c.dt if h is None else h;th=theta_fn(t+h/2)
    f=lambda y:rhs(c,y,d,tau,th,env,mutation)
    k1=f(x);k2=f(x+h*k1/2);k3=f(x+h*k2/2);k4=f(x+h*k3)
    y=x+h*(k1+2*k2+2*k3+k4)/6
    if not np.all(np.isfinite(y)) or np.min(y)<-1e-9:raise FloatingPointError('invalid populations; reduce dt')
    return y

def run(c,d,tau,theta_fn=lambda t:1,points=201,x0=None):
    d,tau=np.broadcast_arrays(np.atleast_1d(d).astype(float),np.atleast_1d(tau).astype(float));validate(c,d,tau)
    x=initial(c,len(d)) if x0 is None else x0.copy();times=np.linspace(0,c.T,points);history=[];states=[];t=0.
    for target in times:
        while t<target-1e-10:
            h=min(c.dt,target-t);x=rkstep(c,x,d,tau,t,theta_fn,h=h);t+=h
        history.append(metrics(c,x,d,tau,theta_fn(target)));states.append(x.copy())
    data={k:np.stack([a[k] for a in history],axis=1) for k in history[0]};data['t']=times
    data['states']=np.stack(states,axis=1);return data

def generator(c,d,tau,q,res,theta=1):
    Z,R=shape(c);size=2*Z*R;basis=np.eye(size).reshape(size,2,Z,R)
    return rhs(c,basis,np.full(size,d),np.full(size,tau),theta,(np.full(size,q),np.full(size,res))).reshape(size,size).T

def equilibrium(c,d,tau,wrong=False):
    cc=replace(c,T=800,initial_adult_correct=.2 if wrong else c.initial_adult_correct)
    x=run(cc,[d],[tau],points=2)['states'][:,-1]
    for _ in range(5):
        residual=np.max(np.abs(rhs(c,x,[d],[tau])))/max(1,x.sum())
        if residual<1e-9:break
        x=run(replace(cc,T=800),[d],[tau],points=2,x0=x)['states'][:,-1]
    residual=np.max(np.abs(rhs(c,x,[d],[tau])))/max(1,x.sum())
    q,res=environment(c,x,1);G=generator(c,d,tau,q[0],res[0]);rate=float(np.max(eigvals(G).real))
    return x,float(q[0]),float(res[0]),rate,float(residual)
