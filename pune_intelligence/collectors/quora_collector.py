"""
Collects public Quora questions and answers about Pune real estate.
No login required — only public pages.
"""
import re
from datetime import datetime, timezone
from scrapling.fetchers import StealthyFetcher
from pune_intelligence.config import PUNE_MICRO_MARKETS, COMPETITORS, SEARCH_QUERIES, INTENT_SIGNALS

_MARKET_RE = {m: re.compile(r'\b' + re.escape(m) + r'\b', re.IGNORECASE) for m in PUNE_MICRO_MARKETS}

QUORA_SEARCH_URLS = [
    "https://www.quora.com/search?q=pune+property+buy",
    "https://www.quora.com/search?q=best+area+pune+flat",
    "https://www.quora.com/search?q=pune+real+estate+investment+2024",
    "https://www.quora.com/topic/Real-Estate-in-Pune",
]

def _detect_markets(text):
    return [m for m, p in _MARKET_RE.items() if p.search(text)]

def _detect_intent(text):
    tl = text.lower()
    for intent, kws in INTENT_SIGNALS.items():
        if any(k in tl for k in kws):
            return intent
    return "general"

def _detect_competitors(text):
    return [c for c in COMPETITORS if c.lower() in text.lower()]


class QuoraCollector:
    def __init__(self):
        self.fetcher = StealthyFetcher()

    def collect_search(self, url: str) -> list:
        signals = []
        try:
            page = self.fetcher.fetch(url)
            # Quora search results / topic page
            for item in page.css(".q-text, .qu-dynamicFontSize, [class*='question'], [class*='answer']"):
                text = " ".join(item.css("::text").getall()).strip()
                if len(text) < 20 or "pune" not in text.lower():
                    continue
                markets = _detect_markets(text)
                signals.append({
                    "source": "Quora",
                    "title": text[:200],
                    "text": text[:1000],
                    "url": url,
                    "micro_markets": markets,
                    "intent": _detect_intent(text),
                    "competitors_mentioned": _detect_competitors(text),
                    "sentiment": "negative" if _detect_intent(text) == "negative" else "positive",
                    "signal_type": "quora_post",
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                })
        except Exception as e:
            print(f"  Quora error ({url}): {e}")
        return signals

    def collect_all(self) -> list:
        all_signals = []
        for url in QUORA_SEARCH_URLS:
            signals = self.collect_search(url)
            all_signals.extend(signals)
        print(f"  Quora: {len(all_signals)} signals")
        return all_signals
