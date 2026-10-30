"""Shared-cultural-environment invasion, inherited mutation-selection, and common-path exponents."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import numpy as np
from scipy.linalg import eigvals
from dataclasses import replace,asdict
from model import *
from run_experiments import ROOT,save,table,envfn,plain


def dynamic_invasion(c,ds,taus,theta_fn,T=1200,burn=400):
    ds=np.asarray(ds);taus=np.asarray(taus);r0,q,s,_,_=equilibrium(c,.5,3)
    x=np.concatenate([r0,np.repeat(r0/r0.sum(),len(ds),axis=0)])
    d=np.r_[.5,ds];tau=np.r_[3,taus];logs=np.zeros(len(ds));startN=None;t=0
    def f(t,y):
        th=theta_fn(t);q,res=environment(c,y[:1],th)
        return rhs(c,y,d,tau,th,(np.full(len(y),q[0]),np.full(len(y),res[0])))
    for i in range(round(T/c.dt)):
        h=c.dt;tht=t+h/2;k1=f(tht,x);k2=f(tht,x+h*k1/2);k3=f(tht,x+h*k2/2);k4=f(tht,x+h*k3);x+=h*(k1+2*k2+2*k3+k4)/6;t=(i+1)*h
        if x.min()<-1e-9:raise ValueError('negative dynamic invasion')
        mass=x[1:].sum((1,2,3));x[1:]/=mass[:,None,None,None]
        if t>burn+1e-9:logs+=np.log(mass)
        if abs(t-burn)<1e-8:startN=x[0].sum()
    absolute=logs/(T-burn);resident=np.log(x[0].sum()/startN)/(T-burn)
    return absolute,absolute-resident,resident


def competition(c,ds,taus,theta_fn,T=1200,mutation=.002,x0=None):
    n=len(ds);x=initial(c,n)/n if x0 is None else x0.copy();times=[];means=[];freqs=[];pop=[];qhist=[]
    # Small, explicit random mutation to any candidate genotype; genotype independent of culture.
    P=np.eye(n)*(1-mutation)+np.ones((n,n))*mutation/n
    def f(t,y):
        q,res=environment(c,y.sum(axis=0,keepdims=True),theta_fn(t));return rhs(c,y,ds,taus,theta_fn(t),(np.full(n,q[0]),np.full(n,res[0])),P)
    for i in range(round(T/c.dt)+1):
        t=i*c.dt
        if i%max(1,round(5/c.dt))==0:
            size=x.sum((1,2,3));fr=size/size.sum();times.append(t);freqs.append(fr);means.append([fr@ds,fr@taus]);pop.append(size.sum());qhist.append(environment(c,x.sum(axis=0,keepdims=True),theta_fn(t))[0][0])
        if i==round(T/c.dt):break
        h=c.dt;tm=t+h/2;k1=f(tm,x);k2=f(tm,x+h*k1/2);k3=f(tm,x+h*k2/2);k4=f(tm,x+h*k3);x+=h*(k1+2*k2+2*k3+k4)/6
        if x.min()<-1e-9:raise ValueError('negative competition')
    return {'t':times,'frequencies':freqs,'mean_traits':means,'N':pop,'advice':qhist,'d':ds,'tau':taus,'mutation':mutation,'final':x.sum((1,2,3))/x.sum()}


def main():
    c=Config(dt=.1);dvals=np.linspace(0,1,11);tauvals=np.geomspace(.5,12,11);pip=[];equilibria=[]
    for axis in ('d','tau'):
      vals=dvals if axis=='d' else tauvals
      for res in vals:
        dr,tr=(res,3) if axis=='d' else (.5,res);x,q,s,selfr,resid=equilibrium(c,dr,tr)
        equilibria.append({'axis':axis,'resident':res,'N':x.sum(),'q':q,'residual':resid,'self':selfr})
        for mut in vals:
            dm,tm=(mut,3) if axis=='d' else (.5,mut);fit=float(np.max(eigvals(generator(c,dm,tm,q,s)).real))
            pip.append({'axis':axis,'resident':res,'mutant':mut,'invasion':fit})
    table('pairwise_invasion.csv',pip);save('pairwise_residents.json',equilibria)
    ds,taus=np.meshgrid(np.linspace(0,1,5),np.geomspace(.5,12,5),indexing='ij');ds=ds.ravel();taus=taus.ravel()
    comps={}
    for name,fun in [('stable',lambda t:1),('periodic',envfn('periodic'))]:
        comps[name]=competition(c,ds,taus,fun);print('COMPETITION',name,comps[name]['mean_traits'][-1],flush=True)
    comps['no_payoff']=competition(replace(c,payoff=False),ds,taus,lambda t:1)
    save('competition.json',comps)
    dyn=[];dd,tt=np.meshgrid([0,.5,1],[1,3,8],indexing='ij');d=dd.ravel();tau=tt.ravel()
    for seed in [-1,2000,2001,2002,2003,2004,3000,3001,3002,3003,3004]:
        if seed==-1:fn=envfn('periodic')
        else:
            rng=np.random.default_rng(seed);sw=np.cumsum(np.maximum(1,np.rint(rng.exponential(70,100))));fn=lambda t,sw=sw:1 if np.searchsorted(sw,t,side='right')%2==0 else -1
        absr,rel,rr=dynamic_invasion(c,d,tau,fn)
        for i in range(len(d)):dyn.append({'seed':seed,'d':d[i],'tau':tau[i],'absolute_log_growth':absr[i],'relative_log_growth':rel[i],'resident_log_growth':rr})
        print('DYNAMIC',seed,'self rel',rel[4],flush=True)
    table('dynamic_invasion.csv',dyn)
    # Check nonstationary integration convergence on same periodic history.
    a,b,r=dynamic_invasion(replace(c,dt=.05),d,tau,envfn('periodic'))
    first=np.array([x['relative_log_growth'] for x in dyn[:9]])
    save('dynamic_convergence.json',{'max_absolute_rate_difference':np.max(abs(b-first)),'dt':.1,'half_dt':.05,'self_relative':b[4]})
    # No mathematical ESS declared on finite mutation grid; compare local invasion around final maximum.
    k=int(np.argmax(comps['stable']['final']));dd0=float(ds[k]);tt0=float(taus[k]);x,q,s,_,_=equilibrium(c,dd0,tt0)
    neighbor=[]
    for dm in np.unique(np.clip([dd0-.05,dd0,dd0+.05],0,1)):
      for tm in [max(.1,tt0*.9),tt0,tt0*1.1]:neighbor.append({'d':dm,'tau':tm,'invasion':float(np.max(eigvals(generator(c,dm,tm,q,s)).real))})
    save('local_invasion.json',{'candidate_d':dd0,'candidate_tau':tt0,'N':x.sum(),'neighbors':neighbor,'claim':'candidate only; positive neighbors refute local uninvadability'})
    print('EVOLUTION DONE',flush=True)
if __name__=='__main__':main()
