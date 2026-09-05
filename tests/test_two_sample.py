import numpy as np

from iorn010.two_sample import benjamini_hochberg, energy_permutation_test, persistence_image


def test_persistence_image_is_dimensionless_under_scaling():
    d = np.array([[-1.0, 1.0], [0.5, 2.0]])
    assert np.allclose(persistence_image(d, 1.0), persistence_image(2 * d, 2.0))


def test_energy_detects_separated_samples():
    rng = np.random.default_rng(4); a = rng.normal(2, .1, (20, 3)); b = rng.normal(0, .1, (20, 3))
    statistic, p = energy_permutation_test(a, b, np.random.default_rng(5), 99)
    assert statistic > 0 and p <= .02


def test_bh_controls_simple_family():
    assert benjamini_hochberg(np.array([0.001, 0.02, 0.8]), 0.05).tolist() == [True, True, False]

