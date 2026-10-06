import hashlib
import re


def make_fingerprint(rec: dict) -> str:
    if rec.get("source") == "Books to Scrape":
        key = f'{rec.get("source", "")} {rec.get("name_or_title", "")}'
    else:
        key = f'{rec.get("source", "")} {rec.get("author", "")} {str(rec.get("name_or_title", ""))[:50]}'
    key = re.sub(r"[^\w\s]", "", key.lower())
    key = " ".join(key.split())
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def find_duplicates(records: list[dict]):
    seen, unique, dupes = set(), [], []
    for rec in records:
        fp = make_fingerprint(rec)
        if fp in seen:
            dupes.append(rec)
        else:
            unique.append(rec)
            seen.add(fp)
    return unique, dupes
