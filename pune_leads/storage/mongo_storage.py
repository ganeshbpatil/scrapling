import os
try:
    from pymongo import MongoClient
    HAS_PYMONGO = True
except ImportError:
    HAS_PYMONGO = False

class MongoStorage:
    def __init__(self, uri: str = None, db: str = None):
        if not HAS_PYMONGO:
            raise RuntimeError("pymongo not installed")
        uri = uri or os.getenv("MONGO_URI", "mongodb://localhost:27017")
        db = db or os.getenv("MONGO_DB", "pune_leads")
        self.collection = MongoClient(uri)[db]["leads"]

    def save(self, lead: dict):
        key = {}
        if lead.get("email"):
            key["email"] = lead["email"]
        if lead.get("phone"):
            key["phone"] = lead["phone"]
        if key:
            self.collection.update_one(key, {"$setOnInsert": lead}, upsert=True)
        else:
            self.collection.insert_one(lead)
