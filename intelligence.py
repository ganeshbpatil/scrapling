#!/usr/bin/env python3
"""
Pune Real Estate Market Intelligence Platform
Usage:
  python intelligence.py collect          # collect from all sources
  python intelligence.py collect --demo   # generate demo data (no API keys needed)
  python intelligence.py collect --reddit # Reddit only
  python intelligence.py collect --news   # News + Quora only
  python intelligence.py report           # print latest report
  python intelligence.py dashboard        # launch Streamlit dashboard
"""
import argparse, json, os, sys, subprocess, random
from datetime import datetime, timezone, timedelta
from pune_intelligence.storage.signal_store import SignalStore
from pune_intelligence.analyzers.trend_analyzer import TrendAnalyzer
from pune_intelligence.config import (
    PUNE_MICRO_MARKETS, PROPERTY_CONFIGS, COMPETITORS, INTENT_SIGNALS
)

def demo_signals(n: int = 120) -> list:
    """Generate realistic demo signals for testing."""
    sources = ["Reddit", "Quora", "News", "Google Maps", "Portal News"]
    intents = list(INTENT_SIGNALS.keys())
    sentiments = ["positive", "positive", "positive", "negative", "neutral"]
    signals = []
    for i in range(n):
        date = datetime.now(timezone.utc) - timedelta(days=random.randint(0, 14))
        markets = random.sample(PUNE_MICRO_MARKETS, k=random.randint(1, 3))
        comp = random.sample(COMPETITORS, k=random.randint(0, 2))
        signals.append({
            "source": random.choice(sources),
            "title": f"Discussion about property in {markets[0]} Pune",
            "text": f"Looking for {random.choice(PROPERTY_CONFIGS)} in {markets[0]}. Budget around 80 lakh. Any suggestions?",
            "url": f"https://reddit.com/r/pune/post{i}",
            "micro_markets": markets,
            "configuration": random.choice(PROPERTY_CONFIGS),
            "budget": random.choice(["50 Lakh", "75 Lakh", "1.2 Cr", "1.5 Cr", "2.0 Cr"]),
            "intent": random.choice(intents),
            "competitors_mentioned": comp,
            "sentiment": random.choice(sentiments),
            "signal_type": "post",
            "upvotes": random.randint(0, 500),
            "collected_at": date.isoformat(),
            "created_at": date.isoformat(),
        })
    return signals

def cmd_collect(args):
    store = SignalStore("output/intelligence")
    all_signals = []

    if args.demo:
        print("Generating demo intelligence data...")
        demo = demo_signals(150)
        added = store.save_signals(demo)
        print(f"✓ {added} demo signals added")
    else:
        if args.reddit or args.all:
            print("Collecting Reddit signals...")
            try:
                client_id = os.getenv("REDDIT_CLIENT_ID", "")
                if client_id:
                    from pune_intelligence.collectors.reddit_collector import RedditCollector
                    signals = RedditCollector().collect_all()
                else:
                    from pune_intelligence.collectors.reddit_collector import RedditCollectorDemo
                    signals = RedditCollectorDemo().collect_all()
                all_signals.extend(signals)
            except Exception as e:
                print(f"  Reddit error: {e}")

        if args.news or args.all:
            print("Collecting News signals...")
            try:
                from pune_intelligence.collectors.news_collector import NewsCollector
                all_signals.extend(NewsCollector().collect_all())
            except Exception as e:
                print(f"  News error: {e}")

        if args.quora or args.all:
            print("Collecting Quora signals...")
            try:
                from pune_intelligence.collectors.quora_collector import QuoraCollector
                all_signals.extend(QuoraCollector().collect_all())
            except Exception as e:
                print(f"  Quora error: {e}")

        if args.gmaps or args.all:
            api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
            if api_key:
                print("Collecting Google Maps reviews...")
                try:
                    from pune_intelligence.collectors.gmaps_collector import GMapsCollector
                    all_signals.extend(GMapsCollector(api_key).collect_all())
                except Exception as e:
                    print(f"  GMaps error: {e}")
            else:
                print("  Skipping GMaps (set GOOGLE_MAPS_API_KEY)")

        if not (args.reddit or args.news or args.quora or args.gmaps):
            args.all = True
            return cmd_collect(args)

        added = store.save_signals(all_signals)
        print(f"\n✓ {added} new signals saved (total: {len(store.all_signals())})")

    # Generate report
    analyzer = TrendAnalyzer(store.all_signals())
    report = analyzer.full_report()
    store.save_report(report)
    print(f"✓ Daily report generated")
    print(f"  Hot markets: {[m['micro_market'] for m in report['hot_markets']]}")
    print(f"  Top config:  {report['config_demand'][0]['configuration'] if report['config_demand'] else '—'}")
    print(f"  Recommendations: {len(report['recommendations'])}")

def cmd_report(args):
    store = SignalStore("output/intelligence")
    report = store.latest_report()
    if not report:
        print("No report yet. Run: python intelligence.py collect")
        return
    print(json.dumps(report, indent=2, default=str))

def cmd_dashboard(args):
    subprocess.run([sys.executable, "-m", "streamlit", "run", "pune_intelligence/dashboard/app.py"])

def main():
    parser = argparse.ArgumentParser(description="Pune Market Intelligence Platform")
    sub = parser.add_subparsers(dest="command")

    cp = sub.add_parser("collect", help="Collect intelligence signals")
    cp.add_argument("--demo",   action="store_true", help="Generate demo data (no API keys needed)")
    cp.add_argument("--reddit", action="store_true", help="Reddit only")
    cp.add_argument("--news",   action="store_true", help="News + Quora only")
    cp.add_argument("--quora",  action="store_true", help="Quora only")
    cp.add_argument("--gmaps",  action="store_true", help="Google Maps only (needs API key)")
    cp.add_argument("--all",    action="store_true", help="All sources")

    sub.add_parser("report",    help="Print latest intelligence report")
    sub.add_parser("dashboard", help="Launch Streamlit dashboard")

    args = parser.parse_args()
    dispatch = {"collect": cmd_collect, "report": cmd_report, "dashboard": cmd_dashboard}
    if args.command in dispatch:
        dispatch[args.command](args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
