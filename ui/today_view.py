from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QCheckBox, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QPoint, QRect
from PyQt6.QtGui import QPainter, QPen, QColor, QFont
from datetime import date

from database import Database

# ── Quotes ────────────────────────────────────────────────────────────────

QUOTES = [
    ("Peace comes from within. Do not seek it without.", "The Buddha"),
    ("The mind is everything. What you think, you become.", "The Buddha"),
    ("Three things cannot be long hidden: the sun, the moon, and the truth.", "The Buddha"),
    ("Do not dwell in the past, do not dream of the future,\nconcentrate the mind on the present moment.", "The Buddha"),
    ("You yourself, as much as anybody in the entire universe,\ndeserve your love and affection.", "The Buddha"),
    ("It is better to travel well than to arrive.", "The Buddha"),
    ("Be where you are; otherwise you will miss your life.", "The Buddha"),
    ("The way is not in the sky. The way is in the heart.", "Dhammapada"),
    ("All that we are is the result of what we have thought.", "Dhammapada"),
    ("A disciplined mind brings happiness.", "Dhammapada"),
    ("In the end, only three things matter:\nhow much you loved, how gently you lived,\nand how gracefully you let go.", "Buddhist Teaching"),
    ("If you light a lamp for somebody,\nit will also brighten your path.", "The Buddha"),
    ("Work out your own salvation. Do not depend on others.", "The Buddha"),
    ("No one saves us but ourselves.\nWe ourselves must walk the path.", "The Buddha"),
    ("Thousands of candles can be lit from a single candle,\nand the life of the candle will not be shortened.\nHappiness never decreases by being shared.", "The Buddha"),
    ("To understand everything is to forgive everything.", "The Buddha"),
    ("The root of suffering is attachment.", "The Buddha"),
    ("With our thoughts we make the world.", "The Buddha"),
    ("Every morning we are born again.\nWhat we do today matters most.", "The Buddha"),
    ("There is no path to happiness. Happiness is the path.", "Thích Nhất Hạnh"),
    ("The present moment is the only moment available to us,\nand it is the door to all moments.", "Thích Nhất Hạnh"),
    ("Smile, breathe, and go slowly.", "Thích Nhất Hạnh"),
    ("Because you are alive, everything is possible.", "Thích Nhất Hạnh"),
    ("The most precious gift we can offer anyone is our attention.", "Thích Nhất Hạnh"),
    ("Breathing in, I calm body and mind.\nBreathing out, I smile.", "Thích Nhất Hạnh"),
    ("Walk as if you are kissing the Earth with your feet.", "Thích Nhất Hạnh"),
    ("Letting go gives us freedom,\nand freedom is the only condition for happiness.", "Thích Nhất Hạnh"),
    ("Nothing is permanent. Everything is subject to change.\nBeing is always becoming.", "The Buddha"),
    ("The greatest wealth is a peaceful mind.", "The Buddha"),
    ("When you realize how perfect everything is,\nyou will tilt your head back and laugh at the sky.", "The Buddha"),
]

PRIORITY_TEXT = {1: "Essential", 2: "Important", 3: "Gentle"}
PRIORITY_COLOR = {1: "#d05a20", 2: "#c8790a", 3: "#5c7a5c"}


# ── Progress Ring ─────────────────────────────────────────────────────────

class ProgressRing(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._done = 0
        self._total = 1
        self.setFixedSize(110, 110)

    def set_progress(self, done: int, total: int):
        self._done = done
        self._total = max(1, total)
        self.update()

    def paintEvent(self, event):
        from PyQt6.QtWidgets import QApplication
        dark = QApplication.palette().window().color().lightness() < 128
        track_col = QColor("#3e3224") if dark else QColor("#e8e0d0")
        arc_col = QColor("#d4880f") if dark else QColor("#c8790a")
        text_col = QApplication.palette().windowText().color()

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        m = 10
        rect = QRectF(m, m, self.width() - 2 * m, self.height() - 2 * m)

        # Track
        pen = QPen(track_col)
        pen.setWidth(9)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawEllipse(rect)

        # Arc
        pct = self._done / self._total if self._total else 0
        if pct > 0:
            angle = int(pct * 360 * 16)
            pen = QPen(arc_col)
            pen.setWidth(9)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.drawArc(rect, 90 * 16, -angle)

        # Center text — muted when at 0%, full color when progress > 0
        pct_int = int(pct * 100)
        font = QFont()
        font.setPixelSize(20)
        font.setBold(True)
        p.setFont(font)
        if pct == 0:
            muted = QColor(text_col)
            muted.setAlphaF(0.35)
            p.setPen(QPen(muted))
        else:
            p.setPen(QPen(text_col))
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{pct_int}%")


# ── Habit Item ────────────────────────────────────────────────────────────

class HabitItem(QFrame):
    toggled = pyqtSignal(int, bool)

    def __init__(self, habit: dict, completed: bool, streak: int,
                 db=None, date_str: str = None, parent=None):
        super().__init__(parent)
        self.habit = habit
        self.habit_id = habit["id"]
        self._completed = completed
        self._db = db
        self._date_str = date_str
        self.setObjectName("habit_item")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._build(habit, completed, streak)
        self._apply_style(completed)

    def _build(self, habit: dict, completed: bool, streak: int):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(14)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(completed)
        self.checkbox.setFixedSize(22, 22)
        self.checkbox.clicked.connect(self._on_click)
        layout.addWidget(self.checkbox)

        info = QVBoxLayout()
        info.setSpacing(2)

        name = QLabel(habit["name"])
        name_font = QFont()
        name_font.setPixelSize(14)
        name_font.setBold(True)
        if completed:
            name_font.setStrikeOut(True)
            name.setStyleSheet("color: #a09080;")
        name.setFont(name_font)
        info.addWidget(name)

        if habit.get("eightfold_aspect"):
            asp = QLabel(f"↝  {habit['eightfold_aspect']}")
            asp.setStyleSheet("color: #a09080; font-size: 11px; font-style: italic;")
            info.addWidget(asp)

        layout.addLayout(info, 1)

        # Right badges
        right = QHBoxLayout()
        right.setSpacing(8)

        if streak > 0:
            streak_lbl = QLabel(f"🔥 {streak}")
            streak_lbl.setStyleSheet("color: #c8790a; font-size: 12px;")
            right.addWidget(streak_lbl)

        pri = habit.get("priority", 2)
        pri_col = PRIORITY_COLOR.get(pri, "#c8790a")
        pri_lbl = QLabel(PRIORITY_TEXT.get(pri, "Important"))
        pri_lbl.setStyleSheet(f"color: {pri_col}; font-size: 11px;")
        right.addWidget(pri_lbl)

        chevron = QLabel("›")
        chevron.setStyleSheet("color: #c8b898; font-size: 16px; padding-left: 4px;")
        right.addWidget(chevron)
        layout.addLayout(right)

    def _apply_style(self, completed: bool):
        from PyQt6.QtWidgets import QApplication
        dark = QApplication.palette().window().color().lightness() < 128
        if completed:
            bg     = "#2e2820" if dark else "#f5f2ec"
            border = "#3e3428" if dark else "#ddd5c5"
        else:
            bg     = "#2a2318" if dark else "#ffffff"
            border = "#3e3224" if dark else "#e8e0d0"
        hover  = "#d4880f"  if dark else "#c8790a"
        self.setStyleSheet(
            f"HabitItem {{ background: {bg}; border: 1px solid {border}; border-radius: 7px; }}"
            f"HabitItem:hover {{ border-color: {hover}; }}"
        )

    def _on_click(self, checked: bool):
        self._completed = checked
        self.toggled.emit(self.habit_id, checked)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            cb_rect = QRect(self.checkbox.mapTo(self, QPoint(0, 0)), self.checkbox.size())
            if cb_rect.contains(event.pos()):
                # Let the checkbox handle it
                pass
            else:
                # Open detail dialog
                self._open_detail()
        super().mousePressEvent(event)

    def _open_detail(self):
        if not self._db or not self._date_str:
            return
        from .habit_detail import HabitDetailDialog
        dlg = HabitDetailDialog(self.habit, self._db, self._date_str,
                                self._completed, self)
        dlg.completion_changed.connect(self._on_external_toggle)
        dlg.exec()

    def _on_external_toggle(self, habit_id: int, completed: bool):
        self._completed = completed
        self.checkbox.blockSignals(True)
        self.checkbox.setChecked(completed)
        self.checkbox.blockSignals(False)
        self._apply_style(completed)
        self.toggled.emit(habit_id, completed)


# ── Today View ────────────────────────────────────────────────────────────

class TodayView(QWidget):
    completion_changed = pyqtSignal()

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self._today = date.today().isoformat()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Header bar ──────────────────────────────
        header = QWidget()
        header.setObjectName("today_header")
        header.setFixedHeight(90)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(28, 16, 28, 16)

        date_block = QVBoxLayout()
        self.date_label = QLabel()
        self.date_label.setObjectName("today_date")
        self.day_label = QLabel()
        self.day_label.setObjectName("today_day")
        date_block.addWidget(self.date_label)
        date_block.addWidget(self.day_label)
        h_layout.addLayout(date_block, 1)

        self.ring = ProgressRing()
        h_layout.addWidget(self.ring)

        outer.addWidget(header)

        # ── Quote bar ──────────────────────────────
        quote_frame = QWidget()
        quote_frame.setObjectName("quote_bar")
        q_layout = QVBoxLayout(quote_frame)
        q_layout.setContentsMargins(28, 12, 28, 12)
        self.quote_text = QLabel()
        self.quote_text.setObjectName("quote_text")
        self.quote_text.setWordWrap(True)
        self.quote_author = QLabel()
        self.quote_author.setObjectName("quote_author")
        q_layout.addWidget(self.quote_text)
        q_layout.addWidget(self.quote_author)
        outer.addWidget(quote_frame)

        # ── Scrollable habit list ──────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll, 1)

        self.habits_container = QWidget()
        self.habits_layout = QVBoxLayout(self.habits_container)
        self.habits_layout.setContentsMargins(24, 16, 24, 24)
        self.habits_layout.setSpacing(8)
        self.habits_layout.addStretch()
        scroll.setWidget(self.habits_container)

    def refresh(self):
        self._today = date.today().isoformat()
        d = date.today()

        # Header
        self.date_label.setText(d.strftime("%B %d, %Y"))
        self.day_label.setText(d.strftime("%A"))

        # Quote (deterministic per day)
        idx = d.timetuple().tm_yday % len(QUOTES)
        text, author = QUOTES[idx]
        self.quote_text.setText(f'"{text}"')
        self.quote_author.setText(f"— {author}")

        # Clear habit list
        while self.habits_layout.count() > 1:
            item = self.habits_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        habits = self.db.get_habits()
        completions = self.db.get_today_completions(self._today)

        done = sum(1 for h in habits if completions.get(h["id"], False))
        self.ring.set_progress(done, len(habits))

        # Group by time of day
        from collections import defaultdict
        grouped: dict = defaultdict(list)
        for h in habits:
            grouped[h.get("time_of_day", "Anytime")].append(h)

        time_order = ["Morning", "Afternoon", "Evening", "Anytime"]
        time_icons  = {"Morning": "🌅", "Afternoon": "☀", "Evening": "🌙", "Anytime": "◦"}
        time_colors = {"Morning": "#c8a050", "Afternoon": "#c8790a",
                       "Evening": "#9c7cbc",  "Anytime":   "#8a9a8a"}

        insert_pos = 0
        for tod in time_order:
            if tod not in grouped:
                continue

            # Time-of-day section header
            tod_header = QWidget()
            th_layout = QHBoxLayout(tod_header)
            th_layout.setContentsMargins(0, 10, 4, 4)
            icon  = time_icons.get(tod, "◦")
            color = time_colors.get(tod, "#888")
            tod_lbl = QLabel(f"  {icon}  {tod.upper()}")
            tod_lbl.setStyleSheet(
                f"color: {color}; font-size: 11px; font-weight: bold; letter-spacing: 2px;"
                f"border-left: 3px solid {color}; padding-left: 6px;"
            )
            th_layout.addWidget(tod_lbl)
            th_layout.addStretch()
            self.habits_layout.insertWidget(insert_pos, tod_header)
            insert_pos += 1

            for h in grouped[tod]:
                completed = completions.get(h["id"], False)
                streak = self.db.get_streak(h["id"])
                item = HabitItem(h, completed, streak, self.db, self._today)
                item.toggled.connect(self._on_habit_toggled)
                self.habits_layout.insertWidget(insert_pos, item)
                insert_pos += 1

            spacer = QWidget()
            spacer.setFixedHeight(6)
            self.habits_layout.insertWidget(insert_pos, spacer)
            insert_pos += 1

    def _on_habit_toggled(self, habit_id: int, completed: bool):
        self.db.set_completion(habit_id, self._today, completed)
        habits = self.db.get_habits()
        completions = self.db.get_today_completions(self._today)
        done = sum(1 for h in habits if completions.get(h["id"], False))
        self.ring.set_progress(done, len(habits))
        self.completion_changed.emit()

        if completed:
            try:
                import json, os
                cfg_path = os.path.expanduser("~/.mindful_path/config.json")
                sound_on = True
                try:
                    if os.path.exists(cfg_path):
                        with open(cfg_path) as f:
                            sound_on = json.load(f).get("sound_enabled", True)
                except (OSError, ValueError, KeyError):
                    sound_on = True
                if sound_on:
                    from sound import play_bell
                    play_bell()
            except Exception:
                pass
