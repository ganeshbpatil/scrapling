#!/usr/bin/env python3
import argparse, json, os, subprocess, sys

def run_spider(spider_name: str, pipeline, crawl_base: str = "./crawl_data"):
    from pune_leads.spiders.google_spider import GoogleLeadSpider
    from pune_leads.spiders.portal_spider import PortalLeadSpider
    from pune_leads.spiders.forum_spider import ForumLeadSpider

    spider_map = {"google": GoogleLeadSpider, "portal": PortalLeadSpider, "forum": ForumLeadSpider}
    if spider_name not in spider_map:
        print(f"Unknown spider '{spider_name}'. Choose from: {list(spider_map.keys())}")
        sys.exit(1)

    SpiderClass = spider_map[spider_name]
    print(f"\n▶  Starting spider: {spider_name}")
    result = SpiderClass(crawldir=f"{crawl_base}/{spider_name}").start()
    count = 0
    for item in result.items:
        if pipeline.process(dict(item)):
            count += 1
    print(f"✓  Spider '{spider_name}' done — {count} leads collected")

def cmd_spider(args):
    os.makedirs("output", exist_ok=True)
    from pune_leads.pipeline.lead_pipeline import LeadPipeline
    pipeline = LeadPipeline(output_dir="output", use_postgres=args.postgres, use_mongo=args.mongo)
    names = ["google", "portal", "forum"] if args.all else ([args.name] if args.name else [])
    if not names:
        print("Specify --name <spider> or --all")
        sys.exit(1)
    for name in names:
        run_spider(name, pipeline)
    stats = pipeline.get_stats()
    print(f"\n📊 Total leads: {stats['total']}")
    print(f"   By config:   {stats['by_config']}")
    print(f"   By location: {stats['by_location']}")
    print(f"   By source:   {stats['by_source']}")
    print(f"   By intent:   {stats['by_intent']}")

def cmd_dashboard(args):
    subprocess.run([sys.executable, "-m", "streamlit", "run", "pune_leads/dashboard/app.py"])

def cmd_export(args):
    from pune_leads.storage.json_storage import JSONStorage
    from pune_leads.storage.csv_storage import CSVStorage
    leads = JSONStorage("output/leads.json").all()
    if args.format == "csv":
        store = CSVStorage("output/export.csv")
        for lead in leads:
            store.save(lead)
        store.close()
        print(f"Exported {len(leads)} leads → output/export.csv")
    else:
        with open("output/export.json", "w") as f:
            json.dump(leads, f, indent=2, default=str)
        print(f"Exported {len(leads)} leads → output/export.json")

def cmd_stats(args):
    from pune_leads.storage.json_storage import JSONStorage
    leads = JSONStorage("output/leads.json").all()
    print(f"Total leads: {len(leads)}")
    def tally(field):
        counts = {}
        for l in leads:
            v = l.get(field, "?") or "?"
            counts[v] = counts.get(v, 0) + 1
        return counts
    for label, field in [("By config", "configuration"), ("By location", "location_interest"),
                          ("By source", "lead_source"), ("By intent", "intent")]:
        print(f"{label}: {tally(field)}")

def main():
    parser = argparse.ArgumentParser(description="Pune Real Estate Lead Intelligence Scraper")
    sub = parser.add_subparsers(dest="command")

    sp = sub.add_parser("spider", help="Run scraping spiders")
    sp.add_argument("--name", help="Spider: google | portal | forum")
    sp.add_argument("--all", action="store_true", help="Run all spiders")
    sp.add_argument("--postgres", action="store_true", help="Save to PostgreSQL")
    sp.add_argument("--mongo", action="store_true", help="Save to MongoDB")

    sub.add_parser("dashboard", help="Launch Streamlit dashboard")

    ep = sub.add_parser("export", help="Export leads to file")
    ep.add_argument("--format", choices=["json", "csv"], default="json")

    sub.add_parser("stats", help="Print lead statistics")

    args = parser.parse_args()
    dispatch = {"spider": cmd_spider, "dashboard": cmd_dashboard,
                "export": cmd_export, "stats": cmd_stats}
    if args.command in dispatch:
        dispatch[args.command](args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
