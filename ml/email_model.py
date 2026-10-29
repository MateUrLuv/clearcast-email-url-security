"""Email-only TF-IDF phishing classifier."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline


def build_email_model():
    return make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_df=0.98,
                        max_features=30000, sublinear_tf=True, strip_accents="unicode"),
        LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
    )


def email_text(subject, body):
    return f"{subject or ''}\n{body or ''}".strip()
