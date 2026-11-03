# V7 R1 recovery comparison

This document records additional bounded recovery experiments after the independent
review.  It does not alter the frozen base, corrected-primary overlay, or their
registrations.  R1a uses the corrected ecological world; R1b is a separately labeled
minimal demographic sensitivity model, not a replacement primary model.

## Registration, definitions, and checks

The immutable pre-outcome registration and source archive are
[`evidence/recovery_comparison/registration.json`](evidence/recovery_comparison/registration.json)
and `source_snapshot.tar.gz`.  They declare Given/When/Then tests, R1a sentinel
regimes 1/5/9, 24 paired fresh seeds `81001..81024`, and R1b pilot seeds
`82001..82024`; no precision-extension batches were used.  The R1b cap repair is
separately registered/snapshotted in `r1b_v2_registration.json`, with fresh seeds
`82101..82124`.  These registrations precede their respective output files.

R1a's common policy observation excludes evaluator truth.  All policies use the
same corrected-world private hardware `rho=.8`, 12 time tokens, 128-operation cap,
physical task utility, production mechanics, and resident demography.  The new
`MatchedActionConditionalPolicy` evaluates a one-decision expected value of
information:

\[
V_I = \sum_s P(s\mid h)\max_a Q_0(a\mid h,s)
 - c_I - c_{op}n_I - c_{time},
\]

then buys only the best positive option relative to \(\max_a Q_0(a\mid h)\).
Query has expected and executed accuracy `.80`; verification has expected and
executed accuracy `.90`.  Executed information consumes the shared ecology time
token and posted charge; computation and physical production are charged through
the existing ledger.  This is an observation-limited, bounded, one-decision
comparator—not general/optimal RL and not a full-horizon optimal policy.

R1b procedures are `prepare → shape → finish` (or a viable shuffled prerequisite
graph).  Functional output requires causal prerequisites, reusable acquired modules,
and actual physical success; newborns inherit a genetic scalar only and begin with
blank procedure state.  Private acquisition, teaching, storage read/write/maintenance,
and production all consume recorded work/resources.  Carrier removal deletes actual
people before post-loss knowledge is recorded; storage is either absent or separately
paid.  The pre-outcome test suite covers private hardware parity, truth firewall,
blank newborn state, paid work, storage-off, non-pooled feasible individual work, and
the v2 forced-cap sentinel.

## R1a corrected-ecology results

The confirmation output has 360 rows: 3 regimes × 5 policies × 24 paired seeds
([`r1a_confirmation.csv.gz`](experiments/output/recovery_comparison/r1a_confirmation.csv.gz)).
Every row completed the fixed 240-season corrected-ecology horizon; legacy output
labels that completed horizon as `running`, so it is not an active/censored run.

| Sentinel | Comparator | Mean population | Paired population difference vs ordinary (MCSE) |
|---:|---|---:|---:|
| 1 | FeatureTrust | 54.916 | -6.714 (0.161) |
| 1 | vector (.5, 0) | 61.941 | +0.311 (0.154) |
| 1 | vector (1, 0) | 61.429 | -0.201 (0.237) |
| 1 | bounded action-conditional | 57.312 | -4.318 (0.185) |
| 5 | FeatureTrust | 56.549 | -6.751 (0.196) |
| 5 | vector (.5, 0) | 63.594 | +0.293 (0.266) |
| 5 | vector (1, 0) | 63.510 | +0.209 (0.192) |
| 5 | bounded action-conditional | 58.997 | -4.304 (0.176) |
| 9 | FeatureTrust | 56.518 | -6.602 (0.331) |
| 9 | vector (.5, 0) | 63.396 | +0.276 (0.285) |
| 9 | vector (1, 0) | 63.331 | +0.211 (0.352) |
| 9 | bounded action-conditional | 58.887 | -4.234 (0.222) |

Across the 72 comparator rows, the bounded comparator selected zero queries and
1,971 verification events in its retained audit window.  This observation is not a
whole-run purchase-rate denominator: the corrected ecology retains a bounded event
window, so precise query/no-teacher/conflict opportunity rates remain unavailable.
It does establish an executed verification path, shared physical accounting, and no
hidden-truth policy interface.  The comparator did not improve this finite outcome
over ordinary social learning in these three sentinels.

## R1b demographic sensitivity results and repairs

The original `82001..82024` R1b output is preserved as a distinctly named,
capacity-constrained pilot (`r1b_confirmation.csv.gz`, 144 rows).  Audit after the
run found its 40-person condition suppressed prospective births without a cap-event
record.  It is therefore not used as the demographic primary result and cannot supply
a cap denominator.

R1b v2 replaces that mechanism with a predeclared operational cap of 256: at an
actual would-exceed birth event it records `cap_censored` and stops while retaining
all living people; it never truncates/replaces a population.  A forced cap=2 sentinel
recorded exactly one cap event and retained two people.  The v2 confirmation
([`r1b_v2_confirmation.csv.gz`](experiments/output/recovery_comparison/r1b_v2_confirmation.csv.gz))
contains 144 rows: 0/144 cap-censored, 15/144 extinct, and 129/144 complete at the
18-season horizon.  These are finite-horizon denominators, not long-run growth.

| v2 arm | Functional people mean | Population mean | Paid work mean |
|---|---:|---:|---:|
| transmission + innovation | 36.458 | 46.292 | 133.250 |
| no transmission | 24.958 | 37.708 | 110.875 |
| independent feasible-work | 24.958 | 37.708 | 110.875 |
| prerequisite shuffle | 36.375 | 46.042 | 132.917 |
| carrier loss, storage off | 1.625 | 2.542 | 49.667 |
| carrier loss, paid storage on | 1.750 | 2.250 | 77.479 |

The separate no-innovation-after-loss output has 48 rows and preserves immediate
loss/recovery fields.  It distinguishes memory present immediately after actual
carrier removal from later possible reinvention; it does not interpret later recovery
as retained memory.

The feasible `equal_work_independent` v2 arm remains a per-person, non-pooled
control, but its realized aggregate work differs from transmission+innovation.
Accordingly, a third, separately preregistered paired shared-work control used fresh
`82201..82224` seeds.  In each season it offers
\(W_t=\min(\text{feasible T+I person-work},\text{feasible independent person-work})\)
to each *independent* population; each allocates only among its own living people
with a four-unit cap.  No knowledge, outcomes, resources, or people cross the pair.
It records every season's offered/realized effort and infeasibility in
`matched_work_raw_seasons.json`.

All 24 pairs realized precisely equal offered work, with zero infeasible pairs and
24 complete-horizon statuses.  Mean functional people were 37.083 for transmission +
innovation and 27.083 for independent solvers.  This is an exact finite
shared-effort intervention—not competition, a pooled solver, selection, or a
long-run result.

## Limitations and unresolved items

- R1b v2's `equal_work_independent` arm is feasible and not pooled, but its realized
  aggregate work (110.875) does **not** equal the transmission+innovation arm's
  realized aggregate work (133.250); it is retained only as a per-person control.
  The distinct `82201..82224` paired shared-work experiment above supplies the
  equal-realized-work comparison, with its own finite/intervention scope.
- The original R1b pilot's active capacity constraint is archived only; it is not a
  censoring result.  V2 fixes the accounting interface but observed no operational
  cap at 256.
- R1a aggregate query/verification/no-teacher/conflict opportunity denominators are
  not whole-run exports.  Retained-window event counts cannot satisfy a Wilson-rate
  precision claim.
- R1a is descriptive for three corrected-world sentinel regimes and 240 seasons;
  R1b is a small 18-season finite demographic sensitivity.  Neither establishes
  general RL optimality, a cultural novelty claim, selection, ESS, or long-run growth.

## Integrity

`machine_checks.json` passes its recorded R1a/R1b pilot gates.  V2's forced-cap,
blank-state, storage-off, and paid-work checks pass in `r1b_v2_machine_checks.json`.
Raw SHA-256 values are in the associated summaries.  Raw rows, including every
extinction and all observed cap events, are retained under
`experiments/output/recovery_comparison/`.
