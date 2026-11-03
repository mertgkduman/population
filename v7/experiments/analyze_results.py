"""Recompute bounded V7 aggregates from raw gzip CSV exports only."""
from __future__ import annotations

import csv
import gzip
import math
from collections import defaultdict
from pathlib import Path


def read_rows(path: Path) -> list[dict]:
    with gzip.open(path, "rt", newline="") as handle:
        return list(csv.DictReader(handle))


def mcse(values: list[float]) -> float | None:
    if len(values) < 2: return None
    average = sum(values) / len(values)
    return (sum((value - average) ** 2 for value in values) / (len(values) * (len(values) - 1))) ** .5


def wilson_half_width(successes: int, total: int) -> float | None:
    if not total: return None
    z, p = 1.959963984540054, successes / total
    return z / (1 + z * z / total) * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total))


def aggregate(rows: list[dict]) -> list[dict]:
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows: groups[(row["regime"], row["policy"])].append(row)
    result = []
    for (regime, policy), group in sorted(groups.items()):
        net = [float(row["net_energy_per_agent_season"]) for row in group]
        populations = [float(row["mean_population"]) for row in group]
        extinct = sum(row["status"] == "extinct" for row in group)
        result.append({"regime": int(regime), "policy": policy, "n": len(group), "net_energy_mean": sum(net) / len(net), "net_energy_mcse": mcse(net), "mean_population": sum(populations) / len(populations), "mean_population_mcse": mcse(populations), "extinctions": extinct, "extinction_wilson_half_width": wilson_half_width(extinct, len(group)), "censored": sum(row["status"] == "cap_censored" for row in group)})
    return result
