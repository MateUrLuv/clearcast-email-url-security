# Reproducible evaluation reports

- `held_out.json` records the internal email and URL held-out splits, metrics, confusion matrices, hashed error examples, and learned feature contributions. URL threshold selection uses validation data, not the held-out test set.
- `external.json` records separate-source tests: PhreshPhish URLs with training-source hostnames removed, and a binary subset of a multiclass phishing-message dataset with overlapping training texts removed.

The reports omit raw messages and URLs. Read [evaluation methods and limitations](../docs/EVALUATION.md) and [data provenance](../docs/DATA.md) before quoting metrics.
