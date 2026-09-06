import numpy as np

from experiments.extend_scaling_precision import labeled_seed


def test_scaling_extension_seed_is_reproducible_and_replication_specific():
    a = labeled_seed(20261096, 1.0, 64).generate_state(8)
    b = labeled_seed(20261096, 1.0, 64).generate_state(8)
    c = labeled_seed(20261096, 1.0, 65).generate_state(8)
    d = labeled_seed(20261096, 1.1, 64).generate_state(8)
    assert np.array_equal(a, b)
    assert not np.array_equal(a, c)
    assert not np.array_equal(a, d)
