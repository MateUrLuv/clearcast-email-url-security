"""Exact additive contributions to each linear model's phishing log-odds."""
from .url_model import FEATURE_NAMES, url_features


def explain_email(model, text, limit=8):
    vectorizer = model.named_steps["tfidfvectorizer"]
    classifier = model.named_steps["logisticregression"]
    row = vectorizer.transform([text])
    contributions = row.data * classifier.coef_[0, row.indices]
    names = vectorizer.get_feature_names_out()
    ranked = sorted(zip((names[i] for i in row.indices), contributions), key=lambda item: abs(item[1]), reverse=True)
    return [{"feature": term, "contribution": round(float(value), 4)} for term, value in ranked[:limit]]


def explain_url(model, url, limit=8, category=None):
    row = model.transform([url]).tocsr()
    weights = model.classifier.coef_[0]
    values = url_features(url)
    char_count = len(model.vectorizer.get_feature_names_out())
    char_names = model.vectorizer.get_feature_names_out()
    ranked = []
    for index, value in zip(row.indices, row.data):
        if category == "text" and index >= char_count:
            continue
        if category == "structure" and index < char_count:
            continue
        if index < char_count:
            ranked.append({"feature": f"URL text: {char_names[index]}",
                           "value": float(value), "contribution": round(float(value * weights[index]), 4)})
        else:
            ranked.append({"feature": FEATURE_NAMES[index - char_count],
                           "value": float(values[index - char_count]),
                           "contribution": round(float(value * weights[index]), 4)})
    return sorted(ranked, key=lambda item: abs(item["contribution"]), reverse=True)[:limit]
