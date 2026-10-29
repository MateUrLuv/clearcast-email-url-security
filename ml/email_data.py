"""Prepare labelled email text while keeping source and duplicate audits visible."""
import hashlib

import pandas as pd

from .email_model import email_text


def text_digest(text):
    normalized = " ".join(text.lower().split())
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def prepare_email_data(raw_dir):
    sources = []
    for filename, label, cap in (
        ("Nazario.csv", 1, None),
        ("SpamAssasin.csv", 0, None),
        ("Enron.csv", 0, 5000),
        ("Ling.csv", 0, None),
    ):
        frame = pd.read_csv(raw_dir / filename, usecols=["subject", "body", "label"])
        frame = frame[frame.label == label].copy()
        if cap is not None:
            frame = frame.sample(n=min(cap, len(frame)), random_state=42)
        frame["text"] = [email_text(s, b) for s, b in zip(frame.subject.fillna(""), frame.body.fillna(""))]
        frame["source"] = filename
        sources.append(frame[["text", "label", "source"]])
    mixed = pd.read_csv(raw_dir / "email_validation.csv", usecols=["Email Text", "Email Type"])
    mixed = mixed[mixed["Email Type"].isin(["Safe Email", "Phishing Email"])].copy()
    mixed["text"] = mixed["Email Text"].fillna("")
    mixed["label"] = (mixed["Email Type"] == "Phishing Email").astype(int)
    mixed["source"] = "email_validation.csv"
    sources.append(mixed[["text", "label", "source"]])
    data = pd.concat(sources, ignore_index=True)
    data = data[data.text.str.len() >= 20].copy()
    data["digest"] = data.text.map(text_digest)
    conflicting = data.groupby("digest").label.nunique()
    data = data[~data.digest.isin(conflicting[conflicting > 1].index)]
    data = data.drop_duplicates("digest").reset_index(drop=True)
    return data
