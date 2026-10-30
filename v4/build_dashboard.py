#!/usr/bin/env python3
"""Build the v4 single-file offline dashboard from a gzip JSON data artifact."""
from __future__ import annotations

import argparse
import base64
import csv
import gzip
import hashlib
import json
import math
import statistics
from pathlib import Path

import plotly

ROOT = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        type=Path,
        default=ROOT / "experiments" / "dashboard_data.json.gz",
        help="gzip-compressed dashboard JSON",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=ROOT / "dashboard_template.html",
        help="HTML template",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "index.html",
        help="single-file HTML output",
    )
    return parser.parse_args()


def validate_data(data: dict) -> dict:
    required = {"run_id", "ds", "taus", "t", "contexts", "hypotheses", "counts"}
    missing = sorted(required - set(data))
    if missing:
        raise ValueError(f"dashboard data missing keys: {', '.join(missing)}")
    if not data["contexts"]:
        raise ValueError("dashboard data contains no contexts")
    n_cells = len(data["ds"]) * len(data["taus"])
    n_time = len(data["t"])
    if n_cells == 0 or n_time == 0:
        raise ValueError("empty trait grid or time grid")
    required_metrics = {
        "rT",
        "delta_rT",
        "N",
        "belief_A",
        "public_F",
        "dogmatism",
        "confidence",
        "recovery",
        "survival",
        "long_run_growth",
        "invasion",
    }
    required_series = {
        "F",
        "A",
        "N",
        "B",
        "D",
        "M",
        "belief_F",
        "belief_A",
        "public_F",
        "advice",
        "confidence",
        "dogmatism",
        "per_capita",
    }
    ids: set[str] = set()
    for i, context in enumerate(data["contexts"]):
        label = context.get("id", f"context[{i}]")
        if label in ids:
            raise ValueError(f"duplicate context id: {label}")
        ids.add(label)
        for key in ("id", "model", "scenario", "config", "metrics", "series"):
            if key not in context:
                raise ValueError(f"{label} missing {key}")
        missing_metrics = sorted(required_metrics - set(context["metrics"]))
        missing_series = sorted(required_series - set(context["series"]))
        if missing_metrics:
            raise ValueError(f"{label} missing metrics: {', '.join(missing_metrics)}")
        if missing_series:
            raise ValueError(f"{label} missing series: {', '.join(missing_series)}")
        for key, values in context["metrics"].items():
            if len(values) != n_cells:
                raise ValueError(f"{label} metric {key} has {len(values)} cells, expected {n_cells}")
        for key, values in context["series"].items():
            if len(values) != n_cells:
                raise ValueError(f"{label} series {key} has {len(values)} cells, expected {n_cells}")
            bad = next((j for j, row in enumerate(values) if len(row) != n_time), None)
            if bad is not None:
                raise ValueError(
                    f"{label} series {key}[{bad}] has {len(values[bad])} points, expected {n_time}"
                )
    return {"contexts": len(data["contexts"]), "cells_per_context": n_cells, "time_points": n_time}


def read_json_if_present(path: Path):
    return json.loads(path.read_text()) if path.exists() else None


def typed_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            clean: dict = {}
            for key, value in row.items():
                if value in (None, ""):
                    clean[key] = None
                    continue
                try:
                    number = float(value)
                    clean[key] = int(number) if number.is_integer() and key == "seed" else number
                except ValueError:
                    clean[key] = value
            rows.append(clean)
    return rows


def stochastic_summary(rows: list[dict]) -> list[dict]:
    groups: dict[tuple, list[dict]] = {}
    for row in rows:
        key = (row.get("phase"), row.get("model"), row.get("d"), row.get("tau"))
        groups.setdefault(key, []).append(row)
    output: list[dict] = []
    measures = ("rT", "N", "mean_adult_accuracy", "mean_persistence")
    for (phase, model, d, tau), group in sorted(groups.items(), key=str):
        record = {"phase": phase, "model": model, "d": d, "tau": tau, "n": len(group)}
        for measure in measures:
            values = [float(row[measure]) for row in group if row.get(measure) is not None and math.isfinite(float(row[measure]))]
            if not values:
                record[measure] = record[f"{measure}_ci95"] = None
                continue
            mean = statistics.fmean(values)
            half = 1.96 * statistics.stdev(values) / math.sqrt(len(values)) if len(values) > 1 else 0.0
            record[measure] = mean
            record[f"{measure}_ci95"] = [mean - half, mean + half]
        output.append(record)
    return output


def enrich_evolution(data: dict, experiment_dir: Path) -> dict:
    competition = read_json_if_present(experiment_dir / "competition.json")
    pairwise = typed_csv(experiment_dir / "pairwise_invasion.csv")
    dynamic = typed_csv(experiment_dir / "dynamic_invasion.csv")
    stochastic = typed_csv(experiment_dir / "stochastic.csv")
    selection_out_of_sample = typed_csv(experiment_dir / "selection_out_of_sample.csv")
    volatility = read_json_if_present(experiment_dir / "volatility.json")
    enriched = {
        "competition": competition or {},
        "selection_refinement": read_json_if_present(experiment_dir / "selection_refinement.json"),
        "isolated_growth_refinement": read_json_if_present(experiment_dir / "refinement.json"),
        "selection_out_of_sample": selection_out_of_sample,
        "no_truth_control": read_json_if_present(experiment_dir / "no_truth_control.json"),
        "reproductive_value": read_json_if_present(experiment_dir / "reproductive_value.json"),
        "replacement": read_json_if_present(experiment_dir / "replacement.json"),
        "volatility": volatility,
        "local_invasion": read_json_if_present(experiment_dir / "local_invasion.json"),
        "dynamic_convergence": read_json_if_present(experiment_dir / "dynamic_convergence.json"),
        "pairwise_invasion": pairwise,
        "dynamic_invasion": dynamic,
        "stochastic_summary": stochastic_summary(stochastic),
        "stochastic_interval_note": "Means and normal-approximation 95% intervals summarize variation across seeded environmental paths only; they are not biological, parameter, or measurement uncertainty intervals.",
    }
    data["evolution"] = enriched
    return {
        "competition_scenarios": len(enriched["competition"]),
        "pairwise_rows": len(pairwise),
        "dynamic_rows": len(dynamic),
        "stochastic_groups": len(enriched["stochastic_summary"]),
        "selection_sensitivity_rows": len(selection_out_of_sample),
        "volatility_contrasts": len((volatility or {}).get("paired_contrasts", [])),
    }


def normalize_legacy_series(data: dict) -> int:
    """Give pre-correction private-choice output an honest export name."""
    renamed = 0
    for context in data["contexts"]:
        series = context["series"]
        if "private_sampling" in series and "private_choice_on_conflict" not in series:
            series["private_choice_rate_legacy"] = series.pop("private_sampling")
            renamed += 1
    if renamed:
        data.setdefault("dashboard_transformations", []).append(
            {
                "field": "private_sampling",
                "renamed_to": "private_choice_rate_legacy",
                "reason": "Stored sweep predates the metric correction; values are nu_F*(1-E_F(w_r)), not private-signal sampling.",
                "contexts": renamed,
            }
        )
    return renamed


def main() -> None:
    args = parse_args()
    compressed = args.data.read_bytes()
    try:
        data = json.loads(gzip.decompress(compressed))
    except Exception as exc:  # pragma: no cover - gives a useful build error
        raise ValueError(f"cannot decode {args.data} as gzip JSON: {exc}") from exc
    dimensions = validate_data(data)
    normalized_legacy_series = normalize_legacy_series(data)
    enrichment = enrich_evolution(data, args.data.parent)
    compressed = gzip.compress(json.dumps(data, separators=(",", ":"), allow_nan=False).encode(), mtime=0)

    plotly_bundle = Path(plotly.__file__).parent / "package_data" / "plotly.min.js"
    template = args.template.read_text()
    for marker in ("/*__PLOTLY__*/", "/*__DATA_GZIP_BASE64__*/"):
        if marker not in template:
            raise ValueError(f"template is missing marker {marker}")
    html = template.replace("/*__PLOTLY__*/", plotly_bundle.read_text()).replace(
        "/*__DATA_GZIP_BASE64__*/",
        json.dumps(base64.b64encode(compressed).decode("ascii")),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html)
    (args.output.parent / "research_dashboard.html").write_text(html)
    result = {
        "output": str(args.output),
        "run_id": data["run_id"],
        "plotly_version": plotly.__version__,
        "compressed_data_bytes": len(compressed),
        "html_bytes": args.output.stat().st_size,
        "html_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        **dimensions,
        **enrichment,
        "normalized_legacy_series": normalized_legacy_series,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
