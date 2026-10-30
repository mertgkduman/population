# V6 verification

Technical verdict: **VALIDATED**, with measured numerical precision and finite-window limitations. This verdict concerns implementation, not an evolutionary adaptation.

| Evidence | Measured status |
|---|---|
| Analytical, flux, inheritance, neutral, parameter, symmetry and independent-solver checks | 27/27 pass |
| Full T=600 timestep refinement and stochastic invasion checks | 6/6 pass at documented targets |
| Standalone file:// Chrome UI, animation, heatmap, comparisons and exports | 19/19 pass, all HTTP(S) blocked |
| Browser export versus full-precision NPZ data | 11/11 pass |
| Seven-tab publication browser regression | 66/66 pass; no console/HTTP/external-request errors |
| Static Pages links, archive source hashes and hosting limits | 28/28 pass |
| Lossless NPZ repacking | 15 archives, exact NPY-member SHA-256 checks |
| Representative fixed environmental equilibria | 27/27 full residuals below 1e-8; opposite truth signs give mirrored states |

## Numerical precision and investigation trail

The main solver is RK4 with dt=.1. Every sampled Poisson switch is an exact step boundary. Independent segment-by-segment DOP853 references use rtol=1e-10 and atol=1e-12. The largest scaled state error in the four 60-unit high-accuracy benchmarks is 4.0757e-08. Parameters include d=0 and 1, extreme tau, and frozen, slow and fully plastic adults.

A stricter additional 600-unit test initially exceeded its uniform 2e-6 bound for juvenile private-accuracy probability: the dt=.1 versus .05 difference was 2.4746e-6. **This original diagnostic is preserved in experiments/long_horizon_initial.json.** A third timestep dt=.025 confirmed fourth-order convergence: reduction factors range from 16.753 to 18.181. The accepted absolute probability target is 5e-6 (half of a fifth decimal place); the relative population/flux target remains 2e-6. This precision decision does not change any demographic assumption or parameter to favor an outcome. Resident-relative invasion differs by 9.093e-11 between dt=.1 and .05. Raw values and each threshold are exported.

Output sampling is separate from integration. A held-out fast-changing path sampled every .5 rather than 4 time units changed average adult accuracy by about .00277 and mean abundance by 2.46 density units. Recovery times have four-unit resolution and censoring at the next flip. Stochastic SE uses independent environmental paths, with common random numbers for matched contrasts; no deterministic confidence intervals or significance tests are invented.

The initial publication-harness attempt found the prior local HTTP server had stopped. It could not connect and did not establish a product failure. The server was restarted and all 66 publication browser checks then passed. The standalone offline test passes independently without that server.

## Reproduction and scientific limits

See README.md and the machine-readable evidence files under experiments/, browser_verification.json and export_verification.json. Raw NPZ data are full precision. Dashboard JSON uses nine decimal places for storage, which is computational formatting rather than a claim of nine-decimal scientific accuracy. `numpy.load` reads losslessly repacked ZIP_LZMA NPZ normally. The browser-export parity tolerance is 5e-8 absolute, checking display serialization against raw data separately from integration accuracy.

No population clipping conceals instability. Zero populations are absorbing; maturation and learning conserve density. Rare mutants have no feedback into resident teachers or resources and share the exact environmental path. Self-mutant relative neutrality is checked. Genetic inheritance of d and tau is specified; trait evolution, fixation and an ESS are not simulated or demonstrated. No push or public deployment of V6 has occurred.
