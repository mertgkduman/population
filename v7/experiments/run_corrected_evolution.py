"""Fresh, four-worker corrected-overlay finite lineage runner."""
from __future__ import annotations
import argparse, csv, gzip, hashlib, json, sys, tarfile
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from v7.experiments.corrected_evolution import DEFAULT_REGIMES, DIRECTED_PAIRS, EXTENSION_SEEDS, LINEAGE_SEASONS, SELECTION_SEEDS, ArmResult, gate_assays, paired_lineage, summarize

OUT=ROOT/"v7/experiments/output/corrected"; EVIDENCE=ROOT/"v7/evidence/corrected"; CHECKPOINT=OUT/"corrected_evolution_checkpoint.jsonl"
FROZEN=("experiments/model.py","experiments/exact.py","experiments/run_experiments.py","experiments/analyze_results.py","experiments/verify.py","experiments/config.json","parameter_schema.json")
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def write_json(p:Path,v:dict)->None:
    p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+".tmp"); t.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");t.replace(p)
def frozen()->dict[str,str]:return {x:sha(ROOT/"v7"/x) for x in FROZEN}
def overlay()->dict[str,str]:return {x:sha(ROOT/"v7/experiments"/x) for x in ("corrected_model.py","corrected_evolution.py",Path(__file__).name)}
def source_snapshot()->dict:
    directory=EVIDENCE/"corrected_evolution_source_snapshot";directory.mkdir(parents=True,exist_ok=True)
    files=[ROOT/"v7/experiments/corrected_model.py",ROOT/"v7/experiments/corrected_evolution.py",Path(__file__),ROOT/"v7/experiments/evolution.py",ROOT/"v7/experiments/config.json"]
    archive=directory/"source.tar.gz"
    with tarfile.open(archive,"w:gz") as bundle:
        for path in files:
            info=bundle.gettarinfo(str(path),arcname=str(path.relative_to(ROOT/"v7")));info.mtime=0;info.uid=info.gid=0;info.uname=info.gname=""
            with path.open("rb") as handle:bundle.addfile(info,handle)
    manifest={"stage":"corrected_evolution_source_snapshot","files":{str(x.relative_to(ROOT/"v7")):sha(x) for x in files},"archive":"v7/evidence/corrected/corrected_evolution_source_snapshot/source.tar.gz","archive_sha256":sha(archive),"frozen_core_sha256":frozen()}
    write_json(directory/"manifest.json",manifest)
    return {"archive_sha256":sha(archive),"manifest_sha256":sha(directory/"manifest.json")}
def jobs():return [(seed,regime,pair) for seed in (*SELECTION_SEEDS,*EXTENSION_SEEDS) for regime in DEFAULT_REGIMES for pair in DIRECTED_PAIRS]
def registration()->dict:
    freeze=EVIDENCE/"freeze_variant"/"manifest.json"
    if not freeze.exists(): raise RuntimeError("corrected ecology freeze manifest is required before corrected evolution registration")
    snapshot=source_snapshot();values=jobs(); return {"stage":"corrected_finite_lineage","status":"registered_before_outcomes","registered_at":datetime.now(timezone.utc).isoformat(),"workers":4,"seeds":{"initial":[79001,79024],"extension_batches":[[x,x+7] for x in range(79025,79097,8)],"maximum":79096},"regimes":DEFAULT_REGIMES,"directed_pairs":DIRECTED_PAIRS,"horizon":LINEAGE_SEASONS,"jobs":len(values),"registered_trajectories":len(values)*2,"core_freeze_source_sha256":frozen(),"overlay_source_sha256":overlay(),"corrected_ecology_freeze_manifest_sha256":sha(freeze),"immutable_source_snapshot":snapshot,"claim_limit":"Finite paid-newborn lineage only; no asymptotic invasion, fixation, or ESS claim."}
def run_job(job):return paired_lineage(*job)
def load()->list[ArmResult]:return [ArmResult(**json.loads(x)) for x in CHECKPOINT.read_text().splitlines()] if CHECKPOINT.exists() else []
def write_rows(p:Path,rows:list[ArmResult]):
    data=[]
    for row in rows:
        v=row.record()
        for k in ("mutant_traits","resident_traits","teacher_pool","frequency_trajectory"):v[k]=json.dumps(v[k],sort_keys=True)
        data.append(v)
    with gzip.open(p,"wt",newline="") as h:
        w=csv.DictWriter(h,fieldnames=list(data[0]) if data else ["seed"]);w.writeheader();w.writerows(data)
def targets(summary):
    contrasts=summary["paired_contrasts"]
    # Missing / all-no-birth contrasts must remain UNRESOLVED, never silently
    # disappear and permit a subset of the pre-registered 3x4 design to pass.
    return len(contrasts)==12 and len(summary["arms"])==24 and all(x["paired_descendant_difference_mcse"]<=.25 and x["max_establishment_wilson_half_width"]<=.10 for x in contrasts.values())
def run(max_seed:int=96)->dict:
    OUT.mkdir(parents=True,exist_ok=True); reg=registration();write_json(EVIDENCE/"corrected_evolution_registration.json",reg)
    gates=gate_assays();write_json(OUT/"corrected_evolution_gates.json",gates)
    if gates["status"]!="passed":return {"status":"blocked","gates":gates}
    records=load(); schedule=[list(SELECTION_SEEDS),*[list(range(x,x+8)) for x in range(79025,79097,8)]]
    for batch in schedule:
        if batch[0]>79000+max_seed:break
        existing={(r.seed,r.regime,r.directed_pair) for r in records if r.arm=="mutant"}; planned=[(s,r,p) for s in batch for r in DEFAULT_REGIMES for p in DIRECTED_PAIRS if (s,r,f"{p[0]}->{p[1]}") not in existing]
        with CHECKPOINT.open("a") as h, ProcessPoolExecutor(max_workers=4) as pool:
            for left,right in pool.map(run_job,planned,chunksize=1):
                for row in (left,right):h.write(json.dumps(row.record(),sort_keys=True,separators=(",",":"))+"\n")
                h.flush();records.extend((left,right))
        summary=summarize(records)
        if targets(summary):break
    p=OUT/"corrected_evolution.csv.gz";write_rows(p,records);summary=summarize(records);status="complete" if targets(summary) else "UNRESOLVED"
    result={"stage":"corrected_finite_lineage","status":status,"records":len(records),"summary":summary,"gates":{"status":gates["status"],"checks":gates["checks"]},"raw":"v7/experiments/output/corrected/corrected_evolution.csv.gz","raw_sha256":sha(p),"registration_sha256":sha(EVIDENCE/"corrected_evolution_registration.json"),"core_freeze_source_sha256":frozen(),"overlay_source_sha256":overlay(),"corrected_ecology_freeze_manifest_sha256":reg["corrected_ecology_freeze_manifest_sha256"],"claim_limit":reg["claim_limit"],"unresolved":[] if status=="complete" else ["Declared paired descendant MCSE and/or establishment Wilson precision not met by seed 79096; no further extension run."]}
    write_json(OUT/"corrected_evolution_summary.json",result);write_json(EVIDENCE/"corrected_evolution_result.json",result);return result
def main():
    p=argparse.ArgumentParser();p.add_argument("--max-seed",type=int,default=96);a=p.parse_args();print(json.dumps({k:v for k,v in run(a.max_seed).items() if k in {"status","records","raw_sha256"}},sort_keys=True))
if __name__=="__main__":main()
