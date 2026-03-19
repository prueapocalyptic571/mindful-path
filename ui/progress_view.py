from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from datetime import date, timedelta
from collections import defaultdict

from database import Database

CATEGORY_COLORS = {
    "Mind": "#7c9cbf", "Body": "#6ea87a", "Study": "#c8790a",
    "Heart": "#c86a7c", "Path": "#9c7cbc",
}


class WeekBar(QWidget):
    """Mini 7-dot row showing last 7 days."""
    def __init__(self, days: list[bool], parent=None):
        super().__init__(parent)
        self._days = days
        self.setFixedSize(7 * 20, 20)

    def paintEvent(self, event):
        from PyQt6.QtWidgets import QApplication
        dark = QApplication.palette().window().color().lightness() < 128
        done_col = QColor("#d4880f") if dark else QColor("#c8790a")
        empty_col = QColor("#3e3224") if dark else QColor("#e8e0d0")

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        for i, done in enumerate(self._days):
            x = i * 20 + 4
            y = 4
            r = 7
            p.setBrush(done_col if done else empty_col)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(x, y, r * 2, r * 2)


class DailyBar(QWidget):
    """Weekly completion bar chart (last 7 days)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: list[tuple[str, float]] = []
        self.setMinimumHeight(120)
        self.setMaximumHeight(150)

    def set_data(self, data: list[tuple[str, float]]):
        self._data = data
        self.update()

    def paintEvent(self, event):
        if not self._data:
            return
        from PyQt6.QtWidgets import QApplication
        dark = QApplication.palette().window().color().lightness() < 128
        bar_active = QColor("#d4880f") if dark else QColor("#c8790a")
        bar_inactive = QColor("#3e3224") if dark else QColor("#e0d4c0")
        label_col = QColor("#8a7860") if dark else QColor("#8a7a6a")
        pct_col = QColor("#a09070") if dark else QColor("#5a4535")

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        pad = 10
        bar_area_h = h - 34
        n = len(self._data)
        slot_w = (w - 2 * pad) / n
        bar_w = min(slot_w * 0.55, 36)

        for i, (label, pct) in enumerate(self._data):
            x = pad + i * slot_w + (slot_w - bar_w) / 2
            bar_h = max(4, pct * bar_area_h)
            y = pad + bar_area_h - bar_h

            # Bar
            if label == date.today().strftime("%a"):
                p.setBrush(bar_active)
            else:
                p.setBrush(bar_inactive)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(QRectF(x, y, bar_w, bar_h), 4, 4)

            # Day label
            font = QFont()
            font.setPixelSize(11)
            p.setFont(font)
            p.setPen(QPen(label_col))
            label_rect = QRectF(x - 4, h - 22, bar_w + 8, 20)
            p.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, label)

            # Percent label (only if > 0)
            if pct > 0.05:
                pct_str = f"{int(pct * 100)}%"
                font2 = QFont()
                font2.setPixelSize(10)
                p.setFont(font2)
                p.setPen(QPen(pct_col))
                p.drawText(QRectF(x - 4, y - 16, bar_w + 8, 16),
                           Qt.AlignmentFlag.AlignCenter, pct_str)


class StatCard(QFrame):
    def __init__(self, label: str, value: str, color: str = "#c8790a", parent=None):
        super().__init__(parent)
        self.setObjectName("stat_card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        val_lbl = QLabel(value)
        val_lbl.setObjectName("stat_value")
        val_lbl.setStyleSheet(f"color: {color}; font-size: 26px; font-weight: bold;")
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        key_lbl = QLabel(label)
        key_lbl.setStyleSheet("color: #8a7a6a; font-size: 11px;")
        key_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(val_lbl)
        layout.addWidget(key_lbl)



class ProgressView(QWidget):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setObjectName("view_header")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(28, 20, 28, 20)
        title = QLabel("Your Progress")
        title.setObjectName("view_title")
        h_layout.addWidget(title)
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(scroll, 1)

        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(24, 16, 24, 24)
        self.content_layout.setSpacing(16)
        scroll.setWidget(content)

    def refresh(self):
        # Clear
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        habits = self.db.get_habits()
        today = date.today().isoformat()
        completions = self.db.get_today_completions(today)
        done_today = sum(1 for h in habits if completions.get(h["id"], False))
        total = len(habits)
        today_pct = int(100 * done_today / total) if total else 0

        best_streak = max((self.db.get_streak(h["id"]) for h in habits), default=0)
        avg_30 = 0.0
        if habits:
            avg_30 = sum(self.db.get_completion_rate(h["id"], 30) for h in habits) / len(habits)

        # ── Stat cards ──────────────────────────
        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)
        card_data = [
            ("Today", f"{today_pct}%", "#c8790a"),
            ("Active Practices", str(total), "#7c9cbf"),
            ("Best Streak", f"{best_streak}🔥", "#d05a20"),
            ("30-Day Avg", f"{int(avg_30 * 100)}%", "#6ea87a"),
        ]
        for label, val, color in card_data:
            card = StatCard(label, val, color)
            cards_row.addWidget(card)
        self.content_layout.addLayout(cards_row)

        # ── Weekly bar chart ──────────────────────
        section_lbl = QLabel("LAST 7 DAYS")
        section_lbl.setStyleSheet(
            "color: #8a7a6a; font-size: 11px; font-weight: bold; letter-spacing: 2px;"
        )
        self.content_layout.addWidget(section_lbl)

        # Build per-day completion rate
        week_data = []
        for i in range(6, -1, -1):
            d = date.today() - timedelta(days=i)
            d_str = d.isoformat()
            day_done = sum(
                1 for h in habits if self.db.get_completion(h["id"], d_str)
            )
            pct = day_done / total if total else 0
            week_data.append((d.strftime("%a"), pct))

        bar_chart = DailyBar()
        bar_chart.set_data(week_data)
        bar_chart.setObjectName("chart_card")
        self.content_layout.addWidget(bar_chart)

        # ── Per-habit streaks ──────────────────────
        section_lbl2 = QLabel("PRACTICE DETAILS")
        section_lbl2.setStyleSheet(
            "color: #8a7a6a; font-size: 11px; font-weight: bold; letter-spacing: 2px; margin-top: 4px;"
        )
        self.content_layout.addWidget(section_lbl2)

        for h in habits:
            streak = self.db.get_streak(h["id"])
            longest = self.db.get_longest_streak(h["id"])
            rate_30 = self.db.get_completion_rate(h["id"], 30)
            week_dots = self.db.get_weekly_completions(h["id"])
            cat = h.get("category", "Mind")
            color = CATEGORY_COLORS.get(cat, "#888")

            row_frame = QFrame()
            row_frame.setObjectName("habit_row")
            row_layout = QHBoxLayout(row_frame)
            row_layout.setContentsMargins(14, 10, 14, 10)
            row_layout.setSpacing(12)

            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 16px;")
            dot.setFixedWidth(20)
            row_layout.addWidget(dot)

            info = QVBoxLayout()
            info.setSpacing(2)
            name_lbl = QLabel(h["name"])
            name_font = QFont()
            name_font.setPixelSize(13)
            name_font.setBold(True)
            name_lbl.setFont(name_font)
            info.addWidget(name_lbl)

            detail = QLabel(f"30-day: {int(rate_30 * 100)}%  ·  Longest: {longest} days")
            detail.setStyleSheet("color: #8a7a6a; font-size: 11px;")
            info.addWidget(detail)

            row_layout.addLayout(info, 1)

            week_bar = WeekBar(week_dots)
            row_layout.addWidget(week_bar)

            streak_lbl = QLabel(f"🔥 {streak}")
            streak_lbl.setStyleSheet("color: #c8790a; font-size: 13px; min-width: 44px;")
            streak_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            row_layout.addWidget(streak_lbl)

            self.content_layout.addWidget(row_frame)

        self.content_layout.addStretch()
