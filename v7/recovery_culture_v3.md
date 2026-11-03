# V7 C3 finite-resource cultural-accumulation sensitivity

This is a new, separately frozen R1b-v3 sensitivity model. It supersedes none of
the earlier R1b toy outputs: v1/v2 and the earlier matched-work exercise remain
finite abstract skill/productivity toys and are not evidence for the accounting
claims below.

## Frozen contract and mechanics

The source/config registration, archive, machine checks, raw seasonal ledger, and
summaries are under `v7/evidence/recovery_culture_v3/`; confirmation endpoints are
under `v7/experiments/output/recovery_culture_v3/`. It fixed 24 fresh seeds
`82301..82324`, 60 seasons, 10 blank founders, maximum age 18, maturation age 3,
four work tokens/person/season, a six-stage procedure, private sensor accuracy .8,
and an operational prospective population cap of 256.

Every energy gain is a resource withdrawal. For resource \(R\), individual energy
\(E_i\), and conversion \(\eta=.75\), regeneration and harvest are

\[
R\leftarrow R+.06(800-R),\qquad R\leftarrow R-d,\quad E_i\leftarrow E_i+.75d.
\]

The unconverted \(.25d\), maintenance, discovery, teaching, storage, and the birth
residual are explicit sinks. A birth debits 6 energy, credits the blank newborn 4,
and books the residual 2 as a sink. Death and carrier removal book remaining energy
as sinks. Each season asserts the resource-plus-living-energy stock equals initial
stock plus recorded regeneration minus recorded sinks, within \(10^{-7}\).

No procedure produces automatic energy: only an actual paid harvest does. A complete
causal recipe draws four physical resource units; otherwise safe harvest draws two.
Failed/incomplete procedures cannot earn the high yield. Private discovery needs
eight paid work units/stage (six stages: minimum 48); the individual lifetime work
ceiling is 72. Copying costs a work token for both teacher and learner plus energy on
both sides; only not-yet-processed teachers with capacity are eligible. Stored
recipes retain a prefix sequence and innovation/source-root identity.

## Actual run

The confirmation has 120 rows (five arms × 24 seeds), with 89 complete horizons and
31 extinctions; no operational caps occurred. Stock accounting, blank-newborn, and
storage-off machine gates passed. Mean functional people were 1.208 for
transmission+innovation, .833 for no transmission, .833 for functional prerequisite
scramble, .208 for carrier loss/storage off, and 2.208 for carrier loss/storage on.
These are finite descriptive outcomes only, not selection, long-run growth, or a
demonstration that culture exceeds feasible individual acquisition.

Carrier-loss rows retain instantaneous loss before later innovation, storage roots,
and a no-innovation-after-loss diagnostic. Storage-off has zero storage items by
construction and check.

## Explicit remaining gap

The required v3 feasible shared-ex-ante-work independent paired control was **not
run**. Its pre-registration prototype failed safety review before source freeze; the
failure record is `matched_control_pre_registration_failure.json`. No source snapshot
or raw outcome was written for it, and no paired result is claimed. A future repair
must use fixed seasonal snapshots, prospective cap/event censoring, and a paid-birth
material upper-bound assertion before new seeds are registered.

R1a's earlier comparator is also retained as approximate: its posted
`time_opportunity=(depth+1)*safe_yield` does not equal the one-token information
transition, and its EVI computation charge is sunk on every decision. It is not a
perfect opportunity-cost-matched comparator.
