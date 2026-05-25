"""
FocusGuard — Settings Window (PyQt6)
A premium dark-themed UI for configuring the distraction blocker.
"""

from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import (
    QColor, QFont, QIcon, QPainter, QBrush, QPen,
    QLinearGradient, QPixmap, QPainterPath,
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox, QSpinBox,
    QListWidget, QListWidgetItem, QFrame, QScrollArea, QSizePolicy,
    QDialog, QDialogButtonBox, QMessageBox, QGraphicsDropShadowEffect,
    QCheckBox, QTabWidget,
)

# ── Palette ─────────────────────────────────────────────────────────────────
BG        = "#0a0a14"
CARD_BG   = "#11112a"
CARD_BDR  = "#1e1e42"
ACCENT    = "#8b5cf6"
ACCENT2   = "#3b82f6"
GREEN     = "#10b981"
RED       = "#ef4444"
ORANGE    = "#f59e0b"
TEXT      = "#f1f5f9"
MUTED     = "#64748b"
INPUT_BG  = "#0d0d22"
HOVER     = "#1a1a38"

STYLESHEET = f"""
QMainWindow, QDialog {{
    background-color: {BG};
    color: {TEXT};
}}
QWidget {{
    background-color: transparent;
    color: {TEXT};
    font-family: "Segoe UI", sans-serif;
    font-size: 13px;
}}
QScrollArea {{
    border: none;
    background-color: {BG};
}}
QScrollBar:vertical {{
    background: {BG};
    width: 8px;
    border-radius: 4px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: #2d2d55;
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {ACCENT};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QLineEdit, QTextEdit, QSpinBox, QComboBox {{
    background-color: {INPUT_BG};
    color: {TEXT};
    border: 1.5px solid {CARD_BDR};
    border-radius: 10px;
    padding: 9px 12px;
    selection-background-color: {ACCENT};
}}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border-color: {ACCENT};
}}
QComboBox::drop-down {{
    border: none;
    width: 28px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {MUTED};
    margin-right: 8px;
}}
QComboBox QAbstractItemView {{
    background-color: {CARD_BG};
    color: {TEXT};
    border: 1px solid {CARD_BDR};
    border-radius: 8px;
    selection-background-color: {ACCENT};
    padding: 4px;
}}
QSpinBox::up-button, QSpinBox::down-button {{
    width: 0;
    height: 0;
}}
QListWidget {{
    background-color: {INPUT_BG};
    border: 1.5px solid {CARD_BDR};
    border-radius: 10px;
    padding: 6px;
    outline: 0;
}}
QListWidget::item {{
    border-radius: 8px;
}}
QListWidget::item:hover {{
    background-color: {HOVER};
}}
QListWidget::item:selected {{
    background-color: #1e1e45;
}}
QToolTip {{
    background-color: {CARD_BG};
    color: {TEXT};
    border: 1px solid {CARD_BDR};
    padding: 6px 10px;
    border-radius: 6px;
}}
QTabWidget::pane {{
    border: none;
    background: transparent;
}}
QTabBar::tab {{
    background: {CARD_BG};
    color: {MUTED};
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
    font-weight: 700;
}}
QTabBar::tab:selected {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {ACCENT}, stop:1 {CARD_BG});
    color: {TEXT};
}}
"""

VOICES = [
    ("en-US-AriaNeural",    "Aria — English US (Female, Natural)"),
    ("en-US-GuyNeural",     "Guy  — English US (Male, Casual)"),
    ("en-US-JennyNeural",   "Jenny — English US (Female, Friendly)"),
    ("en-US-DavisNeural",   "Davis — English US (Male, Professional)"),
    ("en-GB-SoniaNeural",   "Sonia — English UK (Female)"),
    ("en-GB-RyanNeural",    "Ryan — English UK (Male)"),
    ("en-AU-NatashaNeural", "Natasha — English AU (Female)"),
]


# ── Custom Widgets ────────────────────────────────────────────────────────────

class ToggleSwitch(QWidget):
    """Animated toggle switch widget."""
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(54, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._checked = True
        self._offset = 26.0   # thumb x-position (animated)

    @property
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, val: bool):
        self._checked = val
        self._offset = 26.0 if val else 2.0
        self.update()

    def setChecked(self, val: bool):
        self.checked = val

    def isChecked(self) -> bool:
        return self._checked

    def mousePressEvent(self, event):
        self._checked = not self._checked
        self._offset = 26.0 if self._checked else 2.0
        self.update()
        self.toggled.emit(self._checked)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Track
        track_color = QColor(ACCENT) if self._checked else QColor("#2d2d55")
        p.setBrush(QBrush(track_color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 4, 54, 20, 10, 10)

        # Thumb
        p.setBrush(QBrush(QColor("white")))
        p.drawEllipse(int(self._offset), 2, 24, 24)
        p.end()


class Card(QFrame):
    """Styled dark card with border."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FGCard")
        self.setStyleSheet(f"""
            QFrame#FGCard {{
                background-color: {CARD_BG};
                border: 1.5px solid {CARD_BDR};
                border-radius: 14px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)


class SectionLabel(QLabel):
    """Small uppercase section header."""
    def __init__(self, text, parent=None):
        super().__init__(text.upper(), parent)
        self.setStyleSheet(f"""
            color: {MUTED};
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 1.5px;
            padding-bottom: 2px;
        """)


class PrimaryButton(QPushButton):
    def __init__(self, text, icon_text="", parent=None):
        super().__init__(f"{icon_text}  {text}".strip() if icon_text else text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ACCENT}, stop:1 {ACCENT2});
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 22px;
                font-weight: 700;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7c3aed, stop:1 #2563eb);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6d28d9, stop:1 #1d4ed8);
            }}
            QPushButton:disabled {{
                background: #2d2d55;
                color: {MUTED};
            }}
        """)


class SecondaryButton(QPushButton):
    def __init__(self, text, icon_text="", parent=None):
        super().__init__(f"{icon_text}  {text}".strip() if icon_text else text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT};
                border: 1.5px solid {CARD_BDR};
                border-radius: 10px;
                padding: 10px 22px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {HOVER};
                border-color: {ACCENT};
                color: {ACCENT};
            }}
            QPushButton:pressed {{
                background-color: #1e1e45;
            }}
        """)


class DangerButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(28, 28)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {MUTED};
                border: none;
                border-radius: 6px;
                font-size: 15px;
                font-weight: bold;
                padding: 0;
            }}
            QPushButton:hover {{
                background-color: #3d1212;
                color: {RED};
            }}
        """)


class AppListItemWidget(QWidget):
    """Custom widget for list items containing the app info and a delete button."""
    def __init__(self, app_data, delete_cb, parent=None):
        super().__init__(parent)
        self.app_data = app_data
        
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 6, 6, 6)
        
        icon = "🌐" if app_data.get("type") == "browser" else "🖥️"
        kws = ", ".join(app_data.get("keywords", []))
        
        lbl = QLabel(f'<b>{icon}  {app_data["name"]}</b>  —  <span style="color:{MUTED};">{kws}</span>')
        lbl.setStyleSheet("background: transparent;")
        lay.addWidget(lbl)
        
        lay.addStretch()
        
        btn = DangerButton("✖")
        btn.clicked.connect(lambda: delete_cb(self))
        lay.addWidget(btn)


class AnalyticsChart(QWidget):
    def __init__(self, monitor, parent=None):
        super().__init__(parent)
        self.monitor = monitor
        self.setMinimumHeight(300)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update)
        self._timer.start(1000)

    def paintEvent(self, event):
        stats = self.monitor.analytics.get_today_stats()
        good = stats.get("good", {})
        bad = stats.get("bad", {})
        
        items = []
        for name, secs in good.items(): items.append(("good", name, secs))
        for name, secs in bad.items(): items.append(("bad", name, secs))
        items.sort(key=lambda x: x[2], reverse=True)
        
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if not items:
            p.setPen(QColor(MUTED))
            font = p.font()
            font.setPointSize(11)
            p.setFont(font)
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No tracking data yet for today.\nUse monitored apps to see stats.")
            return
            
        max_secs = max(items[0][2], 1)
        
        y = 20
        row_height = 40
        
        font_name = p.font()
        font_name.setPointSize(10)
        font_name.setBold(True)
        
        font_time = p.font()
        font_time.setPointSize(9)

        for cat, name, secs in items:
            mins = secs // 60
            display_time = f"{secs}s" if mins == 0 else (f"{mins}m" if mins < 60 else f"{mins//60}h {mins%60}m")
            
            p.setFont(font_name)
            p.setPen(QColor(TEXT))
            p.drawText(10, y + 25, name[:15])
            
            p.setFont(font_time)
            p.setPen(QColor(MUTED))
            p.drawText(120, y + 25, display_time)
            
            bar_width = max(10, int((secs / max_secs) * (self.width() - 200)))
            
            color = QColor(GREEN) if cat == "good" else QColor(RED)
            p.setBrush(QBrush(color))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(180, y + 10, bar_width, 20, 10, 10)
            
            y += row_height
            
        self.setMinimumHeight(y + 40)


# ── Add App Dialog ────────────────────────────────────────────────────────────

class AddAppDialog(QDialog):
    def __init__(self, category_name="App", parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Add {category_name}")
        self.setFixedWidth(420)
        self.setStyleSheet(STYLESHEET + f"""
            QDialog {{
                background-color: {CARD_BG};
                border: 1.5px solid {CARD_BDR};
                border-radius: 14px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        title = QLabel(f"Add {category_name}")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {TEXT};")
        layout.addWidget(title)

        # Name field
        layout.addWidget(SectionLabel("Display Name"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. YouTube")
        layout.addWidget(self.name_input)

        # Type selector
        layout.addWidget(SectionLabel("Detection Type"))
        self.type_combo = QComboBox()
        self.type_combo.addItem("🌐  Browser Tab (URL/title match)", "browser")
        self.type_combo.addItem("🖥️  Desktop App (process name match)", "process")
        layout.addWidget(self.type_combo)

        # Keywords
        layout.addWidget(SectionLabel("Keywords (comma separated)"))
        self.keywords_input = QLineEdit()
        self.keywords_input.setPlaceholderText("e.g. youtube.com, youtube")
        layout.addWidget(self.keywords_input)

        hint = QLabel("For browser tabs, use the domain name.\nFor desktop apps, use part of the .exe name.")
        hint.setStyleSheet(f"color: {MUTED}; font-size: 11px; line-height: 1.5;")
        layout.addWidget(hint)

        layout.addSpacing(8)

        # Buttons
        btn_row = QHBoxLayout()
        cancel_btn = SecondaryButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        add_btn = PrimaryButton("Add", "✚")
        add_btn.clicked.connect(self._validate_and_accept)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(add_btn)
        layout.addLayout(btn_row)

    def _validate_and_accept(self):
        if not self.name_input.text().strip():
            self.name_input.setFocus()
            self.name_input.setStyleSheet(
                self.name_input.styleSheet() + f"border-color: {RED};"
            )
            return
        if not self.keywords_input.text().strip():
            self.keywords_input.setFocus()
            return
        self.accept()

    def get_app(self) -> dict:
        keywords = [k.strip() for k in self.keywords_input.text().split(",") if k.strip()]
        return {
            "name":     self.name_input.text().strip(),
            "type":     self.type_combo.currentData(),
            "keywords": keywords,
        }


# ── Main Settings Window ──────────────────────────────────────────────────────

class SettingsWindow(QMainWindow):
    def __init__(self, config_getter, config_saver, tts_engine, monitor=None):
        super().__init__()
        self.config_getter = config_getter
        self.config_saver  = config_saver
        self.tts           = tts_engine
        self.monitor       = monitor
        self._config       = config_getter()

        self.setWindowTitle("FocusGuard")
        self.setMinimumWidth(560)
        self.setMaximumWidth(600)
        self.resize(580, 780)
        self.setStyleSheet(STYLESHEET)
        self.setWindowIcon(self._make_icon(True))

        tabs = QTabWidget()
        self.setCentralWidget(tabs)
        
        # ── Settings Tab ─────────────────────────────────────────────────────
        settings_scroll = QScrollArea()
        settings_scroll.setWidgetResizable(True)
        settings_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        container = QWidget()
        settings_scroll.setWidget(container)
        root = QVBoxLayout(container)
        root.setContentsMargins(20, 20, 20, 24)
        root.setSpacing(16)

        root.addWidget(self._build_header())
        root.addWidget(self._build_status_card())
        root.addWidget(self._build_live_detection_card())
        
        root.addWidget(self._build_app_list_card("bad_apps", "Bad Apps (Distractions)", "bad_phrases"))
        root.addWidget(self._build_app_list_card("good_apps", "Good Apps (Productivity)", "good_phrases"))
        
        root.addWidget(self._build_reminder_card())
        root.addWidget(self._build_voice_card())
        root.addWidget(self._build_action_buttons())
        root.addStretch()

        tabs.addTab(settings_scroll, "⚙️ Settings")
        
        # ── Analytics Tab ────────────────────────────────────────────────────
        analytics_scroll = QScrollArea()
        analytics_scroll.setWidgetResizable(True)
        analytics_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        a_container = QWidget()
        analytics_scroll.setWidget(a_container)
        a_root = QVBoxLayout(a_container)
        a_root.setContentsMargins(20, 20, 20, 24)
        a_root.setSpacing(16)
        
        a_root.addWidget(self._build_header())
        
        stats_card = Card()
        slay = QVBoxLayout(stats_card)
        slay.setContentsMargins(18, 14, 18, 14)
        slay.addWidget(SectionLabel("Today's Analytics"))
        
        self.chart = AnalyticsChart(self.monitor)
        slay.addWidget(self.chart)
        a_root.addWidget(stats_card)
        a_root.addStretch()
        
        tabs.addTab(analytics_scroll, "📊 Analytics")

        self._refresh_ui()

    # ── Slot called from monitor thread ──────────────────────────────────────

    def on_distraction_detected(self, category: str, app_name: str):
        color = RED if category == "bad" else GREEN
        text = f"🔴  Watching — {app_name} (Blocked)" if category == "bad" else f"🟢  Watching — {app_name} (Productive)"
        self._status_dot.setStyleSheet(f"background-color: {color}; border-radius: 6px;")
        self._status_text.setText(text)
        self._status_text.setStyleSheet(f"color: {color}; font-weight: 600; font-size: 13px;")

    def on_status_tick(self, proc_name: str, window_title: str, matched_app: str):
        display_title = window_title[:60] + "…" if len(window_title) > 60 else window_title
        display_proc  = proc_name[:30]  + "…" if len(proc_name)  > 30  else proc_name

        self._live_proc_label.setText(f"🖊️  <b>Process:</b> {display_proc}")
        self._live_title_label.setText(f"📰  <b>Tab/Window:</b> {display_title}")

        if matched_app:
            self._live_match_label.setText(f"🎯  <b>Matched:</b> {matched_app} — timer running")
            self._live_match_label.setStyleSheet(f"color: {ORANGE}; font-size: 12px;")
        else:
            self._live_match_label.setText("✅  <b>No monitored app in focus</b>")
            self._live_match_label.setStyleSheet(f"color: {MUTED}; font-size: 12px;")

    def on_distraction_cleared(self):
        if self._config.get("enabled", True):
            self._status_dot.setStyleSheet(f"background-color: {GREEN}; border-radius: 6px;")
            self._status_text.setText("✅  Active — No apps monitored right now")
            self._status_text.setStyleSheet(f"color: {GREEN}; font-weight: 600; font-size: 13px;")
            self._countdown_label.setText("") 

    def on_countdown_tick(self, seconds: int):
        mins = seconds // 60
        secs = seconds % 60
        self._countdown_label.setText(f"Next reminder in: {mins}:{secs:02d}")

    def on_reminder_triggered(self, category: str, app_name: str):
        self._status_text.setText(f"🔊  Speaking reminder — {app_name}")

    # ── UI builders ──────────────────────────────────────────────────────────

    def _build_header(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        row = QHBoxLayout(w)
        row.setContentsMargins(4, 0, 4, 0)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(self._make_icon(True).pixmap(42, 42))
        row.addWidget(icon_lbl)
        row.addSpacing(10)

        txt = QVBoxLayout()
        title = QLabel("FocusGuard")
        title.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {TEXT}; background: transparent;")
        sub = QLabel("Distraction blocker & focus tracker")
        sub.setStyleSheet(f"font-size: 12px; color: {MUTED}; background: transparent;")
        txt.addWidget(title)
        txt.addWidget(sub)
        txt.setSpacing(1)
        row.addLayout(txt)
        row.addStretch()

        return w

    def _build_status_card(self) -> Card:
        card = Card()
        lay = QHBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)

        left = QVBoxLayout()
        left.setSpacing(4)
        dot_row = QHBoxLayout()
        self._status_dot = QLabel()
        self._status_dot.setFixedSize(12, 12)
        dot_row.addWidget(self._status_dot)
        dot_row.addSpacing(6)
        status_lbl = QLabel("STATUS")
        status_lbl.setStyleSheet(f"color: {MUTED}; font-size: 10px; font-weight: 700; letter-spacing: 1.5px;")
        dot_row.addWidget(status_lbl)
        dot_row.addStretch()
        left.addLayout(dot_row)

        self._status_text = QLabel()
        self._status_text.setStyleSheet(f"font-weight: 600; font-size: 13px;")
        left.addWidget(self._status_text)

        self._countdown_label = QLabel("")
        self._countdown_label.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        left.addWidget(self._countdown_label)
        lay.addLayout(left, 1)

        toggle_col = QVBoxLayout()
        toggle_col.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._toggle = ToggleSwitch()
        self._toggle.toggled.connect(self._on_toggle)
        toggle_col.addWidget(self._toggle)
        lay.addLayout(toggle_col)

        return card

    def _build_live_detection_card(self) -> Card:
        card = Card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(6)

        hdr = QHBoxLayout()
        hdr.addWidget(SectionLabel("Live Detection Feed"))
        hdr.addStretch()
        live_dot = QLabel("🟢 LIVE")
        live_dot.setStyleSheet(f"color: {GREEN}; font-size: 10px; font-weight: 700; letter-spacing: 1px;")
        hdr.addWidget(live_dot)
        lay.addLayout(hdr)

        self._live_proc_label = QLabel("🖊️  <b>Process:</b> waiting...")
        self._live_proc_label.setStyleSheet(f"color: {TEXT}; font-size: 12px;")
        self._live_proc_label.setTextFormat(Qt.TextFormat.RichText)
        lay.addWidget(self._live_proc_label)

        self._live_title_label = QLabel("📰  <b>Tab/Window:</b> waiting...")
        self._live_title_label.setStyleSheet(f"color: {TEXT}; font-size: 12px;")
        self._live_title_label.setTextFormat(Qt.TextFormat.RichText)
        self._live_title_label.setWordWrap(True)
        lay.addWidget(self._live_title_label)

        self._live_match_label = QLabel("✅  <b>No monitored app in focus</b>")
        self._live_match_label.setStyleSheet(f"color: {MUTED}; font-size: 12px;")
        self._live_match_label.setTextFormat(Qt.TextFormat.RichText)
        lay.addWidget(self._live_match_label)

        return card

    def _build_app_list_card(self, config_key: str, title: str, phrases_key: str) -> Card:
        card = Card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(10)

        hdr = QHBoxLayout()
        hdr.addWidget(SectionLabel(title))
        hdr.addStretch()
        add_btn = SecondaryButton("+ Add")
        add_btn.setFixedHeight(30)
        add_btn.setStyleSheet(add_btn.styleSheet() + "padding: 4px 14px; font-size: 12px;")
        add_btn.clicked.connect(lambda: self._add_app(config_key))
        hdr.addWidget(add_btn)
        lay.addLayout(hdr)

        list_widget = QListWidget()
        list_widget.setMinimumHeight(120)
        list_widget.setMaximumHeight(200)
        setattr(self, f"_{config_key}_list", list_widget)
        lay.addWidget(list_widget)
        
        lay.addSpacing(6)
        lay.addWidget(SectionLabel(f"Phrases (One per line) - Picked Randomly"))
        
        phrase_edit = QTextEdit()
        phrase_edit.setMinimumHeight(70)
        setattr(self, f"_{phrases_key}_edit", phrase_edit)
        lay.addWidget(phrase_edit)

        return card

    def _build_reminder_card(self) -> Card:
        card = Card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(10)

        lay.addWidget(SectionLabel("Reminder Settings"))

        interval_row = QHBoxLayout()
        interval_lbl = QLabel("Speak reminder every")
        interval_lbl.setStyleSheet(f"color: {TEXT};")
        interval_row.addWidget(interval_lbl)

        self._interval_spin = QSpinBox()
        self._interval_spin.setRange(1, 120)
        self._interval_spin.setValue(2)
        self._interval_spin.setFixedWidth(64)
        self._interval_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        interval_row.addWidget(self._interval_spin)

        mins_lbl = QLabel("minutes")
        mins_lbl.setStyleSheet(f"color: {TEXT};")
        interval_row.addWidget(mins_lbl)
        interval_row.addStretch()
        lay.addLayout(interval_row)

        return card

    def _build_voice_card(self) -> Card:
        card = Card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(10)

        lay.addWidget(SectionLabel("TTS Voice"))

        self._voice_combo = QComboBox()
        for voice_id, voice_label in VOICES:
            self._voice_combo.addItem(voice_label, voice_id)
        lay.addWidget(self._voice_combo)
        return card

    def _build_action_buttons(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)

        test_btn = SecondaryButton("🔊  Test Voice")
        test_btn.clicked.connect(self._test_voice)
        row.addWidget(test_btn)

        row.addStretch()

        save_btn = PrimaryButton("Save Settings", "💾")
        save_btn.clicked.connect(self._save)
        row.addWidget(save_btn)

        return w

    # ── Logic ────────────────────────────────────────────────────────────────

    def _refresh_ui(self):
        cfg = self._config

        self._toggle.setChecked(cfg.get("enabled", True))
        self._update_status_display(cfg.get("enabled", True))

        self._bad_apps_list.clear()
        for app in cfg.get("bad_apps", []):
            self._add_app_row("bad_apps", app)
            
        self._good_apps_list.clear()
        for app in cfg.get("good_apps", []):
            self._add_app_row("good_apps", app)

        self._interval_spin.setValue(cfg.get("reminder_interval", 2))
        
        self._bad_phrases_edit.setPlainText("\n".join(cfg.get("bad_phrases", [])))
        self._good_phrases_edit.setPlainText("\n".join(cfg.get("good_phrases", [])))

        voice_id = cfg.get("tts_voice", "en-US-AriaNeural")
        for i, (vid, _) in enumerate(VOICES):
            if vid == voice_id:
                self._voice_combo.setCurrentIndex(i)
                break

    def _update_status_display(self, enabled: bool):
        if enabled:
            self.on_distraction_cleared()
        else:
            self._status_dot.setStyleSheet(f"background-color: {MUTED}; border-radius: 6px;")
            self._status_text.setText("⏸️  Paused — Protection disabled")
            self._status_text.setStyleSheet(f"color: {MUTED}; font-weight: 600; font-size: 13px;")
            self._countdown_label.setText("")

    def _on_toggle(self, checked: bool):
        self._config["enabled"] = checked
        self._update_status_display(checked)
        self.config_saver(self._config)

    def _remove_app(self, list_key, widget):
        list_widget = getattr(self, f"_{list_key}_list")
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            if list_widget.itemWidget(item) == widget:
                list_widget.takeItem(i)
                self._config[list_key].pop(i)
                break

    def _add_app_row(self, list_key: str, app: dict):
        list_widget = getattr(self, f"_{list_key}_list")
        
        item = QListWidgetItem(list_widget)
        item.setData(Qt.ItemDataRole.UserRole, app)
        
        widget = AppListItemWidget(app, lambda w: self._remove_app(list_key, w))
        item.setSizeHint(widget.sizeHint())
        
        list_widget.addItem(item)
        list_widget.setItemWidget(item, widget)

    def _add_app(self, list_key: str):
        cat_name = "Bad App" if list_key == "bad_apps" else "Good App"
        dlg = AddAppDialog(cat_name, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            app = dlg.get_app()
            if list_key not in self._config:
                self._config[list_key] = []
            self._config[list_key].append(app)
            self._add_app_row(list_key, app)

    def _test_voice(self):
        import random
        phrases = [p.strip() for p in self._bad_phrases_edit.toPlainText().split("\n") if p.strip()]
        if not phrases:
            phrases = ["This is a test of your FocusGuard reminder voice."]
        voice = self._voice_combo.currentData()
        self.tts.speak(random.choice(phrases), voice)

    def _save(self):
        def _get_list(key):
            lw = getattr(self, f"_{key}_list")
            apps = []
            for i in range(lw.count()):
                apps.append(lw.item(i).data(Qt.ItemDataRole.UserRole))
            return apps
            
        def _get_phrases(key):
            te = getattr(self, f"_{key}_edit")
            return [p.strip() for p in te.toPlainText().split("\n") if p.strip()]

        self._config.update({
            "bad_apps": _get_list("bad_apps"),
            "good_apps": _get_list("good_apps"),
            "bad_phrases": _get_phrases("bad_phrases"),
            "good_phrases": _get_phrases("good_phrases"),
            "reminder_interval": self._interval_spin.value(),
            "tts_voice": self._voice_combo.currentData(),
        })

        if self.config_saver(self._config):
            QMessageBox.information(self, "Saved", "Settings saved successfully!\nPhrases will take effect immediately.")
            # Trigger pre-cache of all new phrases
            all_phrases = self._config["bad_phrases"] + self._config["good_phrases"]
            self.tts.prepare_many(all_phrases, self._config["tts_voice"])

    def _make_icon(self, active: bool) -> QIcon:
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

