"""arXiv scraper for AI research papers."""

import re
from datetime import datetime, timedelta
from typing import List
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

from ..base_scraper import BaseScraper, ParsedItem


class ArxivScraper(BaseScraper):
    """Scraper for arXiv papers."""

    # Keywords related to AI alignment and safety
    ALIGNMENT_KEYWORDS = [
        "AI safety", "AI alignment", "value alignment",
        "robustness", "interpretability", "explainability",
        "adversarial", "reward hacking", "specification gaming",
        "corrigibility", "mesa-optimization", "inner alignment",
        "outer alignment", "scalable oversight", "RLHF",
        "AI governance", "AI ethics", "existential risk",
        "AGI", "artificial general intelligence"
    ]

    def __init__(
        self,
        categories: List[str] = None,
        max_results: int = 100,
        days_back: int = 7,
        **kwargs
    ):
        """
        Initialize arXiv scraper.

        Args:
            categories: arXiv categories to search (default: cs.AI, cs.LG, cs.CL, cs.CY)
            max_results: Maximum results per query
            days_back: How many days back to search
        """
        super().__init__(name="arxiv", **kwargs)

        self.categories = categories or ["cs.AI", "cs.LG", "cs.CL", "cs.CY"]
        self.max_results = max_results
        self.days_back = days_back
        self.base_url = "http://export.arxiv.org/api/query"

    async def fetch(self) -> List[ET.Element]:
        """Fetch papers from arXiv API."""
        all_entries = []

        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=self.days_back)

        # Query each category
        for category in self.categories:
            self.logger.info(f"Fetching arXiv category: {category}")

            # Build query
            query_parts = [f"cat:{category}"]

            # Add date filter (submittedDate works better than lastUpdatedDate)
            date_str = start_date.strftime("%Y%m%d")
            query_parts.append(f"submittedDate:[{date_str}* TO *]")

            # Combine query
            search_query = " AND ".join(query_parts)

            # Build URL
            params = {
                "search_query": search_query,
                "start": 0,
                "max_results": self.max_results,
                "sortBy": "submittedDate",
                "sortOrder": "descending"
            }

            url = f"{self.base_url}?{urlencode(params)}"

            try:
                response = await self.fetch_with_retry(url)
                root = ET.fromstring(response.text)

                # Extract entries
                namespace = {"atom": "http://www.w3.org/2005/Atom"}
                entries = root.findall("atom:entry", namespace)

                self.logger.info(f"Found {len(entries)} papers in {category}")
                all_entries.extend(entries)

            except Exception as e:
                self.logger.error(f"Error fetching category {category}: {e}")
                continue

        return all_entries

    async def parse(self, raw_data: List[ET.Element]) -> List[ParsedItem]:
        """Parse arXiv XML entries into ParsedItem objects."""
        items = []
        namespace = {"atom": "http://www.w3.org/2005/Atom"}

        for entry in raw_data:
            try:
                # Extract basic fields
                arxiv_id = self._extract_text(entry, "atom:id", namespace)
                title = self._extract_text(entry, "atom:title", namespace)
                summary = self._extract_text(entry, "atom:summary", namespace)
                published = self._extract_text(entry, "atom:published", namespace)

                # Extract authors
                authors = []
                for author in entry.findall("atom:author", namespace):
                    name = self._extract_text(author, "atom:name", namespace)
                    if name:
                        authors.append(name)

                # Extract categories
                categories = []
                for category in entry.findall("atom:category", namespace):
                    term = category.get("term")
                    if term:
                        categories.append(term)

                # Check if paper is alignment-related
                is_alignment_related = self._is_alignment_related(title, summary)

                # Extract keywords from title and abstract
                keywords = self._extract_keywords(title, summary)

                # Parse date
                published_dt = None
                if published:
                    try:
                        published_dt = datetime.fromisoformat(published.replace('Z', '+00:00'))
                    except ValueError:
                        pass

                # Create ParsedItem
                item = ParsedItem(
                    source="arxiv",
                    source_id=arxiv_id,
                    title=title.strip() if title else "",
                    content=summary.strip() if summary else None,
                    summary=summary[:500] + "..." if summary and len(summary) > 500 else summary,
                    url=arxiv_id,  # arXiv ID is the URL
                    published_at=published_dt,
                    authors=authors if authors else None,
                    keywords=keywords if keywords else None,
                    metadata={
                        "categories": categories,
                        "is_alignment_related": is_alignment_related
                    }
                )

                items.append(item)

            except Exception as e:
                self.logger.error(f"Error parsing entry: {e}")
                continue

        return items

    def _extract_text(
        self,
        element: ET.Element,
        path: str,
        namespace: dict
    ) -> str:
        """Extract text from XML element."""
        found = element.find(path, namespace)
        if found is not None and found.text:
            # Clean up whitespace
            return re.sub(r'\s+', ' ', found.text).strip()
        return ""

    def _is_alignment_related(self, title: str, summary: str) -> bool:
        """Check if paper is related to AI alignment/safety."""
        text = f"{title} {summary}".lower()

        for keyword in self.ALIGNMENT_KEYWORDS:
            if keyword.lower() in text:
                return True

        return False

    def _extract_keywords(self, title: str, summary: str) -> List[str]:
        """Extract relevant keywords from title and summary."""
        text = f"{title} {summary}".lower()
        found_keywords = []

        for keyword in self.ALIGNMENT_KEYWORDS:
            if keyword.lower() in text:
                found_keywords.append(keyword)

        return list(set(found_keywords))  # Remove duplicates


# Example usage
async def main():
    """Test the scraper."""
    scraper = ArxivScraper(max_results=10, days_back=7)
    items = await scraper.run()

    print(f"\nFound {len(items)} papers")
    for item in items[:5]:  # Show first 5
        print(f"\n{'='*80}")
        print(f"Title: {item.title}")
        print(f"Authors: {', '.join(item.authors) if item.authors else 'N/A'}")
        print(f"Published: {item.published_at}")
        print(f"URL: {item.url}")
        print(f"Alignment-related: {item.metadata.get('is_alignment_related')}")
        if item.keywords:
            print(f"Keywords: {', '.join(item.keywords)}")


if __name__ == "__main__":
    import asyncio
    import logging

    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
