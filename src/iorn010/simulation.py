from __future__ import annotations

import csv
import hashlib
import json
import platform
from pathlib import Path
import tomllib

import gudhi
import numpy as np
import scipy

from .metrics import bootstrap_mean_ci
from .noise import paired_white_noise
from .observers import empirical_dprime, ideal_dprime, matched_filter_scores
from .phantom import gaussian_lesion
from .topology import bottleneck, diagram_summary, persistence_diagrams


def load_config(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)["experiment"]


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)


def run(config_path: Path, output_root: Path) -> tuple[Path, Path]:
    cfg = load_config(config_path)
    size = int(cfg["matrix_size"])
    signal = gaussian_lesion(size, cfg["lesion_amplitude"], cfg["lesion_sigma_px"])
    sigmas = np.geomspace(cfg["sigma_min"], cfg["sigma_max"], int(cfg["n_sigma"]))
    root = np.random.SeedSequence(int(cfg["root_seed"]))
    obs_seeds, top_seeds, boot_seeds = root.spawn(3)
    obs_children = obs_seeds.spawn(len(sigmas)); top_children = top_seeds.spawn(len(sigmas))
    boot_rng = np.random.default_rng(boot_seeds)
    raw: list[dict] = []; aggregate: list[dict] = []
    summaries = ("total_persistence", "max_persistence", "persistence_entropy",
                 "n_persistent", "landscape_l2")
    for i, sigma in enumerate(sigmas):
        rng = np.random.default_rng(obs_children[i])
        unit = paired_white_noise(rng, int(cfg["n_observer_pairs"]), signal.shape)
        absent = cfg["background"] + sigma * unit
        present = absent + signal
        sa = matched_filter_scores(absent, signal); sp = matched_filter_scores(present, signal)
        obs_emp = empirical_dprime(sa, sp)
        top_rng = np.random.default_rng(top_children[i])
        unit_top = paired_white_noise(top_rng, int(cfg["n_topology_pairs"]), signal.shape)
        per_sigma: list[dict] = []
        threshold = float(cfg["persistence_threshold_fraction"]) * sigma
        for j, field in enumerate(unit_top):
            da = persistence_diagrams(cfg["background"] + sigma * field)
            dp = persistence_diagrams(cfg["background"] + sigma * field + signal)
            row = {"sigma": float(sigma), "sigma_index": i, "realization": j}
            for dim in (0, 1):
                a = diagram_summary(da[dim], threshold); p = diagram_summary(dp[dim], threshold)
                row[f"h{dim}_bottleneck"] = bottleneck(da[dim], dp[dim])
                for name in summaries:
                    row[f"h{dim}_{name}_absent"] = a[name]
                    row[f"h{dim}_{name}_present"] = p[name]
                    row[f"h{dim}_{name}_delta"] = p[name] - a[name]
            raw.append(row); per_sigma.append(row)
        agg = {"sigma": float(sigma), "dprime_analytic": ideal_dprime(signal, sigma),
               "dprime_empirical": obs_emp}
        for key in [k for k in per_sigma[0] if k.startswith("h") and not k.endswith(("_absent", "_present"))]:
            vals = np.array([r[key] for r in per_sigma], float)
            lo, hi = bootstrap_mean_ci(vals, boot_rng, int(cfg["bootstrap_resamples"]))
            agg[key] = float(vals.mean()); agg[f"{key}_ci_low"] = lo; agg[f"{key}_ci_high"] = hi
        aggregate.append(agg)
    raw_path = output_root / "data" / "poc_noise_sweep_raw.csv"
    agg_path = output_root / "data" / "poc_noise_sweep.csv"
    _write_csv(raw_path, raw); _write_csv(agg_path, aggregate)
    config_bytes = config_path.read_bytes()
    metadata = {"config": cfg, "config_sha256": hashlib.sha256(config_bytes).hexdigest(),
                "python": platform.python_version(), "numpy": np.__version__,
                "scipy": scipy.__version__, "gudhi": gudhi.__version__,
                "filtration": "superlevel cubical (-image)",
                "pairing": "identical noise field for absent and present image",
                "essential_classes": "excluded from finite summaries"}
    (output_root / "data" / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return raw_path, agg_path

