"""Frozen runner for R2v2 juvenile capture and cloned adult intervention arms."""
from __future__ import annotations
import argparse,csv,gzip,json,tarfile
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
from v7.experiments.recovery_causal_v2 import SEEDS,REGIMES,adult_arm,juvenile_seed
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'experiments/output/recovery_causal_v2'; EVIDENCE=ROOT/'evidence/recovery_causal_v2'; CONFIG=EVIDENCE/'config.json'
def digest(p:Path)->str:return sha256(p.read_bytes()).hexdigest()
def dump(p:Path,x:dict)->None:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def write_rows(p:Path,rows:list[dict])->None:
 p.parent.mkdir(parents=True,exist_ok=True)
 with gzip.open(p,'wt',newline='') as h:
  w=csv.DictWriter(h,fieldnames=sorted({k for r in rows for k in r}));w.writeheader();w.writerows(rows)
def freeze()->dict:
 files=[ROOT/'experiments/recovery_causal_v2.py',Path(__file__),ROOT/'experiments/corrected_model.py',ROOT/'experiments/model.py',CONFIG]; arc=EVIDENCE/'source_freeze.tar.gz';arc.parent.mkdir(parents=True,exist_ok=True)
 with tarfile.open(arc,'w:gz') as t:
  for p in files:
   info=t.gettarinfo(str(p),arcname=str(p.relative_to(ROOT)));info.mtime=0;info.uid=info.gid=0;info.uname=info.gname=''
   with p.open('rb') as h:t.addfile(info,h)
 result={'stage':'r2v2-source-freeze','frozen_at':datetime.now(timezone.utc).isoformat(),'files':{str(p.relative_to(ROOT)):digest(p) for p in files},'archive_sha256':digest(arc)};dump(EVIDENCE/'source_freeze.json',result);return result
def run(pilot:bool)->dict:
 source=freeze();seeds=[SEEDS[0]] if pilot else list(SEEDS);adult=seeds
 reg={'stage':'r2v2-registration','status':'registered_before_outcomes','registered_at':datetime.now(timezone.utc).isoformat(),'mode':'pilot' if pilot else 'confirmation','seeds':seeds,'regimes':list(REGIMES),'workers':2,'fixed_cap':24,'tau':5,'juvenile_definition':'actual age < 5 and teacher-present message during live corrected rollout','authority':'randomized matched labels; compare d=(0,0) with applicable d=(.5,0) or (0,.5), no forced conflict','passive_instrumentation':'paired unobserved replay digest must match recorded replay digest','adult_arms':['baseline','audience_removal','free_audit','evidence'],'adult_directions':['supporting','contrary'],'adult_steps':20,'source_freeze_sha256':digest(EVIDENCE/'source_freeze.json')};dump(EVIDENCE/('pilot_registration.json' if pilot else 'registration.json'),reg)
 with ProcessPoolExecutor(max_workers=2) as pool: outcomes=list(pool.map(juvenile_seed,[(s,r) for s in seeds for r in REGIMES],chunksize=1))
 juveniles=[r for o in outcomes for r in o['rows']];adults=[r for s in adult for arm in reg['adult_arms'] for d in (1,-1) for r in adult_arm(s,arm,d)];rows=juveniles+adults;stem='pilot' if pilot else 'confirmation';raw=OUT/f'{stem}_raw.csv.gz';write_rows(raw,rows)
 juv=[r for r in juveniles if r['assay']=='juvenile_authority_itt'];groups={}
 for r in juv:groups.setdefault((r['seed'],r['regime'],r['opportunity_id']),{})[r['randomized_label']]=r
 pairs=[x for x in groups.values() if set(x)=={'neutral','authority'}];adult_groups={(r['seed'],r['arm'],r['evidence_direction']):[] for r in adults}
 for r in adults:adult_groups[(r['seed'],r['arm'],r['evidence_direction'])].append(r['step'])
 summary={'stage':'r2v2','mode':stem,'status':'complete','raw':str(raw.relative_to(ROOT)),'raw_sha256':digest(raw),'juvenile_rows':len(juv),'juvenile_pairs':len(pairs),'juvenile_conflicts':sum(x['authority']['conflict'] for x in pairs),'juvenile_action_changes':sum(x['neutral']['chosen_action']!=x['authority']['chosen_action'] for x in pairs),'all_passive_digest_parity':all(r.get('passive_digest_parity',False) for r in juveniles),'adult_rows':len(adults),'adult_cloned_sequences':len(adult_groups),'all_adult_sequences_20':all(sorted(v)==list(range(1,21)) for v in adult_groups.values()),'all_adult_override_zero':all(float(r['direct_adult_inherited_override'])==0 for r in adults),'claim_limit':'Juvenile rows are decision counterfactuals replayed from live corrected rollouts, not altered demographic trajectories. Adult arms are a separate cognitive assay; dogmatism/normative commitment remain unsupported.'};dump(OUT/f'{stem}_summary.json',summary);dump(EVIDENCE/f'{stem}_verification.json',summary);return summary
def main()->None:
 p=argparse.ArgumentParser();p.add_argument('--pilot',action='store_true');p.add_argument('--run',action='store_true');a=p.parse_args();
 if a.pilot==a.run:p.error('choose one');
 print(json.dumps(run(a.pilot),indent=2,sort_keys=True))
if __name__=='__main__':main()
