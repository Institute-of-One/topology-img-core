from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

from .analysis import add_dimensionless_metrics, read_columns
from .phantom import gaussian_lesion


def make_figures(results_csv: Path, figure_dir: Path, metadata: dict) -> None:
    d = add_dimensionless_metrics(read_columns(results_csv)); figure_dir.mkdir(parents=True, exist_ok=True)
    cfg = metadata["config"]; sigmas = d["sigma"]
    chosen = [sigmas[0], sigmas[len(sigmas)//2], sigmas[-1]]
    signal = gaussian_lesion(int(cfg["matrix_size"]), cfg["lesion_amplitude"], cfg["lesion_sigma_px"])
    rng = np.random.default_rng(int(cfg["root_seed"]) + 1)
    fig, ax = plt.subplots(1, 3, figsize=(10, 3.3), constrained_layout=True)
    for a, s in zip(ax, chosen):
        im = s * rng.standard_normal(signal.shape) + signal
        a.imshow(im, cmap="gray", vmin=-3*s, vmax=3*s); a.set_title(f"σ={s:.3g}"); a.axis("off")
    fig.savefig(figure_dir / "figure_A_examples.png", dpi=180); plt.close(fig)
    fig, ax = plt.subplots(figsize=(5.5, 4)); ax.plot(sigmas, d["dprime_analytic"], label="analytic")
    ax.plot(sigmas, d["dprime_empirical"], "--", label="Monte Carlo"); ax.axhline(1, color="k", lw=.8)
    ax.set(xscale="log", yscale="log", xlabel="Noise σ", ylabel="d′"); ax.legend(); fig.tight_layout()
    fig.savefig(figure_dir / "figure_B_dprime.png", dpi=180); plt.close(fig)
    metric = "h0_bottleneck_normalized"; t = d[metric]
    fig, ax = plt.subplots(figsize=(5.5, 4)); ax.plot(sigmas, t)
    ax.set(xscale="log", xlabel="Noise σ", ylabel="Mean paired H0 bottleneck / σ")
    fig.tight_layout(); fig.savefig(figure_dir / "figure_C_topology.png", dpi=180); plt.close(fig)
    dn = d["dprime_analytic"] / d["dprime_analytic"].max(); tn = t / t.max()
    fig, ax = plt.subplots(figsize=(5.5, 4)); ax.plot(sigmas, dn, label="normalized d′")
    ax.plot(sigmas, tn, label="normalized T (H0 bottleneck)"); ax.set(xscale="log", xlabel="Noise σ", ylabel="Normalized value")
    ax.legend(); fig.tight_layout(); fig.savefig(figure_dir / "figure_D_normalized.png", dpi=180); plt.close(fig)
    fig, ax = plt.subplots(figsize=(5.5, 4)); sc = ax.scatter(d["dprime_analytic"], t, c=np.log10(sigmas), s=18)
    ax.set(xscale="log", xlabel="d′", ylabel="Mean paired H0 bottleneck / σ")
    fig.colorbar(sc, ax=ax, label="log10 σ"); fig.tight_layout(); fig.savefig(figure_dir / "figure_E_relationship.png", dpi=180); plt.close(fig)
