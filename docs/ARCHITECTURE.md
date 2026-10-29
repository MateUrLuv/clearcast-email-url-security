# Architecture

## Data flow

1. `ml/email_data.py` audits and deduplicates email sources; `ml/train.py` downloads labelled public corpora and prepares deterministic samples.
2. `ml/email_model.py` trains a TF-IDF word and phrase vectorizer with logistic regression on email subject and body text.
3. `ml/url_model.py` extracts character n-grams and numeric values from the URL string and trains a separate logistic regression classifier. No email content, DNS query, or webpage is involved.
4. `ml/evaluate.py` chooses the URL threshold on a hostname-separated validation set with a 3% false-positive target, then calculates untouched test metrics and selects errors for review.
5. `ml/explanations.py` multiplies the actual text and structural feature values by their trained linear coefficients. The signed values are exact contributions to phishing log-odds, before rounding and the displayed top-feature limit.
6. `ml/external_eval.py` tests the saved artifacts against separate-source data after excluding overlaps. `ml/email_urls.py` extracts up to five HTTP(S) links from an email without opening them. `app.py` displays the email verdict from the email model and separate URL verdicts for those links, then shows learned contributions and evaluation metrics.

The models share only the label convention: `1` means phishing and `0` means legitimate. Each model has a separate artifact and input pipeline.

## Why these models

TF-IDF with logistic regression is a clear baseline for email text and yields inspectable word and phrase contributions. URL character patterns combined with structural features provide more accurate and still inspectable URL-only predictions. Fixed keyword scores, HTTPS status, and a phishing-word count were rejected after sanity checks showed poor behavior on ordinary pages. The URL features are capped to prevent unusually long URLs from exerting unlimited influence.

The model artifacts use `joblib`; only load artifacts from trusted repository commits. Retraining is deterministic given the same source files and dependency versions. Dataset licenses and limits are in [DATA.md](DATA.md). Results and error patterns are in [EVALUATION.md](EVALUATION.md).

## Decision boundaries

The email verdict comes only from the email model. Embedded URLs are independent evidence, never hidden extra weights in the email verdict. Direct URL submissions use the URL model alone. The 0.52 URL decision threshold was chosen from validation data before the final test evaluation. The app does not visit URLs or use a threat-feed lookup.
