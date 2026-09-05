# IORN-010 Phase-0 findings

## Experiment completed

The preregistered-style Phase-0 sweep used 100 logarithmically spaced noise levels
(σ=0.25–20), 256 paired observer realizations per level, and 16 paired topology
realizations per level. The signal was a centered Gaussian lesion (peak amplitude 1,
width 5 px) on a 128×128 field. Raw and aggregate values are saved under
`results/data/`.

## 1. Detectability

The ideal-observer prediction behaved as expected: d′ was proportional to 1/σ. The
Monte Carlo matched-filter estimate had 4.23% relative RMSE against the analytic
curve. The operational d′=1 threshold was σ_task=8.866.

## 2. Topology metric behavior

Raw persistence distances inherit image-intensity units, so unnormalized bottleneck
distance increased with σ and is not a valid topology-vs-detectability comparison.
After the required scale normalization, paired H0 and H1 bottleneck distances were
the clearest and most monotonic candidates:

- H0 bottleneck/σ versus d′: Spearman ρ=0.9944 (bootstrap 95% CI 0.9875–0.9959).
- H1 bottleneck/σ versus d′: Spearman ρ=0.9958 (bootstrap 95% CI 0.9903–0.9974).

Entropy differences were monotonic but extremely small in absolute dynamic range
(H0≈0.0030, H1≈0.0011), making them less convincing as practical order parameters.
Thresholded feature counts were discrete and less strongly associated (H0 ρ≈0.788,
H1 ρ≈0.625). H1 maximum-persistence change was effectively unrelated to d′
(ρ≈0.042, p≈0.68). Total-persistence and landscape-norm deltas had strong trends but
their sign and aggregation over many noise features make interpretation less direct.

## 3. Relationship between topology and detectability

There is a reproducible, nontrivial monotonic relationship in this controlled model:
dimensionless paired diagram distance decreases as ideal-observer detectability
decreases. This result is not an artifact of noise-only topology because each
signal-present diagram is compared with a signal-absent diagram having the identical
noise field.

The characteristic locations do not coincide. For the primary H0 bottleneck/σ curve:

- half-maximum location: σ≈0.710;
- segmented-regression breakpoint: σ≈1.604;
- bootstrap 95% breakpoint interval: σ=1.468–1.753;
- 10%-of-maximum location: σ≈4.242;
- task threshold d′=1: σ≈8.866.

Thus the paired topological lesion signature weakens substantially before the task
information reaches the chosen operational loss threshold.

## 4. Phase-transition assessment

There is no credible evidence yet for a topological phase transition. A continuous
one-break segmented curve fits better than a single straight line in log σ for the
primary metric (ΔAIC, piecewise minus linear, ≈−257), and the fitted bend is
reproducible under realization bootstrap. This establishes nonlinearity, not a phase
transition. Phase-transition claims additionally require finite-size effects,
scaling, and reproducibility or universality under controlled changes; none were
tested in Phase 0. The current language should remain “nonlinear topological
crossover” or “candidate transition region.”

## 5. Recommended next experiment

Do not expand to correlated noise or reconstruction physics yet. First run a focused
finite-size/lesion-size replication around σ≈0.7–4.3 while preserving the full σ
range as anchors. Use at least three matrix sizes and three lesion widths, increase
topology realizations from 16 to at least 64 near the candidate region, and test
whether curves collapse after physically justified normalization. Also compare the
paired-image result with a distribution-level two-sample diagram distance using
independent signal-present and signal-absent ensembles. This directly tests whether
the breakpoint shifts with size and whether the strong pairing result generalizes.

## Limitations

The topology Monte Carlo sample is adequate for an initial curve and bootstrap but
not for a definitive critical-point estimate. Paired bottleneck distance measures the
incremental lesion effect for identical noise; it is not itself a distance between
the two ensemble distributions. The segmented model searched over candidate knots,
so its AIC improvement should be treated as exploratory. No multiplicity correction
was applied across secondary topology metrics.
