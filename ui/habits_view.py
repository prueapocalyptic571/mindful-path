from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QDialog, QLineEdit, QTextEdit,
    QComboBox, QSpinBox, QFormLayout, QMessageBox, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from database import Database

CATEGORIES = ["Mind", "Body", "Study", "Heart", "Path"]
TIMES_OF_DAY = ["Morning", "Afternoon", "Evening", "Anytime"]
TIME_ICONS = {"Morning": "🌅", "Afternoon": "☀", "Evening": "🌙", "Anytime": "◦"}
EIGHTFOLD = [
    "Right View", "Right Intention", "Right Speech",
    "Right Action", "Right Livelihood", "Right Effort",
    "Right Mindfulness", "Right Concentration", "(None)",
]
PRIORITY_TEXT = {1: "Essential", 2: "Important", 3: "Gentle"}
PRIORITY_COLOR = {1: "#d05a20", 2: "#c8790a", 3: "#5c7a5c"}
CATEGORY_COLORS = {
    "Mind": "#7c9cbf", "Body": "#6ea87a", "Study": "#c8790a",
    "Heart": "#c86a7c", "Path": "#9c7cbc",
}


class HabitDialog(QDialog):
    def __init__(self, parent=None, habit: dict = None):
        super().__init__(parent)
        self.setWindowTitle("Edit Habit" if habit else "New Habit")
        self.setMinimumWidth(440)
        self.setModal(True)
        self._build(habit)

    def _build(self, habit):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Edit Your Practice" if habit else "Add to Your Practice")
        title.setObjectName("dialog_title")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g. Morning Meditation")
        if habit:
            self.name_edit.setText(habit.get("name", ""))
        form.addRow("Name", self.name_edit)

        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("A brief description of this practice…")
        self.desc_edit.setMaximumHeight(72)
        if habit:
            self.desc_edit.setPlainText(habit.get("description", ""))
        form.addRow("Description", self.desc_edit)

        self.category_box = QComboBox()
        self.category_box.addItems(CATEGORIES)
        if habit and habit.get("category") in CATEGORIES:
            self.category_box.setCurrentText(habit["category"])
        form.addRow("Category", self.category_box)

        self.priority_box = QComboBox()
        for v, t in PRIORITY_TEXT.items():
            self.priority_box.addItem(t, v)
        if habit:
            idx = habit.get("priority", 2) - 1
            self.priority_box.setCurrentIndex(max(0, idx))
        else:
            self.priority_box.setCurrentIndex(1)
        form.addRow("Priority", self.priority_box)

        self.aspect_box = QComboBox()
        self.aspect_box.addItems(EIGHTFOLD)
        if habit and habit.get("eightfold_aspect") in EIGHTFOLD:
            self.aspect_box.setCurrentText(habit["eightfold_aspect"])
        form.addRow("Path Aspect", self.aspect_box)

        self.time_box = QComboBox()
        for t in TIMES_OF_DAY:
            self.time_box.addItem(f"{TIME_ICONS[t]}  {t}", t)
        if habit and habit.get("time_of_day") in TIMES_OF_DAY:
            self.time_box.setCurrentText(f"{TIME_ICONS[habit['time_of_day']]}  {habit['time_of_day']}")
        form.addRow("Time of Day", self.time_box)

        layout.addLayout(form)

        # Buttons
        btns = QHBoxLayout()
        btns.setSpacing(10)
        cancel = QPushButton("Cancel")
        cancel.setObjectName("secondary_btn")
        cancel.clicked.connect(self.reject)

        save = QPushButton("Save Practice")
        save.clicked.connect(self._on_save)

        btns.addWidget(cancel)
        btns.addWidget(save)
        layout.addLayout(btns)

    def _on_save(self):
        if not self.name_edit.text().strip():
            self.name_edit.setFocus()
            return
        self.accept()

    def get_values(self) -> dict:
        aspect = self.aspect_box.currentText()
        if aspect == "(None)":
            aspect = ""
        return {
            "name": self.name_edit.text().strip(),
            "description": self.desc_edit.toPlainText().strip(),
            "category": self.category_box.currentText(),
            "priority": self.priority_box.currentData(),
            "eightfold_aspect": aspect,
            "time_of_day": self.time_box.currentData(),
        }


class HabitRow(QFrame):
    edit_requested = pyqtSignal(int)
    archive_requested = pyqtSignal(int)

    def __init__(self, habit: dict, parent=None):
        super().__init__(parent)
        self.habit_id = habit["id"]
        self.setObjectName("habit_row")
        self._build(habit)

    def _build(self, h: dict):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 13, 14, 13)
        layout.setSpacing(12)

        # Category dot
        cat = h.get("category", "Mind")
        color = CATEGORY_COLORS.get(cat, "#888")
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {color}; font-size: 16px;")
        dot.setFixedWidth(20)
        layout.addWidget(dot)

        info = QVBoxLayout()
        info.setSpacing(2)

        name = QLabel(h["name"])
        name_font = QFont()
        name_font.setPixelSize(14)
        name_font.setBold(True)
        name.setFont(name_font)
        info.addWidget(name)

        row2 = QHBoxLayout()
        row2.setSpacing(8)

        cat_badge = QLabel(cat)
        cat_badge.setStyleSheet(
            f"background: {color}20; color: {color}; border: 1px solid {color}50;"
            f"border-radius: 10px; padding: 2px 8px; font-size: 11px; font-weight: bold;"
        )
        row2.addWidget(cat_badge)

        sep = QLabel("·")
        sep.setStyleSheet("color: #c8b898; font-size: 12px;")
        row2.addWidget(sep)

        pri = h.get("priority", 2)
        pri_col = PRIORITY_COLOR.get(pri, "#c8790a")
        pri_lbl = QLabel(PRIORITY_TEXT.get(pri, "Important"))
        pri_lbl.setStyleSheet(f"color: {pri_col}; font-size: 11px;")
        row2.addWidget(pri_lbl)

        tod = h.get("time_of_day", "Anytime")
        tod_lbl = QLabel(f"{TIME_ICONS.get(tod,'◦')}  {tod}")
        tod_lbl.setStyleSheet("color: #8a7a6a; font-size: 11px;")
        row2.addWidget(tod_lbl)

        if h.get("eightfold_aspect"):
            sep2 = QLabel("·")
            sep2.setStyleSheet("color: #c8b898; font-size: 12px;")
            row2.addWidget(sep2)
            asp = QLabel(h["eightfold_aspect"])
            asp.setStyleSheet("color: #a09080; font-size: 11px; font-style: italic;")
            row2.addWidget(asp)

        row2.addStretch()
        info.addLayout(row2)
        layout.addLayout(info, 1)

        edit_btn = QPushButton("Edit")
        edit_btn.setObjectName("secondary_btn")
        edit_btn.setMinimumWidth(64)
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.habit_id))
        layout.addWidget(edit_btn)

        archive_btn = QPushButton("Archive")
        archive_btn.setObjectName("secondary_btn")
        archive_btn.setMinimumWidth(80)
        archive_btn.clicked.connect(lambda: self.archive_requested.emit(self.habit_id))
        layout.addWidget(archive_btn)


class HabitsView(QWidget):
    habits_changed = pyqtSignal()

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self._build_ui()
        self._load()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setObjectName("view_header")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(28, 20, 28, 20)

        title = QLabel("Your Practice")
        title.setObjectName("view_title")
        h_layout.addWidget(title, 1)

        add_btn = QPushButton("+ Add Practice")
        add_btn.setFixedWidth(140)
        add_btn.clicked.connect(self._add_habit)
        h_layout.addWidget(add_btn)

        layout.addWidget(header)

        sub = QLabel(
            "These are the daily practices that form your path. "
            "Add, shape, and refine them as you grow."
        )
        sub.setObjectName("view_sub")
        sub.setWordWrap(True)
        sub.setContentsMargins(28, 0, 28, 16)
        layout.addWidget(sub)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(scroll, 1)

        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(24, 0, 24, 24)
        self.list_layout.setSpacing(6)
        self.list_layout.addStretch()
        scroll.setWidget(self.list_container)

    def _load(self):
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        habits = self.db.get_habits()
        for i, h in enumerate(habits):
            row = HabitRow(h)
            row.edit_requested.connect(self._edit_habit)
            row.archive_requested.connect(self._archive_habit)
            self.list_layout.insertWidget(i, row)

        if not habits:
            empty = QLabel("No active practices. Add one above.")
            empty.setObjectName("empty_label")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_layout.insertWidget(0, empty)

    def _add_habit(self):
        dlg = HabitDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            v = dlg.get_values()
            self.db.add_habit(v["name"], v["description"], v["category"],
                              v["priority"], v["eightfold_aspect"], v["time_of_day"])
            self._load()
            self.habits_changed.emit()

    def _edit_habit(self, habit_id: int):
        habit = self.db.get_habit(habit_id)
        if not habit:
            return
        dlg = HabitDialog(self, habit)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            v = dlg.get_values()
            self.db.update_habit(habit_id, v["name"], v["description"],
                                 v["category"], v["priority"], v["eightfold_aspect"],
                                 v["time_of_day"])
            self._load()
            self.habits_changed.emit()

    def _archive_habit(self, habit_id: int):
        habit = self.db.get_habit(habit_id)
        name = habit["name"] if habit else "this practice"
        reply = QMessageBox.question(
            self, "Archive Practice",
            f'Archive "{name}"?\n\nIt will be hidden from your daily view, but its history is preserved.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.archive_habit(habit_id)
            self._load()
            self.habits_changed.emit()
