"""Independent checks of exported maps, raw trajectories, and derived evidence."""
import json,gzip,csv,numpy as np
from pathlib import Path
from model import Config,maturation_survival
ROOT=Path(__file__).resolve().parent
checks=[]
def add(n,p,detail=None):checks.append({'name':n,'pass':bool(p),'detail':detail})
with gzip.open(ROOT/'dashboard_data.json.gz','rt') as f:p=json.load(f)
maxerr=0
for c in p['contexts']:
 r=np.load(ROOT/(c['id']+'.npz'))
 for key,values in c['series'].items():
  if key in r:
   maxerr=max(maxerr,float(np.max(abs(np.asarray(values)-r[key]))))
 rt=np.log(r['N'][:,-1]/r['N'][:,0])/400
 add(c['id']+'_rT_export',np.max(abs(np.asarray(c['metrics']['rT'])-rt))<6e-9)
 add(c['id']+'_stage_accounting',np.max(abs(r['N']-r['F']-r['A']))<1e-8)
 survival=np.asarray(c['metrics']['survival'])
 expected=maturation_survival(Config(**c['config']),r['d'],r['tau'],r['advice'][:,-1])
 add(c['id']+'_conditional_survival',np.all((survival>=0)&(survival<=1+1e-12)) and np.max(abs(survival-expected))<1e-10)
add('rounded_series_export',maxerr<6e-9,maxerr)
rows=list(csv.DictReader(open(ROOT/'sweep.csv')));add('table_grid_count',len(rows)==len(p['contexts'])*len(p['ds'])*len(p['taus']))
add('survival_csv_range',all(0<=float(x['survival'])<=1+1e-12 for x in rows))
repro=json.load(open(ROOT/'reproductive_value.json'));add('next_generation_eigenvalue_sign',all(x['sign_agreement'] for x in repro['benchmarks']))
conv=json.load(open(ROOT/'dynamic_convergence.json'));add('dynamic_step_halving',conv['max_absolute_rate_difference']<1e-7,conv)
null=json.load(open(ROOT/'no_truth_control.json'));add('no_truth_near_chance',max(abs(np.asarray(null['final_adult_accuracy'])-.5))<1e-4,null)
eq=json.load(open(ROOT/'resident_equilibria.json'));add('all_resident_equilibria_resolved',all(x['residual']<1e-8 and abs(x['self_invasion'])<1e-7 for x in eq.values()))
# Own-baseline half-recovery must be same source as CSV export.
for c in p['contexts']:
 if c['scenario']=='shock':
  a=[x for x in rows if x['model']==c['model'] and x['scenario']=='shock']
  add(c['id']+'_recovery_export',all((x['recovery']=='' and v is None) or (v is not None and float(x['recovery'])==v) for x,v in zip(a,c['metrics']['recovery'])))
out={'pass':all(x['pass'] for x in checks),'checks':checks};(ROOT/'artifact_verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[x for x in checks if not x['pass']]}))
if not out['pass']:raise SystemExit(1)
