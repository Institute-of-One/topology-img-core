# IORN-010 — a completed preregistered study, published as a record rather than a paper

A preregistered study of how the persistent homology of a noisy image relates to task
detectability. It is finished. Its registered question has an answer, and the answer is
negative.

**This repository is the publication.** There is no manuscript and there will not be one
unless the work resumes. What follows says what was asked, what was found, and why the
finding is public while no paper was written — because those are three different things and
running them together is how publication bias is made.

## What was asked

A fixed Gaussian lesion in a uniform field, degraded only by additive white Gaussian noise —
no anatomy, no blur, no correlated noise, no reconstruction physics. Detectability comes
from an ideal prewhitening observer; topology from a superlevel cubical filtration with H0
and H1 reported separately. As noise rises, detectability is lost. Does the topology change
with it in a way that is reproducible, and does its location converge as the image grows?

## What was found

**A nonlinear topological crossover accompanies detectability loss, and it reproduces.** For
matrix 128 with lesion sigma 5 px the H0 breakpoint recurred at sigma = 1.60 against an
original estimate of 1.604, on independent seeds and four times the realizations.

**Its location does not converge.** Across matrix sizes 64, 96, 128, 192 and 256 the
breakpoint moved and the breakpoint d′ ranged from 3.32 to 7.75. The preregistered
classification is **Outcome 3: nonconvergence over the reachable range**.

There is no credible evidence here for a critical phase transition or a universal
detectability threshold. The registered hypothesis is not supported.

## Why this is public

The finding is negative and it is complete. Outcome 3 was one of three results named in the
preregistration before any data existed, so reaching it is an answer, not a failure.

**The preregistration is verifiable rather than asserted.** The freeze commit precedes the
first data commit, and `tests/test_preregistration_order.py` asserts in continuous
integration that the freeze is an ancestor of the data. The registered design cannot have
been written after the data it governs, and anyone can check that rather than take it on
trust.

Everything is here: the hypothesis, the frozen protocol and its two amendments, every result
file, the analysis code, the figures, and the outcome assignment.

## Why there is no manuscript, which is a separate question

**Not because the result is negative.** A negative result withheld for being negative is
exactly the bias this record exists to avoid.

The manuscript was set aside on scope. The object of study is a Gaussian lesion in a uniform
field: it is a synthetic phantom, not a medical image. The work changes no clinical,
dosimetric or regulatory practice, and its readership is narrow. Effort moved to a project
that reaches existing clinical scans. That judgement is open to disagreement, which is
another reason the whole record is here rather than in a drawer.

An exploratory extension putting the same lesion on a real anatomical background was frozen
on 2026-09-06 and **deliberately not executed**;
`docs/exploratory_anatomical_background_protocol.md` records that in as many words, so a
frozen protocol with no result is not mistaken for a withheld one.

**Freezing a study this way is legitimate only once its preregistered outcome has been
assigned.** Stopping before that point looks the same from outside and is not the same
thing.

## Reproduce

```powershell
python -m pip install -e .
python experiments/poc_noise_sweep.py --config configs/poc_noise_sweep.toml
python experiments/plot_saved_results.py --results results/data/poc_noise_sweep.csv
python experiments/finite_size_replication.py --config configs/finite_size_replication.toml
```

The simulation writes raw per-realization data, aggregated data, metadata, figures and a
machine-generated report under `results/`. Figures are generated only from saved numerical
data. Random streams use NumPy `SeedSequence`; the root seed and derived configuration are
recorded in the metadata.

Findings documents, in the order they were produced, are under `docs/`: `phase0_findings`,
`finite_size_findings`, `seed_sensitivity_findings`, `unpaired_two_sample_findings`,
`refined` grids at each size, `resource_gate_findings`, and `finite_size_scaling_findings`,
which carries the outcome assignment.

## Method notes

The ideal prewhitening observer is appropriate because the signal and location are known
exactly and the noise is white Gaussian. Topology uses a superlevel cubical filtration
(`-image`) with GUDHI, reported separately for H0 and H1. Infinite essential classes are
excluded from finite persistence summaries. Paired signal/noise diagrams share the same
noise realization, isolating the lesion's incremental topological effect.

Because filtration coordinates inherit image-intensity units, primary comparisons use
dimensionless metrics: bottleneck, total persistence and maximum persistence are divided by
sigma; the landscape L2 surrogate by sigma^(3/2). Raw dimensional metrics remain saved so
the normalization is auditable.

An apparent bend is never called a phase transition. The analysis compares smooth and
segmented fits and estimates bootstrap uncertainty in any breakpoint.

## Citing

Cite the archived release rather than this page; `CITATION.cff` carries the metadata. It is
a negative research record, and citing it as one is the point.
