"""Predeclared numerical checks for v2, including v1 parity and JS solver parity."""
from __future__ import annotations
import csv,json,math,subprocess
from pathlib import Path
import numpy as np
from model import ROOT,SCHEMA,config,scenario,sigma_a,loss,mu_f,r_inst,rhs,trajectory,batch_trajectory

def check(name,measured,tolerance=1e-8,detail=''):
    v=float(measured);return {'name':name,'pass':bool(math.isfinite(v) and v<=tolerance),'measured':v,'tolerance':tolerance,'detail':detail}

def main():
    checks=[];metrics={};base=config()
    baseline=json.loads((ROOT/'v1_reference_fixtures.json').read_text());v1_err=0;v1_analytic=0
    for x in baseline:
        q={**base,**x['config'],'drift_rate':0.,'sigma_floor':base['sigma_floor'],'sigma_ceiling':base['sigma_ceiling']};tr=trajectory(q)
        for key in ('F','A'):
            ref=np.array(x[key]);v1_err=max(v1_err,float(np.max(abs(tr[key]-ref)/np.maximum(1,abs(ref)))))
        v1_analytic=max(v1_analytic,abs(loss(0,q)-x['expected']['loss']),abs(mu_f(0,q)-x['expected']['mu_F']),abs(r_inst(0,q)-x['expected']['r0']))
    checks.append(check('g0_v1_trajectory_parity',v1_err,2e-6,'12 v1 fixtures; scaled by max(1, |reference state|)'))
    checks.append(check('g0_v1_analytic_parity',v1_analytic,1e-12))
    rows=list(csv.DictReader((ROOT/'sweep.csv').open()))
    metrics['main_horizon_records']=len(rows);metrics['main_trajectories']=len(rows)//3
    d0={}
    for r in rows:
        if float(r['d'])==0.:
            k=(r['scenario'],r['policy'],r['model'],r['tau_model_time'],r['horizon_model_time'])
            d0.setdefault(k,[]).append(float(r['N_T_density']))
    d0_abs=max(max(v)-min(v) for v in d0.values())
    d0_scaled=max((max(v)-min(v))/max(1,abs(np.mean(v))) for v in d0.values())
    checks.append(check('d0_drift_invariance_batched_scaled',d0_scaled,2e-7,'max spread across nine g values divided by max(1, mean N); batched adaptive steps depend on other cells'))
    single_d0=[]
    for g in (-.01,0.,.01):
        q=scenario(config(d=0.,tau=3.,drift_rate=g),'helpful')
        single_d0.append(trajectory(q,81)['N'])
    checks.append(check('d0_drift_invariance_individual',max(float(np.max(abs(single_d0[i]-single_d0[1]))) for i in (0,2)),1e-10,'single-trait DOP853 solves have identical RHS'))
    zero_effect={}
    for r in rows:
        if r['scenario']=='no_effect':
            k=(r['policy'],r['model'],r['tau_model_time'],r['horizon_model_time'])
            zero_effect.setdefault(k,[]).append(float(r['N_T_density']))
    no_effect_err=max(max(v)-min(v) for v in zero_effect.values())
    checks.append(check('k_error0_d_and_g_invariance',no_effect_err,1e-6))
    for g in (-.01,.01):
        p={**base,'drift_rate':g};s=np.array([sigma_a(t,p) for t in np.linspace(0,200,401)])
        monotonic=max(0,float(np.max(np.diff(s)))) if g>0 else max(0,float(-np.min(np.diff(s))))
        checks.append(check(f'sigma_monotonic_g_{g}',monotonic,1e-14))
        checks.append(check(f'sigma_bounds_g_{g}',max(0,p['sigma_floor']-min(s),max(s)-p['sigma_ceiling']),0))
    p={**base,'drift_rate':-.01,'policy':'copy'};cross=math.log(p['sigma_A']/p['sigma_I'])/p['drift_rate']
    before=mu_f(cross-1,{**p,'d':1})-mu_f(cross-1,{**p,'d':0});after=mu_f(cross+1,{**p,'d':1})-mu_f(cross+1,{**p,'d':0})
    checks.append(check('copy_mortality_effect_reverses_at_MSE_crossing',max(0,before)+max(0,-after)+abs(mu_f(cross,{**p,'d':1})-mu_f(cross,{**p,'d':0})),1e-12))
    metrics['helpful_decay_crossing_time']=cross
    # Compare stacked independent systems with an individual high-accuracy solve.
    batch_err=0
    for scenario_name,policy,model,g,d,tau in [('helpful','copy','M0',-.01,1.,20.),('noisy','blend','M1',.01,.5,3.),('biased','copy','M1',-.005,0.,.5),('cloned','blend','M0',.005,1.,3.)]:
        p=scenario(config(policy=policy,model=model,drift_rate=g),scenario_name)
        bt=batch_trajectory(p,np.array([d]),np.array([tau]));single=trajectory({**p,'d':d,'tau':tau})
        for bi,si in ((1,100),(2,200),(3,400)):
            for key in ('F','A'):
                batch_err=max(batch_err,abs(float(bt[key][0,bi])-float(single[key][si]))/max(1,abs(float(single[key][si]))))
    checks.append(check('batch_vs_individual_DOP853',batch_err,2e-6))
    # Stage transfer identity and all-zero absorption remain valid with changing advice.
    pure={**base,'beta_const':0.,'mu_F_base':0.,'k_error':0.,'mu_A':0.,'tau':2.,'drift_rate':-.01};tr=trajectory(pure,81)
    exact_f=80*np.exp(-tr['t']/2);exact_a=20+80*(1-np.exp(-tr['t']/2))
    checks.append(check('maturation_conserves_N_closed_form',max(float(np.max(abs(tr['F']-exact_f))),float(np.max(abs(tr['A']-exact_a))),float(np.max(abs(tr['N']-100)))),1e-6))
    dynamic=trajectory(base,81)
    checks.append(check('flux_identity_dynamic',np.max(abs(dynamic['net']-np.array([sum(rhs(t,(f,a),base)) for t,f,a in zip(dynamic['t'],dynamic['F'],dynamic['A'])]))),1e-12))
    zero={**base,'F_initial':0.,'A_initial':0.};checks.append(check('all_zero_absorbing',np.max(abs(trajectory(zero,11)['N'])),0))
    min_population=min(min(float(r['F_T_density']),float(r['A_T_density'])) for r in rows)
    checks.append(check('sweep_nonnegative',max(0,-min_population),0))
    rejected=0
    for p in ({**base,'tau':0},{**base,'d':1.1},{**base,'sigma_floor':.5},{**base,'sigma_ceiling':.2},{**base,'drift_rate':float('nan')}):
        try:trajectory(p,3)
        except ValueError:rejected+=1
    checks.append(check('invalid_ranges_rejected',5-rejected,0))
    # The JS model is exactly the code embedded into the HTML; direct Chrome parity is a separate gate.
    out=subprocess.run(['node','parity.js'],cwd=ROOT,text=True,capture_output=True)
    if out.returncode:raise RuntimeError(out.stderr or out.stdout)
    js=json.loads((ROOT/'js_parity.json').read_text())
    checks.append(check('js_scipy_trajectory_parity',js['max_scaled_error'],2e-5,'24 signed-drift fixtures; denominator max(1, |reference state|)'))
    checks.append(check('js_step_halving',js['max_halving_scaled'],2e-5))
    checks.append(check('js_analytic_moment_parity',js['max_analytic_error'],1e-11))
    refined=list(csv.DictReader((ROOT/'refined_sweep.csv').open()))
    coarse_summary=json.loads((ROOT/'summary.json').read_text())['contexts'];refine_metrics={}
    for g in (-.005,0.,.005):
        fine=[r for r in refined if float(r['drift_rate_per_time'])==g];top=max(fine,key=lambda x:float(x['r_200_per_time']))
        coarse=next(x for x in coarse_summary if x['scenario']=='helpful' and x['policy']=='copy' and x['model']=='M0' and x['drift_rate']==g)
        refine_metrics[str(g)]={'coarse_max_rT':coarse['max_r_T'],'refined_max_rT':float(top['r_200_per_time']),'refined_d':float(top['d']),'refined_tau':float(top['tau_model_time']),'tau_boundary':abs(float(top['tau_model_time'])-.5)<1e-12}
    metrics.update({'d0_batched_absolute_spread':d0_abs,'d0_batched_scaled_spread':d0_scaled,'g0_v1_scaled_error':v1_err,'batch_scaled_error':batch_err,'min_population':min_population,'js_parity':{k:v for k,v in js.items() if k!='cases'},'refinement':refine_metrics})
    status='PASS' if all(x['pass'] for x in checks) else 'FAIL'
    (ROOT/'verification.json').write_text(json.dumps({'status':status,'checks':checks,'metrics':metrics,'browser_ui':'pending'},indent=2)+'\n')
    print(json.dumps({'status':status,'failed':[x for x in checks if not x['pass']],'metrics':metrics},indent=2))

if __name__=='__main__':main()
