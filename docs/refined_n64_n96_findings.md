# Refined-grid N=64 and N=96 interim findings

Date: 2026-09-06

These measurements were generated from code commit
`ae0104688ae95fbffb9d681f9c26ee2d479cb7f3` under Phase 2 preregistration v1.0
and the resource-gate supplement. Each size used the registered lesion width of
5 px, the sigma grid 1.00--2.50 in 0.10 increments with registered anchors, 64
paired realizations per dense point, 16 per anchor, and 500 breakpoint bootstrap
replicates.

## Results

- N=64: breakpoint sigma=1.60, 95% bootstrap interval 1.40--1.70,
  d-prime at breakpoint=5.5389, interval width=0.30, wall time=52.97 s, and
  peak RSS=0.0711 GiB.
- N=96: breakpoint sigma=1.20, 95% bootstrap interval 1.00--1.60,
  d-prime at breakpoint=7.3852, interval width=0.60, wall time=136.11 s, and
  peak RSS=0.0726 GiB.

Both conditions completed all 1,104 planned paired realizations. Piecewise fits
were favored over linear fits (delta AIC=-56.74 at N=64 and -42.14 at N=96).

## Preregistered decision check

N=64 does not trigger the v1.0 breakpoint-interval inconclusive condition. N=96
triggers it in two ways: its interval touches the allowed lower knot-search
boundary sigma=1.00, and its width 0.60 exceeds the maximum allowed width 0.40.

No N=192 data are generated while this trigger is unresolved. Existing N=96 data
will not be removed, replaced, or selectively filtered. Any boundary extension or
additional-realization rule must be frozen in a prospective amendment before new
N=96 data are generated.
