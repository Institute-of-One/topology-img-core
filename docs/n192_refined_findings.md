# Refined-grid N=192 findings and resource measurement

Date: 2026-09-06

The N=192 condition was generated after the scaling-precision amendment and used
the amended uniform dense grid sigma=0.80--2.50, 64 paired realizations per dense
point, the five registered anchors with 16 pairs each, and 500 breakpoint
bootstrap replicates. All 1,232 planned pairs completed.

## Scientific result

The H0 breakpoint is sigma=1.20 with 95% bootstrap interval 1.00--1.30 and
d-prime at the breakpoint=7.3852. The interval width is 0.30 and it touches
neither allowed candidate boundary 0.80 nor 2.50. The preregistered within-size
continuation conditions therefore pass. This result is not yet a scaling-model
conclusion.

## Resource result

Under the frozen measurement boundary, the complete N=192 condition required
890.67 seconds (14.84 minutes) and peak RSS was 0.0820 GiB. Clean standard-load
resource calibrations using the same 23 sigma levels and 1,232 pairs gave:

- N=64: 56.48 seconds and 0.0716 GiB;
- N=96: 152.83 seconds and 0.0726 GiB;
- N=128: 310.21 seconds and 0.0752 GiB;
- N=192: 890.67 seconds and 0.0820 GiB.

The N=64/96/128 calibration-output topology estimates are resource-benchmark
byproducts and are excluded from all scientific scaling analyses. The registered
N=64, N=96, and N=128 scientific estimates remain authoritative.

The resource-gate decision is deferred to the separately implemented frozen
log-log ordinary-least-squares power-law extrapolation. No fifth-size topology
data have been generated.
