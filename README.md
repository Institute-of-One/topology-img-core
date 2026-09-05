# IORN-010 — A Topological Phase Transition in Medical Image Detectability

Minimal, preregistered-style Phase-0 proof of concept. A fixed Gaussian lesion is
embedded in a 128×128 uniform field and degraded only by additive white Gaussian
noise. Detectability and image topology are evaluated without tuning metrics to
force agreement.

## Reproduce

```powershell
python -m pip install -e .
python experiments/poc_noise_sweep.py --config configs/poc_noise_sweep.toml
python experiments/plot_saved_results.py --results results/data/poc_noise_sweep.csv
```

The simulation writes raw per-realization data, aggregated data, metadata, figures,
and a machine-generated report under `results/`. Figures are generated only from
saved numerical data. Random streams use NumPy `SeedSequence`; the root seed and
derived configuration are recorded in the metadata.

The focused follow-up finite-size replication is configured separately and resumes
from per-condition checkpoints:

```powershell
python experiments/finite_size_replication.py --config configs/finite_size_replication.toml
```

## Scope and interpretation

This repository currently implements Phase 0 only. The ideal prewhitening observer
is appropriate because the signal and location are known exactly and the noise is
white Gaussian. Topology uses a superlevel cubical filtration (`-image`) with GUDHI,
reported separately for H0 and H1. Infinite essential classes are excluded from
finite persistence summaries. The paired signal/noise diagrams share the same noise
realization, isolating the lesion's incremental topological effect.

Because filtration coordinates inherit image-intensity units, primary comparisons
use dimensionless metrics: bottleneck, total persistence, and maximum persistence
are divided by σ; the landscape L2 surrogate is divided by σ^(3/2). Raw dimensional
metrics remain saved to make this normalization auditable.

An apparent bend is not called a phase transition. The analysis compares smooth and
segmented curve fits and estimates bootstrap uncertainty in any breakpoint. Evidence
for scaling, finite-size behavior, and universality is outside Phase 0 and therefore
cannot be claimed here.
