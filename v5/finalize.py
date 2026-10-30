#!/usr/bin/env python3
"""Hash the complete V5 research project and produce its verified archive."""
import argparse,dataclasses,hashlib,json,platform,subprocess,sys,zipfile
from datetime import datetime,timezone
from pathlib import Path
import numpy,scipy,numba,plotly
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent
sys.path.insert(0,str(ROOT/'experiments'))
from model import Config
from run_experiments import MODELS,SCENARIOS,config,segments

def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def files():
 a=list(ROOT.rglob('*'));sp=REPO/'.planning/spikes'
 a.extend(sp/name for name in ('MANIFEST.md','CONVENTIONS.md'))
 for pattern in ('009-*','010-*','011-*'):
  for folder in sp.glob(pattern):a.extend(folder.rglob('*'))
 return sorted(p for p in a if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.nbc','.nbi') and p.name!='project_manifest.json')
def command(*args):
 try:return subprocess.check_output(args,cwd=REPO,text=True,stderr=subprocess.DEVNULL).strip()
 except (OSError,subprocess.CalledProcessError):return 'unavailable (e.g. unpacked archive outside Git)'
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--verify',action='store_true');args=parser.parse_args();manifest=ROOT/'project_manifest.json'
 if args.verify:
  data=json.loads(manifest.read_text());bad=[r['path'] for r in data['files'] if not (REPO/r['path']).exists() or digest(REPO/r['path'])!=r['sha256']]
  print(json.dumps({'pass':not bad,'checked':len(data['files']),'mismatches':bad}));return int(bool(bad))
 cfg=dataclasses.asdict(Config());units={k:'dimensionless' for k in cfg}
 for k in ('nu_private','nu_social','nu_adult','mu_F','mu_A','error_F','error_A','beta_base','beta_skill'):units[k]='1/model_time'
 units.update(H='score_steps',audit_threshold='score_steps',T='model_time',dt='model_time',K='continuous_population_density',S0='resource',KS='resource',query_cost='mortality_hazard_per_private_query')
 schema={'authority':'experiments/model.py Config and validate; generated metadata','defaults':cfg,'units':units,'traits':{'d':{'range':[0,1],'units':'probability of override conditional on disagreement'},'tau':{'range':[.5,12],'units':'mean_maturation_hazard_timescale','expanded_selection_range':[.2,12]}},'models':MODELS,'scenarios':SCENARIOS,'scenario_segments':{s:segments(config('retained',s),s) for s in SCENARIOS},'initial_stage_densities':{'F':80,'A':20},'separate_benchmarks':['repertoire.py','repertoire_tutors.py','bayes_benchmark.py'],'private_cognition':'Fixed cue processing and memory capacity within each scenario; private-only learners retain acquired evidence.'}
 (ROOT/'parameter_schema.json').write_text(json.dumps(schema,indent=2)+'\n')
 checks={}
 for label,path in [('numerical','experiments/verification.json'),('artifacts','experiments/artifact_verification.json'),('followups','experiments/followup_verification.json'),('bayes','experiments/bayes_benchmark.json'),('repertoire','experiments/repertoire.json'),('tutors','experiments/repertoire_tutors.json'),('browser','browser_verification.json')]:
  obj=json.loads((ROOT/path).read_text());items=obj.get('checks') or list(obj['invariants'].values());passed=sum(bool(x.get('pass',x.get('passed',False))) for x in items)
  checks[label]={'passed':passed,'total':len(items)}
  if passed!=len(items):raise RuntimeError('Verification failed: '+label)
 if digest(ROOT/'index.html')!=digest(ROOT/'research_dashboard.html'):raise RuntimeError('HTML mirrors differ')
 records=[{'path':str(p.relative_to(REPO)),'bytes':p.stat().st_size,'sha256':digest(p)} for p in files()]
 data={'schema_version':1,'label':'hypothetical simulation data','generated_utc':datetime.now(timezone.utc).isoformat(),'branch':command('git','branch','--show-current'),'source_parent_commit_at_packaging':command('git','rev-parse','HEAD'),'versions':{'python':platform.python_version(),'numpy':numpy.__version__,'scipy':scipy.__version__,'numba':numba.__version__,'plotly':plotly.__version__,'node':command('node','--version')},'solver':{'primary':'Numba-accelerated explicit flux RK4','dt':.1,'half_dt':.05,'reference':'SciPy DOP853','rtol':1e-11,'atol':1e-13},'config_sha256':hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest(),'verification':checks,'files':records,'scope':'All V5 source/data/HTML/reports and GSD009–011 evidence. Manifest excludes itself to avoid circular hashing. Prior versions remain in Git.'}
 manifest.write_text(json.dumps(data,indent=2)+'\n');archive=REPO/'v5_research_complete.zip'
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=4,allowZip64=True) as z:
  for p in files()+[manifest]:z.write(p,str(p.relative_to(REPO)))
 with zipfile.ZipFile(archive) as z:
  bad=z.testzip()
  if bad:raise RuntimeError('Archive CRC failure: '+bad)
 print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'sha256':digest(archive),'files':len(records),'verification':checks,'archive_crc':'PASS'},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
