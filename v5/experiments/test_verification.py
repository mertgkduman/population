"""Independent structural and numerical checks for the V5 information model.

The reference event enumerator below is intentionally separate from the Numba
kernel.  Results are persisted to verification.json and any failed check makes
the process exit nonzero.
"""
from __future__ import annotations

import json
import math
from dataclasses import replace
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import eigvals, expm

from model import (
    Config,
    MODES,
    environment,
    equilibrium,
    generator,
    initial,
    metrics,
    rhs,
    run,
    survival,
    validate,
)


ROOT = Path(__file__).resolve().parent


def check(name, measured, tolerance, detail=""):
    value = float(measured)
    return {
        "name": name,
        "pass": bool(math.isfinite(value) and value <= tolerance),
        "measured": value,
        "tolerance": float(tolerance),
        "detail": detail,
    }


def scaled_error(observed, expected):
    observed = np.asarray(observed)
    expected = np.asarray(expected)
    return float(
        np.max(np.abs(observed - expected) / np.maximum(1.0, np.abs(expected)))
    )


def query_rate_adult(c, b_index, mode):
    base = c.nu_adult * c.access / c.load
    if mode == MODES["frozen"]:
        return 0.0
    if mode == MODES["audit"]:
        return base * (
            1.0 if abs(b_index - c.H) < c.audit_threshold else c.audit_floor
        )
    return base


def reference_rhs(c, x, d, tau, theta, cue_plus, env, modes, mutation=0.0):
    """Pure-Python event enumeration for the fixed-policy source kernel."""
    if c.policy != "fixed":
        raise ValueError("reference enumerator covers the fixed policy")
    x = np.asarray(x, dtype=float)
    d = np.broadcast_to(np.asarray(d, dtype=float), (len(x),))
    tau = np.broadcast_to(np.asarray(tau, dtype=float), (len(x),))
    env = np.broadcast_to(np.asarray(env, dtype=float), (len(x), 3))
    modes = np.broadcast_to(np.asarray(modes, dtype=int), (len(x),))
    n, _, Z, _ = x.shape
    H = c.H
    private_rate = c.nu_private * c.access / c.load
    social_rate = c.nu_social / c.load
    out = np.zeros_like(x)
    births = np.zeros(n)

    for i in range(n):
        m = 1.0 / tau[i]
        teacher_plus, resource, adult_present = env[i]
        w = d[i] * adult_present
        for u in range(Z):
            private_plus = 1.0 if u > H else (0.0 if u < H else 0.5)
            action_weight = w if c.override else 0.0
            public_plus = (
                (1.0 - action_weight) * private_plus
                + action_weight * teacher_plus
            )
            public_correct = public_plus if theta == 1 else 1.0 - public_plus
            juvenile_mortality = (
                c.mu_F
                + (c.error_F * (1.0 - public_correct) if c.payoff else 0.0)
                + c.query_cost * private_rate
            )
            for b in range(Z):
                F = x[i, 0, u, b]
                A = x[i, 1, u, b]
                held_correct = (
                    (1.0 if b > H else (0.0 if b < H else 0.5))
                    if theta == 1
                    else (0.0 if b > H else (1.0 if b < H else 0.5))
                )
                adult_query = query_rate_adult(c, b, int(modes[i]))
                adult_mortality = (
                    c.mu_A
                    + (c.error_A * (1.0 - held_correct) if c.payoff else 0.0)
                    + c.query_cost * adult_query
                )
                out[i, 0, u, b] -= (m + juvenile_mortality) * F
                out[i, 1, u, b] -= adult_mortality * A
                if c.reset:
                    out[i, 1, H, H] += m * F
                else:
                    out[i, 1, u, b] += m * F
                births[i] += (
                    resource
                    * (c.beta_base + (c.beta_skill * held_correct if c.payoff else 0.0))
                    * A
                )

                for sign, probability in ((-1, 1.0 - cue_plus), (1, cue_plus)):
                    un = min(Z - 1, max(0, u + sign))
                    bn = min(Z - 1, max(0, b + sign))
                    flux_f = private_rate * probability * F
                    flux_a = adult_query * probability * A
                    out[i, 0, u, b] -= flux_f
                    out[i, 0, un, bn] += flux_f
                    out[i, 1, u, b] -= flux_a
                    out[i, 1, un, bn] += flux_a

                    social_weight = w if c.accept else 0.0
                    if c.conflict_only:
                        social_weight *= (
                            1.0 - private_plus if sign == 1 else private_plus
                        )
                    social_probability = (
                        teacher_plus if sign == 1 else 1.0 - teacher_plus
                    )
                    social_flux = (
                        social_rate * social_weight * social_probability * F
                    )
                    out[i, 0, u, b] -= social_flux
                    out[i, 0, u, bn] += social_flux

    total_births = float(births.sum())
    for i in range(n):
        out[i, 0, c.H, c.H] += (
            (1.0 - mutation) * births[i] + mutation * total_births / n
        )
    return out


def dop853_reference(c, d, tau, times, modes=None, segments=None):
    y0 = initial(c, 1).ravel()
    target_shape = initial(c, 1).shape
    if segments is not None and len(segments) != 1:
        raise ValueError("reference helper expects one continuous segment")
    theta = 1 if segments is None else segments[0][1]
    cue_plus = c.p if segments is None else segments[0][2]

    def fun(_t, y):
        return rhs(
            c,
            y.reshape(target_shape),
            [d],
            [tau],
            theta=theta,
            cue_plus=cue_plus,
            modes=modes,
        ).ravel()

    sol = solve_ivp(
        fun,
        (float(times[0]), float(times[-1])),
        y0,
        method="DOP853",
        rtol=1e-11,
        atol=1e-13,
        t_eval=times,
    )
    if not sol.success:
        raise RuntimeError(sol.message)
    return sol.y.T


def off_diagonal_mass(states, H):
    mask = ~np.eye(2 * H + 1, dtype=bool)
    return float(np.max(states[..., mask]))


def main():
    checks = []
    diagnostics = {}
    rng = np.random.default_rng(20261030)

    # Basic shape and input validation.
    c = Config(H=2)
    x0 = initial(c, 3)
    shape_error = max(
        abs(x0.shape[0] - 3),
        abs(x0.shape[1] - 2),
        abs(x0.shape[2] - 5),
        abs(x0.shape[3] - 5),
        max(0.0, -float(x0.min())),
    )
    checks.append(check("state_shape_and_nonnegative_initial_density", shape_error, 0.0))

    # The shallow H=1 sensitivity must remain runnable even though the default
    # audit threshold exceeds its reachable confidence depth.  In that case
    # the audit architecture correctly reduces to full adult updating.
    h1_cfg = Config(H=1, adult_mode="audit", T=2.0, dt=0.1)
    h1_run = run(h1_cfg, [0.5], [3.0], points=3)
    h1_full_query = h1_cfg.nu_adult * h1_cfg.access / h1_cfg.load
    h1_error = max(
        max(0.0, -float(h1_run["final_state"].min())),
        float(np.max(np.abs(h1_run["query_A"] - h1_full_query))),
    )
    checks.append(
        check(
            "H1_default_audit_threshold_runnable",
            h1_error,
            2e-14,
            "With |b|<=1 and threshold=2, every adult state uses the full query rate.",
        )
    )

    invalid_missed = 0
    invalid = [
        (replace(c, H=0), [0.5], [3.0]),
        (replace(c, p=np.nan), [0.5], [3.0]),
        (replace(c, load=0.0), [0.5], [3.0]),
        (replace(c, policy="unknown"), [0.5], [3.0]),
        (c, [np.nan], [3.0]),
        (c, [0.5], [0.0]),
        (c, [-0.1], [3.0]),
    ]
    for config, d, tau in invalid:
        try:
            validate(config, np.asarray(d), np.asarray(tau))
        except ValueError:
            continue
        invalid_missed += 1
    checks.append(check("invalid_parameters_rejected", invalid_missed, 0.0))

    # Independent full-event enumeration for primary, audit/conflict-only,
    # and frozen/reset/flagged configurations.
    enumeration_error = 0.0
    enumeration_cases = [
        (Config(H=2), MODES["update"], 0.61, 0.67),
        (
            Config(H=2, adult_mode="audit", conflict_only=True, override=False),
            MODES["audit"],
            0.74,
            0.39,
        ),
        (
            Config(H=2, adult_mode="frozen", accept=False, reset=True),
            MODES["frozen"],
            0.43,
            0.82,
        ),
    ]
    for config, mode, d, cue_plus in enumeration_cases:
        state = rng.uniform(0.05, 2.0, size=initial(config, 1).shape)
        env = np.array([0.71, 0.23, 1.0])
        observed = rhs(
            config,
            state,
            [d],
            [3.4],
            theta=-1,
            cue_plus=cue_plus,
            env=env,
            modes=[mode],
            mutation=0.17,
        )
        expected = reference_rhs(
            config,
            state,
            [d],
            [3.4],
            -1,
            cue_plus,
            env,
            [mode],
            mutation=0.17,
        )
        enumeration_error = max(enumeration_error, float(np.max(np.abs(observed - expected))))
    checks.append(check("independent_event_enumeration", enumeration_error, 3e-14))

    # Explicit reflecting-edge checks for private and social events.
    edge_cfg = Config(
        H=2,
        payoff=False,
        query_cost=0.0,
        mu_F=0.0,
        mu_A=0.0,
        beta_base=0.0,
        beta_skill=0.0,
        nu_social=0.0,
        nu_adult=0.0,
    )
    edge_state = np.zeros_like(initial(edge_cfg, 1))
    edge_state[0, 0, -1, -1] = 1.0
    edge = rhs(
        edge_cfg,
        edge_state,
        [0.0],
        [1e12],
        cue_plus=0.7,
        env=[0.8, 0.0, 1.0],
    )
    edge_error = max(
        abs(edge[0, 0, -2, -2] - 0.3),
        abs(edge[0, 0, -1, -1] + 0.3 + 1e-12),
        abs(edge[0, 1, -1, -1] - 1e-12),
        abs(edge.sum()),
    )
    social_cfg = replace(edge_cfg, nu_private=0.0, nu_social=1.0)
    social_state = np.zeros_like(initial(social_cfg, 1))
    social_state[0, 0, social_cfg.H, -1] = 1.0
    social = rhs(
        social_cfg,
        social_state,
        [1.0],
        [1e12],
        env=[0.8, 0.0, 1.0],
    )
    edge_error = max(
        edge_error,
        abs(social[0, 0, social_cfg.H, -2] - 0.2),
        abs(social[0, 0, social_cfg.H, -1] + 0.2 + 1e-12),
        abs(social.sum()),
    )
    checks.append(check("reflecting_private_and_social_edges", edge_error, 3e-12))

    # Births must enter only neutral juvenile cognition.
    birth_cfg = Config(
        H=2,
        payoff=False,
        query_cost=0.0,
        nu_private=0.0,
        nu_social=0.0,
        nu_adult=0.0,
        mu_F=0.0,
        mu_A=0.0,
    )
    birth_state = np.zeros_like(initial(birth_cfg, 1))
    birth_state[0, 1, 0, -1] = 10.0
    birth_derivative = rhs(
        birth_cfg,
        birth_state,
        [0.5],
        [1e12],
        env=[0.6, 0.25, 1.0],
    )
    juvenile = birth_derivative[0, 0].copy()
    neutral_birth = juvenile[birth_cfg.H, birth_cfg.H]
    juvenile[birth_cfg.H, birth_cfg.H] = 0.0
    birth_error = float(np.max(np.abs(juvenile))) + abs(neutral_birth - 0.25 * birth_cfg.beta_base * 10.0)
    checks.append(check("births_enter_neutral_private_and_held_scores", birth_error, 2e-12))

    # d=0 must preserve the full u=b support, not only equal means.
    invariant_cfg = Config(H=2, T=30.0, dt=0.1)
    invariant = run(
        invariant_cfg,
        [0.0, 0.0, 0.0],
        [3.0, 3.0, 3.0],
        modes=[MODES["update"], MODES["frozen"], MODES["audit"]],
        points=31,
    )
    diagonal_error = off_diagonal_mass(invariant["states"], invariant_cfg.H)
    checks.append(check("d0_private_and_held_scores_identical", diagonal_error, 3e-12))

    # Without any information events or adult source, neutral cognition cannot
    # appear away from (u,b)=(0,0).
    neutral_cfg = Config(
        H=2,
        T=20.0,
        dt=0.1,
        nu_private=0.0,
        nu_social=0.0,
        nu_adult=0.0,
        payoff=False,
        query_cost=0.0,
    )
    neutral_state = np.zeros_like(initial(neutral_cfg, 1))
    neutral_state[0, 0, neutral_cfg.H, neutral_cfg.H] = 80.0
    neutral_state[0, 1, neutral_cfg.H, neutral_cfg.H] = 20.0
    neutral = run(neutral_cfg, [1.0], [3.0], x0=neutral_state, points=11)
    off_neutral = neutral["states"].copy()
    off_neutral[:, :, :, neutral_cfg.H, neutral_cfg.H] = 0.0
    checks.append(check("no_information_no_spontaneous_cognition", np.max(np.abs(off_neutral)), 0.0))

    # Private evidence dynamics are identical across d when social events and
    # cognition-linked vital rates are disabled.
    private_cfg = Config(
        H=2,
        payoff=False,
        query_cost=0.0,
        nu_social=0.0,
        beta_base=0.0,
        mu_F=0.0,
        mu_A=0.0,
    )
    common = rng.uniform(0.1, 2.0, size=initial(private_cfg, 1).shape)
    private_state = np.repeat(common, 3, axis=0)
    private_derivative = rhs(
        private_cfg,
        private_state,
        [0.0, 0.5, 1.0],
        [4.0, 4.0, 4.0],
        env=np.tile([0.9, 0.0, 1.0], (3, 1)),
    )
    private_error = float(np.max(np.abs(private_derivative - private_derivative[:1])))
    checks.append(check("private_information_fixed_across_d", private_error, 2e-14))

    # Parameter labels that preserve all realized query/social rates must not
    # change the generator.
    rate_cfg = Config(H=2, load=1.0, nu_private=0.8, nu_social=1.1, nu_adult=0.4)
    scaled_cfg = replace(
        rate_cfg,
        load=3.0,
        nu_private=2.4,
        nu_social=3.3,
        nu_adult=1.2,
    )
    rate_state = rng.uniform(0.1, 2.0, size=initial(rate_cfg, 1).shape)
    rate_env = [0.68, 0.21, 1.0]
    rate_error = float(
        np.max(
            np.abs(
                rhs(rate_cfg, rate_state, [0.6], [4.0], env=rate_env)
                - rhs(scaled_cfg, rate_state, [0.6], [4.0], env=rate_env)
            )
        )
    )
    checks.append(check("realized_rate_parameterization_invariant", rate_error, 3e-14))

    # Zero correctness payoff plus zero query cost makes d demographically
    # neutral even though held-belief distributions may differ.
    neutral_payoff_cfg = Config(
        H=2, T=30.0, dt=0.1, payoff=False, query_cost=0.0
    )
    neutral_payoff = run(
        neutral_payoff_cfg,
        [0.0, 0.5, 1.0],
        [4.0, 4.0, 4.0],
        points=31,
    )
    demographic_null = max(
        float(np.max(np.ptp(neutral_payoff["F"], axis=0))),
        float(np.max(np.ptp(neutral_payoff["A"], axis=0))),
        float(np.max(np.ptp(neutral_payoff["N"], axis=0))),
    )
    cultural_difference = float(
        np.max(np.abs(neutral_payoff["belief_A"][0] - neutral_payoff["belief_A"][2]))
    )
    checks.append(
        check(
            "zero_payoff_and_cost_d_demographic_null",
            demographic_null,
            2e-9,
            "Cognitive distributions are allowed to differ.",
        )
    )
    diagnostics["zero_payoff_cultural_difference"] = cultural_difference

    # No adults means no social acceptance or override, hence a d null.
    absent_cfg = Config(H=2)
    absent_state = rng.uniform(0.1, 2.0, size=initial(absent_cfg, 1).shape)
    absent_state[:, 1] = 0.0
    absent = np.repeat(absent_state, 2, axis=0)
    absent_env = np.tile([0.9, 0.2, 0.0], (2, 1))
    absent_rhs = rhs(absent_cfg, absent, [0.0, 1.0], [3.0, 3.0], env=absent_env)
    checks.append(check("no_adults_d_null", np.max(np.abs(absent_rhs[0] - absent_rhs[1])), 2e-14))

    # Public action and conflict/override metrics from an independent weighted
    # enumeration, including the private tie state.
    metric_cfg = Config(H=2)
    metric_state = rng.uniform(0.1, 2.0, size=initial(metric_cfg, 1).shape)
    metric_env = np.array([0.73, 0.24, 1.0])
    metric_d = 0.62
    observed_metric = metrics(
        metric_cfg, metric_state, [metric_d], [3.0], env=metric_env
    )
    F = float(metric_state[0, 0].sum())
    public_mass = 0.0
    conflict_mass = 0.0
    for u in range(2 * metric_cfg.H + 1):
        private_plus = 1.0 if u > metric_cfg.H else (0.0 if u < metric_cfg.H else 0.5)
        mass = float(metric_state[0, 0, u].sum())
        public_mass += mass * ((1.0 - metric_d) * private_plus + metric_d * metric_env[0])
        conflict_mass += mass * (
            private_plus * (1.0 - metric_env[0])
            + (1.0 - private_plus) * metric_env[0]
        )
    metric_error = max(
        abs(float(observed_metric["public_F"][0]) - public_mass / F),
        abs(float(observed_metric["conflict"][0]) - conflict_mass / F),
        abs(float(observed_metric["override"][0]) - metric_d),
    )
    checks.append(check("public_action_conflict_override_algebra", metric_error, 3e-15))

    # Acceptance and current override are independently switchable.
    flag_base = Config(H=2, payoff=False, query_cost=0.0)
    flag_state = rng.uniform(0.1, 2.0, size=initial(flag_base, 1).shape)
    flag_env = [0.8, 0.2, 1.0]
    action_only = replace(flag_base, accept=False, override=True)
    neither = replace(flag_base, accept=False, override=False)
    storage_only = replace(flag_base, accept=True, override=False)
    action_rhs = rhs(action_only, flag_state, [0.8], [3.0], env=flag_env)
    neither_rhs = rhs(neither, flag_state, [0.8], [3.0], env=flag_env)
    storage_rhs = rhs(storage_only, flag_state, [0.8], [3.0], env=flag_env)
    action_metric = metrics(action_only, flag_state, [0.8], [3.0], env=flag_env)
    neither_metric = metrics(neither, flag_state, [0.8], [3.0], env=flag_env)
    storage_metric = metrics(storage_only, flag_state, [0.8], [3.0], env=flag_env)
    # With payoff disabled, action choice changes metrics but not state flow;
    # storage changes state flow while override remains private-only.
    flag_error = max(
        float(np.max(np.abs(action_rhs - neither_rhs))),
        abs(float(storage_metric["public_F"][0]) - float(neither_metric["public_F"][0])),
        max(0.0, 1e-5 - abs(float(action_metric["public_F"][0] - neither_metric["public_F"][0]))),
        max(0.0, 1e-5 - float(np.max(np.abs(storage_rhs - neither_rhs)))),
    )
    checks.append(check("acceptance_and_override_separable", flag_error, 3e-14))

    # Full mass accounting: state derivative equals independently enumerated
    # births minus deaths; cognitive and maturation fluxes cancel.
    accounting_cfg = Config(H=2, adult_mode="audit")
    accounting_state = rng.uniform(0.1, 2.0, size=initial(accounting_cfg, 1).shape)
    accounting_env = np.array([0.69, 0.26, 1.0])
    accounting_rhs = rhs(
        accounting_cfg,
        accounting_state,
        [0.7],
        [5.0],
        env=accounting_env,
        modes=[MODES["audit"]],
    )
    accounting_metric = metrics(
        accounting_cfg,
        accounting_state,
        [0.7],
        [5.0],
        env=accounting_env,
        modes=[MODES["audit"]],
    )
    accounting_error = abs(
        float(accounting_rhs.sum())
        - float(accounting_metric["B"][0] - accounting_metric["DF"][0] - accounting_metric["DA"][0])
    )
    checks.append(check("total_flux_accounting", accounting_error, 2e-12))

    # Exact observational equivalence: same absolute signed cue law, different
    # truth labels, and no truth-linked vital rates.
    equivalence_cfg = Config(
        H=2, T=30.0, dt=0.1, payoff=False, query_cost=0.0, adult_mode="audit"
    )
    common_initial = initial(equivalence_cfg, 1)
    misleading = run(
        equivalence_cfg,
        [0.7],
        [4.0],
        segments=[(0.0, 1, 0.35)],
        x0=common_initial,
        modes=[MODES["audit"]],
        points=31,
    )
    reversal = run(
        equivalence_cfg,
        [0.7],
        [4.0],
        segments=[(0.0, -1, 0.35)],
        x0=common_initial,
        modes=[MODES["audit"]],
        points=31,
    )
    equivalence_error = float(np.max(np.abs(misleading["states"] - reversal["states"])))
    checks.append(check("misinformation_reversal_observational_equivalence", equivalence_error, 2e-12))

    payoff_control = replace(equivalence_cfg, payoff=True)
    misleading_payoff = run(
        payoff_control,
        [0.7],
        [4.0],
        segments=[(0.0, 1, 0.35)],
        x0=common_initial,
        modes=[MODES["audit"]],
        points=2,
    )
    reversal_payoff = run(
        payoff_control,
        [0.7],
        [4.0],
        segments=[(0.0, -1, 0.35)],
        x0=common_initial,
        modes=[MODES["audit"]],
        points=2,
    )
    payoff_difference = float(
        np.max(np.abs(misleading_payoff["final_state"] - reversal_payoff["final_state"]))
    )
    checks.append(
        check(
            "truth_linked_payoff_positive_control",
            max(0.0, 1e-3 - payoff_difference),
            0.0,
            f"state difference={payoff_difference}",
        )
    )
    diagnostics["truth_linked_payoff_state_difference"] = payoff_difference

    # Frozen-environment generators must be Metzler and agree with expm.
    metzler_violation = 0.0
    expm_error = 0.0
    fixed_env = np.array([0.72, 0.25, 1.0])
    for mode in ("update", "frozen", "audit"):
        operator_cfg = Config(H=2, adult_mode=mode, T=2.0, dt=0.01)
        G = generator(operator_cfg, 0.6, 4.0, fixed_env)
        off = G.copy()
        np.fill_diagonal(off, 0.0)
        metzler_violation = max(metzler_violation, max(0.0, -float(off.min())))
        expected = expm(G * operator_cfg.T) @ initial(operator_cfg, 1).ravel()
        observed = run(
            operator_cfg,
            [0.6],
            [4.0],
            fixed_env=fixed_env,
            points=2,
        )["final_state"].ravel()
        expm_error = max(expm_error, scaled_error(observed, expected))
    checks.append(check("frozen_generators_metzler", metzler_violation, 2e-14))
    checks.append(check("matrix_exponential_fixed_environment_parity", expm_error, 2e-9))

    # Nonlinear RK4 trajectories against DOP853 and explicit step halving.
    rk_errors = {}
    for mode in ("update", "audit"):
        numerical_cfg = Config(H=2, adult_mode=mode, T=30.0, dt=0.2)
        times = np.linspace(0.0, numerical_cfg.T, 31)
        mode_array = [MODES[mode]]
        reference = dop853_reference(
            numerical_cfg, 0.8, 4.0, times, modes=mode_array
        )
        for dt in (0.2, 0.1, 0.05):
            observed = run(
                replace(numerical_cfg, dt=dt),
                [0.8],
                [4.0],
                modes=mode_array,
                points=len(times),
            )["states"][0].reshape(len(times), -1)
            rk_errors[f"{mode}_dt_{dt}"] = scaled_error(observed, reference)
    error_02 = max(v for k, v in rk_errors.items() if k.endswith("0.2"))
    error_01 = max(v for k, v in rk_errors.items() if k.endswith("0.1"))
    error_005 = max(v for k, v in rk_errors.items() if k.endswith("0.05"))
    checks.append(check("rk4_dt_0p2_vs_DOP853", error_02, 1.2e-3))
    checks.append(check("rk4_dt_0p1_vs_DOP853", error_01, 7e-5))
    checks.append(check("rk4_dt_0p05_vs_DOP853", error_005, 5e-6))
    checks.append(check("rk4_step_halving_reduces_error", max(0.0, error_01 - error_02 / 10.0), 0.0))
    diagnostics["rk4_scaled_errors"] = rk_errors

    # No clipping: invalid negative initial state and unstable large-step
    # integration must be rejected rather than silently projected positive.
    clipping_misses = 0
    negative_initial = initial(Config(H=2), 1)
    negative_initial[0, 0, 0, 0] = -1e-3
    try:
        run(Config(H=2), [0.5], [3.0], x0=negative_initial, points=2)
        clipping_misses += 1
    except ValueError:
        pass
    try:
        run(Config(H=2, T=20.0, dt=1.0), [1.0], [8.0], points=2)
        clipping_misses += 1
    except ValueError:
        pass
    checks.append(check("invalid_density_rejected_without_clipping", clipping_misses, 0.0))

    # Frozen-resident rare-mutant operator: self-neutrality, a genuine positive
    # invader, and a nonzero resource perturbation negative control.
    resident_cfg = Config(H=2, dt=0.1)
    resident = equilibrium(resident_cfg, 0.5, 3.0)
    resident_G = generator(
        resident_cfg, 0.5, 3.0, resident["environment"]
    )
    resident_vector = resident["state"].ravel()
    independent_residual = float(
        np.max(np.abs(resident_G @ resident_vector))
        / max(1.0, resident_vector.sum())
    )
    independent_self_rate = float(np.max(eigvals(resident_G).real))
    positive_invader = float(
        np.max(eigvals(generator(resident_cfg, 1.0, 1.0, resident["environment"])).real)
    )
    perturbed_env = resident["environment"].copy()
    perturbed_env[1] *= 1.05
    perturbed_rate = float(
        np.max(eigvals(generator(resident_cfg, 0.5, 3.0, perturbed_env)).real)
    )
    checks.append(check("resident_self_operator_residual", max(independent_residual, resident["residual"]), 2e-9))
    checks.append(check("resident_self_spectral_abscissa", max(abs(independent_self_rate), abs(resident["self_rate"])), 2e-8))
    checks.append(check("shared_culture_positive_invader", max(0.0, 1e-5 - positive_invader), 0.0, f"rate={positive_invader}"))
    checks.append(check("resource_perturbation_nonzero_control", max(0.0, 1e-5 - abs(perturbed_rate)), 0.0, f"rate={perturbed_rate}"))

    # Conditional newborn survival is a probability and becomes one when
    # juvenile mortality and query cost vanish.
    survival_violation = 0.0
    zero_mortality_error = 0.0
    for d in (0.0, 0.5, 1.0):
        for tau in (0.5, 3.0, 8.0):
            value = survival(resident_cfg, d, tau, resident["environment"])
            survival_violation = max(
                survival_violation, max(0.0, -value), max(0.0, value - 1.0)
            )
            zero_cfg = replace(
                resident_cfg,
                payoff=False,
                query_cost=0.0,
                mu_F=0.0,
            )
            zero_value = survival(zero_cfg, d, tau, resident["environment"])
            zero_mortality_error = max(zero_mortality_error, abs(zero_value - 1.0))
    checks.append(check("conditional_survival_probability_range", survival_violation, 2e-14))
    checks.append(check("conditional_survival_zero_mortality", zero_mortality_error, 2e-12))

    diagnostics["operator"] = {
        "resident_N": resident["N"],
        "reported_residual": resident["residual"],
        "independent_residual": independent_residual,
        "reported_self_rate": resident["self_rate"],
        "independent_self_rate": independent_self_rate,
        "positive_invader_d1_tau1": positive_invader,
        "resource_plus_5pct_self_rate": perturbed_rate,
    }

    status = "PASS" if all(item["pass"] for item in checks) else "FAIL"
    payload = {
        "status": status,
        "scope": (
            "Independent event enumeration, invariants, truth-confusion identification, "
            "operator, integration, and negative-control checks; not empirical validation."
        ),
        "checks": checks,
        "diagnostics": diagnostics,
    }
    (ROOT / "verification.json").write_text(
        json.dumps(payload, indent=2, allow_nan=False) + "\n"
    )
    failed = [item for item in checks if not item["pass"]]
    print(json.dumps({"status": status, "failed": failed, "diagnostics": diagnostics}, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
