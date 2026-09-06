# IORN-010 Phase 2 scaling-precision amendment v1.0

Date: 2026-09-06

This amendment is frozen after the registered N=64 and N=96 refined-grid data
commit `83b89141b87ef2d417211c9e55ff15acef9a84bc` and before any scaling-precision
extension data or N=192 data are generated. It does not alter, remove, or replace
the completed measurements.

## Trigger

N=64 completed with breakpoint sigma=1.60 and 95% bootstrap interval 1.40--1.70.
N=96 completed with breakpoint sigma=1.20 and interval 1.00--1.60. The N=96
interval touched the registered lower knot-search boundary 1.00 and had width
0.60, exceeding the v1.0 maximum of 0.40. The preregistered scaling inconclusive
condition therefore triggered before N=192 data generation.

## Uniform lower-boundary extension

For the primary scaling series, the dense sigma grid and allowed breakpoint
candidate grid become 0.80, 0.90, 1.00, ..., 2.50 at every matrix size. The
anchors 0.50, 0.75, 3.00, 4.00, and 8.00 are unchanged.

- At N=64, add 64 paired realizations at sigma=0.80 and 64 at sigma=0.90.
- At N=96, generate 128 paired realizations at sigma=0.80 and 128 at sigma=0.90.
- At N=128, reuse the 64-pair sigma=0.80 and 0.90 extension for root seed
  20260906 that was generated prospectively under amendment v1.2. No other
  seed-sensitivity run enters the primary N=128 scaling estimate.
- At N=192 and the resource-approved fifth size, include 64 paired realizations
  at sigma=0.80 and 64 at sigma=0.90 in the initial run.

The uniform candidate range prevents matrix size from determining the allowed
breakpoint support.

## N=96 precision extension

At each existing dense point sigma=1.00, 1.10, ..., 2.50, add 64 new paired
realizations to the existing 64, giving 128 total paired realizations at every
N=96 dense point from 0.80 through 2.50. Existing anchors remain at 16 pairs.

All added N=96 streams are derived deterministically from root seed 20261096 and
labels containing `scaling-precision-extension`, the sigma value, and replicate
index. They are independent of the original streams. Existing observations are
retained exactly and pooled without filtering. N=64 extension streams use the
same labeling rule with root seed 20261064.

The segmented-regression equation, topology metric, normalization, analytic
d-prime, and 500 within-size bootstrap replicates remain unchanged. Bootstrap
resampling occurs within each sigma level over the full pooled group.

## Frozen decision after extension

N=96 is adequate to continue to N=192 only if all of the following hold:

1. all planned extension realizations are finite and complete;
2. its 95% breakpoint interval touches neither 0.80 nor 2.50; and
3. its 95% breakpoint interval width is no more than 0.40.

If any condition fails, no further adaptive grid extension, realization increase,
seed replacement, or breakpoint-method change is allowed in Phase 2. The primary
scaling experiment is reported as inconclusive and N=192 is not generated.

The N=64 interval is recomputed on the extended uniform grid but does not receive
a precision-driven realization increase because its registered interval already
passed v1.0. If its recomputed interval newly touches 0.80 or exceeds width 0.40,
the same inconclusive stop applies.

This amendment is distinct from the conditionally planned resource-substitution
amendment v1.3. The latter is created only if the N=256 resource gate fails and
before any substitute-size data are generated.
