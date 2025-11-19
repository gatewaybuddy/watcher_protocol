"""Base scraper class for data collection."""

import asyncio
import hashlib
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


logger = logging.getLogger(__name__)


@dataclass
class ParsedItem:
    """Standardized parsed item from any source."""

    source: str
    source_id: str
    title: str
    content: Optional[str] = None
    summary: Optional[str] = None
    url: Optional[str] = None
    published_at: Optional[datetime] = None
    authors: Optional[List[str]] = None
    organizations: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    def content_hash(self) -> str:
        """Generate hash for deduplication."""
        # Normalize title and create hash
        normalized = self.title.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()


class RateLimiter:
    """Simple rate limiter for API requests."""

    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self.min_interval = 60.0 / requests_per_minute
        self.last_request = 0.0

    async def wait(self):
        """Wait if necessary to respect rate limit."""
        now = asyncio.get_event_loop().time()
        time_since_last = now - self.last_request

        if time_since_last < self.min_interval:
            await asyncio.sleep(self.min_interval - time_since_last)

        self.last_request = asyncio.get_event_loop().time()


class BaseScraper(ABC):
    """Base class for all data scrapers."""

    def __init__(
        self,
        name: str,
        rate_limit: int = 30,
        timeout: int = 30,
        max_retries: int = 3
    ):
        self.name = name
        self.rate_limiter = RateLimiter(requests_per_minute=rate_limit)
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logging.getLogger(f"scraper.{name}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def fetch_with_retry(self, url: str, **kwargs) -> httpx.Response:
        """Fetch URL with retry logic."""
        await self.rate_limiter.wait()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, **kwargs)
            response.raise_for_status()
            return response

    @abstractmethod
    async def fetch(self) -> List[Any]:
        """
        Fetch raw data from the source.

        Returns:
            List of raw data items (format depends on source)
        """
        pass

    @abstractmethod
    async def parse(self, raw_data: List[Any]) -> List[ParsedItem]:
        """
        Parse raw data into standardized format.

        Args:
            raw_data: Raw data from fetch()

        Returns:
            List of ParsedItem objects
        """
        pass

    async def run(self) -> List[ParsedItem]:
        """
        Main execution method.

        Fetches data, parses it, and returns standardized items.
        """
        try:
            self.logger.info(f"Starting scraper: {self.name}")

            # Fetch raw data
            raw_data = await self.fetch()
            self.logger.info(f"Fetched {len(raw_data)} raw items")

            # Parse data
            parsed_items = await self.parse(raw_data)
            self.logger.info(f"Parsed {len(parsed_items)} items")

            return parsed_items

        except Exception as e:
            self.logger.error(f"Scraper {self.name} failed: {e}", exc_info=True)
            raise

    async def update_status(self, success: bool, error_msg: Optional[str] = None):
        """
        Update scraper status in database.

        Args:
            success: Whether the scraping was successful
            error_msg: Error message if failed
        """
        # TODO: Update scraper_status table
        pass
