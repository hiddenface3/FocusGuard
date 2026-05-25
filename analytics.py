import json
import os
import time
from collections import defaultdict
from datetime import datetime

from config import BASE_DIR

ANALYTICS_FILE = os.path.join(BASE_DIR, "analytics.json")


class AnalyticsManager:
    """Handles tracking and persisting app usage time."""
    def __init__(self):
        self._data = self._load()
        self._last_save = time.time()
        self._save_interval = 60  # seconds

    def _load(self) -> dict:
        if os.path.exists(ANALYTICS_FILE):
            try:
                with open(ANALYTICS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[Analytics] Load error: {e}")
        return {}

    def _save(self):
        try:
            with open(ANALYTICS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
            self._last_save = time.time()
        except Exception as e:
            print(f"[Analytics] Save error: {e}")

    def log_time(self, category: str, app_name: str, seconds: int = 1):
        """Log active time for an app in a specific category (good/bad)."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        if today not in self._data:
            self._data[today] = {"good": {}, "bad": {}}
            
        if category not in self._data[today]:
            self._data[today][category] = {}
            
        if app_name not in self._data[today][category]:
            self._data[today][category][app_name] = 0
            
        self._data[today][category][app_name] += seconds

        if time.time() - self._last_save > self._save_interval:
            self._save()

    def get_today_stats(self) -> dict:
        """Return analytics for today."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self._data.get(today, {"good": {}, "bad": {}})

    def flush(self):
        """Force save to disk."""
        self._save()
