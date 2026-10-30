"""Independent consistency audit for the exported V5 simulation artifacts.

This script does not regenerate scientific results.  It reads the exported
CSV/JSON/NPZ products, independently recomputes accounting identities and a
small set of declared contrasts, and writes ``artifact_verification.json``.
"""

from __future__ import annotations

import csv
import gzip
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "artifact_verification.json"
TOL = 1e-8


def read_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(name: str):
    return json.loads((ROOT / name).read_text())


def number(value) -> float:
    if value is None:
        return np.nan
    return float(value)


def max_error(left, right) -> float:
    a = np.asarray(left, dtype=float)
    b = np.asarray(right, dtype=float)
    if a.shape != b.shape:
        return float("inf")
    both_nan = np.isnan(a) & np.isnan(b)
    mismatch = np.isnan(a) ^ np.isnan(b)
    if mismatch.any():
        return float("inf")
    finite = ~(both_nan | np.isinf(a) | np.isinf(b))
    if np.any((np.isinf(a) | np.isinf(b)) & (a != b)):
        return float("inf")
    return float(np.max(np.abs(a[finite] - b[finite]))) if finite.any() else 0.0


def main() -> None:
    checks: list[dict] = []
    diagnostics: dict = {}

    def check(name: str, passed: bool, measured=None, detail: str = "") -> None:
        checks.append(
            {
                "name": name,
                "passed": bool(passed),
                "measured": measured,
                "detail": detail,
            }
        )

    required = [
        "dashboard_data.json.gz",
        "sweep.csv",
        "run_manifest.json",
        "residents.json",
        "mechanisms.csv",
        "mechanisms.json",
        "source_conditions.csv",
        "source_conditions.json",
        "histories.csv",
        "histories_summary.json",
        "sensitivity.csv",
        "sensitivity.json",
        "repertoire.csv",
        "repertoire.json",
        "architecture_residents.json",
        "architecture_invasion.csv",
        "pairwise.csv",
        "competition.json",
        "dynamic_invasion.csv",
        "dynamic_convergence.json",
        "selection.json",
    ]
    missing = [name for name in required if not (ROOT / name).is_file()]
    check("required exported artifacts exist", not missing, missing)
    if missing:
        OUT.write_text(json.dumps({"status": "FAIL", "checks": checks}, indent=2) + "\n")
        raise SystemExit(f"missing required artifacts: {missing}")

    manifest = read_json("run_manifest.json")
    sweep = read_csv("sweep.csv")
    with gzip.open(ROOT / "dashboard_data.json.gz", "rt") as handle:
        dash = json.load(handle)

    ds = np.asarray(dash["ds"], dtype=float)
    taus = np.asarray(dash["taus"], dtype=float)
    times = np.asarray(dash["t"], dtype=float)
    contexts = dash["contexts"]
    ngrid = len(ds) * len(taus)
    expected_d = np.repeat(ds, len(taus))
    expected_tau = np.tile(taus, len(ds))
    expected_ids = {
        f"{model}_{scenario}"
        for model in ("retained", "frozen", "audit", "reset", "oracle")
        for scenario in (
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
        )
    }
    context_ids = [cx["id"] for cx in contexts]
    check(
        "main grid and context cardinality",
        len(ds) == 13
        and len(taus) == 15
        and len(times) == 81
        and len(contexts) == 50
        and set(context_ids) == expected_ids
        and len(sweep) == 9750,
        {
            "d": len(ds),
            "tau": len(taus),
            "time": len(times),
            "contexts": len(contexts),
            "sweep_rows": len(sweep),
        },
        "Expected 13 x 15 x 81 per context, 50 contexts and 9,750 view rows.",
    )
    check(
        "manifest cardinalities agree with exports",
        manifest["counts"] == dash["counts"]
        and dash["counts"]["pilot"] == 200
        and dash["counts"]["main_unique_trajectories"] == 7950
        and dash["counts"]["main_view_cells"] == 9750,
        dash["counts"],
    )
    check(
        "run identifiers agree",
        manifest["run_id"] == dash["run_id"]
        and all(row["run_id"] == dash["run_id"] for row in sweep),
        dash["run_id"],
    )

    sweep_by_context: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in sweep:
        sweep_by_context[(row["model"], row["scenario"])].append(row)

    series_errors: list[float] = []
    metric_errors: list[float] = []
    dist_errors: list[float] = []
    stage_errors: list[float] = []
    tail_errors: list[float] = []
    minimum_density = float("inf")
    survival_values: list[float] = []
    recovery_values: list[float] = []
    recovery_censored = 0
    config_ok = True
    grid_ok = True
    d0_off_diagonal = 0.0
    oracle_d_error = 0.0
    common_resident_ok = True
    residents = read_json("residents.json")
    transient = {"truth_reversal", "misinformation"}
    resident_scenarios = set(residents)
    metric_names = list(contexts[0]["metrics"])

    for cx in contexts:
        model, scenario = cx["model"], cx["scenario"]
        rows = sweep_by_context[(model, scenario)]
        config_ok &= len(rows) == ngrid and cx["id"] == f"{model}_{scenario}"
        grid_ok &= max_error([number(r["d"]) for r in rows], expected_d) <= TOL
        grid_ok &= max_error([number(r["tau"]) for r in rows], expected_tau) <= TOL

        expected_resident = None if scenario in transient else residents[scenario]
        common_resident_ok &= cx["resident"] == expected_resident
        if expected_resident is not None:
            common_resident_ok &= expected_resident["architecture"] == "retained"
            common_resident_ok &= expected_resident["d"] == 0.5
            common_resident_ok &= expected_resident["tau"] == 3.0

        with np.load(ROOT / f"{cx['id']}.npz") as raw:
            grid_ok &= raw["d"].shape == (ngrid,) and raw["tau"].shape == (ngrid,)
            grid_ok &= max_error(raw["d"], expected_d) <= TOL
            grid_ok &= max_error(raw["tau"], expected_tau) <= TOL
            grid_ok &= raw["N"].shape == (ngrid, len(times))
            grid_ok &= raw["distF"].shape == (ngrid, len(times), 9)
            grid_ok &= raw["distA"].shape == (ngrid, len(times), 9)
            grid_ok &= raw["final_state"].shape == (ngrid, 2, 9, 9)
            minimum_density = min(
                minimum_density,
                float(np.min(raw["F"])),
                float(np.min(raw["A"])),
                float(np.min(raw["N"])),
                float(np.min(raw["distF"])),
                float(np.min(raw["distA"])),
                float(np.min(raw["final_state"])),
            )
            stage_errors.append(max_error(raw["distF"].sum(axis=2), raw["F"]))
            stage_errors.append(max_error(raw["distA"].sum(axis=2), raw["A"]))
            stage_errors.append(max_error(raw["F"] + raw["A"], raw["N"]))
            stage_errors.append(max_error(raw["final_state"].sum((1, 2, 3)), raw["N"][:, -1]))

            for key, value in cx["series"].items():
                series_errors.append(max_error(raw[key], value))
            dist_errors.append(max_error(raw["distF"], cx["distF"]))
            dist_errors.append(max_error(raw["distA"], cx["distA"]))

            # Fixed-policy d=0 prohibits accepted testimony, hence private and
            # held scores remain equal. Oracle-gate is intentionally excluded:
            # its effective acceptance is endogenous and its plotted d is inert.
            if model != "oracle":
                fs = raw["final_state"].reshape(len(ds), len(taus), 2, 9, 9)[0]
                off = ~np.eye(9, dtype=bool)
                d0_off_diagonal = max(d0_off_diagonal, float(fs[..., off].max()))

            if model == "oracle":
                for key in raw.files:
                    if key in {"t", "d", "tau"}:
                        continue
                    arr = raw[key]
                    if arr.shape and arr.shape[0] == ngrid:
                        shaped = arr.reshape((len(ds), len(taus)) + arr.shape[1:])
                        oracle_d_error = max(
                            oracle_d_error,
                            max_error(shaped, np.broadcast_to(shaped[:1], shaped.shape)),
                        )

            idx = int(np.searchsorted(raw["t"], max(0.0, cx["config"]["T"] - 100.0)))
            exact_tail = np.log(raw["N"][:, -1] / raw["N"][:, idx]) / (
                raw["t"][-1] - raw["t"][idx]
            )
            tail_errors.append(max_error(exact_tail, cx["metrics"]["tail_growth"]))

        for key in metric_names:
            metric_errors.append(
                max_error(cx["metrics"][key], [number(row[key]) for row in rows])
            )
        survival_values.extend(number(x) for x in cx["metrics"]["survival"])
        for value in cx["metrics"]["recovery"]:
            if value is None:
                recovery_censored += 1
            else:
                recovery_values.append(float(value))
        if scenario not in transient:
            config_ok &= all(x is None for x in cx["metrics"]["recovery"])

    check("within-context configuration and grid are fixed", config_ok and grid_ok)
    check(
        "NPZ, dashboard series and distributions agree",
        max(series_errors + dist_errors) <= TOL,
        {
            "max_series_error": max(series_errors),
            "max_distribution_error": max(dist_errors),
        },
    )
    check(
        "dashboard metrics and sweep CSV agree",
        max(metric_errors) <= TOL,
        max(metric_errors),
        "CSV nan and dashboard null are treated as the same censored value.",
    )
    check(
        "all exported densities are nonnegative",
        minimum_density >= -1e-10,
        minimum_density,
        "No clipping is performed by the simulator.",
    )
    check(
        "score distributions reconcile to stage stocks",
        max(stage_errors) <= TOL,
        max(stage_errors),
    )
    check(
        "maturation survival is a probability",
        min(survival_values) >= -TOL and max(survival_values) <= 1 + TOL,
        {"min": min(survival_values), "max": max(survival_values)},
    )
    check(
        "recovery uses explicit censoring",
        all(0 <= x <= times[-1] - 150 for x in recovery_values)
        and recovery_censored + len(recovery_values) == len(contexts) * ngrid,
        {
            "observed": len(recovery_values),
            "censored": recovery_censored,
            "range": [min(recovery_values), max(recovery_values)] if recovery_values else None,
        },
    )
    check("main tail growth is exactly the last 100 time units", max(tail_errors) <= TOL, max(tail_errors))
    check("fixed-policy d=0 preserves u=b in exported source states", d0_off_diagonal <= 1e-12, d0_off_diagonal)
    check("oracle output is exactly duplicated across inert d views", oracle_d_error <= TOL, oracle_d_error)
    check("all candidate architectures use the common retained resident", common_resident_ok)

    # Load/access are only fully equivalent for d=0: sparse access reduces
    # private/adult observation, while load also reduces social encounters.
    load_equivalence = {}
    for model in ("retained", "frozen", "audit", "reset"):
        with np.load(ROOT / f"{model}_sparse.npz") as sparse, np.load(
            ROOT / f"{model}_load.npz"
        ) as load:
            shaped_s = sparse["final_state"].reshape(len(ds), len(taus), 2, 9, 9)
            shaped_l = load["final_state"].reshape(len(ds), len(taus), 2, 9, 9)
            d0 = max_error(shaped_s[0], shaped_l[0])
            d1_n = max_error(
                sparse["N"].reshape(len(ds), len(taus), len(times))[-1],
                load["N"].reshape(len(ds), len(taus), len(times))[-1],
            )
            load_equivalence[model] = {"d0_state_error": d0, "d1_N_difference": d1_n}
    check(
        "access/load equivalence holds only on the no-social d=0 slice",
        max(x["d0_state_error"] for x in load_equivalence.values()) <= TOL,
        load_equivalence,
        "At d>0, load changes social exposure too; the nonzero contrasts are expected and must not be called source-only effects.",
    )
    diagnostics["access_load"] = load_equivalence

    # Supplementary products used fewer stored time points in the run that
    # generated them, so an obsolete window-dependent field must not leak out.
    supplementary_csv = ["mechanisms.csv", "source_conditions.csv", "histories.csv", "sensitivity.csv"]
    leaked = {}
    for name in supplementary_csv:
        header = next(csv.reader((ROOT / name).open()))
        leaked[name] = "tail_growth" in header
    supplementary_json = ["mechanisms.json", "sensitivity.json"]
    for name in supplementary_json:
        value = read_json(name)
        rows = value["rows"] if isinstance(value, dict) and "rows" in value else value
        leaked[name] = any("tail_growth" in row for row in rows)
    source_json = read_json("source_conditions.json")
    leaked["source_conditions.json"] = any(
        "tail_growth" in row for row in source_json.get("contrasts", [])
    )
    check("obsolete supplemental tail-growth field is omitted", not any(leaked.values()), leaked)

    mechanism_rows = read_csv("mechanisms.csv")
    mechanism_json = read_json("mechanisms.json")["rows"]
    check("mechanism factorial cardinality", len(mechanism_rows) == 315 and len(mechanism_json) == 315)
    mechanism_parity = []
    for a, b in zip(mechanism_rows, mechanism_json):
        for key, value in b.items():
            mechanism_parity.append(max_error([number(a[key])], [number(value)]) if key not in {"scenario", "variant"} else 0.0 if a[key] == value else float("inf"))
    check("mechanism CSV and JSON agree", max(mechanism_parity) <= TOL, max(mechanism_parity))
    mech = {(r["scenario"], r["variant"], number(r["d"]), number(r["tau"])): r for r in mechanism_rows}
    mechanism_contrasts = {}
    for scenario in sorted({r["scenario"] for r in mechanism_rows}):
        n = mech[(scenario, "neither", 1.0, 3.0)]
        a = mech[(scenario, "action_only", 1.0, 3.0)]
        s = mech[(scenario, "storage_only", 1.0, 3.0)]
        b = mech[(scenario, "both", 1.0, 3.0)]
        mechanism_contrasts[scenario] = {
            "action_rT": number(a["rT"]) - number(n["rT"]),
            "storage_rT": number(s["rT"]) - number(n["rT"]),
            "interaction_rT": number(b["rT"]) - number(a["rT"]) - number(s["rT"]) + number(n["rT"]),
            "action_public_accuracy": number(a["public_F"]) - number(n["public_F"]),
        }
    check(
        "2x2 mechanisms are reported as measured contrasts, not assumed benefits",
        any(x["action_rT"] < 0 < x["action_public_accuracy"] for x in mechanism_contrasts.values()),
        mechanism_contrasts,
        "The isolated action effect is negative in at least one environment despite higher current public accuracy.",
    )
    diagnostics["mechanism_contrasts_d1_tau3"] = mechanism_contrasts

    source_rows = read_csv("source_conditions.csv")
    check("source-condition factorial cardinality", len(source_rows) == 972 and len(source_json["contrasts"]) == 486)
    def source_key(row):
        # JSON is intentionally canonicalized to nine decimal places while
        # CSV retains full binary float text.
        return (
            round(number(row["p"]), 9),
            round(number(row["access"]), 9),
            round(number(row["cost"]), 9),
            row["mode"],
        )

    source_pairs = defaultdict(dict)
    for row in source_rows:
        key = source_key(row)
        source_pairs[key][number(row["d"])] = row
    source_recomputed = {}
    for key, pair in source_pairs.items():
        source_recomputed[key] = {
            "delta_rT": number(pair[1.0]["rT"]) - number(pair[0.0]["rT"]),
            "delta_N": number(pair[1.0]["N"]) - number(pair[0.0]["N"]),
            "delta_accuracy": number(pair[1.0]["belief_A"]) - number(pair[0.0]["belief_A"]),
        }
    source_json_map = {source_key(r): r for r in source_json["contrasts"]}
    source_errors = []
    for key, derived in source_recomputed.items():
        source_errors.extend(max_error([value], [source_json_map[key][name]]) for name, value in derived.items())
    signs = {
        "positive_delta_rT": sum(x["delta_rT"] > 0 for x in source_recomputed.values()),
        "negative_delta_rT": sum(x["delta_rT"] < 0 for x in source_recomputed.values()),
    }
    check("source-condition JSON contrasts are recomputed from paired CSV rows", max(source_errors) <= TOL, {"max_error": max(source_errors), **signs})
    diagnostics["source_condition_signs"] = signs

    histories = read_csv("histories.csv")
    history_summary = read_json("histories_summary.json")
    check("history design cardinality", len(histories) == 1296 and len(history_summary["rows"]) == 36)
    history_groups = defaultdict(list)
    for row in histories:
        key = (row["phase"], row["seed"], row["world"], row["model"], number(row["tau"]))
        history_groups[key].append(row)
    deltas = defaultdict(list)
    for (phase, _seed, world, model, tau), rows in history_groups.items():
        by_d = {number(r["d"]): number(r["rT"]) for r in rows}
        deltas[(phase, world, model, tau)].append(by_d[1.0] - by_d[0.0])
    history_errors = []
    for row in history_summary["rows"]:
        values = np.asarray(deltas[(row["phase"], row["world"], row["model"], number(row["tau"]))])
        history_errors.extend(
            [
                max_error([values.mean()], [row["mean"]]),
                max_error([values.std(ddof=1) / np.sqrt(len(values))], [row["se"]]),
                max_error([(values > 0).sum()], [row["positive"]]),
            ]
        )
    check("history summaries recompute from seed-level rows", max(history_errors) <= 1e-8, max(history_errors))

    repertoire_rows = read_csv("repertoire.csv")
    repertoire = read_json("repertoire.json")
    invariant_values = repertoire["invariants"]
    invariant_failures = []
    if isinstance(invariant_values, dict):
        for name, value in invariant_values.items():
            if isinstance(value, dict) and not value.get("passed", value.get("pass", False)):
                invariant_failures.append(name)
    elif isinstance(invariant_values, list):
        invariant_failures = [str(x.get("name", i)) for i, x in enumerate(invariant_values) if not x.get("passed", x.get("pass", False))]
    check(
        "repertoire cardinalities and invariants",
        len(repertoire_rows) == 23328
        and len(repertoire["run_summaries"]) == 972
        and len(repertoire["aggregates"]) == 162
        and not invariant_failures,
        {
            "csv": len(repertoire_rows),
            "runs": len(repertoire["run_summaries"]),
            "aggregates": len(repertoire["aggregates"]),
            "failed_invariants": invariant_failures,
        },
    )

    architecture = read_csv("architecture_invasion.csv")
    arch_diag = [abs(number(r["rate"])) for r in architecture if r["resident"] == r["mutant"]]
    check("architecture invasion spectrum has neutral self diagonal", len(architecture) == 96 and max(arch_diag) <= 1e-7, max(arch_diag))
    pairwise = read_csv("pairwise.csv")
    pair_diag = [abs(number(r["rate"])) for r in pairwise if number(r["resident"]) == number(r["mutant"])]
    residuals = [abs(number(r["residual"])) for r in pairwise]
    resident_self = [abs(number(r["self_rate"])) for r in pairwise]
    check(
        "pairwise invasion spectrum has neutral self diagonal and converged residents",
        len(pairwise) == 648 and max(pair_diag) <= 1e-7 and max(residuals) <= 1e-8 and max(resident_self) <= 1e-7,
        {"diagonal": max(pair_diag), "residual": max(residuals), "resident_self": max(resident_self)},
    )

    competition = read_json("competition.json")
    competition_error = 0.0
    competition_min = float("inf")
    for run in competition:
        freq = np.asarray(run["frequency"], dtype=float)
        competition_error = max(competition_error, float(np.max(np.abs(freq.sum(axis=0) - 1))))
        competition_min = min(competition_min, float(freq.min()), min(run["N"]))
    check(
        "competition frequencies are normalized and nonnegative",
        len(competition) == 10 and competition_error <= 2e-8 and competition_min >= -TOL,
        {"sum_error": competition_error, "minimum": competition_min},
    )

    dynamic = read_csv("dynamic_invasion.csv")
    dynamic_self = [abs(number(r["relative_rate"])) for r in dynamic if number(r["d"]) == 0.5 and number(r["tau"]) == 3.0]
    convergence = read_json("dynamic_convergence.json")
    check(
        "dynamic rare-mutant run has shared-resident self neutrality and dt halving",
        len(dynamic) == 216
        and max(dynamic_self) <= 1e-10
        and abs(number(convergence["self_relative"])) <= 1e-10
        and abs(number(convergence["half_self_relative"])) <= 1e-10
        and number(convergence["max_absolute_difference"]) <= 1e-5,
        {"rows": len(dynamic), "max_self": max(dynamic_self), **convergence},
        "Rates are finite-window, common-resident relative growth, not an ESS proof.",
    )

    selection = read_json("selection.json")
    selection_counts = {
        "architecture_invasion": len(selection["architecture_invasion"]),
        "pairwise": len(selection["pairwise"]),
        "competition": len(selection["competition"]),
        "dynamic_invasion": len(selection["dynamic_invasion"]),
    }
    check(
        "selection bundle includes every evolution artifact",
        selection_counts == {
            "architecture_invasion": 96,
            "pairwise": 648,
            "competition": 10,
            "dynamic_invasion": 216,
        },
        selection_counts,
    )

    failed = [item["name"] for item in checks if not item["passed"]]
    result = {
        "status": "PASS" if not failed else "FAIL",
        "scope": "Read-only cross-artifact and accounting audit; no simulation results regenerated.",
        "run_id": dash["run_id"],
        "checks_passed": len(checks) - len(failed),
        "checks_total": len(checks),
        "failed": failed,
        "checks": checks,
        "diagnostics": diagnostics,
        "limitations": [
            "Parity across exports can reveal serialization or wiring errors but is not independent validation of model equations.",
            "Mechanism and source-condition results are conditional simulation contrasts, not general causal or optimality proofs.",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(f"{result['status']} {result['checks_passed']}/{result['checks_total']}")
    for item in checks:
        print(("PASS" if item["passed"] else "FAIL"), item["name"])
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
