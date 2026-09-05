from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import tomllib

import matplotlib.pyplot as plt
import numpy as np

from iorn010.observers import ideal_dprime
from iorn010.phantom import gaussian_lesion
from iorn010.topology import persistence_diagrams
from iorn010.two_sample import (benjamini_hochberg, bootstrap_spearman,
                                energy_permutation_test, persistence_image)


def atomic_npz(path: Path, **arrays: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); tmp = path.with_suffix(".tmp.npz")
    np.savez_compressed(tmp, **arrays); os.replace(tmp, path)


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def generate_features(cfg: dict, sigma: float, group_seeds: tuple[np.random.SeedSequence, np.random.SeedSequence],
                      signal: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    present_seed, absent_seed = group_seeds
    kwargs = {"resolution": int(cfg["persistence_image_resolution"]),
              "birth_bounds": (cfg["birth_min_normalized"], cfg["birth_max_normalized"]),
              "persistence_bounds": (cfg["persistence_min_normalized"], cfg["persistence_max_normalized"]),
              "bandwidth": cfg["gaussian_bandwidth"]}
    features = []
    for group_seed, with_signal in ((present_seed, True), (absent_seed, False)):
        rng = np.random.default_rng(group_seed); group = []
        for _ in range(int(cfg["n_per_group"])):
            image = cfg["background"] + sigma * rng.standard_normal(signal.shape)
            if with_signal: image += signal
            diagram = persistence_diagrams(image)[int(cfg["homology_dimension"])]
            group.append(persistence_image(diagram, sigma, **kwargs))
        features.append(np.asarray(group, dtype=np.float32))
    return features[0], features[1]


def run(config_path: Path, output: Path) -> dict:
    with config_path.open("rb") as f: cfg = tomllib.load(f)["experiment"]
    sigmas = np.geomspace(cfg["sigma_min"], cfg["sigma_max"], int(cfg["n_sigma"]))
    signal = gaussian_lesion(int(cfg["matrix_size"]), cfg["lesion_amplitude"], cfg["lesion_sigma_px"])
    seeds = np.random.SeedSequence(int(cfg["root_seed"])).spawn(len(sigmas))
    rows = []
    for idx, (sigma, seed) in enumerate(zip(sigmas, seeds)):
        present_seed, absent_seed, permutation_seed = seed.spawn(3)
        checkpoint = output / "checkpoints" / f"sigma_{idx:03d}.npz"
        if checkpoint.exists():
            saved = np.load(checkpoint); present, absent = saved["present"], saved["absent"]
        else:
            present, absent = generate_features(cfg, float(sigma), (present_seed, absent_seed), signal)
            atomic_npz(checkpoint, present=present, absent=absent, sigma=np.array(sigma))
        perm_rng = np.random.default_rng(permutation_seed)
        energy, p = energy_permutation_test(present, absent, perm_rng, int(cfg["n_permutations"]))
        rows.append({"sigma_index": idx, "sigma": float(sigma),
                     "dprime_analytic": ideal_dprime(signal, float(sigma)),
                     "energy_distance": energy, "permutation_p": p})
        print(f"{idx+1}/{len(sigmas)} sigma={sigma:.5g} energy={energy:.6g} p={p:.4g}", flush=True)
    rejected = benjamini_hochberg(np.array([r["permutation_p"] for r in rows]), cfg["fdr_q"])
    for row, reject in zip(rows, rejected): row["fdr_significant"] = int(reject)
    write_csv(output / "data" / "unpaired_two_sample.csv", rows)
    dp = np.array([r["dprime_analytic"] for r in rows]); energy = np.array([r["energy_distance"] for r in rows])
    assoc = bootstrap_spearman(dp, energy, np.random.default_rng(int(cfg["root_seed"]) + 1),
                               int(cfg["association_bootstrap_resamples"]))
    high = dp >= 2; low = dp <= 0.5
    high_fraction = float(rejected[high].mean()); low_fraction = float(rejected[low].mean())
    survived = assoc["ci_low"] > 0 and high_fraction >= 0.5 and low_fraction <= 0.1
    analysis = {"association": assoc, "significant_fraction_dprime_ge_2": high_fraction,
                "significant_fraction_dprime_le_0_5": low_fraction,
                "survives_unpaired_validation": bool(survived),
                "complete_sigma_levels": len(rows)}
    output.mkdir(parents=True, exist_ok=True)
    (output / "analysis.json").write_text(json.dumps(analysis, indent=2), encoding="utf-8")
    meta = {"config": cfg, "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
            "freeze_commit": "0e83e8c0f7783711a9e62d8b02369a634b764b0f"}
    (output / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    fig, ax = plt.subplots(figsize=(6, 4)); ax.plot(sigmas, energy); ax.scatter(sigmas[rejected], energy[rejected], s=16, label="BH-FDR q=0.05")
    ax.set(xscale="log", yscale="log", xlabel="Noise σ", ylabel="Unpaired persistence-image energy distance")
    ax.legend(); fig.tight_layout(); (output / "figures").mkdir(exist_ok=True)
    fig.savefig(output / "figures" / "figure_I_unpaired_energy.png", dpi=180); plt.close(fig)
    print(json.dumps(analysis, indent=2)); return analysis


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--config", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("results/unpaired_two_sample")); a = p.parse_args()
    run(a.config, a.output)
