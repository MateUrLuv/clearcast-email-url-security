import numpy as np
import pytest

from ml.email_model import build_email_model
from ml.explanations import explain_email, explain_url
from ml.url_model import FEATURE_NAMES, build_url_model, feature_matrix, hostname, url_features


def test_url_features_are_offline_and_validate_input():
    row = url_features("https://login.example.com/account?id=1")
    assert len(row) == len(FEATURE_NAMES)
    assert hostname("example.com/path") == "example.com"
    with pytest.raises(ValueError):
        url_features("javascript:alert(1)")
    with pytest.raises(ValueError):
        url_features("https://bad host/")


def test_email_explanation_matches_linear_score():
    texts = ["verify your account now", "confirm your password now", "meeting agenda for tomorrow", "lunch plans for tomorrow"]
    model = build_email_model().fit(texts, [1, 1, 0, 0])
    text = "verify your password now"
    explanation = explain_email(model, text, limit=100)
    score = model.decision_function([text])[0]
    intercept = model.named_steps["logisticregression"].intercept_[0]
    assert np.isclose(sum(x["contribution"] for x in explanation) + intercept, score, atol=0.005)


def test_url_explanation_matches_linear_score():
    urls = ["https://example.org", "https://school.edu/events", "http://1.2.3.4/login/verify?token=x", "http://account-secure.example.net/password/update"]
    model = build_url_model().fit(urls * 3, [0, 0, 1, 1] * 3)
    url = "http://1.2.3.4/login/verify?token=x"
    explanation = explain_url(model, url, limit=1000)
    assert any(item["feature"].startswith("URL text:") for item in explanation)
    assert any(item["feature"] in FEATURE_NAMES for item in explanation)
    score = model.decision_function([url])[0]
    intercept = model.classifier.intercept_[0]
    assert np.isclose(sum(x["contribution"] for x in explanation) + intercept, score, atol=0.005)
