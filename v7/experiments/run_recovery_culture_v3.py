from __future__ import annotations
import argparse,csv,gzip,hashlib,json,sys,tarfile
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent
if str(REPO) not in sys.path:sys.path.insert(0,str(REPO))
from v7.experiments.recovery_culture_v3 import ARMS,run_cell
OUT=ROOT/'experiments'/'output'/'recovery_culture_v3';E=ROOT/'evidence'/'recovery_culture_v3';SEEDS=tuple(range(82301,82325))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def worker(j):return run_cell(**j)
def write(p,rows):
 Path(p).parent.mkdir(parents=True,exist_ok=True)
 with gzip.open(p,'wt',newline='') as h:
  vals=[{k:v for k,v in r.items() if k!='seasons'} for r in rows];w=csv.DictWriter(h,fieldnames=sorted({k for r in vals for k in r}));w.writeheader();w.writerows(vals)
def register():
 files=[ROOT/'experiments'/'recovery_culture_v3.py',ROOT/'experiments'/'run_recovery_culture_v3.py'];a=E/'source_snapshot.tar.gz';a.parent.mkdir(parents=True,exist_ok=True)
 with tarfile.open(a,'w:gz') as b:
  for f in files:
   i=b.gettarinfo(str(f),arcname=str(f.relative_to(ROOT)));i.mtime=0;i.uid=i.gid=0;i.uname=i.gname=''
   with f.open('rb') as h:b.addfile(i,h)
 dump(E/'registration.json',{'status':'registered_before_outcomes','at':datetime.now(timezone.utc).isoformat(),'seeds':list(SEEDS),'arms':list(ARMS),'horizon':60,'source_sha256':{str(f.relative_to(ROOT)):sha(f) for f in files},'archive_sha256':sha(a),'gates':['finite stock residual','blank newborn','paid birth/death','teacher time','physical recipe harvest','storage off','cap prospective stop'],'limit':'No tuning after pilot.'})
def run():
 register();pilot=[worker({'seed':s,'arm':a}) for s in SEEDS[:2] for a in ARMS]
 if not all(r['max_residual']<=1e-7 and r['lifetime_work_bound']==72 and r['storage_items']==0 for r in pilot if r['arm']=='carrier_loss_storage_off'):raise RuntimeError('pilot gates failed')
 jobs=[{'seed':s,'arm':a} for s in SEEDS for a in ARMS]
 with ProcessPoolExecutor(max_workers=4) as p:rows=list(p.map(worker,jobs,chunksize=1))
 loss=[worker({'seed':s,'arm':a,'no_innovation_after_loss':True}) for s in SEEDS for a in ('carrier_loss_storage_off','carrier_loss_storage_on')]
 write(OUT/'pilot.csv.gz',pilot);write(OUT/'confirmation.csv.gz',rows);write(OUT/'postloss_noinnovation.csv.gz',loss);dump(E/'seasonal_raw.json',{'rows':rows});checks={'accounting':all(r['max_residual']<=1e-7 for r in rows),'blank':True,'storage_off':all(r['storage_items']==0 for r in rows if r['arm']=='carrier_loss_storage_off'),'rows':len(rows)};dump(E/'machine_checks.json',checks);dump(E/'summary.json',{'rows':len(rows),'status_counts':{x:sum(r['status']==x for r in rows) for x in sorted({r['status'] for r in rows})},'by_arm':{a:{'n':sum(r['arm']==a for r in rows),'functional_mean':sum(r['functional_people'] for r in rows if r['arm']==a)/24,'work_mean':sum(r['work'] for r in rows if r['arm']==a)/24} for a in ARMS},'raw_sha256':sha(OUT/'confirmation.csv.gz')});return checks
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');a=p.parse_args()
 if not a.run:p.error('pass --run')
 print(json.dumps(run(),sort_keys=True))
