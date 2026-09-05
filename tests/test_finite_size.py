from experiments.finite_size_replication import aggregate
from iorn010.metrics import piecewise_breakpoint
import numpy as np


def test_aggregate_groups_conditions():
    rows = [{"matrix_size": 64, "lesion_sigma_px": 3.0, "sigma": 1.0,
             "dprime_analytic": 2.0, "h0_bottleneck_normalized": x,
             "h1_bottleneck_normalized": x / 2} for x in (1.0, 3.0)]
    out = aggregate(rows)
    assert len(out) == 1
    assert out[0]["h0_bottleneck_normalized"] == 2.0


def test_piecewise_accepts_focused_17_point_sweep():
    x = np.geomspace(0.25, 20, 17)
    y = np.exp(-x)
    assert np.isfinite(piecewise_breakpoint(x, y)["breakpoint"])
