#!/usr/bin/env python3
"""Hash research artifacts and produce a self-contained, verifiable V4 archive."""
import argparse,dataclasses,hashlib,json,platform,subprocess,sys,zipfile
from datetime import datetime,timezone
from pathlib import Path
import numpy,scipy,plotly

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent
sys.path.insert(0,str(ROOT/'experiments'))
from model import Config
from run_experiments import MODELS,SCENARIOS

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def files():
    candidates=list(ROOT.rglob('*'))
    spikes=REPO/'.planning/spikes'
    for name in ('MANIFEST.md','CONVENTIONS.md'):candidates.append(spikes/name)
    for folder in spikes.glob('00[4-8]-*'):candidates.extend(folder.rglob('*'))
    return sorted(p for p in candidates if p.is_file() and '__pycache__' not in p.parts
                  and p.suffix!='.pyc' and p.name!='project_manifest.json')

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--verify',action='store_true')
    args=parser.parse_args();manifest=ROOT/'project_manifest.json'
    if args.verify:
        data=json.loads(manifest.read_text())
        mismatches=[r['path'] for r in data['files'] if not (REPO/r['path']).exists() or digest(REPO/r['path'])!=r['sha256']]
        print(json.dumps({'pass':not mismatches,'checked':len(data['files']),'mismatches':mismatches}));return int(bool(mismatches))
    cfg=dataclasses.asdict(Config())
    units={k:'dimensionless' for k in cfg}
    for key in ('juvenile_rate','adult_rate','mu_F','mu_A','error_death','adult_error_death','beta_base','beta_skill'):units[key]='1/model_time'
    units.update(dt='model_time',T='model_time',K='population_density',S0='resource',KS='resource',H='score_steps')
    schema={'source':'experiments/model.py:Config and validate; generated, not a second parameter authority',
            'defaults':cfg,'units':units,'traits':{'d':{'bounds':[0,1],'units':'probability on private/adult conflict'},'tau':{'lower_exclusive':0,'units':'model_time','main_range':[.5,12]}},
            'initial_densities':{'F':80,'A':20},'models':MODELS,'scenarios':SCENARIOS,
            'scenario_definitions':{'stable':'theta=+1','shock':'theta switches +1 to -1 at t=150','periodic':'first reversal at120, then every60','wrong_history':'stable theta; initial adult correctness .2 instead of .8','no_payoff':'stable theta; correctness effects on all vital rates disabled'},
            'independent_environment_seed_ranges':{'exploratory':[100,119],'confirmatory':[1000,1019],'dynamic':[[2000,2004],[3000,3004]],'volatility':[4000,4005]}}
    (ROOT/'parameter_schema.json').write_text(json.dumps(schema,indent=2)+'\n')
    checks={}
    for label,name in [('numerical','experiments/verification.json'),('artifacts','experiments/artifact_verification.json'),('browser','browser_verification.json')]:
        result=json.loads((ROOT/name).read_text());checks[label]={'passed':sum(x['pass'] for x in result['checks']),'total':len(result['checks'])}
        if checks[label]['passed']!=checks[label]['total']:raise RuntimeError('Failed checks: '+label)
    if digest(ROOT/'index.html')!=digest(ROOT/'research_dashboard.html'):raise RuntimeError('HTML copies differ')
    records=[{'path':str(p.relative_to(REPO)),'bytes':p.stat().st_size,'sha256':digest(p)} for p in files()]
    def command(*args):
        try:return subprocess.check_output(args,cwd=REPO,text=True,stderr=subprocess.DEVNULL).strip()
        except (OSError,subprocess.CalledProcessError):return 'unavailable (e.g. unpacked outside Git)'
    data={'schema_version':1,'label':'hypothetical simulation data','generated_utc':datetime.now(timezone.utc).isoformat(),
          'branch':command('git','branch','--show-current'),'source_parent_commit_at_packaging':command('git','rev-parse','HEAD'),
          'versions':{'python':platform.python_version(),'numpy':numpy.__version__,'scipy':scipy.__version__,'plotly':plotly.__version__,'node':command('node','--version')},
          'solver':{'primary':'vectorized RK4','dt':.1,'reference':'SciPy DOP853','rtol':1e-11,'atol':1e-13,'step_halving_dt':.05},
          'configuration_sha256':hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest(),
          'verification':checks,'files':records,
          'scope':'V4 complete source, data, dashboard, literature, verification and GSD records. Pre-v4 branches preserved separately in Git. Manifest excludes itself to avoid circular hash.'}
    manifest.write_text(json.dumps(data,indent=2)+'\n')
    archive=REPO/'v4_research_complete.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=4,allowZip64=True) as z:
        for p in files()+[manifest]:z.write(p,str(p.relative_to(REPO)))
    with zipfile.ZipFile(archive) as z:
        bad=z.testzip()
        if bad:raise RuntimeError('Archive CRC failed: '+bad)
    print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'sha256':digest(archive),'files':len(records),'verification':checks,'archive_crc':'PASS'},indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
