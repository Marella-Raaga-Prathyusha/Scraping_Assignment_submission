import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class BooksScraper(BaseScraper):
    START_URL = "https://books.toscrape.com/"
    SOURCE = "Books to Scrape"

    def parse_page(self, soup: BeautifulSoup, page_url: str) -> list[dict]:
        records = []
        for article in soup.select("article.product_pod"):
            try:
                link = article.select_one("h3 > a")
                price = article.select_one("p.price_color")
                rating = article.select_one("p.star-rating")
                availability = article.select_one("p.instock.availability")

                records.append(
                    {
                        "source": self.SOURCE,
                        "source_url": urljoin(page_url, link["href"]) if link and link.get("href") else None,
                        "name_or_title": link.get("title") if link else None,
                        "category": None,
                        "price": price.get_text(" ", strip=True) if price else None,
                        "rating": " ".join(rating.get("class", [])) if rating else None,
                        "author": None,
                        "tags": None,
                        "description": None,
                        "availability": availability.get_text(" ", strip=True) if availability else None,
                    }
                )
            except (AttributeError, KeyError, TypeError) as exc:
                logger.warning("Skipping malformed book record on %s: %s", page_url, exc)
        return records

    def scrape(self) -> list[dict]:
        records = []
        url = self.START_URL
        page = 1
        while url:
            logger.info("Books page %d: %s", page, url)
            response = self.get(url)
            if response is None:
                logger.error("Stopping Books to Scrape after page failure: %s", url)
                break
            soup = BeautifulSoup(response.text, "lxml")
            page_records = self.parse_page(soup, url)
            records.extend(page_records)
            next_link = soup.select_one("li.next > a")
            url = urljoin(url, next_link["href"]) if next_link and next_link.get("href") else None
            page += 1
            self.pause()
        return records
