# Data sources and label scope

## Email training

[Phishing Email Curated Datasets](https://zenodo.org/records/8339691) (Champa et al., CC BY 4.0) supply phishing mail from `Nazario.csv` and legitimate mail from `SpamAssasin.csv`, `Enron.csv`, and `Ling.csv`. Only rows labelled legitimate are used from the latter three. Their spam rows are excluded because spam is not necessarily phishing. Enron legitimate mail is capped at 5,000 messages with seed 42 so it does not dominate training.

[Phishing validation emails](https://zenodo.org/records/13474746) (Miltchev et al., CC BY 4.0) supplies both safe and phishing messages to training. Although the file has 2,000 rows, it contains only **100 unique messages** after normalization and deduplication: 77 safe and 23 phishing. It mixes real and artificially generated messages. The project reports the unique counts rather than claiming 2,000 distinct training examples.

Subjects and bodies are combined, normalized-text duplicates are removed before splitting, and any exact text with conflicting labels is discarded. The final source counts appear in `reports/held_out.json`. Sources still correlate with labels, so the internal split can overstate generalization.

## Email external test

[Multiclass NLP Dataset for Phishing and Social Engineering Threat Detection](https://zenodo.org/records/15235123) (Engineering Ingegneria Informatica, CC BY 4.0) is **never used for training**. Its `Corpus` field stores text and label separated by a tab; the project includes only `Phishing` and `NOT-Malicious General Class` records. Other malicious classes are outside this binary task. After malformed rows and training-text overlaps are removed, 283 email- or SMS-like messages remain. This is a small, shifted-domain test.

## URL training and external test

[EdgePhish-5G URLs](https://zenodo.org/records/19371661) (AlBattra, CC BY 4.0) provide the training source. The project reads only raw `url` and binary `label`, samples up to 16,000 per class, and separates hostnames across training, validation, and test. `source` and `slice` are not features.

[PhreshPhish](https://huggingface.co/datasets/phreshphish/phreshphish) (CC BY 4.0) supplies an independent-source URL stress test. The first official test shard has 1,000 labelled URLs. Exact URLs and hostnames appearing anywhere in the EdgePhish source are excluded, leaving 834 URLs. Only the URL and label columns are read; webpage HTML is not used.

The earlier [UCI PhiUSIIL URL set](https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset) was rejected for training because its legitimate class consisted entirely of HTTPS URLs and mostly short homepages. That shortcut yielded misleadingly high internal scores.

Source datasets download to ignored `data/raw/` during training or external evaluation. Raw messages, HTML, and URLs are not redistributed in this repository; reports identify mistakes by short hashes.
