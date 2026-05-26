import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

DEFAULT_CONFIG = {
    "bad_apps": [
        {"name": "YouTube",    "type": "browser", "keywords": ["youtube.com", "youtube"]},
        {"name": "Instagram",  "type": "browser", "keywords": ["instagram.com", "instagram"]},
        {"name": "Facebook",   "type": "browser", "keywords": ["facebook.com", "facebook"]},
        {"name": "Twitter / X","type": "browser", "keywords": ["twitter.com", "x.com"]},
        {"name": "TikTok",     "type": "browser", "keywords": ["tiktok.com", "tiktok"]},
        {"name": "Reddit",     "type": "browser", "keywords": ["reddit.com", "reddit"]},
        {"name": "Netflix",    "type": "browser", "keywords": ["netflix.com", "netflix"]},
        {"name": "Twitch",     "type": "browser", "keywords": ["twitch.tv", "twitch"]},
    ],
    "good_apps": [
        {"name": "VS Code",    "type": "process", "keywords": ["code.exe"]},
        {"name": "Notion",     "type": "browser", "keywords": ["notion.so"]},
        {"name": "Docs",       "type": "browser", "keywords": ["docs.google.com"]},
    ],
    "bad_phrases": [
        "Hey! Stop scrolling and get back to work!",
        "You are wasting your precious time. Close this app.",
        "Focus! Don't let distractions win."
    ],
    "good_phrases": [
        "Great job! Keep up the good work.",
        "You are being very productive. Well done!",
        "Excellent focus."
    ],
    "reminder_interval": 2,        # minutes
    "tts_voice": "en-US-AriaNeural",
    "enabled": True,
}


def load_config() -> dict:
    """Load config from disk, merging with defaults for missing keys."""
    merged = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Migration logic from v1 -> v2 schema
            if "blocked_apps" in data and "bad_apps" not in data:
                data["bad_apps"] = data.pop("blocked_apps")
            
            if "reminder_phrase" in data and "bad_phrases" not in data:
                phrase = data.pop("reminder_phrase")
                if phrase:
                    data["bad_phrases"] = [phrase]

            merged.update(data)
        except Exception as e:
            print(f"[Config] Load error: {e}")
    return merged


def save_config(config: dict) -> bool:
    """Persist config to disk. Returns True on success."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[Config] Save error: {e}")
        return False
