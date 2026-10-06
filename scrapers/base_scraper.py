import logging
import time
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

logger = logging.getLogger(__name__)


class BaseScraper:
    """Shared HTTP behavior for the two source scrapers."""

    def __init__(self, delay: float = 0.5, timeout: int = 10) -> None:
        self.delay = delay
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "ScrapingAssignment/1.0 (learning project)"}
        )
        retry = Retry(
            total=3,
            connect=3,
            read=3,
            status=3,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=frozenset(["GET"]),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def get(self, url: str) -> Optional[requests.Response]:
        """Fetch a URL, logging failures and returning None instead of crashing."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response
        except requests.RequestException as exc:
            logger.error("Failed to fetch %s: %s", url, exc)
            return None

    def pause(self) -> None:
        time.sleep(self.delay)
