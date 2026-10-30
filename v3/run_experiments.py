"""Large batched v3 sweep, selected slices, trajectories, and offline dashboard build."""
from __future__ import annotations
import csv,hashlib,json,math,platform
from datetime import datetime,timezone
from pathlib import Path
import numpy as np,scipy,plotly
from model import ROOT,SCHEMA,config,scenario,deference,feature,sigma_a,loss,mu_f,r_inst,trajectory,batch_trajectory

def plain(x):
    if isinstance(x,dict):return {k:plain(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [plain(v) for v in x]
    if isinstance(x,np.ndarray):return plain(x.tolist())
    if isinstance(x,np.generic):return x.item()
    return x

def dump(name,obj):(ROOT/name).write_text(json.dumps(plain(obj),indent=2,allow_nan=False)+'\n')

def write_csv(name,columns,rows):
    with (ROOT/name).open('w',newline='') as f:w=csv.writer(f);w.writerow(columns);w.writerows(rows)

def main_matrix(run_id):
    e=SCHEMA['experiment'];scenarios=list(SCHEMA['scenarios']);policies=['copy','blend'];models=['M0','M1'];lds=e['lambda_d'];lqs=e['lambda_Q'];ds=np.linspace(0,1,e['d0_values']);taus=np.geomspace(e['tau_min'],e['tau_max'],e['tau_values']);hs=e['horizons'];shape=(len(scenarios),2,2,len(lds),len(lqs),len(ds),len(taus),len(hs))
    F=np.empty(shape,dtype=np.float64);A=np.empty_like(F);N=np.empty_like(F);rT=np.empty_like(F)
    selected_rate_pairs={(0.,0.),(.005,.005),(.02,.005),(.005,.02)}
    slice_columns=['run_id','scenario','policy','model','lambda_d','lambda_Q','d0','tau_model_time','N_200_density','r_200_per_time','matched_delta_r_200_per_time']
    slices=[];summary=[];n0=SCHEMA['defaults']['F_initial']+SCHEMA['defaults']['A_initial'];near_index=int(np.argmin(abs(taus-3)))
    for si,s in enumerate(scenarios):
      for pi,policy in enumerate(policies):
       for mi,model in enumerate(models):
        for li,ld in enumerate(lds):
         for qi,lq in enumerate(lqs):
          p=scenario(config(policy=policy,model=model,lambda_d=ld,lambda_Q=lq),s)
          batch=batch_trajectory(p,ds,taus,hs)
          f=batch['F'][:,1:].reshape(len(ds),len(taus),len(hs));a=batch['A'][:,1:].reshape(len(ds),len(taus),len(hs));n=f+a
          F[si,pi,mi,li,qi]=f;A[si,pi,mi,li,qi]=a;N[si,pi,mi,li,qi]=n
          local=np.log(np.maximum(n,np.finfo(float).tiny)/n0)/np.asarray(hs)[None,None,:]
          local[n<=0]=np.nan;rT[si,pi,mi,li,qi]=local
          z=local[:,:,2];top=float(np.nanmax(z));winners=np.argwhere(np.isfinite(z)&(abs(z-top)<=1e-8));win_d=ds[winners[:,0]];win_t=taus[winners[:,1]]
          summary.append({'scenario':s,'policy':policy,'model':model,'lambda_d':ld,'lambda_Q':lq,'max_r_200':top,'maximizers_count':len(winners),'d0_range':[float(win_d.min()),float(win_d.max())],'tau_range':[float(win_t.min()),float(win_t.max())],'tau_boundary':bool(np.any((abs(win_t-.5)<1e-12)|(abs(win_t-20)<1e-12))),'tau_near_3':float(taus[near_index]),'r_200_d0_at_tau3':float(z[0,near_index]),'r_200_d1_at_tau3':float(z[-1,near_index]),'matched_d1_minus_d0_at_tau3':float(z[-1,near_index]-z[0,near_index]),'N_200_d0_at_tau3':float(n[0,near_index,2]),'N_200_d1_at_tau3':float(n[-1,near_index,2])})
          if (ld,lq) in selected_rate_pairs:
           for di,d in enumerate(ds):
            for ti,tau in enumerate(taus):
             slices.append([run_id,s,policy,model,ld,lq,float(d),float(tau),float(n[di,ti,2]),float(z[di,ti]),float(z[di,ti]-z[0,ti])])
    np.savez_compressed(ROOT/'sweep.npz',F=F,A=A,N=N,r_T=rT,scenarios=np.asarray(scenarios),policies=np.asarray(policies),models=np.asarray(models),lambda_d=np.asarray(lds),lambda_Q=np.asarray(lqs),d0=ds,tau=taus,horizons=np.asarray(hs),run_id=np.asarray(run_id))
    dump('summary.json',{'run_id':run_id,'label':'simulation data','contexts':summary})
    columns=['scenario','policy','model','lambda_d','lambda_Q','max_r_200','maximizers_count','d0_min','d0_max','tau_min','tau_max','tau_boundary','tau_near_3','r_200_d0_at_tau3','r_200_d1_at_tau3','matched_d1_minus_d0_at_tau3','N_200_d0_at_tau3','N_200_d1_at_tau3']
    records=[[x['scenario'],x['policy'],x['model'],x['lambda_d'],x['lambda_Q'],x['max_r_200'],x['maximizers_count'],*x['d0_range'],*x['tau_range'],x['tau_boundary'],x['tau_near_3'],x['r_200_d0_at_tau3'],x['r_200_d1_at_tau3'],x['matched_d1_minus_d0_at_tau3'],x['N_200_d0_at_tau3'],x['N_200_d1_at_tau3']] for x in summary]
    write_csv('summary.csv',columns,records);write_csv('selected_slices.csv',slice_columns,slices)
    return summary,shape

def refined(run_id,summary):
    e=SCHEMA['experiment'];ds=np.linspace(0,1,e['refined_grid']);taus=np.geomspace(.5,20,e['refined_grid']);pairs=[(0.,0.),(.005,.005),(.02,.005),(.005,.02)];rows=[]
    for s in ('helpful','noisy'):
      for policy in ('copy','blend'):
       for model in ('M0','M1'):
        for ld,lq in pairs:
         p=scenario(config(policy=policy,model=model,lambda_d=ld,lambda_Q=lq),s);batch=batch_trajectory(p,ds,taus,(50.,100.,200.));n=batch['N'][:,-1].reshape(len(ds),len(taus));z=np.log(n/100)/200
         index=np.unravel_index(np.nanargmax(z),z.shape);coarse=next(x for x in summary if x['scenario']==s and x['policy']==policy and x['model']==model and x['lambda_d']==ld and x['lambda_Q']==lq)
         rows.append({'scenario':s,'policy':policy,'model':model,'lambda_d':ld,'lambda_Q':lq,'coarse_max_r_200':coarse['max_r_200'],'refined_max_r_200':float(z[index]),'refined_d0':float(ds[index[0]]),'refined_tau':float(taus[index[1]]),'tau_boundary':bool(index[1] in (0,len(taus)-1))})
    dump('refined_summary.json',{'run_id':run_id,'label':'simulation data','contexts':rows})
    cols=list(rows[0]);write_csv('refined_summary.csv',cols,[[x[k] for k in cols] for x in rows])
    return rows

def representative(run_id):
    cols=['run_id','scenario','policy','model','lambda_d','lambda_Q','d0','tau','t','F','A','N','B','D','M','net','per_capita','d_t','Q_t','sigma_A_t','loss_t','mu_F_t','r_inst_t'];rows=[];fixtures=[]
    pairs=[(0.,0.),(.005,.005),(.02,.005),(.005,.02)]
    for s in ('helpful','noisy'):
      for policy in ('copy','blend'):
       for model in ('M0','M1'):
        for ld,lq in pairs:
         for d0 in (0.,.5,1.):
          p=scenario(config(policy=policy,model=model,lambda_d=ld,lambda_Q=lq,d0=d0,tau=3.),s);tr=trajectory(p)
          for i in range(len(tr['t'])):rows.append([run_id,s,policy,model,ld,lq,d0,3.,*[float(tr[k][i]) for k in ('t','F','A','N','B','D','M','net','per_capita','d','Q','sigma_A','loss','mu_F','r_inst')]])
          if d0 in (0.,1.) and (ld,lq) in ((0.,0.),(.005,.005),(.02,.005),(.005,.02)):
              fixtures.append({'config':p,'t':tr['t'],'F':tr['F'],'A':tr['A'],'d':tr['d'],'Q':tr['Q'],'sigma_A':tr['sigma_A'],'loss':tr['loss'],'r_inst':tr['r_inst']})
    write_csv('representative_series.csv',cols,rows);dump('fixtures.json',fixtures)

def build_html(run_id,summary):
    bundle=Path(plotly.__file__).parent/'package_data'/'plotly.min.js';template=(ROOT/'dashboard_template.html').read_text()
    html=template.replace('/*__SCHEMA__*/',json.dumps(SCHEMA)).replace('/*__RUN_ID__*/',json.dumps(run_id)).replace('/*__SUMMARY__*/',json.dumps(summary)).replace('/*__SCIENCE__*/',(ROOT/'science.js').read_text()).replace('/*__APP__*/',(ROOT/'app.js').read_text()).replace('<!--__PLOTLY__-->','<script>'+bundle.read_text()+'</script>')
    (ROOT/'index.html').write_text(html)
    return {'plotly':plotly.__version__,'html_bytes':len(html.encode()),'plotly_bundle_bytes':bundle.stat().st_size}

def main():
    run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');summary,shape=main_matrix(run_id);ref=refined(run_id,summary);representative(run_id);build=build_html(run_id,summary)
    manifest={'run_id':run_id,'timestamp_utc':datetime.now(timezone.utc).isoformat(),'branch':'v3-time-coupled-copying','label':'simulation data','mechanism':'decreasing d(t), increasing adult feature Q(t); exactly two demographic ODE states','defaults':SCHEMA['defaults'],'units':SCHEMA['units'],'experiment':SCHEMA['experiment'],'solver':SCHEMA['solver'],'versions':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,**build},'main_trait_trajectories':int(np.prod(shape[:-1])),'main_horizon_records':int(np.prod(shape)),'refined_trait_trajectories':len(ref)*SCHEMA['experiment']['refined_grid']**2,'context_count':len(summary),'source_parent_branch':'v2-advice-drift'}
    dump('run_manifest.json',manifest)
    print(json.dumps({k:manifest[k] for k in ('run_id','main_trait_trajectories','main_horizon_records','refined_trait_trajectories','context_count')},indent=2))

if __name__=='__main__':main()
