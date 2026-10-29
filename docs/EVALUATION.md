# Evaluation

## Internal held-out test

Email text is deduplicated, then split 80/20 with stratification and seed 42. URLs are deduplicated, sampled evenly by class, and split by hostname into training, validation, and a 20% held-out test set. The URL decision threshold of 0.52 was chosen on validation data for a 3% false-positive target. The email threshold is 0.5. Exact counts and error hashes are in [`reports/held_out.json`](../reports/held_out.json).

| Model | Test examples | Precision | Recall | F1 | False-positive rate | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Email | 2,623 | 95.68% | 98.41% | 97.03% | 0.61% | 14 | 5 |
| URL | 6,320 | 96.82% | 90.30% | 93.45% | 2.98% | 94 | 307 |

## External-source stress test

The trained artifacts are evaluated without fitting or threshold tuning on these examples. PhreshPhish URL examples with a hostname found anywhere in the EdgePhish source are removed. Email examples matching a training text hash are removed. Exact results are in [`reports/external.json`](../reports/external.json).

| Model | External examples | Precision | Recall | F1 | False-positive rate | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Email | 283 | 98.78% | 71.05% | 82.65% | 0.59% | 1 | 33 |
| URL | 834 | 85.67% | 67.63% | 75.59% | 13.32% | 51 | 146 |

The URL drop shows that its internal benchmark does **not** transfer cleanly to a different collection. It should assist human review, not block traffic automatically. The email model has fewer false alarms on this external set but misses 33 of 114 phishing messages. That set is small and contains email- and SMS-like text.

## Email data change

On the same 283 external email examples, the previous model had 76.72% precision, 78.07% recall, 77.39% F1, and 15.98% false positives. The expanded training set improved F1 and reduced false alarms, while recall fell by about seven percentage points. This is a tradeoff, not a universal accuracy gain. The comparison informed this project, so another future source is needed for a truly untouched final assessment.

## Remaining risks

Source-specific language still correlates with email labels. The mixed-class training file has only 100 unique messages. Familiar login domains can be present in phishing URLs, and URL-only analysis cannot see destination content. The model probabilities are learned on curated datasets and are not calibrated to live phishing prevalence. The investigation screen scores links inside an email separately; those URL scores do not change the email-model verdict.
