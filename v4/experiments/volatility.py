"""Targeted environmental-volatility sensitivity for the fixed-deference model.

Each of 24 telegraph histories is shared by all nine (d, tau) traits.  The
output is deliberately descriptive: r600 is finite-horizon monomorphic
population growth, not rare-mutant invasion fitness, and six histories at four
switching scales cannot establish a general volatility theorem.
"""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from model import Config, run


ROOT = Path(__file__).resolve().parent
MEAN_INTERVALS = (20.0, 50.0, 100.0, 200.0)
SEEDS = tuple(range(4000, 4006))
D_VALUES = (0.0, 0.5, 1.0)
TAU_VALUES = (1.0, 3.0, 8.0)


def telegraph_history(seed: int, mean_interval: float, horizon: float):
    """Return a +1-starting symmetric telegraph path and realized path facts."""
    rng = np.random.default_rng(seed)
    switches = []
    t = 0.0
    while True:
        t += float(rng.exponential(mean_interval))
        if t >= horizon:
            break
        switches.append(t)
    switches = np.asarray(switches, dtype=float)

    def theta(time, switch_times=switches):
        return 1 if np.searchsorted(switch_times, time, side="right") % 2 == 0 else -1

    edges = np.r_[0.0, switches, horizon]
    lengths = np.diff(edges)
    plus_time = float(lengths[::2].sum())
    completed = np.diff(np.r_[0.0, switches])
    facts = {
        "switch_count": int(len(switches)),
        "observed_switch_rate": float(len(switches) / horizon),
        "plus_fraction": plus_time / horizon,
        "mean_completed_interval": (
            float(completed.mean()) if len(completed) else None
        ),
        "longest_observed_sojourn": float(lengths.max()),
    }
    return theta, facts


def sample_summary(values):
    values = np.asarray(values, dtype=float)
    return {
        "mean": float(values.mean()),
        "sd": float(values.std(ddof=1)) if len(values) > 1 else 0.0,
        "se": float(values.std(ddof=1) / np.sqrt(len(values))) if len(values) > 1 else 0.0,
        "min": float(values.min()),
        "max": float(values.max()),
    }


def write_csv(path: Path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    config = replace(Config(), T=600.0, dt=0.1)
    ds, taus = np.meshgrid(D_VALUES, TAU_VALUES, indexing="ij")
    ds = ds.ravel()
    taus = taus.ravel()
    paired_rows = []
    path_rows = []

    for mean_interval in MEAN_INTERVALS:
        for seed in SEEDS:
            theta, path_facts = telegraph_history(seed, mean_interval, config.T)
            result = run(config, ds, taus, theta, points=2)
            r600 = np.log(result["N"][:, -1] / result["N"][:, 0]) / config.T
            if not np.all(np.isfinite(r600)):
                raise FloatingPointError("nonfinite volatility outcome")

            path_rows.append(
                {
                    "mean_interval": mean_interval,
                    "seed": seed,
                    **path_facts,
                }
            )
            for tau in TAU_VALUES:
                by_d = {
                    float(d): int(np.flatnonzero((ds == d) & (taus == tau))[0])
                    for d in D_VALUES
                }
                paired_rows.append(
                    {
                        "mean_interval": mean_interval,
                        "seed": seed,
                        "tau": tau,
                        **path_facts,
                        "r600_d0": float(r600[by_d[0.0]]),
                        "r600_d0p5": float(r600[by_d[0.5]]),
                        "r600_d1": float(r600[by_d[1.0]]),
                        "delta_r600_d1_minus_d0": float(
                            r600[by_d[1.0]] - r600[by_d[0.0]]
                        ),
                        "N600_d0": float(result["N"][by_d[0.0], -1]),
                        "N600_d0p5": float(result["N"][by_d[0.5], -1]),
                        "N600_d1": float(result["N"][by_d[1.0], -1]),
                    }
                )
            print(
                "VOLATILITY",
                f"mean={mean_interval:g}",
                f"seed={seed}",
                f"switches={path_facts['switch_count']}",
                flush=True,
            )

    if len(path_rows) != 24 or len(paired_rows) != 72:
        raise AssertionError("unexpected volatility output dimensions")

    contrasts = []
    for mean_interval in MEAN_INTERVALS:
        for tau in TAU_VALUES:
            subset = [
                row
                for row in paired_rows
                if row["mean_interval"] == mean_interval and row["tau"] == tau
            ]
            delta = [row["delta_r600_d1_minus_d0"] for row in subset]
            contrasts.append(
                {
                    "mean_interval": mean_interval,
                    "tau": tau,
                    "n_histories": len(subset),
                    "delta_r600_d1_minus_d0": sample_summary(delta),
                    "positive_histories": int(np.sum(np.asarray(delta) > 0.0)),
                    "mean_r600_by_d": {
                        "0": float(np.mean([row["r600_d0"] for row in subset])),
                        "0.5": float(np.mean([row["r600_d0p5"] for row in subset])),
                        "1": float(np.mean([row["r600_d1"] for row in subset])),
                    },
                    "paired_values_by_seed": {
                        str(row["seed"]): row["delta_r600_d1_minus_d0"]
                        for row in subset
                    },
                }
            )

    environment_variability = []
    for mean_interval in MEAN_INTERVALS:
        subset = [row for row in path_rows if row["mean_interval"] == mean_interval]
        environment_variability.append(
            {
                "mean_interval": mean_interval,
                "n_histories": len(subset),
                "switch_count": sample_summary([row["switch_count"] for row in subset]),
                "observed_switch_rate": sample_summary(
                    [row["observed_switch_rate"] for row in subset]
                ),
                "plus_fraction": sample_summary([row["plus_fraction"] for row in subset]),
                "paths": subset,
            }
        )

    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "config": asdict(config),
        "design": {
            "model": "fixed",
            "mean_intervals": list(MEAN_INTERVALS),
            "seeds": list(SEEDS),
            "d": list(D_VALUES),
            "tau": list(TAU_VALUES),
            "histories": len(path_rows),
            "batched_traits_per_history": len(ds),
            "shared_path_rule": "All nine traits use the identical theta(t) within each mean-interval/seed history.",
            "rate_coupling_rule": "The same seed is reinitialized at each mean interval, coupling rate conditions through common standardized exponential draws.",
            "telegraph_rule": "Start at +1; alternate sign after independent exponential waiting times.",
        },
        "environment_variability": environment_variability,
        "paired_contrasts": contrasts,
        "interpretation": (
            "delta_r600_d1_minus_d0 is a paired finite-horizon monomorphic growth "
            "contrast on six shared histories. It is not invasion fitness, and four "
            "switching scales with six histories do not establish a general theorem."
        ),
    }
    write_csv(ROOT / "volatility.csv", paired_rows)
    (ROOT / "volatility.json").write_text(
        json.dumps(payload, indent=2, allow_nan=False) + "\n"
    )
    print("VOLATILITY DONE", len(path_rows), "histories", len(paired_rows), "paired rows")


if __name__ == "__main__":
    main()
