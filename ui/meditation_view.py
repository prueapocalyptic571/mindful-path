"""Meditation timer with breathing guide, ambient audio, and spacebar gong."""
import math
import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QComboBox, QSizePolicy, QApplication,
)
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

from sound import play_bell

try:
    from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
    from PyQt6.QtCore import QUrl
    HAS_MULTIMEDIA = True
except ImportError:
    HAS_MULTIMEDIA = False

# Breathing cycle: (label, duration_seconds)
BREATH_PHASES = [
    ("Breathe In",  4),
    ("Hold",        4),
    ("Breathe Out", 4),
    ("Hold",        4),
]
BREATH_CYCLE = sum(d for _, d in BREATH_PHASES)

DURATIONS = [
    ("5 min",  5),
    ("10 min", 10),
    ("15 min", 15),
    ("20 min", 20),
    ("30 min", 30),
    ("45 min", 45),
    ("60 min", 60),
]


def _ease(t: float) -> float:
    """Smooth ease in-out cubic."""
    return t * t * (3.0 - 2.0 * t)


# ── Breathing Circle ───────────────────────────────────────────────────────

class BreathingCircle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(220, 220)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._session_elapsed = 0.0   # fractional seconds
        self._active = False
        self._phase_name = "Ready"

        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(50)          # 20 fps
        self._tick_timer.timeout.connect(self._tick)

    def start(self):
        self._active = True
        self._session_elapsed = 0.0
        self._tick_timer.start()
        self.update()

    def stop(self):
        self._active = False
        self._phase_name = "Ready"
        self._tick_timer.stop()
        self.update()

    def pause(self, paused: bool):
        if paused:
            self._tick_timer.stop()
        else:
            self._tick_timer.start()

    def _tick(self):
        self._session_elapsed += 0.05
        pos = self._session_elapsed % BREATH_CYCLE
        acc = 0
        for name, dur in BREATH_PHASES:
            acc += dur
            if pos < acc:
                self._phase_name = name
                break
        self.update()

    def _phase_radius_factor(self) -> float:
        """Returns 0.0–1.0 for current radius relative to max."""
        if not self._active:
            return 0.35
        pos = self._session_elapsed % BREATH_CYCLE
        acc = 0
        for name, dur in BREATH_PHASES:
            t = (pos - acc) / dur
            t = max(0.0, min(1.0, t))
            if pos < acc + dur:
                if name == "Breathe In":
                    return 0.35 + 0.65 * _ease(t)
                elif name == "Hold" and acc == 4:      # hold after in
                    return 1.0
                elif name == "Breathe Out":
                    return 1.0 - 0.65 * _ease(t)
                else:                                   # hold after out
                    return 0.35
            acc += dur
        return 0.35

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w / 2.0, h / 2.0
        max_r = min(w, h) / 2.0 - 16

        is_dark = QApplication.palette().window().color().lightness() < 128

        # Track ring
        track_col = QColor("#3e3224") if is_dark else QColor("#e8e0d0")
        painter.setPen(QPen(track_col, 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QRectF(cx - max_r, cy - max_r, max_r * 2, max_r * 2))

        # Breathing circle
        r = max_r * self._phase_radius_factor()
        if self._phase_name == "Breathe In":
            col = QColor("#c8790a")
        elif self._phase_name == "Breathe Out":
            col = QColor("#5c7a5c")
        elif self._active:
            col = QColor("#7a6a5a")
        else:
            col = QColor("#5a4a38") if is_dark else QColor("#c0b0a0")
        col.setAlpha(170)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(col)
        painter.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))

        # Phase label
        text_col = QColor("#e0d0b8") if is_dark else QColor("#2c2416")
        painter.setPen(text_col)
        font = QFont()
        font.setPointSize(13)
        font.setWeight(QFont.Weight.Medium)
        painter.setFont(font)
        painter.drawText(QRectF(0, cy - 14, w, 28), Qt.AlignmentFlag.AlignCenter, self._phase_name)

        painter.end()


# ── Meditation View ────────────────────────────────────────────────────────

class MeditationView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False
        self._paused = False
        self._elapsed = 0
        self._duration = 10 * 60
        self._ambient_path = None

        self._player = None
        self._audio_out = None
        if HAS_MULTIMEDIA:
            self._player = QMediaPlayer(self)
            self._audio_out = QAudioOutput(self)
            self._player.setAudioOutput(self._audio_out)
            self._audio_out.setVolume(0.5)
            self._player.mediaStatusChanged.connect(self._on_media_status)

        self._session_timer = QTimer(self)
        self._session_timer.setInterval(1000)
        self._session_timer.timeout.connect(self._tick)

        self._build_ui()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 32, 40, 32)
        layout.setSpacing(0)

        # Title
        title = QLabel("Meditate")
        title.setObjectName("view_title")
        layout.addWidget(title)
        layout.addSpacing(20)

        # Top controls row
        ctrl = QWidget()
        c_lay = QHBoxLayout(ctrl)
        c_lay.setContentsMargins(0, 0, 0, 0)
        c_lay.setSpacing(10)

        dur_label = QLabel("Duration:")
        c_lay.addWidget(dur_label)

        self._dur_combo = QComboBox()
        for label, mins in DURATIONS:
            self._dur_combo.addItem(label, mins)
        self._dur_combo.setCurrentIndex(1)
        self._dur_combo.currentIndexChanged.connect(self._on_duration_changed)
        c_lay.addWidget(self._dur_combo)
        c_lay.addStretch()

        if HAS_MULTIMEDIA:
            self._load_btn = QPushButton("♪  Load Ambient")
            self._load_btn.setObjectName("secondary_btn")
            self._load_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._load_btn.clicked.connect(self._load_ambient)
            c_lay.addWidget(self._load_btn)

        layout.addWidget(ctrl)
        layout.addSpacing(16)

        # Breathing circle
        self._circle = BreathingCircle()
        layout.addWidget(self._circle, 1)
        layout.addSpacing(12)

        # Timer
        self._timer_label = QLabel("10:00")
        self._timer_label.setObjectName("meditation_timer")
        self._timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._timer_label)
        layout.addSpacing(6)

        # Hint
        self._hint = QLabel("Press Space to ring gong")
        self._hint.setObjectName("meditation_hint")
        self._hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._hint)
        layout.addSpacing(20)

        # Buttons
        btn_row = QWidget()
        b_lay = QHBoxLayout(btn_row)
        b_lay.setContentsMargins(0, 0, 0, 0)
        b_lay.setSpacing(10)
        b_lay.addStretch()

        self._start_btn = QPushButton("▶  Begin Session")
        self._start_btn.setMinimumWidth(160)
        self._start_btn.setMinimumHeight(44)
        self._start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._start_btn.clicked.connect(self._toggle)
        b_lay.addWidget(self._start_btn)

        self._stop_btn = QPushButton("■  End Session")
        self._stop_btn.setObjectName("secondary_btn")
        self._stop_btn.setMinimumWidth(140)
        self._stop_btn.setMinimumHeight(44)
        self._stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._stop_btn.clicked.connect(self._stop)
        self._stop_btn.setVisible(False)
        b_lay.addWidget(self._stop_btn)

        b_lay.addStretch()
        layout.addWidget(btn_row)

        # Ambient file name
        if HAS_MULTIMEDIA:
            self._ambient_label = QLabel("No ambient sound loaded")
            self._ambient_label.setObjectName("meditation_hint")
            self._ambient_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addSpacing(8)
            layout.addWidget(self._ambient_label)

    # ── Controls ───────────────────────────────────────────────────────────

    def _toggle(self):
        if not self._running and not self._paused:
            self._begin()
        elif self._running:
            self._pause()
        else:
            self._resume()

    def _begin(self):
        mins = self._dur_combo.currentData()
        self._duration = mins * 60
        self._elapsed = 0
        self._running = True
        self._paused = False
        self._session_timer.start()
        self._circle.start()
        self._dur_combo.setEnabled(False)
        self._start_btn.setText("⏸  Pause")
        self._stop_btn.setVisible(True)
        if HAS_MULTIMEDIA:
            self._load_btn.setEnabled(False)
        self._update_display(self._duration)
        play_bell()
        self._start_ambient()

    def _pause(self):
        self._running = False
        self._paused = True
        self._session_timer.stop()
        self._circle.pause(True)
        self._start_btn.setText("▶  Resume")
        if self._player:
            self._player.pause()

    def _resume(self):
        self._running = True
        self._paused = False
        self._session_timer.start()
        self._circle.pause(False)
        self._start_btn.setText("⏸  Pause")
        if self._player and self._ambient_path:
            self._player.play()

    def _stop(self):
        self._running = False
        self._paused = False
        self._elapsed = 0
        self._session_timer.stop()
        self._circle.stop()
        self._dur_combo.setEnabled(True)
        self._start_btn.setText("▶  Begin Session")
        self._stop_btn.setVisible(False)
        if HAS_MULTIMEDIA:
            self._load_btn.setEnabled(True)
        mins = self._dur_combo.currentData()
        self._duration = mins * 60
        self._update_display(self._duration)
        if self._player:
            self._player.stop()

    def _tick(self):
        self._elapsed += 1
        remaining = self._duration - self._elapsed
        self._update_display(remaining)
        if remaining <= 0:
            self._complete()

    def _complete(self):
        play_bell()
        self._stop()
        self._hint.setText("Session complete. Well done.")
        QTimer.singleShot(4000, lambda: self._hint.setText("Press Space to ring gong"))

    def _update_display(self, seconds: int):
        m, s = divmod(max(0, seconds), 60)
        self._timer_label.setText(f"{m:02d}:{s:02d}")

    def _on_duration_changed(self):
        if not self._running and not self._paused:
            mins = self._dur_combo.currentData()
            self._duration = mins * 60
            self._update_display(self._duration)

    # ── Ambient audio ──────────────────────────────────────────────────────

    def _load_ambient(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Ambient Sound", os.path.expanduser("~"),
            "Audio Files (*.wav *.mp3 *.ogg *.flac)"
        )
        if path:
            self._ambient_path = path
            self._ambient_label.setText(f"♪  {os.path.basename(path)}")

    def _start_ambient(self):
        if self._player and self._ambient_path:
            self._player.setSource(QUrl.fromLocalFile(self._ambient_path))
            self._player.play()

    def _on_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia and self._running:
            self._player.setPosition(0)
            self._player.play()

    # ── Spacebar gong ──────────────────────────────────────────────────────

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            play_bell()
            event.accept()
        else:
            super().keyPressEvent(event)
