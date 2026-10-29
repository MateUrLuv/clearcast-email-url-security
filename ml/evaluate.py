"""Held-out metrics and error review without publishing email contents."""
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support


def evaluate(model, features, labels, identifiers, kind, threshold=0.5):
    identifiers = list(identifiers)
    probabilities = model.predict_proba(features)[:, 1]
    predictions = (probabilities >= threshold).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average="binary", zero_division=0)
    matrix = confusion_matrix(labels, predictions, labels=[0, 1])
    errors = {}
    for name, actual, predicted in (("false_positives", 0, 1), ("false_negatives", 1, 0)):
        candidates = [i for i, (truth, guess) in enumerate(zip(labels, predictions)) if truth == actual and guess == predicted]
        candidates.sort(key=lambda i: probabilities[i], reverse=(name == "false_positives"))
        errors[name] = [{"id": str(identifiers[i]), "phishing_probability": round(float(probabilities[i]), 4)} for i in candidates[:10]]
    return {
        "task": kind, "held_out_count": len(labels), "threshold": round(float(threshold), 2),
        "precision": round(float(precision), 4), "recall": round(float(recall), 4), "f1": round(float(f1), 4),
        "confusion_matrix": {"true_negative": int(matrix[0, 0]), "false_positive": int(matrix[0, 1]),
                             "false_negative": int(matrix[1, 0]), "true_positive": int(matrix[1, 1])},
        "false_positive_rate": round(float(matrix[0, 1] / max(1, matrix[0].sum())), 4),
        "errors": errors,
    }


def choose_threshold(labels, probabilities, max_false_positive_rate=0.03):
    """Choose on validation data only; prefer F1 subject to an FP-rate budget."""
    from sklearn.metrics import f1_score
    import numpy as np

    labels = np.asarray(labels)
    candidates = []
    for threshold in np.arange(0.3, 0.951, 0.01):
        predictions = probabilities >= threshold
        fpr = np.mean(predictions[labels == 0])
        if fpr <= max_false_positive_rate:
            candidates.append((f1_score(labels, predictions), -fpr, threshold))
    if not candidates:
        return 0.95
    return round(float(max(candidates)[2]), 2)
