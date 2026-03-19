from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QScrollArea, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import date

from database import Database

MOODS = [
    ("☁", "Turbulent", "#a07060"),
    ("〜", "Unsettled", "#b08860"),
    ("◦", "Neutral", "#8a9a8a"),
    ("◌", "Content", "#6ea87a"),
    ("✦", "Peaceful", "#c8790a"),
]

PROMPTS_MORNING = [
    "What intention will guide your steps today?",
    "What quality do you wish to cultivate today?",
    "How will you show up with kindness today?",
    "What do you most want to bring into the world today?",
    "What would make today feel meaningful?",
]

PROMPTS_EVENING = [
    "Where did you find peace today?",
    "What arose that you can gently release?",
    "What moment brought you fully present?",
    "How did you grow or learn today?",
    "What are you ready to let go of as this day closes?",
]


class MoodSelector(QWidget):
    mood_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected = 3
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        self._buttons: list[QPushButton] = []

        for i, (icon, label, color) in enumerate(MOODS):
            btn = QPushButton(f"{icon}  {label}")
            btn.setCheckable(True)
            btn.setObjectName("mood_btn")
            btn.clicked.connect(lambda _, idx=i: self._select(idx))
            self._buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()
        self._select(2)  # default: Neutral

    def _select(self, idx: int):
        from PyQt6.QtWidgets import QApplication
        dark = QApplication.palette().window().color().lightness() < 128
        if dark:
            bg_default   = "#2a2318"
            text_default = "#8a7860"
            border_def   = "#4a3e2c"
            hover_bg     = "#342c1e"
        else:
            bg_default   = "#f0ebe0"
            text_default = "#8a7a6a"
            border_def   = "#d8d0c0"
            hover_bg     = "#e8e0d0"

        self._selected = idx + 1
        for i, (btn, (_, _, color)) in enumerate(zip(self._buttons, MOODS)):
            btn.setChecked(i == idx)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {bg_default}; color: {text_default};
                    border: 1px solid {border_def}; border-radius: 18px;
                    padding: 6px 14px; font-size: 12px;
                }}
                QPushButton:checked {{
                    background: {color}22; color: {color};
                    border: 1px solid {color};
                }}
                QPushButton:hover {{ background: {hover_bg}; }}
            """)
        self.mood_changed.emit(self._selected)

    def set_mood(self, mood: int):
        self._select(max(0, mood - 1))

    @property
    def value(self) -> int:
        return self._selected


class ReflectionView(QWidget):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self._today = date.today().isoformat()
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

        title = QLabel("Daily Reflection")
        title.setObjectName("view_title")
        h_layout.addWidget(title, 1)

        self.date_lbl = QLabel()
        self.date_lbl.setStyleSheet("color: #8a7a6a; font-size: 13px;")
        h_layout.addWidget(self.date_lbl)

        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(scroll, 1)

        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(28, 16, 28, 28)
        cl.setSpacing(20)
        scroll.setWidget(content)

        # ── Intention ──────────────────────────
        intention_card = QFrame()
        intention_card.setObjectName("reflect_card")
        ic_layout = QVBoxLayout(intention_card)
        ic_layout.setContentsMargins(20, 18, 20, 18)
        ic_layout.setSpacing(10)

        self.intent_prompt = QLabel()
        self.intent_prompt.setObjectName("reflect_prompt")
        self.intent_prompt.setWordWrap(True)
        ic_layout.addWidget(self.intent_prompt)

        self.intent_edit = QTextEdit()
        self.intent_edit.setPlaceholderText("Write your intention here…")
        self.intent_edit.setMaximumHeight(90)
        self.intent_edit.setObjectName("reflect_edit")
        ic_layout.addWidget(self.intent_edit)

        cl.addWidget(intention_card)

        # ── Evening ────────────────────────────
        evening_card = QFrame()
        evening_card.setObjectName("reflect_card")
        ec_layout = QVBoxLayout(evening_card)
        ec_layout.setContentsMargins(20, 18, 20, 18)
        ec_layout.setSpacing(10)

        self.eve_prompt = QLabel()
        self.eve_prompt.setObjectName("reflect_prompt")
        self.eve_prompt.setWordWrap(True)
        ec_layout.addWidget(self.eve_prompt)

        self.eve_edit = QTextEdit()
        self.eve_edit.setPlaceholderText("Reflect on your day with compassion…")
        self.eve_edit.setMinimumHeight(110)
        self.eve_edit.setObjectName("reflect_edit")
        ec_layout.addWidget(self.eve_edit)

        cl.addWidget(evening_card)

        # ── Gratitude ──────────────────────────
        grat_card = QFrame()
        grat_card.setObjectName("reflect_card")
        gc_layout = QVBoxLayout(grat_card)
        gc_layout.setContentsMargins(20, 18, 20, 18)
        gc_layout.setSpacing(10)

        grat_lbl = QLabel("✦  What are you grateful for today?")
        grat_lbl.setObjectName("reflect_prompt")
        gc_layout.addWidget(grat_lbl)

        self.grat_edit = QTextEdit()
        self.grat_edit.setPlaceholderText("Three things, however small, that brought light today…")
        self.grat_edit.setMaximumHeight(90)
        self.grat_edit.setObjectName("reflect_edit")
        gc_layout.addWidget(self.grat_edit)

        cl.addWidget(grat_card)

        # ── Mood ────────────────────────────────
        mood_card = QFrame()
        mood_card.setObjectName("reflect_card")
        mc_layout = QVBoxLayout(mood_card)
        mc_layout.setContentsMargins(20, 18, 20, 18)
        mc_layout.setSpacing(10)

        mood_lbl = QLabel("◯  How would you describe the quality of your mind today?")
        mood_lbl.setObjectName("reflect_prompt")
        mc_layout.addWidget(mood_lbl)

        self.mood_selector = MoodSelector()
        mc_layout.addWidget(self.mood_selector)

        cl.addWidget(mood_card)

        # ── Save ────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.save_btn = QPushButton("Save Reflection")
        self.save_btn.setFixedWidth(160)
        self.save_btn.clicked.connect(self._save)
        btn_row.addWidget(self.save_btn)

        self.saved_lbl = QLabel("Saved ✓")
        self.saved_lbl.setStyleSheet("color: #6ea87a; font-size: 13px;")
        self.saved_lbl.setVisible(False)
        btn_row.addWidget(self.saved_lbl)

        cl.addLayout(btn_row)
        cl.addStretch()

    def refresh(self):
        self._today = date.today().isoformat()
        d = date.today()
        self.date_lbl.setText(d.strftime("%A, %B %d"))

        # Prompts vary by day
        idx = d.timetuple().tm_yday
        self.intent_prompt.setText(f"☀  {PROMPTS_MORNING[idx % len(PROMPTS_MORNING)]}")
        self.eve_prompt.setText(f"🌙  {PROMPTS_EVENING[idx % len(PROMPTS_EVENING)]}")

        reflection = self.db.get_reflection(self._today)
        if reflection:
            self.intent_edit.setPlainText(reflection.get("morning_intention", ""))
            self.eve_edit.setPlainText(reflection.get("evening_reflection", ""))
            self.grat_edit.setPlainText(reflection.get("gratitude", ""))
            self.mood_selector.set_mood(reflection.get("mood", 3))
        else:
            self.intent_edit.clear()
            self.eve_edit.clear()
            self.grat_edit.clear()
            self.mood_selector.set_mood(3)

        self.saved_lbl.setVisible(False)

    def _save(self):
        self.db.save_reflection(
            self._today,
            self.intent_edit.toPlainText().strip(),
            self.eve_edit.toPlainText().strip(),
            self.grat_edit.toPlainText().strip(),
            self.mood_selector.value,
        )
        self.saved_lbl.setVisible(True)
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2500, lambda: self.saved_lbl.setVisible(False))
