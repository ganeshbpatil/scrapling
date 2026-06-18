"""
Generate realistic sample leads for dashboard testing.
Run: python -m pune_leads.seeder
"""
import random, json, os
from datetime import datetime, timedelta
from pune_leads.config import PUNE_MICRO_MARKETS, PROPERTY_CONFIGS, LEAD_SOURCES
from pune_leads.storage.json_storage import JSONStorage
from pune_leads.storage.csv_storage import CSVStorage

INTENTS = ["Ready to Buy", "Researching", "Investor", "Looking for Rental",
           "Looking for Commercial", "Luxury Buyer", "NRI Buyer"]
SOURCES = list(LEAD_SOURCES.values()) + ["Google Search", "Web"]
NAMES = ["Rahul Sharma", "Priya Mehta", "Amit Patil", "Sneha Kulkarni",
         "Vikas Joshi", "Neha Desai", "Sanjay Gupta", "Pooja Iyer",
         "Rohan Verma", "Kavita Nair", "Arun Singh", "Deepa Rao"]
BUDGETS = ["45 Lakh", "65 Lakh", "75 Lakh", "85 Lakh", "1.2 Cr",
           "1.5 Cr", "2.0 Cr", "3.0 Cr", "50 Lakh", "90 Lakh"]

def generate(n: int = 50) -> list:
    leads = []
    for i in range(n):
        date = datetime.now() - timedelta(days=random.randint(0, 30))
        phone_suffix = random.randint(6000000000, 9999999999)
        leads.append({
            "name": random.choice(NAMES),
            "phone": f"+91{phone_suffix}",
            "email": f"lead{i+1}@example.com",
            "configuration": random.choice(PROPERTY_CONFIGS),
            "location_interest": random.choice(PUNE_MICRO_MARKETS),
            "budget": random.choice(BUDGETS),
            "lead_source": random.choice(SOURCES),
            "source_url": "https://example.com/sample",
            "lead_date": date.strftime("%Y-%m-%d"),
            "inquiry_text": "Interested in buying property in Pune.",
            "confidence_score": random.choice([50, 60, 70, 80, 90, 100]),
            "intent": random.choice(INTENTS),
            "validation_errors": [],
        })
    return leads

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    leads = generate(50)
    j = JSONStorage("output/leads.json")
    c = CSVStorage("output/leads.csv")
    for lead in leads:
        j.save(lead)
        c.save(lead)
    c.close()
    print(f"✓ Generated {len(leads)} sample leads → output/leads.json + leads.csv")
