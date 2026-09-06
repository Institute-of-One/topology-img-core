from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from iorn010.heterogeneity import random_effects_meta, run_level_bootstrap
from iorn010.phantom import gaussian_lesion
from iorn010.refined import bootstrap_breakpoint
from iorn010.topology import bottleneck, persistence_diagrams


SEEDS = [20260906, 20260916, 20260926, 20261006, 20261016]
EXTENSION_SIGMAS = [0.8, 0.9]


def labeled_seed(root_seed: int, label: str) -> np.random.SeedSequence:
    digest = hashlib.sha256(f"{root_seed}|{label}".encode()).digest()
    words = np.frombuffer(digest[:16], dtype=np.uint32).astype(np.uint64).tolist()
    return np.random.SeedSequence([root_seed, *words])


def atomic_npz(path: Path, **arrays: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); tmp=path.with_suffix(".tmp.npz")
    np.savez_compressed(tmp,**arrays);os.replace(tmp,path)


def read_raw(path: Path) -> list[dict]:
    with path.open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def generate_extension(seed: int, sigma: float, path: Path, n: int=64) -> tuple[np.ndarray,np.ndarray]:
    if path.exists():
        saved=np.load(path);return saved["h0"],saved["h1"]
    signal=gaussian_lesion(128,1.0,5.0);rng=np.random.default_rng(labeled_seed(seed,f"extension-{sigma:.2f}"))
    h0=np.empty(n);h1=np.empty(n)
    for j in range(n):
        noise=sigma*rng.standard_normal(signal.shape);a=persistence_diagrams(noise);p=persistence_diagrams(noise+signal)
        h0[j]=bottleneck(a[0],p[0])/sigma;h1[j]=bottleneck(a[1],p[1])/sigma
    atomic_npz(path,seed=np.array(seed),sigma=np.array(sigma),h0=h0,h1=h1);return h0,h1


def main() -> None:
    p=argparse.ArgumentParser();p.add_argument("--existing-run",type=Path,required=True)
    p.add_argument("--seed-root",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    all_rows=[];run_rows=[];all_draws=[];extension_rows=[]
    for seed in SEEDS:
        base=a.existing_run if seed==SEEDS[0] else a.seed_root/"runs"/f"seed_{seed}"
        rows=read_raw(base/"data"/"refined_sigma_raw.csv")
        groups={s:np.array([float(r["h0_bottleneck_normalized"]) for r in rows if float(r["sigma"])==s]) for s in sorted({float(r["sigma"]) for r in rows})}
        for sigma in EXTENSION_SIGMAS:
            checkpoint=a.output/"extensions"/f"seed_{seed}_sigma_{sigma:.2f}.npz"
            h0,h1=generate_extension(seed,sigma,checkpoint)
            groups[sigma]=h0
            for j,(v0,v1) in enumerate(zip(h0,h1)):
                extension_rows.append({"seed":seed,"sigma":sigma,"realization":j,"h0_bottleneck_normalized":float(v0),"h1_bottleneck_normalized":float(v1)})
        sigmas=np.array(sorted(groups));ordered=[groups[s] for s in sigmas]
        fit,draws=bootstrap_breakpoint(sigmas,ordered,np.arange(.8,2.51,.1),np.random.default_rng(seed+1),500)
        row={"seed":seed,"breakpoint_sigma":fit["breakpoint_sigma"],"within_bootstrap_variance":float(draws.var(ddof=1)),"ci_low":fit["breakpoint_ci_low"],"ci_high":fit["breakpoint_ci_high"],"ci_width":fit["breakpoint_ci_width"]}
        run_rows.append(row);all_draws.append(draws);print(json.dumps(row),flush=True)
    estimates=np.array([r["breakpoint_sigma"] for r in run_rows]);variances=np.array([r["within_bootstrap_variance"] for r in run_rows])
    result=random_effects_meta(estimates,variances);sensitivity=run_level_bootstrap(all_draws,np.random.default_rng(2026090602),10000)
    lo,hi=np.quantile(sensitivity,[.025,.975]);result.update({"run_level_bootstrap_ci_low":float(lo),"run_level_bootstrap_ci_high":float(hi),"complete_runs":5,"extension_realizations":len(extension_rows),"amendment_commit":"419c37ba1d47a4aebf40c2be1b1a3a05be293000"})
    result["within_uncertainty_adequate"]=bool(result["q_p_value"]>=.05 and result["tau"]<=.10)
    result["material_between_run_heterogeneity"]=not result["within_uncertainty_adequate"]
    result["inconclusive"]=bool(any(r["ci_width"]>.40 or r["ci_low"]<=.8 or r["ci_high"]>=2.5 for r in run_rows))
    write_csv(a.output/"data"/"run_estimates_extended.csv",run_rows);write_csv(a.output/"data"/"boundary_extension_raw.csv",extension_rows)
    np.savez_compressed(a.output/"data"/"bootstrap_draws_extended.npz",**{f"seed_{r['seed']}":d for r,d in zip(run_rows,all_draws)},run_level=sensitivity)
    (a.output/"analysis_extended.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    figdir=a.output/"figures";figdir.mkdir(parents=True,exist_ok=True);fig,ax=plt.subplots(figsize=(6,4));y=np.arange(5);x=estimates;low=x-np.array([r["ci_low"] for r in run_rows]);high=np.array([r["ci_high"] for r in run_rows])-x
    ax.errorbar(x,y,xerr=np.vstack([low,high]),fmt="o",capsize=4);ax.axvline(result["random_effects_breakpoint"],color="tab:red",ls="--",label="random-effects estimate");ax.set(yticks=y,yticklabels=SEEDS,xlabel="Breakpoint σ",ylabel="Root seed");ax.legend();fig.tight_layout();fig.savefig(figdir/"figure_N_seed_forest_extended.png",dpi=180);plt.close(fig)
    print(json.dumps(result,indent=2))


if __name__=="__main__":main()

