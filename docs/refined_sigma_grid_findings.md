# Phase 2 §4.2 refined sigma-grid findings

## Frozen design and completion

The original condition (128 by 128 matrix, Gaussian lesion width 5 px) was measured
on the preregistered dense grid from sigma 1.00 through 2.50 in increments of 0.10,
with 64 paired realizations at each dense point. Five outer anchors used 16 paired
realizations each. All 1,104 planned paired realizations completed; no values were
missing or nonfinite.

## Breakpoint estimate

The normalized H0 bottleneck curve produced:

- breakpoint sigma: 1.30;
- bootstrap 95% interval: 1.20 to 1.50;
- interval width: 0.30;
- analytic d-prime at the breakpoint: 6.817;
- delta AIC, piecewise minus linear: -59.97.

The one-break model is strongly preferred to a single linear-in-log-sigma curve. The
interval does not touch a knot-search boundary and is narrower than the
preregistered inconclusive threshold of 0.40, so the run is not inconclusive.

## What refinement resolved

The previous intervals were adjacent coarse grid values and could not distinguish
grid quantization from statistical uncertainty. The new 0.10 grid resolves that
problem: the 95% interval spans several refined grid points. Its remaining width is
therefore driven by realization variability and local curve shape, not simply by the
old grid spacing.

The interval is not narrower than one refined grid increment; the preregistered
diagnostic `ci_narrower_than_grid` is false. The breakpoint can now be reported with
an uncertainty interval, but it should not be presented as a high-precision critical
constant.

## Comparison with the earlier independent run

The earlier 128 by 128, lesion-width 5 px run gave a breakpoint of 1.60. Reanalysis
of its raw data with the new profile-fitting implementation still gives 1.60, so the
difference is not caused by changing the estimator. Its reanalysis interval is
approximately 1.42 to 2.00, whereas the new interval is 1.20 to 1.50. The small
overlap near 1.5 and shift in point estimate show that seed-to-seed curve variability
is scientifically material even with 64 realizations in the dense region.

This result strengthens the decision not to call the fitted knot a thermodynamic
critical point. It remains a reproducible region of nonlinear crossover, with a
location that is sensitive to ensemble realization and model condition.

## Decision for the next stage

None of the preregistered inconclusive conditions was triggered: the interval width
is 0.30 rather than greater than 0.40, it does not touch the search boundary, and all
planned realizations completed. Phase 2 may therefore proceed to the N=192 resource
measurement and refined-grid scaling run. The observed seed sensitivity must be
propagated through the preregistered bootstrap scaling analysis and discussed as a
limitation; it must not be hidden by selecting the earlier or later point estimate.
