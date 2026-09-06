# Scaling-precision extension findings

Date: 2026-09-06

The extension was generated after freeze commit
`cc961f9be19ad557aaaf09c7596c4fd3989aead2` and implementation commit
`8d598161c70b96f697475adf94b680f2a49b35c4`. All original N=64 and N=96
observations were retained without filtering.

## N=64 uniform-grid check

Adding 64 paired realizations at each of sigma=0.80 and 0.90 left the estimate
unchanged: breakpoint sigma=1.60, 95% interval 1.40--1.70, width=0.30, and
d-prime at the breakpoint=5.5389. The interval does not touch the amended
candidate boundaries and the frozen adequacy rule passes.

## N=96 precision check

The extension added 128 paired realizations at sigma=0.80 and 0.90 and 64 new
pairs at each existing dense point from 1.00 through 2.50. The dense points now
contain 128 pairs each; existing anchors remain at 16 pairs. The pooled result is
breakpoint sigma=1.20, 95% interval 1.00--1.40, width=0.40, and d-prime at the
breakpoint=7.3852.

The interval no longer touches the lower candidate boundary 0.80 and its width
meets, but does not improve beyond, the maximum permitted width of 0.40. The
prospectively frozen continuation rule therefore passes. This is a boundary-case
pass and must not be described as high-precision localization.

## Decision

All planned extension realizations completed and were finite. Neither N=64 nor
N=96 triggers the amended stop rule. N=192 data generation may proceed. No
additional adaptive N=64 or N=96 data are allowed in Phase 2.
