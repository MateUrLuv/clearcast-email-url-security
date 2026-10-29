"""Download public corpora, train both models, and save held-out evaluation."""
import hashlib
import json
import urllib.request
from pathlib import Path

import joblib
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, train_test_split

from .email_model import build_email_model
from .email_data import prepare_email_data
from .evaluate import evaluate, choose_threshold
from .explanations import explain_email, explain_url
from .url_model import build_url_model, hostname

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SOURCES = {
    "Nazario.csv": "https://zenodo.org/api/records/8339691/files/Nazario.csv/content",
    "SpamAssasin.csv": "https://zenodo.org/api/records/8339691/files/SpamAssasin.csv/content",
    "Enron.csv": "https://zenodo.org/api/records/8339691/files/Enron.csv/content",
    "Ling.csv": "https://zenodo.org/api/records/8339691/files/Ling.csv/content",
    "email_validation.csv": "https://zenodo.org/api/records/13474746/files/Phishing_validation_emails.csv/content",
    "urls_better.csv": "https://zenodo.org/api/records/19371661/files/urls_dataset.csv/content",
}


def download():
    RAW.mkdir(parents=True, exist_ok=True)
    for name, url in SOURCES.items():
        target = RAW / name
        if not target.exists():
            print(f"Downloading {name}...")
            urllib.request.urlretrieve(url, target)


def train_email():
    data = prepare_email_data(RAW)
    train, test = train_test_split(data, test_size=0.2, random_state=42, stratify=data.label)
    model = build_email_model().fit(train.text, train.label)
    report = evaluate(model, test.text, test.label.to_numpy(), test.digest, "email")
    report["training_count"] = len(train)
    report["unique_source_counts"] = data.groupby(["source", "label"]).size().rename("count").reset_index().to_dict("records")
    by_id = dict(zip(test.digest, test.text))
    report["error_review"] = {kind: [{"id": item["id"], "top_model_terms": explain_email(model, by_id[item["id"]], 4)}
                                      for item in report["errors"][kind][:3]]
                              for kind in ("false_positives", "false_negatives")}
    joblib.dump(model, ROOT / "artifacts" / "email_model.joblib", compress=3)
    return report


def train_url():
    data = pd.read_csv(RAW / "urls_better.csv", usecols=["url", "label"]).rename(columns={"url": "URL"})
    data = data.dropna().drop_duplicates("URL").copy()
    data["phishing"] = data.label.astype(int)
    # Cap the sample before feature extraction for a reproducible laptop-sized project.
    data = pd.concat([part.sample(n=min(16000, len(part)), random_state=42) for _, part in data.groupby("phishing")], ignore_index=True)
    def safe_hostname(url):
        try:
            return hostname(url)
        except ValueError:
            return None
    data["hostname"] = data.URL.map(safe_hostname)
    data = data.dropna(subset=["hostname"]).reset_index(drop=True)
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(splitter.split(data, data.phishing, groups=data.hostname))
    remaining, test = data.iloc[train_idx], data.iloc[test_idx]
    train_idx, validation_idx = next(splitter.split(remaining, remaining.phishing, groups=remaining.hostname))
    train, validation = remaining.iloc[train_idx], remaining.iloc[validation_idx]
    model = build_url_model().fit(train.URL, train.phishing)
    validation_scores = model.predict_proba(validation.URL)[:, 1]
    threshold = choose_threshold(validation.phishing.to_numpy(), validation_scores)
    report = evaluate(model, test.URL, test.phishing.to_numpy(), test.URL.map(lambda u: hashlib.sha256(u.encode()).hexdigest()[:16]), "url", threshold)
    report["training_count"] = len(train)
    report["validation_count"] = len(validation)
    report["validation_fpr_limit"] = 0.03
    report["hostname_overlap"] = len(set(train.hostname) & set(test.hostname) | set(train.hostname) & set(validation.hostname) | set(test.hostname) & set(validation.hostname))
    by_id = {hashlib.sha256(url.encode()).hexdigest()[:16]: url for url in test.URL}
    report["error_review"] = {kind: [{"id": item["id"], "top_model_features": explain_url(model, by_id[item["id"]], 4)}
                                      for item in report["errors"][kind][:3]]
                              for kind in ("false_positives", "false_negatives")}
    joblib.dump(model, ROOT / "artifacts" / "url_model.joblib", compress=3)
    return report


def main():
    download()
    (ROOT / "artifacts").mkdir(exist_ok=True)
    (ROOT / "reports").mkdir(exist_ok=True)
    report = {"email": train_email(), "url": train_url(), "target": "1 means phishing", "threshold": {"email": 0.5, "url": None},
              "limitations": ["Email sources still correlate with labels; the mixed-class source contains only 100 unique messages after deduplication.",
                              "Historical corpora and a balanced URL sample do not reflect current prevalence or attacks.",
                              "The URL model still has a substantial false-positive rate; review positive results manually."]}
    report["threshold"]["url"] = report["url"]["threshold"]
    (ROOT / "reports" / "held_out.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
