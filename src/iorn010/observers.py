import numpy as np


def ideal_dprime(signal: np.ndarray, sigma: float) -> float:
    """Known-signal-known-exactly ideal observer in white Gaussian noise."""
    return float(np.linalg.norm(signal.ravel()) / sigma)


def matched_filter_scores(images: np.ndarray, template: np.ndarray) -> np.ndarray:
    return np.einsum("nij,ij->n", images, template, optimize=True)


def empirical_dprime(absent: np.ndarray, present: np.ndarray) -> float:
    pooled_var = 0.5 * (absent.var(ddof=1) + present.var(ddof=1))
    return float((present.mean() - absent.mean()) / np.sqrt(pooled_var))

