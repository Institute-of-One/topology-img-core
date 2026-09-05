from __future__ import annotations
import argparse, json
from pathlib import Path
from iorn010.analysis import analyze
from iorn010.plotting import make_figures
from iorn010.simulation import load_config, run


def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("--config", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("results")); args = p.parse_args()
    raw, agg = run(args.config, args.output)
    cfg = load_config(args.config)
    report = analyze(agg, args.output / "analysis.json", cfg["task_threshold_dprime"], raw)
    metadata = json.loads((args.output / "data" / "metadata.json").read_text(encoding="utf-8"))
    make_figures(agg, args.output / "figures", metadata)
    print(json.dumps(report, indent=2))


if __name__ == "__main__": main()
