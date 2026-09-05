from __future__ import annotations

import numpy as np


def segmented_fit(x: np.ndarray, y: np.ndarray, candidate_knots: np.ndarray) -> dict[str, float]:
    z = np.log(np.asarray(x, float)); y = np.asarray(y, float)
    base = np.column_stack([np.ones_like(z), z])
    rss_linear = float(np.sum((y - base @ np.linalg.lstsq(base, y, rcond=None)[0]) ** 2))
    best_rss, best_knot = np.inf, np.nan
    for knot in np.asarray(candidate_knots, float):
        zk = np.log(knot)
        design = np.column_stack([np.ones_like(z), z, np.maximum(z - zk, 0.0)])
        rss = float(np.sum((y - design @ np.linalg.lstsq(design, y, rcond=None)[0]) ** 2))
        if rss < best_rss:
            best_rss, best_knot = rss, float(knot)
    n = len(y)
    aic_linear = n * np.log(max(rss_linear / n, 1e-300)) + 2 * 3
    aic_piecewise = n * np.log(max(best_rss / n, 1e-300)) + 2 * 5
    return {"breakpoint_sigma": best_knot, "rss_linear": rss_linear,
            "rss_piecewise": best_rss,
            "delta_aic_piecewise_minus_linear": float(aic_piecewise - aic_linear)}


def bootstrap_breakpoint(sigmas: np.ndarray, groups: list[np.ndarray], candidates: np.ndarray,
                         rng: np.random.Generator, n_boot: int) -> tuple[dict, np.ndarray]:
    curve = np.array([g.mean() for g in groups]); fit = segmented_fit(sigmas, curve / curve.max(), candidates)
    draws = []
    for _ in range(n_boot):
        sample = np.array([rng.choice(g, len(g), replace=True).mean() for g in groups])
        draws.append(segmented_fit(sigmas, sample / sample.max(), candidates)["breakpoint_sigma"])
    draws = np.asarray(draws)
    lo, hi = np.quantile(draws, [0.025, 0.975])
    fit.update({"breakpoint_ci_low": float(lo), "breakpoint_ci_high": float(hi),
                "breakpoint_ci_width": float(hi - lo)})
    return fit, draws

