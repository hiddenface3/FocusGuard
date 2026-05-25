"""
FocusGuard — main.py
Entry point. Creates the system tray icon and wires up all components.

Run with:  python main.py
"""

import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QLinearGradient, QBrush, QColor, QPen, QFont
from PyQt6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QMessageBox
)

from config import load_config, save_config
from tts_engine import TTSEngine
from browser_server import BrowserTabServer
from monitor import WindowMonitor
from settings_window import SettingsWindow, ACCENT, ACCENT2, MUTED


def make_tray_icon(active: bool) -> QIcon:
    """Build a simple gradient 'F' icon for the system tray."""
    px = QPixmap(64, 64)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    g = QLinearGradient(0, 0, 64, 64)
    if active:
        g.setColorAt(0, QColor(ACCENT))
        g.setColorAt(1, QColor(ACCENT2))
    else:
        g.setColorAt(0, QColor("#3a3a6a"))
        g.setColorAt(1, QColor("#2d2d55"))

    p.setBrush(QBrush(g))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(2, 2, 60, 60)

    p.setPen(QPen(QColor("white")))
    font = QFont("Segoe UI", 26, QFont.Weight.Bold)
    p.setFont(font)
    p.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, "F")
    p.end()
    return QIcon(px)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("FocusGuard")
    app.setApplicationDisplayName("FocusGuard")
    # Keep the app alive even when all windows are closed (tray-only mode)
    app.setQuitOnLastWindowClosed(False)

    # ── Core components ──────────────────────────────────────────────────────
    tts = TTSEngine()
    config_store = {"data": load_config()}

    def get_config():
        return config_store["data"]

    def set_config(new_cfg):
        config_store["data"] = new_cfg
        return save_config(new_cfg)

    # ── Browser Extension Server ─────────────────────────────────────────────
    browser_server = BrowserTabServer()
    browser_server.start()

    # ── Monitor thread ───────────────────────────────────────────────────────
    monitor = WindowMonitor(get_config, tts, browser_server)

    # ── Settings window ──────────────────────────────────────────────────────
    win = SettingsWindow(
        config_getter=get_config,
        config_saver=set_config,
        tts_engine=tts,
        monitor=monitor
    )

    # Wire monitor signals → window slots
    monitor.distraction_detected.connect(win.on_distraction_detected)
    monitor.distraction_cleared.connect(win.on_distraction_cleared)
    monitor.reminder_triggered.connect(win.on_reminder_triggered)
    monitor.countdown_tick.connect(win.on_countdown_tick)
    monitor.status_tick.connect(win.on_status_tick)   # Live detection feed

    # ── System tray ──────────────────────────────────────────────────────────
    tray = QSystemTrayIcon()
    tray.setIcon(make_tray_icon(True))
    tray.setToolTip("FocusGuard — Active")

    menu = QMenu()
    menu.setStyleSheet("""
        QMenu {
            background-color: #11112a;
            color: #f1f5f9;
            border: 1px solid #1e1e42;
            border-radius: 10px;
            padding: 6px;
            font-family: "Segoe UI";
            font-size: 13px;
        }
        QMenu::item { padding: 8px 20px; border-radius: 6px; }
        QMenu::item:selected { background-color: #8b5cf6; }
        QMenu::separator { height: 1px; background: #1e1e42; margin: 4px 8px; }
    """)

    open_action = menu.addAction("⚙️  Open Settings")
    menu.addSeparator()

    toggle_action = menu.addAction("⏸️  Pause Protection")
    menu.addSeparator()

    quit_action = menu.addAction("✖  Quit FocusGuard")

    tray.setContextMenu(menu)
    tray.show()

    # Tray icon single-click → open settings
    def on_tray_activated(reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            _open_settings()

    def _open_settings():
        win.show()
        win.raise_()
        win.activateWindow()

    def _toggle_protection():
        cfg = get_config()
        new_state = not cfg.get("enabled", True)
        cfg["enabled"] = new_state
        set_config(cfg)
        config_store["data"] = cfg

        tray.setIcon(make_tray_icon(new_state))
        if new_state:
            toggle_action.setText("⏸️  Pause Protection")
            tray.setToolTip("FocusGuard — Active")
            tray.showMessage("FocusGuard", "✅ Protection resumed!", QSystemTrayIcon.MessageIcon.Information, 2000)
        else:
            toggle_action.setText("▶️  Resume Protection")
            tray.setToolTip("FocusGuard — Paused")
            tray.showMessage("FocusGuard", "⏸️ Protection paused.", QSystemTrayIcon.MessageIcon.Information, 2000)

        # Update main window toggle if visible
        win._config = cfg
        win._toggle.setChecked(new_state)
        win._update_status_display(new_state)

    def _quit():
        if hasattr(monitor, 'analytics'):
            monitor.analytics.flush()
        monitor.stop()
        browser_server.stop()
        tts.cleanup()
        app.quit()

    open_action.triggered.connect(_open_settings)
    toggle_action.triggered.connect(_toggle_protection)
    quit_action.triggered.connect(_quit)
    tray.activated.connect(on_tray_activated)

    # Update tray tooltip from monitor signals
    def _on_distraction(category, app_name):
        tray.setToolTip(f"FocusGuard — ⚠️ Watching: {app_name} ({category})")

    def _on_cleared():
        cfg = get_config()
        if cfg.get("enabled", True):
            tray.setToolTip("FocusGuard — ✅ Active")

    monitor.distraction_detected.connect(_on_distraction)
    monitor.distraction_cleared.connect(_on_cleared)

    # Also show balloon on reminder
    def _on_reminder(category, app_name):
        import random
        cfg = get_config()
        phrases = cfg.get("bad_phrases", []) if category == "bad" else cfg.get("good_phrases", [])
        if not phrases: phrases = ["Reminder!"]
        phrase = random.choice(phrases)
        
        msg = f"You've been on {app_name} too long!\n\"{phrase}\"" if category == "bad" else f"You are doing great on {app_name}!\n\"{phrase}\""
        
        tray.showMessage(
            "FocusGuard Reminder 🔔" if category == "bad" else "FocusGuard 🌟",
            msg,
            QSystemTrayIcon.MessageIcon.Warning if category == "bad" else QSystemTrayIcon.MessageIcon.Information,
            4000,
        )

    monitor.reminder_triggered.connect(_on_reminder)

    # ── TTS Engine ───────────────────────────────────────────────────────────
    current_config = get_config()
    
    # Fire off a background task to pre-generate all possible phrases
    voice = current_config.get("tts_voice", "en-US-AriaNeural")
    all_phrases = current_config.get("bad_phrases", []) + current_config.get("good_phrases", [])
    tts.prepare_many(all_phrases, voice)

    # ── Start monitoring ──────────────────────────────────────────────────────
    monitor.start()

    # Show settings on first launch if no config file exists
    import os
    from config import CONFIG_FILE
    if not os.path.exists(CONFIG_FILE):
        win.show()
    else:
        tray.showMessage(
            "FocusGuard is running 🛡️",
            "FocusGuard is protecting you in the background.\nClick the tray icon to open settings.",
            QSystemTrayIcon.MessageIcon.Information,
            3000,
        )

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
