from experiments.refined_sigma_grid import peak_rss_bytes


def test_peak_rss_is_positive_and_identifies_method():
    peak, method = peak_rss_bytes()
    assert peak > 0
    assert method
