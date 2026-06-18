"""
Google Trends collector — tracks daily search volumes for Pune micro-markets.
Uses pytrends (unofficial but stable Google Trends API wrapper).
"""
import time
from datetime import datetime, timezone
from pune_intelligence.config import PUNE_MICRO_MARKETS, PROPERTY_CONFIGS

try:
    from pytrends.request import TrendReq
    HAS_PYTRENDS = True
except ImportError:
    HAS_PYTRENDS = False


class TrendsCollector:
    def __init__(self):
        if not HAS_PYTRENDS:
            raise RuntimeError("pytrends not installed. Run: pip install pytrends")
        self.pytrends = TrendReq(hl="en-IN", tz=330, timeout=(10, 25))

    def get_market_trends(self, timeframe: str = "today 3-m") -> list:
        """Get search trend data for each Pune micro-market."""
        results = []
        # Process in batches of 5 (Google Trends limit)
        batches = [PUNE_MICRO_MARKETS[i:i+5] for i in range(0, len(PUNE_MICRO_MARKETS), 5)]
        for batch in batches:
            keywords = [f"{m} pune property" for m in batch]
            try:
                self.pytrends.build_payload(keywords, geo="IN-MH", timeframe=timeframe)
                df = self.pytrends.interest_over_time()
                if df.empty:
                    continue
                for kw, market in zip(keywords, batch):
                    if kw not in df.columns:
                        continue
                    series = df[kw]
                    results.append({
                        "source": "Google Trends",
                        "micro_market": market,
                        "keyword": kw,
                        "avg_interest": round(float(series.mean()), 1),
                        "peak_interest": int(series.max()),
                        "latest_interest": int(series.iloc[-1]),
                        "trend_direction": "rising" if series.iloc[-1] > series.mean() else "falling",
                        "collected_at": datetime.now(timezone.utc).isoformat(),
                        "timeframe": timeframe,
                    })
                time.sleep(1)  # rate limit
            except Exception as e:
                print(f"  Trends batch error ({batch}): {e}")
        return results

    def get_config_trends(self, timeframe: str = "today 3-m") -> list:
        """Track which BHK configurations are trending in Pune searches."""
        results = []
        keywords = [f"{c} pune" for c in PROPERTY_CONFIGS[:5]]
        try:
            self.pytrends.build_payload(keywords, geo="IN-MH", timeframe=timeframe)
            df = self.pytrends.interest_over_time()
            if not df.empty:
                for kw, config in zip(keywords, PROPERTY_CONFIGS[:5]):
                    if kw not in df.columns:
                        continue
                    series = df[kw]
                    results.append({
                        "source": "Google Trends",
                        "configuration": config,
                        "keyword": kw,
                        "avg_interest": round(float(series.mean()), 1),
                        "peak_interest": int(series.max()),
                        "latest_interest": int(series.iloc[-1]),
                        "trend_direction": "rising" if series.iloc[-1] > series.mean() else "falling",
                        "collected_at": datetime.now(timezone.utc).isoformat(),
                    })
        except Exception as e:
            print(f"  Config trends error: {e}")
        return results

    def get_competitor_trends(self, competitors: list, timeframe: str = "today 3-m") -> list:
        """Track which builders are being searched most."""
        results = []
        batches = [competitors[i:i+5] for i in range(0, len(competitors), 5)]
        for batch in batches:
            try:
                self.pytrends.build_payload(batch, geo="IN-MH", timeframe=timeframe)
                df = self.pytrends.interest_over_time()
                if df.empty:
                    continue
                for competitor in batch:
                    if competitor not in df.columns:
                        continue
                    series = df[competitor]
                    results.append({
                        "source": "Google Trends",
                        "competitor": competitor,
                        "avg_interest": round(float(series.mean()), 1),
                        "peak_interest": int(series.max()),
                        "latest_interest": int(series.iloc[-1]),
                        "trend_direction": "rising" if series.iloc[-1] > series.mean() else "falling",
                        "collected_at": datetime.now(timezone.utc).isoformat(),
                    })
                time.sleep(1)
            except Exception as e:
                print(f"  Competitor trends error ({batch}): {e}")
        return results

    def get_related_queries(self, market: str) -> dict:
        """Get what people ALSO search after searching for a micro-market."""
        try:
            self.pytrends.build_payload([f"{market} pune property"], geo="IN-MH")
            related = self.pytrends.related_queries()
            key = f"{market} pune property"
            top = related.get(key, {}).get("top")
            rising = related.get(key, {}).get("rising")
            return {
                "micro_market": market,
                "top_queries": top.to_dict("records") if top is not None else [],
                "rising_queries": rising.to_dict("records") if rising is not None else [],
            }
        except Exception as e:
            return {"micro_market": market, "error": str(e)}

    def collect_all(self) -> dict:
        print("  Fetching market trends...")
        market_trends = self.get_market_trends()
        print(f"  → {len(market_trends)} market trend records")
        print("  Fetching config trends...")
        config_trends = self.get_config_trends()
        print(f"  → {len(config_trends)} config trend records")
        return {"market_trends": market_trends, "config_trends": config_trends}
