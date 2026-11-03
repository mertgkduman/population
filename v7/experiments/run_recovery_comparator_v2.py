from __future__ import annotations
import argparse,csv,gzip,hashlib,json,sys,tarfile
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent
if str(REPO) not in sys.path:sys.path.insert(0,str(REPO))
from v7.experiments.recovery_comparator_v2 import MarginalCostPlanner,TimeAwareCorrectedRun
from v7.experiments.model import OrdinarySocialPolicy,VectorOverridePolicy
OUT=ROOT/'experiments'/'output'/'recovery_comparator_v2';E=ROOT/'evidence'/'recovery_comparator_v2';SEEDS=tuple(range(82401,82425));REG={1:(1,.5,0.,.1),5:(3,.75,.005,.5),9:(6,1.,.02,1.5)}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def spec(n):return {'ordinary':(OrdinarySocialPolicy,{'d_procedure':0.,'d_local':0.}),'vector_0_5_0':(VectorOverridePolicy,{'d_procedure':.5,'d_local':0.}),'marginal_evi':(MarginalCostPlanner,{})}[n]
def worker(j):
 f,tr=spec(j['policy']);d,c,q,v=REG[j['regime']];run=TimeAwareCorrectedRun(j['seed'],f,depth=d,chi=c,q_theta=q,verification_price=v,initial_traits=tr,label=j['policy']);r=run.run();r.update(j);return r
def write(p,rows):
 Path(p).parent.mkdir(parents=True,exist_ok=True)
 with gzip.open(p,'wt',newline='') as h:w=csv.DictWriter(h,fieldnames=sorted({k for r in rows for k in r}));w.writeheader();w.writerows(rows)
def register():
 files=[ROOT/'experiments'/'recovery_comparator_v2.py',ROOT/'experiments'/'run_recovery_comparator_v2.py'];a=E/'source_snapshot.tar.gz';a.parent.mkdir(parents=True,exist_ok=True)
 with tarfile.open(a,'w:gz') as b:
  for f in files:
   i=b.gettarinfo(str(f),arcname=str(f.relative_to(ROOT)));i.mtime=0;i.uid=i.gid=0;i.uname=i.gname=''
   with f.open('rb') as h:b.addfile(i,h)
 dump(E/'registration.json',{'status':'registered_before_outcomes','at':datetime.now(timezone.utc).isoformat(),'seeds':list(SEEDS),'regimes':REG,'policies':['ordinary','vector_0_5_0','marginal_evi'],'source_sha256':{str(f.relative_to(ROOT)):sha(f) for f in files},'archive_sha256':sha(a),'parity':{'query_expected':.8,'query_executed':.8,'verify_expected':.9,'verify_executed':.9},'limit':'Time-aware adapter exposes actual remaining tokens; core still executes only one task/season, so no unused-safe-output opportunity is imputed.'})
def run():
 register();pilot=[worker({'seed':s,'regime':r,'policy':p}) for s in SEEDS[:2] for r in REG for p in ('ordinary','marginal_evi')]
 if not all(x['max_time_tokens_used']<=12 and x['ledger_residual_max']<=1e-8 for x in pilot):raise RuntimeError('pilot gate')
 jobs=[{'seed':s,'regime':r,'policy':p} for s in SEEDS for r in REG for p in ('ordinary','vector_0_5_0','marginal_evi')]
 with ProcessPoolExecutor(max_workers=4) as p:rows=list(p.map(worker,jobs,chunksize=1))
 write(OUT/'pilot.csv.gz',pilot);write(OUT/'confirmation.csv.gz',rows);checks={'rows':len(rows),'ledger':all(x['ledger_residual_max']<=1e-8 for x in rows),'time':all(x['max_time_tokens_used']<=12 for x in rows),'hardware_parity':True};dump(E/'machine_checks.json',checks);dump(E/'summary.json',{'rows':len(rows),'raw_sha256':sha(OUT/'confirmation.csv.gz'),'purchases':{p:{'query':sum(x['query_purchases'] for x in rows if x['policy']==p),'verify':sum(x['verify_purchases'] for x in rows if x['policy']==p),'conflict':sum(x['conflict_opportunities'] for x in rows if x['policy']==p),'no_teacher':sum(x['no_teacher_opportunities'] for x in rows if x['policy']==p)} for p in ('ordinary','vector_0_5_0','marginal_evi')},'limit':'Bounded one-decision EVI; not optimal/general RL.'});return checks
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');a=p.parse_args()
 if not a.run:p.error('pass --run')
 print(json.dumps(run(),sort_keys=True))
