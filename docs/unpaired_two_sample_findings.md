# Phase 2 §4.1 unpaired two-sample findings

## Frozen design

The analysis followed `phase2_preregistration_v1.0.md` without changing the
filtration, normalization, persistence-image representation, sample size, test
statistic, permutation count, FDR rule, or decision thresholds. At each of the 100
noise levels, 64 signal-present and 64 signal-absent images were generated from
disjoint random streams. No image pair shared a noise realization.

## Primary result

The unpaired persistence-image energy distance retained a strong positive monotonic
association with analytic detectability:

- Spearman rho: 0.8409;
- 95% bootstrap interval: 0.7508 to 0.8973;
- two-sided association p-value: 7.02e-28.

After Benjamini-Hochberg correction over all 100 noise levels:

- 60% of levels with analytic d-prime at least 2 were significant;
- 0% of levels with analytic d-prime at most 0.5 were significant.

All three preregistered survival criteria were met. The paired association therefore
survives independent-ensemble validation.

## Interpretation

The earlier rho of approximately 0.994 was strengthened by sharing the noise field,
but it was not created by that pairing. Removing the pairing reduced the association
to rho approximately 0.841 and produced considerable pointwise variability around
the crossover region. This distinction changes the paper framing: persistent
homology contains an ensemble-level lesion signal related to detectability, while
the near-deterministic paired curve overstates the strength available in an
observer-realistic unpaired setting.

The low-detectability negative control behaved correctly: no noise level with
d-prime at most 0.5 survived FDR. Isolated small uncorrected p-values at high noise
were removed by the family-wise analysis and were not interpreted as signal.

This experiment does not establish a phase transition or universality. It validates
that the signal/noise topological distinction is not merely a paired-noise artifact
and clears the preregistered programme to proceed to refined-grid breakpoint
measurement before larger matrices.

## Reproducibility

The result consists of 100 compressed per-sigma feature checkpoints, the complete
scalar result table, analysis JSON, metadata containing the frozen commit hash and
configuration digest, and Figure I. Total stored size is approximately 20.2 MB.
Every sigma level completed with both groups of 64, so no inconclusive condition was
triggered.
