import numpy as np


def gaussian_lesion(size: int, amplitude: float, sigma_px: float) -> np.ndarray:
    """Centered Gaussian lesion with a pixel-centered, deterministic coordinate grid."""
    y, x = np.indices((size, size), dtype=float)
    c = (size - 1) / 2.0
    r2 = (x - c) ** 2 + (y - c) ** 2
    return amplitude * np.exp(-r2 / (2.0 * sigma_px**2))

