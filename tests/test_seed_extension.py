from experiments.extend_seed_boundary import labeled_seed


def test_labeled_seed_is_reproducible_and_label_specific():
    a=labeled_seed(42,"extension-0.80").generate_state(8)
    b=labeled_seed(42,"extension-0.80").generate_state(8)
    c=labeled_seed(42,"extension-0.90").generate_state(8)
    assert (a==b).all() and not (a==c).all()
