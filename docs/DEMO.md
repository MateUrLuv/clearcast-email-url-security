# Hackathon demo flow

1. Open the app with `streamlit run app.py`. The landing view explains the two independent models and the privacy boundary: pasted URLs are not visited.
2. In **Email investigation**, paste a message containing a subject, body, and at least one HTTP(S) link. Show the email score and the words or phrases that moved it. Expand an embedded URL to show its separate URL score. Explain that link analysis does not silently change the email verdict.
3. In **URL investigation**, paste a URL directly. Show both learned character fragments and structural feature contributions. A link can be investigated without uploading an email.
4. In **Evidence & evaluation**, show internal and external precision, recall, F1, false-positive rates, confusion matrices, and the URL validation threshold. Mention the external URL performance drop and why the hostname exclusion matters.
5. Close with the limitation: source labels can be noisy, email corpora differ by class, and scores from a balanced research sample are not calibrated real-world risk. This is an assisted-review prototype.

A concise pitch: **“ClearCast turns a suspicious message into two independently explainable investigations: what the email says and the patterns in its links. We select the URL threshold on validation data and show our misses, not just our successes.”**
