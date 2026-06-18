from datetime import datetime, timezone
from scrapling.spiders import Spider, Response
from scrapling.fetchers import StealthyFetcher
from pune_leads.config import PUNE_MICRO_MARKETS, LEAD_SOURCES

_RELEVANCE_KW = [m.lower() for m in PUNE_MICRO_MARKETS] + [
    "bhk", "villa", "plot", "property", "apartment", "flat", "buy", "pune", "real estate",
]

class BaseLeadSpider(Spider):
    fetcher = StealthyFetcher  # TLS browser impersonation — bypasses basic bot detection
    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "RESPECT_ROBOTS_TXT": True,
        "CONCURRENT_REQUESTS": 5,
    }

    def is_relevant(self, url: str) -> bool:
        url_lower = url.lower()
        return any(kw in url_lower for kw in _RELEVANCE_KW)

    def get_lead_source(self, url: str) -> str:
        for domain, source in LEAD_SOURCES.items():
            if domain in url:
                return source
        return "Web"

    def build_lead(self, response: Response, **kwargs) -> dict:
        return {
            "name": "",
            "email": "",
            "phone": "",
            "configuration": "",
            "location_interest": "",
            "budget": "",
            "lead_source": self.get_lead_source(str(response.url)),
            "source_url": str(response.url),
            "lead_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "inquiry_text": "",
            "confidence_score": 0.0,
            "intent": "",
            **kwargs,
        }
