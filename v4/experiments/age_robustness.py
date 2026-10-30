"""Erlang juvenile-stage robustness for the V4 fixed-deference model.

The core model uses one juvenile compartment, so maturation is memoryless with
hazard 1/tau.  This script replaces that compartment with L serial juvenile
subcompartments.  Each progression has hazard L/tau, giving an Erlang waiting
time with the same mean tau and variance tau**2/L.  Cultural score z is retained
through every juvenile progression and on entry to the adult compartment.

Only the age-hazard representation changes.  Cognitive transitions, testimony,
vital rates, births, density regulation, and adult correction reuse model.py's
definitions.  L=1 is checked numerically against model.run before outputs are
accepted.
"""
from __future__ import annotations

import csv
import json
import platform
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

import model as core


ROOT = Path(__file__).resolve().parent
D_VALUES = np.asarray([0.0, 0.5, 1.0])
TAU_VALUES = np.asarray([1.0, 3.0, 8.0])
ERLANG_SHAPES = (1, 4)
SCENARIOS = ("stable", "shock")
OUTPUT_POINTS = 401
MATCH_TOLERANCE = 1e-9


def theta_fn(scenario: str):
    if scenario == "stable":
        return lambda _t: 1
    if scenario == "shock":
        return lambda t: 1 if t < 150.0 else -1
    raise ValueError(f"unknown scenario: {scenario}")


def initial_erlang(c: core.Config, n: int, L: int) -> np.ndarray:
    """Match core.initial, placing all initial juveniles in Erlang phase one."""
    if L < 1:
        raise ValueError("L must be positive")
    base = core.initial(c, n)
    Z, R = core.shape(c)
    x = np.zeros((n, L + 1, Z, R))
    x[:, 0] = base[:, 0]
    x[:, L] = base[:, 1]
    return x


def aggregate_stages(x: np.ndarray, L: int) -> np.ndarray:
    """Return the core two-stage view: all juvenile phases summed as F, then A."""
    return np.stack((x[:, :L].sum(axis=1), x[:, L]), axis=1)


def rhs_erlang(
    c: core.Config,
    x: np.ndarray,
    d: np.ndarray,
    tau: np.ndarray,
    L: int,
    theta: int,
) -> np.ndarray:
    """Kolmogorov-demographic RHS with L serial juvenile subcompartments."""
    if c.policy != "fixed":
        raise ValueError("age robustness is defined for the fixed policy")
    two_stage = aggregate_stages(x, L)
    q, resource = core.environment(c, two_stage, theta)
    w = core.choice(c, d, q)
    action_accuracy = c.p + w[:, 0] * (q - c.p)
    adult_correct = core.correct(c, theta)[None, :, None]

    juvenile_mortality = c.mu_F + (
        c.error_death * (1.0 - action_accuracy) if c.payoff else 0.0
    )
    adult_mortality = c.mu_A + (
        c.adult_error_death * (1.0 - adult_correct) if c.payoff else 0.0
    )
    progression = L / tau

    out = np.zeros_like(x)
    juveniles = x[:, :L]
    adults = x[:, L]

    # Death and serial age progression.  Each flux retains the same cultural z.
    for phase in range(L):
        out[:, phase] -= (
            progression[:, None, None] + juvenile_mortality[:, None, None]
        ) * juveniles[:, phase]
        if phase + 1 < L:
            out[:, phase + 1] += progression[:, None, None] * juveniles[:, phase]
        else:
            out[:, L] += progression[:, None, None] * juveniles[:, phase]

    out[:, L] -= adult_mortality * adults

    births = (
        adults
        * (
            c.beta_base
            + (c.beta_skill * adult_correct if c.payoff else 0.0)
        )
        * resource[:, None, None]
    ).sum((1, 2))
    out[:, 0, c.H, core.shape(c)[1] // 2] += births

    # The fixed-policy juvenile score kernel is identical in every age phase.
    stored_accuracy = action_accuracy if c.internalize else np.full(len(x), c.p)
    up = np.where(theta == 1, stored_accuracy, 1.0 - stored_accuracy)
    for phase in range(L):
        F_phase = juveniles[:, phase]
        out[:, phase] += c.juvenile_rate * (
            up[:, None, None] * core.shift(F_phase, 1)
            + (1.0 - up)[:, None, None] * core.shift(F_phase, -1)
            - F_phase
        )

    adult_up = c.p if theta == 1 else 1.0 - c.p
    out[:, L] += c.adult_rate * (
        adult_up * core.shift(adults, 1)
        + (1.0 - adult_up) * core.shift(adults, -1)
        - adults
    )
    return out


def rk4_step(
    c: core.Config,
    x: np.ndarray,
    d: np.ndarray,
    tau: np.ndarray,
    L: int,
    t: float,
    environment,
    h: float,
) -> np.ndarray:
    theta = environment(t + h / 2.0)
    f = lambda y: rhs_erlang(c, y, d, tau, L, theta)
    k1 = f(x)
    k2 = f(x + h * k1 / 2.0)
    k3 = f(x + h * k2 / 2.0)
    k4 = f(x + h * k3)
    y = x + h * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
    if not np.all(np.isfinite(y)) or np.min(y) < -1e-9:
        raise FloatingPointError("invalid Erlang-stage population; reduce dt")
    return y


def run_erlang(
    c: core.Config,
    d,
    tau,
    L: int,
    environment,
    points: int = OUTPUT_POINTS,
) -> dict[str, np.ndarray]:
    d, tau = np.broadcast_arrays(
        np.atleast_1d(d).astype(float), np.atleast_1d(tau).astype(float)
    )
    core.validate(c, d, tau)
    x = initial_erlang(c, len(d), L)
    times = np.linspace(0.0, c.T, points)
    metric_history = []
    state_history = []
    t = 0.0
    for target in times:
        while t < target - 1e-10:
            h = min(c.dt, target - t)
            x = rk4_step(c, x, d, tau, L, t, environment, h)
            t += h
        two_stage = aggregate_stages(x, L)
        metric_history.append(
            core.metrics(c, two_stage, d, tau, environment(target))
        )
        state_history.append(x.copy())
    result = {
        key: np.stack([entry[key] for entry in metric_history], axis=1)
        for key in metric_history[0]
    }
    result["t"] = times
    result["states"] = np.stack(state_history, axis=1)
    return result


def wrong_high_confidence(
    c: core.Config, states: np.ndarray, L: int, theta: int
) -> np.ndarray:
    adults = states[:, -1, L]
    z = np.arange(-c.H, c.H + 1)
    mask = ((theta * z) < 0) & (np.abs(z) > 3)
    total = adults.sum((1, 2))
    wrong = adults[:, mask, :].sum((1, 2))
    return np.divide(wrong, total, out=np.zeros_like(wrong), where=total > 0)


def summarize_run(
    c: core.Config,
    result: dict[str, np.ndarray],
    L: int,
    scenario: str,
) -> list[dict[str, float | int | str | None]]:
    times = result["t"]
    final_theta = theta_fn(scenario)(times[-1])
    wrong_final = wrong_high_confidence(c, result["states"], L, final_theta)
    N = result["N"]
    rT = np.log(N[:, -1] / N[:, 0]) / c.T

    recovery = np.full(len(rT), np.nan)
    accuracy_debt = np.full(len(rT), np.nan)
    wrong_peak = np.full(len(rT), np.nan)
    if scenario == "shock":
        start = int(np.searchsorted(times, 150.0))
        post_t = times[start:]
        post_belief = result["belief_A"][:, start:]
        accuracy_debt = np.trapezoid(
            np.maximum(0.0, 0.75 - post_belief), post_t, axis=1
        )
        wrong_series = np.stack(
            [
                wrong_high_confidence(c, result["states"][:, j : j + 1], L, -1)
                for j in range(start, len(times))
            ],
            axis=1,
        )
        wrong_peak = wrong_series.max(axis=1)
        for i in range(len(rT)):
            for j in range(post_belief.shape[1] - 4):
                if np.all(post_belief[i, j : j + 5] >= 0.75):
                    recovery[i] = post_t[j] - 150.0
                    break

    rows = []
    for i in range(len(rT)):
        rows.append(
            {
                "scenario": scenario,
                "L": L,
                "d": float(D_VALUES.repeat(len(TAU_VALUES))[i]),
                "tau": float(np.tile(TAU_VALUES, len(D_VALUES))[i]),
                "maturation_cv": float(1.0 / np.sqrt(L)),
                "rT": float(rT[i]),
                "N_T": float(N[i, -1]),
                "adult_belief_T": float(result["belief_A"][i, -1]),
                "persistence_T": float(result["dogmatism"][i, -1]),
                "mean_abs_z_T": float(result["confidence"][i, -1]),
                "wrong_high_confidence_T": float(wrong_final[i]),
                "recovery_time": (
                    None if not np.isfinite(recovery[i]) else float(recovery[i])
                ),
                "postshock_accuracy_debt": (
                    None
                    if not np.isfinite(accuracy_debt[i])
                    else float(accuracy_debt[i])
                ),
                "postshock_wrong_high_confidence_peak": (
                    None if not np.isfinite(wrong_peak[i]) else float(wrong_peak[i])
                ),
            }
        )
    return rows


def l1_equivalence_check(
    c: core.Config,
    d: np.ndarray,
    tau: np.ndarray,
    scenario: str,
    erlang_result: dict[str, np.ndarray],
) -> dict[str, float | bool | str]:
    environment = theta_fn(scenario)
    direct = core.run(c, d, tau, environment, points=OUTPUT_POINTS)
    metric_keys = ("N", "belief_A", "public_F", "dogmatism", "confidence")
    metric_errors = {
        key: float(np.max(np.abs(erlang_result[key] - direct[key])))
        for key in metric_keys
    }
    state_error = float(np.max(np.abs(erlang_result["states"] - direct["states"])))
    max_error = max(state_error, *metric_errors.values())
    return {
        "scenario": scenario,
        "max_state_abs_error": state_error,
        **{f"max_{key}_abs_error": value for key, value in metric_errors.items()},
        "max_abs_error": max_error,
        "tolerance": MATCH_TOLERANCE,
        "passed": bool(max_error <= MATCH_TOLERANCE),
    }


def with_l1_deltas(rows: list[dict]) -> list[dict]:
    baseline = {
        (row["scenario"], row["d"], row["tau"]): row
        for row in rows
        if row["L"] == 1
    }
    fields = (
        "rT",
        "adult_belief_T",
        "persistence_T",
        "mean_abs_z_T",
        "wrong_high_confidence_T",
    )
    for row in rows:
        ref = baseline[(row["scenario"], row["d"], row["tau"])]
        for field in fields:
            row[f"delta_{field}_vs_L1"] = float(row[field] - ref[field])
    return rows


def plain(value):
    if isinstance(value, dict):
        return {key: plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(item) for item in value]
    if isinstance(value, np.generic):
        return plain(value.item())
    if isinstance(value, float):
        return round(value, 10) if np.isfinite(value) else None
    return value


def aggregate_summary(rows: list[dict]) -> dict:
    summary = {}
    for scenario in SCENARIOS:
        selected = [
            row for row in rows if row["scenario"] == scenario and row["L"] == 4
        ]
        summary[scenario] = {
            "L4_minus_L1_rT_range": [
                min(row["delta_rT_vs_L1"] for row in selected),
                max(row["delta_rT_vs_L1"] for row in selected),
            ],
            "L4_minus_L1_adult_belief_T_range": [
                min(row["delta_adult_belief_T_vs_L1"] for row in selected),
                max(row["delta_adult_belief_T_vs_L1"] for row in selected),
            ],
            "L4_minus_L1_persistence_T_range": [
                min(row["delta_persistence_T_vs_L1"] for row in selected),
                max(row["delta_persistence_T_vs_L1"] for row in selected),
            ],
            "largest_abs_rT_change_cell": max(
                selected, key=lambda row: abs(row["delta_rT_vs_L1"])
            ),
            "largest_abs_adult_belief_change_cell": max(
                selected,
                key=lambda row: abs(row["delta_adult_belief_T_vs_L1"]),
            ),
            "largest_abs_persistence_change_cell": max(
                selected,
                key=lambda row: abs(row["delta_persistence_T_vs_L1"]),
            ),
        }
    return summary


def main() -> None:
    c = replace(core.Config(), H=6, p=0.65, T=400.0, dt=0.05)
    DD, TT = np.meshgrid(D_VALUES, TAU_VALUES, indexing="ij")
    d = DD.ravel()
    tau = TT.ravel()
    rows = []
    checks = []

    for scenario in SCENARIOS:
        environment = theta_fn(scenario)
        for L in ERLANG_SHAPES:
            result = run_erlang(c, d, tau, L, environment)
            rows.extend(summarize_run(c, result, L, scenario))
            if L == 1:
                checks.append(l1_equivalence_check(c, d, tau, scenario, result))

    if not all(check["passed"] for check in checks):
        raise AssertionError(f"L=1 failed core equivalence check: {checks}")

    rows = with_l1_deltas(rows)
    csv_path = ROOT / "age_robustness.csv"
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    payload = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": (
            "Robustness of fixed-deference conclusions to replacing memoryless "
            "juvenile maturation with an Erlang age hazard of equal mean."
        ),
        "interpretation": {
            "L1": "exponential/memoryless maturation with mean tau",
            "L4": (
                "four serial juvenile phases, progression hazard 4/tau, mean tau, "
                "coefficient of variation 1/2"
            ),
            "stage_accounting": "F is the sum of all juvenile phases; A is mature",
            "cultural_retention": (
                "z is unchanged by juvenile phase progression and maturation"
            ),
            "persistence_T": "fraction of adults with absolute score greater than 3",
            "wrong_high_confidence": (
                "fraction of adults with score opposite the current environment "
                "and absolute score greater than 3"
            ),
            "rT": "log(N(T)/N(0))/T",
        },
        "config": asdict(c),
        "grid": {
            "L": list(ERLANG_SHAPES),
            "d": D_VALUES.tolist(),
            "tau": TAU_VALUES.tolist(),
            "scenarios": list(SCENARIOS),
            "shock_flip_time": 150.0,
            "output_points": OUTPUT_POINTS,
        },
        "L1_core_equivalence": checks,
        "summary": aggregate_summary(rows),
        "rows": rows,
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "solver": "deterministic RK4",
            "dt": c.dt,
        },
    }
    (ROOT / "age_robustness.json").write_text(
        json.dumps(plain(payload), indent=2, allow_nan=False) + "\n"
    )
    print(json.dumps(plain(payload["L1_core_equivalence"]), indent=2))
    print(json.dumps(plain(payload["summary"]), indent=2))


if __name__ == "__main__":
    main()
