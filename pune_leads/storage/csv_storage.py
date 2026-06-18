import csv, os

FIELDS = [
    "name", "phone", "email", "configuration", "location_interest",
    "budget", "lead_source", "source_url", "lead_date", "intent",
    "confidence_score", "inquiry_text",
]

class CSVStorage:
    def __init__(self, filepath: str = "output/leads.csv"):
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        exists = os.path.exists(filepath)
        self._file = open(filepath, "a", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._file, fieldnames=FIELDS, extrasaction="ignore")
        if not exists:
            self._writer.writeheader()

    def save(self, lead: dict):
        self._writer.writerow(lead)
        self._file.flush()

    def close(self):
        self._file.close()
