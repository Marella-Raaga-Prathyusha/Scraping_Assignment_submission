import re
from urllib.parse import urljoin, urlparse

RATING_MAP = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}

# Fixed reference rate used for reproducible assignment runs.
# 1 GBP = 127.34 INR (reference rate for 2026-10-06).
GBP_TO_INR_RATE = 127.34


def clean_text(value):
    if value is None:
        return None
    text = " ".join(str(value).replace("\xa0", " ").split())
    return text or None


def strip_quotes(value):
    text = clean_text(value)
    if not text:
        return None
    return text.strip("“”\"'") or None


def clean_price(raw):
    """Convert a scraped GBP price to INR."""
    if raw is None or raw == "":
        return None

    match = re.search(r"\d+(?:\.\d+)?", str(raw).replace(",", ""))
    if not match:
        return None

    gbp_price = float(match.group())
    return round(gbp_price * GBP_TO_INR_RATE, 2)


def clean_rating(raw):
    for word in (raw or "").lower().split():
        if word in RATING_MAP:
            return RATING_MAP[word]
    return None


def clean_tags(tags):
    if not tags:
        return None
    cleaned = sorted({clean_text(tag).lower() for tag in tags if clean_text(tag)})
    return ";".join(cleaned) or None


def normalize_url(url, base_url=None):
    if not url:
        return None
    value = str(url).strip()
    if base_url:
        value = urljoin(base_url, value)
    parsed = urlparse(value)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return value
    return None


def clean_record(record):
    cleaned = dict(record)
    cleaned["source"] = clean_text(cleaned.get("source"))
    cleaned["source_url"] = normalize_url(cleaned.get("source_url"))
    cleaned["name_or_title"] = strip_quotes(cleaned.get("name_or_title"))
    cleaned["category"] = clean_text(cleaned.get("category"))
    cleaned["price"] = clean_price(cleaned.get("price"))
    cleaned["rating"] = clean_rating(cleaned.get("rating"))
    cleaned["author"] = clean_text(cleaned.get("author"))
    cleaned["tags"] = clean_tags(cleaned.get("tags")) if isinstance(cleaned.get("tags"), list) else clean_text(cleaned.get("tags"))
    cleaned["description"] = clean_text(cleaned.get("description"))
    return cleaned
