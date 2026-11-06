# Hackathon demo flow

1. Open the app with `streamlit run app.py`. The landing view explains the two independent models and the privacy boundary: pasted URLs are not visited.
2. In **Email investigation**, use a Gmail-downloaded `.eml` file or paste a message containing a subject, body, and URL text (it need not be clickable). For Gmail, open the message, choose **More (⋮) → Download message**, upload the `.eml`, and load its subject and body. Show the email score and the words or phrases that moved it. If the file contains authentication-result headers, explain that ClearCast displays them as supplied and does not verify them. Expand an embedded URL to show its separate URL score; link analysis does not change the email verdict. Imported HTML `href` targets are also analyzed, including destinations hidden behind link text.
3. In **URL investigation**, paste a URL directly. Show both learned character fragments and structural feature contributions. A link can be investigated without uploading an email.
4. In **Review history**, repeat a previously analyzed email or URL. Show how ClearCast flags a repeat from its local fingerprint history. Point out that the history stores scores, timestamps, and hashes, not the underlying email or full URL.
5. In **Evidence & evaluation**, show internal and external precision, recall, F1, false-positive rates, confusion matrices, and the URL validation threshold. Mention the external URL performance drop and why the hostname exclusion matters.
6. Close with the limitation: source labels can be noisy, email corpora differ by class, and scores from a balanced research sample are not calibrated real-world risk. This is an assisted-review prototype.

A concise pitch: **“ClearCast turns a suspicious message into two independently explainable investigations: what the email says and the patterns in its links. We select the URL threshold on validation data and show our misses, not just our successes.”**
