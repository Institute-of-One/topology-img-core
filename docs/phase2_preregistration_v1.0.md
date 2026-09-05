# IORN-010 Phase 2 preregistration v1.0

Frozen before any Phase-2 data are generated. The freeze commit must contain this
document and no Phase-2 experiment code or data. All thresholds below are fixed
before examining Phase-2 outcomes.

## 1. Scientific question and declared consequences

Does the reproducible nonlinear topological crossover converge under increasing
matrix size, and does its location become a universal function of task detectability?

The possible outcomes and their consequences are fixed as follows:

1. If the breakpoint and d′ at the breakpoint converge, the result supports a
   topological order parameter for detectability in this controlled model.
2. If the breakpoint converges in noise σ but d′ at the breakpoint continues to
   drift, the result establishes a reproducible topological boundary that is not a
   function of task detectability.
3. If neither quantity can be shown to converge over the reachable sizes, the result
   is reported as nonconvergence over the tested range, subject to the inconclusive
   conditions below.

No result will be relabelled by adding metrics, changing filtration, or changing
normalization after data inspection.

## 2. Frozen image model and topology

- Uniform 2D background; centered Gaussian lesion.
- Lesion peak amplitude: 1.0.
- Primary scaling experiment lesion width: 5.0 px.
- Independent white Gaussian pixel noise with standard deviation σ.
- Superlevel cubical filtration of `-image`, coefficient field 2.
- Finite H0 and H1 classes; essential classes excluded.
- Primary topology curve: mean paired H0 bottleneck distance divided by σ.
- H1 bottleneck/σ is secondary and cannot reverse the primary conclusion.
- No correlated noise, blur, reconstruction filtering, new topology metric,
  filtration tuning, or alternative normalization is allowed in Phase 2.

## 3. Primary order parameter and breakpoint

For matrix side length N, let T_N(σ) be the realization mean of paired H0 bottleneck
distance divided by σ and normalized to its maximum over the frozen σ grid. A
continuous one-knot segmented regression is fit to T_N against log σ:

`T_N(σ) = β0 + β1 log(σ) + β2 max[log(σ) - log(σc,N), 0] + ε`.

The knot σc,N minimizes residual sum of squares over allowed interior grid points.
The primary order parameter is

`q_N = d′(σc,N) = ||s||₂ / σc,N`.

The breakpoint in σ, σc,N, is a co-primary diagnostic needed to distinguish outcome
2 from outcomes 1 and 3. Bootstrap intervals resample realizations independently
within each σ level. Five hundred bootstrap replicates are used.

## 4. Scaling models

The following models are fit separately to `q_N` and `σc,N`:

- Constant/universal: `y(N) = c` (one free parameter).
- Convergent finite-size correction: `y(N) = y∞ + a N^(-ω)`, with free parameters
  `y∞`, `a`, and `ω`, constrained to `ω > 0`.
- Nonconvergent log drift: `y(N) = b0 + b1 log(N)`, with two free parameters.

Fits use bootstrap-weighted nonlinear least squares. Model comparison uses AICc.
Uncertainty is obtained by propagating the within-size breakpoint bootstrap samples
through 2,000 scaling-fit bootstrap replicates.

## 5. Frozen convergence decision rule

A quantity is called converged if either rule A or rule B is satisfied:

- Rule A (constant): the constant model has the lowest AICc or is within 2 AICc
  units of the lowest model, and the largest-minus-smallest fitted value over
  N=128,192,256 is no more than 10% of the constant estimate.
- Rule B (finite-size limit): the convergent model beats the log-drift model by at
  least 6 AICc units; the 95% bootstrap interval for ω lies wholly above zero; the
  95% interval width of y∞ is no more than 20% of |y∞|; and the absolute correction
  `|a 256^(-ω)|` is no more than 10% of |y∞|.

Outcome assignment:

- Outcome 1: both σc,N and q_N converge.
- Outcome 2: σc,N converges and q_N does not converge, provided the run is not
  inconclusive.
- Outcome 3: σc,N does not converge, provided the run is not inconclusive.

Failure to meet a convergence rule is evidence of nonconvergence only within the
tested N range; it is not proof that no asymptotic limit exists.

## 6. Matrix sizes, σ grid, and realizations

The scaling series is N = 64, 96, 128, 192, and 256. Existing 64/96/128 data may be
used only after the refined-grid measurement below is completed for the same model;
coarse-grid breakpoint estimates are descriptive, not inputs to the primary fit.

The refined σ grid is fixed at 0.10 increments from 1.00 through 2.50 inclusive,
with anchor points 0.50, 0.75, 3.00, 4.00, and 8.00. The dense interval 1.00–2.50
uses 64 paired realizations per σ. Anchors use 16 paired realizations per σ.

Before the 256 run, wall time and peak resident memory are measured for the complete
192 condition. The 256 condition proceeds if extrapolated wall time is at most 12
hours and extrapolated peak resident memory is at most 16 GiB. Otherwise N=192 is
declared the reachable limit and the primary scaling result is inconclusive, not
negative.

## 7. Unpaired two-sample validation (performed first)

This validation uses the original condition N=128, lesion width 5 px, and the 100 σ
values in `configs/poc_noise_sweep.toml`. At every σ, generate 64 independent
signal-present images and 64 independent signal-absent images from disjoint random
streams. No noise field is shared across groups.

Each H0 persistence diagram is transformed into a persistence image on fixed
birth/persistence coordinates after dividing filtration coordinates by σ. Bounds are
fixed globally to birth/σ in [-5, 5] and persistence/σ in [0, 8], using a 32×32 grid,
Gaussian bandwidth 0.15, and linear persistence weighting. Values outside the bounds
are clipped to the boundary. The two-sample statistic is the unbiased energy distance
between the resulting vectors using Euclidean ground distance. Statistical evidence
uses 999 label permutations independently at each σ; Benjamini-Hochberg FDR is fixed
at q=0.05 over the 100 σ tests.

The unpaired topology curve U(σ) is the nonnegative sample energy distance. Its
association with analytic d′ is summarized by Spearman ρ with a 2,000-replicate
bootstrap interval over σ levels. The paired association is considered to survive
unpaired validation if all three conditions hold:

1. Spearman ρ is positive and its 95% bootstrap interval excludes zero;
2. at least 50% of σ levels with analytic d′ >= 2 are significant after FDR; and
3. no more than 10% of σ levels with analytic d′ <= 0.5 are significant after FDR.

If these criteria fail, the paired association is reported as pairing-dependent.
No alternative persistence-image resolution, bandwidth, bounds, weight, test
statistic, or significance threshold will replace this primary analysis. Sensitivity
analysis, if later justified, must be labelled secondary.

## 8. Inconclusive conditions

The scaling run is inconclusive if any of the following occurs:

- fewer than three refined-grid matrix sizes are completed, including at least one
  of N=192 or N=256;
- more than 5% of planned realizations are missing or nonfinite;
- at any N, the 95% breakpoint interval spans more than 0.40 in σ or touches an
  allowed knot-search boundary;
- the 256 resource gate fails and the remaining sizes cannot distinguish the
  constant, convergent, and log-drift models by at least 6 AICc units;
- numerical optimization fails in more than 5% of scaling bootstrap replicates.

The unpaired validation is inconclusive if more than 5% of images or diagrams fail,
or if fewer than 95 of the 100 planned σ levels have complete groups of 64.

## 9. Reproducibility and commit-order requirement

Randomness uses NumPy `SeedSequence` with root seeds recorded in machine-readable
configuration and metadata. Raw numerical outputs are saved before plotting. Figures
are generated only from saved outputs. Each condition is checkpointed atomically.

This file is committed alone. Phase-2 experiment code, tests, configurations, and
data appear only in later commits. The repository test must verify:

`git merge-base --is-ancestor <freeze_commit> <first_phase2_data_commit>`.

CI must use complete history (`actions/checkout` with `fetch-depth: 0`) so this check
is meaningful.
