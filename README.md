# Multi-Source Web Scraping & Data Consolidation

## Overview

This project implements the Realisieren Technologies Python web scraping assignment. It collects records from **Books to Scrape** and **Quotes to Scrape**, cleans and validates them, removes duplicates, and writes one standardized CSV plus a JSON summary and execution log.

The pipeline is:

`Scrape -> Clean -> Validate -> Deduplicate -> Consolidate -> Save`

The implementation follows the reference assignment's required stages and keeps source-specific scraping logic separate from data-processing logic.

## Python version

Use Python **3.10, 3.11, or 3.12**.

Check your version:

```bash
python3 --version
```

## Setup

```bash
git clone <your-repository-url>
cd scraping_assignment
python -m venv venv
source venv/bin/activate        # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

## Run

From the project root:

```bash
python3 main.py
```

The command automatically creates:

- `output/final_dataset.csv`
- `output/summary_report.json`
- `logs/scraper.log`

## Sources and page structure

### Books to Scrape

- Record: `article.product_pod`
- Title/link: `h3 > a`; full title is in the `title` attribute
- Price: `p.price_color`
- Rating: class on `p.star-rating`
- Availability: `p.instock.availability`
- Next page: `li.next > a`

### Quotes to Scrape

- Record: `div.quote`
- Quote: `span.text`
- Author: `small.author`
- Tags: `a.tag`
- Author link: `a[href^="/author/"]`
- Next page: `li.next > a`

Pagination follows the site's `next` link dynamically; page numbers are not hard-coded.

## Data model

| Column | Books | Quotes |
|---|---|---|
| `source` | Books to Scrape | Quotes to Scrape |
| `source_url` | Book detail URL | Quote page URL |
| `name_or_title` | Book title | Quote text |
| `category` | Empty unless detail-page enrichment is added | Empty |
| `price` | Numeric price | Empty |
| `rating` | Integer 1-5 | Empty |
| `author` | Empty | Author name |
| `tags` | Empty | Lowercase, sorted, semicolon-separated tags |
| `description` | Empty unless detail-page enrichment is added | Empty |
| `scraped_at` | UTC timestamp | UTC timestamp |

The assignment says not to invent data. Therefore category and description remain empty in the listing-page implementation rather than being guessed.

## Cleaning

`processing/cleaning.py` contains pure transformation functions:

- `clean_text()` collapses whitespace and converts non-breaking spaces.
- `strip_quotes()` removes curly/straight quote wrappers.
- `clean_price()` extracts the GBP amount and converts it to INR using the fixed reference rate `1 GBP = 127.34 INR`. For example, `£51.77` becomes `₹6,589.15` (stored as the numeric value `6589.15` in the CSV).
- `clean_rating()` maps `One` through `Five` to integers 1-5.
- `clean_tags()` lowercases, sorts, de-duplicates, and joins tags with `;`.
- `normalize_url()` accepts only complete HTTP/HTTPS URLs after normalization.

## Validation

Every cleaned record is checked for:

- recognized source
- non-empty name/title
- HTTP/HTTPS source URL
- non-negative numeric price when present
- integer rating from 1 through 5 when present

Invalid records are rejected and the reason is recorded in `summary_report.json` and the log.

## Duplicate detection

A SHA-256 fingerprint is generated after normalization.

- Books: `source + title`
- Quotes: `source + author + first 50 characters of quote`

The fingerprint lowercases text, removes punctuation, and collapses whitespace. This means values such as `Example Book Title`, ` Example Book Title `, and `EXAMPLE BOOK TITLE` are treated as equivalent.

Duplicates are removed from the final CSV and counted in `duplicates_detected`. A unit test deliberately creates duplicates because the real practice sites normally contain unique records.

## Error handling

The shared HTTP layer uses `requests.Session`, a descriptive User-Agent, a 10-second timeout, and retries for temporary HTTP failures including 429, 500, 502, 503, and 504.

Each source is processed independently. A source failure is logged and does not prevent the other source from being attempted. Individual malformed records are skipped rather than crashing the complete run.

Requests are separated by a 0.5-second pause to respect reasonable request rates.

## Tests

Run:

```bash
pytest -q
```

The tests cover text/price/rating/tag/URL cleaning, validation, and duplicate detection without requiring internet access.

## Output

`final_dataset.csv` contains one row per valid, non-duplicate record with a fixed column order.

`summary_report.json` contains:

- records collected per source
- records after cleaning per source
- validation rejection counts by source/reason
- duplicate count
- final record count
- start/end timestamps
- execution duration

`logs/scraper.log` contains timestamped page progress, warnings, errors, and final output information.

## Assumptions and limitations

1. The assignment's practice sites are server-rendered HTML, so Requests + BeautifulSoup is sufficient; Selenium/Playwright is unnecessary.
2. The book listing page does not contain category/description, so this implementation leaves those fields empty rather than making extra detail-page requests or inventing values.
3. The quote `source_url` is the page where the quote appeared, which is stable and directly identifies its source page.
4. The final dataset is generated by running `python main.py` against the live public practice sites. Network access is required for that step.

## AI usage

See `AI_USAGE.md` for the required disclosure of AI assistance, prompts, review, corrections, and verification.
