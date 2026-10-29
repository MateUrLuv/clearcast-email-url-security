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

The app loads the checked-in model files from `artifacts/`, so training is optional for running it. Open the local address shown by Streamlit. Use the sidebar to choose **Email investigation**, **URL investigation**, or **Evidence & evaluation**. Paste an email's subject and body or inspect a URL directly.

The email workspace includes local sample messages for a quick demonstration. Gmail integration is not implemented; no inbox access or account connection is used.

## Retrain and test

```bash
.venv/bin/python -m ml.train
.venv/bin/python -m ml.external_eval
.venv/bin/python -m pytest -q
```

Training downloads source CSVs to ignored `data/raw/`, overwrites the model files in `artifacts/`, and regenerates `reports/held_out.json`. External evaluation downloads its separate sources and writes `reports/external.json`. Commit those generated files together when intentionally updating a model. The URL model never visits a submitted URL.

With `pip`, create a virtual environment and install `-e '.[dev]'` into it, then use its `python` and `streamlit` executables.
