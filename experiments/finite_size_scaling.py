from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize_scalar

from iorn010.phantom import gaussian_lesion


SIZES = np.array([64, 96, 128, 192, 256], float)
TAU_SIGMA = 0.08854267658347979
BOOTSTRAP_REPLICATES = 2000


def read_csv_draws(path: Path) -> np.ndarray:
    with path.open(newline="", encoding="utf-8") as stream:
        return np.array([float(r["breakpoint_sigma"]) for r in csv.DictReader(stream)])


def load_draws() -> dict[int, np.ndarray]:
    seed = np.load("results/seed_sensitivity/data/bootstrap_draws_extended.npz")
    return {
        64: read_csv_draws(Path("results/refined_sigma_grid_n64_extended/data/breakpoint_bootstrap.csv")),
        96: read_csv_draws(Path("results/refined_sigma_grid_n96_extended/data/breakpoint_bootstrap.csv")),
        128: np.asarray(seed["seed_20260906"], float),
        192: read_csv_draws(Path("results/refined_sigma_grid_n192/data/breakpoint_bootstrap.csv")),
        256: read_csv_draws(Path("results/refined_sigma_grid_n256/data/breakpoint_bootstrap.csv")),
    }


def aicc(rss: float, n: int, k: int) -> float:
    if n - k - 1 <= 0:
        return float("inf")
    return float(n * np.log(max(rss / n, 1e-300)) + 2*k + 2*k*(k+1)/(n-k-1))


def fit_models(n: np.ndarray, y: np.ndarray, se: np.ndarray) -> dict:
    weights = 1 / np.square(se)
    constant = float(np.sum(weights * y) / np.sum(weights))
    rss_constant = float(np.sum(np.square((y - constant) / se)))

    design = np.column_stack([np.ones_like(n), np.log(n)])
    weighted_design = design / se[:, None]
    b0, b1 = np.linalg.lstsq(weighted_design, y / se, rcond=None)[0]
    pred_log = b0 + b1 * np.log(n)
    rss_log = float(np.sum(np.square((y - pred_log) / se)))

    def profiled(log_omega: float) -> tuple[float, float, float, float]:
        omega = float(np.exp(log_omega))
        conv_design = np.column_stack([np.ones_like(n), n ** (-omega)])
        parameters = np.linalg.lstsq(conv_design / se[:, None], y / se, rcond=None)[0]
        fitted = conv_design @ parameters
        rss = float(np.sum(np.square((y - fitted) / se)))
        return rss, float(parameters[0]), float(parameters[1]), omega

    optimized = minimize_scalar(lambda z: profiled(z)[0],
                                bounds=(np.log(1e-6), np.log(10.0)),
                                method="bounded", options={"xatol": 1e-8})
    rss_convergent, y_inf, amplitude, omega = profiled(float(optimized.x))
    if not np.all(np.isfinite([rss_convergent, y_inf, amplitude, omega])):
        raise RuntimeError("convergent-model optimization failed")

    models = {
        "constant": {"parameters": {"c": constant}, "rss": rss_constant,
                     "aicc": aicc(rss_constant, len(n), 1)},
        "log_drift": {"parameters": {"b0": float(b0), "b1": float(b1)}, "rss": rss_log,
                      "aicc": aicc(rss_log, len(n), 2)},
        "convergent": {"parameters": {"y_inf": y_inf, "a": amplitude, "omega": omega},
                       "rss": rss_convergent, "aicc": aicc(rss_convergent, len(n), 3)},
    }
    return models


def analyze_quantity(name: str, values: np.ndarray, draws: list[np.ndarray],
                     rng: np.random.Generator, add_tau: bool = False) -> dict:
    se = np.array([d.std(ddof=1) for d in draws])
    if name == "q":
        norms = np.array([np.linalg.norm(gaussian_lesion(int(n), 1.0, 5.0)) for n in SIZES])
        sigma_values = values.copy()
        values = norms / sigma_values
        se = np.array([norm * d.std(ddof=1) / sigma**2
                       for norm, d, sigma in zip(norms, draws, sigma_values)])
    models = fit_models(SIZES, values, se)
    records = []
    failures = 0
    for _ in range(BOOTSTRAP_REPLICATES):
        sigma_sample = np.array([rng.choice(d) for d in draws])
        if add_tau:
            sigma_sample = np.maximum(0.05, sigma_sample + rng.normal(0, TAU_SIGMA, len(SIZES)))
        sample = sigma_sample
        if name == "q":
            sample = norms / sigma_sample
        try:
            fitted = fit_models(SIZES, sample, se)
            p = fitted["convergent"]["parameters"]
            records.append([p["omega"], p["y_inf"], p["a"],
                            fitted["convergent"]["aicc"], fitted["log_drift"]["aicc"]])
        except (RuntimeError, ValueError, FloatingPointError):
            failures += 1
    records = np.asarray(records)
    conv = models["convergent"]
    minimum_aicc = min(m["aicc"] for m in models.values())
    observed_range = float(np.ptp(values[[2, 3, 4]]))
    rule_a = bool(models["constant"]["aicc"] <= minimum_aicc + 2
                  and observed_range <= 0.10 * abs(models["constant"]["parameters"]["c"]))
    omega_ci = np.quantile(records[:, 0], [.025, .975]) if len(records) else [np.nan, np.nan]
    y_inf_ci = np.quantile(records[:, 1], [.025, .975]) if len(records) else [np.nan, np.nan]
    p = conv["parameters"]
    rule_b = bool(
        conv["aicc"] <= models["log_drift"]["aicc"] - 6
        and omega_ci[0] > 0
        and (y_inf_ci[1] - y_inf_ci[0]) <= .20 * abs(p["y_inf"])
        and abs(p["a"] * 256 ** (-p["omega"])) <= .10 * abs(p["y_inf"])
    )
    return {
        "values": values.tolist(), "standard_errors": se.tolist(), "models": models,
        "observed_range_n128_n256": observed_range,
        "rule_a": rule_a, "rule_b": rule_b,
        "omega_ci": list(map(float, omega_ci)), "y_inf_ci": list(map(float, y_inf_ci)),
        "optimization_failures": failures,
        "optimization_failure_fraction": failures / BOOTSTRAP_REPLICATES,
        "seed_floor_sensitivity": add_tau,
    }


def main() -> None:
    draws_by_size = load_draws()
    draws = [draws_by_size[int(n)] for n in SIZES]
    points = np.array([1.6, 1.2, 1.3, 1.2, 1.1])
    primary_rng = np.random.default_rng(2026090603)
    sigma = analyze_quantity("sigma", points, draws, primary_rng)
    q = analyze_quantity("q", points, draws, primary_rng)
    sensitivity_rng = np.random.default_rng(2026090604)
    sigma_sensitivity = analyze_quantity("sigma", points, draws, sensitivity_rng, add_tau=True)
    q_sensitivity = analyze_quantity("q", points, draws, sensitivity_rng, add_tau=True)
    inconclusive = bool(sigma["optimization_failure_fraction"] > .05
                        or q["optimization_failure_fraction"] > .05)
    if inconclusive:
        outcome = "inconclusive"
    elif sigma["rule_a"] or sigma["rule_b"]:
        outcome = "outcome_1" if (q["rule_a"] or q["rule_b"]) else "outcome_2"
    else:
        outcome = "outcome_3"
    result = {
        "sizes": SIZES.astype(int).tolist(), "breakpoint_points": points.tolist(),
        "bootstrap_replicates": BOOTSTRAP_REPLICATES, "seed_noise_floor_tau_sigma": TAU_SIGMA,
        "primary_sigma": sigma, "primary_q": q,
        "tau_sensitivity_sigma": sigma_sensitivity, "tau_sensitivity_q": q_sensitivity,
        "preregistered_outcome": outcome,
    }
    output = Path("results/finite_size_scaling")
    output.mkdir(parents=True, exist_ok=True)
    (output / "analysis.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    axes[0].errorbar(SIZES, sigma["values"], yerr=sigma["standard_errors"], marker="o", capsize=3)
    axes[0].set(xlabel="Matrix side N", ylabel="Breakpoint sigma")
    axes[1].errorbar(SIZES, q["values"], yerr=q["standard_errors"], marker="o", capsize=3)
    axes[1].set(xlabel="Matrix side N", ylabel="d-prime at breakpoint")
    fig.tight_layout()
    fig.savefig(output / "finite_size_order_parameters.png", dpi=180)
    plt.close(fig)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
