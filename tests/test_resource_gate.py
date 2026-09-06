import numpy as np

from experiments.evaluate_resource_gate import power_law_fit


def test_power_law_fit_recovers_frozen_model():
    n = np.array([64, 96, 128, 192], float)
    cost = 2.5 * n ** 2.25
    fit = power_law_fit(n, cost)
    assert np.isclose(fit["coefficient"], 2.5)
    assert np.isclose(fit["alpha"], 2.25)
    assert np.allclose(fit["fitted"], cost)
