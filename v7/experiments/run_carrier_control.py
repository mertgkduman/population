"""Total-carrier removal, audited naive restart, and costed artifact recovery.

The restart is an explicitly external experimental intervention, never a natural
birth or a fitness measurement. Both arms inherit identical resource conditions.
"""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import csv,gzip,hashlib,io,json,tarfile
from v7.experiments.resource_control import World,Person,Settings
ROOT=Path(__file__).resolve().parents[2];E=ROOT/'v7/evidence/carrier_control';O=ROOT/'v7/experiments/output/carrier_control'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def write(p,rows):
    b=io.StringIO();w=csv.DictWriter(b,fieldnames=sorted(set().union(*(r.keys() for r in rows))));w.writeheader()
    for r in rows:w.writerow({k:json.dumps(v) if isinstance(v,(list,tuple,dict)) else v for k,v in r.items()})
    p.write_bytes(gzip.compress(b.getvalue().encode(),mtime=0))
def one(seed):
    original=World(seed,'carrier_loss_storage_on');write_events=[];original_acquire=original.acquire
    def observed(p,recipe,roots,kind):
        old=set(original.storage);energy=p.energy;work=original.total_work
        original_acquire(p,recipe,roots,kind)
        if set(original.storage)-old:
            assert original.total_work-work==1 and abs(p.energy-energy+.2)<1e-9
            write_events.append({'season':original.season,'actor':p.ident,'recipe':recipe,'roots':roots,'energy_debit':.2,'time_debit':1})
    original.acquire=observed
    for t in range(30):
        original.begin(t);original.allocate(len(original.people)*4);original.actions();original.finish()
    # Remove the observer closure before copying; it never affected decisions.
    del original.acquire
    before=original.resource+sum(p.energy for p in original.people.values())
    artifacts=deepcopy(original.storage);roots={r for rs in artifacts.values() for r in rs};rows=[];histories=[]
    for enabled in (False,True):
        world=deepcopy(original);world.arm='carrier_loss_storage_on' if enabled else 'carrier_loss_storage_off'
        removed_energy=sum(p.energy for p in world.people.values());removed_people=len(world.people)
        for ident in list(world.people):world.remove(ident,'carrier')
        world.people={f'naive{i}':Person(f'naive{i}') for i in range(10)}
        injected=80.
        stock=world.resource+sum(p.energy for p in world.people.values())
        assert abs(stock-(before-removed_energy+injected))<1e-7
        world.storage=deepcopy(artifacts) if enabled else {}
        assert all(not p.recipe and not p.roots and p.progress==0 for p in world.people.values())
        world.initial=stock;world.regenerated=world.sinks=0.;world.births=world.deaths=world.removals=0
        world.history=[];world.acquisitions=[];world.no_innovation=True;world.status='running'
        for t in range(30,50):
            world.begin(t);world.allocate(len(world.people)*4);world.actions();world.finish()
            if world.status!='running':break
        learned_roots={r for p in world.people.values() for r in p.roots}
        if enabled:assert learned_roots<=roots
        else:assert not learned_roots and not world.storage and all(not p.recipe for p in world.people.values())
        reads=sum(a['kind']=='storage_read' for a in world.acquisitions)
        result=world.result();result.update(seed=seed,storage_enabled=enabled,checkpoint=30,recovery_horizon=20,
            removed_people=removed_people,removed_energy=removed_energy,external_naive_replacements=10,external_energy_injection=injected,
            post_restart_stock=stock,post_restart_blank=True,stored_prefixes_before=len(artifacts),
            recovered_roots_trace_to_artifacts=learned_roots<=roots,storage_reads=reads,read_energy_cost=.2*reads,read_time_cost=reads,
            prior_write_energy_cost=sum(x['energy_debit'] for x in write_events),mean_population_post=sum(x['N'] for x in world.history)/20,
            scope='Externally restarted memory-retention assay, not natural demographic fitness.')
        rows.append(result);histories.extend({'seed':seed,'storage_enabled':enabled,**r} for r in world.history)
    return rows,histories,{'seed':seed,'artifacts':[{'recipe':k,'roots':v} for k,v in artifacts.items()],'paid_writes':write_events}
def main():
    E.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
    files=[Path(__file__),ROOT/'v7/experiments/resource_control.py']
    config={'seeds':list(range(82801,82825)),'checkpoint':30,'recovery_horizon':20,'restart_population':10,'external_energy':80.,
            'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in files},'settings':Settings().__dict__,
            'gwt':[{'given':'All living people removed,ten blank replacements and matched resource','when':'storage unavailable and innovation disabled','then':'no recipe/provenance survives'},
                   {'given':'Paid stored artifacts retained','when':'naive replacement learns','then':'every recovered origin is stored and reading is paid'}]}
    p=E/'registration.json'
    if p.exists():assert json.loads(p.read_text())['config']==config
    else:
        dump(p,{'status':'registered_before_confirmation','registered_at':datetime.now(timezone.utc).isoformat(),'config':config})
        with tarfile.open(E/'source.tar.gz','w:gz') as z:
            for path in files:z.add(path,arcname=str(path.relative_to(ROOT)))
    rows=[];history=[];ledger=[]
    for seed in config['seeds']:
        r,h,l=one(seed);rows.extend(r);history.extend(h);ledger.append(l)
    write(O/'endpoints.csv.gz',rows);write(O/'seasons.csv.gz',history)
    (O/'artifact_ledger.json.gz').write_bytes(gzip.compress(json.dumps(ledger).encode(),mtime=0))
    report={'status':'complete','rows':len(rows),'independent_paired_seeds':24,'all_off_no_recipe':all(r['knowledge_items']==0 and r['storage_items']==0 for r in rows if not r['storage_enabled']),
            'all_on_origins_trace':all(r['recovered_roots_trace_to_artifacts'] for r in rows),
            'storage_on_recovery_runs':sum(r['knowledge_items']>0 for r in rows if r['storage_enabled']),
            'max_stock_residual':max(r['max_residual'] for r in rows),
            'raw_sha256':{str(p.relative_to(ROOT)):sha(p) for p in O.iterdir() if p.is_file()},
            'scope':'Naive-restart intervention with explicit external energy/population input; not an invasion or natural growth experiment.'}
    dump(E/'summary.json',report);print(json.dumps(report,indent=2))
if __name__=='__main__':main()
