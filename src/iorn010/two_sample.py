from __future__ import annotations

import numpy as np
from scipy.spatial.distance import cdist
from scipy import stats


def persistence_image(diagram: np.ndarray, sigma: float, *, resolution: int = 32,
                      birth_bounds: tuple[float, float] = (-5.0, 5.0),
                      persistence_bounds: tuple[float, float] = (0.0, 8.0),
                      bandwidth: float = 0.15) -> np.ndarray:
    """Fixed, dimensionless persistence image with linear persistence weights."""
    if len(diagram) == 0:
        return np.zeros(resolution * resolution, dtype=np.float32)
    birth = np.clip(diagram[:, 0] / sigma, *birth_bounds)
    life = np.clip((diagram[:, 1] - diagram[:, 0]) / sigma, *persistence_bounds)
    bx = np.linspace(*birth_bounds, resolution, dtype=np.float64)
    py = np.linspace(*persistence_bounds, resolution, dtype=np.float64)
    db = bx[None, None, :] - birth[:, None, None]
    dp = py[None, :, None] - life[:, None, None]
    image = np.sum(life[:, None, None] * np.exp(-(db * db + dp * dp) / (2 * bandwidth**2)), axis=0)
    return image.astype(np.float32).ravel()


def energy_statistic_from_distances(distances: np.ndarray, labels: np.ndarray) -> float:
    labels = np.asarray(labels, bool); x = np.flatnonzero(labels); y = np.flatnonzero(~labels)
    nx, ny = len(x), len(y)
    cross = distances[np.ix_(x, y)].mean()
    within_x = distances[np.ix_(x, x)].sum() / (nx * (nx - 1))
    within_y = distances[np.ix_(y, y)].sum() / (ny * (ny - 1))
    return float(max(0.0, 2.0 * cross - within_x - within_y))


def energy_permutation_test(present: np.ndarray, absent: np.ndarray, rng: np.random.Generator,
                            n_permutations: int = 999) -> tuple[float, float]:
    features = np.vstack([present, absent]).astype(np.float64, copy=False)
    distances = cdist(features, features, metric="euclidean")
    n = len(present); labels = np.zeros(len(features), dtype=bool); labels[:n] = True
    observed = energy_statistic_from_distances(distances, labels)
    exceed = 0
    for _ in range(n_permutations):
        perm = rng.permutation(len(features)); candidate = np.zeros(len(features), dtype=bool)
        candidate[perm[:n]] = True
        exceed += energy_statistic_from_distances(distances, candidate) >= observed
    return observed, float((exceed + 1) / (n_permutations + 1))


def benjamini_hochberg(p_values: np.ndarray, q: float = 0.05) -> np.ndarray:
    p = np.asarray(p_values, float); order = np.argsort(p); ranked = p[order]
    passing = ranked <= q * np.arange(1, len(p) + 1) / len(p)
    rejected = np.zeros(len(p), dtype=bool)
    if passing.any():
        rejected[order[:np.flatnonzero(passing)[-1] + 1]] = True
    return rejected


def bootstrap_spearman(x: np.ndarray, y: np.ndarray, rng: np.random.Generator,
                       n_boot: int) -> dict[str, float]:
    rho, p = stats.spearmanr(x, y); draws = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(x), len(x)); r = stats.spearmanr(x[idx], y[idx]).statistic
        if np.isfinite(r): draws.append(r)
    lo, hi = np.quantile(draws, [0.025, 0.975])
    return {"rho": float(rho), "p": float(p), "ci_low": float(lo), "ci_high": float(hi)}

