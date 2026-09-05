import numpy as np

from iorn010.refined import bootstrap_breakpoint, segmented_fit


def test_segmented_fit_recovers_grid_knot():
    x = np.arange(0.5, 3.1, 0.1); knot = 1.7; z = np.log(x)
    y = 2 - .4*z - 1.2*np.maximum(z-np.log(knot), 0)
    fit = segmented_fit(x, y, np.arange(1.0, 2.51, .1))
    assert np.isclose(fit["breakpoint_sigma"], knot)


def test_bootstrap_reports_interval():
    x=np.arange(.5,3.1,.1); groups=[np.repeat(np.exp(-s),8) for s in x]
    fit, draws=bootstrap_breakpoint(x,groups,np.arange(1,2.51,.1),np.random.default_rng(1),20)
    assert len(draws)==20 and fit["breakpoint_ci_low"] <= fit["breakpoint_sigma"] <= fit["breakpoint_ci_high"]
