from __future__ import annotations

import csv
import json
from pathlib import Path
import numpy as np

from .metrics import piecewise_breakpoint, spearman_with_ci


def read_columns(path: Path) -> dict[str, np.ndarray]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {k: np.array([float(r[k]) for r in rows]) for k in rows[0]}


def add_dimensionless_metrics(d: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Remove the trivial filtration-amplitude scaling induced by changing sigma."""
    sigma = d["sigma"]
    for key, value in list(d.items()):
        if key.endswith("_bottleneck") or key.endswith("_total_persistence_delta") or key.endswith("_max_persistence_delta"):
            d[key + "_normalized"] = value / sigma
        elif key.endswith("_landscape_l2_delta"):
            d[key + "_normalized"] = value / sigma**1.5
    return d


def primary_metric_bootstrap(raw_path: Path, rng: np.random.Generator,
                             n_boot: int = 500) -> dict[str, float]:
    raw = read_columns(raw_path); unique = np.unique(raw["sigma"])
    groups = [raw["h0_bottleneck"][raw["sigma"] == s] / s for s in unique]
    means = np.array([g.mean() for g in groups])
    breaks = []
    for _ in range(n_boot):
        curve = np.array([rng.choice(g, len(g), replace=True).mean() for g in groups])
        breaks.append(piecewise_breakpoint(unique, curve / curve.max())["breakpoint"])
    lo, hi = np.quantile(breaks, [0.025, 0.975])
    normalized = means / means.max()
    half = float(np.interp(0.5, normalized[::-1], unique[::-1]))
    tenth = float(np.interp(0.1, normalized[::-1], unique[::-1]))
    return {"breakpoint_ci_low": float(lo), "breakpoint_ci_high": float(hi),
            "half_max_sigma": half, "ten_percent_sigma": tenth}


def analyze(path: Path, output: Path, task_threshold: float = 1.0,
            raw_path: Path | None = None) -> dict:
    d = add_dimensionless_metrics(read_columns(path)); sigma = d["sigma"]; dp = d["dprime_analytic"]
    metric_names = [k for k in d if (k.endswith("_normalized") or k.endswith("_entropy_delta") or k.endswith("_persistent_delta"))
                    and not (k.endswith("_low") or k.endswith("_high"))]
    rng = np.random.default_rng(8128)
    task_cross = float(np.interp(task_threshold, dp[::-1], sigma[::-1]))
    report = {"task_threshold_dprime": task_threshold, "sigma_task": task_cross,
              "observer_relative_rmse": float(np.sqrt(np.mean(((d["dprime_empirical"]-dp)/dp)**2))),
              "metrics": {}}
    for name in metric_names:
        y = np.abs(d[name]) if name.endswith("_delta") else d[name]
        scale = np.nanmax(y)
        yn = y / scale if scale > 0 else y
        report["metrics"][name] = {"spearman_vs_dprime": spearman_with_ci(dp, yn, rng),
                                    "segmented_fit": piecewise_breakpoint(sigma, yn),
                                    "dynamic_range": float(np.nanmax(y)-np.nanmin(y))}
    if raw_path is not None:
        report["primary_h0_bottleneck_normalized"] = primary_metric_bootstrap(raw_path, rng)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
