import json, os
from datetime import datetime, timezone

class SignalStore:
    def __init__(self, output_dir: str = "output/intelligence"):
        os.makedirs(output_dir, exist_ok=True)
        self.dir = output_dir
        self.signals_file = f"{output_dir}/signals.json"
        self.report_file  = f"{output_dir}/daily_report.json"
        self._signals: list = []
        if os.path.exists(self.signals_file):
            with open(self.signals_file) as f:
                self._signals = json.load(f)

    def save_signals(self, signals: list):
        # Deduplicate by URL+title
        existing_keys = {(s.get("url",""), s.get("title","")) for s in self._signals}
        new = [s for s in signals if (s.get("url",""), s.get("title","")) not in existing_keys]
        self._signals.extend(new)
        with open(self.signals_file, "w") as f:
            json.dump(self._signals, f, indent=2, default=str)
        return len(new)

    def save_report(self, report: dict):
        # Keep last 30 daily reports
        history = []
        if os.path.exists(self.report_file):
            with open(self.report_file) as f:
                data = json.load(f)
                history = data if isinstance(data, list) else [data]
        history.append(report)
        history = history[-30:]
        with open(self.report_file, "w") as f:
            json.dump(history, f, indent=2, default=str)

    def latest_report(self) -> dict:
        if not os.path.exists(self.report_file):
            return {}
        with open(self.report_file) as f:
            data = json.load(f)
        return data[-1] if isinstance(data, list) and data else (data or {})

    def all_signals(self) -> list:
        return self._signals

    def signals_today(self) -> list:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return [s for s in self._signals if s.get("collected_at", "").startswith(today)]
