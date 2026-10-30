"""Two demographic ODEs with prescribed decreasing deference and increasing advice quality."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp

ROOT=Path(__file__).resolve().parent
SCHEMA=json.loads((ROOT/'schema.json').read_text())

def validate(p):
    positive=('K_S','K_N','tau_learning','T','tau')
    nonnegative=('sigma_I','sigma_A0','mu_F_base','k_error','mu_A','S0','beta_const','beta_min','beta_gain','F_initial','A_initial','lambda_d','lambda_Q','Q0','Q_max','d0','d_floor')
    for key in positive+nonnegative+('bias_A','rho'):
        if not np.isfinite(p[key]):raise ValueError(f'{key} must be finite')
    for key in positive:
        if p[key]<=0:raise ValueError(f'{key} must be positive')
    for key in nonnegative:
        if p[key]<0:raise ValueError(f'{key} must be nonnegative')
    if not 0<=p['d_floor']<=p['d0']<=1:raise ValueError('require 0<=d_floor<=d0<=1')
    if p['Q_max']<p['Q0']:raise ValueError('Q_max must be at least Q0')
    if not -1<=p['rho']<=1:raise ValueError('rho out of range')
    if p['policy'] not in ('copy','blend') or p['model'] not in ('M0','M1'):raise ValueError('unknown policy/model')
    return p

def config(**changes):
    p=dict(SCHEMA['defaults']);p.update(changes);return validate(p)

def scenario(base,name):
    p=dict(base);p.update({k:v for k,v in SCHEMA['scenarios'][name].items() if k!='label'});p['scenario']=name
    return validate(p)

def deference(t,p,d0=None):
    initial=p['d0'] if d0 is None else d0
    return p['d_floor']+(initial-p['d_floor'])*np.exp(-p['lambda_d']*np.asarray(t))

def feature(t,p):return p['Q0']+(p['Q_max']-p['Q0'])*(1-np.exp(-p['lambda_Q']*np.asarray(t)))

def sigma_a(t,p):return p['sigma_A0']*(1+p['Q0'])/(1+feature(t,p))

def loss(t,p,d0=None):
    d=deference(t,p,d0);s=sigma_a(t,p);i=p['sigma_I']**2;a=s*s+p['bias_A']**2
    return (1-d)*i+d*a if p['policy']=='copy' else (1-d)**2*i+d*d*a+2*p['rho']*d*(1-d)*p['sigma_I']*s

def mu_f(t,p,d0=None):return p['mu_F_base']+p['k_error']*loss(t,p,d0)

def beta_max(p,tau=None):
    tau=p['tau'] if tau is None else tau
    return p['beta_const'] if p['model']=='M0' else p['beta_min']+p['beta_gain']*tau/(tau+p['tau_learning'])

def beta(n,p,tau=None):
    s=p['S0']/(1+n/p['K_N'])
    return beta_max(p,tau)*s/(p['K_S']+s)

def r_inst(t,p,d0=None,tau=None):
    tau=p['tau'] if tau is None else tau;m=1/tau;u=mu_f(t,p,d0);v=p['mu_A'];b=beta(0,p,tau)
    return .5*(-(m+u+v)+np.sqrt((m+u-v)**2+4*m*b))

def flux(t,f,a,p):
    b=beta(f+a,p)*a;death=mu_f(t,p)*f+p['mu_A']*a;m=f/p['tau']
    return b,death,m

def rhs(t,y,p):
    f,a=y;b,_,m=flux(t,f,a,p)
    return b-m-mu_f(t,p)*f,m-p['mu_A']*a

def trajectory(p,points=401):
    validate(p);ts=np.linspace(0,p['T'],points)
    sol=solve_ivp(rhs,(0,p['T']),(p['F_initial'],p['A_initial']),args=(p,),method=SCHEMA['solver']['python_method'],rtol=SCHEMA['solver']['python_rtol'],atol=SCHEMA['solver']['python_atol'],t_eval=ts)
    if not sol.success:raise RuntimeError(sol.message)
    f,a=sol.y
    if np.min(sol.y)<-1e-8:raise RuntimeError('materially negative population')
    n=f+a;b,death,m=flux(ts,f,a,p)
    return {'t':ts,'F':f,'A':a,'N':n,'B':b,'D':death,'M':m,'net':b-death,'per_capita':np.divide(b-death,n,out=np.full_like(n,np.nan),where=n>0),'d':deference(ts,p),'Q':feature(ts,p),'sigma_A':sigma_a(ts,p),'loss':loss(ts,p),'mu_F':mu_f(ts,p),'r_inst':r_inst(ts,p)}

def batch_trajectory(base,d0_values,taus,horizons=(50.,100.,200.)):
    """Stack independent copies of the two-state equations in one DOP853 solve."""
    validate(base);d_grid,tau_grid=np.meshgrid(d0_values,taus,indexing='ij');d0=d_grid.ravel();tau=tau_grid.ravel();n=d0.size
    if np.min(d0)<base['d_floor']:raise ValueError('d grid contains values below d_floor')
    y0=np.r_[np.full(n,base['F_initial']),np.full(n,base['A_initial'])]
    def f(t,y):
        F=y[:n];A=y[n:];s=base['S0']/(1+(F+A)/base['K_N']);birth=beta_max(base,tau)*s/(base['K_S']+s)*A
        u=mu_f(t,base,d0);m=F/tau
        return np.r_[birth-m-u*F,m-base['mu_A']*A]
    times=np.array([0.,*horizons],float)
    sol=solve_ivp(f,(0,max(horizons)),y0,method=SCHEMA['solver']['python_method'],rtol=SCHEMA['solver']['python_rtol'],atol=SCHEMA['solver']['python_atol'],t_eval=times)
    if not sol.success:raise RuntimeError(sol.message)
    if np.min(sol.y)<-1e-8:raise RuntimeError('materially negative batch population')
    return {'d0':d0,'tau':tau,'t':times,'F':sol.y[:n], 'A':sol.y[n:],'N':sol.y[:n]+sol.y[n:]}
