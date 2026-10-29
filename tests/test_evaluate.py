import numpy as np

from ml.evaluate import choose_threshold


def test_threshold_is_selected_from_validation_false_positive_budget():
    labels = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    scores = np.array([0.10, 0.20, 0.40, 0.70, 0.55, 0.65, 0.80, 0.90])
    threshold = choose_threshold(labels, scores, max_false_positive_rate=0.0)
    assert threshold > 0.70
    assert np.mean(scores[labels == 0] >= threshold) == 0.0
