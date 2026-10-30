"""Exact calibrated-Bayes benchmark for bounded unit-step cue updating.

This is an exploratory one-task, stable-world comparator.  It has no
demography, social learning, query costs, or assumed adult wisdom.  The
prior q0 is calibrated knowledge only for this benchmark.
"""

from __future__ import annotations

import itertools
import json
from math import comb
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "bayes_benchmark.json"
H = 4
PRIORS = (0.70, 0.85, 0.95)
CUE_ACCURACIES = (0.55, 0.65, 0.85)
N_MAX = 40


def bayes_accuracy(q0: float, p: float, n: int) -> float:
    """Expected accuracy of the calibrated posterior decision."""
    total = 0.0
    for k in range(n + 1):
        like_plus = comb(n, k) * p**k * (1 - p) ** (n - k)
        like_minus = comb(n, k) * (1 - p) ** k * p ** (n - k)
        total += max(q0 * like_plus, (1 - q0) * like_minus)
    return total


def transition(p_plus: float) -> np.ndarray:
    """Markov transition with saturated (reflecting/self-loop) boundaries."""
    size = 2 * H + 1
    matrix = np.zeros((size, size))
    for index, score in enumerate(range(-H, H + 1)):
        up = min(H, score + 1) + H
        down = max(-H, score - 1) + H
        matrix[index, up] += p_plus
        matrix[index, down] += 1 - p_plus
    return matrix


def correct_probability(distribution: np.ndarray, theta: int) -> float:
    scores = np.arange(-H, H + 1)
    correct = scores * theta > 0
    return float(distribution[correct].sum() + 0.5 * distribution[scores == 0].sum())


def bounded_curve(q0: float, p: float, n_max: int = N_MAX):
    plus = np.zeros(2 * H + 1)
    minus = np.zeros(2 * H + 1)
    plus[-1] = 1.0
    minus[-1] = 1.0
    t_plus = transition(p)
    t_minus = transition(1 - p)
    rows = []
    for n in range(n_max + 1):
        accuracy = q0 * correct_probability(plus, 1) + (1 - q0) * correct_probability(minus, -1)
        rows.append((accuracy, plus.copy(), minus.copy()))
        plus = plus @ t_plus
        minus = minus @ t_minus
    return rows


def enumerate_distribution(p_plus: float, n: int) -> np.ndarray:
    """Independent explicit path enumeration, used only for small n tests."""
    result = np.zeros(2 * H + 1)
    for path in itertools.product((-1, 1), repeat=n):
        score = H
        probability = 1.0
        for cue in path:
            probability *= p_plus if cue == 1 else 1 - p_plus
            score = min(H, max(-H, score + cue))
        result[score + H] += probability
    return result


def main() -> None:
    checks = []

    def check(name: str, passed: bool, measured=None) -> None:
        checks.append({"name": name, "passed": bool(passed), "measured": measured})

    rows = []
    erosion_cases = []
    normalization_error = 0.0
    n0_error = 0.0
    bayes_monotonic_drop = 0.0
    bayes_prior_shortfall = 0.0
    enumeration_error = 0.0

    for p in CUE_ACCURACIES:
        curve_by_prior = {q0: bounded_curve(q0, p) for q0 in PRIORS}
        for p_plus, label in ((p, "theta_plus"), (1 - p, "theta_minus")):
            enumerated = enumerate_distribution(p_plus, 10)
            markov = curve_by_prior[PRIORS[0]][10][1 if label == "theta_plus" else 2]
            enumeration_error = max(enumeration_error, float(np.max(np.abs(enumerated - markov))))
        for q0 in PRIORS:
            curve = curve_by_prior[q0]
            bayes_values = []
            bounded_values = []
            for n, (bounded, plus, minus) in enumerate(curve):
                bayes = bayes_accuracy(q0, p, n)
                bayes_values.append(bayes)
                bounded_values.append(bounded)
                normalization_error = max(
                    normalization_error,
                    abs(float(plus.sum()) - 1.0),
                    abs(float(minus.sum()) - 1.0),
                    max(0.0, -float(plus.min())),
                    max(0.0, -float(minus.min())),
                )
                rows.append(
                    {
                        "q0": q0,
                        "p": p,
                        "n": n,
                        "bayes_accuracy": bayes,
                        "bounded_accuracy": bounded,
                        "bayes_value_over_prior": bayes - q0,
                        "bounded_change_from_prior": bounded - q0,
                        "bounded_regret_vs_bayes": bayes - bounded,
                    }
                )
            n0_error = max(n0_error, abs(bayes_values[0] - q0), abs(bounded_values[0] - q0))
            bayes_monotonic_drop = max(
                bayes_monotonic_drop,
                max([0.0] + [a - b for a, b in zip(bayes_values, bayes_values[1:])]),
            )
            bayes_prior_shortfall = max(bayes_prior_shortfall, max(q0 - x for x in bayes_values))
            minimum_n = int(np.argmin(bounded_values))
            minimum = float(bounded_values[minimum_n])
            if minimum < q0 - 1e-12:
                erosion_cases.append(
                    {
                        "q0": q0,
                        "p": p,
                        "minimum_n": minimum_n,
                        "minimum_bounded_accuracy": minimum,
                        "erosion_below_prior": q0 - minimum,
                        "bayes_accuracy_at_same_n": bayes_values[minimum_n],
                    }
                )

    check("all Markov distributions normalize and remain nonnegative", normalization_error <= 2e-14, normalization_error)
    check("n=0 equals calibrated prior accuracy", n0_error <= 2e-14, n0_error)
    check("Bayes expected accuracy is nondecreasing in n", bayes_monotonic_drop <= 2e-14, bayes_monotonic_drop)
    check("Bayes expected accuracy never falls below the prior", bayes_prior_shortfall <= 2e-14, bayes_prior_shortfall)
    check("Markov transitions match independent path enumeration at n=10", enumeration_error <= 2e-14, enumeration_error)
    check("bounded unit-step updating has at least one prior-erosion case", bool(erosion_cases), len(erosion_cases))

    worst = max(erosion_cases, key=lambda row: row["erosion_below_prior"])
    result = {
        "status": "PASS" if all(item["passed"] for item in checks) else "FAIL",
        "label": "exploratory analytical comparator",
        "scope": {
            "task": "one binary state, stable world, conditionally independent cues",
            "prior": "q0 is calibrated initial knowledge for this benchmark only",
            "bayes": "posterior decision maximizing expected correctness after n cues",
            "bounded": "initial score +4; each signed cue moves one unit; saturated boundary self-loops; score-zero ties randomize",
            "excluded": ["demography", "social transmission", "query cost", "human optimality claim"],
        },
        "parameters": {"H": H, "q0": list(PRIORS), "p": list(CUE_ACCURACIES), "n": [0, N_MAX]},
        "checks": checks,
        "summary": {
            "erosion_case_count": len(erosion_cases),
            "worst_erosion_case": worst,
            "claim_limit": "Freezing can beat misweighted finite-memory updating, but cannot beat optimal cost-free calibrated Bayes in expected accuracy under these benchmark assumptions.",
        },
        "erosion_cases": erosion_cases,
        "rows": rows,
        "limitations": [
            "Conditional cue independence and a stable binary world are benchmark assumptions, not claims about all environments.",
            "The comparator diagnoses the bounded update rule; it does not establish that people or organisms implement Bayes.",
            "The V5 demographic simulations contain feedbacks absent from this one-task accuracy calculation.",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(f"{result['status']} {sum(x['passed'] for x in checks)}/{len(checks)}")
    print(json.dumps(result["summary"], indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
