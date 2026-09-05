from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import time
import tomllib

import matplotlib.pyplot as plt
import numpy as np

from iorn010.observers import ideal_dprime
from iorn010.phantom import gaussian_lesion
from iorn010.refined import bootstrap_breakpoint
from iorn010.topology import bottleneck, persistence_diagrams


def atomic_npz(path: Path, **arrays: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); tmp = path.with_suffix(".tmp.npz")
    np.savez_compressed(tmp, **arrays); os.replace(tmp, path)


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)


def run(config_path: Path, output: Path) -> dict:
    with config_path.open("rb") as f: cfg = tomllib.load(f)["experiment"]
    dense = np.array(cfg["dense_sigmas"], float); anchors = np.array(cfg["anchor_sigmas"], float)
    sigmas = np.sort(np.concatenate([dense, anchors])); signal = gaussian_lesion(
        int(cfg["matrix_size"]), cfg["lesion_amplitude"], cfg["lesion_sigma_px"])
    seeds = np.random.SeedSequence(int(cfg["root_seed"])).spawn(len(sigmas)); raw_rows = []; started = time.perf_counter()
    groups_h0 = []; groups_h1 = []
    for idx, (sigma, seed) in enumerate(zip(sigmas, seeds)):
        n_pairs = int(cfg["n_pairs_dense"] if sigma in dense else cfg["n_pairs_anchor"])
        checkpoint = output / "checkpoints" / f"sigma_{idx:02d}.npz"
        if checkpoint.exists():
            saved = np.load(checkpoint); h0, h1 = saved["h0"], saved["h1"]
        else:
            rng = np.random.default_rng(seed); h0 = np.empty(n_pairs); h1 = np.empty(n_pairs)
            for j in range(n_pairs):
                noise = sigma * rng.standard_normal(signal.shape)
                absent = persistence_diagrams(cfg["background"] + noise)
                present = persistence_diagrams(cfg["background"] + noise + signal)
                h0[j] = bottleneck(absent[0], present[0]) / sigma
                h1[j] = bottleneck(absent[1], present[1]) / sigma
            atomic_npz(checkpoint, sigma=np.array(sigma), h0=h0, h1=h1)
        groups_h0.append(h0); groups_h1.append(h1)
        for j, (v0, v1) in enumerate(zip(h0, h1)):
            raw_rows.append({"sigma": float(sigma), "realization": j,
                             "dprime_analytic": ideal_dprime(signal, float(sigma)),
                             "h0_bottleneck_normalized": float(v0), "h1_bottleneck_normalized": float(v1)})
        print(f"{idx+1}/{len(sigmas)} sigma={sigma:.2f} n={n_pairs}", flush=True)
    fit, draws = bootstrap_breakpoint(sigmas, groups_h0, dense, np.random.default_rng(int(cfg["root_seed"]) + 1),
                                      int(cfg["bootstrap_resamples"]))
    fit["dprime_at_breakpoint"] = ideal_dprime(signal, fit["breakpoint_sigma"])
    fit["grid_spacing"] = 0.1; fit["ci_narrower_than_grid"] = fit["breakpoint_ci_width"] < 0.1
    fit["complete_realizations"] = len(raw_rows); fit["wall_time_seconds"] = time.perf_counter() - started
    means = np.array([g.mean() for g in groups_h0]); ses = np.array([g.std(ddof=1)/np.sqrt(len(g)) for g in groups_h0])
    agg = [{"sigma": float(s), "n_pairs": len(g), "dprime_analytic": ideal_dprime(signal, float(s)),
            "h0_bottleneck_normalized": float(m), "h0_standard_error": float(se)}
           for s, g, m, se in zip(sigmas, groups_h0, means, ses)]
    write_csv(output / "data" / "refined_sigma_raw.csv", raw_rows); write_csv(output / "data" / "refined_sigma_aggregate.csv", agg)
    output.mkdir(parents=True, exist_ok=True); (output / "analysis.json").write_text(json.dumps(fit, indent=2), encoding="utf-8")
    metadata = {"config": cfg, "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
                "freeze_commit": "0e83e8c0f7783711a9e62d8b02369a634b764b0f"}
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (output / "data" / "breakpoint_bootstrap.csv").write_text("breakpoint_sigma\n" + "\n".join(map(str, draws)) + "\n", encoding="utf-8")
    figures = output / "figures"; figures.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(6,4)); ax.errorbar(sigmas, means/means.max(), yerr=ses/means.max(), marker="o", ms=3)
    ax.axvline(fit["breakpoint_sigma"], color="tab:red", ls="--", label=f"breakpoint σ={fit['breakpoint_sigma']:.2f}")
    ax.axvspan(fit["breakpoint_ci_low"], fit["breakpoint_ci_high"], color="tab:red", alpha=.15, label="bootstrap 95% interval")
    ax.set(xscale="log", xlabel="Noise σ", ylabel="Normalized mean H0 bottleneck / σ"); ax.legend(); fig.tight_layout()
    fig.savefig(figures / "figure_J_refined_breakpoint.png", dpi=180); plt.close(fig)
    fig, ax = plt.subplots(figsize=(6,4)); bins=np.arange(dense.min()-.05,dense.max()+.15,.1); ax.hist(draws,bins=bins)
    ax.set(xlabel="Bootstrap breakpoint σ", ylabel="Count"); fig.tight_layout(); fig.savefig(figures / "figure_K_breakpoint_bootstrap.png", dpi=180); plt.close(fig)
    print(json.dumps(fit, indent=2)); return fit


if __name__ == "__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("--config",type=Path,required=True)
    parser.add_argument("--output",type=Path,default=Path("results/refined_sigma_grid")); args=parser.parse_args()
    run(args.config,args.output)

