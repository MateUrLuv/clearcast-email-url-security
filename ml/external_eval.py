"""Independent-source stress tests; no external examples are used for fitting."""
import hashlib
import json
import urllib.request

import joblib
import pandas as pd
import pyarrow.parquet as parquet

from .email_data import prepare_email_data, text_digest
from .evaluate import evaluate
from .train import RAW, ROOT
from .url_model import hostname

EXTERNAL_SOURCES = {
    "phresh_test_000.parquet": "https://huggingface.co/datasets/phreshphish/phreshphish/resolve/main/data/test-000.parquet",
    "email_external.xlsx": "https://zenodo.org/api/records/15235123/files/phishing_nlp_dataset.xlsx/content",
}


def download_external():
    RAW.mkdir(parents=True, exist_ok=True)
    for name, url in EXTERNAL_SOURCES.items():
        target = RAW / name
        if not target.exists():
            print(f"Downloading {name}...")
            urllib.request.urlretrieve(url, target)


def external_urls(threshold):
    source = pd.read_csv(RAW / "urls_better.csv", usecols=["url"]).dropna().drop_duplicates()
    seen_urls = set(source.url)
    seen_hosts = set()
    for url in source.url:
        try:
            seen_hosts.add(hostname(url))
        except ValueError:
            pass
    frame = parquet.read_table(RAW / "phresh_test_000.parquet", columns=["url", "label"]).to_pandas()
    original_count = len(frame)
    rows = []
    for url, label in zip(frame.url, frame.label):
        if label not in ("benign", "phish") or not isinstance(url, str):
            continue
        try:
            host = hostname(url)
        except ValueError:
            continue
        if url in seen_urls or host in seen_hosts:
            continue
        rows.append((url, int(label == "phish")))
    model = joblib.load(ROOT / "artifacts" / "url_model.joblib")
    urls = [url for url, _ in rows]
    report = evaluate(model, urls, [label for _, label in rows],
                      [hashlib.sha256(url.encode()).hexdigest()[:16] for url in urls], "url_external", threshold)
    report.update({"source": EXTERNAL_SOURCES["phresh_test_000.parquet"],
                   "source_count": original_count, "excluded_seen_or_invalid": original_count - len(rows),
                   "hostname_overlap_with_training_source": 0})
    return report


def external_emails():
    training_digests = set(prepare_email_data(RAW).digest)
    frame = pd.read_excel(RAW / "email_external.xlsx", dtype=str)
    original_count = len(frame)
    rows = []
    for raw in frame.Corpus.fillna(""):
        parts = raw.rsplit("\t", 1)
        if len(parts) != 2:
            continue
        content, label = parts[0].strip(), parts[1].strip()
        if label not in ("Phishing", "NOT-Malicious General Class") or len(content) < 20:
            continue
        digest = text_digest(content)
        if digest not in training_digests:
            rows.append((content, int(label == "Phishing"), digest))
    model = joblib.load(ROOT / "artifacts" / "email_model.joblib")
    report = evaluate(model, [text for text, _, _ in rows], [label for _, label, _ in rows],
                      [digest for _, _, digest in rows], "email_external")
    report.update({"source": EXTERNAL_SOURCES["email_external.xlsx"],
                   "source_count": original_count, "excluded_other_classes_or_invalid_or_seen": original_count - len(rows),
                   "training_text_overlap": 0,
                   "note": "Only Phishing and NOT-Malicious General Class messages are in scope; other malicious classes are excluded."})
    return report


def main():
    download_external()
    benchmark = json.loads((ROOT / "reports" / "held_out.json").read_text())
    report = {"url": external_urls(benchmark["url"]["threshold"]),
              "email": external_emails(),
              "limitations": ["These datasets differ in collection process and prevalence from the training data.",
                              "The email external set includes email- and SMS-like messages; the selected binary subset is small.",
                              "Model selection during this project considered external results, so repeat on a future untouched source before claiming deployment performance."]}
    target = ROOT / "reports" / "external.json"
    target.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
