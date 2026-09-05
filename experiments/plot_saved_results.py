from __future__ import annotations
import argparse, json
from pathlib import Path
from iorn010.plotting import make_figures

p = argparse.ArgumentParser(); p.add_argument("--results", type=Path, required=True)
args = p.parse_args(); root = args.results.parent.parent
meta = json.loads((root / "data" / "metadata.json").read_text(encoding="utf-8"))
make_figures(args.results, root / "figures", meta)

