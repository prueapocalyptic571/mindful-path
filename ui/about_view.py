from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame,
)
from PyQt6.QtCore import Qt

PATH_ASPECTS = [
    ("Right View", "◉", "See clearly — understand how things truly are, without distortion or delusion. For students: approach your work and yourself with honesty and curiosity."),
    ("Right Intention", "◎", "Cultivate wholesome motivation. Study not to impress, but to genuinely understand. Act from kindness and compassion, not fear."),
    ("Right Speech", "◯", "Speak truthfully and kindly. In study groups, with professors, with yourself — words shape reality."),
    ("Right Action", "◈", "Act ethically and with care. Honor your body, your commitments, and those around you."),
    ("Right Livelihood", "◇", "Engage in work that doesn't harm others. Find meaning in what you study — connect your efforts to something larger."),
    ("Right Effort", "◆", "Cultivate consistent, balanced effort — not frantic bursts or lazy drifting. The Middle Way between burnout and avoidance."),
    ("Right Mindfulness", "✦", "Bring full, non-judgmental awareness to each moment — while studying, eating, resting. The mind that is present learns deeply."),
    ("Right Concentration", "☸", "Develop the capacity for sustained, deep focus. A calm, steady mind is the ground of all wisdom."),
]

PRINCIPLES = [
    ("Impermanence (Anicca)", "◦",
     "Everything changes — including your struggles, your grades, your mood. A missed day is not a broken self. Each morning is a fresh beginning."),
    ("The Middle Way", "〜",
     "Avoid extremes. Neither punishing perfectionism nor aimless drift — but a balanced, sustainable path of gentle consistency."),
    ("Non-Attachment", "◌",
     "Do the practice for its own sake, not for the outcome. Effort without clinging to results frees you from anxiety and deepens your learning."),
    ("Self-Compassion (Metta)", "♡",
     "Offer yourself the same kindness you would offer a dear friend. Criticism and guilt are poor teachers. Warmth and honesty are better ones."),
    ("Mindfulness", "☯",
     "The quality of full presence — awake to this moment, this breath, this page. It is both a practice and a way of being."),
    ("Interconnection", "∞",
     "You are not separate from those around you. Your growth ripples outward. Your struggles are shared by countless others on the same path."),
]


class AboutView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setObjectName("view_header")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(28, 20, 28, 20)
        title = QLabel("About")
        title.setObjectName("view_title")
        h_layout.addWidget(title)
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(scroll, 1)

        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(28, 16, 28, 40)
        cl.setSpacing(24)
        scroll.setWidget(content)

        # ── Intro ──────────────────────────────────
        intro = QFrame()
        intro.setObjectName("reflect_card")
        il = QVBoxLayout(intro)
        il.setContentsMargins(24, 22, 24, 22)
        il.setSpacing(10)

        wheel = QLabel("☸")
        wheel.setStyleSheet("font-size: 36px; color: #c8790a;")
        wheel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        il.addWidget(wheel)

        app_name = QLabel("Mindful Path")
        app_name.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c2416;")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        il.addWidget(app_name)

        tagline = QLabel("A Daily Practice Tracker for Students")
        tagline.setStyleSheet("font-size: 13px; color: #8a7a6a;")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        il.addWidget(tagline)

        desc = QLabel(
            "Mindful Path helps you build a daily practice rooted in balance, "
            "awareness, and compassion. Inspired by Buddhist wisdom — without dogma "
            "or religion — it offers a gentle framework for the habits that support "
            "a student's deepest flourishing: mind, body, study, and heart.\n\n"
            "There are no penalties for missed days. Impermanence is built in. "
            "Each morning, the path begins again."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #4a3a2a; font-size: 13px; line-height: 1.6;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        il.addWidget(desc)

        cl.addWidget(intro)

        # ── Eightfold Path ────────────────────────
        section = QLabel("THE NOBLE EIGHTFOLD PATH")
        section.setStyleSheet(
            "color: #8a7a6a; font-size: 11px; font-weight: bold; letter-spacing: 2px;"
        )
        cl.addWidget(section)

        sub = QLabel(
            "The Eightfold Path is not a checklist — it is eight facets of a single "
            "jewel, developed together. Each practice in Mindful Path is linked to one "
            "of these aspects as a gentle reminder of the deeper intention behind your habits."
        )
        sub.setWordWrap(True)
        sub.setStyleSheet("color: #6a5a4a; font-size: 12px;")
        cl.addWidget(sub)

        for name, icon, desc_text in PATH_ASPECTS:
            card = QFrame()
            card.setObjectName("habit_row")
            c_layout = QHBoxLayout(card)
            c_layout.setContentsMargins(16, 12, 16, 12)
            c_layout.setSpacing(14)

            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("color: #c8790a; font-size: 18px;")
            icon_lbl.setFixedWidth(24)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignTop)
            c_layout.addWidget(icon_lbl)

            text_col = QVBoxLayout()
            text_col.setSpacing(3)
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet("font-weight: bold; font-size: 13px; color: #2c2416;")
            text_col.addWidget(name_lbl)
            desc_lbl = QLabel(desc_text)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet("color: #6a5a4a; font-size: 12px;")
            text_col.addWidget(desc_lbl)
            c_layout.addLayout(text_col, 1)

            cl.addWidget(card)

        # ── Core Principles ────────────────────────
        section2 = QLabel("CORE PRINCIPLES")
        section2.setStyleSheet(
            "color: #8a7a6a; font-size: 11px; font-weight: bold; letter-spacing: 2px;"
        )
        section2.setContentsMargins(0, 8, 0, 0)
        cl.addWidget(section2)

        for name, icon, desc_text in PRINCIPLES:
            card = QFrame()
            card.setObjectName("habit_row")
            c_layout = QHBoxLayout(card)
            c_layout.setContentsMargins(16, 12, 16, 12)
            c_layout.setSpacing(14)

            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("color: #9c7cbc; font-size: 18px;")
            icon_lbl.setFixedWidth(24)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignTop)
            c_layout.addWidget(icon_lbl)

            text_col = QVBoxLayout()
            text_col.setSpacing(3)
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet("font-weight: bold; font-size: 13px; color: #2c2416;")
            text_col.addWidget(name_lbl)
            desc_lbl = QLabel(desc_text)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet("color: #6a5a4a; font-size: 12px;")
            text_col.addWidget(desc_lbl)
            c_layout.addLayout(text_col, 1)

            cl.addWidget(card)

        # ── Categories ────────────────────────────
        section3 = QLabel("PRACTICE CATEGORIES")
        section3.setStyleSheet(
            "color: #8a7a6a; font-size: 11px; font-weight: bold; letter-spacing: 2px;"
        )
        section3.setContentsMargins(0, 8, 0, 0)
        cl.addWidget(section3)

        categories = [
            ("Mind", "◯", "#7c9cbf", "Meditation, awareness, and presence practices. The ground of clear seeing."),
            ("Body", "◈", "#6ea87a", "Movement, nourishment, rest. The vessel must be cared for."),
            ("Study", "◎", "#c8790a", "Deep learning, focused effort, and the joy of understanding."),
            ("Heart", "♡", "#c86a7c", "Gratitude, kindness, connection. The practices that keep us human."),
            ("Path", "☸", "#9c7cbc", "Intention, reflection, and alignment with your deepest values."),
        ]
        for cat, icon, color, desc_text in categories:
            card = QFrame()
            card.setObjectName("habit_row")
            c_layout = QHBoxLayout(card)
            c_layout.setContentsMargins(16, 10, 16, 10)
            c_layout.setSpacing(14)

            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet(f"color: {color}; font-size: 16px;")
            icon_lbl.setFixedWidth(24)
            c_layout.addWidget(icon_lbl)

            name_lbl = QLabel(f"<b>{cat}</b> — {desc_text}")
            name_lbl.setStyleSheet("color: #4a3a2a; font-size: 12px;")
            name_lbl.setWordWrap(True)
            c_layout.addWidget(name_lbl, 1)

            cl.addWidget(card)

        cl.addStretch()
