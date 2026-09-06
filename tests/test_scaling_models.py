import numpy as np

from experiments.finite_size_scaling import aicc, fit_models


def test_aicc_requires_positive_small_sample_denominator():
    assert np.isinf(aicc(1.0, 3, 2))
    assert np.isfinite(aicc(1.0, 5, 3))


def test_scaling_models_fit_exact_constant_and_log_curves():
    n = np.array([64, 96, 128, 192, 256], float)
    se = np.full(5, 0.1)
    constant = fit_models(n, np.full(5, 2.0), se)
    assert np.isclose(constant["constant"]["parameters"]["c"], 2.0)
    log_y = 1.5 + 0.2 * np.log(n)
    drift = fit_models(n, log_y, se)
    assert np.isclose(drift["log_drift"]["parameters"]["b1"], 0.2)
