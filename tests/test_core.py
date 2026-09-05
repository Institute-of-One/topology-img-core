import numpy as np
from iorn010.observers import ideal_dprime
from iorn010.phantom import gaussian_lesion
from iorn010.topology import diagram_summary, persistence_diagrams


def test_dprime_inverse_noise():
    s = gaussian_lesion(32, 1.0, 3.0)
    assert np.isclose(ideal_dprime(s, 2.0), ideal_dprime(s, 1.0) / 2)


def test_persistence_is_finite_after_essential_exclusion():
    d = persistence_diagrams(gaussian_lesion(16, 1.0, 2.0))
    assert all(np.isfinite(x).all() for x in d.values())


def test_empty_summary():
    assert diagram_summary(np.empty((0, 2)), .1)["total_persistence"] == 0.0

