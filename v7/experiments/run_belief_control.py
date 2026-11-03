"""Register and run the final coherent proposition/habit control."""
from pathlib import Path
from datetime import datetime,timezone
import csv,gzip,hashlib,io,json,sys,tarfile
from v7.experiments.belief_control import train,adult,ARMS
ROOT=Path(__file__).resolve().parents[2];E=ROOT/'v7/evidence/belief_control';O=ROOT/'v7/experiments/output/belief_control'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(path,rows):
    out=io.StringIO();w=csv.DictWriter(out,fieldnames=sorted(set().union(*(r.keys() for r in rows))));w.writeheader()
    for row in rows:w.writerow({k:json.dumps(v) if isinstance(v,(dict,list,tuple)) else v for k,v in row.items()})
    path.write_bytes(gzip.compress(out.getvalue().encode(),mtime=0))
def main():
    E.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
    paths=[Path(__file__),ROOT/'v7/experiments/belief_control.py',ROOT/'v7/tests/test_belief_control.py']
    config={'seeds':list(range(84201,84225)),'d':[0.,.5],'assumed_switch_hazard':[0.,.01],'arms':ARMS,
            'training_episodes':40,'adult_episodes':20,'private_accuracy':.8,'source_accuracy':.7,
            'audit_accuracy':{'baseline':.8,'audience_removal':.8,'free_audit':.8,'independent_reliable_evidence':.95},
            'inheritance':'Trait d affects juvenile conflict action only; adult override zero. No acquired state at initialization.',
            'gwt':[{'given':'Common private/feedback information and one source root','when':'d varied','then':'Factual posterior trajectory invariant; action values may differ'},
                   {'given':'Same trained adult cloned','when':'audience removed or audit fee removed','then':'Relevant actual reinforcement/credit transition changes'},
                   {'given':'Stable training followed by unexpected reversal','when':'static versus switching belief model compared','then':'Persistence can depend on prior/environment model without authority-specific rigidity'}],
            'scope':'Separate cognitive assay, not demographic/invasion fitness. Posterior inertia under a static-world assumption is not irrational dogmatism.',
            'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in paths}}
    path=E/'registration.json'
    if path.exists():assert json.loads(path.read_text())['config']==config
    else:
        path.write_text(json.dumps({'status':'registered_before_confirmation','registered_at':datetime.now(timezone.utc).isoformat(),'config':config,'python':sys.version},indent=2)+'\n')
        with tarfile.open(E/'source.tar.gz','w:gz') as z:
            for p in paths:z.add(p,arcname=str(p.relative_to(ROOT)))
    training=[];adults=[]
    for seed in config['seeds']:
        for h in config['assumed_switch_hazard']:
            for d in config['d']:
                state,trace=train(seed,d,h);training.extend(trace)
                for arm in ARMS:
                    for change in (False,True):adults.extend(adult(seed,d,h,state,arm,change))
    write(O/'training.csv.gz',training);write(O/'adults.csv.gz',adults)
    ends=[r for r in adults if r['step']==19]
    summary={'status':'complete','training_rows':len(training),'adult_rows':len(adults),'adult_sequences':len(ends),
             'private_correct':sum(r['private']==r['truth'] for r in training),'private_denominator':len(training),
             'endpoints':[{ 'hazard':h,'d':d,'arm':arm,'environment_change':change,'n':24,
                           'posterior_correct':sum(r['posterior_correct'] for r in ends if r['hazard']==h and r['juvenile_d']==d and r['arm']==arm and r['environment_change']==change),
                           'action_correct':sum(r['action_correct'] for r in ends if r['hazard']==h and r['juvenile_d']==d and r['arm']==arm and r['environment_change']==change)}
                          for h in config['assumed_switch_hazard'] for d in config['d'] for arm in ARMS for change in (False,True)],
             'source_sha256':config['source_sha256'],'raw_sha256':{str(p.relative_to(ROOT)):sha(p) for p in O.iterdir() if p.is_file()},'scope':config['scope']}
    (E/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='endpoints'},indent=2))
if __name__=='__main__':main()
