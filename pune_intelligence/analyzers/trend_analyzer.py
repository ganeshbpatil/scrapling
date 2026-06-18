"""
Analyzes collected signals to produce:
- Micro-market demand rankings
- Rising vs falling areas
- Competitor share of voice
- Configuration demand breakdown
- Daily trend summary
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone

class TrendAnalyzer:

    def __init__(self, signals: list):
        self.signals = signals

    def market_demand_rank(self) -> list:
        """Rank micro-markets by number of mentions."""
        counts = Counter()
        sentiment = defaultdict(list)
        for s in self.signals:
            for market in s.get("micro_markets", []):
                counts[market] += 1
                sentiment[market].append(s.get("sentiment", "neutral"))
        ranked = []
        for market, count in counts.most_common():
            neg = sentiment[market].count("negative")
            pos = sentiment[market].count("positive")
            ranked.append({
                "micro_market": market,
                "mention_count": count,
                "positive_mentions": pos,
                "negative_mentions": neg,
                "sentiment_score": round((pos - neg) / max(count, 1), 2),
                "demand_score": round(count * (1 + (pos - neg) / max(count, 1)), 1),
            })
        return sorted(ranked, key=lambda x: x["demand_score"], reverse=True)

    def config_demand(self) -> list:
        """Which BHK configurations are most discussed."""
        counts = Counter()
        for s in self.signals:
            cfg = s.get("configuration", "")
            if cfg:
                counts[cfg] += 1
        return [{"configuration": k, "mentions": v} for k, v in counts.most_common()]

    def competitor_share_of_voice(self) -> list:
        """How often each builder is mentioned and with what sentiment."""
        counts = Counter()
        sentiments = defaultdict(list)
        for s in self.signals:
            for comp in s.get("competitors_mentioned", []):
                counts[comp] += 1
                sentiments[comp].append(s.get("sentiment", "neutral"))
        total = max(sum(counts.values()), 1)
        result = []
        for comp, count in counts.most_common():
            neg = sentiments[comp].count("negative")
            pos = sentiments[comp].count("positive")
            result.append({
                "competitor": comp,
                "mentions": count,
                "share_of_voice_pct": round(count / total * 100, 1),
                "positive": pos,
                "negative": neg,
                "net_sentiment": "positive" if pos >= neg else "negative",
            })
        return result

    def intent_breakdown(self) -> dict:
        """Distribution of buyer intent across all signals."""
        counts = Counter(s.get("intent", "general") for s in self.signals)
        total = max(sum(counts.values()), 1)
        return {k: {"count": v, "pct": round(v / total * 100, 1)} for k, v in counts.most_common()}

    def source_breakdown(self) -> dict:
        counts = Counter(s.get("source", "Unknown") for s in self.signals)
        return dict(counts.most_common())

    def daily_trend(self) -> list:
        """Signals per day to show activity trend."""
        by_date = Counter()
        for s in self.signals:
            ts = s.get("collected_at", "") or s.get("created_at", "")
            if ts:
                date = ts[:10]
                by_date[date] += 1
        return [{"date": k, "signals": v} for k, v in sorted(by_date.items())]

    def hot_markets(self, top_n: int = 5) -> list:
        """Markets with rising demand signal."""
        ranked = self.market_demand_rank()
        return ranked[:top_n]

    def recommendations(self) -> list:
        """Actionable recommendations based on signal analysis."""
        recs = []
        ranked = self.market_demand_rank()
        config_demand = self.config_demand()
        competitors = self.competitor_share_of_voice()

        if ranked:
            top = ranked[0]
            recs.append({
                "type": "opportunity",
                "priority": "HIGH",
                "title": f"High demand in {top['micro_market']}",
                "detail": f"{top['mention_count']} mentions with {top['positive_mentions']} positive signals. Consider increasing inventory or marketing here.",
                "action": f"Launch targeted campaign for {top['micro_market']}",
            })
        # Rising but low-inventory markets
        for market_data in ranked[1:4]:
            if market_data["sentiment_score"] > 0.3:
                recs.append({
                    "type": "expansion",
                    "priority": "MEDIUM",
                    "title": f"Growing interest in {market_data['micro_market']}",
                    "detail": f"Strong positive sentiment ({market_data['positive_mentions']} positive vs {market_data['negative_mentions']} negative). Early mover advantage.",
                    "action": f"Evaluate land acquisition or project launch in {market_data['micro_market']}",
                })
        # Most demanded config
        if config_demand:
            top_cfg = config_demand[0]
            recs.append({
                "type": "product",
                "priority": "HIGH",
                "title": f"{top_cfg['configuration']} is most discussed",
                "detail": f"{top_cfg['mentions']} mentions — buyers are actively searching for this configuration.",
                "action": f"Ensure {top_cfg['configuration']} units are available in top demand markets",
            })
        # Competitor with negative sentiment
        for comp in competitors:
            if comp["net_sentiment"] == "negative" and comp["mentions"] >= 3:
                recs.append({
                    "type": "competitive",
                    "priority": "MEDIUM",
                    "title": f"{comp['competitor']} receiving negative reviews",
                    "detail": f"{comp['negative']} negative mentions. Their dissatisfied buyers are potential leads for you.",
                    "action": f"Run retargeting ads targeting {comp['competitor']} searchers. Highlight your delivery track record.",
                })
        return recs

    def full_report(self) -> dict:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_signals": len(self.signals),
            "market_demand_rank": self.market_demand_rank(),
            "config_demand": self.config_demand(),
            "competitor_share_of_voice": self.competitor_share_of_voice(),
            "intent_breakdown": self.intent_breakdown(),
            "source_breakdown": self.source_breakdown(),
            "daily_trend": self.daily_trend(),
            "hot_markets": self.hot_markets(),
            "recommendations": self.recommendations(),
        }
