import csv
import json
import logging
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from processing.cleaning import clean_record
from processing.deduplication import find_duplicates
from processing.validation import validate_record
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
LOG_DIR = ROOT / "logs"
CSV_PATH = OUTPUT_DIR / "final_dataset.csv"
SUMMARY_PATH = OUTPUT_DIR / "summary_report.json"
REPORT_PATH = OUTPUT_DIR / "report.html"
LOG_PATH = LOG_DIR / "scraper.log"

COLUMNS = [
    "source", "source_url", "name_or_title", "category", "price", "rating",
    "author", "tags", "description", "scraped_at"
]


def configure_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def process_source(scraper, source: str, stats: dict) -> list[dict]:
    raw_records = scraper.scrape()
    stats["collected_per_source"][source] = len(raw_records)
    cleaned = []
    rejection_counter = Counter()

    for raw in raw_records:
        try:
            record = clean_record(raw)
            record["scraped_at"] = datetime.now(timezone.utc).isoformat()
            problems = validate_record(record)
            if problems:
                for reason in problems:
                    rejection_counter[reason] += 1
                logging.warning("Rejected %s record: %s", source, problems)
                continue
            cleaned.append(record)
        except (ValueError, TypeError, AttributeError) as exc:
            rejection_counter["processing_error"] += 1
            logging.warning("Rejected malformed %s record: %s", source, exc)

    stats["cleaned_per_source"][source] = len(cleaned)
    stats["rejected_by_source"][source] = dict(rejection_counter)
    return cleaned


def write_csv(records: list[dict]):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def write_summary(stats: dict):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with SUMMARY_PATH.open("w", encoding="utf-8") as handle:
        json.dump(stats, handle, indent=4)


def write_html_report(stats: dict):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    template_path = ROOT / "report_template.html"
    template = template_path.read_text(encoding="utf-8")
    rows = "".join(
        f"<tr><td>{source}</td><td>{stats['collected_per_source'].get(source, 0)}</td>"
        f"<td>{stats['cleaned_per_source'].get(source, 0)}</td></tr>"
        for source in stats["collected_per_source"]
    )
    html = (template
        .replace("{{generated_at}}", stats["ended_at"])
        .replace("{{final_count}}", str(stats["final_record_count"]))
        .replace("{{duplicates}}", str(stats["duplicates_detected"]))
        .replace("{{duration}}", str(stats["duration_seconds"]))
        .replace("{{source_rows}}", rows))
    REPORT_PATH.write_text(html, encoding="utf-8")


def main():
    configure_logging()
    start = time.perf_counter()
    started_at = datetime.now(timezone.utc)
    stats = {
        "started_at": started_at.isoformat(),
        "collected_per_source": {},
        "cleaned_per_source": {},
        "rejected_by_source": {},
        "duplicates_detected": 0,
        "final_record_count": 0,
    }

    all_cleaned = []
    for scraper, source in [
        (BooksScraper(), "Books to Scrape"),
        (QuotesScraper(), "Quotes to Scrape"),
    ]:
        try:
            all_cleaned.extend(process_source(scraper, source, stats))
        except Exception:
            logging.exception("Unexpected failure while processing %s; continuing.", source)

    unique, duplicates = find_duplicates(all_cleaned)
    stats["duplicates_detected"] = len(duplicates)
    stats["final_record_count"] = len(unique)
    stats["ended_at"] = datetime.now(timezone.utc).isoformat()
    stats["duration_seconds"] = round(time.perf_counter() - start, 3)

    write_csv(unique)
    write_summary(stats)
    write_html_report(stats)
    logging.info("Finished: %d final records; %d duplicates.", len(unique), len(duplicates))
    logging.info("CSV: %s", CSV_PATH)
    logging.info("Summary: %s", SUMMARY_PATH)
    logging.info("HTML report: %s", REPORT_PATH)


if __name__ == "__main__":
    main()
