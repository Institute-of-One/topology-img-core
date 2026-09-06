# IORN-010 Phase 2 resource-gate supplement

Date: 2026-09-06

This supplement is frozen before refined-grid measurements at N=64, 96, or 192
and before any resource measurement at N=192. It does not alter an observed
topology result. It fixes how computational cost will be extrapolated and how a
failed N=256 resource gate will be handled without inspecting substitute-size
topology outcomes.

## 1. Resource limits and their operational basis

The v1.0 limits remain 12 hours of extrapolated wall time and 16 GiB of
extrapolated peak resident memory for the complete N=256 condition. These are
machine-operational constraints, not thresholds derived from topology results:
the workstation has 31.87 GiB of physical RAM, so the 16 GiB ceiling reserves
approximately half of physical memory for the operating system and other work,
and 12 hours is the maximum acceptable uninterrupted run window on this shared
interactive workstation.

Neither limit may be changed after examining N=192 resource measurements or any
scaling topology result.

## 2. Frozen cost model

The complete refined-grid conditions at N=64, 96, 128, and 192 provide four
pre-specified calibration points. For each resource quantity C separately, fit

`C(N) = c N^alpha`,

equivalently by ordinary least squares of `log C` on `log N`. Wall time and peak
resident memory are modeled independently, producing separate exponents and
coefficients. The observed complete-condition wall time and peak resident memory
at all four sizes are used; no point is omitted or reweighted after inspection.

The fitted models are used to extrapolate the complete-condition resource costs
at N=256, 224, and 160. No alternative functional form, subset of sizes, robust
fit, or topology-dependent adjustment may replace this primary extrapolation
after the N=192 measurements are seen. Observed-to-fitted residuals and the fitted
exponents are reported with the gate decision.

The N=128 calibration value is the completed refined-grid run. N=64 and N=96 are
remeasured on the v1.0 refined grid before entering the cost fit. N=192 is the
complete refined-grid resource measurement specified by v1.0. Timing boundaries
and peak-memory instrumentation must be identical across all four calibration
sizes and documented before the first new calibration run.

## 3. Gate and substitute-size decision tree

1. If extrapolated N=256 wall time is at most 12 hours and extrapolated peak
   resident memory is at most 16 GiB, retain the registered five-size series
   N=64, 96, 128, 192, and 256.
2. If either N=256 limit is exceeded, do not reduce the primary analysis to four
   sizes. Before generating any substitute-size data, freeze amendment v1.3 with
   the measured calibration values, fitted cost model, failed gate, and selected
   substitute size.
3. Prefer N=224 if its extrapolated wall time and memory satisfy both limits.
   Otherwise use N=160 if it satisfies both limits. If neither substitute is
   feasible, the primary scaling analysis is reported as resource-inconclusive.

The selection uses resource extrapolations only. Inspecting topology values,
breakpoints, confidence intervals, AICc values, fitted scaling parameters, or any
other scientific outcome at N=224 or N=160 before choosing the substitute is
prohibited. Pilot topology runs at candidate substitute sizes are likewise
prohibited.

## 4. Inferential limitation of substitution

A fifth size restores finite AICc calculations for the registered models, but it
does not guarantee that Rule B can be satisfied. Relative to the N=64 endpoint,
the natural-log size ranges are approximately 1.39 for N=256, 1.25 for N=224,
and 0.92 for N=160. Thus N=224 retains nearly the registered logarithmic leverage,
whereas N=160 shortens it to about two thirds of the N=256 range.

Amendment v1.3, if triggered, must state prospectively that N=160 makes the models
evaluable but is expected to estimate omega less precisely; its bootstrap interval
may therefore include zero and fail Rule B even when AICc is computable. This
limitation is fixed here before resource or topology outcomes are examined and
must be carried into the final interpretation.
