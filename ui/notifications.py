"""Desktop notification manager using QSystemTrayIcon."""
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import QTimer, QTime, Qt
from datetime import date
import json, os

CONFIG_PATH = os.path.expanduser("~/.mindful_path/config.json")

TIME_MESSAGES = {
    "morning": [
        ("Mindful Path", "Good morning. Your practice awaits. 🌅"),
        ("Mindful Path", "A new day, a fresh beginning. Set your intention. ☸"),
        ("Mindful Path", "The present moment is the only moment. Begin here. 🌿"),
    ],
    "afternoon": [
        ("Mindful Path", "Afternoon check-in — how is your practice going? ☀"),
        ("Mindful Path", "A mindful breath, right now. Then carry on. 🌬"),
        ("Mindful Path", "Half the day remains. What will you bring to it? ◉"),
    ],
    "evening": [
        ("Mindful Path", "Evening — time to reflect and let the day settle. 🌙"),
        ("Mindful Path", "Complete your practice and take a moment to be grateful. ✦"),
        ("Mindful Path", "The day is closing. Return to yourself. 🌿"),
    ],
}


def _make_tray_icon() -> QIcon:
    """Draw a simple ☸ icon for the system tray."""
    px = QPixmap(64, 64)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor("#c8790a"))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(4, 4, 56, 56)
    p.setPen(QColor("#ffffff"))
    font = QFont()
    font.setPixelSize(36)
    p.setFont(font)
    p.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, "☸")
    p.end()
    return QIcon(px)


class NotificationManager:
    def __init__(self, parent=None):
        self._parent = parent
        self._cfg = self._load_config()
        self._tray: QSystemTrayIcon | None = None
        self._timer: QTimer | None = None
        self._last_fired: dict = self._cfg.get("last_notified", {})

        if QSystemTrayIcon.isSystemTrayAvailable():
            self._tray = QSystemTrayIcon(_make_tray_icon(), parent)
            self._tray.setToolTip("Mindful Path")
            menu = QMenu()
            menu.addAction("Open Mindful Path", self._on_open)
            menu.addSeparator()
            menu.addAction("Quit", QApplication.instance().quit)
            self._tray.setContextMenu(menu)
            self._tray.show()

        self._timer = QTimer()
        self._timer.setInterval(60_000)  # check every minute
        self._timer.timeout.connect(self._check)
        if self._cfg.get("notifications_enabled", True):
            self._timer.start()

    # ── Config ──────────────────────────────────────────────

    def _load_config(self) -> dict:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH) as f:
                return json.load(f)
        return {}

    def _save_config(self):
        existing = {}
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH) as f:
                existing = json.load(f)
        existing.update({
            "notifications_enabled": self._cfg.get("notifications_enabled", True),
            "morning_time":  self._cfg.get("morning_time",  "08:00"),
            "afternoon_time": self._cfg.get("afternoon_time", "14:00"),
            "evening_time":  self._cfg.get("evening_time",  "20:00"),
            "last_notified": self._last_fired,
        })
        with open(CONFIG_PATH, "w") as f:
            json.dump(existing, f)

    @property
    def enabled(self) -> bool:
        return self._cfg.get("notifications_enabled", True)

    @property
    def morning_time(self) -> str:
        return self._cfg.get("morning_time", "08:00")

    @property
    def afternoon_time(self) -> str:
        return self._cfg.get("afternoon_time", "14:00")

    @property
    def evening_time(self) -> str:
        return self._cfg.get("evening_time", "20:00")

    def update_settings(self, enabled: bool, morning: str, afternoon: str, evening: str):
        self._cfg["notifications_enabled"] = enabled
        self._cfg["morning_time"]  = morning
        self._cfg["afternoon_time"] = afternoon
        self._cfg["evening_time"]  = evening
        self._save_config()
        if enabled:
            self._timer.start()
        else:
            self._timer.stop()

    # ── Notification logic ───────────────────────────────────

    def _check(self):
        if not self._tray:
            return
        now     = QTime.currentTime()
        today   = date.today().isoformat()
        slots   = [
            ("morning",   self.morning_time),
            ("afternoon", self.afternoon_time),
            ("evening",   self.evening_time),
        ]
        for slot, time_str in slots:
            try:
                h, m = map(int, time_str.split(":"))
            except ValueError:
                continue
            target = QTime(h, m)
            diff   = abs(now.secsTo(target))
            fired_key = f"{today}_{slot}"
            if diff <= 60 and fired_key not in self._last_fired:
                self._fire(slot)
                self._last_fired[fired_key] = True
                self._save_config()

    def _fire(self, slot: str):
        if not self._tray:
            return
        msgs = TIME_MESSAGES.get(slot, [])
        idx  = date.today().timetuple().tm_yday % len(msgs)
        title, msg = msgs[idx]
        self._tray.showMessage(title, msg, QSystemTrayIcon.MessageIcon.NoIcon, 6000)

    def notify_completion(self, habit_name: str):
        """Called when a habit is marked complete."""
        if self._tray and self._cfg.get("notifications_enabled", True):
            self._tray.showMessage(
                "Practice complete ✓",
                f"{habit_name}",
                QSystemTrayIcon.MessageIcon.NoIcon,
                2500,
            )

    def _on_open(self):
        if self._parent:
            self._parent.showNormal()
            self._parent.raise_()
            self._parent.activateWindow()
