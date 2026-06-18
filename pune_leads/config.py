PUNE_MICRO_MARKETS = [
    "Baner", "Balewadi", "Bhugaon", "Bavdhan", "Wakad", "Hinjewadi",
    "Mahalunge", "Kharadi", "Viman Nagar", "Kalyani Nagar", "Koregaon Park",
    "NIBM", "Undri", "Hadapsar", "Ravet", "Punawale", "Tathawade",
    "Pashan", "Aundh", "Kothrud", "Shivajinagar",
]

PROPERTY_CONFIGS = ["1 BHK", "2 BHK", "3 BHK", "4 BHK", "5 BHK", "Villa", "Plot", "Commercial"]

LEAD_SOURCES = {
    "99acres.com": "99acres",
    "magicbricks.com": "MagicBricks",
    "housing.com": "Housing.com",
    "commonfloor.com": "CommonFloor",
    "google.com": "Google Search",
    "facebook.com": "Facebook",
    "instagram.com": "Instagram",
    "linkedin.com": "LinkedIn",
    "reddit.com": "Reddit",
    "quora.com": "Quora",
}

CONFIDENCE_SCORES = {
    "direct_inquiry": 100,
    "contact_form": 90,
    "property_comment": 80,
    "property_discussion": 70,
    "forum_mention": 60,
    "general_interest": 50,
}

INTENT_KEYWORDS = {
    "Ready to Buy": ["ready to buy", "want to buy", "looking to buy", "purchase", "booking", "immediate", "finalizing"],
    "Researching": ["comparing", "researching", "options", "which is better", "suggestion", "advice", "explore"],
    "Investor": ["investment", "roi", "rental yield", "returns", "portfolio", "investor", "appreciation"],
    "Looking for Rental": ["rental", "rent", "tenant", "pg", "paying guest", "lease"],
    "Looking for Commercial": ["office", "shop", "commercial", "workspace", "retail", "showroom"],
    "Luxury Buyer": ["luxury", "premium", "high-end", "penthouse", "duplex", "ultra"],
    "NRI Buyer": ["nri", "abroad", "overseas", "usa", "uk", "dubai", "canada", "australia", "nri investor"],
}

_configs = ["1bhk", "2bhk", "3bhk", "4bhk", "villa", "plot"]
_markets = ["baner", "balewadi", "bhugaon", "bavdhan", "wakad", "hinjewadi", "kharadi", "hadapsar", "kothrud", "aundh"]
START_URLS = []
for _c in _configs:
    for _m in _markets[:5]:
        START_URLS.append(f"https://www.google.com/search?q={_c}+{_m.replace(' ', '+')}+pune+buy")

PORTAL_URLS = [
    "https://www.99acres.com/property-in-pune-ffid",
    "https://www.magicbricks.com/property-for-sale/residential-real-estate?proptype=Multistorey-Apartment&cityName=Pune",
    "https://housing.com/in/buy/searches/pune",
]

FORUM_URLS = [
    "https://www.quora.com/topic/Real-Estate-in-Pune",
    "https://www.reddit.com/r/pune/search/?q=property+buy&sort=new",
    "https://www.reddit.com/r/india/search/?q=pune+property&sort=new",
]
