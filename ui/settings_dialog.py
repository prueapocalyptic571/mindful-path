from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QCheckBox, QTimeEdit, QFrame, QWidget,
)
from PyQt6.QtCore import Qt, QTime


class SettingsDialog(QDialog):
    def __init__(self, notif_manager, parent=None):
        super().__init__(parent)
        self.nm = notif_manager
        self.setWindowTitle("Settings")
        self.setMinimumWidth(380)
        self.setModal(True)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 24)
        layout.setSpacing(20)

        title = QLabel("Settings")
        title.setObjectName("dialog_title")
        layout.addWidget(title)

        # ── Notifications ────────────────────────────────
        notif_lbl = QLabel("NOTIFICATIONS")
        notif_lbl.setStyleSheet(
            "color: #8a7a6a; font-size: 11px; font-weight: bold; letter-spacing: 2px;"
        )
        layout.addWidget(notif_lbl)

        card = QFrame()
        card.setObjectName("reflect_card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(18, 16, 18, 16)
        cl.setSpacing(14)

        self.enabled_cb = QCheckBox("Enable daily reminders")
        self.enabled_cb.setChecked(self.nm.enabled)
        cl.addWidget(self.enabled_cb)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #e8e0d0;")
        cl.addWidget(line)

        for label, attr, prop in [
            ("🌅  Morning reminder",   "_morning_edit",   self.nm.morning_time),
            ("☀    Afternoon reminder", "_afternoon_edit", self.nm.afternoon_time),
            ("🌙  Evening reminder",   "_evening_edit",   self.nm.evening_time),
        ]:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet("font-size: 13px;")
            row.addWidget(lbl, 1)
            te = QTimeEdit()
            te.setDisplayFormat("HH:mm")
            h, m = map(int, prop.split(":"))
            te.setTime(QTime(h, m))
            te.setFixedWidth(80)
            setattr(self, attr, te)
            row.addWidget(te)
            cl.addLayout(row)

        layout.addWidget(card)

        sub = QLabel(
            "Reminders appear as desktop notifications at the times above. "
            "They'll gently prompt you to check in with your practice."
        )
        sub.setWordWrap(True)
        sub.setStyleSheet("color: #8a7a6a; font-size: 11px;")
        layout.addWidget(sub)

        # ── Sound ────────────────────────────────────────
        sound_lbl = QLabel("COMPLETION SOUND")
        sound_lbl.setStyleSheet(
            "color: #8a7a6a; font-size: 11px; font-weight: bold; letter-spacing: 2px;"
        )
        layout.addWidget(sound_lbl)

        sound_card = QFrame()
        sound_card.setObjectName("reflect_card")
        sc = QVBoxLayout(sound_card)
        sc.setContentsMargins(18, 14, 18, 14)
        sc.setSpacing(10)

        self.sound_cb = QCheckBox("Play bell when a habit is completed")
        import json as _json, os as _os
        _cfg_path = _os.path.expanduser("~/.mindful_path/config.json")
        _cfg = {}
        if _os.path.exists(_cfg_path):
            try:
                with open(_cfg_path) as _f:
                    _cfg = _json.load(_f)
            except Exception:
                pass
        self.sound_cb.setChecked(_cfg.get("sound_enabled", True))
        sc.addWidget(self.sound_cb)

        test_row = QHBoxLayout()
        test_row.addStretch()
        test_btn = QPushButton("Test bell  🔔")
        test_btn.setObjectName("secondary_btn")
        test_btn.clicked.connect(self._test_sound)
        test_row.addWidget(test_btn)
        sc.addLayout(test_row)

        layout.addWidget(sound_card)

        # ── Buttons ──────────────────────────────────────
        btns = QHBoxLayout()
        btns.setSpacing(10)
        cancel = QPushButton("Cancel")
        cancel.setObjectName("secondary_btn")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Save Settings")
        save.clicked.connect(self._save)
        btns.addWidget(cancel)
        btns.addStretch()
        btns.addWidget(save)
        layout.addLayout(btns)

    def _test_sound(self):
        from sound import play_bell
        play_bell()

    def _save(self):
        import json as _json, os as _os
        _cfg_path = _os.path.expanduser("~/.mindful_path/config.json")
        self.nm.update_settings(
            self.enabled_cb.isChecked(),
            self._morning_edit.time().toString("HH:mm"),
            self._afternoon_edit.time().toString("HH:mm"),
            self._evening_edit.time().toString("HH:mm"),
        )
        _cfg = {}
        if _os.path.exists(_cfg_path):
            try:
                with open(_cfg_path) as _f:
                    _cfg = _json.load(_f)
            except Exception:
                pass
        _cfg["sound_enabled"] = self.sound_cb.isChecked()
        _os.makedirs(_os.path.dirname(_cfg_path), exist_ok=True)
        with open(_cfg_path, "w") as _f:
            _json.dump(_cfg, _f)
        self.accept()
