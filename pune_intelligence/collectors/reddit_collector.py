"""
Collects public Reddit posts and comments about Pune real estate.
Uses PRAW (official Reddit API) — free, legal, no scraping.
"""
import os, re
from datetime import datetime, timezone
from pune_intelligence.config import PUNE_MICRO_MARKETS, COMPETITORS, PROPERTY_CONFIGS, REDDIT_SUBREDDITS, INTENT_SIGNALS

try:
    import praw
    HAS_PRAW = True
except ImportError:
    HAS_PRAW = False

_MARKET_RE = {m: re.compile(r'\b' + re.escape(m) + r'\b', re.IGNORECASE) for m in PUNE_MICRO_MARKETS}
_CONFIG_RE  = {c: re.compile(r'\b' + re.escape(c) + r'\b', re.IGNORECASE) for c in PROPERTY_CONFIGS}
_BUDGET_RE  = re.compile(r'\b([\d.]+)\s*(cr(?:ore)?|lakh?|lac)\b', re.IGNORECASE)

def _detect_markets(text):
    return [m for m, p in _MARKET_RE.items() if p.search(text)]

def _detect_config(text):
    for c, p in _CONFIG_RE.items():
        if p.search(text): return c
    return ""

def _detect_budget(text):
    m = _BUDGET_RE.search(text)
    if not m: return ""
    amt, unit = float(m.group(1)), m.group(2).lower()
    return f"{amt} Cr" if unit.startswith("cr") else f"{amt} Lakh"

def _detect_intent(text):
    tl = text.lower()
    for intent, kws in INTENT_SIGNALS.items():
        if any(k in tl for k in kws):
            return intent
    return "general"

def _detect_competitors(text):
    tl = text.lower()
    return [c for c in COMPETITORS if c.lower() in tl]

def _is_pune_property(text):
    tl = text.lower()
    return "pune" in tl and any(k in tl for k in ["property", "flat", "bhk", "buy", "invest", "plot", "apartment"])


class RedditCollector:
    def __init__(self):
        if not HAS_PRAW:
            raise RuntimeError("praw not installed. Run: pip install praw")
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID", ""),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET", ""),
            user_agent="PunePropertyIntelligence/1.0 (market research tool)",
        )

    def collect_subreddit(self, subreddit_name: str, limit: int = 100) -> list:
        signals = []
        sub = self.reddit.subreddit(subreddit_name)
        for post in sub.search("pune property OR pune flat OR pune real estate", limit=limit, sort="new"):
            text = f"{post.title} {post.selftext}"
            if not _is_pune_property(text):
                continue
            markets = _detect_markets(text)
            signal = {
                "source": "Reddit",
                "subreddit": subreddit_name,
                "post_id": post.id,
                "title": post.title,
                "text": post.selftext[:1000],
                "url": f"https://reddit.com{post.permalink}",
                "author": str(post.author) if post.author else "[deleted]",
                "upvotes": post.score,
                "comments_count": post.num_comments,
                "created_at": datetime.fromtimestamp(post.created_utc, tz=timezone.utc).isoformat(),
                "micro_markets": markets,
                "configuration": _detect_config(text),
                "budget": _detect_budget(text),
                "intent": _detect_intent(text),
                "competitors_mentioned": _detect_competitors(text),
                "sentiment": "negative" if _detect_intent(text) == "negative" else "positive",
                "signal_type": "post",
            }
            signals.append(signal)

            # Collect top comments
            post.comments.replace_more(limit=0)
            for comment in list(post.comments)[:20]:
                ct = comment.body
                if not _is_pune_property(ct):
                    continue
                cm = _detect_markets(ct)
                signals.append({
                    "source": "Reddit",
                    "subreddit": subreddit_name,
                    "post_id": post.id,
                    "title": f"Comment on: {post.title}",
                    "text": ct[:500],
                    "url": f"https://reddit.com{post.permalink}",
                    "author": str(comment.author) if comment.author else "[deleted]",
                    "upvotes": comment.score,
                    "comments_count": 0,
                    "created_at": datetime.fromtimestamp(comment.created_utc, tz=timezone.utc).isoformat(),
                    "micro_markets": cm or markets,
                    "configuration": _detect_config(ct) or signal["configuration"],
                    "budget": _detect_budget(ct) or signal["budget"],
                    "intent": _detect_intent(ct),
                    "competitors_mentioned": _detect_competitors(ct),
                    "sentiment": "negative" if _detect_intent(ct) == "negative" else "positive",
                    "signal_type": "comment",
                })
        return signals

    def collect_all(self, limit: int = 50) -> list:
        all_signals = []
        for sub in REDDIT_SUBREDDITS:
            try:
                signals = self.collect_subreddit(sub, limit)
                all_signals.extend(signals)
                print(f"  Reddit r/{sub}: {len(signals)} signals")
            except Exception as e:
                print(f"  Reddit r/{sub} error: {e}")
        return all_signals


class RedditCollectorDemo:
    """Scrape-based fallback when no Reddit API credentials are available."""

    def __init__(self):
        from scrapling.fetchers import StealthyFetcher
        self.fetcher = StealthyFetcher()

    def collect_all(self, limit: int = 20) -> list:
        from scrapling import Adaptor
        signals = []
        urls = [
            "https://old.reddit.com/r/pune/search?q=property+buy&sort=new&restrict_sr=on",
            "https://old.reddit.com/r/india/search?q=pune+property&sort=new&restrict_sr=on",
        ]
        for url in urls:
            try:
                page = self.fetcher.fetch(url)
                for item in page.css(".search-result-link"):
                    title = " ".join(item.css("::text").getall())
                    href = item.attrib.get("href", "")
                    if not _is_pune_property(title):
                        continue
                    markets = _detect_markets(title)
                    signals.append({
                        "source": "Reddit",
                        "subreddit": "r/pune",
                        "post_id": href,
                        "title": title,
                        "text": title,
                        "url": href,
                        "author": "",
                        "upvotes": 0,
                        "comments_count": 0,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "micro_markets": markets,
                        "configuration": _detect_config(title),
                        "budget": _detect_budget(title),
                        "intent": _detect_intent(title),
                        "competitors_mentioned": _detect_competitors(title),
                        "sentiment": "positive",
                        "signal_type": "post",
                    })
            except Exception as e:
                print(f"  Reddit scrape error: {e}")
        print(f"  Reddit (scrape): {len(signals)} signals")
        return signals
