# Phase 2 resource-gate findings

Date: 2026-09-06

The gate used the model frozen in resource-gate commit
`6739705fb5e4238d8c08a442cc7f498a65d7a285`: separate ordinary least-squares
fits of log cost on log N at N=64, 96, 128, and 192. No calibration point was
omitted or reweighted and no alternative cost model was examined.

## Fitted resource models

- Wall time: coefficient=0.00164970 and alpha=2.50739.
- Peak RSS: coefficient=45,171,009 bytes and alpha=0.123530.

The N=256 predictions are 1,802.17 seconds (0.5006 hours) and 89,608,365 bytes
(0.08345 GiB). Both are far below the frozen limits of 12 hours and 16 GiB.
Observed-to-fitted log residuals are saved in `results/resource_gate/calibration.csv`.

## Decision

The N=256 resource gate passes and the registered fifth size remains N=256.
Neither N=224 nor N=160 is selected. The conditional resource-substitution
amendment v1.3 is not triggered and is not created. No topology result at a
candidate substitute size was generated or inspected.
