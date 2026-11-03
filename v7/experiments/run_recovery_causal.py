"""Registered runner for R2 causal ecology/provenance and adult diagnostics."""
from __future__ import annotations
import argparse, csv, gzip, json, tarfile
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

from v7.experiments.recovery_causal import ADULT_SEEDS, ECOLOGY_SEEDS, HORIZON, REGIMES, adult_trajectory, ecological_seed_records, summarize

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "output" / "recovery_causal"
EVIDENCE = ROOT / "evidence" / "recovery_causal"
CONFIG = EVIDENCE / "recovery_causal_config.json"

def digest(path: Path) -> str: return sha256(path.read_bytes()).hexdigest()
def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n"); temp.replace(path)
def write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); fields = sorted({key for row in rows for key in row})
    with gzip.open(path, "wt", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader(); writer.writerows(rows)

def freeze(mode: str) -> dict[str, Any]:
    files = [ROOT / "experiments" / "recovery_causal.py", Path(__file__), ROOT / "experiments" / "corrected_model.py", ROOT / "experiments" / "model.py", ROOT / "experiments" / "postfreeze.py", CONFIG]
    archive = EVIDENCE / f"source_freeze_{mode}.tar.gz"; archive.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "w:gz") as bundle:
        for path in files:
            info = bundle.gettarinfo(str(path), arcname=str(path.relative_to(ROOT))); info.mtime = 0; info.uid = info.gid = 0; info.uname = info.gname = ""
            with path.open("rb") as handle: bundle.addfile(info, handle)
    payload = {"stage": "recovery-causal-source-freeze", "frozen_at": datetime.now(timezone.utc).isoformat(),
               "files": {str(path.relative_to(ROOT)): digest(path) for path in files}, "archive": str(archive.relative_to(ROOT)), "archive_sha256": digest(archive),
               "immutable_dependencies": ["v7/experiments/model.py", "v7/experiments/corrected_model.py", "v7/experiments/postfreeze.py"]}
    write_json(EVIDENCE / f"source_freeze_{mode}.json", payload); return payload

def registration(pilot: bool, source: dict[str, Any]) -> dict[str, Any]:
    seeds = [ECOLOGY_SEEDS[0]] if pilot else list(ECOLOGY_SEEDS)
    adult = [ADULT_SEEDS[0]] if pilot else list(ADULT_SEEDS)
    value = {"stage": "recovery-causal-registration", "status": "registered_before_outcomes", "registered_at": datetime.now(timezone.utc).isoformat(),
             "mode": "pilot" if pilot else "confirmation", "ecological_seeds": seeds, "adult_seeds": adult, "sentinel_regimes": list(REGIMES), "horizon": HORIZON,
             "workers": 2, "fixed_seed_cap": 24, "adult_steps": 20, "adult_evidence_directions": ["supporting", "contrary"], "likelihood_strength": .80,
             "private_hardware_accuracy": .8, "authority_design": "message/evidence matched randomized visible label; d=0 label-neutral arm and d=.5 operational treatment; no obedience reward",
             "provenance_design": "actual corrected-world physical root IDs; copied/independent x visible/hidden; unknown never counted as independent",
             "precision": "Wilson only on seed-level clusters; repeated records are not independent Bernoulli trials; no extensions beyond fixed cap.",
             "given_when_then": ["Given matched actual messages, when labels change under d=0, then paired action is unchanged.", "Given actual distinct root IDs, when visibility changes, then content is preserved and hidden provenance is evaluator-only.", "Given matched likelihood directions, when twenty adult updates run, then B/K/H/T and action are separately exported with direct adult override zero."],
             "source_freeze_sha256": digest(EVIDENCE / f"source_freeze_{'pilot' if pilot else 'confirmation'}.json"), "source_archive_sha256": source["archive_sha256"]}
    write_json(EVIDENCE / ("pilot_registration.json" if pilot else "registration.json"), value); return value

def run(pilot: bool) -> dict[str, Any]:
    stem = "pilot" if pilot else "confirmation"
    source = freeze(stem); reg = registration(pilot, source)
    eco_seeds = reg["ecological_seeds"]; adult_seeds = reg["adult_seeds"]
    jobs = [(seed, regime) for seed in eco_seeds for regime in REGIMES]
    with ProcessPoolExecutor(max_workers=2) as pool:
        ecological = [row for group in pool.map(ecological_seed_records, jobs, chunksize=1) for row in group]
        adults = [row for seed in adult_seeds for direction in (1, -1) for row in adult_trajectory(seed, direction)]
    all_rows = ecological + adults
    raw = OUT / f"{stem}_raw.csv.gz"; write_rows(raw, all_rows)
    report = summarize(all_rows)
    report.update({"stage": "recovery-causal", "mode": stem, "registration": str((EVIDENCE / ("pilot_registration.json" if pilot else "registration.json")).relative_to(ROOT)), "raw": str(raw.relative_to(ROOT)), "raw_sha256": digest(raw), "source_freeze": str((EVIDENCE / f"source_freeze_{stem}.json").relative_to(ROOT))})
    write_json(OUT / f"{stem}_summary.json", report); write_json(EVIDENCE / f"{stem}_verification.json", report)
    return report

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--pilot", action="store_true"); parser.add_argument("--run", action="store_true"); args = parser.parse_args()
    if args.pilot == args.run: parser.error("choose exactly one of --pilot or --run")
    print(json.dumps(run(args.pilot), indent=2, sort_keys=True))
if __name__ == "__main__": main()
