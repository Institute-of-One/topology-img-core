# IORN-010 Phase 2 preregistration amendment v1.1

Date: 2026-09-06

This amendment is frozen after completion of the first refined-grid run and before
generation of any seed-sensitivity data. It does not replace v1.0. It inserts a
measurement of ensemble-seed heterogeneity before the N=192 and N=256 scaling runs.

## Reason for amendment

Two independent measurements at the fixed 128 by 128, lesion-width 5 px condition
gave breakpoint estimates of 1.60 (reanalysis interval approximately 1.42 to 2.00)
and 1.30 (refined-grid interval 1.20 to 1.50). The intervals have only marginal
overlap. Existing bootstrap intervals resample realizations within one run and do not
measure variation between independently seeded ensembles. If between-run variation
exceeds within-run uncertainty, a one-run-per-size scaling analysis would confound
matrix-size effects with ensemble realization.

## Frozen experiment

The image model, H0 bottleneck divided by sigma, filtration, breakpoint regression,
refined sigma grid, anchors, and realization counts remain exactly those in
`configs/refined_sigma_grid.toml` and preregistration v1.0.

The completed root seed 20260906 is retained. Four additional complete refined-grid
runs use root seeds 20260916, 20260926, 20261006, and 20261016. The five-run set is
the primary seed-sensitivity dataset. The older coarse-grid run is reported as
historical replication but is not included in the primary five-run variance estimate.

Each new run contains 64 paired realizations at every dense sigma from 1.00 through
2.50 in increments of 0.10 and 16 paired realizations at anchors 0.50, 0.75, 3.00,
4.00, and 8.00. Each run uses 500 within-run bootstrap replicates.

## Frozen heterogeneity analysis

For run i, let theta_i be its breakpoint and let v_i be the sample variance of its
500 bootstrap breakpoint draws. Let the inverse-variance fixed-effect estimate be

`theta_FE = sum(w_i theta_i) / sum(w_i)`, where `w_i = 1 / v_i`.

Cochran's Q is

`Q = sum[w_i (theta_i - theta_FE)^2]`

and is compared with a chi-squared distribution with four degrees of freedom.
Between-run variance is estimated by the DerSimonian-Laird estimator

`tau^2 = max(0, (Q - 4) / (sum(w_i) - sum(w_i^2)/sum(w_i)))`.

The random-effects pooled breakpoint uses weights `1 / (v_i + tau^2)`. Its 95%
interval is the normal interval from the inverse summed random-effects weight. A
nonparametric run-level bootstrap (10,000 resamples of the five runs, including each
selected run's within-run bootstrap draw) is also saved as a sensitivity interval;
it does not replace the primary random-effects interval.

Report additionally the observed standard deviation and range of the five theta_i,
the square root of mean v_i as the typical within-run standard error, I-squared
`max(0, (Q-4)/Q)`, and the ratio of observed between-run SD to typical within-run SE.

## Decision rule

The current within-run uncertainty definition is considered adequate only if both:

1. the Q-test p-value is at least 0.05; and
2. estimated tau is no greater than one refined grid step, 0.10 in sigma.

If either condition fails, between-run heterogeneity is declared material. Before
N=192 data are generated, preregistration must then be amended again so that every
size uses multiple independent root seeds and scaling uncertainty is based on a
hierarchical or random-effects analysis including both variance components.

If both conditions pass, the v1.0 one-run-per-size plan may proceed, while the
measured seed variance is still propagated as a sensitivity analysis.

## Inconclusive conditions

The seed-sensitivity experiment is inconclusive if fewer than four of the five total
runs complete, more than 5% of planned realizations are missing or nonfinite, any
run's breakpoint interval touches the allowed knot-search boundary, or at least one
run has breakpoint interval width greater than 0.40 in sigma.

No seed may be replaced because its result appears atypical. A failed run may be
restarted only from its deterministic checkpoints with the same root seed.
