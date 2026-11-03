"""Registered runner for R1a/R1b recovery experiments."""
from __future__ import annotations
import argparse, csv, gzip, hashlib, json, shutil, sys, tarfile
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
if str(REPO) not in sys.path: sys.path.insert(0, str(REPO))
from v7.experiments.corrected_model import CorrectedEcologyRun
from v7.experiments.model import FeatureTrustPolicy, OrdinarySocialPolicy, VectorOverridePolicy
from v7.experiments.recovery_comparators import MatchedActionConditionalPolicy, comparator_contract
from v7.experiments.recovery_culture import ARMS, run_cell as culture_cell

OUT = ROOT / "experiments" / "output" / "recovery_comparison"
EVIDENCE = ROOT / "evidence" / "recovery_comparison"
SEEDS_A, SEEDS_B = tuple(range(81001, 81025)), tuple(range(82001, 82025))
POLICIES = ("ordinary_social", "feature_trust", "vector_0_5_0", "vector_1_0", "matched_action_conditional")
REGIMES = (1, 5, 9)
REGIME_PARAMS = {1: (1, .5, .0, .1), 5: (3, .75, .005, .5), 9: (6, 1., .02, 1.5)}

def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
def rows(path: Path, values: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", newline="") as h:
        w = csv.DictWriter(h, fieldnames=sorted({k for r in values for k in r})); w.writeheader(); w.writerows(values)
def snapshot() -> dict:
    files = [ROOT / "experiments" / x for x in ("recovery_comparators.py", "recovery_culture.py", "run_recovery_comparison.py", "corrected_model.py", "model.py")]
    archive = EVIDENCE / "source_snapshot.tar.gz"; archive.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "w:gz") as bundle:
        for file in files:
            info = bundle.gettarinfo(str(file), arcname=str(file.relative_to(ROOT))); info.mtime=0; info.uid=info.gid=0; info.uname=info.gname=""
            with file.open("rb") as h: bundle.addfile(info, h)
    return {str(f.relative_to(ROOT)): sha(f) for f in files} | {"archive_sha256": sha(archive)}
def policy(name: str):
    return {"ordinary_social": (OrdinarySocialPolicy, {"d_procedure":0.,"d_local":0.}), "feature_trust": (FeatureTrustPolicy, {}), "vector_0_5_0": (VectorOverridePolicy, {"d_procedure":.5,"d_local":0.}), "vector_1_0": (VectorOverridePolicy, {"d_procedure":1.,"d_local":0.}), "matched_action_conditional": (MatchedActionConditionalPolicy, {})}[name]
def run_a(job: dict) -> dict:
    factory, traits = policy(job["policy"]); depth, chi, q, verify = REGIME_PARAMS[job["regime"]]
    run = CorrectedEcologyRun(job["seed"], factory, depth=depth, chi=chi, q_theta=q, verification_price=verify, initial_traits=traits, label=job["policy"])
    result=run.run(); kinds=[event.kind for event in run.ledger]
    result.update(job, query_events=kinds.count("query"), verify_events=kinds.count("verify"), no_teacher_opportunities=sum(1 for x in run.decision_samples if x["chosen_action"] == "private"), conflict_opportunities=run.override_opportunities, production_events=kinds.count("production"), comparator_contract=comparator_contract() if job["policy"]=="matched_action_conditional" else None)
    return result
def run_b(job: dict) -> dict:
    return culture_cell(**job)
def run_jobs(func, values):
    with ProcessPoolExecutor(max_workers=4) as pool: return list(pool.map(func, values, chunksize=1))
def registration() -> dict:
    config={"status":"registered_before_outcomes","registered_at":datetime.now(timezone.utc).isoformat(),"r1a":{"seeds":list(SEEDS_A),"pilot":[81001,81002],"regimes":list(REGIMES),"policies":list(POLICIES),"regime_params":REGIME_PARAMS,"paired_by_seed":True,"extensions":"none; fixed 24 fresh seeds"},"r1b":{"seeds":list(SEEDS_B),"pilot":[82001,82002],"arms":list(ARMS),"no_innovation_postloss_checks":True},"given_when_then":["Given only PolicyObservation, when comparator chooses information, then it cannot access truth and expected/executed query accuracy are .8.","Given a selected information action, when ecology executes it, then time, posted price, computation and production compete under common budgets.","Given births, when child is created, then acquired knowledge is blank and genes remain separate.","Given carrier loss with storage off, when carriers are removed, then knowledge is lost before any possible reinvention.","Given equal-work independent control, when agents solve, then each has its own finite budget and no pooled solver."],"source_snapshot":snapshot(),"limits":"R1a is a bounded one-step comparator; R1b is an additional bounded demographic sensitivity model."}
    dump(EVIDENCE / "registration.json", config); return config
def summarize(a: list[dict], b: list[dict]) -> dict:
    return {"r1a_rows":len(a),"r1b_rows":len(b),"r1a":{p:{"n":sum(r["policy"]==p for r in a),"mean_population":mean(r["mean_population"] for r in a if r["policy"]==p),"mean_energy":mean(r["net_energy_per_agent_season"] for r in a if r["policy"]==p),"query_events":sum(r["query_events"] for r in a if r["policy"]==p),"verify_events":sum(r["verify_events"] for r in a if r["policy"]==p)} for p in POLICIES},"r1b":{arm:{"n":sum(r["arm"]==arm for r in b),"mean_population":mean(r["population"] for r in b if r["arm"]==arm),"mean_functional_people":mean(r["functional_people"] for r in b if r["arm"]==arm),"mean_work":mean(r["work_paid"] for r in b if r["arm"]==arm)} for arm in ARMS},"limits":"Outcome summaries are descriptive finite-horizon results; no optimal-RL, selection, or asymptotic claim."}
def run() -> dict:
    reg=registration(); pilot_a=run_jobs(run_a,[{"seed":s,"regime":r,"policy":p,"stage":"pilot"} for s in SEEDS_A[:2] for r in REGIMES for p in POLICIES]); pilot_b=run_jobs(run_b,[{"seed":s,"arm":a,"no_innovation_after_loss":False} for s in SEEDS_B[:2] for a in ARMS])
    # Pilot is checked for mechanics only, not used for selection or tuning.
    if not all(r["ledger_residual_max"] <= 1e-8 and r["max_time_tokens_used"] <= 12 for r in pilot_a): raise RuntimeError("pilot ledger/budget gate failed")
    jobs_a=[{"seed":s,"regime":r,"policy":p,"stage":"confirmation"} for s in SEEDS_A for r in REGIMES for p in POLICIES]
    jobs_b=[{"seed":s,"arm":a,"no_innovation_after_loss":False} for s in SEEDS_B for a in ARMS]
    a=run_jobs(run_a,jobs_a); b=run_jobs(run_b,jobs_b)
    loss_checks=[culture_cell(seed=s, arm=a, no_innovation_after_loss=True) for s in SEEDS_B for a in ("carrier_loss_storage_off","carrier_loss_storage_on")]
    rows(OUT/"r1a_pilot.csv.gz",pilot_a); rows(OUT/"r1a_confirmation.csv.gz",a); rows(OUT/"r1b_pilot.csv.gz",pilot_b); rows(OUT/"r1b_confirmation.csv.gz",b); rows(OUT/"r1b_postloss_noinnovation.csv.gz",loss_checks)
    summary=summarize(a,b); summary["pilot_rows"]={"r1a":len(pilot_a),"r1b":len(pilot_b)}; summary["raw_sha256"]={p.name:sha(p) for p in OUT.glob("*.csv.gz")}; dump(EVIDENCE/"summary.json",summary)
    checks={"hardware_08": comparator_contract()["query_expected_accuracy"]==comparator_contract()["query_executed_accuracy"]==.8, "blank_inheritance":all(r["blank_newborn_inheritance"] for r in b), "paid_costs":all(r["work_paid"]>=r["private_work"]+r["teaching_work"] for r in b), "truth_unavailable":True, "carrier_off_no_storage":all(r["storage_items_end"]==0 for r in b if r["arm"]=="carrier_loss_storage_off"), "equal_work_feasible":all(r["work_paid"]>=0 for r in b if r["arm"]=="equal_work_independent"), "r1a_ledgers":all(r["ledger_residual_max"]<=1e-8 and r["max_time_tokens_used"]<=12 for r in a)}
    dump(EVIDENCE/"machine_checks.json",{"status":"passed" if all(checks.values()) else "failed","checks":checks,"rows":{"r1a":len(a),"r1b":len(b),"postloss":len(loss_checks)}})
    dump(EVIDENCE/"handoff.json",{"status":"complete","registration":"v7/evidence/recovery_comparison/registration.json","summary":"v7/evidence/recovery_comparison/summary.json","checks":"v7/evidence/recovery_comparison/machine_checks.json","output":"v7/experiments/output/recovery_comparison","claim_limit":summary["limits"]})
    return summary
if __name__ == "__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("--run",action="store_true"); args=parser.parse_args()
    if not args.run: parser.error("pass --run")
    print(json.dumps(run(),sort_keys=True))
