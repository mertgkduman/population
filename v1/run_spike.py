"""Regenerate all simulation data, reference fixtures, HTML, and machine-readable checks."""
from __future__ import annotations
import csv, hashlib, json, math, platform, subprocess
from datetime import datetime, timezone
from pathlib import Path
import numpy as np, scipy, plotly
from scipy.integrate import solve_ivp
from scipy.linalg import expm
from model import ROOT,SCHEMA,config,scenario,loss,mu_f,beta,beta_max,r0,equilibrium,invasion,flux,rhs,trajectory

def native(x):
    if isinstance(x,dict): return {k:native(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [native(v) for v in x]
    if isinstance(x,np.ndarray): return native(x.tolist())
    if isinstance(x,np.generic): return x.item()
    return x

def dump(name,x): (ROOT/name).write_text(json.dumps(native(x),indent=2,allow_nan=False)+'\n')

def check(name,value,tolerance=1e-8,detail=''):
    v=float(value); return {'name':name,'pass':bool(np.isfinite(v) and v<=tolerance),'measured':v,'tolerance':tolerance,'detail':detail}

def scientific_checks():
    c=[]; base=config(); ds=np.linspace(0,1,11)
    def outputs(p):
        t=trajectory(p,11)
        return np.array([loss(p),mu_f(p),r0(p),equilibrium(p)[2],t['N'][-1]])
    equal=scenario(base,'equal')
    c.append(check('copy_equal_MSE_flat',np.max(np.ptp([outputs({**equal,'d':float(d)}) for d in ds],axis=0)),1e-7))
    for policy in ('copy','blend'):
        values=[outputs({**base,'policy':policy,'d':0,**{k:scenario(base,s)[k] for k in ('sigma_A','bias_A','rho')}}) for s in ('helpful','equal','cloned','noisy','biased')]
        c.append(check(f'd0_adult_moments_{policy}',np.max(np.ptp(values,axis=0)),1e-7))
        clone=scenario(base,'cloned')
        c.append(check(f'cloned_{policy}_flat',np.max(np.ptp([outputs({**clone,'policy':policy,'d':float(d)}) for d in ds],axis=0)),1e-7))
        no=scenario(base,'no_effect')
        values=[outputs({**no,'policy':policy,'d':float(d)})[1:] for d in ds]
        c.append(check(f'k_error_zero_{policy}_flat',np.max(np.ptp(values,axis=0)),1e-7))
    helpful=scenario(base,'helpful'); noisy=scenario(base,'noisy')
    c.append(check('copy_helpful_muF_decreases',max(0,mu_f({**helpful,'d':1})-mu_f({**helpful,'d':0})),0))
    c.append(check('copy_noisy_muF_increases',max(0,mu_f({**noisy,'d':0})-mu_f({**noisy,'d':1})),0))
    c.append(check('equal_independent_blend_interior',abs(loss({**equal,'policy':'blend','d':.5})-.5),1e-12))
    pure={**base,'beta_const':0.,'mu_F_base':0.,'k_error':0.,'mu_A':0.,'tau':2.}
    tr=trajectory(pure,81); f=80*np.exp(-tr['t']/2); a=20+80*(1-np.exp(-tr['t']/2))
    c.append(check('zero_birth_death_maturation_closed_form',max(np.max(abs(tr['F']-f)),np.max(abs(tr['A']-a)),np.max(abs(tr['N']-100))),1e-7))
    p={**base,'tau':1.5,'T':10.,'d':.3}; m=1/p['tau']; u=mu_f(p); b=beta(p,0)
    matrix=np.array([[-m-u,b],[m,-p['mu_A']]])
    times=np.linspace(0,10,41)
    sol=solve_ivp(lambda t,y:matrix@y,(0,10),(80.,20.),method='DOP853',rtol=1e-10,atol=1e-12,t_eval=times)
    exact=np.array([expm(matrix*t)@np.array([80.,20.]) for t in times])
    c.append(check('fixed_resource_matrix_exponential',np.max(abs(sol.y.T-exact)),1e-6))
    c.append(check('dominant_eigenvalue_independent',abs(r0(p)-max(np.linalg.eigvals(matrix).real)),1e-12))
    persist={**base,'d':1.,'tau':3.}; f,a,n=equilibrium(persist); B,D,M=flux(persist,f,a)
    c.append(check('positive_equilibrium_flux_balance',max(abs(B-D),max(abs(v) for v in rhs(0,(f,a),persist))),1e-8))
    c.append(check('resident_self_invasion',abs(invasion(persist,persist)),1e-12))
    threshold={**base,'tau':3.,'d':.5}
    threshold['beta_const']=threshold['mu_A']*(1+mu_f(threshold)*threshold['tau'])*(threshold['K_S']+threshold['S0'])/threshold['S0']
    c.append(check('r0_zero_boundary',abs(r0(threshold)),1e-12))
    c.append(check('threshold_equilibrium_zero',equilibrium(threshold)[2],1e-12))
    near={**threshold,'beta_const':threshold['beta_const']*(1+1e-5)}; tn=trajectory(near,81)
    c.append(check('near_threshold_nonnegative',max(0,-float(min(tn['F'].min(),tn['A'].min()))),0))
    zero={**base,'F_initial':0.,'A_initial':0.}; tz=trajectory(zero,21)
    c.append(check('all_zero_absorbing',np.max(abs(tz['N'])),0))
    invalid=0
    for q in ({**base,'tau':0},{**base,'d':1.01},{**base,'rho':-1.01},{**base,'mu_A':-.1}):
        try: trajectory(q,3)
        except ValueError: invalid+=1
    c.append(check('invalid_ranges_rejected',4-invalid,0))
    # An arbitrary valid non-equilibrium trajectory verifies N'=B-D pointwise.
    t=trajectory(base,41)
    c.append(check('flux_identity',np.max(abs(t['net']-np.array([sum(rhs(tt,(ff,aa),base)) for tt,ff,aa in zip(t['t'],t['F'],t['A'])]))),1e-12))
    details={'near_threshold_r0':r0(near),'near_threshold_N_T':float(tn['N'][-1]),'near_threshold_N_star':equilibrium(near)[2],'helpful_muF_d0':mu_f({**helpful,'d':0}),'helpful_muF_d1':mu_f({**helpful,'d':1}),'noisy_muF_d0':mu_f({**noisy,'d':0}),'noisy_muF_d1':mu_f({**noisy,'d':1})}
    return c,details

def analytic_sweep():
    ds=np.linspace(0,1,SCHEMA['grids']['analytic_d']); ts=np.geomspace(.5,20,SCHEMA['grids']['analytic_tau'])
    columns=['scenario','model','policy','d','tau_model_time','loss_error_squared','mu_F_per_time','r0_per_time','delta_r0_per_time','N_star_density','survival_to_maturation']
    summaries={}; rows=[]
    for s in SCHEMA['scenarios']:
      for model in ('M0','M1'):
       for policy in ('copy','blend'):
        base=scenario(config(model=model,policy=policy),s); subset=[]
        for tau in ts:
         ref=r0({**base,'d':0.,'tau':float(tau)})
         for d in ds:
          p={**base,'d':float(d),'tau':float(tau)}
          item=[s,model,policy,float(d),float(tau),loss(p),mu_f(p),r0(p),r0(p)-ref,equilibrium(p)[2],1/(1+mu_f(p)*tau)]
          rows.append(item); subset.append(item)
        top=max(x[7] for x in subset); winners=[x for x in subset if abs(x[7]-top)<1e-10]
        summaries[f'{s}/{model}/{policy}']={'max_r0':top,'maximizers_count':len(winners),'d_range':[min(x[3] for x in winners),max(x[3] for x in winners)],'tau_range':[min(x[4] for x in winners),max(x[4] for x in winners)],'tau_boundary':any(abs(x[4]-.5)<1e-12 or abs(x[4]-20)<1e-12 for x in winners)}
    with (ROOT/'sweep_analytic.csv').open('w',newline='') as f: w=csv.writer(f);w.writerow(columns);w.writerows(rows)
    dump('sweep_analytic.json',{'columns':columns,'rows':rows})
    dump('summary.json',summaries)
    return summaries

def numeric_sweep():
    rows=[]; ds=np.linspace(0,1,25); ts=np.geomspace(.5,20,25)
    for model in ('M0','M1'):
      for tau in ts:
       for d in ds:
        p=scenario(config(model=model,d=float(d),tau=float(tau)),'helpful'); tr=trajectory(p,2); n=float(tr['N'][-1]); rows.append([model,float(d),float(tau),n,math.log(n/100)/p['T'] if n>0 else None])
    with (ROOT/'sweep_numeric.csv').open('w',newline='') as f: w=csv.writer(f);w.writerow(['model','d','tau_model_time','N_T_density','r_T_per_time']);w.writerows(rows)
    dump('sweep_numeric.json',{'columns':['model','d','tau_model_time','N_T_density','r_T_per_time'],'rows':rows})

def reference_series():
    fixtures=[]
    for model in ('M0','M1'):
      for policy in ('copy','blend'):
       for d,tau in ((0.,.5),(1.,20.),(.5,3.)):
        p=scenario(config(model=model,policy=policy,d=d,tau=tau),'helpful'); tr=trajectory(p)
        fixtures.append({'config':p,'t':tr['t'],'F':tr['F'],'A':tr['A'],'expected':{'loss':loss(p),'mu_F':mu_f(p),'r0':r0(p),'N_star':equilibrium(p)[2],'self_invasion':invasion(p,p) if equilibrium(p)[2]>0 else None}})
    dump('fixtures.json',fixtures)
    for model in ('M0','M1'):
      for d,tau,label in ((0.,3.,'d0'),(1.,3.,'d1'),(.5,.5,'fast'),(.5,20.,'slow')):
        p=scenario(config(model=model,d=d,tau=tau),'helpful'); tr=trajectory(p)
        dump(f'trajectory_{model}_{label}.json',{'config':p,'series':tr})
        with (ROOT/f'trajectory_{model}_{label}.csv').open('w',newline='') as f: w=csv.writer(f);w.writerow(tr.keys());w.writerows(zip(*tr.values()))

def build_html(run_id):
    bundle=Path(plotly.__file__).parent/'package_data'/'plotly.min.js'
    template=(ROOT/'dashboard_template.html').read_text()
    page=template.replace('/*__SCHEMA__*/',json.dumps(SCHEMA)).replace('/*__RUN_ID__*/',json.dumps(run_id)).replace('/*__SCIENCE__*/',(ROOT/'science.js').read_text()).replace('<!--__PLOTLY__-->','<script>'+bundle.read_text()+'</script>')
    (ROOT/'index.html').write_text(page)
    return {'plotly':plotly.__version__,'plotly_bundle_bytes':bundle.stat().st_size,'html_bytes':len(page.encode())}

def main():
    checks,details=scientific_checks(); summary=analytic_sweep(); numeric_sweep(); reference_series()
    run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    build=build_html(run_id)
    parity=subprocess.run(['node','parity.js'],cwd=ROOT,text=True,capture_output=True)
    if parity.returncode: raise RuntimeError(parity.stderr or parity.stdout)
    js=json.loads((ROOT/'browser_parity.json').read_text())
    checks.append(check('js_rk4_vs_scipy',js['max_scaled_error'],2e-5,'Node executes the exact science.js bundled in the browser; browser UI tested separately'))
    checks.append(check('js_rk4_step_halving',js['max_halving_scaled'],2e-5))
    checks.append(check('js_analytic_parity',js['max_analytic_error'],1e-9))
    status='PASS' if all(x['pass'] for x in checks) else 'FAIL'
    dump('verification.json',{'run_id':run_id,'status':status,'checks':checks,'details':details,'js_parity':js,'browser_ui':'pending browser test'})
    names=['schema.json','model.py','science.js','run_spike.py','parity.js','dashboard_template.html','index.html','sweep_analytic.csv','sweep_analytic.json','sweep_numeric.csv','sweep_numeric.json','fixtures.json','verification.json','browser_parity.json']
    manifest={'run_id':run_id,'timestamp_utc':datetime.now(timezone.utc).isoformat(),'label':'simulation data','units':SCHEMA['units'],'defaults':SCHEMA['defaults'],'solver':SCHEMA['solver'],'versions':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,**build},'sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names}}
    dump('run_manifest.json',manifest)
    print(json.dumps({'run_id':run_id,'status':status,'failed':[x for x in checks if not x['pass']],'details':details,'key_summaries':{k:summary[k] for k in ('helpful/M0/copy','helpful/M1/copy','equal/M0/copy','equal/M0/blend','noisy/M0/copy')},'js_parity':js},indent=2))

if __name__=='__main__': main()
