"""Regenerate conditional survival from final advice, without rerunning trajectories."""
import csv,gzip,json
from pathlib import Path
import numpy as np
from model import Config,maturation_survival
from run_experiments import cfg
ROOT=Path(__file__).resolve().parent

def correct(payload):
    diagnostics=[]
    for context in payload['contexts']:
        c=Config(**context['config'])
        with np.load(ROOT/(context['id']+'.npz')) as raw:
            q=raw['advice'][:,-1];d=raw['d'];tau=raw['tau']
        probability=maturation_survival(c,d,tau,q)
        context['metrics']['survival']=probability.tolist()
        diagnostics.append({'context':context['id'],'min':float(probability.min()),'max':float(probability.max())})
    for scenario in ('stable','shock'):
        path=ROOT/('refined_'+scenario+'.npz')
        with np.load(path) as raw:data={k:raw[k] for k in raw.files}
        c=cfg('fixed',scenario);q=c.transmission_error+(1-2*c.transmission_error)*data['belief_A']
        data['survival']=maturation_survival(c,data['d'],data['tau'],q)
        np.savez_compressed(path,**data)
    report={'definition':'Newborn probability of reaching adulthood if final advice accuracy remains fixed; RL trust continues updating. Not a realized time-varying cohort estimate.',
            'supersedes':'Coarse trapezoidal integration of population-average hazards, which could exceed one. No trajectory, growth, invasion or selection result used this derived metric.',
            'checks':diagnostics,'pass':all(0<=x['min']<=x['max']<=1+1e-12 for x in diagnostics)}
    (ROOT/'survival_correction.json').write_text(json.dumps(report,indent=2)+'\n')
    return payload

if __name__=='__main__':
    payload=json.load(gzip.open(ROOT/'dashboard_data.json.gz','rt'));correct(payload)
    with gzip.open(ROOT/'dashboard_data.json.gz','wt') as f:json.dump(payload,f,separators=(',',':'),allow_nan=False)
    lookup={c['id']:c for c in payload['contexts']};counts={k:0 for k in lookup}
    with open(ROOT/'sweep.csv') as f:rows=list(csv.DictReader(f))
    for row in rows:
        key=row['model']+'_'+row['scenario'];i=counts[key];counts[key]+=1
        row['survival']=lookup[key]['metrics']['survival'][i]
    with open(ROOT/'sweep.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print('Corrected conditional survival across all maps, refinements and sweep exports.')
