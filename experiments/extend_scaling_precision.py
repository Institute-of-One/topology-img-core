from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import time

import matplotlib.pyplot as plt
import numpy as np

from iorn010.observers import ideal_dprime
from iorn010.phantom import gaussian_lesion
from iorn010.refined import bootstrap_breakpoint
from iorn010.topology import bottleneck, persistence_diagrams


AMENDMENT_COMMIT = "cc961f9be19ad557aaaf09c7596c4fd3989aead2"
CANDIDATES = np.round(np.arange(0.8, 2.51, 0.1), 2)
ANCHORS = {0.5, 0.75, 3.0, 4.0, 8.0}


def labeled_seed(root_seed: int, sigma: float, replicate: int) -> np.random.SeedSequence:
    label = f"scaling-precision-extension|sigma={sigma:.2f}|replicate={replicate}"
    digest = hashlib.sha256(f"{root_seed}|{label}".encode()).digest()
    words = np.frombuffer(digest[:16], dtype=np.uint32).astype(np.uint64).tolist()
    return np.random.SeedSequence([root_seed, *words])


def atomic_npz(path: Path, **arrays: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.npz")
    np.savez_compressed(tmp, **arrays)
    os.replace(tmp, path)


def read_groups(path: Path) -> tuple[dict[float, np.ndarray], dict[float, np.ndarray]]:
    h0: dict[float, list[float]] = {}
    h1: dict[float, list[float]] = {}
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            sigma = float(row["sigma"])
            h0.setdefault(sigma, []).append(float(row["h0_bottleneck_normalized"]))
            h1.setdefault(sigma, []).append(float(row["h1_bottleneck_normalized"]))
    return ({s: np.asarray(v) for s, v in h0.items()},
            {s: np.asarray(v) for s, v in h1.items()})


def generate(root_seed: int, matrix_size: int, sigma: float, start: int,
             count: int, path: Path) -> tuple[np.ndarray, np.ndarray]:
    if path.exists():
        saved = np.load(path)
        return saved["h0"], saved["h1"]
    signal = gaussian_lesion(matrix_size, 1.0, 5.0)
    h0 = np.empty(count)
    h1 = np.empty(count)
    for offset in range(count):
        replicate = start + offset
        rng = np.random.default_rng(labeled_seed(root_seed, sigma, replicate))
        noise = sigma * rng.standard_normal(signal.shape)
        absent = persistence_diagrams(noise)
        present = persistence_diagrams(noise + signal)
        h0[offset] = bottleneck(absent[0], present[0]) / sigma
        h1[offset] = bottleneck(absent[1], present[1]) / sigma
    atomic_npz(path, sigma=np.array(sigma), start=np.array(start), h0=h0, h1=h1)
    return h0, h1


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(base: Path, output: Path, matrix_size: int, root_seed: int) -> dict:
    groups_h0, groups_h1 = read_groups(base / "data" / "refined_sigma_raw.csv")
    target_dense = 64 if matrix_size == 64 else 128
    started = time.perf_counter()
    added = 0
    for sigma in CANDIDATES:
        sigma = float(sigma)
        current = len(groups_h0.get(sigma, []))
        count = target_dense - current
        if count <= 0:
            continue
        checkpoint = output / "extension_checkpoints" / f"sigma_{sigma:.2f}_start_{current}.npz"
        h0, h1 = generate(root_seed, matrix_size, sigma, current, count, checkpoint)
        groups_h0[sigma] = np.concatenate([groups_h0.get(sigma, np.empty(0)), h0])
        groups_h1[sigma] = np.concatenate([groups_h1.get(sigma, np.empty(0)), h1])
        added += count
        print(f"sigma={sigma:.2f} added={count} total={len(groups_h0[sigma])}", flush=True)

    sigmas = np.array(sorted(groups_h0))
    ordered = [groups_h0[float(s)] for s in sigmas]
    fit, draws = bootstrap_breakpoint(
        sigmas, ordered, CANDIDATES, np.random.default_rng(root_seed + 1), 500
    )
    signal = gaussian_lesion(matrix_size, 1.0, 5.0)
    fit.update({
        "matrix_size": matrix_size,
        "breakpoint_candidate_low": 0.8,
        "breakpoint_candidate_high": 2.5,
        "breakpoint_interval_touches_boundary": bool(
            fit["breakpoint_ci_low"] <= 0.8 or fit["breakpoint_ci_high"] >= 2.5
        ),
        "precision_adequate": bool(
            fit["breakpoint_ci_width"] <= 0.4
            and fit["breakpoint_ci_low"] > 0.8
            and fit["breakpoint_ci_high"] < 2.5
        ),
        "dprime_at_breakpoint": ideal_dprime(signal, fit["breakpoint_sigma"]),
        "extension_realizations": added,
        "extension_wall_time_seconds": time.perf_counter() - started,
        "complete_realizations": int(sum(map(len, ordered))),
        "amendment_commit": AMENDMENT_COMMIT,
    })

    raw_rows = []
    aggregate_rows = []
    for sigma in sigmas:
        s = float(sigma)
        h0 = groups_h0[s]
        h1 = groups_h1[s]
        for j, (v0, v1) in enumerate(zip(h0, h1)):
            raw_rows.append({"sigma": s, "realization": j,
                             "dprime_analytic": ideal_dprime(signal, s),
                             "h0_bottleneck_normalized": float(v0),
                             "h1_bottleneck_normalized": float(v1)})
        aggregate_rows.append({"sigma": s, "n_pairs": len(h0),
                               "dprime_analytic": ideal_dprime(signal, s),
                               "h0_bottleneck_normalized": float(h0.mean()),
                               "h0_standard_error": float(h0.std(ddof=1) / np.sqrt(len(h0)))})
    write_csv(output / "data" / "refined_sigma_raw.csv", raw_rows)
    write_csv(output / "data" / "refined_sigma_aggregate.csv", aggregate_rows)
    (output / "data" / "breakpoint_bootstrap.csv").write_text(
        "breakpoint_sigma\n" + "\n".join(map(str, draws)) + "\n", encoding="utf-8"
    )
    (output / "analysis.json").write_text(json.dumps(fit, indent=2), encoding="utf-8")
    metadata = {"base": str(base), "matrix_size": matrix_size, "root_seed": root_seed,
                "amendment_commit": AMENDMENT_COMMIT,
                "stream_label": "scaling-precision-extension|sigma={sigma:.2f}|replicate={replicate}"}
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    figures = output / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    means = np.array([g.mean() for g in ordered])
    ses = np.array([g.std(ddof=1) / np.sqrt(len(g)) for g in ordered])
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.errorbar(sigmas, means / means.max(), yerr=ses / means.max(), marker="o", ms=3)
    ax.axvline(fit["breakpoint_sigma"], color="tab:red", ls="--")
    ax.axvspan(fit["breakpoint_ci_low"], fit["breakpoint_ci_high"], color="tab:red", alpha=.15)
    ax.set(xscale="log", xlabel="Noise sigma", ylabel="Normalized mean H0 bottleneck / sigma")
    fig.tight_layout()
    fig.savefig(figures / "figure_extended_breakpoint.png", dpi=180)
    plt.close(fig)
    print(json.dumps(fit, indent=2))
    return fit


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--matrix-size", type=int, choices=(64, 96), required=True)
    parser.add_argument("--root-seed", type=int, required=True)
    args = parser.parse_args()
    run(args.base, args.output, args.matrix_size, args.root_seed)
