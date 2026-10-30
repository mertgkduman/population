"""Finite-window rare-mutant growth in one nonfeedback resident environment."""
import numpy as np
from numba import njit
from model import _env, _rhs, initial, packed

@njit(cache=True)
def advance(x,d,tau,c,start,end,dt,theta,pi):
    modes=np.zeros(len(d),dtype=np.int64)
    def f(y):
        resident=_env(y[:1],theta,c,False)
        env=np.empty((len(d),3))
        for i in range(len(d)):env[i]=resident[0]
        return _rhs(y,d,tau,theta,pi,c,modes,env,0.)
    t=start
    while t<end-1e-10:
        h=min(dt,end-t)
        k1=f(x);k2=f(x+h*k1/2);k3=f(x+h*k2/2);k4=f(x+h*k3)
        x=x+h*(k1+2*k2+2*k3+k4)/6
        if np.min(x)<-1e-10 or not np.all(np.isfinite(x)):raise ValueError('unstable invasion integration')
        t+=h
    return x

def run_invasion(c,ds,taus,segments,times,resident=(.5,3.)):
    d=np.r_[resident[0],ds];tau=np.r_[resident[1],taus]
    x=initial(c,len(d));x[1:]/=100.
    logs=np.zeros(len(ds));hist=[];rn=[];t=0.;j=0
    for target in times:
        while t<target-1e-10:
            stop=min(target,segments[j+1][0] if j+1<len(segments) else target)
            x=advance(x,d,tau,packed(c),t,stop,c.dt,segments[j][1],segments[j][2]);t=stop
            if j+1<len(segments) and t>=segments[j+1][0]-1e-10:j+=1
        masses=x[1:].sum((1,2,3))
        if np.any(masses<=0):raise ValueError('undefined mutant log growth')
        logs+=np.log(masses);x[1:]/=masses[:,None,None,None]
        hist.append(logs.copy());rn.append(x[0].sum())
    return np.array(hist).T,np.array(rn)
