"""Register, gate, and execute fresh R1b paired matched-work controls."""
from __future__ import annotations
import argparse, csv, gzip, hashlib, json, sys, tarfile
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]; REPO = ROOT.parent
if str(REPO) not in sys.path: sys.path.insert(0, str(REPO))
from v7.experiments.recovery_culture_matched import run_pair
OUT = ROOT / "experiments" / "output" / "recovery_comparison"; EVIDENCE = ROOT / "evidence" / "recovery_comparison"; SEEDS = tuple(range(82201, 82225))
def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p: Path, x: object) -> None: p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(x, indent=2, sort_keys=True) + "\n")
def write(p: Path, values: list[dict]) -> None:
    fields = ["seed","horizon","person_work_cap","population_cap","status","offered_work_total","ti_realized_work","independent_realized_work","any_infeasible","ti_population","ti_functional","ti_knowledge","independent_population","independent_functional","independent_knowledge","claim_limit"]
    with gzip.open(p, "wt", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields); w.writeheader(); w.writerows([{k:v for k,v in r.items() if k != "seasons"} for r in values])
def register() -> dict:
    files = [ROOT / "experiments" / "recovery_culture_matched.py", ROOT / "experiments" / "run_recovery_culture_matched.py"]; archive = EVIDENCE / "matched_work_source_snapshot.tar.gz"
    with tarfile.open(archive, "w:gz") as bundle:
        for file in files:
            info = bundle.gettarinfo(str(file), arcname=str(file.relative_to(ROOT))); info.mtime=0; info.uid=info.gid=0; info.uname=info.gname=""
            with file.open("rb") as h: bundle.addfile(info, h)
    value = {"status":"registered_before_outcomes", "registered_at":datetime.now(timezone.utc).isoformat(), "seeds":list(SEEDS), "pairs":24,
             "mechanism":"Each season W=min(feasible TI person-work, feasible independent person-work); each independent population allocates W only among its own live persons with cap 4. No shared K, outcomes, resources, or people.",
             "source_sha256":{str(f.relative_to(ROOT)):sha(f) for f in files}, "archive_sha256":sha(archive),
             "gates":["equal offered and realized work", "per-person caps", "no pooled knowledge/outcomes", "retain one/both extinction and cap status"], "claim_limit":"Paired shared-work intervention, not competition."}
    dump(EVIDENCE / "matched_work_registration.json", value); return value
def run() -> dict:
    register(); pilot = [run_pair(seed) for seed in SEEDS[:2]]
    if not all(r["ti_realized_work"] == r["independent_realized_work"] == r["offered_work_total"] and not r["any_infeasible"] for r in pilot): raise RuntimeError("matched-work pilot gate failed")
    with ProcessPoolExecutor(max_workers=4) as pool: result = list(pool.map(run_pair, SEEDS, chunksize=1))
    write(OUT / "r1b_matched_work_pilot.csv.gz", pilot); write(OUT / "r1b_matched_work_confirmation.csv.gz", result)
    dump(EVIDENCE / "matched_work_raw_seasons.json", {"rows":result})
    summary = {"rows":len(result), "equal_work_pairs":sum(r["ti_realized_work"] == r["independent_realized_work"] == r["offered_work_total"] for r in result), "infeasible_pairs":sum(r["any_infeasible"] for r in result), "status_counts":{x:sum(r["status"] == x for r in result) for x in sorted({r["status"] for r in result})}, "ti_functional_mean":mean(r["ti_functional"] for r in result), "independent_functional_mean":mean(r["independent_functional"] for r in result), "raw_sha256":sha(OUT / "r1b_matched_work_confirmation.csv.gz"), "scope":"Exact paired realized effort under finite cap/horizon; no competition or long-run inference."}
    dump(EVIDENCE / "matched_work_summary.json", summary); dump(EVIDENCE / "matched_work_checks.json", {"status":"passed" if summary["equal_work_pairs"] == 24 and not summary["infeasible_pairs"] else "failed", **summary}); return summary
if __name__ == "__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("--run", action="store_true"); args=parser.parse_args()
    if not args.run: parser.error("pass --run")
    print(json.dumps(run(), sort_keys=True))
