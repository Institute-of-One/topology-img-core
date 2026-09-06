import numpy as np
from iorn010.heterogeneity import random_effects_meta, run_level_bootstrap


def test_random_effects_detects_heterogeneity():
    result=random_effects_meta(np.array([1.0,1.1,1.8,1.9,2.0]),np.repeat(.01,5))
    assert result["tau"]>0 and result["q_p_value"]<.05 and result["i_squared"]>0


def test_run_level_bootstrap_is_reproducible():
    draws=[np.array([1.0,1.1]),np.array([1.5,1.6])]
    a=run_level_bootstrap(draws,np.random.default_rng(3),20);b=run_level_bootstrap(draws,np.random.default_rng(3),20)
    assert np.array_equal(a,b)
