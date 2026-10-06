# AI_USAGE.md

## Tool used

**Tool:** ChatGPT

## How AI was used

AI assistance was used for:

- translating the assignment requirements into a clean Python project structure
- drafting the shared Requests session and retry behavior
- drafting BeautifulSoup selectors and dynamic pagination logic
- designing cleaning, validation, and duplicate-fingerprint functions
- generating unit-test cases for edge conditions
- reviewing the README structure and required documentation

## Representative prompts

1. "Complete the Python web scraping assignment using the provided reference document."
2. "Implement dynamic pagination for Books to Scrape and Quotes to Scrape without hard-coding page numbers."
3. "Create reusable cleaning, validation, and SHA-256 duplicate detection functions according to the assignment requirements."
4. "Add tests for whitespace/price/rating cleaning, validation failures, and duplicates that differ only by case and spaces."

## AI-assisted parts

AI-assisted implementation included the initial structure of:

- `scrapers/base_scraper.py`
- `scrapers/books_scraper.py`
- `scrapers/quotes_scraper.py`
- `processing/cleaning.py`
- `processing/validation.py`
- `processing/deduplication.py`
- `main.py`
- the unit tests
- documentation drafts

## Review and verification

The implementation was reviewed against the assignment requirements. In particular:

- pagination follows the HTML `next` link instead of a fixed page range
- missing selectors are checked before field access
- temporary HTTP failures are retried
- each source is isolated so one source failure does not stop the other
- cleaning is separated from scraping
- validation returns specific rejection reasons
- duplicate detection normalizes case, punctuation, and whitespace before hashing
- outputs use UTF-8 and a fixed CSV schema
- tests do not require network access

## Important limitation during preparation

The execution environment used to prepare this submission did not have DNS/network access to the two live practice websites. Therefore the live scraper could not be executed here to produce a truthful live `final_dataset.csv` and live `summary_report.json`. The submitted code is designed to generate those files when run in a normal network-enabled environment with:

```bash
python3 main.py
```

No fabricated live scraping counts or records are included.

## Custom changes requested after the initial implementation

- Changed `clean_price()` so scraped GBP prices are converted to INR using a fixed reference rate of 127.34 INR per GBP for reproducibility.
- Added a generated `output/report.html` presentation page with background color `#fffff` and primary text color `#e05572`.
- Updated the cleaning test and README to document the currency conversion.
- Re-ran the unit test suite after the changes: 9 tests passed.
