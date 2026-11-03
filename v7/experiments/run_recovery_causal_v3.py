from __future__ import annotations
import argparse,csv,gzip,json,tarfile
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
from v7.experiments.recovery_causal_v3 import SEEDS,ADULT_SEEDS,REGIMES,juvenile,training,adult_updates
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments/output/recovery_causal_v3';E=ROOT/'evidence/recovery_causal_v3';C=E/'config.json'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def rows(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 with gzip.open(p,'wt',newline='') as h:w=csv.DictWriter(h,fieldnames=sorted({k for r in x for k in r}));w.writeheader();w.writerows(x)
def freeze():
 fs=[ROOT/'experiments/recovery_causal_v3.py',Path(__file__),ROOT/'experiments/model.py',ROOT/'experiments/corrected_model.py',C];arc=E/'source_freeze.tar.gz';arc.parent.mkdir(parents=True,exist_ok=True)
 with tarfile.open(arc,'w:gz') as t:
  for p in fs:
   i=t.gettarinfo(str(p),arcname=str(p.relative_to(ROOT)));i.mtime=0;i.uid=i.gid=0;i.uname=i.gname=''
   with p.open('rb') as h:t.addfile(i,h)
 x={'stage':'r3-source-freeze','frozen_at':datetime.now(timezone.utc).isoformat(),'files':{str(p.relative_to(ROOT)):sha(p) for p in fs},'archive_sha256':sha(arc)};dump(E/'source_freeze.json',x);return x
def run(pilot):
 f=freeze();seeds=[SEEDS[0]] if pilot else list(SEEDS);adults=[ADULT_SEEDS[0]] if pilot else list(ADULT_SEEDS);reg={'stage':'r3-registration','status':'registered_before_outcomes','mode':'pilot' if pilot else 'confirmation','seeds':seeds,'adult_seeds':adults,'regimes':list(REGIMES),'fixed_cap':24,'workers':2,'role_label':'randomized visible typed message used by live policy; paired label swap is a matched counterfactual','adult_training':'40 paid stochastic episodes from B=.5,K=empty,H=0,T=.5 before cloning arms','arms':['baseline','audience_removal','free_audit','reliable_evidence'],'directions':['supporting','contrary'],'steps':20,'provenance_limit':'PROV-01 remains partial: IDs/metadata alone do not establish independent testimony histories.','source_freeze_sha256':sha(E/'source_freeze.json')};dump(E/('pilot_registration.json' if pilot else 'registration.json'),reg)
 with ProcessPoolExecutor(max_workers=2) as pool: js=list(pool.map(juvenile,[(s,r) for s in seeds for r in REGIMES],chunksize=1))
 j=[r for x in js for r in x['rows']];tr=[];a=[]; states={}
 for seed in adults:
  for trait in ('d0','dhalf'):
   state,episodes=training(seed,trait);tr+=episodes;states[(seed,trait)]=state
   for arm in reg['arms']:
    for direction in (1,-1):a+=adult_updates(seed,trait,state,arm,direction)
 allrows=j+tr+a;stem='pilot' if pilot else 'confirmation';raw=OUT/f'{stem}_raw.csv.gz';rows(raw,allrows)
 jr=[r for r in j if r['assay']=='juvenile_role_label'];g={}
 for r in jr:g.setdefault((r['seed'],r['regime'],r['opportunity_id'],r['trait']),{})[r['tested_label']]=r
 pairs=[x for x in g.values() if set(x)=={'peer','authority'}];role_null=sum(x['peer']['chosen_action']!=x['authority']['chosen_action'] for x in pairs);cross={}
 for r in jr:
  if r['tested_label']==r['assigned_label']:cross[(r['seed'],r['regime'],r['opportunity_id'],r['tested_label'],r['trait'])]=r
 initial_ok=all(next(x for x in a if x['seed']==seed and x['trait']==trait and x['step']==1)['K_acquired_procedure']==states[(seed,trait)]['K'] for seed in adults for trait in ('d0','dhalf'))
 private_correct=sum(r['private_signal']==r['truth'] for r in tr)
 s={'stage':'r3','mode':stem,'status':'complete','raw':str(raw.relative_to(ROOT)),'raw_sha256':sha(raw),'juvenile_rows':len(jr),'label_pairs':len(pairs),'label_action_changes':role_null,'juvenile_conflicts':sum(r['conflict'] for r in jr if r['trait']=='d0'),'all_passive_digest_parity':all(x['parity'] for x in js),'training_rows':len(tr),'private_signal_correct':private_correct,'private_signal_accuracy_empirical':private_correct/len(tr),'adult_initial_state_replays_training_K':initial_ok,'adult_rows':len(a),'adult_sequences':len(adults)*2*4*2,'all_adult_steps_20':all(sum(1 for r in a if r['seed']==seed and r['trait']==trait and r['arm']==arm and r['evidence_direction']==direction)==20 for seed in adults for trait in ('d0','dhalf') for arm in reg['arms'] for direction in ('supporting','contrary')),'K_changes_only_training':all(r['K_acquired_procedure']==next(x['K_acquired_procedure'] for x in a if x['seed']==r['seed'] and x['trait']==r['trait'] and x['arm']==r['arm'] and x['evidence_direction']==r['evidence_direction'] and x['step']==1) for r in [x for x in a if x['step']==20]),'provenance_status':'PARTIAL','claim_limit':'Role labels are randomized typed-message inputs; ordinary policy structurally ignores them, so label-null results are distinct from d conflict override. Juvenile decisions are not demographic ITT. Adult assay is acquired-state cognitive evidence, not dogmatism/norm evidence.'};dump(OUT/f'{stem}_summary.json',s);dump(E/f'{stem}_verification.json',s);return s
def main():
 p=argparse.ArgumentParser();p.add_argument('--pilot',action='store_true');p.add_argument('--run',action='store_true');x=p.parse_args();
 if x.pilot==x.run:p.error('choose one')
 print(json.dumps(run(x.pilot),indent=2,sort_keys=True))
if __name__=='__main__':main()
