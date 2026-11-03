"""Frozen fresh-seed confirmation of an execution-priced bounded planner."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
import csv,gzip,hashlib,io,json,sys,tarfile
from v7.experiments.execution_planner import CountedExecutionWorld,ExecutionPlanner
from v7.experiments.model import OrdinarySocialPolicy,VectorOverridePolicy
from v7.experiments.run_experiments import _regime
REPO=Path(__file__).resolve().parents[2];E=REPO/'v7/evidence/execution_planner';OUT=REPO/'v7/experiments/output/execution_planner'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def worker(job):
    seed,regime,policy=job;r=_regime(regime-1)
    cls,traits={'ordinary':(OrdinarySocialPolicy,{}),'vector_0_5_0':(VectorOverridePolicy,{'d_procedure':.5,'d_local':0.}),
                'execution_evi':(ExecutionPlanner,{})}[policy]
    world=CountedExecutionWorld(seed,cls,depth=int(r['depth']),chi=float(r['chi']),q_theta=float(r['q_theta']),verification_price=float(r['verification_price']),graph_variant=1,initial_traits=traits,label=policy)
    result=world.run();result.update(seed=seed,regime=regime,policy=policy)
    result['completion_label']='complete_horizon' if result['seasons_completed']==240 and result['status']=='running' else result['status']
    return result

def main():
    E.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    files=[Path(__file__),REPO/'v7/experiments/execution_planner.py',REPO/'v7/tests/test_execution_planner.py',
           REPO/'v7/experiments/model.py',REPO/'v7/experiments/corrected_model.py',REPO/'v7/experiments/exact.py',REPO/'v7/experiments/config.json']
    config={'seeds':list(range(82701,82725)),'sentinels':[1,5,9],'policies':['ordinary','vector_0_5_0','execution_evi'],
            'horizon':240,'deliberation_units':12,'query_accuracy':.8,'verify_accuracy':.9,
            'claim_scope':'Bounded one-decision planner under shared Q0 and explicitly priced12 abstract units; not globally optimal/resource-rational RL.',
            'precision':'Fixed24 independent paired seed blocks; per-seed contrasts and MCSE, no pooled event binomial intervals.',
            'gwt':[{'given':'Shared one-task-per-season engine','when':'information purchased','then':'one token and incremental executed costs apply; physical execution remains feasible'},
                   {'given':'Common deliberation already executed','when':'options ranked','then':'its sunk cost cannot penalize only purchase'},
                   {'given':'Actor dies after decisions','when':'counts reported','then':'world-level counts retain its requests'}],
            'source_sha256':{str(p.relative_to(REPO)):sha(p) for p in files}}
    path=E/'registration.json'
    if path.exists():assert json.loads(path.read_text())['config']==config,'Frozen planner registration differs'
    else:
        path.write_text(json.dumps({'registered_at':datetime.now(timezone.utc).isoformat(),'status':'registered_before_confirmation','config':config,'python':sys.version},indent=2)+'\n')
        with tarfile.open(E/'source.tar.gz','w:gz') as z:
            for p in files:z.add(p,arcname=str(p.relative_to(REPO)))
    jobs=[(s,r,p) for s in config['seeds'] for r in config['sentinels'] for p in config['policies']]
    with ProcessPoolExecutor(max_workers=4) as pool:rows=list(pool.map(worker,jobs,chunksize=1))
    assert all(r['ledger_residual_max']<1e-8 and r['max_time_tokens_used']<=12 for r in rows)
    columns=sorted(set().union(*(r.keys() for r in rows)));buf=io.StringIO();w=csv.DictWriter(buf,fieldnames=columns);w.writeheader()
    for row in rows:w.writerow({k:json.dumps(v,sort_keys=True) if isinstance(v,(dict,list)) else v for k,v in row.items()})
    raw=OUT/'confirmation.csv.gz';raw.write_bytes(gzip.compress(buf.getvalue().encode(),mtime=0))
    summary={'status':'complete','rows':len(rows),'raw_sha256':sha(raw),'source_sha256':config['source_sha256'],
             'completion_counts':{s:sum(r['completion_label']==s for r in rows) for s in sorted({r['completion_label'] for r in rows})},
             'max_ledger_residual':max(r['ledger_residual_max'] for r in rows),
             'max_time_tokens_used':max(r['max_time_tokens_used'] for r in rows),
             'counts':{p:{k:sum(r.get('count_'+k,0) for r in rows if r['policy']==p) for k in ['all_initial_decisions','no_teacher','teacher_present','initial_conflicts','query_purchases','verify_purchases']} for p in config['policies']},
             'mean_population':{str(r):{p:sum(x['mean_population'] for x in rows if x['regime']==r and x['policy']==p)/24 for p in config['policies']} for r in config['sentinels']},'claim_scope':config['claim_scope']}
    (E/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
