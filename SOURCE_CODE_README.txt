CLEARCAST - PHISHING EMAIL AND URL ANALYZER
==========================================

WELCOME
-------
This folder contains the ClearCast project. This plain-text guide can be
opened with Notepad on Windows or any basic text editor.

No Git, GitHub account, or command-line download tool is needed. The project
already includes its trained models and saved evaluation results.


WHAT THIS PROJECT DOES
----------------------
ClearCast is a local Streamlit app for reviewing email text and URLs:

1. Paste an email subject and body, or import a Gmail-downloaded original
   email file (.eml), to see the email model's score and contributing text
   features.
2. Any web links in the email are checked separately by the URL model.
   Visible HTTP/HTTPS URLs, www. links, and bare dotted hostnames are found
   even when not clickable. Hidden HTML hyperlink destinations in .eml files
   are checked too. A URL result does not change the email result.
3. Paste a URL to see its independent score and feature contributions.
4. Open Review history to see prior checks and identify repeats.
5. Open Evidence & evaluation in the app to review the saved model results.

ClearCast analyzes URL text only. It does not visit websites, download page
content, follow redirects, sign in to Gmail, or access an inbox.


IMPORT AN ORIGINAL GMAIL MESSAGE
-------------------------------
1. In Gmail, open the email you want to review.
2. Select the More menu (three vertical dots) and choose "Download message".
3. In ClearCast, choose Email investigation.
4. Expand "Import an original Gmail message (.eml)" and select the downloaded
   .eml file.
5. Review the sender and any authentication-result headers shown. These values
   are copied from the file; ClearCast does not independently verify them.
6. Select "Load email into the fields", then select "Analyze email".

The app loads the message subject and readable body into the existing form.
Hidden HTTP/HTTPS destinations in HTML hyperlinks are also extracted from
the .eml's href attributes and checked separately by the URL model, even if
the visible link text does not show the address. ClearCast never opens them.
The email and URL scores remain independent. You can still edit the fields
or paste an email instead.

There is no Gmail login, OAuth, inbox permission, or Gmail API connection.
When running locally, the app reads the selected file on your computer.


REVIEW HISTORY AND REPEATS
--------------------------
ClearCast adds a Review history workspace. Reanalyzing the same email text or
URL lets the app flag it as previously seen.

History is saved on this computer in:

    .clearcast/review_history.sqlite3

It stores timestamps, item type, source, model score, threshold, assessment,
and SHA-256 fingerprints for repeat matching. It does NOT store email bodies,
senders, or full URLs. Fingerprints are deterministic, not encryption or
anonymization, and the database is not encrypted. Select Review history,
confirm the checkbox, and choose "Clear local review history" to delete
saved entries.

IMPORTANT LIMITATION
--------------------
This is a student research and awareness project, not a production security
product. Scores are model outputs, not calibrated real-world probabilities.
A high score does not prove a message or URL is malicious. A result below
the decision threshold does not mean that it is legitimate or safe.
Independently verify unexpected requests through a trusted channel.


WHAT YOU NEED
-------------
- Windows, macOS, or Linux
- Python 3.11 or Python 3.12
- Internet access for the initial installation of Python packages
- A web browser

Install Python from:
https://www.python.org/downloads/

On Windows, select "Add python.exe to PATH" during installation if that
option is shown.


STEP 1 - EXTRACT THE PROJECT ZIP
-------------------------------
If you received ClearCast_Project.zip:

1. Find the ZIP file in File Explorer (Windows) or your Downloads folder.
2. On Windows, right-click the ZIP and choose "Extract All...".
3. Choose a convenient location, such as your Desktop, and extract it.
4. Open the extracted ClearCast_Project folder.
5. Confirm that you can see app.py, pyproject.toml, and the folders named
   artifacts and ml.

Do not try to run the app from inside the ZIP preview. Extract it first.

If you received this folder already extracted, open that folder directly.


STEP 2 - OPEN A TERMINAL IN THE PROJECT FOLDER
----------------------------------------------
WINDOWS:
1. Open the extracted ClearCast_Project folder in File Explorer.
2. Click the address bar, type: powershell
3. Press Enter. PowerShell opens in that folder.

Alternatively, open PowerShell and change to the folder where you extracted
the ZIP. For example, if it is on your Desktop, run:

    cd "$HOME\Desktop\ClearCast_Project"

If you chose a different extraction location, adjust that folder path.

MACOS:
Open Terminal. Type "cd " (including the space), drag the extracted
ClearCast_Project folder into the Terminal window, and press Enter.

LINUX:
Open Terminal, type "cd " (including the space), drag the extracted
ClearCast_Project folder into the Terminal window if your desktop supports
it, and press Enter.

Before continuing, check that this command lists app.py:

    Windows PowerShell:  Get-ChildItem
    macOS or Linux:      ls


STEP 3 - CREATE A PROJECT PYTHON ENVIRONMENT
--------------------------------------------
This keeps ClearCast's installed packages separate from other Python
projects on your computer.

WINDOWS POWERSHELL:

    py -3.12 -m venv .venv

If you installed Python 3.11 instead, use:

    py -3.11 -m venv .venv

If the "py" command is not available, try:

    python -m venv .venv

MACOS OR LINUX:

    python3 -m venv .venv

Wait for the command to finish. It creates a .venv folder inside the
ClearCast project folder.


STEP 4 - ACTIVATE THE ENVIRONMENT
---------------------------------
WINDOWS POWERSHELL:

    .\.venv\Scripts\Activate.ps1

MACOS OR LINUX:

    source .venv/bin/activate

If Windows says that script execution is disabled, do not change your
computer's security policy. You can skip activation and use the explicit
Python commands in the "IF SOMETHING GOES WRONG" section below.


STEP 5 - INSTALL THE REQUIRED PACKAGES
--------------------------------------
With the environment activated, run:

    python -m pip install --upgrade pip
    python -m pip install -e ".[dev]"

The first installation may take a few minutes. Internet access is needed
for this step. You do not need to download training datasets or retrain
the models to use the included application.


STEP 6 - START CLEARCAST
-----------------------
Run:

    python -m streamlit run app.py

Wait for Streamlit to show a local web address, usually:

    http://localhost:8501

Open that address in your web browser. Choose Email investigation, URL
investigation, or Evidence & evaluation from the app's navigation.

For a quick demonstration:
1. Choose Email investigation.
2. Select "Load suspicious sample".
3. Select "Analyze email".

To stop the app, return to the terminal and press Ctrl+C.


IF SOMETHING GOES WRONG
=======================

WINDOWS: PowerShell does not allow environment activation
----------------------------------------------------------
You can run the app without activating the environment. In PowerShell,
from the project folder, run:

    .\.venv\Scripts\python.exe -m pip install --upgrade pip
    .\.venv\Scripts\python.exe -m pip install -e ".[dev]"
    .\.venv\Scripts\python.exe -m streamlit run app.py

No security policy changes are needed.

"No module named streamlit"
---------------------------
The packages were not installed in the project environment. Return to
Step 5 and run the installation command again from this project folder.

"py" or "python" is not recognized (Windows)
---------------------------------------------
Install Python from https://www.python.org/downloads/, then close and
reopen PowerShell. If available, try "python" instead of "py".

"python3" is not recognized (macOS or Linux)
--------------------------------------------
Install Python 3.11 or 3.12 using your operating system's standard method,
then open a new Terminal window.

Port 8501 is already in use
---------------------------
Start ClearCast on another port:

    python -m streamlit run app.py --server.port 8502

The browser cannot open the app
-------------------------------
Make sure the Streamlit command is still running in the terminal. Use the
exact local address printed by Streamlit. The app is served by your own
computer.


OPTIONAL - RUN THE TESTS
========================
After completing setup, run:

    python -m pytest -q

The tests check the project code. They are optional for launching the app.


PROJECT FOLDER CONTENTS
=======================
app.py              ClearCast Streamlit application
email_import.py     Local .eml parsing, including hidden HTML link targets
review_history.py   Persistent local history with content-free fingerprints
ml/                 Model and feature-explanation code
artifacts/          Included trained email and URL models
reports/            Saved held-out and external evaluation results
tests/              Automated project tests
docs/               Architecture, data, setup, demo, and evaluation notes
screenshots/        Images of the application
.streamlit/         Streamlit appearance settings
pyproject.toml      Python package and dependency information

The app loads the included model files. Do not remove or rename files in
the artifacts folder.

Gmail sign-in and inbox access are not part of this project. Original messages
can be imported by downloading the .eml file from Gmail and loading it in the
email workspace.
