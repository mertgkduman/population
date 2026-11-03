"""Fresh preregistered R1b v2 execution after the capacity-constrained pilot."""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,sys,tarfile
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
from statistics import mean
ROOT=Path(__file__).resolve().parents[1]; REPO=ROOT.parent
if str(REPO) not in sys.path: sys.path.insert(0,str(REPO))
from v7.experiments.recovery_culture_v2 import ARMS,POP_CAP,run_cell
OUT=ROOT/"experiments"/"output"/"recovery_comparison"; EVIDENCE=ROOT/"evidence"/"recovery_comparison"; SEEDS=tuple(range(82101,82125))
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p:Path,x:object)->None:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
def write(p:Path,x:list[dict])->None:
    p.parent.mkdir(parents=True,exist_ok=True)
    with gzip.open(p,"wt",newline="") as h:w=csv.DictWriter(h,fieldnames=sorted({k for r in x for k in r}));w.writeheader();w.writerows(x)
def worker(j:dict)->dict:return run_cell(**j)
def register()->dict:
    files=[ROOT/"experiments"/x for x in ("recovery_culture_v2.py","run_recovery_culture_v2.py")]; archive=EVIDENCE/"r1b_v2_source_snapshot.tar.gz"
    with tarfile.open(archive,"w:gz") as b:
        for f in files:
            i=b.gettarinfo(str(f),arcname=str(f.relative_to(ROOT)));i.mtime=0;i.uid=i.gid=0;i.uname=i.gname=""
            with f.open("rb") as h:b.addfile(i,h)
    r={"status":"registered_before_outcomes","reason":"R1b pilot had active capacity-constrained births without cap events; retained as pilot only.","fresh_seeds":list(SEEDS),"arms":list(ARMS),"horizon":18,"operational_population_cap":POP_CAP,"cap_rule":"At actual would-exceed birth event, record cap_censored and stop without deleting/replacing/suppressing an existing individual.","source_sha256":{str(f.relative_to(ROOT)):sha(f) for f in files},"archive_sha256":sha(archive),"checks":["forced small-cap run records status cap_censored and cap_events=1","blank newborn acquired state","paid work/nonnegative ledger","storage-off contains no storage"],"claim_limit":"No long-run growth inference."};dump(EVIDENCE/"r1b_v2_registration.json",r);return r
def run()->dict:
    reg=register(); sentinel=run_cell(82100,"transmission_innovation",population_cap=2,start_population=2,birth_probability=1.)
    if sentinel["status"]!="cap_censored" or sentinel["cap_events"]!=1 or sentinel["population"]!=2:raise RuntimeError("forced cap sentinel failed")
    pilot=[worker({"seed":s,"arm":a}) for s in SEEDS[:2] for a in ARMS]
    jobs=[{"seed":s,"arm":a} for s in SEEDS for a in ARMS]; result=list(ProcessPoolExecutor(max_workers=4).map(worker,jobs,chunksize=1))
    loss=[worker({"seed":s,"arm":a,"no_innovation_after_loss":True}) for s in SEEDS for a in ("carrier_loss_storage_off","carrier_loss_storage_on")]
    write(OUT/"r1b_v2_pilot.csv.gz",pilot);write(OUT/"r1b_v2_confirmation.csv.gz",result);write(OUT/"r1b_v2_postloss_noinnovation.csv.gz",loss)
    summary={"rows":len(result),"postloss_rows":len(loss),"cap_censored":sum(r["status"]=="cap_censored" for r in result),"extinct":sum(r["status"]=="extinct" for r in result),"complete_horizon":sum(r["status"]=="complete_horizon" for r in result),"denominator":len(result),"by_arm":{a:{"n":sum(r["arm"]==a for r in result),"functional_people_mean":mean(r["functional_people"] for r in result if r["arm"]==a),"population_mean":mean(r["population"] for r in result if r["arm"]==a),"work_mean":mean(r["work_paid"] for r in result if r["arm"]==a)} for a in ARMS},"raw_sha256":{p.name:sha(p) for p in OUT.glob("r1b_v2*.csv.gz")},"scope":"Fresh R1b v2 finite demography; exact cap/extinction denominators retained, no long-run claim."};dump(EVIDENCE/"r1b_v2_summary.json",summary);dump(EVIDENCE/"r1b_v2_machine_checks.json",{"status":"passed","forced_cap":sentinel,"blank":all(r["blank_newborn_inheritance"] for r in result),"storage_off":all(r["storage_items_end"]==0 for r in result if r["arm"]=="carrier_loss_storage_off"),"paid":all(r["work_paid"]>=r["private_work"]+r["teaching_work"] for r in result)});return summary
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--run",action="store_true");a=p.parse_args()
    if not a.run:p.error("pass --run")
    print(json.dumps(run(),sort_keys=True))
