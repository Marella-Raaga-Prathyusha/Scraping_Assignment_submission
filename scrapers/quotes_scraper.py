import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class QuotesScraper(BaseScraper):
    START_URL = "https://quotes.toscrape.com/"
    SOURCE = "Quotes to Scrape"

    def parse_page(self, soup: BeautifulSoup, page_url: str) -> list[dict]:
        records = []
        for quote in soup.select("div.quote"):
            try:
                text = quote.select_one("span.text")
                author = quote.select_one("small.author")
                tags = quote.select("a.tag")
                author_link = quote.select_one('a[href^="/author/"]')
                records.append(
                    {
                        "source": self.SOURCE,
                        "source_url": page_url,
                        "name_or_title": text.get_text(" ", strip=True) if text else None,
                        "category": None,
                        "price": None,
                        "rating": None,
                        "author": author.get_text(" ", strip=True) if author else None,
                        "tags": [tag.get_text(" ", strip=True) for tag in tags],
                        "description": None,
                        "author_url": urljoin(page_url, author_link["href"]) if author_link and author_link.get("href") else None,
                    }
                )
            except (AttributeError, KeyError, TypeError) as exc:
                logger.warning("Skipping malformed quote record on %s: %s", page_url, exc)
        return records

    def scrape(self) -> list[dict]:
        records = []
        url = self.START_URL
        page = 1
        while url:
            logger.info("Quotes page %d: %s", page, url)
            response = self.get(url)
            if response is None:
                logger.error("Stopping Quotes to Scrape after page failure: %s", url)
                break
            soup = BeautifulSoup(response.text, "lxml")
            records.extend(self.parse_page(soup, url))
            next_link = soup.select_one("li.next > a")
            url = urljoin(url, next_link["href"]) if next_link and next_link.get("href") else None
            page += 1
            self.pause()
        return records
