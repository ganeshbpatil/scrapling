from datetime import datetime

PUNE_MICRO_MARKETS = [
    "Baner", "Balewadi", "Bhugaon", "Bavdhan", "Wakad", "Hinjewadi",
    "Mahalunge", "Kharadi", "Viman Nagar", "Kalyani Nagar", "Koregaon Park",
    "NIBM", "Undri", "Hadapsar", "Ravet", "Punawale", "Tathawade",
    "Pashan", "Aundh", "Kothrud", "Shivajinagar",
]

PROPERTY_CONFIGS = ["1 BHK", "2 BHK", "3 BHK", "4 BHK", "5 BHK", "Villa", "Plot", "Commercial"]

BUDGET_RANGES = ["Under 50 Lakh", "50-75 Lakh", "75L-1Cr", "1-1.5 Cr", "1.5-2 Cr", "2 Cr+"]

# Known Pune builders/competitors to track
COMPETITORS = [
    "Godrej Properties", "Kolte Patil", "Paranjape Schemes", "Goel Ganga",
    "VTP Realty", "Kumar Properties", "Rohan Builders", "Nyati Group",
    "Panchshil Realty", "Majestique Landmarks", "Gera Developments",
    "Pride Purple", "Shapoorji Pallonji", "Sobha", "Lodha",
]

# Reddit subreddits to monitor
REDDIT_SUBREDDITS = ["pune", "india", "IndiaInvestments", "personalfinanceindia", "realestateindia"]

# Google Trends keywords per micro-market
TREND_KEYWORDS = []
for market in PUNE_MICRO_MARKETS[:10]:  # top 10 markets
    TREND_KEYWORDS.extend([
        f"{market} property",
        f"flat in {market}",
        f"{market} pune real estate",
    ])

# Search keywords for Quora/news scraping
SEARCH_QUERIES = [
    "pune property 2024", "pune real estate investment", "best area buy flat pune",
    "pune property price increase", "pune micro market trend",
] + [f"{m} pune property" for m in PUNE_MICRO_MARKETS[:8]]

# Intent signal keywords
INTENT_SIGNALS = {
    "strong_buy": ["want to buy", "looking to buy", "finalizing", "ready to invest", "booking open"],
    "researching": ["which is better", "suggest", "compare", "options in pune", "good area"],
    "price_sensitive": ["affordable", "budget", "under 50 lakh", "below 1 cr", "cheap"],
    "investor": ["roi", "rental yield", "appreciation", "investment", "returns"],
    "nri": ["nri", "dubai", "usa", "uk", "abroad", "overseas investment"],
    "negative": ["overpriced", "scam", "avoid", "bad builder", "delay", "fraud"],
}

SENTIMENT_KEYWORDS = {
    "positive": ["great", "excellent", "recommend", "good", "worth", "happy", "satisfied", "appreciate"],
    "negative": ["bad", "poor", "fraud", "delay", "cheat", "avoid", "worst", "terrible", "scam"],
    "neutral": ["okay", "average", "decent", "fine", "moderate"],
}
