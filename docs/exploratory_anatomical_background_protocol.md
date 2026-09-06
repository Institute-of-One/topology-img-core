# Exploratory extension — an anatomical background under the same lesion

Frozen 2026-09-06, before any background patch was extracted or any topology computed.

**This is outside the Phase-0 and Phase-2 preregistrations and does not amend them.** They
govern a uniform field with additive white Gaussian noise, and that design is unchanged.
Nothing here is offered as confirmatory evidence, and the manuscript will present it in a
section that says so.

## Why it exists

The registered study never touches a medical image. A Gaussian lesion in a uniform field is
as far from anatomy as an image can be while remaining an image, and calling it a synthetic
phantom rather than a medical image makes that visible rather than resolving it. A reviewer
will ask whether the crossover survives real structure, and the honest options are to answer
with a bounded look or to say the question is open. This is the bounded look.

## The one thing that makes the comparison clean

The ideal observer used throughout is `d' = ||signal|| / sigma`, for a known signal in white
Gaussian noise. A background added **deterministically** leaves the only stochastic term the
white noise, so **`d'` is analytically identical with and without anatomy**.

That is the whole design. Detectability is held exactly fixed; only the topology sees the
anatomy. Any change in where the topological crossover falls is therefore attributable to
anatomical topology alone, and to nothing else.

## Method

Everything not named below is unchanged from `configs/poc_noise_sweep.toml`: matrix 128,
lesion amplitude 1.0, lesion sigma 5 px, the sigma grid, the observer and topology pair
counts, the persistence threshold fraction, and the superlevel cubical filtration with H0
and H1 reported separately.

**Backgrounds.** 128 x 128 patches from three public chest CT series already held locally
for IORN-011, identified by SeriesInstanceUID with their licences recorded. No imaging is
redistributed and none enters this repository.

**Patch selection, fixed in advance and applied without inspection of the result:**

- from the middle third of the scanned range, so patches are thoracic rather than neck or
  abdomen;
- centred on the mediastinum, taken as the centroid of voxels between -100 and +150 HU in
  the slice, so the patch is soft tissue rather than lung or bone;
- rejected if more than 10 per cent of the patch is below -300 HU (lung) or above +300 HU
  (bone), so a patch is either soft tissue or it is not used;
- 12 patches per series, evenly spaced through the eligible range;
- **no patch is dropped after its topology has been computed.**

**Scaling.** Patches are converted to the phantom's units by subtracting the patch mean and
dividing by the patch standard deviation, then multiplied by a background contrast factor
`beta` swept over 0 (the registered uniform case), 0.5, 1, 2 and 4. `beta = 0` must
reproduce the registered result and is the check that the harness is the same harness.

## What each outcome would mean, decided now

- **The crossover persists at its registered location for all `beta`.** The phenomenon is
  robust to anatomical structure, which would be a stronger claim than the registered study
  makes and would be reported as exploratory support, not as evidence.
- **The crossover persists but moves with `beta`.** Anatomy shifts the crossover. This
  strengthens the registered finding of nonconvergence rather than weakening it: the
  location depends on the image support in yet another way.
- **The crossover disappears at realistic `beta`.** Anatomical topology swamps the lesion's
  H0 and H1 signature. The registered result stands as a statement about uniform fields and
  the manuscript says plainly that it does not extend to anatomy.

**The third is what is expected.** A chest CT contains vessels, airways, ribs and fat planes,
all of which generate persistent features, and one Gaussian lesion is a small perturbation
on that. Writing that down before running is what stops the expected outcome being reported
as a disappointment or the unexpected one as a triumph.

## Provenance and governance

The three series are public and de-identified under their stated licences. Their UIDs,
collections and licences are recorded with the results. Patches are derived data and are not
redistributed; the extraction script plus the UIDs reproduce them from the archive.
