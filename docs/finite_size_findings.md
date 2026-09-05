# Finite-size and lesion-size replication findings

## Design

This focused replication followed Phase 0 without adding correlated noise, blur, or
reconstruction physics. It crossed matrix sizes 64, 96, and 128 with Gaussian lesion
widths 3, 5, and 7 px. Seventeen noise levels covered σ=0.25–20. The candidate region
σ=0.5–5 used 64 paired topology realizations per point; anchors used 16. In total,
7,200 paired signal-present/signal-absent realizations were analyzed. All 14,400
images used the same superlevel cubical filtration and normalized H0/H1 bottleneck
definitions as Phase 0.

## Reproduction of the original condition

For matrix 128 and lesion σ=5 px, the new H0 breakpoint was σ=1.60 with bootstrap
95% interval 1.60–2.00. The original Phase-0 estimate was σ=1.604 with interval
1.468–1.753. The point estimates agree and the intervals overlap at σ=1.60, despite
independent random seeds and four times as many topology realizations in the dense
region. The nonlinear crossover is therefore reproducible for the original model.

## Dependence on matrix and lesion size

Candidate H0 breakpoints varied from σ=1.25 to 2.50 across the nine conditions.
Breakpoints generally moved to higher σ for larger lesions at fixed matrix size and
to lower σ for larger matrices at fixed lesion width. The fitted breakpoint d′ was
not invariant: it ranged from 3.32 to 7.75.

| Matrix | Lesion σ | Breakpoint σ | Bootstrap 95% interval | d′ at breakpoint |
|---:|---:|---:|---:|---:|
| 64 | 3 | 1.60 | 1.25–1.60 | 3.32 |
| 64 | 5 | 2.00 | 1.60–2.00 | 4.43 |
| 64 | 7 | 2.50 | 2.00–2.50 | 4.96 |
| 96 | 3 | 1.25 | 1.25–1.60 | 4.25 |
| 96 | 5 | 2.00 | 1.60–2.00 | 4.43 |
| 96 | 7 | 2.00 | 1.60–2.00 | 6.20 |
| 128 | 3 | 1.25 | 1.00–1.25 | 4.25 |
| 128 | 5 | 1.60 | 1.60–2.00 | 5.54 |
| 128 | 7 | 1.60 | 1.60–2.00 | 7.75 |

Breakpoint resolution is limited by the discrete σ grid, so interval endpoints are
quantized and should not be read as high-precision critical parameters.

## Curve-collapse test

After normalizing each H0 topology curve to its own maximum, the mean pointwise
between-condition standard deviation was:

- 0.0371 on the noise-σ axis;
- 0.0747 on the ideal-observer-d′ axis.

Thus collapse on σ was approximately twice as good as collapse on d′. The topology
curve is not a universal function of conventional detectability in this experiment.
The result instead suggests that the topological crossover depends on image/noise
scale and lesion geometry in a way not captured by d′ alone.

## Phase-transition assessment

All nine segmented fits favored a one-break curve over a single linear-in-log-σ
model (ΔAIC from −26.3 to −54.4). This confirms reproducible nonlinearity. It does
not establish a phase transition: the candidate point shifts with finite matrix and
lesion size, d′ at the point is non-universal, no asymptotic scaling law was tested,
and the largest matrix was only 128.

The strongest defensible conclusion is:

> A reproducible nonlinear topological crossover accompanies loss of detectability,
> but its location is condition-dependent and does not collapse universally onto d′.

## Recommended next experiment

The next experiment should isolate the two observed dependencies rather than add new
physics. Hold lesion σ=5 px and extend matrix size to 192 and 256 with a refined σ
grid around 1.0–2.5; separately hold matrix size at 128 and sample lesion widths more
densely. Fit an explicit finite-size scaling model and test whether the breakpoint
approaches a limit. Only after that result should correlated noise be introduced.

