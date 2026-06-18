"""
Collects news articles and blog posts about Pune real estate.
Sources: Google News RSS, MagicBricks News, 99acres Articles, Economic Times.
"""
import re
from datetime import datetime, timezone
from scrapling.fetchers import StealthyFetcher
from pune_intelligence.config import PUNE_MICRO_MARKETS, COMPETITORS, INTENT_SIGNALS

_MARKET_RE = {m: re.compile(r'\b' + re.escape(m) + r'\b', re.IGNORECASE) for m in PUNE_MICRO_MARKETS}
_BUDGET_RE  = re.compile(r'\b([\d.]+)\s*(cr(?:ore)?|lakh?|lac)\b', re.IGNORECASE)

NEWS_RSS_FEEDS = [
    "https://news.google.com/rss/search?q=pune+real+estate&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=pune+property+price&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=pune+housing+market&hl=en-IN&gl=IN&ceid=IN:en",
]

SCRAPE_URLS = [
    "https://www.magicbricks.com/blog/category/real-estate-news/pune",
    "https://housing.com/news/category/real-estate/pune/",
    "https://www.99acres.com/articles/pune-real-estate-news.html",
]

def _detect_markets(text):
    return [m for m, p in _MARKET_RE.items() if p.search(text)]

def _detect_competitors(text):
    tl = text.lower()
    return [c for c in COMPETITORS if c.lower() in tl]

def _detect_sentiment(text):
    tl = text.lower()
    neg = sum(1 for k in ["delay", "fraud", "scam", "overpriced", "complaint", "issue"] if k in tl)
    pos = sum(1 for k in ["launch", "growth", "appreciation", "demand", "record", "boom"] if k in tl)
    if neg > pos: return "negative"
    if pos > neg: return "positive"
    return "neutral"


class NewsCollector:
    def __init__(self):
        self.fetcher = StealthyFetcher()

    def collect_rss(self) -> list:
        """Parse Google News RSS feeds."""
        signals = []
        for feed_url in NEWS_RSS_FEEDS:
            try:
                page = self.fetcher.fetch(feed_url)
                items = page.css("item")
                for item in items:
                    title = item.css("title::text").get("") or ""
                    link  = item.css("link::text").get("") or ""
                    pub   = item.css("pubDate::text").get("") or ""
                    desc  = item.css("description::text").get("") or ""
                    text  = f"{title} {desc}"
                    markets = _detect_markets(text)
                    signals.append({
                        "source": "News",
                        "title": title.strip(),
                        "url": link.strip(),
                        "published_at": pub.strip(),
                        "description": desc[:500],
                        "micro_markets": markets,
                        "competitors_mentioned": _detect_competitors(text),
                        "sentiment": _detect_sentiment(text),
                        "signal_type": "news_article",
                        "collected_at": datetime.now(timezone.utc).isoformat(),
                    })
            except Exception as e:
                print(f"  RSS error ({feed_url}): {e}")
        print(f"  News RSS: {len(signals)} articles")
        return signals

    def collect_portal_news(self) -> list:
        """Scrape news sections of property portals."""
        signals = []
        for url in SCRAPE_URLS:
            try:
                page = self.fetcher.fetch(url)
                for article in page.css("article, .blog-post, .news-item, .article-card"):
                    title = " ".join(article.css("h1::text, h2::text, h3::text, a::text").getall()).strip()
                    href  = article.css("a::attr(href)").get("") or ""
                    text  = " ".join(article.css("::text").getall())
                    if not title or "pune" not in text.lower():
                        continue
                    markets = _detect_markets(text)
                    signals.append({
                        "source": "Portal News",
                        "title": title[:200],
                        "url": href if href.startswith("http") else url,
                        "published_at": "",
                        "description": text[:500],
                        "micro_markets": markets,
                        "competitors_mentioned": _detect_competitors(text),
                        "sentiment": _detect_sentiment(text),
                        "signal_type": "portal_article",
                        "collected_at": datetime.now(timezone.utc).isoformat(),
                    })
            except Exception as e:
                print(f"  Portal news error ({url}): {e}")
        print(f"  Portal news: {len(signals)} articles")
        return signals

    def collect_all(self) -> list:
        return self.collect_rss() + self.collect_portal_news()
