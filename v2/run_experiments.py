"""Run the predeclared signed-drift experiment matrix and build offline HTML."""
from __future__ import annotations
import csv,hashlib,json,math,platform,shutil
from datetime import datetime,timezone
from pathlib import Path
import numpy as np,scipy,plotly
from model import ROOT,SCHEMA,config,scenario,sigma_a,loss,mu_f,r_inst,trajectory,batch_trajectory

def plain(x):
    if isinstance(x,dict):return {k:plain(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [plain(v) for v in x]
    if isinstance(x,np.ndarray):return plain(x.tolist())
    if isinstance(x,np.generic):return x.item()
    return x

def dump(name,x):(ROOT/name).write_text(json.dumps(plain(x),indent=2,allow_nan=False)+'\n')

def write_csv(name,columns,rows):
    with (ROOT/name).open('w',newline='') as f:
        w=csv.writer(f);w.writerow(columns);w.writerows(rows)

def main_sweep(run_id):
    e=SCHEMA['experiment'];ds=np.linspace(0,1,e['d_values']);taus=np.geomspace(e['tau_min'],e['tau_max'],e['tau_values']);horizons=e['horizons']
    columns=['run_id','scenario','policy','model','drift_rate_per_time','d','tau_model_time','horizon_model_time','F_T_density','A_T_density','N_T_density','r_T_per_time','delta_r_T_matched_per_time','delta_r_T_vs_static_per_time','sigma_A_0','sigma_A_T','adult_MSE_T','loss_T','mu_F_T_per_time','r_inst_0_per_time','r_inst_T_per_time']
    rows=[]
    for s in SCHEMA['scenarios']:
      for policy in ('copy','blend'):
       for model in ('M0','M1'):
        for g in e['drift_rates']:
         p=scenario(config(policy=policy,model=model,drift_rate=g),s)
         batch=batch_trajectory(p,ds,taus,horizons)
         n_tau=len(taus)
         for hi,h in enumerate(horizons,1):
          baseline=SCHEMA['defaults']['F_initial']+SCHEMA['defaults']['A_initial']
          for j,(d,tau) in enumerate(zip(batch['d'],batch['tau'])):
           n=float(batch['N'][j,hi]);ref_n=float(batch['N'][j%n_tau,hi])
           rt=math.log(n/baseline)/h if n>0 else None
           ref_rt=math.log(ref_n/baseline)/h if ref_n>0 else None
           q={**p,'d':float(d),'tau':float(tau)};sa0=float(sigma_a(0,q));sat=float(sigma_a(h,q))
           rows.append([run_id,s,policy,model,g,float(d),float(tau),h,float(batch['F'][j,hi]),float(batch['A'][j,hi]),n,rt,rt-ref_rt if rt is not None and ref_rt is not None else None,None,sa0,sat,sat*sat+q['bias_A']**2,float(loss(h,q)),float(mu_f(h,q)),float(r_inst(0,q)),float(r_inst(h,q))])
    # Cross-rate contrast is explicitly separate from the within-rate matched-d contrast.
    keys={name:i for i,name in enumerate(columns)}
    static={(r[1],r[2],r[3],round(r[5],12),round(r[6],12),r[7]):r[11] for r in rows if r[4]==0}
    for r in rows:
        ref=static[(r[1],r[2],r[3],round(r[5],12),round(r[6],12),r[7])]
        r[13]=r[11]-ref if r[11] is not None and ref is not None else None
    write_csv('sweep.csv',columns,rows)
    dump('sweep.json',{'columns':columns,'rows':rows,'label':'simulation data','grid':'9 deference × 11 logarithmic tau, six scenarios, two policies, two maturation models, nine drift rates, three horizons'})
    summary=[]; near3=min(taus,key=lambda x:abs(x-3))
    for s in SCHEMA['scenarios']:
      for policy in ('copy','blend'):
       for model in ('M0','M1'):
        for g in e['drift_rates']:
         subset=[r for r in rows if r[1]==s and r[2]==policy and r[3]==model and r[4]==g and r[7]==200]
         top=max(r[11] for r in subset if r[11] is not None);winners=[r for r in subset if r[11] is not None and abs(r[11]-top)<=1e-8]
         near=[r for r in subset if abs(r[6]-near3)<1e-10]
         d0=next(r for r in near if r[5]==0);d1=next(r for r in near if r[5]==1)
         summary.append({'scenario':s,'policy':policy,'model':model,'drift_rate':g,'max_r_T':top,'maximizers_count':len(winners),'d_range':[min(r[5] for r in winners),max(r[5] for r in winners)],'tau_range':[min(r[6] for r in winners),max(r[6] for r in winners)],'tau_boundary':any(abs(r[6]-.5)<1e-12 or abs(r[6]-20)<1e-12 for r in winners),'tau_near_3':float(near3),'r_T_d0_at_tau3':d0[11],'r_T_d1_at_tau3':d1[11],'matched_d1_minus_d0_at_tau3':d1[12],'N_T_d0_at_tau3':d0[10],'N_T_d1_at_tau3':d1[10]})
    dump('summary.json',{'run_id':run_id,'label':'simulation data','contexts':summary})
    return rows,summary

def refined_sweeps(run_id):
    ds=np.linspace(0,1,25);taus=np.geomspace(.5,20,25);rows=[]
    for g in (-.005,0.,.005):
        p=scenario(config(policy='copy',model='M0',drift_rate=g),'helpful')
        b=batch_trajectory(p,ds,taus,(50.,100.,200.))
        for j,(d,tau) in enumerate(zip(b['d'],b['tau'])):
            n=float(b['N'][j,-1]);ref=float(b['N'][j%25,-1]);rt=math.log(n/100)/200 if n>0 else None;ref_rt=math.log(ref/100)/200 if ref>0 else None
            rows.append([run_id,g,float(d),float(tau),n,rt,rt-ref_rt if rt is not None and ref_rt is not None else None])
    columns=['run_id','drift_rate_per_time','d','tau_model_time','N_200_density','r_200_per_time','delta_r_200_matched_per_time']
    write_csv('refined_sweep.csv',columns,rows);dump('refined_sweep.json',{'columns':columns,'rows':rows,'label':'simulation data'})

def references():
    fixtures=[];series_rows=[];series_cols=['scenario','model','policy','drift_rate','d','tau','t','F','A','N','B','D','M','net','per_capita','sigma_A','loss','mu_F','r_inst']
    for g in (-.01,0.,.01):
      for model in ('M0','M1'):
       for policy in ('copy','blend'):
        for d,tau in ((0.,.5),(1.,20.)):
         p=scenario(config(drift_rate=g,model=model,policy=policy,d=d,tau=tau),'helpful');tr=trajectory(p)
         fixtures.append({'config':p,'t':tr['t'],'F':tr['F'],'A':tr['A'],'sigma_A':tr['sigma_A'],'loss':tr['loss'],'r_inst':tr['r_inst']})
    for g in (-.005,0.,.005):
      for model in ('M0','M1'):
       for policy in ('copy','blend'):
        for d in (0.,.5,1.):
         p=scenario(config(drift_rate=g,model=model,policy=policy,d=d,tau=3.),'helpful');tr=trajectory(p)
         for i in range(len(tr['t'])):
            series_rows.append(['helpful',model,policy,g,d,3.,*[float(tr[k][i]) for k in ('t','F','A','N','B','D','M','net','per_capita','sigma_A','loss','mu_F','r_inst')]])
    dump('fixtures.json',fixtures);write_csv('representative_series.csv',series_cols,series_rows)
    dump('representative_series.json',{'columns':series_cols,'rows':series_rows,'label':'simulation data'})
    baseline=ROOT.parent/'v1'/'fixtures.json'
    if baseline.exists():shutil.copy2(baseline,ROOT/'v1_reference_fixtures.json')

def build_html(run_id,summary):
    bundle=Path(plotly.__file__).parent/'package_data'/'plotly.min.js'
    template=(ROOT/'dashboard_template.html').read_text()
    page=template.replace('/*__SCHEMA__*/',json.dumps(SCHEMA)).replace('/*__RUN_ID__*/',json.dumps(run_id)).replace('/*__SUMMARY__*/',json.dumps(summary)).replace('/*__SCIENCE__*/',(ROOT/'science.js').read_text()).replace('<!--__PLOTLY__-->','<script>'+bundle.read_text()+'</script>')
    (ROOT/'index.html').write_text(page)
    return {'plotly':plotly.__version__,'html_bytes':len(page.encode()),'plotly_bundle_bytes':bundle.stat().st_size}

def main():
    run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    rows,summary=main_sweep(run_id);refined_sweeps(run_id);references();build=build_html(run_id,summary)
    manifest={'run_id':run_id,'timestamp_utc':datetime.now(timezone.utc).isoformat(),'branch':'v2-advice-drift','label':'simulation data','mechanism':'bounded externally prescribed adult advice sigma_A(t); two demographic ODE states','units':SCHEMA['units'],'defaults':SCHEMA['defaults'],'experiment':SCHEMA['experiment'],'solver':SCHEMA['solver'],'versions':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,**build},'trait_trajectories_main':len(rows)//3,'horizon_records_main':len(rows),'refined_trajectories':1875}
    dump('run_manifest.json',manifest)
    print(json.dumps({'run_id':run_id,'trait_trajectories_main':len(rows)//3,'horizon_records_main':len(rows),'refined_trajectories':1875,'contexts':len(summary)},indent=2))

if __name__=='__main__':main()
