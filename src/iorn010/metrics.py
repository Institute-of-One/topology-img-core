from __future__ import annotations

import numpy as np
from scipy import stats


def bootstrap_mean_ci(values: np.ndarray, rng: np.random.Generator, n_boot: int) -> tuple[float, float]:
    values = np.asarray(values, float)
    if len(values) < 2:
        return float(values.mean()), float(values.mean())
    means = np.mean(rng.choice(values, size=(n_boot, len(values)), replace=True), axis=1)
    return tuple(np.quantile(means, [0.025, 0.975]).tolist())


def spearman_with_ci(x: np.ndarray, y: np.ndarray, rng: np.random.Generator,
                     n_boot: int = 1000) -> dict[str, float]:
    rho, p = stats.spearmanr(x, y)
    vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(x), len(x))
        r = stats.spearmanr(x[idx], y[idx]).statistic
        if np.isfinite(r):
            vals.append(r)
    lo, hi = np.quantile(vals, [0.025, 0.975])
    return {"rho": float(rho), "p": float(p), "ci_low": float(lo), "ci_high": float(hi)}


def piecewise_breakpoint(x: np.ndarray, y: np.ndarray) -> dict[str, float]:
    """Compare linear-in-log-x against continuous one-break segmented regression."""
    z = np.log(np.asarray(x, float)); y = np.asarray(y, float)
    base = np.column_stack([np.ones_like(z), z])
    rss0 = float(np.sum((y - base @ np.linalg.lstsq(base, y, rcond=None)[0]) ** 2))
    best = (np.inf, np.nan)
    # Keep at least three observations on each side while using a wider guard for
    # dense curves. The original fixed guard of ten is invalid for focused sweeps.
    margin = max(3, min(10, len(z) // 4))
    for k in range(margin, len(z) - margin):
        knot = z[k]
        a = np.column_stack([np.ones_like(z), z, np.maximum(z - knot, 0.0)])
        rss = float(np.sum((y - a @ np.linalg.lstsq(a, y, rcond=None)[0]) ** 2))
        if rss < best[0]:
            best = (rss, float(np.exp(knot)))
    n = len(y)
    aic_linear = n * np.log(max(rss0 / n, 1e-300)) + 2 * 3
    aic_piecewise = n * np.log(max(best[0] / n, 1e-300)) + 2 * 5
    return {"breakpoint": best[1], "rss_linear": rss0, "rss_piecewise": best[0],
            "delta_aic_piecewise_minus_linear": float(aic_piecewise - aic_linear)}
