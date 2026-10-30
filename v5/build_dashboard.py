#!/usr/bin/env python3
"""Build the V5 self-contained offline research dashboard."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import math
from pathlib import Path

import plotly


ROOT = Path(__file__).resolve().parent
MODELS = {"retained", "frozen", "audit", "reset", "oracle"}
SCENARIOS = {
    "stable",
    "clean",
    "noisy",
    "sparse",
    "load",
    "truth_reversal",
    "misinformation",
    "wrong_history",
    "no_cost",
    "neutral",
}
REQUIRED_METRICS = {
    "N", "rT", "delta_rT", "invasion", "survival", "private_F", "private_A",
    "belief_F", "belief_A", "public_F", "advice", "confidence", "persistence",
    "wrong_confidence", "peak_wrong_confidence", "query_rate", "query_A",
    "query_cost", "cumulative_query_cost", "override", "conflict", "tail_growth",
    "recovery", "accuracy_debt",
}
REQUIRED_SERIES = {
    "F", "A", "N", "B", "DF", "DA", "D", "M", "per_capita", "private_F",
    "private_A", "belief_F", "belief_A", "public_F", "advice", "confidence",
    "persistence", "wrong_confidence", "query_rate", "query_F", "query_A",
    "query_cost", "override", "conflict",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "experiments" / "dashboard_data.json.gz")
    parser.add_argument("--template", type=Path, default=ROOT / "dashboard_template.html")
    parser.add_argument("--output", type=Path, default=ROOT / "index.html")
    return parser.parse_args()


def finite_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate_payload(data: dict) -> dict:
    required = {
        "schema_version", "run_id", "label", "ds", "taus", "t", "scores",
        "contexts", "counts", "hypotheses",
    }
    missing = sorted(required - set(data))
    if missing:
        raise ValueError(f"dashboard payload missing keys: {', '.join(missing)}")
    if data["schema_version"] != 1:
        raise ValueError(f"unsupported schema_version {data['schema_version']!r}")
    if data["label"] != "simulation data":
        raise ValueError("payload must remain labelled simulation data")
    ds, taus, times, scores = data["ds"], data["taus"], data["t"], data["scores"]
    if not ds or not taus or not times or not scores:
        raise ValueError("empty dashboard axis")
    if any(not finite_number(x) for x in ds + taus + times + scores):
        raise ValueError("nonfinite dashboard axis")
    if any(b <= a for a, b in zip(ds, ds[1:])) or any(b <= a for a, b in zip(taus, taus[1:])):
        raise ValueError("d and tau axes must be strictly increasing")
    if any(x <= 0 for x in taus):
        raise ValueError("tau must be positive for a logarithmic axis")
    if any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError("time axis must be strictly increasing")
    n_cells, n_time, n_scores = len(ds) * len(taus), len(times), len(scores)
    contexts = data["contexts"]
    if len(contexts) != len(MODELS) * len(SCENARIOS):
        raise ValueError(f"expected {len(MODELS) * len(SCENARIOS)} contexts, found {len(contexts)}")
    got_pairs: set[tuple[str, str]] = set()
    ids: set[str] = set()
    for index, context in enumerate(contexts):
        label = context.get("id", f"context[{index}]")
        for key in ("id", "model", "scenario", "config", "segments", "d_inactive", "metrics", "series", "distF", "distA"):
            if key not in context:
                raise ValueError(f"{label} missing {key}")
        if label in ids:
            raise ValueError(f"duplicate context id: {label}")
        ids.add(label)
        got_pairs.add((context["model"], context["scenario"]))
        missing_metrics = sorted(REQUIRED_METRICS - set(context["metrics"]))
        missing_series = sorted(REQUIRED_SERIES - set(context["series"]))
        if missing_metrics:
            raise ValueError(f"{label} missing metrics: {', '.join(missing_metrics)}")
        if missing_series:
            raise ValueError(f"{label} missing series: {', '.join(missing_series)}")
        for key, values in context["metrics"].items():
            if len(values) != n_cells:
                raise ValueError(f"{label} metric {key}: {len(values)} cells, expected {n_cells}")
        for key, values in context["series"].items():
            if len(values) != n_cells:
                raise ValueError(f"{label} series {key}: {len(values)} cells, expected {n_cells}")
            bad = next((i for i, row in enumerate(values) if len(row) != n_time), None)
            if bad is not None:
                raise ValueError(f"{label} series {key}[{bad}] has {len(values[bad])} times, expected {n_time}")
        for stage in ("distF", "distA"):
            values = context[stage]
            if len(values) != n_cells:
                raise ValueError(f"{label} {stage}: {len(values)} cells, expected {n_cells}")
            bad_time = next((i for i, rows in enumerate(values) if len(rows) != n_time), None)
            if bad_time is not None:
                raise ValueError(f"{label} {stage}[{bad_time}] has wrong time dimension")
            bad_score = next(
                ((i, j) for i, rows in enumerate(values) for j, row in enumerate(rows) if len(row) != n_scores),
                None,
            )
            if bad_score is not None:
                raise ValueError(f"{label} {stage}{bad_score} has wrong score dimension")
        if context["model"] == "oracle" and not context["d_inactive"]:
            raise ValueError(f"{label}: oracle must declare d inactive")
        if context["model"] != "oracle" and context["d_inactive"]:
            raise ValueError(f"{label}: only oracle may declare d inactive")
    expected_pairs = {(m, s) for m in MODELS for s in SCENARIOS}
    if got_pairs != expected_pairs:
        raise ValueError(f"context model/scenario coverage mismatch: {sorted(expected_pairs ^ got_pairs)}")
    return {
        "contexts": len(contexts),
        "cells_per_context": n_cells,
        "time_points": n_time,
        "score_states": n_scores,
    }


def read_json(path: Path):
    return json.loads(path.read_text()) if path.exists() else None


def enrich(payload: dict, experiment_dir: Path) -> dict:
    supplements = {
        "repertoire": read_json(experiment_dir / "repertoire.json"),
        "mechanisms": read_json(experiment_dir / "mechanisms.json"),
        "selection": read_json(experiment_dir / "selection.json"),
        "source_conditions": read_json(experiment_dir / "source_conditions.json"),
        "histories_summary": read_json(experiment_dir / "histories_summary.json"),
        "repertoire_tutors": read_json(experiment_dir / "repertoire_tutors.json"),
        "bayes_benchmark": read_json(experiment_dir / "bayes_benchmark.json"),
        "cost_memory": read_json(experiment_dir / "cost_memory.json"),
        "refinement": read_json(experiment_dir / "refinement.json"),
        "dynamic_convergence": read_json(experiment_dir / "dynamic_convergence.json"),
        "selection_refinement": read_json(experiment_dir / "selection_refinement.json"),
        "mechanism_invasion": read_json(experiment_dir / "mechanism_invasion.json"),
        "frozen_replacement": read_json(experiment_dir / "frozen_replacement.json"),
    }
    payload["supplements"] = supplements
    return {key: bool(value) for key, value in supplements.items()}


def compact_inactive_oracle(payload: dict) -> int:
    """Losslessly store one d-row for oracle contexts; the browser reconstructs duplicate views."""
    n_tau = len(payload["taus"])
    n_d = len(payload["ds"])
    compacted = 0
    for context in payload["contexts"]:
        if not context["d_inactive"]:
            continue
        for section in ("metrics", "series"):
            for key, values in context[section].items():
                first = values[:n_tau]
                if any(values[i * n_tau:(i + 1) * n_tau] != first for i in range(1, n_d)):
                    raise ValueError(f"{context['id']} {section}.{key} is not exactly duplicated over inactive d")
                context[section][key] = first
        for section in ("distF", "distA"):
            values = context[section]
            first = values[:n_tau]
            if any(values[i * n_tau:(i + 1) * n_tau] != first for i in range(1, n_d)):
                raise ValueError(f"{context['id']} {section} is not exactly duplicated over inactive d")
            context[section] = first
        context["oracle_compact"] = True
        compacted += 1
    payload["dashboard_storage"] = {
        "oracle_contexts_compacted": compacted,
        "method": "one exact tau row stored for d-inactive oracle contexts; duplicate d views and exports reconstructed in browser",
        "numeric_rounding": False,
    }
    return compacted


def main() -> None:
    args = parse_args()
    try:
        payload = json.loads(gzip.decompress(args.data.read_bytes()))
    except Exception as exc:
        raise ValueError(f"cannot decode {args.data} as gzip JSON: {exc}") from exc
    dimensions = validate_payload(payload)
    supplements = enrich(payload, args.data.parent)
    compacted_oracles = compact_inactive_oracle(payload)
    reviewed = gzip.compress(json.dumps(payload, separators=(",", ":"), allow_nan=False).encode(), mtime=0)
    template = args.template.read_text()
    for marker in ("/*__PLOTLY__*/", "/*__DATA_GZIP_BASE64__*/"):
        if marker not in template:
            raise ValueError(f"template missing marker {marker}")
    plotly_bundle = Path(plotly.__file__).parent / "package_data" / "plotly.min.js"
    html = template.replace("/*__PLOTLY__*/", plotly_bundle.read_text()).replace(
        "/*__DATA_GZIP_BASE64__*/", json.dumps(base64.b64encode(reviewed).decode("ascii"))
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html)
    mirror = args.output.parent / "research_dashboard.html"
    mirror.write_text(html)
    digest = hashlib.sha256(html.encode()).hexdigest()
    print(json.dumps({
        "output": str(args.output),
        "mirror": str(mirror),
        "run_id": payload["run_id"],
        "plotly_version": plotly.__version__,
        "compressed_data_bytes": len(reviewed),
        "html_bytes": len(html.encode()),
        "html_sha256": digest,
        "mirror_sha256": hashlib.sha256(mirror.read_bytes()).hexdigest(),
        **dimensions,
        "supplements": supplements,
        "compacted_oracle_contexts": compacted_oracles,
    }, indent=2))


if __name__ == "__main__":
    main()
