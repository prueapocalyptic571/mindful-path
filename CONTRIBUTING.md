# Contributing to Mindful Path

Thanks for your interest in contributing. This is a small, focused app — contributions that keep it simple and intentional are most welcome.

## What's welcome

- Bug fixes
- New habit suggestions (with good descriptions and an Eightfold Path mapping)
- UI improvements that stay within the existing aesthetic
- Translations / i18n groundwork
- Better bell sound generation
- Packaging improvements (Flatpak, AUR PKGBUILD)

## What to avoid

- Heavy new dependencies
- Features that add complexity without clear user value
- Breaking the local-only, no-account philosophy

## Setup

```bash
git clone https://github.com/yourusername/mindful-path.git
cd mindful-path
pip install PyQt6
python3 main.py
```

## Structure

```
mindful_path/
├── main.py              # Entry point
├── database.py          # SQLite interface
├── sound.py             # Bell sound generation/playback
├── generate_icon.py     # Generates app icons
├── mindful-path.sh      # Linux launcher script
├── ui/
│   ├── main_window.py   # Main window + sidebar + theme toggle
│   ├── today_view.py    # Daily habit checklist
│   ├── habits_view.py   # Habit management
│   ├── progress_view.py # Stats and streaks
│   ├── reflection_view.py  # Daily reflection journal
│   ├── about_view.py    # About + Buddhist principles
│   ├── habit_detail.py  # Per-habit detail dialog
│   ├── notifications.py # Desktop notification manager
│   └── settings_dialog.py  # Settings dialog
└── resources/
    ├── style.qss        # Light theme stylesheet
    └── dark.qss         # Dark theme stylesheet
```

## Submitting changes

1. Fork the repo
2. Create a branch: `git checkout -b my-change`
3. Make your changes
4. Test: `python3 main.py`
5. Open a pull request with a clear description
