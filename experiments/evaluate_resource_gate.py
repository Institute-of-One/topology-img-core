from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


CALIBRATION = {
    64: Path("results/resource_calibration/n64/analysis.json"),
    96: Path("results/resource_calibration/n96/analysis.json"),
    128: Path("results/resource_calibration/n128/analysis.json"),
    192: Path("results/refined_sigma_grid_n192/analysis.json"),
}
TARGETS = (160, 224, 256)


def power_law_fit(n: np.ndarray, cost: np.ndarray) -> dict:
    x = np.log(np.asarray(n, float))
    y = np.log(np.asarray(cost, float))
    design = np.column_stack([np.ones_like(x), x])
    intercept, alpha = np.linalg.lstsq(design, y, rcond=None)[0]
    fitted = np.exp(design @ np.array([intercept, alpha]))
    return {
        "coefficient": float(np.exp(intercept)),
        "alpha": float(alpha),
        "fitted": fitted,
        "log_residuals": y - np.log(fitted),
    }


def evaluate(output: Path) -> dict:
    sizes = np.array(sorted(CALIBRATION), float)
    rows = []
    for n in sizes.astype(int):
        values = json.loads(CALIBRATION[n].read_text(encoding="utf-8"))
        rows.append({"matrix_size": n, "wall_time_seconds": values["wall_time_seconds"],
                     "peak_rss_bytes": values["peak_rss_bytes"]})
    wall = np.array([r["wall_time_seconds"] for r in rows])
    memory = np.array([r["peak_rss_bytes"] for r in rows])
    wall_fit = power_law_fit(sizes, wall)
    memory_fit = power_law_fit(sizes, memory)

    predictions = {}
    for n in TARGETS:
        wall_seconds = wall_fit["coefficient"] * n ** wall_fit["alpha"]
        memory_bytes = memory_fit["coefficient"] * n ** memory_fit["alpha"]
        predictions[str(n)] = {
            "wall_time_seconds": float(wall_seconds),
            "wall_time_hours": float(wall_seconds / 3600),
            "peak_rss_bytes": float(memory_bytes),
            "peak_rss_gib": float(memory_bytes / 1024**3),
            "within_12_hours": bool(wall_seconds <= 12 * 3600),
            "within_16_gib": bool(memory_bytes <= 16 * 1024**3),
        }
    gate_pass = predictions["256"]["within_12_hours"] and predictions["256"]["within_16_gib"]
    result = {
        "resource_gate_commit": "6739705fb5e4238d8c08a442cc7f498a65d7a285",
        "n192_data_commit": "13a856cb32b32b99cf99f213c9e4da8860dcdac0",
        "model": "ordinary least squares of log cost on log N using N=64,96,128,192",
        "wall_time_fit": {"coefficient": wall_fit["coefficient"], "alpha": wall_fit["alpha"]},
        "peak_rss_fit": {"coefficient": memory_fit["coefficient"], "alpha": memory_fit["alpha"]},
        "predictions": predictions,
        "n256_gate_pass": bool(gate_pass),
        "selected_fifth_size": 256 if gate_pass else None,
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "analysis.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    with (output / "calibration.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["matrix_size", "wall_time_seconds",
                                                     "peak_rss_bytes", "wall_log_residual",
                                                     "memory_log_residual"])
        writer.writeheader()
        for i, row in enumerate(rows):
            writer.writerow({**row, "wall_log_residual": wall_fit["log_residuals"][i],
                             "memory_log_residual": memory_fit["log_residuals"][i]})
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    grid = np.linspace(64, 256, 200)
    for ax, observed, fit, ylabel in (
        (axes[0], wall / 3600, wall_fit, "Wall time (hours)"),
        (axes[1], memory / 1024**3, memory_fit, "Peak RSS (GiB)"),
    ):
        scale = 3600 if "Wall" in ylabel else 1024**3
        ax.scatter(sizes, observed, label="observed")
        ax.plot(grid, fit["coefficient"] * grid ** fit["alpha"] / scale, label="power-law OLS")
        ax.scatter(TARGETS, [predictions[str(n)]["wall_time_hours" if "Wall" in ylabel else "peak_rss_gib"]
                             for n in TARGETS], marker="x", label="extrapolated")
        ax.set(xlabel="Matrix side N", ylabel=ylabel)
        ax.legend()
    fig.tight_layout()
    fig.savefig(output / "resource_extrapolation.png", dpi=180)
    plt.close(fig)
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/resource_gate"))
    evaluate(parser.parse_args().output)
