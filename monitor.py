"""
WindowMonitor — QThread that polls the foreground window every second.
Detects distraction apps and fires the TTS reminder on the configured interval.
"""

import time
import random

import psutil
import win32gui
import win32process
from PyQt6.QtCore import QThread, pyqtSignal

from analytics import AnalyticsManager

# Browser process names to watch (lowercase)
BROWSER_PROCESSES = {
    "chrome.exe", "firefox.exe", "msedge.exe",
    "opera.exe", "brave.exe", "vivaldi.exe",
}


class WindowMonitor(QThread):
    # Emitted when a distraction app becomes foreground
    distraction_detected = pyqtSignal(str, str)   # category, app name
    # Emitted when focus returns to non-distraction
    distraction_cleared = pyqtSignal()
    # Emitted each time a reminder fires
    reminder_triggered = pyqtSignal(str, str)     # category, app name
    # Emitted every second with time remaining (seconds) until next reminder
    countdown_tick = pyqtSignal(int)
    # Emitted every second with live window info: (proc_name, window_title, matched_app_or_empty)
    status_tick = pyqtSignal(str, str, str)

    def __init__(self, config_getter, tts_engine, browser_server=None):
        super().__init__()
        self.config_getter  = config_getter
        self.tts            = tts_engine
        self.browser_server = browser_server   # Optional BrowserTabServer
        self.analytics      = AnalyticsManager()
        self._running       = False
        self._current_distraction: str | None = None
        self._current_category: str | None = None
        self._last_reminder_time: float | None = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_foreground_info(self):
        """Return (proc_name_lower, window_title_lower) of the foreground window."""
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return None, None
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid <= 0:
                return None, None
            proc = psutil.Process(pid)
            return proc.name().lower(), win32gui.GetWindowText(hwnd).lower()
        except Exception:
            return None, None

    def _match_app(self, proc_name, window_title, apps_list, browser_url, browser_title) -> str | None:
        if not proc_name: return None
        for app in apps_list:
            app_type = app.get("type", "browser")
            keywords = [k.lower() for k in app.get("keywords", [])]
            if app_type == "browser":
                if proc_name in BROWSER_PROCESSES:
                    check = (browser_url.lower() + " " + browser_title.lower()) if browser_url else window_title
                    if any(kw in check for kw in keywords):
                        return app["name"]
            elif app_type == "process":
                if any(kw in proc_name for kw in keywords):
                    return app["name"]
        return None

    def _match_distraction(self, proc_name, window_title, bad_apps, good_apps,
                            browser_url: str = "", browser_title: str = "") -> tuple[str | None, str | None]:
        """Return (category, app_name) or (None, None). category is 'bad' or 'good'."""
        bad_match = self._match_app(proc_name, window_title, bad_apps, browser_url, browser_title)
        if bad_match:
            return "bad", bad_match
        
        good_match = self._match_app(proc_name, window_title, good_apps, browser_url, browser_title)
        if good_match:
            return "good", good_match

        return None, None

    # ------------------------------------------------------------------
    # QThread entry point
    # ------------------------------------------------------------------

    def run(self):
        self._running = True

        while self._running:
            cfg = self.config_getter()

            if not cfg.get("enabled", True):
                if self._current_distraction is not None:
                    self._current_distraction = None
                    self._current_category = None
                    self._last_reminder_time = None
                    self.distraction_cleared.emit()
                time.sleep(1)
                continue

            proc_name, window_title = self._get_foreground_info()
            bad_apps      = cfg.get("bad_apps", [])
            good_apps     = cfg.get("good_apps", [])
            interval_secs = cfg.get("reminder_interval", 2) * 60
            bad_phrases   = cfg.get("bad_phrases", ["Please go back to your work!"])
            good_phrases  = cfg.get("good_phrases", ["Great job! Keep up the good work."])
            voice         = cfg.get("tts_voice", "en-US-AriaNeural")

            browser_url   = ""
            browser_title = ""
            if self.browser_server and proc_name in BROWSER_PROCESSES:
                browser_url   = self.browser_server.current_url
                browser_title = self.browser_server.current_title

            category, distraction = self._match_distraction(
                proc_name, window_title, bad_apps, good_apps, browser_url, browser_title
            )
            now = time.time()

            if distraction and category:
                self.analytics.log_time(category, distraction, 1)

            if self.browser_server:
                self.browser_server.set_matched_app(distraction or "")

            self.status_tick.emit(
                proc_name or "",
                window_title or "",
                distraction or ""
            )

            if distraction:
                if self._current_distraction != distraction:
                    self._current_distraction = distraction
                    self._current_category = category
                    self._last_reminder_time = now
                    self.distraction_detected.emit(category, distraction)

                elapsed = now - self._last_reminder_time
                remaining = max(0, int(interval_secs - elapsed))
                self.countdown_tick.emit(remaining)

                if elapsed >= interval_secs:
                    self._last_reminder_time = now
                    self.reminder_triggered.emit(category, distraction)
                    
                    phrases = bad_phrases if category == "bad" else good_phrases
                    if not phrases:
                        phrases = ["Reminder!"]
                    phrase = random.choice(phrases)
                    self.tts.speak(phrase, voice)
            else:
                if self._current_distraction is not None:
                    self._current_distraction = None
                    self._current_category = None
                    self._last_reminder_time = None
                    self.distraction_cleared.emit()

            time.sleep(1)

    def stop(self):
        self._running = False
        self.wait(3000)
