# Predeclared Given/When/Then checks

Recorded before running the sweep. Measured values appear in `verification.json`.

1. Given copying and equal private/adult MSE, when d varies, then loss and demographic outputs are unchanged.
2. Given d=0, when adult accuracy, bias, or correlation changes, then outputs are unchanged.
3. Given cloned signals, when d varies, then copying and weighted judgment are unchanged.
4. Given k_error=0, when d varies, then demography is unchanged under both policies.
5. Given copying, when adult MSE is below or above private MSE, then follower mortality respectively falls or rises with d.
6. Given independent equal-quality estimates and weighted judgment, when d varies, then minimum loss occurs inside (0,1).
7. Given zero births and deaths, when maturation proceeds, then N is constant and F/A match the closed form.
8. Given fixed resources, when numerically integrated, then the solution matches the matrix exponential and r0 matches an independent eigenvalue calculation.
9. Given positive and threshold cases, when equilibrium and invasion are computed, then fluxes balance, r0=0 matches the threshold, and resident self-invasion is zero.
10. Given invalid, zero, and near-threshold cases, when solved, then invalid inputs fail, populations remain nonnegative, all-zero is absorbing, and near-threshold transients are distinguished from equilibrium.
11. Given both policies and M0/M1 with extreme d and tau, when browser RK4 is compared to SciPy DOP853, then errors and step halving meet recorded tolerances.
12. Given the dashboard, when loaded offline and exercised, then play/pause/scrub, heatmap click, pins, exports, resize, and console errors are checked or explicitly marked unavailable.
