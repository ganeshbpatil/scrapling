"""
Google Maps Reviews collector.
Uses Google Places API (free tier: 1000 req/month).
Tracks reviews for Pune residential projects and micro-market areas.
"""
import os, re, time
from datetime import datetime, timezone
from pune_intelligence.config import PUNE_MICRO_MARKETS, COMPETITORS

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

GMAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

PLACES_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

_SENTIMENT_POS = ["great", "excellent", "recommend", "good", "worth", "satisfied", "beautiful", "amazing"]
_SENTIMENT_NEG = ["bad", "poor", "fraud", "delay", "avoid", "worst", "terrible", "scam", "cheat", "fake"]

def _detect_sentiment(text):
    tl = text.lower()
    pos = sum(1 for k in _SENTIMENT_POS if k in tl)
    neg = sum(1 for k in _SENTIMENT_NEG if k in tl)
    if neg > pos: return "negative"
    if pos > neg: return "positive"
    return "neutral"

def _detect_markets(text):
    tl = text.lower()
    return [m for m in PUNE_MICRO_MARKETS if m.lower() in tl]


class GMapsCollector:
    def __init__(self, api_key: str = None):
        if not HAS_REQUESTS:
            raise RuntimeError("requests not installed")
        self.api_key = api_key or GMAPS_API_KEY
        if not self.api_key:
            raise RuntimeError("Set GOOGLE_MAPS_API_KEY env var")

    def search_projects(self, query: str) -> list:
        params = {"query": query, "key": self.api_key, "region": "in"}
        r = requests.get(PLACES_SEARCH_URL, params=params, timeout=10)
        return r.json().get("results", [])

    def get_reviews(self, place_id: str) -> list:
        params = {"place_id": place_id, "fields": "name,rating,reviews,formatted_address", "key": self.api_key}
        r = requests.get(PLACE_DETAILS_URL, params=params, timeout=10)
        return r.json().get("result", {})

    def collect_market_reviews(self, market: str, limit: int = 5) -> list:
        signals = []
        try:
            places = self.search_projects(f"residential project {market} Pune")[:limit]
            for place in places:
                place_id = place["place_id"]
                details = self.get_reviews(place_id)
                reviews = details.get("reviews", [])
                for review in reviews:
                    text = review.get("text", "")
                    if not text:
                        continue
                    signals.append({
                        "source": "Google Maps",
                        "project_name": details.get("name", ""),
                        "address": details.get("formatted_address", ""),
                        "place_id": place_id,
                        "rating": review.get("rating", 0),
                        "review_text": text[:1000],
                        "reviewer": review.get("author_name", ""),
                        "review_time": review.get("relative_time_description", ""),
                        "micro_market": market,
                        "overall_rating": details.get("rating", 0),
                        "sentiment": _detect_sentiment(text),
                        "signal_type": "gmaps_review",
                        "collected_at": datetime.now(timezone.utc).isoformat(),
                    })
                time.sleep(0.2)
        except Exception as e:
            print(f"  GMaps error ({market}): {e}")
        return signals

    def collect_competitor_reviews(self, competitor: str) -> list:
        signals = []
        try:
            places = self.search_projects(f"{competitor} Pune")[:3]
            for place in places:
                details = self.get_reviews(place["place_id"])
                for review in details.get("reviews", []):
                    text = review.get("text", "")
                    if not text:
                        continue
                    signals.append({
                        "source": "Google Maps",
                        "competitor": competitor,
                        "project_name": details.get("name", ""),
                        "rating": review.get("rating", 0),
                        "review_text": text[:1000],
                        "overall_rating": details.get("rating", 0),
                        "sentiment": _detect_sentiment(text),
                        "micro_markets": _detect_markets(text),
                        "signal_type": "competitor_review",
                        "collected_at": datetime.now(timezone.utc).isoformat(),
                    })
        except Exception as e:
            print(f"  GMaps competitor error ({competitor}): {e}")
        return signals

    def collect_all(self, markets: list = None, competitors: list = None) -> list:
        all_signals = []
        markets = markets or PUNE_MICRO_MARKETS[:5]
        for market in markets:
            s = self.collect_market_reviews(market)
            all_signals.extend(s)
            print(f"  GMaps {market}: {len(s)} reviews")
        if competitors:
            for comp in competitors[:5]:
                s = self.collect_competitor_reviews(comp)
                all_signals.extend(s)
        return all_signals
