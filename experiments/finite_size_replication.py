from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import tomllib

import numpy as np
import matplotlib.pyplot as plt

from iorn010.metrics import piecewise_breakpoint
from iorn010.phantom import gaussian_lesion
from iorn010.topology import bottleneck, persistence_diagrams


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def condition_path(root: Path, size: int, lesion_sigma: float) -> Path:
    return root / "checkpoints" / f"size_{size}_lesion_{lesion_sigma:g}.csv"


def simulate_condition(cfg: dict, size: int, lesion_sigma: float, seed: np.random.SeedSequence,
                       output: Path) -> list[dict]:
    checkpoint = condition_path(output, size, lesion_sigma)
    if checkpoint.exists():
        print(f"resume {checkpoint}", flush=True)
        return read_csv(checkpoint)
    signal = gaussian_lesion(size, cfg["lesion_amplitude"], lesion_sigma)
    rows: list[dict] = []
    sigma_seeds = seed.spawn(len(cfg["noise_sigmas"]))
    for idx, (sigma, sigma_seed) in enumerate(zip(cfg["noise_sigmas"], sigma_seeds)):
        dense = cfg["dense_region_min"] <= sigma <= cfg["dense_region_max"]
        n_pairs = int(cfg["n_pairs_dense"] if dense else cfg["n_pairs_anchor"])
        rng = np.random.default_rng(sigma_seed)
        for realization in range(n_pairs):
            noise = sigma * rng.standard_normal((size, size))
            absent = persistence_diagrams(cfg["background"] + noise)
            present = persistence_diagrams(cfg["background"] + noise + signal)
            rows.append({"matrix_size": size, "lesion_sigma_px": lesion_sigma,
                         "sigma": sigma, "sigma_index": idx, "realization": realization,
                         "dprime_analytic": float(np.linalg.norm(signal) / sigma),
                         "h0_bottleneck_normalized": bottleneck(absent[0], present[0]) / sigma,
                         "h1_bottleneck_normalized": bottleneck(absent[1], present[1]) / sigma})
        print(f"size={size} lesion={lesion_sigma:g} sigma={sigma:g} n={n_pairs}", flush=True)
    write_csv(checkpoint, rows)
    return rows


def aggregate(rows: list[dict]) -> list[dict]:
    groups: dict[tuple[int, float, float], list[dict]] = {}
    for row in rows:
        key = (int(row["matrix_size"]), float(row["lesion_sigma_px"]), float(row["sigma"]))
        groups.setdefault(key, []).append(row)
    out = []
    for (size, lesion, sigma), values in sorted(groups.items()):
        item = {"matrix_size": size, "lesion_sigma_px": lesion, "sigma": sigma,
                "n_pairs": len(values), "dprime_analytic": float(values[0]["dprime_analytic"])}
        for metric in ("h0_bottleneck_normalized", "h1_bottleneck_normalized"):
            x = np.array([float(v[metric]) for v in values])
            item[metric] = float(x.mean()); item[metric + "_se"] = float(x.std(ddof=1) / np.sqrt(len(x)))
        out.append(item)
    return out


def analyze(rows: list[dict], rng: np.random.Generator, n_boot: int) -> dict:
    conditions = sorted({(int(r["matrix_size"]), float(r["lesion_sigma_px"])) for r in rows})
    result = {"conditions": {}}
    for size, lesion in conditions:
        subset = [r for r in rows if int(r["matrix_size"]) == size and float(r["lesion_sigma_px"]) == lesion]
        sigmas = np.array(sorted({float(r["sigma"]) for r in subset}))
        groups = [[float(r["h0_bottleneck_normalized"]) for r in subset if float(r["sigma"]) == s] for s in sigmas]
        curve = np.array([np.mean(g) for g in groups]); fit = piecewise_breakpoint(sigmas, curve / curve.max())
        breaks = []
        for _ in range(n_boot):
            boot = np.array([np.mean(rng.choice(g, len(g), replace=True)) for g in groups])
            breaks.append(piecewise_breakpoint(sigmas, boot / boot.max())["breakpoint"])
        lo, hi = np.quantile(breaks, [0.025, 0.975])
        signal_norm = float(np.linalg.norm(gaussian_lesion(size, 1.0, lesion)))
        result["conditions"][f"size_{size}_lesion_{lesion:g}"] = {
            **fit, "breakpoint_ci_low": float(lo), "breakpoint_ci_high": float(hi),
            "dprime_at_breakpoint": signal_norm / fit["breakpoint"]}
    vals = list(result["conditions"].values())
    # Compare dimensionless curve collapse on the acquisition (sigma) axis and the
    # observer-information (dprime) axis using a common log grid.
    curves = []
    for size, lesion in conditions:
        subset = [r for r in rows if int(r["matrix_size"]) == size and float(r["lesion_sigma_px"]) == lesion]
        sig = np.array(sorted({float(r["sigma"]) for r in subset}))
        t = np.array([np.mean([float(r["h0_bottleneck_normalized"]) for r in subset if float(r["sigma"]) == s]) for s in sig])
        dp = np.array([float(next(r["dprime_analytic"] for r in subset if float(r["sigma"]) == s)) for s in sig])
        curves.append((sig, dp, t / t.max()))
    sigma_grid = np.geomspace(max(c[0].min() for c in curves), min(c[0].max() for c in curves), 100)
    dp_grid = np.geomspace(max(c[1].min() for c in curves), min(c[1].max() for c in curves), 100)
    sigma_stack = np.vstack([np.interp(np.log(sigma_grid), np.log(s), t) for s, _, t in curves])
    dp_stack = np.vstack([np.interp(np.log(dp_grid), np.log(dp[::-1]), t[::-1]) for _, dp, t in curves])
    result["summary"] = {"breakpoint_min": min(v["breakpoint"] for v in vals),
                         "breakpoint_max": max(v["breakpoint"] for v in vals),
                         "dprime_at_breakpoint_min": min(v["dprime_at_breakpoint"] for v in vals),
                         "dprime_at_breakpoint_max": max(v["dprime_at_breakpoint"] for v in vals),
                         "collapse_mean_sd_sigma_axis": float(np.mean(np.std(sigma_stack, axis=0))),
                         "collapse_mean_sd_dprime_axis": float(np.mean(np.std(dp_stack, axis=0)))}
    return result


def make_figures(aggregate_rows: list[dict], report: dict, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    sizes = sorted({int(r["matrix_size"]) for r in aggregate_rows})
    lesions = sorted({float(r["lesion_sigma_px"]) for r in aggregate_rows})
    colors = dict(zip(lesions, ("tab:blue", "tab:orange", "tab:green")))
    for axis_name, filename, xlabel in (("sigma", "figure_F_curves_sigma.png", "Noise σ"),
                                        ("dprime_analytic", "figure_G_curves_dprime.png", "Ideal-observer d′")):
        fig, axes = plt.subplots(1, len(sizes), figsize=(12, 3.5), sharey=True, constrained_layout=True)
        for ax, size in zip(axes, sizes):
            for lesion in lesions:
                rows = [r for r in aggregate_rows if int(r["matrix_size"]) == size and float(r["lesion_sigma_px"]) == lesion]
                rows.sort(key=lambda r: float(r[axis_name]))
                x = np.array([float(r[axis_name]) for r in rows]); y = np.array([float(r["h0_bottleneck_normalized"]) for r in rows]); y /= y.max()
                ax.plot(x, y, marker="o", ms=3, color=colors[lesion], label=f"lesion σ={lesion:g}")
            ax.set_xscale("log"); ax.set_title(f"matrix {size}×{size}"); ax.set_xlabel(xlabel)
        axes[0].set_ylabel("Normalized H0 bottleneck / σ"); axes[-1].legend(fontsize=8)
        fig.savefig(output / filename, dpi=180); plt.close(fig)
    heat = np.array([[report["conditions"][f"size_{s}_lesion_{l:g}"]["breakpoint"] for l in lesions] for s in sizes])
    fig, ax = plt.subplots(figsize=(5.2, 4)); im = ax.imshow(heat, cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(lesions)), [f"{x:g}" for x in lesions]); ax.set_yticks(range(len(sizes)), sizes)
    ax.set(xlabel="Lesion σ (px)", ylabel="Matrix size", title="Candidate breakpoint σ")
    for i in range(len(sizes)):
        for j in range(len(lesions)): ax.text(j, i, f"{heat[i,j]:.2g}", ha="center", va="center", color="white")
    fig.colorbar(im, ax=ax); fig.tight_layout(); fig.savefig(output / "figure_H_breakpoints.png", dpi=180); plt.close(fig)


def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("--config", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("results/finite_size")); args = p.parse_args()
    with args.config.open("rb") as f: cfg = tomllib.load(f)["experiment"]
    root = np.random.SeedSequence(int(cfg["root_seed"]))
    conditions = [(int(s), float(l)) for s in cfg["matrix_sizes"] for l in cfg["lesion_sigmas_px"]]
    rows = []
    for (size, lesion), seed in zip(conditions, root.spawn(len(conditions))):
        rows.extend(simulate_condition(cfg, size, lesion, seed, args.output))
    agg = aggregate(rows)
    write_csv(args.output / "data" / "finite_size_raw.csv", rows)
    write_csv(args.output / "data" / "finite_size_aggregate.csv", agg)
    report = analyze(rows, np.random.default_rng(int(cfg["root_seed"]) + 1), int(cfg["bootstrap_resamples"]))
    (args.output / "analysis.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (args.output / "metadata.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    make_figures(agg, report, args.output / "figures")
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__": main()
