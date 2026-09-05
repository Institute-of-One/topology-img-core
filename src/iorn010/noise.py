import numpy as np


def paired_white_noise(rng: np.random.Generator, n: int, shape: tuple[int, int]) -> np.ndarray:
    """Unit-variance fields reused for absent/present paired comparisons."""
    return rng.standard_normal((n, *shape))

