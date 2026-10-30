CLEARCAST - PHISHING EMAIL AND URL ANALYZER
==========================================

WHAT THIS PROJECT DOES
----------------------
ClearCast is a local Streamlit app for reviewing suspicious emails and URLs.
It uses two separate machine-learning models:

1. The email model analyzes the subject and pasted message body.
2. The URL model analyzes the text and structure of a URL.

If an email contains links, ClearCast analyzes each link separately. A URL
result never changes the email result.

ClearCast does NOT open URLs, download web pages, access an inbox, or connect
to Gmail. Gmail integration is not implemented.

IMPORTANT LIMITATION
-------------------
This is a student research and awareness project, not a production security
product. Scores are model outputs from curated datasets. They are not
calibrated real-world probabilities. A high score is not proof that something
is malicious. A low score is not proof that it is safe.


BEGINNER SETUP: WINDOWS
======================

You need:
- Python 3.11 or 3.12
- Git
- An internet connection for the first dependency installation

STEP 1 - Install Python and Git
-------------------------------
Install Python from:
https://www.python.org/downloads/

During Python installation on Windows, select:
"Add python.exe to PATH"

Install Git from:
https://git-scm.com/downloads

Open PowerShell and check the installations:

    py --version
    git --version

STEP 2 - Download the source code
---------------------------------
Copy and run:

    git clone https://github.com/MateUrLuv/clearcast-email-url-security.git
    cd clearcast-email-url-security

This creates a folder named "clearcast-email-url-security" containing the
source code and this README.

STEP 3 - Create a project-only Python environment
-------------------------------------------------
For Python 3.12, run:

    py -3.12 -m venv .venv

If you installed Python 3.11 instead, run:

    py -3.11 -m venv .venv

STEP 4 - Activate the environment
---------------------------------
Run:

    .\.venv\Scripts\Activate.ps1

If PowerShell prevents activation, you do not need to change your computer's
security policy. Skip activation and use the explicit Python commands in
"IF SETUP DOES NOT WORK" below.

STEP 5 - Install project dependencies
-------------------------------------
Run:

    python -m pip install --upgrade pip
    python -m pip install -e ".[dev]"

Wait until installation finishes.

STEP 6 - Start ClearCast
-----------------------
Run:

    python -m streamlit run app.py

Wait for Streamlit to display a local address, usually:

    http://localhost:8501

Open that address in your web browser. Use the left sidebar to select Email
investigation, URL investigation, or Evidence & evaluation.

For a quick demonstration, choose Email investigation, click "Load suspicious
sample", and click "Analyze email".

To stop ClearCast, return to PowerShell and press Ctrl+C.


BEGINNER SETUP: MACOS OR LINUX
=============================

Install Python 3.11 or 3.12 and Git. Open Terminal and run:

    git clone https://github.com/MateUrLuv/clearcast-email-url-security.git
    cd clearcast-email-url-security
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -e ".[dev]"
    python -m streamlit run app.py

Open the local address Streamlit displays in your browser. Press Ctrl+C in
Terminal to stop the app.


IF SETUP DOES NOT WORK
======================

PowerShell cannot activate the environment:

Run these commands instead; they do not require activation:

    .\.venv\Scripts\python.exe -m pip install --upgrade pip
    .\.venv\Scripts\python.exe -m pip install -e ".[dev]"
    .\.venv\Scripts\python.exe -m streamlit run app.py

"No module named streamlit":

The dependencies were not installed into this project's environment. Run:

    .\.venv\Scripts\python.exe -m pip install -e ".[dev]"

Port 8501 is already in use:

Start Streamlit on another port:

    python -m streamlit run app.py --server.port 8502

The "git" command is not recognized:

Install Git, close PowerShell, open it again, and retry.

The "py" command is not recognized:

Install Python and enable "Add python.exe to PATH". Reopen PowerShell.
Depending on your installation, "python -m venv .venv" may work instead.


FILES AND TESTS
===============

app.py              Streamlit user interface
ml/                 Machine-learning models and related code
artifacts/          Included trained models; no training needed to run the app
reports/            Saved evaluation results
screenshots/        Screenshots of the app
tests/              Automated tests
docs/               Setup, data, architecture, and evaluation notes

After setup, run the tests with:

    python -m pytest -q

Retraining is optional. Do not run "python -m ml.train" unless you intend to
download the source datasets and regenerate the trained model artifacts.
Dataset details and licenses are in docs/DATA.md.

For the full project description and screenshots, open README.md in this
folder or visit:
https://github.com/MateUrLuv/clearcast-email-url-security
