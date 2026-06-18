import json, os

class JSONStorage:
    def __init__(self, filepath: str = "output/leads.json"):
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        self.filepath = filepath
        self._leads: list = []
        if os.path.exists(filepath):
            with open(filepath) as f:
                self._leads = json.load(f)

    def save(self, lead: dict):
        self._leads.append(lead)
        with open(self.filepath, "w") as f:
            json.dump(self._leads, f, indent=2, default=str)

    def all(self) -> list:
        return self._leads
