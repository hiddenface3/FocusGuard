"""
FocusGuard — Settings Window (PyQt6)
A premium dark-themed UI for configuring the distraction blocker.
"""

from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize, QTimer, pyqtProperty
from PyQt6.QtGui import (
    QColor, QFont, QIcon, QPainter, QBrush, QPen,
    QLinearGradient, QPixmap, QPainterPath,
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox, QSpinBox,
    QListWidget, QListWidgetItem, QFrame, QScrollArea, QSizePolicy,
    QDialog, QDialogButtonBox, QMessageBox, QGraphicsDropShadowEffect,
    QCheckBox, QTabWidget, QStackedWidget,
)

# ── Palette ─────────────────────────────────────────────────────────────────
BG        = "#0b1326"
CARD_BG   = "#131b2e"
CARD_BDR  = "rgba(255, 255, 255, 0.1)"
ACCENT    = "#d0bcff"
ACCENT2   = "#adc6ff"
GREEN     = "#4edea3"
RED       = "#ffb4ab"
ORANGE    = "#f59e0b"
TEXT      = "#dbe2fd"
MUTED     = "#cac4d0"
INPUT_BG  = "rgba(11, 19, 38, 0.5)"
HOVER     = "#171f33"

STYLESHEET = f"""
QMainWindow, QDialog {{
    background-color: {BG};
    color: {TEXT};
}}
QWidget {{
    background-color: transparent;
    color: {TEXT};
    font-family: "Inter", "Segoe UI", sans-serif;
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
    ("gemini-Puck",         "Gemini — Puck (Male, Natural)"),
    ("gemini-Charon",       "Gemini — Charon (Male, Deep)"),
    ("gemini-Kore",         "Gemini — Kore (Female, Natural)"),
    ("gemini-Fenrir",       "Gemini — Fenrir (Male, Natural)"),
    ("gemini-Aoede",        "Gemini — Aoede (Female, Expressive)"),
    ("kokoro-af_heart",     "Kokoro — Heart (Female, American)"),
    ("kokoro-af_sarah",     "Kokoro — Sarah (Female, American)"),
    ("kokoro-af_bella",     "Kokoro — Bella (Female, American)"),
    ("kokoro-af_nicole",    "Kokoro — Nicole (Female, American)"),
    ("kokoro-af_sky",       "Kokoro — Sky (Female, American)"),
    ("kokoro-am_adam",      "Kokoro — Adam (Male, American)"),
    ("kokoro-am_michael",   "Kokoro — Michael (Male, American)"),
    ("kokoro-bf_emma",      "Kokoro — Emma (Female, British)"),
    ("kokoro-bf_isabella",  "Kokoro — Isabella (Female, British)"),
    ("kokoro-bm_george",    "Kokoro — George (Male, British)"),
    ("kokoro-bm_lewis",     "Kokoro — Lewis (Male, British)"),
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
        self._anim = None

    @pyqtProperty(float)
    def offset(self) -> float:
        return self._offset

    @offset.setter
    def offset(self, val: float):
        self._offset = val
        self.update()

    @property
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, val: bool):
        if self._checked == val:
            return
        self._checked = val
        if self.isVisible():
            self._animate(val)
        else:
            self._offset = 26.0 if val else 2.0
            self.update()

    def setChecked(self, val: bool):
        self.checked = val

    def isChecked(self) -> bool:
        return self._checked

    def mousePressEvent(self, event):
        self._checked = not self._checked
        self._animate(self._checked)
        self.toggled.emit(self._checked)

    def _animate(self, val: bool):
        target = 26.0 if val else 2.0
        self._anim = QPropertyAnimation(self, b"offset")
        self._anim.setDuration(180)
        self._anim.setStartValue(self._offset)
        self._anim.setEndValue(target)
        self._anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self._anim.start()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Track
        if self._checked:
            track_color = QColor(ACCENT)
            p.setBrush(QBrush(track_color))
        else:
            p.setBrush(QBrush(QColor("#2d3449"))) # surface-variant
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
                border: 1px solid {CARD_BDR};
                border-top: 1px solid rgba(255, 255, 255, 0.2);
                border-left: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 16px;
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
                    stop:0 #665590, stop:1 #2c4677);
                color: {TEXT};
                border: 1px solid rgba(208, 188, 255, 0.3);
                border-radius: 8px;
                padding: 10px 22px;
                font-family: "Inter", sans-serif;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7f6ba8, stop:1 #3e5a8f);
                border: 1px solid rgba(208, 188, 255, 0.6);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #504273, stop:1 #1e3157);
            }}
            QPushButton:disabled {{
                background: #222a3e;
                color: {MUTED};
                border: none;
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
                border: 1px dashed #49454f;
                border-radius: 8px;
                padding: 10px 22px;
                font-family: "Inter", sans-serif;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {HOVER};
                border-color: {ACCENT};
                color: {ACCENT};
            }}
            QPushButton:pressed {{
                background-color: #222a3e;
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
        from datetime import datetime
        self.selected_date = datetime.now().strftime("%Y-%m-%d")
        self.setMinimumHeight(400)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update)
        self._timer.start(1000)

    def set_selected_date(self, date_str: str):
        self.selected_date = date_str
        self.update()

    def paintEvent(self, event):
        from datetime import datetime
        stats = self.monitor.analytics.get_stats_for_date(self.selected_date)
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
            msg = "No tracking data yet for today." if self.selected_date == datetime.now().strftime("%Y-%m-%d") else f"No tracking data for {self.selected_date}."
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, msg)
            return
            
        max_secs = max(items[0][2], 1)
        total_good = sum(v for k,v in good.items())
        total_bad = sum(v for k,v in bad.items())
        
        # Header Row
        p.setPen(QColor(MUTED))
        f_small = p.font()
        f_small.setPointSize(9)
        f_small.setBold(True)
        f_small.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.5)
        p.setFont(f_small)
        
        p.drawText(self.width() - 250, 15, "PRODUCTIVE")
        p.drawText(self.width() - 100, 15, "DISTRACTION")
        
        f_large = p.font()
        f_large.setPointSize(14)
        f_large.setBold(True)
        f_large.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 100)
        p.setFont(f_large)
        
        p.setPen(QColor(TEXT))
        p.drawText(self.width() - 250, 40, f"{total_good//3600}h {(total_good%3600)//60}m")
        p.setPen(QColor(RED))
        p.drawText(self.width() - 100, 40, f"{total_bad//3600}h {(total_bad%3600)//60}m")
        
        # Separator line
        p.setPen(QPen(QColor(CARD_BDR), 1))
        p.drawLine(0, 60, self.width(), 60)
        
        y = 80
        row_height = 60
        
        font_name = p.font()
        font_name.setPointSize(11)
        font_name.setBold(True)
        
        font_time = p.font()
        font_time.setPointSize(10)

        for i, (cat, name, secs) in enumerate(items):
            mins = secs // 60
            display_time = f"{secs}s" if mins == 0 else (f"{mins}m" if mins < 60 else f"{mins//60}h {mins%60}m")
            
            icon = "🖥️" if cat == "good" else "🚫"
            
            p.setFont(font_name)
            p.setPen(QColor(TEXT))
            p.drawText(10, y + 25, f"{icon}   {name}")
            
            color_hex = GREEN if cat == "good" else RED
            color = QColor(color_hex)
            max_bar_width = max(50, self.width() - 180 - 120)
            bar_width = int((secs / max_secs) * max_bar_width)
            if secs > 0 and bar_width < 5:
                bar_width = 5
            
            p.setBrush(QBrush(color))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(180, y + 10, bar_width, 20, 10, 10)
            
            p.setFont(font_time)
            p.setPen(QColor(MUTED))
            p.drawText(180 + bar_width + 12, y + 25, display_time)
            
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
        self.setMinimumWidth(1100)
        self.resize(1200, 800)
        self.setStyleSheet(STYLESHEET)
        self.setWindowIcon(self._make_icon(True))

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top Nav Bar
        top_nav = QWidget()
        top_nav.setFixedHeight(70)
        top_nav.setStyleSheet(f"background-color: {BG}; border-bottom: 1px solid {CARD_BDR};")
        nav_lay = QHBoxLayout(top_nav)
        nav_lay.setContentsMargins(24, 0, 24, 0)
        
        # Logo
        logo_lbl = QLabel()
        logo_lbl.setPixmap(self._make_icon(True).pixmap(32, 32))
        title = QLabel("focus guard")
        title.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {GREEN}; font-family: 'Inter';")
        nav_lay.addWidget(logo_lbl)
        nav_lay.addSpacing(10)
        nav_lay.addWidget(title)
        
        nav_lay.addStretch()
        
        # Links
        links = ["Dashboard"]
        self.nav_btns = {}
        for link in links:
            btn = QPushButton(link)
            self.nav_btns[link] = btn
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, l=link: self._switch_tab(l))
            btn.setStyleSheet(f"color: {GREEN}; border-bottom: 2px solid {GREEN}; font-weight: bold; padding: 24px 10px 22px 10px; background: transparent; font-size: 14px;")
            nav_lay.addWidget(btn)
            
        nav_lay.addStretch()
        
        # Status right
        live_btn = QPushButton("● Live")
        live_btn.setStyleSheet(f"color: {GREEN}; border: 1px solid {GREEN}; border-radius: 14px; padding: 4px 12px; background: transparent; font-weight: bold; font-family: 'Inter';")
        nav_lay.addWidget(live_btn)
        
        main_layout.addWidget(top_nav)
        
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # Content Area - Dashboard (Index 0)
        content_scroll = QScrollArea()
        content_scroll.setWidgetResizable(True)
        content_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content_w = QWidget()
        content_scroll.setWidget(content_w)
        
        # Page layout with header and columns
        main_page_lay = QVBoxLayout(content_w)
        main_page_lay.setContentsMargins(40, 40, 40, 40)
        main_page_lay.setSpacing(32)
        
        # Header inside content_w layout
        hdr_lay = QVBoxLayout()
        hdr_lay.setSpacing(6)
        
        db_title = QLabel("Dashboard")
        db_title.setStyleSheet(f"font-size: 32px; font-weight: 800; color: {TEXT}; font-family: 'Inter';")
        hdr_lay.addWidget(db_title)
        
        db_sub = QLabel("Real-time application filter rules, configuration, and cognitive focus metrics.")
        db_sub.setStyleSheet(f"font-size: 15px; color: {MUTED};")
        hdr_lay.addWidget(db_sub)
        
        main_page_lay.addLayout(hdr_lay)
        
        # Grid layout for bottom content
        content_lay = QHBoxLayout()
        content_lay.setSpacing(24)
        
        # Left Col
        left_col = QVBoxLayout()
        left_col.setSpacing(24)
        left_col.addWidget(self._build_status_card())
        left_col.addWidget(self._build_live_detection_card())
        left_col.addStretch()
        
        # Right Side Layout
        right_side_layout = QVBoxLayout()
        right_side_layout.setSpacing(24)
        
        # 1. Today's Focus Card (Analytics Widget)
        focus_card = Card()
        fc_lay = QVBoxLayout(focus_card)
        fc_lay.setContentsMargins(32, 24, 32, 24)
        fc_lay.setSpacing(16)
        
        fhdr = QHBoxLayout()
        ftitle = QLabel("Focus Analytics")
        ftitle.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {TEXT};")
        fhdr.addWidget(ftitle)
        
        sync_badge = QLabel("Live Sync")
        sync_badge.setStyleSheet(f"color: {GREEN}; border: 1px solid {GREEN}; border-radius: 10px; padding: 2px 8px; font-size: 11px; font-weight: bold;")
        fhdr.addWidget(sync_badge)
        fhdr.addStretch()

        self._date_combo = QComboBox()
        self._date_combo.setFixedHeight(30)
        self._date_combo.setMinimumWidth(130)
        self._date_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {INPUT_BG};
                color: {TEXT};
                border: 1.5px solid {CARD_BDR};
                border-radius: 8px;
                padding: 3px 10px;
                font-size: 12px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {MUTED};
                margin-right: 4px;
            }}
        """)
        self._date_combo.currentIndexChanged.connect(self._on_analytics_date_changed)
        fhdr.addWidget(self._date_combo)

        fc_lay.addLayout(fhdr)
        
        fsub = QLabel("Real-time application usage mapped to cognitive load.")
        fsub.setStyleSheet(f"color: {MUTED}; font-size: 14px;")
        fc_lay.addWidget(fsub)
        
        fc_lay.addSpacing(10)
        
        self.chart = AnalyticsChart(self.monitor)
        fc_lay.addWidget(self.chart)
        
        right_side_layout.addWidget(focus_card)
        
        # 2. Rule Configuration columns
        mid_col = QVBoxLayout()
        mid_col.setSpacing(24)
        mid_col.addWidget(self._build_app_list_card("bad_apps", "🚫 Bad Apps", "bad_phrases", "Blocked Phrases"))
        
        right_col = QVBoxLayout()
        right_col.setSpacing(24)
        right_col.addWidget(self._build_app_list_card("good_apps", "✅ Good Apps", "good_phrases", "✨ Focus Phrases"))
        
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(24)
        columns_layout.addLayout(mid_col)
        columns_layout.addLayout(right_col)
        
        right_side_layout.addLayout(columns_layout)
        
        # 3. System Preferences
        right_side_layout.addWidget(self._build_system_preferences_card())
        right_side_layout.addStretch()
        
        content_lay.addLayout(left_col, 1)
        content_lay.addLayout(right_side_layout, 2)
        
        main_page_lay.addLayout(content_lay)
        
        self.stack.addWidget(content_scroll)
        
        self._refresh_ui()
        
    def _switch_tab(self, tab_name):
        # Update button styles
        for name, btn in self.nav_btns.items():
            if name == tab_name:
                btn.setStyleSheet(f"color: {GREEN}; border-bottom: 2px solid {GREEN}; font-weight: bold; padding: 24px 10px 22px 10px; background: transparent; font-size: 14px;")
            else:
                btn.setStyleSheet(f"color: {MUTED}; padding: 24px 10px; background: transparent; border: none; font-size: 14px;")
        
        if tab_name == "Dashboard":
            self.stack.setCurrentIndex(0)


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

    def _build_status_card(self) -> Card:
        card = Card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(16)

        hdr = QHBoxLayout()
        title = QLabel("Status")
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {TEXT};")
        hdr.addWidget(title)
        hdr.addStretch()
        
        self._toggle = ToggleSwitch()
        self._toggle.toggled.connect(self._on_toggle)
        hdr.addWidget(self._toggle)
        lay.addLayout(hdr)

        active_box = QFrame()
        active_box.setStyleSheet(f"background-color: rgba(78, 222, 163, 0.05); border: 1px solid rgba(78, 222, 163, 0.2); border-radius: 8px;")
        ab_lay = QHBoxLayout(active_box)
        
        self._status_dot = QLabel()
        self._status_dot.setFixedSize(10, 10)
        ab_lay.addWidget(self._status_dot)
        
        self._status_text = QLabel("Active\nNo distractions detected")
        self._status_text.setStyleSheet(f"font-weight: 500; font-size: 13px; border: none; background: transparent;")
        ab_lay.addWidget(self._status_text)
        ab_lay.addStretch()
        lay.addWidget(active_box)
        
        lay.addSpacing(16)
        
        lbl_rem = QLabel("NEXT REMINDER IN")
        lbl_rem.setStyleSheet(f"color: {MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 2px;")
        lbl_rem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(lbl_rem)
        
        self._countdown_label = QLabel("00:00")
        self._countdown_label.setStyleSheet(f"color: {GREEN}; font-size: 42px; font-weight: bold; font-family: 'JetBrains Mono';")
        self._countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self._countdown_label)
        
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
        self._live_proc_label.setStyleSheet(f"color: {TEXT}; font-size: 12px; font-family: 'JetBrains Mono', Consolas, monospace;")
        self._live_proc_label.setTextFormat(Qt.TextFormat.RichText)
        lay.addWidget(self._live_proc_label)

        self._live_title_label = QLabel("📰  <b>Tab/Window:</b> waiting...")
        self._live_title_label.setStyleSheet(f"color: {TEXT}; font-size: 12px; font-family: 'JetBrains Mono', Consolas, monospace;")
        self._live_title_label.setTextFormat(Qt.TextFormat.RichText)
        self._live_title_label.setWordWrap(True)
        lay.addWidget(self._live_title_label)

        self._live_match_label = QLabel("✅  <b>No monitored app in focus</b>")
        self._live_match_label.setStyleSheet(f"color: {MUTED}; font-size: 12px; font-family: 'JetBrains Mono', Consolas, monospace;")
        self._live_match_label.setTextFormat(Qt.TextFormat.RichText)
        lay.addWidget(self._live_match_label)

        return card

    def _build_app_list_card(self, config_key: str, title: str, phrases_key: str, phrases_title: str) -> QWidget:
        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(0,0,0,0)
        lay.setSpacing(24)
        
        # Apps Card
        card = Card()
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(24, 20, 24, 20)
        card_lay.setSpacing(16)

        hdr = QLabel(title)
        color = RED if "Bad" in title else GREEN
        hdr.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color};")
        card_lay.addWidget(hdr)

        list_widget = QListWidget()
        list_widget.setMinimumHeight(150)
        list_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: 0;
            }}
            QListWidget::item {{
                background-color: transparent;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                margin-bottom: 8px;
            }}
        """)
        setattr(self, f"_{config_key}_list", list_widget)
        card_lay.addWidget(list_widget)
        add_btn = SecondaryButton("+ Add App")
        add_btn.setFixedHeight(40)
        add_btn.clicked.connect(lambda: self._add_app(config_key))
        card_lay.addWidget(add_btn)
        
        lay.addWidget(card)
        
        # Phrases Card
        p_card = Card()
        p_lay = QVBoxLayout(p_card)
        p_lay.setContentsMargins(24, 20, 24, 20)
        p_lay.setSpacing(16)
        
        p_hdr = QLabel(phrases_title)
        p_hdr.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {TEXT};")
        p_lay.addWidget(p_hdr)
        
        phrase_edit = QTextEdit()
        phrase_edit.setMinimumHeight(120)
        phrase_edit.setStyleSheet(f"background-color: rgba(11, 19, 38, 0.3); border: 1px solid {CARD_BDR}; border-radius: 8px; padding: 12px; color: {MUTED};")
        setattr(self, f"_{phrases_key}_edit", phrase_edit)
        p_lay.addWidget(phrase_edit)
        
        lay.addWidget(p_card)
        
        return container

    def _build_system_preferences_card(self) -> Card:
        card = Card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(16)
        
        title = QLabel("System Preferences")
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {TEXT};")
        lay.addWidget(title)
        
        # Grid/Form for major settings
        grid = QGridLayout()
        grid.setSpacing(20)
        
        # 1. Reminder interval
        rem_col = QVBoxLayout()
        rem_col.setSpacing(6)
        rem_lbl = SectionLabel("REMINDER INTERVAL (MIN)")
        rem_col.addWidget(rem_lbl)
        self._interval_spin = QSpinBox()
        self._interval_spin.setRange(1, 120)
        self._interval_spin.setValue(15)
        self._interval_spin.setFixedHeight(42)
        rem_col.addWidget(self._interval_spin)
        grid.addLayout(rem_col, 0, 0)
        
        # 2. TTS Engine selection
        engine_col = QVBoxLayout()
        engine_col.setSpacing(6)
        engine_lbl = SectionLabel("TTS ENGINE")
        engine_col.addWidget(engine_lbl)
        self._engine_combo = QComboBox()
        self._engine_combo.setFixedHeight(42)
        self._engine_combo.addItem("☁️ Microsoft Edge Cloud TTS", "edge")
        self._engine_combo.addItem("✨ Google Gemini Flash TTS", "gemini")
        self._engine_combo.addItem("🤖 Local Kokoro TTS (Offline AI)", "kokoro")
        self._engine_combo.addItem("💻 Offline System TTS", "offline")
        engine_col.addWidget(self._engine_combo)
        grid.addLayout(engine_col, 0, 1)
        
        # 3. Voice Assistant selection
        voice_col = QVBoxLayout()
        voice_col.setSpacing(6)
        voice_lbl = SectionLabel("AI VOICE ASSISTANT")
        voice_col.addWidget(voice_lbl)
        self._voice_combo = QComboBox()
        self._voice_combo.setFixedHeight(42)
        voice_col.addWidget(self._voice_combo)
        grid.addLayout(voice_col, 1, 0)
        
        # 4. Gemini API Key container
        self._gemini_key_container = QWidget()
        key_lay = QVBoxLayout(self._gemini_key_container)
        key_lay.setContentsMargins(0, 0, 0, 0)
        key_lay.setSpacing(6)
        
        key_lbl = SectionLabel("GEMINI API KEY")
        self._gemini_key_input = QLineEdit()
        self._gemini_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._gemini_key_input.setPlaceholderText("Enter Gemini API key (optional if env var set)")
        self._gemini_key_input.setFixedHeight(42)
        key_lay.addWidget(key_lbl)
        key_lay.addWidget(self._gemini_key_input)
        
        grid.addWidget(self._gemini_key_container, 1, 1)
        
        # 5. Autostart Checkbox
        self._autostart_checkbox = QCheckBox("Start FocusGuard automatically when Windows starts")
        self._autostart_checkbox.setStyleSheet(f"color: {TEXT}; font-size: 13px; font-weight: 500; padding-top: 8px;")
        grid.addWidget(self._autostart_checkbox, 2, 0, 1, 2)
        
        lay.addLayout(grid)
        
        # Connect engine change slot
        self._engine_combo.currentIndexChanged.connect(self._on_engine_changed)
        
        # Description
        desc = QLabel(
            "FocusGuard supports dynamic Text-to-Speech engines. "
            "Microsoft Edge Cloud provides high-quality neural voices (internet required). "
            "Google Gemini Flash offers ultra-realistic conversational voices (Gemini API key required). "
            "Offline System TTS runs locally without an internet connection."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {MUTED}; font-size: 12px; line-height: 1.45;")
        lay.addWidget(desc)
        
        # 5. Actions Row (Horizontal at bottom)
        actions_lay = QHBoxLayout()
        actions_lay.setSpacing(12)
        actions_lay.addStretch()
        
        test_btn = SecondaryButton("🔊 Test Voice")
        test_btn.setFixedHeight(42)
        test_btn.setMinimumWidth(130)
        test_btn.clicked.connect(self._test_voice)
        actions_lay.addWidget(test_btn)
        
        save_btn = QPushButton("💾 Save Settings")
        save_btn.setFixedHeight(42)
        save_btn.setMinimumWidth(160)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {GREEN};
                color: #002114;
                border-radius: 8px;
                padding: 0 24px;
                font-weight: bold;
                font-family: 'Inter';
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: #6ffbbe; }}
            QPushButton:pressed {{ background-color: #3bca91; }}
        """)
        save_btn.clicked.connect(self._save)
        actions_lay.addWidget(save_btn)
        
        lay.addLayout(actions_lay)
        return card

    # ── Logic ────────────────────────────────────────────────────────────────

    def _refresh_ui(self):
        cfg = self._config
        self._refresh_date_combo()

        self._toggle.setChecked(cfg.get("enabled", True))
        self._update_status_display(cfg.get("enabled", True))

        self._bad_apps_list.clear()
        for app in cfg.get("bad_apps", []):
            self._add_app_row("bad_apps", app)
            
        self._good_apps_list.clear()
        for app in cfg.get("good_apps", []):
            self._add_app_row("good_apps", app)

        self._interval_spin.setValue(cfg.get("reminder_interval", 2))
        
        # Set engine based on configuration
        use_gemini = cfg.get("use_gemini", False)
        use_htts = cfg.get("use_htts", False)
        use_kokoro = cfg.get("use_kokoro", False)
        
        if use_gemini:
            engine_idx = self._engine_combo.findData("gemini")
        elif use_kokoro:
            engine_idx = self._engine_combo.findData("kokoro")
        elif use_htts:
            engine_idx = self._engine_combo.findData("edge")
        else:
            engine_idx = self._engine_combo.findData("offline")
            
        if engine_idx != -1:
            self._engine_combo.setCurrentIndex(engine_idx)
        else:
            self._engine_combo.setCurrentIndex(0) # fallback to edge
            
        self._gemini_key_input.setText(cfg.get("gemini_api_key", ""))
        
        self._bad_phrases_edit.setPlainText("\n".join(cfg.get("bad_phrases", [])))
        self._good_phrases_edit.setPlainText("\n".join(cfg.get("good_phrases", [])))

        # Voice selection
        voice_id = cfg.get("tts_voice", "en-US-AriaNeural")
        voice_idx = self._voice_combo.findData(voice_id)
        if voice_idx != -1:
            self._voice_combo.setCurrentIndex(voice_idx)
        else:
            self._voice_combo.setCurrentIndex(0)

        # Autostart checkbox
        self._autostart_checkbox.setChecked(cfg.get("autostart", False))

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

    def _on_engine_changed(self, index):
        engine = self._engine_combo.currentData()
        self._voice_combo.clear()
        
        # Unload Kokoro ONNX model from memory if switched away to save CPU/memory
        if engine != "kokoro" and hasattr(self, "tts"):
            self.tts.unload_kokoro()

        # Filter voices based on selected engine
        if engine == "edge":
            for voice_id, voice_label in VOICES:
                if not voice_id.startswith("gemini-") and not voice_id.startswith("kokoro-"):
                    self._voice_combo.addItem(voice_label, voice_id)
            self._gemini_key_container.setVisible(False)
        elif engine == "gemini":
            for voice_id, voice_label in VOICES:
                if voice_id.startswith("gemini-"):
                    self._voice_combo.addItem(voice_label, voice_id)
            self._gemini_key_container.setVisible(True)
        elif engine == "kokoro":
            for voice_id, voice_label in VOICES:
                if voice_id.startswith("kokoro-"):
                    self._voice_combo.addItem(voice_label, voice_id)
            self._gemini_key_container.setVisible(False)
        else: # offline
            self._voice_combo.addItem("Default System Voice (Offline)", "system-default")
            self._gemini_key_container.setVisible(False)

    def _refresh_date_combo(self):
        prev_selected = self._date_combo.currentData()
        self._date_combo.blockSignals(True)
        self._date_combo.clear()
        
        from datetime import datetime, timedelta
        dates = self.monitor.analytics.get_available_dates()
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in dates:
            dates.insert(0, today)
            
        for d in dates:
            label = "Today" if d == today else d
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            if d == yesterday:
                label = "Yesterday"
            self._date_combo.addItem(label, d)
            
        # Restore selection
        if prev_selected:
            idx = self._date_combo.findData(prev_selected)
            if idx != -1:
                self._date_combo.setCurrentIndex(idx)
            else:
                self._date_combo.setCurrentIndex(0)
        else:
            self._date_combo.setCurrentIndex(0)
            
        self._date_combo.blockSignals(False)

    def _on_analytics_date_changed(self):
        selected_date = self._date_combo.currentData()
        if selected_date:
            self.chart.set_selected_date(selected_date)

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
        engine = self._engine_combo.currentData()
        
        use_htts = (engine == "edge")
        use_gemini = (engine == "gemini")
        use_kokoro = (engine == "kokoro")
        
        self.tts.speak(
            random.choice(phrases),
            voice,
            use_htts=use_htts,
            use_gemini=use_gemini,
            use_kokoro=use_kokoro,
            gemini_api_key=self._gemini_key_input.text().strip()
        )

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

        engine = self._engine_combo.currentData()
        use_htts = (engine == "edge")
        use_gemini = (engine == "gemini")
        use_kokoro = (engine == "kokoro")

        self._config.update({
            "bad_apps": _get_list("bad_apps"),
            "good_apps": _get_list("good_apps"),
            "bad_phrases": _get_phrases("bad_phrases"),
            "good_phrases": _get_phrases("good_phrases"),
            "reminder_interval": self._interval_spin.value(),
            "tts_voice": self._voice_combo.currentData(),
            "use_htts": use_htts,
            "use_gemini": use_gemini,
            "use_kokoro": use_kokoro,
            "gemini_api_key": self._gemini_key_input.text().strip(),
            "autostart": self._autostart_checkbox.isChecked(),
        })

        if self.config_saver(self._config):
            from config import set_autostart
            set_autostart(self._config["autostart"])
            QMessageBox.information(self, "Saved", "Settings saved successfully!\nPhrases will take effect immediately.")
            # Trigger pre-cache of all new phrases
            all_phrases = self._config["bad_phrases"] + self._config["good_phrases"]
            self.tts.prepare_many(
                all_phrases,
                self._config["tts_voice"],
                self._config["use_htts"],
                self._config["use_gemini"],
                self._config["use_kokoro"],
                self._config["gemini_api_key"]
            )

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

