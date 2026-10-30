"""Independent numerical and structural checks for the v4 finite-state model.

This script intentionally rebuilds several expected quantities outside the main
experiment driver.  It writes machine-readable measured results to
``verification.json`` and exits nonzero if any predeclared check fails.
"""
from __future__ import annotations

import json
import math
from dataclasses import replace
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import eigvals, expm
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

from model import (
    Config,
    choice,
    correct,
    environment,
    equilibrium,
    generator,
    initial,
    maturation_survival,
    metrics,
    rhs,
    rkstep,
    run,
    shape,
    shift,
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
    return float(np.max(np.abs(observed - expected) / np.maximum(1.0, np.abs(expected))))


def integrate_fixed_environment(c, d, tau, q, resource, horizon):
    x = initial(c, 1)
    t = 0.0
    env = (np.array([q]), np.array([resource]))
    while t < horizon - 1e-12:
        h = min(c.dt, horizon - t)
        x = rkstep(c, x, [d], [tau], t, lambda _: 1, env=env, h=h)
        t += h
    return x


def dop853_reference(c, d, tau, times):
    y0 = initial(c, 1).ravel()
    target_shape = (1, 2, *shape(c))

    def fun(_t, y):
        return rhs(c, y.reshape(target_shape), [d], [tau], 1).ravel()

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


def main():
    checks = []
    diagnostics = {}

    # Reflecting score caps: confirmation stays at a cap and contradiction
    # moves inward.  The operation must conserve mass, including RL trust caps.
    c = Config(H=1)
    x = np.zeros((1, *shape(c)))
    x[0, -1, 0] = 2.0
    x[0, 0, 0] = 3.0
    up = shift(x, 1)
    down = shift(x, -1)
    boundary_error = max(
        abs(up[0, -1, 0] - 2.0),
        abs(down[0, -2, 0] - 2.0),
        abs(down[0, 0, 0] - 3.0),
        abs(up[0, 1, 0] - 3.0),
        abs(up.sum() - x.sum()),
        abs(down.sum() - x.sum()),
    )
    checks.append(check("reflecting_score_caps_move_inward", boundary_error, 0.0))

    crl = Config(H=1, policy="rl")
    xr = np.zeros((1, *shape(crl)))
    xr[0, 1, -1] = 4.0
    trust_inward = shift(xr, 0, -1)
    trust_outward = shift(xr, 0, 1)
    trust_error = max(
        abs(trust_inward[0, 1, -2] - 4.0),
        abs(trust_outward[0, 1, -1] - 4.0),
        abs(trust_inward.sum() - xr.sum()),
        abs(trust_outward.sum() - xr.sum()),
    )
    checks.append(check("reflecting_trust_caps_move_inward", trust_error, 0.0))

    # A no-birth/no-death system contains only cognitive transitions and
    # state-preserving maturation, so total density is exactly conserved.
    closed = Config(
        H=2,
        juvenile_rate=0.7,
        adult_rate=0.4,
        mu_F=0.0,
        mu_A=0.0,
        error_death=0.0,
        adult_error_death=0.0,
        beta_base=0.0,
        beta_skill=0.0,
        payoff=False,
    )
    rng = np.random.default_rng(20261030)
    random_state = rng.uniform(0.1, 4.0, size=(1, 2, *shape(closed)))
    closed_rhs = rhs(closed, random_state, [0.6], [3.0], 1)
    checks.append(check("learning_and_maturation_conserve_total_density", abs(closed_rhs.sum()), 2e-13))

    # Closed-form pure maturation benchmark.
    pure = replace(closed, juvenile_rate=0.0, adult_rate=0.0, T=10.0, dt=0.1)
    tau = 4.0
    tr = run(pure, [0.6], [tau], points=101)
    expected_f = 80.0 * np.exp(-tr["t"] / tau)
    expected_a = 20.0 + 80.0 * (1.0 - np.exp(-tr["t"] / tau))
    maturation_error = max(
        float(np.max(np.abs(tr["F"][0] - expected_f))),
        float(np.max(np.abs(tr["A"][0] - expected_a))),
        float(np.max(np.abs(tr["N"][0] - 100.0))),
    )
    checks.append(check("pure_maturation_closed_form", maturation_error, 2e-7))

    # Instantaneous state-preserving transfer and its reset negative control.
    transfer_state = np.zeros((1, 2, *shape(pure)))
    transfer_state[0, 0, 0, 0] = 3.0
    transfer_state[0, 0, -1, 0] = 7.0
    fixed_env = (np.array([0.5]), np.array([0.0]))
    carry = rhs(pure, transfer_state, [0.0], [2.0], 1, fixed_env)
    reset = rhs(replace(pure, reset_maturation=True), transfer_state, [0.0], [2.0], 1, fixed_env)
    carry_expected = np.zeros(shape(pure)[0])
    carry_expected[0], carry_expected[-1] = 1.5, 3.5
    reset_expected = np.zeros(shape(pure)[0])
    reset_expected[pure.H] = 5.0
    checks.append(check("maturation_preserves_cognitive_state", np.max(np.abs(carry[0, 1, :, 0] - carry_expected)), 0.0))
    checks.append(check("reset_maturation_routes_to_neutral_state", np.max(np.abs(reset[0, 1, :, 0] - reset_expected)), 0.0))

    # All births must enter neutral score and neutral trust.
    birth_cfg = Config(H=2, policy="rl", juvenile_rate=0.0, adult_rate=0.0, mu_F=0.0, mu_A=0.0, error_death=0.0, adult_error_death=0.0)
    birth_state = np.zeros((1, 2, *shape(birth_cfg)))
    birth_state[0, 1, -1, -1] = 10.0
    birth_rhs = rhs(birth_cfg, birth_state, [0.0], [3.0], 1, (np.array([0.7]), np.array([0.25])))
    nonneutral = birth_rhs[0, 0].copy()
    neutral_birth = nonneutral[birth_cfg.H, shape(birth_cfg)[1] // 2]
    nonneutral[birth_cfg.H, shape(birth_cfg)[1] // 2] = 0.0
    birth_error = float(np.max(np.abs(nonneutral))) + max(0.0, -float(neutral_birth))
    checks.append(check("births_enter_neutral_score_and_trust", birth_error, 0.0))

    # Independently reconstruct total births and deaths, then compare them
    # with the full state derivative for both fixed and RL policies.
    flux_error = 0.0
    for policy in ("fixed", "rl"):
        fc = Config(H=2, policy=policy)
        state = rng.uniform(0.2, 3.0, size=(1, 2, *shape(fc)))
        d, tau = 0.7, 5.0
        q, resource = environment(fc, state, 1)
        w = choice(fc, [d], q)
        q_eff = np.maximum(q, 1.0 - q) if policy == "oracle" else q
        acc = fc.p + w * (q_eff[:, None] - fc.p)
        ac = correct(fc, 1)[None, :, None]
        births = np.sum(state[:, 1] * (fc.beta_base + fc.beta_skill * ac) * resource[:, None, None])
        deaths_f = np.sum(state[:, 0] * (fc.mu_F + fc.error_death * (1.0 - acc))[:, None, :])
        deaths_a = np.sum(state[:, 1] * (fc.mu_A + fc.adult_error_death * (1.0 - ac)))
        flux_error = max(flux_error, abs(float(rhs(fc, state, [d], [tau], 1).sum()) - float(births - deaths_f - deaths_a)))
    checks.append(check("total_flux_identity", flux_error, 2e-12))

    # At q=p the full fixed-policy generator, not just current mortality, is
    # independent of d in this mean-field internalization construction.
    null_error = 0.0
    for internalize in (True, False):
        nc = Config(H=2, internalize=internalize)
        g0 = generator(nc, 0.0, 4.0, nc.p, 0.25)
        g1 = generator(nc, 1.0, 4.0, nc.p, 0.25)
        null_error = max(null_error, float(np.max(np.abs(g0 - g1))))
    checks.append(check("equal_accuracy_full_generator_d_null", null_error, 2e-14))

    # Direct source-choice checks: the fixed rule must obey p+d(q-p), and the
    # oracle must invert sufficiently anti-informative adult advice rather than
    # treating its raw sign as accurate.
    source_state = initial(Config(H=2), 1)
    fixed_cfg = Config(H=2)
    fixed_metric = metrics(fixed_cfg, source_state, [0.7], [4.0], env=(np.array([0.8]), np.array([0.25])))
    fixed_formula_error = abs(float(fixed_metric["public_F"][0]) - (fixed_cfg.p + 0.7 * (0.8 - fixed_cfg.p)))
    checks.append(check("fixed_conflict_choice_accuracy_formula", fixed_formula_error, 2e-15))

    oracle_cfg = Config(H=2, policy="oracle")
    oracle_state = initial(oracle_cfg, 1)
    inverted = metrics(oracle_cfg, oracle_state, [0.0], [4.0], env=(np.array([0.2]), np.array([0.25])))
    ignored = metrics(oracle_cfg, oracle_state, [0.0], [4.0], env=(np.array([0.4]), np.array([0.25])))
    oracle_error = max(abs(float(inverted["public_F"][0]) - 0.8), abs(float(ignored["public_F"][0]) - oracle_cfg.p))
    checks.append(check("oracle_inverts_only_when_effectively_more_accurate", oracle_error, 2e-15))

    # With objective full feedback, certainly correct adult advice moves every
    # juvenile trust state up and certainly wrong advice moves it down.  With
    # feedback disabled, trust cannot move.  Aggregate over score because the
    # selected/private action may legitimately split z states.
    trust_cfg = Config(
        H=1,
        policy="rl",
        juvenile_rate=1.0,
        adult_rate=0.0,
        mu_F=0.0,
        mu_A=0.0,
        error_death=0.0,
        adult_error_death=0.0,
        beta_base=0.0,
        beta_skill=0.0,
        payoff=False,
        feedback=1.0,
    )
    trust_state = np.zeros((1, 2, *shape(trust_cfg)))
    trust_state[0, 0, trust_cfg.H, 2] = 1.0
    trust_up = rhs(trust_cfg, trust_state, [0.0], [1e12], 1, (np.array([1.0]), np.array([0.0])))
    trust_down = rhs(trust_cfg, trust_state, [0.0], [1e12], 1, (np.array([0.0]), np.array([0.0])))
    no_feedback = rhs(replace(trust_cfg, feedback=0.0), trust_state, [0.0], [1e12], 1, (np.array([1.0]), np.array([0.0])))
    # Subtract the negligible maturation outflow from the neutral trust state's
    # expected diagonal before comparing the trust marginal.
    up_marginal = trust_up[0, 0].sum(axis=0)
    down_marginal = trust_down[0, 0].sum(axis=0)
    nofb_marginal = no_feedback[0, 0].sum(axis=0)
    trust_error = max(
        abs(up_marginal[3] - 1.0),
        abs(down_marginal[1] - 1.0),
        abs(nofb_marginal[1]),
        abs(nofb_marginal[3]),
    )
    checks.append(check("rl_trust_uses_realized_objective_feedback", trust_error, 2e-12))

    # With all correctness payoffs disabled, d may change culture but cannot
    # change aggregate demography at fixed tau.
    npc = Config(H=2, payoff=False, T=30.0, dt=0.05)
    no_payoff = run(npc, [0.0, 1.0], [4.0, 4.0], points=31)
    demographic_null = max(
        float(np.max(np.ptp(no_payoff["F"], axis=0))),
        float(np.max(np.ptp(no_payoff["A"], axis=0))),
        float(np.max(np.ptp(no_payoff["N"], axis=0))),
    )
    cultural_difference = float(np.max(np.abs(no_payoff["belief_A"][0] - no_payoff["belief_A"][1])))
    checks.append(check("no_payoff_d_demographic_null", demographic_null, 2e-9, "Cultural states are allowed to differ."))
    diagnostics["no_payoff_max_adult_belief_difference"] = cultural_difference

    # Newborn survival-to-maturation is a probability conditional on fixed
    # final advice, not a time-grid integral of standing-population hazards.
    # First enforce probability bounds over policies and heterogeneous inputs.
    survival_range_violation = 0.0
    survival_samples = {}
    survival_d = np.array([0.0, 0.35, 1.0])
    survival_tau = np.array([0.5, 3.0, 12.0])
    survival_q = np.array([0.0, 0.65, 1.0])
    for policy in ("fixed", "private", "oracle", "rl"):
        sc = Config(policy=policy)
        observed = maturation_survival(sc, survival_d, survival_tau, survival_q)
        survival_samples[policy] = observed.tolist()
        if not np.all(np.isfinite(observed)):
            survival_range_violation = float("inf")
        else:
            survival_range_violation = max(
                survival_range_violation,
                max(0.0, -float(observed.min())),
                max(0.0, float(observed.max()) - 1.0),
            )
    checks.append(check("maturation_survival_probability_range", survival_range_violation, 2e-14))

    # Fixed d=0 and d=1 reduce to scalar competing-risk formulas using private
    # and adult accuracy respectively.
    scalar_cfg = Config(policy="fixed")
    scalar_tau = 4.0
    scalar_q = 0.82
    scalar_observed = maturation_survival(
        scalar_cfg, np.array([0.0, 1.0]), scalar_tau, scalar_q
    )
    scalar_m = 1.0 / scalar_tau
    scalar_accuracy = np.array([scalar_cfg.p, scalar_q])
    scalar_mortality = scalar_cfg.mu_F + scalar_cfg.error_death * (1.0 - scalar_accuracy)
    scalar_expected = scalar_m / (scalar_m + scalar_mortality)
    checks.append(
        check(
            "maturation_survival_fixed_scalar_endpoints",
            np.max(np.abs(scalar_observed - scalar_expected)),
            2e-15,
        )
    )

    # With feedback disabled, a newborn RL learner remains at neutral trust,
    # so its five-state calculation must equal the scalar neutral-trust risk.
    nofb_cfg = Config(policy="rl", feedback=0.0)
    nofb_tau = 5.0
    nofb_q = 0.78
    nofb_observed = maturation_survival(
        nofb_cfg, np.array([0.0, 1.0]), nofb_tau, nofb_q
    )
    neutral_follow = 0.5
    neutral_accuracy = nofb_cfg.p + neutral_follow * (nofb_q - nofb_cfg.p)
    neutral_mortality = nofb_cfg.mu_F + nofb_cfg.error_death * (1.0 - neutral_accuracy)
    nofb_expected = (1.0 / nofb_tau) / (1.0 / nofb_tau + neutral_mortality)
    checks.append(
        check(
            "maturation_survival_rl_no_feedback_scalar",
            np.max(np.abs(nofb_observed - nofb_expected)),
            2e-15,
        )
    )

    # If juvenile mortality is zero, maturation eventually occurs with
    # probability one for every policy even while RL trust continues moving.
    zero_mortality_error = 0.0
    for policy in ("fixed", "private", "oracle", "rl"):
        zmc = Config(policy=policy, mu_F=0.0, error_death=0.0)
        observed = maturation_survival(zmc, survival_d, survival_tau, survival_q)
        zero_mortality_error = max(
            zero_mortality_error, float(np.max(np.abs(observed - 1.0)))
        )
    checks.append(check("maturation_survival_zero_mortality", zero_mortality_error, 3e-15))

    # Independently integrate the killed RL trust process in time and its
    # accumulated maturation flux.  This checks the linear solve against a
    # different numerical route and reconstructs J locally in the test.
    transient_cfg = Config(policy="rl", feedback=0.73)
    transient_d, transient_tau, transient_q = 0.27, 3.7, 0.74
    transient_m = 1.0 / transient_tau
    trust = np.arange(-2, 3)
    follow = 1.0 / (1.0 + np.exp(-transient_cfg.trust_temperature * trust))
    trust_accuracy = transient_cfg.p + follow * (transient_q - transient_cfg.p)
    trust_mortality = transient_cfg.mu_F + transient_cfg.error_death * (1.0 - trust_accuracy)
    transient_J = -np.diag(transient_m + trust_mortality)
    for r in range(5):
        for step, probability in ((1, transient_q), (-1, 1.0 - transient_q)):
            rate = transient_cfg.juvenile_rate * transient_cfg.feedback * probability
            target = min(4, max(0, r + step))
            transient_J[target, r] += rate
            transient_J[r, r] -= rate
    augmented_initial = np.zeros(6)
    augmented_initial[2] = 1.0

    def transient_rhs(_time, state):
        derivative = np.empty_like(state)
        derivative[:5] = transient_J @ state[:5]
        derivative[5] = transient_m * state[:5].sum()
        return derivative

    transient_solution = solve_ivp(
        transient_rhs,
        (0.0, 150.0),
        augmented_initial,
        method="DOP853",
        rtol=1e-12,
        atol=1e-14,
    )
    if not transient_solution.success:
        raise RuntimeError(transient_solution.message)
    transient_integral = float(transient_solution.y[5, -1])
    transient_tail = float(transient_solution.y[:5, -1].sum())
    transient_exact = float(
        maturation_survival(
            transient_cfg, [transient_d], [transient_tau], [transient_q]
        )[0]
    )
    transient_error = abs(transient_integral - transient_exact) + abs(transient_tail)
    checks.append(
        check(
            "maturation_survival_rl_transient_integral",
            transient_error,
            2e-11,
            "Error includes the residual unmatured/undead transient mass at integration cutoff.",
        )
    )
    diagnostics["maturation_survival"] = {
        "range_samples": survival_samples,
        "fixed_scalar_observed": scalar_observed.tolist(),
        "fixed_scalar_expected": scalar_expected.tolist(),
        "rl_no_feedback_observed": nofb_observed.tolist(),
        "rl_no_feedback_expected": nofb_expected,
        "rl_transient_linear_solve": transient_exact,
        "rl_transient_time_integral": transient_integral,
        "rl_transient_tail": transient_tail,
    }

    # The basis-built generator must be Metzler and agree with an independent
    # matrix exponential.  Primary positive-rate graphs should be irreducible.
    metzler_violation = 0.0
    exponential_error = 0.0
    reducible_cases = 0
    for policy in ("fixed", "private", "oracle", "rl"):
        gc = Config(H=2, policy=policy, dt=0.01)
        d, tau, q, resource, horizon = 0.7, 4.0, 0.72, 0.30, 2.0
        g = generator(gc, d, tau, q, resource)
        off_diagonal = g.copy()
        np.fill_diagonal(off_diagonal, 0.0)
        metzler_violation = max(metzler_violation, max(0.0, -float(np.min(off_diagonal))))
        adjacency = csr_matrix((off_diagonal.T > 1e-14).astype(np.int8))
        components = connected_components(adjacency, directed=True, connection="strong", return_labels=False)
        reducible_cases += int(components != 1)
        exact = expm(g * horizon) @ initial(gc, 1).ravel()
        observed = integrate_fixed_environment(gc, d, tau, q, resource, horizon).ravel()
        exponential_error = max(exponential_error, scaled_error(observed, exact))
    checks.append(check("mutant_generators_are_metzler", metzler_violation, 2e-14))
    checks.append(check("primary_transition_graphs_irreducible", reducible_cases, 0.0))
    checks.append(check("fixed_environment_matrix_exponential_parity", exponential_error, 1e-8))

    # Dynamic nonlinear RK4 trajectories against an independent DOP853 solve,
    # and explicit step halving.  These are representative fixed and RL cases,
    # not a broad sweep.
    rk4_errors = {}
    for policy in ("fixed", "rl"):
        dc = Config(H=3, policy=policy, T=30.0, dt=0.1)
        times = np.linspace(0.0, dc.T, 31)
        reference = dop853_reference(dc, 0.8, 7.0, times)
        for dt in (0.1, 0.05):
            observed = run(replace(dc, dt=dt), [0.8], [7.0], points=len(times))["states"][0].reshape(len(times), -1)
            rk4_errors[f"{policy}_dt_{dt}"] = scaled_error(observed, reference)
    checks.append(check("rk4_dt_0p1_vs_DOP853", max(v for k, v in rk4_errors.items() if k.endswith("0.1")), 2e-5))
    checks.append(check("rk4_dt_0p05_vs_DOP853", max(v for k, v in rk4_errors.items() if k.endswith("0.05")), 2e-6))
    diagnostics["rk4_scaled_errors"] = rk4_errors

    # Three representative equilibria: independently check both Lx*=0 and
    # the resident-self spectral abscissa.  Perturbing the frozen resource is
    # a negative control demonstrating that the test is not identically zero.
    self_rate_error = 0.0
    self_residual_error = 0.0
    negative_control_shortfall = 0.0
    equilibrium_records = []
    for d, tau in ((0.1, 1.0), (0.5, 3.0), (0.9, 12.0)):
        ec = Config(H=3)
        x, q, resource, reported_rate, reported_residual = equilibrium(ec, d, tau)
        g = generator(ec, d, tau, q, resource)
        vector = x.ravel()
        independent_residual = float(np.max(np.abs(g @ vector)) / max(1.0, np.sum(vector)))
        independent_rate = float(np.max(eigvals(g).real))
        perturbed_rate = float(np.max(eigvals(generator(ec, d, tau, q, resource * 1.05)).real))
        self_rate_error = max(self_rate_error, abs(independent_rate), abs(reported_rate))
        self_residual_error = max(self_residual_error, independent_residual, reported_residual)
        negative_control_shortfall = max(negative_control_shortfall, max(0.0, 1e-5 - abs(perturbed_rate)))
        equilibrium_records.append(
            {
                "d": d,
                "tau": tau,
                "N": float(x.sum()),
                "q_adv": q,
                "resource": resource,
                "reported_residual": reported_residual,
                "independent_residual": independent_residual,
                "reported_self_rate": reported_rate,
                "independent_self_rate": independent_rate,
                "resource_plus_5pct_rate": perturbed_rate,
            }
        )
    checks.append(check("resident_self_operator_residual", self_residual_error, 2e-9))
    checks.append(check("resident_self_spectral_abscissa", self_rate_error, 2e-8))
    checks.append(check("self_invasion_resource_negative_control", negative_control_shortfall, 0.0))
    diagnostics["representative_equilibria"] = equilibrium_records

    # All-zero is absorbing even though the resource factor and empty-adult
    # testimony default to finite values.
    zc = Config(H=2, T=5.0)
    zeros = np.zeros((1, 2, *shape(zc)))
    zero_run = run(zc, [0.5], [3.0], points=6, x0=zeros)
    checks.append(check("all_zero_state_absorbing", np.max(np.abs(zero_run["states"])), 0.0))

    # Validation must fail early and deterministically, including NaN/Inf and
    # nonintegral score bounds.  Count any case not rejected with ValueError.
    invalid_cases = [
        (replace(Config(), p=-0.1), 0.5, 3.0),
        (replace(Config(), p=1.1), 0.5, 3.0),
        (replace(Config(), transmission_error=0.6), 0.5, 3.0),
        (replace(Config(), feedback=-0.1), 0.5, 3.0),
        (replace(Config(), H=0), 0.5, 3.0),
        (replace(Config(), H=1.5), 0.5, 3.0),
        (replace(Config(), K=0.0), 0.5, 3.0),
        (replace(Config(), KS=np.inf), 0.5, 3.0),
        (replace(Config(), dt=0.0), 0.5, 3.0),
        (replace(Config(), T=0.0), 0.5, 3.0),
        (replace(Config(), mu_A=-0.1), 0.5, 3.0),
        (replace(Config(), p=np.nan), 0.5, 3.0),
        (Config(), np.nan, 3.0),
        (Config(), 0.5, np.nan),
        (Config(), -0.1, 3.0),
        (Config(), 1.1, 3.0),
        (Config(), 0.5, 0.0),
        (replace(Config(), policy="unknown"), 0.5, 3.0),
    ]
    missed = []
    for i, (ic, d, tau) in enumerate(invalid_cases):
        try:
            validate(ic, np.array([d]), np.array([tau]))
        except ValueError:
            continue
        missed.append(i)
    checks.append(check("invalid_parameters_rejected_early", len(missed), 0.0, f"missed case indexes: {missed}"))
    diagnostics["invalid_case_count"] = len(invalid_cases)

    status = "PASS" if all(item["pass"] for item in checks) else "FAIL"
    payload = {
        "status": status,
        "scope": "Independent algebra, generator, numerical-integrator, equilibrium, and negative-control checks; not empirical validation.",
        "checks": checks,
        "diagnostics": diagnostics,
    }
    (ROOT / "verification.json").write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": status, "failed": [c for c in checks if not c["pass"]], "diagnostics": diagnostics}, indent=2))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
