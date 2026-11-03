"""Fresh registered corrected-overlay ecology experiments (four workers max)."""
from __future__ import annotations

import argparse, copy, csv, gzip, hashlib, json, sys, tarfile, time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from v7.experiments.corrected_model import CorrectedEcologyRun
from v7.experiments.confirm_extensions import DepthAwareReliabilityPolicy
from v7.experiments.model import CandidateBPolicy, FeatureTrustPolicy, OrdinarySocialPolicy, VectorOverridePolicy
from v7.experiments.run_experiments import L9_ROWS, LEVELS, POLICIES, _policy_spec, _regime

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "output" / "corrected"
EVIDENCE = ROOT / "evidence" / "corrected"
CONFIG = ROOT / "experiments" / "config.json"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def write_json(path: Path, value: dict) -> None:
    """Atomically register intent before a worker pool can begin producing data."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)
def write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    with gzip.open(path, "wt", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
def source_hashes() -> dict[str, str]:
    files = [ROOT / "experiments" / "model.py", ROOT / "experiments" / "exact.py",
             ROOT / "experiments" / "run_experiments.py", ROOT / "experiments" / "config.json",
             ROOT / "experiments" / "corrected_model.py", Path(__file__)]
    return {str(path.relative_to(ROOT)): sha(path) for path in files}
def base_hashes() -> dict[str, str]:
    manifest = json.loads((ROOT / "evidence" / "core_freeze" / "manifest.json").read_text())
    return manifest["source_sha256"]


def discovery_source_snapshot() -> dict:
    """Archive the exact runnable source set before any corrected outcome exists."""
    snapshot = EVIDENCE / "discovery_source_snapshot"
    snapshot.mkdir(parents=True, exist_ok=True)
    files = [ROOT / "experiments" / "corrected_model.py", Path(__file__),
             ROOT / "experiments" / "run_experiments.py", ROOT / "experiments" / "config.json"]
    archive = snapshot / "source.tar.gz"
    with tarfile.open(archive, "w:gz") as bundle:
        for path in files:
            info = bundle.gettarinfo(str(path), arcname=str(path.relative_to(ROOT)))
            info.mtime = 0; info.uid = info.gid = 0; info.uname = info.gname = ""
            with path.open("rb") as handle: bundle.addfile(info, handle)
    manifest = {"stage":"corrected_discovery_source_snapshot", "files":{str(path.relative_to(ROOT)):sha(path) for path in files},
                "base_frozen_sha256":base_hashes(), "archive":"v7/evidence/corrected/discovery_source_snapshot/source.tar.gz",
                "archive_sha256":sha(archive)}
    write_json(snapshot / "manifest.json", manifest)
    return {"archive_sha256":sha(archive), "manifest_sha256":sha(snapshot / "manifest.json"), "manifest":manifest}


def run_cell(job: dict) -> dict:
    if job["policy"] == "ordinary_social":
        factory, traits = OrdinarySocialPolicy, {"d_procedure": 0., "d_local": 0.}
    elif job["policy"] == "depth_aware_reliability_d0":
        factory, traits = DepthAwareReliabilityPolicy, {"d_procedure": 0., "d_local": 0.}
    else:
        factory, traits = _policy_spec(job["policy"])
    run = CorrectedEcologyRun(job["seed"], factory, depth=job["depth"], chi=job["chi"],
                              q_theta=job["q_theta"], verification_price=job["verification_price"],
                              graph_variant=job.get("graph_variant", 0), initial_traits=traits,
                              label=job["policy"])
    result = run.run(); result.update(job); return result


def run_jobs(jobs: list[dict], workers: int) -> list[dict]:
    if workers != 4: raise ValueError("corrected registration requires exactly four workers")
    with ProcessPoolExecutor(max_workers=4) as pool:
        return list(pool.map(run_cell, jobs, chunksize=1))


def discovery_jobs() -> list[dict]:
    return [{**_regime(regime), "seed": seed, "policy": policy, "stage": "corrected_discovery", "graph_variant": 0}
            for regime in range(9) for policy in POLICIES for seed in range(77001, 77005)]


def register_discovery() -> dict:
    jobs = discovery_jobs()
    snapshot = discovery_source_snapshot()
    value = {"stage": "corrected_discovery", "status": "registered_before_outcomes",
             "registered_at": datetime.now(timezone.utc).isoformat(), "workers": 4,
             "seeds": [77001, 77004], "jobs": len(jobs), "jobs_detail": jobs,
             "same_parameters": {"l9_rows": L9_ROWS, "levels": LEVELS, "policies": POLICIES},
             "base_frozen_sha256": base_hashes(), "overlay_source_sha256": sha(ROOT / "experiments" / "corrected_model.py"),
             "source_sha256": source_hashes(), "config_sha256": sha(CONFIG),
             "immutable_source_snapshot": {"archive_sha256":snapshot["archive_sha256"], "manifest_sha256":snapshot["manifest_sha256"], "path":"v7/evidence/corrected/discovery_source_snapshot"},
             "claim_limit": "Fresh corrected variant; original raw outputs remain invalidated historical artifacts."}
    write_json(EVIDENCE / "discovery_registration.json", value); return value


def run_discovery() -> dict:
    registration = register_discovery(); rows = run_jobs(discovery_jobs(), 4)
    path = OUT / "discovery.csv.gz"; write_rows(path, rows)
    done = {**registration, "status": "complete", "completed_at": datetime.now(timezone.utc).isoformat(),
            "output": str(path.relative_to(ROOT)), "rows": len(rows), "sha256": sha(path)}
    write_json(EVIDENCE / "discovery_result.json", done); return done


def freeze_variant() -> dict:
    discovery = OUT / "discovery.csv.gz"
    if not discovery.exists(): raise RuntimeError("corrected discovery is required before corrected freeze")
    with gzip.open(discovery, "rt", newline="") as handle: rows = list(csv.DictReader(handle))
    if len(rows) != 504 or {int(r["seed"]) for r in rows} != set(range(77001, 77005)):
        raise RuntimeError("corrected discovery partition mismatch")
    by: dict[str, list[float]] = {}
    for row in rows: by.setdefault(row["policy"], []).append(float(row["net_energy_per_agent_season"]))
    # vector_0_0 is a fixed primary comparator.  Choose two additional vectors so
    # the holdout remains the predeclared six-policy, 1,368-row design even if the
    # ordinary comparator happens to lead the discovery grid.
    vectors = sorted((p for p in by if p.startswith("vector_") and p != "vector_0_0"), key=lambda p: (-mean(by[p]), p))[:2]
    scalar = max((p for p in by if p.startswith("scalar_")), key=lambda p: (mean(by[p]), p))
    freeze = EVIDENCE / "freeze_variant"; freeze.mkdir(parents=True, exist_ok=True)
    archive = freeze / "overlay_source.tar.gz"
    overlay = ROOT / "experiments" / "corrected_model.py"
    with tarfile.open(archive, "w:gz") as bundle:
        info = bundle.gettarinfo(str(overlay), arcname="experiments/corrected_model.py"); info.mtime=0; info.uid=info.gid=0; info.uname=info.gname=""
        with overlay.open("rb") as h: bundle.addfile(info, h)
    replay = run_cell({**_regime(4), "seed": 77999, "policy": "vector_0_0", "stage": "corrected_freeze_replay", "graph_variant": 0})
    value = {"stage": "corrected_overlay_freeze", "status": "frozen_before_holdout",
             "frozen_at": datetime.now(timezone.utc).isoformat(), "base_frozen_sha256": base_hashes(),
             "overlay_sha256": sha(overlay), "runner_sha256": sha(Path(__file__)), "config_sha256": sha(CONFIG),
             "discovery_sha256": sha(discovery), "overlay_archive_sha256": sha(archive),
             "candidate_rule": "top two vector policies by corrected discovery mean net_energy; lexical tiebreak; best scalar by same rule",
             "frozen_vectors": vectors, "frozen_scalar": scalar,
             "comparators": ["vector_0_0", "feature_trust", "candidate_b_resource_rational", "asocial_access_off"],
             "replay": {"seed":77999, "replay_digest":replay["replay_digest"]},
             "no_teacher_fix": "teacher=None exposes only private action and uses private cue; base teacher-present path unchanged."}
    write_json(freeze / "manifest.json", value); return value


def holdout_jobs(freeze: dict) -> list[dict]:
    policies = list(dict.fromkeys(["vector_0_0", "feature_trust", "candidate_b_resource_rational", freeze["frozen_scalar"], *freeze["frozen_vectors"]]))
    jobs = [{**_regime(regime), "seed":seed, "policy":policy, "stage":"corrected_holdout", "graph_variant":1}
            for regime in range(9) for policy in policies for seed in range(78001,78025)]
    jobs += [{**_regime(regime), "seed":seed, "policy":"asocial_access_off", "stage":"corrected_holdout_access_sentinel", "graph_variant":1}
             for regime in (0,4,8) for seed in range(78001,78025)]
    return jobs


def run_holdout() -> dict:
    freeze = json.loads((EVIDENCE / "freeze_variant" / "manifest.json").read_text())
    jobs = holdout_jobs(freeze)
    registration = {"stage":"corrected_holdout", "status":"registered_before_outcomes", "registered_at":datetime.now(timezone.utc).isoformat(),
                    "workers":4, "seeds":[78001,78024], "jobs":len(jobs), "policies":sorted({j["policy"] for j in jobs}),
                    "freeze_sha256":sha(EVIDENCE / "freeze_variant" / "manifest.json"), "source_sha256":source_hashes(), "config_sha256":sha(CONFIG)}
    write_json(EVIDENCE / "holdout_registration.json", registration)
    rows=run_jobs(jobs,4); path=OUT / "holdout.csv.gz"; write_rows(path,rows)
    result={**registration,"status":"complete","rows":len(rows),"sha256":sha(path),"output":str(path.relative_to(ROOT))}
    write_json(EVIDENCE / "holdout_result.json", result); return result


def depth_control_jobs(freeze: dict) -> list[dict]:
    """Registered depth-aware control: 3 regimes x 4 fixed policies x 24 seeds."""
    policies = ("ordinary_social", "depth_aware_reliability_d0", "vector_0_5_0", "candidate_b_resource_rational")
    return [{**_regime(regime), "seed": seed, "policy": policy,
             "stage": "corrected_depth_reliability_control", "graph_variant": 1}
            for regime in (0, 4, 8) for policy in policies for seed in range(78501, 78525)]


def run_depth_control() -> dict:
    freeze_path = EVIDENCE / "freeze_variant" / "manifest.json"
    if not freeze_path.exists():
        raise RuntimeError("corrected freeze manifest is required before fixed depth control")
    jobs = depth_control_jobs(json.loads(freeze_path.read_text()))
    registration = {
        "stage": "corrected_depth_reliability_control", "status": "registered_before_outcomes",
        "registered_at": datetime.now(timezone.utc).isoformat(), "workers": 4,
        "seeds": [78501, 78524], "jobs": len(jobs), "jobs_detail": jobs,
        "source_sha256": source_hashes(), "config_sha256": sha(CONFIG),
        "freeze_sha256": sha(freeze_path), "base_frozen_sha256": base_hashes(),
        "control_scope": "Depth-aware d=0 routine-capacity calibration control; it is not a new optimized policy.",
    }
    write_json(EVIDENCE / "depth_control_registration.json", registration)
    rows = run_jobs(jobs, 4); path = OUT / "depth_reliability_control.csv.gz"; write_rows(path, rows)
    result = {**registration, "status": "complete", "rows": len(rows), "sha256": sha(path),
              "output": str(path.relative_to(ROOT))}
    write_json(EVIDENCE / "depth_control_result.json", result); return result


def _h9_job(job: dict) -> list[dict]:
    """Three cloned d=0 arms over CorrectedEcologyRun; no frozen model call."""
    run = CorrectedEcologyRun(job["seed"], OrdinarySocialPolicy, depth=job["depth"], chi=job["chi"], q_theta=job["q_theta"], initial_traits={"d_procedure":0.,"d_local":0.}, burn_in=60, measurement=180, label="corrected_h9_d0")
    checkpoint = run.burn_in + 90
    while run.season < checkpoint and run.status == "running": run.advance_season()
    pre_population, pre_energy = len(run.population), sum(p.energy for p in run.population.values())
    pre_knowledge = sum(len(p.K) for p in run.population.values())
    rows=[]
    for arm,shock,erase in (("control",False,False),("shock",True,False),("shock_memory_erasure",True,True)):
        clone=copy.copy(run)
        for name in ("population","ledger","biological_edges","cultural_edges","decision_samples","reports","_season_events","losses","_time_used","theta"):
            setattr(clone,name,copy.deepcopy(getattr(run,name)))
        clone.stream=hashlib.sha256(); clone.start_time=time.monotonic()
        if shock:
            for family in tuple(clone.theta): clone.theta[family]=1-clone.theta[family]
        removed=0
        if erase:
            for person in clone.population.values(): removed += len(person.K); person.K.clear(); person.independent_successes.clear()
        result=clone.run()
        rows.append({**job,"arm":arm,"checkpoint_season":90,"shock":shock,"memory_erasure":erase,"pre_population":pre_population,"pre_energy":pre_energy,"pre_stored_procedures":pre_knowledge,"removed_procedures":removed,"post_stored_procedures":result["stored_knowledge"],"recovery_status":result["status"],"seasons_completed":result["seasons_completed"],"mean_population":result["mean_population"],"replay_digest":result["replay_digest"],"claim_label":"PARTIAL: corrected-overlay d=0 shock/K-erasure diagnostic; not carrier death, root diversity, d mediation, or causal H9 proof."})
    return rows


def run_h9() -> dict:
    jobs=[{**_regime(regime),"seed":seed,"stage":"corrected_h9_d0","graph_variant":1} for regime in (0,4,8) for seed in range(78601,78625)]
    registration={"stage":"corrected_h9_d0","status":"registered_before_outcomes","registered_at":datetime.now(timezone.utc).isoformat(),"workers":4,"seeds":[78601,78624],"jobs":len(jobs),"registered_rows":len(jobs)*3,"arms":["control","shock","shock_memory_erasure"],"d_procedure":0.,"base_frozen_sha256":base_hashes(),"overlay_source_sha256":sha(ROOT/"experiments"/"corrected_model.py"),"runner_source_sha256":sha(Path(__file__)),"claim_limit":"PARTIAL only: actual d=0 theta shock and K erasure; no carrier death, root diversity, recovery-time mediation, or d-by-shock proof."}
    write_json(EVIDENCE/"corrected_h9_registration.json",registration)
    with ProcessPoolExecutor(max_workers=4) as pool: rows=[row for group in pool.map(_h9_job,jobs,chunksize=1) for row in group]
    path=OUT/"corrected_h9.csv.gz";write_rows(path,rows)
    result={**registration,"status":"complete","rows":len(rows),"output":str(path.relative_to(ROOT)),"sha256":sha(path)}
    write_json(EVIDENCE/"corrected_h9_result.json",result);return result


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--stage", choices=("discovery","freeze","holdout","depth-control","h9"), required=True); args=parser.parse_args()
    value={"discovery":run_discovery,"freeze":freeze_variant,"holdout":run_holdout,"depth-control":run_depth_control,"h9":run_h9}[args.stage](); print(json.dumps(value, sort_keys=True))
if __name__ == "__main__": main()
