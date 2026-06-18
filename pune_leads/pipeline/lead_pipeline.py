from pune_leads.storage.json_storage import JSONStorage
from pune_leads.storage.csv_storage import CSVStorage

class LeadPipeline:
    def __init__(self, output_dir: str = "output", use_postgres: bool = False, use_mongo: bool = False):
        self.json_store = JSONStorage(f"{output_dir}/leads.json")
        self.csv_store = CSVStorage(f"{output_dir}/leads.csv")
        self._seen: set = set()
        self._stats = {"total": 0, "by_config": {}, "by_location": {}, "by_source": {}, "by_intent": {}}
        self.pg_store = None
        self.mongo_store = None
        if use_postgres:
            try:
                from pune_leads.storage.postgres_storage import PostgresStorage
                self.pg_store = PostgresStorage()
            except Exception as e:
                print(f"Postgres unavailable: {e}")
        if use_mongo:
            try:
                from pune_leads.storage.mongo_storage import MongoStorage
                self.mongo_store = MongoStorage()
            except Exception as e:
                print(f"MongoDB unavailable: {e}")

    def _key(self, lead: dict) -> str:
        return f"{lead.get('email', '')}__{lead.get('phone', '')}"

    def process(self, lead: dict):
        key = self._key(lead)
        if key == "__" or key in self._seen:
            return None
        self._seen.add(key)
        self.json_store.save(lead)
        self.csv_store.save(lead)
        if self.pg_store:
            self.pg_store.save(lead)
        if self.mongo_store:
            self.mongo_store.save(lead)
        self._stats["total"] += 1
        for stat_key, field in [("by_config", "configuration"), ("by_location", "location_interest"),
                                  ("by_source", "lead_source"), ("by_intent", "intent")]:
            val = lead.get(field, "Unknown") or "Unknown"
            self._stats[stat_key][val] = self._stats[stat_key].get(val, 0) + 1
        return lead

    def get_stats(self) -> dict:
        return self._stats
