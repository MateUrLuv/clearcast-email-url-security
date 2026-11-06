# Setup

## Requirements

- Python 3.11 or 3.12
- `uv` (recommended) or `pip`
- Internet access only when retraining to download the public datasets

## Run the app

From the repository root:

```bash
uv venv --python 3.12
uv pip install --python .venv/bin/python -e '.[dev]'
.venv/bin/streamlit run app.py
```

The app loads the checked-in model files from `artifacts/`, so training is optional for running it. Open the local address shown by Streamlit. Use the sidebar to choose **Email investigation**, **URL investigation**, or **Evidence & evaluation**. Paste an email's subject and body, import a Gmail-downloaded `.eml` file, or inspect a URL directly.

To import an original Gmail message, open it in Gmail, select **More (⋮) → Download message**, then upload the `.eml` file in Email investigation and load its subject and body into the fields. ClearCast does not sign in to Gmail, access an inbox, or independently verify authentication-result headers shown from the file.

ClearCast finds visible HTTP/HTTPS URLs, `www.` links, and bare dotted hostnames in email text even when they are not clickable. When importing `.eml` files, it also extracts HTTP/HTTPS destinations from HTML link `href` attributes. This handles links labelled "click here" whose actual URL is not visible in the message text. These destinations go only to the separate URL model; ClearCast does not open them or add them to the email model's input.

The **Review history** workspace remembers prior checks on the same computer. It stores timestamps, item type, source, score, threshold, assessment, and SHA-256 fingerprints for repeat matching—not message bodies, senders, or full URLs. Fingerprints are deterministic, not encryption or anonymization. The database is `.clearcast/review_history.sqlite3` and is not encrypted. Clear it from **Review history → Clear local review history**.

The email workspace also includes local sample messages for a quick demonstration.

## Retrain and test

```bash
.venv/bin/python -m ml.train
.venv/bin/python -m ml.external_eval
.venv/bin/python -m pytest -q
```

Training downloads source CSVs to ignored `data/raw/`, overwrites the model files in `artifacts/`, and regenerates `reports/held_out.json`. External evaluation downloads its separate sources and writes `reports/external.json`. Commit those generated files together when intentionally updating a model. The URL model never visits a submitted URL.

With `pip`, create a virtual environment and install `-e '.[dev]'` into it, then use its `python` and `streamlit` executables.
