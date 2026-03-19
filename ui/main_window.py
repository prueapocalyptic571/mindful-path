from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame, QApplication,
)
from PyQt6.QtCore import Qt
import os
import json

from .today_view import TodayView
from .habits_view import HabitsView
from .progress_view import ProgressView
from .reflection_view import ReflectionView
from .about_view import AboutView
from database import Database

CONFIG_PATH = os.path.expanduser("~/.mindful_path/config.json")


def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {"dark_mode": False}


def save_config(cfg: dict):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f)


class NavButton(QPushButton):
    def __init__(self, icon: str, text: str, parent=None):
        super().__init__(parent)
        self.setText(f"  {icon}   {text}")
        self.setCheckable(True)
        self.setMinimumHeight(46)
        self.setFlat(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("nav_button")


class MainWindow(QMainWindow):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self._cfg = load_config()
        self._dark = self._cfg.get("dark_mode", False)
        self._notif = None  # guard: set properly in _build_ui
        self.setWindowTitle("Mindful Path")
        self.setMinimumSize(960, 680)
        self.resize(1100, 740)
        self._build_ui()
        self._apply_theme()

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_sidebar())

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setObjectName("sidebar_sep")
        layout.addWidget(sep)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        self.today_view = TodayView(self.db)
        self.habits_view = HabitsView(self.db)
        self.progress_view = ProgressView(self.db)
        self.reflection_view = ReflectionView(self.db)
        self.about_view = AboutView()

        for v in (self.today_view, self.habits_view, self.progress_view,
                  self.reflection_view, self.about_view):
            self.stack.addWidget(v)

        self.habits_view.habits_changed.connect(self.today_view.refresh)
        self.habits_view.habits_changed.connect(self.progress_view.refresh)

        self.nav_buttons[0].setChecked(True)
        self.stack.setCurrentIndex(0)

        # Notifications
        from .notifications import NotificationManager
        self._notif = NotificationManager(self)

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setObjectName("sidebar")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 16)
        layout.setSpacing(0)

        # ── Header ──────────────────────────────
        header = QWidget()
        header.setObjectName("sidebar_header")
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(16, 22, 16, 18)
        h_layout.setSpacing(4)

        wheel = QLabel("☸")
        wheel.setObjectName("sidebar_wheel")
        wheel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h_layout.addWidget(wheel)

        title = QLabel("Mindful Path")
        title.setObjectName("sidebar_title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h_layout.addWidget(title)

        sub = QLabel("Daily Practice")
        sub.setObjectName("sidebar_sub")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h_layout.addWidget(sub)

        layout.addWidget(header)

        # ── Nav ──────────────────────────────
        nav_items = [
            ("◉", "Today"),
            ("≡", "Habits"),
            ("◈", "Progress"),
            ("✦", "Reflect"),
            ("☯", "About"),
        ]
        self.nav_buttons: list[NavButton] = []

        nav_wrap = QWidget()
        nav_layout = QVBoxLayout(nav_wrap)
        nav_layout.setContentsMargins(10, 10, 10, 10)
        nav_layout.setSpacing(3)

        for i, (icon, text) in enumerate(nav_items):
            btn = NavButton(icon, text)
            btn.clicked.connect(lambda _, idx=i: self._go(idx))
            self.nav_buttons.append(btn)
            nav_layout.addWidget(btn)

        layout.addWidget(nav_wrap)
        layout.addStretch()

        # ── Theme toggle ─────────────────────────
        self.theme_btn = QPushButton()
        self.theme_btn.setObjectName("theme_toggle")
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.clicked.connect(self._toggle_theme)

        settings_btn = QPushButton("⚙")
        settings_btn.setObjectName("theme_toggle")
        settings_btn.setToolTip("Settings")
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.clicked.connect(self._open_settings)

        bottom_row = QWidget()
        br_layout = QHBoxLayout(bottom_row)
        br_layout.setContentsMargins(12, 0, 12, 0)
        br_layout.setSpacing(8)
        br_layout.addWidget(settings_btn)
        br_layout.addStretch()
        br_layout.addWidget(self.theme_btn)
        layout.addWidget(bottom_row)

        hint = QLabel("each day, begin again")
        hint.setObjectName("sidebar_hint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        return sidebar

    def _go(self, index: int):
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        self.stack.setCurrentIndex(index)
        if index == 0:
            self.today_view.refresh()
        elif index == 2:
            self.progress_view.refresh()
        elif index == 3:
            self.reflection_view.refresh()

    def _apply_theme(self):
        from PyQt6.QtGui import QPalette, QColor
        app = QApplication.instance()

        # Load QSS
        base = os.path.dirname(os.path.dirname(__file__))
        qss_file = "dark.qss" if self._dark else "style.qss"
        with open(os.path.join(base, "resources", qss_file)) as f:
            app.setStyleSheet(f.read())

        # Update QPalette so Fusion-drawn widgets also respect the theme
        p = QPalette()
        if self._dark:
            p.setColor(QPalette.ColorRole.Window,          QColor("#1a1510"))
            p.setColor(QPalette.ColorRole.WindowText,      QColor("#e0d0b8"))
            p.setColor(QPalette.ColorRole.Base,            QColor("#241e14"))
            p.setColor(QPalette.ColorRole.AlternateBase,   QColor("#2a2318"))
            p.setColor(QPalette.ColorRole.Text,            QColor("#e0d0b8"))
            p.setColor(QPalette.ColorRole.BrightText,      QColor("#ffffff"))
            p.setColor(QPalette.ColorRole.Button,          QColor("#2a2318"))
            p.setColor(QPalette.ColorRole.ButtonText,      QColor("#e0d0b8"))
            p.setColor(QPalette.ColorRole.Highlight,       QColor("#d4880f"))
            p.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
            p.setColor(QPalette.ColorRole.ToolTipBase,     QColor("#2a2318"))
            p.setColor(QPalette.ColorRole.ToolTipText,     QColor("#e0d0b8"))
            p.setColor(QPalette.ColorRole.PlaceholderText, QColor("#6a5a48"))
            p.setColor(QPalette.ColorRole.Mid,             QColor("#3e3224"))
            p.setColor(QPalette.ColorRole.Dark,            QColor("#130e0a"))
            p.setColor(QPalette.ColorRole.Shadow,          QColor("#0a0806"))
        else:
            p.setColor(QPalette.ColorRole.Window,          QColor("#faf8f3"))
            p.setColor(QPalette.ColorRole.WindowText,      QColor("#2c2416"))
            p.setColor(QPalette.ColorRole.Base,            QColor("#ffffff"))
            p.setColor(QPalette.ColorRole.AlternateBase,   QColor("#f4efe6"))
            p.setColor(QPalette.ColorRole.Text,            QColor("#2c2416"))
            p.setColor(QPalette.ColorRole.BrightText,      QColor("#000000"))
            p.setColor(QPalette.ColorRole.Button,          QColor("#f0ebe0"))
            p.setColor(QPalette.ColorRole.ButtonText,      QColor("#2c2416"))
            p.setColor(QPalette.ColorRole.Highlight,       QColor("#c8790a"))
            p.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
            p.setColor(QPalette.ColorRole.PlaceholderText, QColor("#a09080"))
            p.setColor(QPalette.ColorRole.Mid,             QColor("#d8d0c0"))
            p.setColor(QPalette.ColorRole.Dark,            QColor("#b0a898"))
            p.setColor(QPalette.ColorRole.Shadow,          QColor("#807060"))
        app.setPalette(p)

        self.theme_btn.setText("☀  Light" if self._dark else "◑  Dark")

        # Refresh views so inline-styled widgets repaint with correct colors
        self.today_view.refresh()
        self.progress_view.refresh()

    def _open_settings(self):
        from .settings_dialog import SettingsDialog
        dlg = SettingsDialog(self._notif, self)
        dlg.exec()

    def _toggle_theme(self):
        self._dark = not self._dark
        self._cfg["dark_mode"] = self._dark
        save_config(self._cfg)
        self._apply_theme()

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)
