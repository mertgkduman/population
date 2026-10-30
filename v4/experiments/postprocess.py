"""Derive interpretable recovery and wrong-confidence metrics from saved raw data."""
import gzip,json,csv
import numpy as np
from model import *
from run_experiments import ROOT,envfn,table
with gzip.open(ROOT/'dashboard_data.json.gz','rt') as f:payload=json.load(f)
from correct_survival import correct
correct(payload)
by={x['id']:x for x in payload['contexts']};times=np.asarray(payload['t']);start=np.searchsorted(times,150)
for context in payload['contexts']:
 if context['scenario']!='shock':continue
 q=np.asarray(context['series']['belief_A']);baseline=np.asarray(by[context['model']+'_stable']['series']['belief_A'])
 target=.5+.5*(baseline[:,-1]-.5);rec=np.full(len(q),np.nan);chance=rec.copy()
 for i in range(len(q)):
  for j in range(start,len(times)-4):
   if np.isnan(chance[i]) and np.all(q[i,j:j+5]>=.5):chance[i]=times[j]-150
   if np.all(q[i,j:j+5]>=target[i]):rec[i]=times[j]-150;break
 debt=np.trapezoid(np.maximum(0,baseline[:,start:]-q[:,start:]),times[start:],axis=1)
 context['metrics'].setdefault('recovery_absolute75',context['metrics']['recovery'])
 context['metrics']['recovery']=[float(x) if np.isfinite(x) else None for x in rec]
 context['metrics']['chance_recovery']=[float(x) if np.isfinite(x) else None for x in chance]
 context['metrics']['adaptation_debt']=debt.tolist()
with gzip.open(ROOT/'dashboard_data.json.gz','wt') as f:json.dump(payload,f,separators=(',',':'))
rows=list(csv.DictReader(open(ROOT/'sweep.csv')))
for context in payload['contexts']:
 subset=[r for r in rows if r['model']==context['model'] and r['scenario']==context['scenario']]
 for i,row in enumerate(subset):
  row['survival']=context['metrics']['survival'][i]
  row.setdefault('recovery_absolute75',row['recovery']);row['recovery']=context['metrics']['recovery'][i]
  row['wrong_high_confidence']=context['metrics'].get('wrong_high_confidence',[None]*len(subset))[i]
  row['peak_wrong_confidence']=context['metrics'].get('peak_wrong_confidence',[None]*len(subset))[i]
  row['adaptation_debt']=context['metrics'].get('adaptation_debt',[None]*len(subset))[i]
  row['chance_recovery']=context['metrics'].get('chance_recovery',[None]*len(subset))[i]
table('sweep.csv',rows)
# no truth-linked information or demographic selection: independent p=.5 and payoff off
c=Config(p=.5,payoff=False);rr=run(c,[0,.5,1],[3,3,3],envfn('shock'),points=81)
(ROOT/'no_truth_control.json').write_text(json.dumps({'p':.5,'payoff':False,'final_adult_accuracy':rr['belief_A'][:,-1].tolist(),'explanation':'initial cultural bias may decay to chance; no truth-linked innovation or differential survival'},indent=2)+'\n')
# Selected independent reproduction of invasion/abundance mismatch and low-density rate.
from scipy.linalg import eigvals
rows=[]
for name,c in [('default',Config()),('p06',Config(p=.6)),('p075',Config(p=.75)),('H3',Config(H=3)),('H9',Config(H=9))]:
 xr,q,s,sr,resid=equilibrium(c,1,3.19222305);xm,_,_,_,_=equilibrium(c,1,.74655056)
 fit=float(eigvals(generator(c,1,.74655056,q,s)).real.max());rows.append({'setting':name,'resident_tau':3.19222305,'mutant_tau':.74655056,'invasion':fit,'resident_N':float(xr.sum()),'mutant_monoculture_N':float(xm.sum())})
table('selection_out_of_sample.csv',rows)
print('POSTPROCESS DONE',flush=True)
