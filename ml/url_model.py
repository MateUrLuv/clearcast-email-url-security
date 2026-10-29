"""Features observable from a URL string, with no network requests."""
import ipaddress
import re
from urllib.parse import urlsplit

import numpy as np
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

FEATURE_NAMES = (
    "Hostname length", "Hostname dots", "Hostname hyphens",
    "Hostname digits", "Hostname is IP", "Punycode", "Subdomain levels",
    "Path length", "Path depth", "Query length", "Query parameters",
    "At signs", "Percent escapes",
)


def normalized_url(value):
    value = value.strip()
    if not value or any(ch.isspace() for ch in value):
        raise ValueError("Enter one URL without spaces.")
    if "://" not in value:
        if re.match(r"^[a-z][a-z0-9+.-]*:", value, re.I) and not re.match(r"^[^/]+:\d+(?:/|$)", value):
            raise ValueError("Enter an HTTP or HTTPS URL.")
        value = "https://" + value
    parsed = urlsplit(value)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Enter a valid HTTP or HTTPS URL.")
    return value, parsed


def hostname(value):
    return normalized_url(value)[1].hostname.lower()


def url_features(value):
    value, parsed = normalized_url(value)
    host = parsed.hostname.lower()
    try:
        ipaddress.ip_address(host)
        is_ip = 1
    except ValueError:
        is_ip = 0
    labels = host.split(".")
    # Registrable-domain lookup is intentionally avoided to keep inference offline.
    subdomains = max(0, len(labels) - 2)
    raw = np.array([
        len(host), host.count("."), host.count("-"),
        sum(c.isdigit() for c in host), is_ip, int("xn--" in host), subdomains,
        len(parsed.path), parsed.path.count("/"), len(parsed.query),
        parsed.query.count("&") + bool(parsed.query), value.count("@"),
        len(re.findall(r"%[0-9a-fA-F]{2}", value)),
    ], dtype=float)
    caps = np.array([100, 10, 10, 30, 1, 1, 8, 400, 30, 400, 30, 3, 30], dtype=float)
    return np.minimum(raw, caps)


def feature_matrix(urls):
    return np.vstack([url_features(url) for url in urls])


def url_text(value):
    """Drop protocol and leading www so the text model cannot key on HTTPS."""
    value, _ = normalized_url(value)
    return value.lower().removeprefix("https://").removeprefix("http://").removeprefix("www.")


class URLClassifier:
    """One linear model over URL character patterns and structural values."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(3, 5),
                                          min_df=3, max_features=100000, sublinear_tf=True)
        self.scaler = StandardScaler()
        self.classifier = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
        self.numeric_weight = 0.25

    def transform(self, urls):
        urls = list(urls)
        chars = self.vectorizer.transform([url_text(url) for url in urls])
        numbers = self.scaler.transform(feature_matrix(urls)) * self.numeric_weight
        return hstack([chars, csr_matrix(numbers)], format="csr")

    def fit(self, urls, labels):
        urls = list(urls)
        self.vectorizer.fit([url_text(url) for url in urls])
        self.scaler.fit(feature_matrix(urls))
        self.classifier.fit(self.transform(urls), labels)
        return self

    def predict_proba(self, urls):
        return self.classifier.predict_proba(self.transform(urls))

    def predict(self, urls):
        return self.classifier.predict(self.transform(urls))

    def decision_function(self, urls):
        return self.classifier.decision_function(self.transform(urls))


def build_url_model():
    return URLClassifier()
