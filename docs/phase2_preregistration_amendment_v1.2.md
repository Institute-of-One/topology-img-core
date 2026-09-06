# IORN-010 Phase 2 preregistration amendment v1.2

Date: 2026-09-06

This amendment is frozen after the five-run seed-sensitivity experiment defined in
v1.1 and before any boundary-extension data are generated.

## Trigger

The primary heterogeneity test supported adequacy of within-run uncertainty (Q-test
p=0.529, estimated tau=0), but two of five run-level 95% intervals touched the
allowed knot-search lower boundary sigma=1.00. The v1.1 inconclusive condition was
therefore triggered even though the heterogeneity decision itself passed.

No run or seed is removed or replaced. All completed measurements remain part of the
analysis.

## Frozen minimal boundary extension

For each of the five registered root seeds (20260906, 20260916, 20260926, 20261006,
20261016), add 64 paired realizations at sigma=0.80 and 64 at sigma=0.90 using new,
deterministic seed branches derived from the root seed and labels `extension-0.80`
and `extension-0.90`. These random streams must be independent of all existing
streams and reproducible from the recorded root seed and label.

The breakpoint candidate grid becomes sigma=0.80, 0.90, 1.00, ..., 2.50. Existing
data at all other sigma values are reused unchanged. The regression equation,
normalization, 500 within-run bootstraps, Q test, DerSimonian-Laird estimator,
heterogeneity alpha=0.05, material tau threshold=0.10, and 10,000 run-level
bootstrap are unchanged.

## Decision after extension

The seed-sensitivity study becomes conclusive if at least four of five extended runs
complete, no run's 95% breakpoint interval touches the new lower boundary 0.80 or
upper boundary 2.50, no interval width exceeds 0.40, and no more than 5% of planned
extension realizations are missing or nonfinite.

If a breakpoint interval touches 0.80 after this extension, no further adaptive grid
extension is allowed in Phase 2. Seed sensitivity is then reported as unresolved and
N=192/256 scaling is paused pending a separately designed study.

The v1.1 heterogeneity decision rule remains authoritative:

- if Q p is at least 0.05 and tau is no greater than 0.10, the current within-run
  uncertainty definition is adequate;
- otherwise a further preregistration amendment must define multiple seeds per
  matrix size before scaling data are generated.
