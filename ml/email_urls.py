"""Extract URL candidates from email text without fetching them."""
import re

URL_PATTERN = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
TRAILING = ".,;:!?)]}"


def extract_urls(text, limit=5):
    seen = set()
    result = []
    for match in URL_PATTERN.finditer(text):
        url = match.group().rstrip(TRAILING)
        if url not in seen:
            seen.add(url)
            result.append(url)
            if len(result) >= limit:
                break
    return result
