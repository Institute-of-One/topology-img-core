from __future__ import annotations

import numpy as np
from scipy.stats import chi2


def random_effects_meta(estimates: np.ndarray, variances: np.ndarray) -> dict[str, float]:
    estimates = np.asarray(estimates, float); variances = np.asarray(variances, float)
    if len(estimates) < 2 or np.any(variances <= 0) or not np.isfinite(variances).all():
        raise ValueError("At least two estimates with positive finite variances are required")
    weights = 1.0 / variances; fixed = float(np.sum(weights * estimates) / weights.sum())
    q = float(np.sum(weights * (estimates - fixed) ** 2)); df = len(estimates) - 1
    c = float(weights.sum() - np.sum(weights**2) / weights.sum())
    tau2 = float(max(0.0, (q - df) / c)); re_weights = 1.0 / (variances + tau2)
    pooled = float(np.sum(re_weights * estimates) / re_weights.sum())
    se = float(np.sqrt(1.0 / re_weights.sum()))
    return {"fixed_effect_breakpoint": fixed, "cochran_q": q, "q_df": df,
            "q_p_value": float(chi2.sf(q, df)), "i_squared": float(max(0.0, (q-df)/q)) if q else 0.0,
            "tau_squared": tau2, "tau": float(np.sqrt(tau2)),
            "random_effects_breakpoint": pooled, "random_effects_se": se,
            "random_effects_ci_low": pooled - 1.96*se, "random_effects_ci_high": pooled + 1.96*se,
            "observed_between_run_sd": float(estimates.std(ddof=1)),
            "typical_within_run_se": float(np.sqrt(variances.mean())),
            "between_to_within_ratio": float(estimates.std(ddof=1) / np.sqrt(variances.mean())),
            "breakpoint_min": float(estimates.min()), "breakpoint_max": float(estimates.max())}


def run_level_bootstrap(draws: list[np.ndarray], rng: np.random.Generator, n_boot: int) -> np.ndarray:
    out = np.empty(n_boot); n = len(draws)
    for b in range(n_boot):
        selected = rng.integers(0, n, n)
        out[b] = np.mean([rng.choice(draws[i]) for i in selected])
    return out

