"""Reference two-state model. Units and scenarios: schema.json."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parent
SCHEMA = json.loads((ROOT / 'schema.json').read_text())

def validate(p):
    positive = ('K_S','K_N','tau_learning','T','tau')
    nonnegative = ('sigma_I','sigma_A','mu_F_base','k_error','mu_A','S0','beta_const','beta_min','beta_gain','F_initial','A_initial')
    for key in positive + nonnegative + ('bias_A','rho','d'):
        if not np.isfinite(p[key]): raise ValueError(f'{key} must be finite')
    for key in positive:
        if p[key] <= 0: raise ValueError(f'{key} must be positive')
    for key in nonnegative:
        if p[key] < 0: raise ValueError(f'{key} must be nonnegative')
    if not 0 <= p['d'] <= 1 or not -1 <= p['rho'] <= 1: raise ValueError('d/rho out of range')
    if p['policy'] not in ('copy','blend') or p['model'] not in ('M0','M1'): raise ValueError('unknown policy/model')
    return p

def config(**kwargs):
    p = dict(SCHEMA['defaults']); p.update(kwargs)
    return validate(p)

def scenario(base, name):
    p = dict(base); p.update({k:v for k,v in SCHEMA['scenarios'][name].items() if k != 'label'}); p['scenario']=name
    return validate(p)

def loss(p):
    d=p['d']; i=p['sigma_I']**2; a=p['sigma_A']**2+p['bias_A']**2
    return (1-d)*i+d*a if p['policy']=='copy' else (1-d)**2*i+d**2*a+2*p['rho']*d*(1-d)*p['sigma_I']*p['sigma_A']

def mu_f(p): return p['mu_F_base']+p['k_error']*loss(p)

def beta_max(p):
    return p['beta_const'] if p['model']=='M0' else p['beta_min']+p['beta_gain']*p['tau']/(p['tau']+p['tau_learning'])

def beta(p,n):
    s=p['S0']/(1+n/p['K_N'])
    return beta_max(p)*s/(p['K_S']+s)

def dominant(m,u,v,b):
    return .5*(-(m+u+v)+np.sqrt((m+u-v)**2+4*m*b))

def r0(p): return dominant(1/p['tau'],mu_f(p),p['mu_A'],beta(p,0))

def equilibrium(p):
    if r0(p) <= 0: return (0.,0.,0.)
    required=p['mu_A']*(1+mu_f(p)*p['tau'])
    if required == 0: return (np.nan,np.nan,np.nan)  # no finite positive equilibrium
    n=p['K_N']*((p['S0']/p['K_S'])*(beta_max(p)/required-1)-1)
    a=n/(1+p['mu_A']*p['tau'])
    return (n-a,a,n)

def invasion(mutant,resident):
    n=equilibrium(resident)[2]
    if not np.isfinite(n) or n<=0: return np.nan
    return dominant(1/mutant['tau'],mu_f(mutant),mutant['mu_A'],beta(mutant,n))

def flux(p,f,a):
    b=beta(p,f+a)*a; d=mu_f(p)*f+p['mu_A']*a; m=f/p['tau']
    return b,d,m

def rhs(t,y,p):
    f,a=y; b,_,m=flux(p,f,a)
    return (b-m-mu_f(p)*f,m-p['mu_A']*a)

def trajectory(p,points=401):
    validate(p)
    t=np.linspace(0,p['T'],points)
    sol=solve_ivp(rhs,(0,p['T']),(p['F_initial'],p['A_initial']),args=(p,),method='DOP853',rtol=SCHEMA['solver']['python_rtol'],atol=SCHEMA['solver']['python_atol'],t_eval=t)
    if not sol.success: raise RuntimeError(sol.message)
    f,a=sol.y
    if np.min(sol.y)<-1e-8: raise RuntimeError('materially negative population')
    n=f+a; b,d,m=flux(p,f,a)
    return {'t':t,'F':f,'A':a,'N':n,'follower_fraction':np.divide(f,n,out=np.full_like(n,np.nan),where=n>0),'adult_fraction':np.divide(a,n,out=np.full_like(n,np.nan),where=n>0),'B':b,'D':d,'M':m,'net':b-d,'per_capita':np.divide(b-d,n,out=np.full_like(n,np.nan),where=n>0)}
