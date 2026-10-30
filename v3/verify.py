"""Predeclared scientific checks for the large v3 matrix."""
from __future__ import annotations
import json,math,subprocess
import numpy as np
from model import ROOT,SCHEMA,config,scenario,deference,feature,sigma_a,loss,mu_f,r_inst,rhs,trajectory,batch_trajectory

def check(name,value,tolerance=1e-8,detail=''):
    v=float(value);return {'name':name,'pass':bool(math.isfinite(v) and v<=tolerance),'measured':v,'tolerance':tolerance,'detail':detail}

def main():
    checks=[];metrics={};base=config();sweep=np.load(ROOT/'sweep.npz');N=sweep['N'];F=sweep['F'];A=sweep['A'];rT=sweep['r_T'];metrics['main_shape']=list(N.shape);metrics['main_trait_trajectories']=int(np.prod(N.shape[:-1]));metrics['main_horizon_records']=int(N.size)
    # V1 is the zero-rate corner: identical equations, fixed advice and deference.
    v1=json.loads((ROOT/'v1_reference_fixtures.json').read_text());v1scaled=0;v1analytic=0
    for x in v1:
        old=x['config'];q=config(d0=old['d'],tau=old['tau'],policy=old['policy'],model=old['model'],sigma_A0=old['sigma_A'],bias_A=old['bias_A'],rho=old['rho'],k_error=old['k_error'],lambda_d=0.,lambda_Q=0.)
        tr=trajectory(q)
        for key in ('F','A'):
            ref=np.asarray(x[key]);v1scaled=max(v1scaled,float(np.max(abs(tr[key]-ref)/np.maximum(1,abs(ref)))))
        v1analytic=max(v1analytic,abs(loss(0,q)-x['expected']['loss']),abs(mu_f(0,q)-x['expected']['mu_F']),abs(r_inst(0,q)-x['expected']['r0']))
    checks.append(check('zero_rates_v1_trajectory_parity',v1scaled,2e-6,'12 v1 fixtures, scaled by max(1, |reference state|)'))
    checks.append(check('zero_rates_v1_analytic_parity',v1analytic,1e-12))
    # Prescribed time functions must be monotone at all declared rate values.
    ts=np.linspace(0,200,401);max_d_increase=0;max_Q_decrease=0;max_sigma_increase=0
    for ld in SCHEMA['experiment']['lambda_d']:
      for lq in SCHEMA['experiment']['lambda_Q']:
        p={**base,'lambda_d':ld,'lambda_Q':lq};ds=deference(ts,p);qs=feature(ts,p);ss=sigma_a(ts,p)
        max_d_increase=max(max_d_increase,float(max(0,np.max(np.diff(ds)))))
        max_Q_decrease=max(max_Q_decrease,float(max(0,-np.min(np.diff(qs)))))
        max_sigma_increase=max(max_sigma_increase,float(max(0,np.max(np.diff(ss)))))
    checks.extend([check('deference_never_increases',max_d_increase,1e-14),check('adult_feature_never_decreases',max_Q_decrease,1e-14),check('adult_error_never_increases',max_sigma_increase,1e-14)])
    # Nulls in the full batched matrix. Adaptive batch steps create tiny absolute spreads.
    d0_values=N[:,:,:,:,:,0,:,:];spread=np.ptp(d0_values,axis=(3,4));level=np.mean(d0_values,axis=(3,4));d0scaled=float(np.max(spread/np.maximum(1,abs(level))))
    checks.append(check('d0_zero_quality_rate_null_scaled',d0scaled,2e-7,'spread over both rate axes; common d_floor=0'))
    no=N[4];spread=np.ptp(no,axis=(2,3,4));level=np.mean(no,axis=(2,3,4));noeffect=float(np.max(spread/np.maximum(1,abs(level))))
    checks.append(check('k_error_zero_null_scaled',noeffect,2e-7,'spread over d0 and both rate axes'))
    individual=[]
    for ld,lq in ((0,0),(.02,0),(0,.02),(.02,.02)):
        q=scenario(config(d0=0.,tau=3.,lambda_d=ld,lambda_Q=lq),'helpful');individual.append(trajectory(q,81)['N'])
    checks.append(check('d0_zero_individual_null',max(float(np.max(abs(x-individual[0]))) for x in individual[1:]),1e-9))
    biased=scenario(base,'biased');bias_margin=min(float(sigma_a(t,biased)**2+biased['bias_A']**2-biased['sigma_I']**2) for t in ts)
    checks.append(check('biased_copy_always_harmful',max(0,-bias_margin),0,'minimum adult MSE minus private MSE must stay positive'))
    noisy=scenario(config(d0=1.,lambda_d=.005,lambda_Q=.01,policy='copy'),'noisy');cross=math.log(2)/.01;before=mu_f(cross-1,noisy)-mu_f(cross-1,{**noisy,'d0':0});after=mu_f(cross+1,noisy)-mu_f(cross+1,{**noisy,'d0':0})
    checks.append(check('noisy_MSE_crossing_sign',max(0,-before)+max(0,after)+abs(sigma_a(cross,noisy)-1),1e-12))
    metrics['noisy_crossing_time_lambdaQ_0p01']=cross
    # Batch parity for selected cells and flux/transfer identities.
    batch_error=0
    for s,policy,model,ld,lq,d0,tau in [('helpful','copy','M0',.02,.005,1.,20.),('noisy','blend','M1',.005,.02,.5,3.),('biased','copy','M1',0,.02,0.,.5),('equal','blend','M0',.02,0,1.,3.)]:
        p=scenario(config(policy=policy,model=model,lambda_d=ld,lambda_Q=lq),s);batch=batch_trajectory(p,np.array([d0]),np.array([tau]));single=trajectory({**p,'d0':d0,'tau':tau})
        for bi,si in ((1,100),(2,200),(3,400)):
            for key in ('F','A'):
                batch_error=max(batch_error,abs(float(batch[key][0,bi])-float(single[key][si]))/max(1,abs(float(single[key][si]))))
    checks.append(check('batch_individual_DOP853_parity',batch_error,2e-6))
    pure={**base,'beta_const':0.,'mu_F_base':0.,'k_error':0.,'mu_A':0.,'tau':2.,'lambda_d':.02,'lambda_Q':.02};tr=trajectory(pure,81);exact_f=80*np.exp(-tr['t']/2);exact_a=20+80*(1-np.exp(-tr['t']/2))
    checks.append(check('maturation_conserves_N_closed_form',max(float(np.max(abs(tr['N']-100))),float(np.max(abs(tr['F']-exact_f))),float(np.max(abs(tr['A']-exact_a)))),1e-6))
    dynamic=trajectory(base,81);checks.append(check('flux_identity',np.max(abs(dynamic['net']-np.array([sum(rhs(t,(f,a),base)) for t,f,a in zip(dynamic['t'],dynamic['F'],dynamic['A'])]))),1e-12))
    zero={**base,'F_initial':0.,'A_initial':0.};checks.append(check('all_zero_absorbing',np.max(abs(trajectory(zero,11)['N'])),0))
    min_pop=float(min(np.min(F),np.min(A)));checks.append(check('sweep_nonnegative',max(0,-min_pop),0))
    finite=int(np.isfinite(N).sum()+np.isfinite(rT).sum());checks.append(check('all_main_outputs_finite',N.size*2-finite,0))
    expected=np.log(N/100)/np.asarray(SCHEMA['experiment']['horizons'])[None,None,None,None,None,None,None,:]
    checks.append(check('rT_definition',np.max(abs(rT-expected)),1e-12))
    rejected=0
    for p in ({**base,'d_floor':.9},{**base,'d0':1.1},{**base,'lambda_d':-.1},{**base,'lambda_Q':-.1},{**base,'Q_max':-.1},{**base,'tau':0},{**base,'rho':2}):
        try:trajectory(p,3)
        except ValueError:rejected+=1
    checks.append(check('invalid_parameters_rejected',7-rejected,0))
    # Grid refinement includes every coarse point (21 vs 41 logarithmic locations).
    refinements=json.loads((ROOT/'refined_summary.json').read_text())['contexts'];gap=max(0,max(x['coarse_max_r_200']-x['refined_max_r_200'] for x in refinements));checks.append(check('refined_max_at_least_coarse_max',gap,2e-7))
    proc=subprocess.run(['node','parity.js'],cwd=ROOT,text=True,capture_output=True)
    if proc.returncode:raise RuntimeError(proc.stderr or proc.stdout)
    js=json.loads((ROOT/'js_parity.json').read_text());checks.append(check('js_scipy_scaled_parity',js['max_scaled_error'],2e-5,'64 signed-rate fixtures; denominator max(1, |reference state|)'));checks.append(check('js_step_halving',js['max_halving_scaled'],2e-5));checks.append(check('js_analytic_parity',js['max_analytic_error'],1e-11))
    metrics.update({'v1_scaled_error':v1scaled,'d0_batch_scaled_spread':d0scaled,'no_effect_batch_scaled_spread':noeffect,'batch_scaled_error':batch_error,'minimum_population_density':min_pop,'refinement_max_coarse_minus_fine':gap,'js_parity':{k:v for k,v in js.items() if k!='cases'}})
    status='PASS' if all(c['pass'] for c in checks) else 'FAIL'
    (ROOT/'verification.json').write_text(json.dumps({'status':status,'checks':checks,'metrics':metrics,'browser_ui':'pending'},indent=2)+'\n')
    print(json.dumps({'status':status,'failed':[x for x in checks if not x['pass']],'metrics':metrics},indent=2))

if __name__=='__main__':main()
