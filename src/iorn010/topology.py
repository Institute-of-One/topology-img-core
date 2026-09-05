from __future__ import annotations

import gudhi as gd
import numpy as np


def persistence_diagrams(image: np.ndarray) -> dict[int, np.ndarray]:
    """H0/H1 finite diagrams for a bright-object (superlevel) cubical filtration."""
    cc = gd.CubicalComplex(top_dimensional_cells=-np.asarray(image, dtype=np.float64))
    cc.compute_persistence(homology_coeff_field=2, min_persistence=0.0)
    out: dict[int, np.ndarray] = {}
    for dim in (0, 1):
        dgm = np.asarray(cc.persistence_intervals_in_dimension(dim), dtype=float).reshape(-1, 2)
        out[dim] = dgm[np.isfinite(dgm).all(axis=1)]
    return out


def diagram_summary(dgm: np.ndarray, threshold: float) -> dict[str, float]:
    if len(dgm) == 0:
        return {"total_persistence": 0.0, "max_persistence": 0.0,
                "persistence_entropy": 0.0, "n_persistent": 0.0, "landscape_l2": 0.0}
    life = np.maximum(dgm[:, 1] - dgm[:, 0], 0.0)
    total = float(life.sum())
    p = life[life > 0] / total if total > 0 else np.empty(0)
    entropy = float(-(p * np.log(p)).sum()) if len(p) else 0.0
    # L2 norm of the first-order triangular persistence landscape per interval,
    # aggregated in quadrature. This is a stable scalar surrogate, not a distance.
    landscape_l2 = float(np.sqrt(np.sum(life**3 / 12.0)))
    return {"total_persistence": total, "max_persistence": float(life.max(initial=0.0)),
            "persistence_entropy": entropy, "n_persistent": float((life > threshold).sum()),
            "landscape_l2": landscape_l2}


def bottleneck(a: np.ndarray, b: np.ndarray) -> float:
    return float(gd.bottleneck_distance(a, b, e=1e-4))

