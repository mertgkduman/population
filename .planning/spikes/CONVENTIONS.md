# Spike Conventions

This initial spike follows choices explicitly required by the user; future spikes should reuse them where applicable.

## Stack

Python NumPy/SciPy for high-accuracy references; plain JavaScript and inline Plotly for offline interactive inspection.

## Structure

One numbered `.planning/spikes/NNN-name/` directory with schema, readable reference source, browser source, verification JSON, data exports, README, and findings. `.planning/spikes/MANIFEST.md` indexes the spike.

## Patterns

Write Given/When/Then checks before execution. Keep analytic and numerical outcomes distinct. Record all units, versions, tolerances, timestamps, run IDs, and hashes. A technical VALIDATED verdict does not imply empirical support for the underlying biological story.

## Tools and libraries

NumPy 2.2.6, SciPy 1.17.1, Plotly 7.1.0, Node 24.21.0, Chrome for Testing 154.0.8037.92 worked in this environment.

## Multi-spike research versions

V4 uses one versioned research folder with shared model/schema/data and numbered evidence records that link to it. Across spikes004–008, retain exactly two biological stages per genotype but explicitly document additional cognitive states. Keep genetic inheritance separate from learned cultural state. Compare mutants in the same resident culture/resources. Label finite-horizon growth, low-density growth, equilibrium abundance and invasion fitness separately. Reuse independent seeds within matched environmental paths, then reserve fresh paths for confirmation.

Derived probabilities need explicit [0,1] checks; coarse plotting intervals must not be used as integration steps. Offline dashboards may explore precomputed results when the interface explicitly says so. Verify rendered interactions with HTTP(S) blocked and preserve the browser test report.

## Information-access comparisons (V5)

Across spikes009–011, retain private learners' acquired knowledge as the primary comparator. Separate social memory acceptance from current conflict override; compare held beliefs, private evidence and public actions. Treat forced memory reset as an ablation. Label imposed adult query policies and test zero query cost. Confidence-based source selection must expose search availability and costs; it may not access true correctness. A task-load rate divisor is not a model of combinatorial complexity. Pair stochastic histories with common random numbers and reserve new seeds for exploratory follow-ups.
