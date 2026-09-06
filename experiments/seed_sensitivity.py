from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import tomllib

import matplotlib.pyplot as plt
import numpy as np

from experiments.refined_sigma_grid import run as run_refined
from iorn010.heterogeneity import random_effects_meta, run_level_bootstrap


def load_run(path: Path, seed: int) -> tuple[dict, np.ndarray]:
    analysis = json.loads((path / "analysis.json").read_text(encoding="utf-8"))
    with (path / "data" / "breakpoint_bootstrap.csv").open(newline="", encoding="utf-8") as f:
        draws = np.array([float(r["breakpoint_sigma"]) for r in csv.DictReader(f)])
    return {"seed": seed, "breakpoint_sigma": analysis["breakpoint_sigma"],
            "within_bootstrap_variance": float(draws.var(ddof=1)),
            "ci_low": analysis["breakpoint_ci_low"], "ci_high": analysis["breakpoint_ci_high"],
            "ci_width": analysis["breakpoint_ci_width"]}, draws


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def main() -> None:
    parser=argparse.ArgumentParser();parser.add_argument("--config",type=Path,required=True)
    parser.add_argument("--refined-config",type=Path,required=True);parser.add_argument("--existing-run",type=Path,required=True)
    parser.add_argument("--output",type=Path,default=Path("results/seed_sensitivity"));args=parser.parse_args()
    with args.config.open("rb") as f: cfg=tomllib.load(f)["experiment"]
    rows=[]; all_draws=[]
    row,draws=load_run(args.existing_run,int(cfg["existing_seed"]));rows.append(row);all_draws.append(draws)
    for seed in cfg["additional_seeds"]:
        run_dir=args.output/"runs"/f"seed_{seed}"
        run_refined(args.refined_config,run_dir,root_seed_override=int(seed))
        row,draws=load_run(run_dir,int(seed));rows.append(row);all_draws.append(draws)
    estimates=np.array([r["breakpoint_sigma"] for r in rows]);variances=np.array([r["within_bootstrap_variance"] for r in rows])
    meta=random_effects_meta(estimates,variances)
    sensitivity=run_level_bootstrap(all_draws,np.random.default_rng(2026090601),int(cfg["run_level_bootstrap_resamples"]))
    slo,shi=np.quantile(sensitivity,[.025,.975]);meta["run_level_bootstrap_ci_low"]=float(slo);meta["run_level_bootstrap_ci_high"]=float(shi)
    meta["within_uncertainty_adequate"] = bool(meta["q_p_value"] >= cfg["heterogeneity_alpha"] and meta["tau"] <= cfg["material_tau_threshold"])
    meta["material_between_run_heterogeneity"] = not meta["within_uncertainty_adequate"]
    meta["complete_runs"]=len(rows);meta["amendment_commit"]=cfg["amendment_commit"]
    meta["inconclusive"] = bool(len(rows)<4 or any(r["ci_width"]>0.40 or r["ci_low"]<=1.0 or r["ci_high"]>=2.5 for r in rows))
    write_csv(args.output/"data"/"run_estimates.csv",rows)
    (args.output/"data").mkdir(parents=True,exist_ok=True);np.savez_compressed(args.output/"data"/"within_run_bootstrap_draws.npz",**{f"seed_{r['seed']}":d for r,d in zip(rows,all_draws)},run_level=sensitivity)
    (args.output/"analysis.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
    figures=args.output/"figures";figures.mkdir(parents=True,exist_ok=True)
    fig,ax=plt.subplots(figsize=(6,4));y=np.arange(len(rows));x=np.array([r["breakpoint_sigma"] for r in rows]);lo=x-np.array([r["ci_low"] for r in rows]);hi=np.array([r["ci_high"] for r in rows])-x
    ax.errorbar(x,y,xerr=np.vstack([lo,hi]),fmt="o",capsize=4);ax.axvline(meta["random_effects_breakpoint"],color="tab:red",ls="--",label="random-effects estimate")
    ax.set(yticks=y,yticklabels=[str(r["seed"]) for r in rows],xlabel="Breakpoint σ",ylabel="Root seed");ax.legend();fig.tight_layout();fig.savefig(figures/"figure_L_seed_forest.png",dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(6,4));ax.hist(sensitivity,bins=30);ax.set(xlabel="Run-level bootstrap mean breakpoint σ",ylabel="Count");fig.tight_layout();fig.savefig(figures/"figure_M_run_level_bootstrap.png",dpi=180);plt.close(fig)
    print(json.dumps(meta,indent=2))


if __name__=="__main__":main()

