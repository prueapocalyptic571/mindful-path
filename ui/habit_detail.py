from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QFrame, QWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont
from datetime import date

from database import Database

CATEGORY_COLORS = {
    "Mind": "#7c9cbf", "Body": "#6ea87a", "Study": "#c8790a",
    "Heart": "#c86a7c", "Path": "#9c7cbc",
}
CATEGORY_ICONS = {
    "Mind": "◯", "Body": "◈", "Study": "◎", "Heart": "♡", "Path": "☸",
}


class MiniDots(QWidget):
    """7-day completion dots."""
    def __init__(self, days: list[bool], parent=None):
        super().__init__(parent)
        self._days = days
        self.setFixedSize(7 * 22 + 6, 22)

    def paintEvent(self, event):
        from PyQt6.QtWidgets import QApplication
        dark = QApplication.palette().window().color().lightness() < 128
        done_col  = QColor("#d4880f") if dark else QColor("#c8790a")
        empty_col = QColor("#3e3224") if dark else QColor("#e8e0d0")
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        for i, done in enumerate(self._days):
            p.setBrush(done_col if done else empty_col)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(i * 22 + 2, 2, 16, 16)


class StatRow(QWidget):
    def __init__(self, icon: str, label: str, value: str, color: str = "#c8790a", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"color: {color}; font-size: 15px;")
        icon_lbl.setFixedWidth(22)
        layout.addWidget(icon_lbl)

        key_lbl = QLabel(label)
        key_lbl.setStyleSheet("color: #8a7a6a; font-size: 12px;")
        layout.addWidget(key_lbl, 1)

        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f"color: {color}; font-size: 13px; font-weight: bold;")
        layout.addWidget(val_lbl)


class HabitDetailDialog(QDialog):
    completion_changed = pyqtSignal(int, bool)   # habit_id, completed

    def __init__(self, habit: dict, db: Database, date_str: str, completed: bool, parent=None):
        super().__init__(parent)
        self.habit = habit
        self.db = db
        self.date_str = date_str
        self._completed = completed
        self.setWindowTitle(habit["name"])
        self.setMinimumWidth(460)
        self.setModal(True)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 24)
        layout.setSpacing(18)

        # ── Header ──────────────────────────────────
        cat   = self.habit.get("category", "Mind")
        color = CATEGORY_COLORS.get(cat, "#888")
        icon  = CATEGORY_ICONS.get(cat, "●")

        header = QHBoxLayout()
        header.setSpacing(10)

        cat_badge = QLabel(f"{icon}  {cat}")
        cat_badge.setStyleSheet(
            f"background: {color}20; color: {color}; border: 1px solid {color}50;"
            f"border-radius: 10px; padding: 3px 10px; font-size: 11px; font-weight: bold;"
        )
        header.addWidget(cat_badge)
        header.addStretch()

        layout.addLayout(header)

        name_lbl = QLabel(self.habit["name"])
        name_font = QFont()
        name_font.setPixelSize(20)
        name_font.setBold(True)
        name_lbl.setFont(name_font)
        name_lbl.setWordWrap(True)
        layout.addWidget(name_lbl)

        if self.habit.get("description"):
            desc = QLabel(self.habit["description"])
            desc.setWordWrap(True)
            desc.setStyleSheet("color: #8a7a6a; font-size: 13px;")
            layout.addWidget(desc)

        if self.habit.get("eightfold_aspect"):
            asp = QLabel(f"↝   {self.habit['eightfold_aspect']}")
            asp.setStyleSheet("color: #a09080; font-size: 12px; font-style: italic;")
            layout.addWidget(asp)

        # ── Divider ──────────────────────────────────
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #e8e0d0;")
        layout.addWidget(line)

        # ── Stats ────────────────────────────────────
        streak  = self.db.get_streak(self.habit["id"])
        longest = self.db.get_longest_streak(self.habit["id"])
        rate    = self.db.get_completion_rate(self.habit["id"], 30)
        week    = self.db.get_weekly_completions(self.habit["id"])

        stats_frame = QFrame()
        stats_frame.setObjectName("reflect_card")
        sf_layout = QVBoxLayout(stats_frame)
        sf_layout.setContentsMargins(16, 14, 16, 14)
        sf_layout.setSpacing(10)

        sf_layout.addWidget(StatRow("🔥", "Current streak",  f"{streak} days",          "#d4880f"))
        sf_layout.addWidget(StatRow("⭐", "Longest streak",  f"{longest} days",         "#c8790a"))
        sf_layout.addWidget(StatRow("◈", "30-day completion", f"{int(rate * 100)}%",    "#6ea87a"))

        dots_row = QHBoxLayout()
        dots_row.setSpacing(8)
        dots_lbl = QLabel("Last 7 days")
        dots_lbl.setStyleSheet("color: #8a7a6a; font-size: 12px;")
        dots_row.addWidget(dots_lbl)
        dots_row.addWidget(MiniDots(week))
        dots_row.addStretch()
        sf_layout.addLayout(dots_row)

        layout.addWidget(stats_frame)

        # ── Note ─────────────────────────────────────
        note_lbl = QLabel("Note for today  (optional)")
        note_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #8a7a6a;")
        layout.addWidget(note_lbl)

        self.note_edit = QTextEdit()
        self.note_edit.setPlaceholderText("How did this practice feel? Any observations…")
        self.note_edit.setMaximumHeight(80)
        existing_note = self.db.get_completion_note(self.habit["id"], self.date_str)
        if existing_note:
            self.note_edit.setPlainText(existing_note)
        layout.addWidget(self.note_edit)

        # ── Buttons ───────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        close_btn = QPushButton("Close")
        close_btn.setObjectName("secondary_btn")
        close_btn.clicked.connect(self._save_and_close)

        self.toggle_btn = QPushButton()
        self._update_toggle_label()
        self.toggle_btn.clicked.connect(self._toggle)

        btn_row.addWidget(close_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.toggle_btn)
        layout.addLayout(btn_row)

    def _update_toggle_label(self):
        if self._completed:
            self.toggle_btn.setText("✓  Mark Incomplete")
            self.toggle_btn.setObjectName("secondary_btn")
            self.toggle_btn.style().unpolish(self.toggle_btn)
            self.toggle_btn.style().polish(self.toggle_btn)
        else:
            self.toggle_btn.setText("◉  Mark Complete")
            self.toggle_btn.setObjectName("")
            self.toggle_btn.style().unpolish(self.toggle_btn)
            self.toggle_btn.style().polish(self.toggle_btn)

    def _toggle(self):
        self._completed = not self._completed
        self.db.set_completion(self.habit["id"], self.date_str, self._completed)
        self._update_toggle_label()
        self.completion_changed.emit(self.habit["id"], self._completed)

    def _save_and_close(self):
        note = self.note_edit.toPlainText().strip()
        if note:
            self.db.save_completion_note(self.habit["id"], self.date_str, note)
        self.accept()

    def closeEvent(self, event):
        # Save note without calling accept() to avoid recursion
        note = self.note_edit.toPlainText().strip()
        if note:
            self.db.save_completion_note(self.habit["id"], self.date_str, note)
        super().closeEvent(event)
