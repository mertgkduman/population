"""Register then execute the final closed-resource and matched-work controls."""
from dataclasses import asdict
from datetime import datetime,timezone
import csv,gzip,hashlib,io,json,sys,tarfile
from pathlib import Path
from v7.experiments.resource_control import Settings,run,pair

REPO=Path(__file__).resolve().parents[2]
EVIDENCE=REPO/'v7/evidence/resource_control'
OUTPUT=REPO/'v7/experiments/output/resource_control'
ARMS=('transmission_innovation','no_transmission','prerequisite_scramble','carrier_loss_storage_off','carrier_loss_storage_on')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path,data):path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
def csv_write(path,rows):
    cols=sorted(set().union(*(r.keys() for r in rows)));out=io.StringIO();w=csv.DictWriter(out,fieldnames=cols);w.writeheader();w.writerows(rows)
    path.write_bytes(gzip.compress(out.getvalue().encode(),mtime=0))
def main():
    EVIDENCE.mkdir(parents=True,exist_ok=True);OUTPUT.mkdir(parents=True,exist_ok=True)
    files=[REPO/'v7/experiments/resource_control.py',Path(__file__),REPO/'v7/tests/test_resource_control.py']
    config={'settings':asdict(Settings()),'core_seeds':list(range(82601,82625)),'pair_seeds':list(range(82501,82525)),
            'arms':ARMS,'no_innovation_after_loss':True,'precision':'Fixed24 independent seed blocks; means/paired MCSE only, no pooled event-binomial CI.',
            'knowledge_bound':'Six discoveries cost at least48 tokens; lifetime ceiling72, harvest-reserved ceiling54, so beyond-individual accumulation is NOT guaranteed.',
            'hypotheses':[{'given':'Closed finite-resource world','when':'birth,death,learning,harvest and removal occur','then':'stock and N identities close and work/person<=4'},
                          {'given':'Two independent populations','when':'same feasible effort budget offered each season','then':'realized work is equal or failure/censoring is explicit'},
                          {'given':'All acquired carriers removed,storage off','when':'innovation disabled after removal','then':'no learned recipe persists or reappears'}],
            'source_sha256':{str(p.relative_to(REPO)):sha(p) for p in files}}
    registration=EVIDENCE/'registration.json'
    if registration.exists():
        assert json.loads(registration.read_text())['config']==config,'Frozen resource-control registration differs'
    else:
        dump(registration,{'registered_at':datetime.now(timezone.utc).isoformat(),'status':'registered_before_confirmation','config':config,'python':sys.version})
        with tarfile.open(EVIDENCE/'source.tar.gz','w:gz') as z:
            for p in files:z.add(p,arcname=str(p.relative_to(REPO)))
    rows=[];histories=[];acquisitions=[]
    for seed in config['core_seeds']:
        for arm in ARMS:
            world=run(seed,arm);rows.append({'phase':'core',**world.result()})
            histories.extend({'seed':seed,'arm':arm,**h} for h in world.history)
            if seed==82601:acquisitions.extend({'seed':seed,'arm':arm,**r} for r in world.acquisitions)
        for arm in ARMS[-2:]:
            world=run(seed,arm,no_innovation=True);rows.append({'phase':'no_innovation_after_loss',**world.result()})
    pair_rows=[]
    for seed in config['pair_seeds']:
        a,b=pair(seed)
        for world in (a,b):
            pair_rows.append({'phase':'paired_effort',**world.result()})
            histories.extend({'seed':seed,'arm':'paired_'+world.arm,**h} for h in world.history)
    csv_write(OUTPUT/'endpoints.csv.gz',rows);csv_write(OUTPUT/'pairs.csv.gz',pair_rows);csv_write(OUTPUT/'seasons.csv.gz',histories)
    (OUTPUT/'representative_acquisitions.json.gz').write_bytes(gzip.compress(json.dumps(acquisitions).encode(),mtime=0))
    summary={'status':'complete','interpretation':'Ordinary skill-transmission control, not authority-deference selection or proof of cumulative culture beyond individuals.',
             'endpoint_rows':len(rows),'pair_rows':len(pair_rows),'pair_count':len(pair_rows)//2,
             'max_stock_residual':max(r['max_residual'] for r in rows+pair_rows),
             'max_person_work':max(r['max_person_work'] for r in rows+pair_rows),
             'status_counts':{s:sum(r['status']==s for r in rows+pair_rows) for s in sorted({r['status'] for r in rows+pair_rows})},
             'core_arm_means':{arm:{'n':24,'mean_N':sum(r['mean_population'] for r in rows if r['phase']=='core' and r['arm']==arm)/24,
                                   'functional_end':sum(r['functional'] for r in rows if r['phase']=='core' and r['arm']==arm)/24} for arm in ARMS},
             'source_sha256':config['source_sha256'],'raw_sha256':{str(p.relative_to(REPO)):sha(p) for p in OUTPUT.iterdir() if p.is_file()}}
    dump(EVIDENCE/'summary.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
