import sqlite3
import os
from datetime import date, timedelta
from typing import List, Optional, Dict


class Database:
    def __init__(self):
        data_dir = os.path.expanduser("~/.mindful_path")
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, "tracker.db")
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")

    def initialize(self):
        self.connect()
        c = self.conn.cursor()
        c.executescript("""
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                category TEXT DEFAULT 'Mind',
                priority INTEGER DEFAULT 2,
                eightfold_aspect TEXT DEFAULT '',
                time_of_day TEXT DEFAULT 'Anytime',
                active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS daily_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER REFERENCES habits(id) ON DELETE CASCADE,
                date TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                completed_at TEXT,
                notes TEXT,
                UNIQUE(habit_id, date)
            );

            CREATE TABLE IF NOT EXISTS daily_reflections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                morning_intention TEXT DEFAULT '',
                evening_reflection TEXT DEFAULT '',
                gratitude TEXT DEFAULT '',
                mood INTEGER DEFAULT 3,
                updated_at TEXT DEFAULT (datetime('now'))
            );
        """)

        # Migrate: add time_of_day column if it doesn't exist yet
        cols = [r[1] for r in c.execute("PRAGMA table_info(habits)").fetchall()]
        if "time_of_day" not in cols:
            c.execute("ALTER TABLE habits ADD COLUMN time_of_day TEXT DEFAULT 'Anytime'")
            self._assign_default_times(c)

        # Migrate: add notes column to completions if missing
        cols2 = [r[1] for r in c.execute("PRAGMA table_info(daily_completions)").fetchall()]
        if "notes" not in cols2:
            c.execute("ALTER TABLE daily_completions ADD COLUMN notes TEXT")

        c.execute("SELECT COUNT(*) FROM habits")
        if c.fetchone()[0] == 0:
            self._insert_default_habits(c)
        else:
            self._add_new_habits(c)

        self.conn.commit()

    # time_of_day defaults for known habit names
    _TIME_MAP = {
        "Morning Meditation":        "Morning",
        "Mindful Breathing":         "Morning",
        "Phone-Free Morning":        "Morning",
        "Eat Before You Study":      "Morning",
        "Tidy Your Space":           "Morning",
        "Set Daily Intention":       "Morning",
        "Physical Movement":         "Morning",
        "Healthy Breakfast":         "Morning",
        "Deep Study Session":        "Afternoon",
        "Self-Testing":              "Afternoon",
        "Ask for Help":              "Afternoon",
        "Weekly Planning":           "Afternoon",
        "Weekly Review":             "Afternoon",
        "Review & Consolidate Notes":"Evening",
        "Gratitude Practice":        "Evening",
        "Evening Reflection":        "Evening",
        "Plan Tomorrow Tonight":     "Evening",
        "Restful Sleep":             "Evening",
    }

    def _assign_default_times(self, c):
        """Set time_of_day for existing habits where we have a sensible default."""
        for name, tod in self._TIME_MAP.items():
            c.execute(
                "UPDATE habits SET time_of_day = ? WHERE name = ? AND time_of_day = 'Anytime'",
                (tod, name),
            )

    def _insert_default_habits(self, c):
        defaults = [
            # (name, description, category, priority, eightfold_aspect, time_of_day)
            ("Morning Meditation", "Sit quietly and observe the breath for 10 minutes", "Mind", 1, "Right Mindfulness", "Morning"),
            ("Mindful Breathing", "Take three conscious breaths before beginning each task", "Mind", 2, "Right Mindfulness", "Morning"),
            ("Digital Detox", "One hour fully away from screens — be completely present", "Mind", 2, "Right Concentration", "Anytime"),
            ("Physical Movement", "30 minutes of exercise, yoga, or mindful walking", "Body", 1, "Right Action", "Morning"),
            ("Nourishing Meal", "Eat at least one meal with full awareness, no screens", "Body", 2, "Right Action", "Anytime"),
            ("Hydration", "Drink 8 glasses of water throughout the day", "Body", 3, "Right Action", "Anytime"),
            ("Restful Sleep", "Sleep 7–8 hours — a clear mind is the foundation of practice", "Body", 1, "Right Effort", "Evening"),
            ("Deep Study Session", "90 minutes of focused, distraction-free study", "Study", 1, "Right Concentration", "Afternoon"),
            ("Review & Consolidate Notes", "Reflect on and organize what you learned today", "Study", 2, "Right Effort", "Evening"),
            ("Inspired Reading", "Read something that expands your understanding of the world", "Study", 3, "Right View", "Anytime"),
            ("Gratitude Practice", "Note three things you are genuinely grateful for", "Heart", 1, "Right Intention", "Evening"),
            ("Act of Kindness", "Do one kind thing for another person today", "Heart", 2, "Right Action", "Anytime"),
            ("Connect with Someone", "Share meaningful time with a friend or family member", "Heart", 3, "Right Speech", "Anytime"),
            ("Set Daily Intention", "Begin your day with a clear and compassionate purpose", "Path", 1, "Right Intention", "Morning"),
            ("Evening Reflection", "Review your day with honesty and self-compassion", "Path", 1, "Right View", "Evening"),
        ]
        c.executemany(
            "INSERT INTO habits (name, description, category, priority, eightfold_aspect, time_of_day) VALUES (?,?,?,?,?,?)",
            defaults,
        )

    def _add_new_habits(self, c):
        """Insert habits that don't already exist (by name). Safe to run on every launch."""
        new_habits = [
            # (name, description, category, priority, eightfold_aspect, time_of_day)
            ("Self-Testing", "Quiz yourself without looking at notes. Retrieval is stronger than rereading.", "Study", 1, "Right Effort", "Afternoon"),
            ("Phone-Free Morning", "Keep the first 30 minutes screen-free. Protect your attention before the day demands it.", "Mind", 2, "Right Concentration", "Morning"),
            ("Tidy Your Space", "Spend 5 minutes clearing your study area. A calm environment supports a calm mind.", "Mind", 3, "Right Mindfulness", "Morning"),
            ("Eat Before You Study", "A nourishing meal or snack before studying boosts recall and sustained focus.", "Body", 2, "Right Action", "Morning"),
            ("Weekly Planning", "Each week, set clear intentions: what will I learn, complete, and let go of?", "Path", 2, "Right Intention", "Afternoon"),
            ("Ask for Help", "Reach out to a professor, tutor, or peer when stuck. Seeking help is wisdom, not weakness.", "Heart", 2, "Right Speech", "Anytime"),
            ("Weekly Review", "Look back at the week: what did I understand deeply? What gaps remain?", "Study", 2, "Right View", "Afternoon"),
            ("Plan Tomorrow Tonight", "Before bed, write your top 3 intentions for tomorrow. Begin each day with direction.", "Path", 3, "Right Effort", "Evening"),
        ]
        inserted_any = False
        for habit in new_habits:
            c.execute("SELECT id FROM habits WHERE name = ?", (habit[0],))
            if not c.fetchone():
                c.execute(
                    "INSERT INTO habits (name, description, category, priority, eightfold_aspect, time_of_day) VALUES (?,?,?,?,?,?)",
                    habit,
                )
                inserted_any = True
        # Only run time migration when we actually inserted something new,
        # or if habits with 'Anytime' exist that have a known mapping
        if inserted_any:
            self._assign_default_times(c)
        else:
            # Lightweight guard: only update if any habits still have 'Anytime'
            # and match a name in _TIME_MAP (idempotent since WHERE filters them)
            c.execute(
                "SELECT 1 FROM habits WHERE time_of_day = 'Anytime' AND name IN ({})".format(
                    ",".join("?" * len(self._TIME_MAP))
                ),
                list(self._TIME_MAP.keys()),
            )
            if c.fetchone():
                self._assign_default_times(c)

    # ── Habit CRUD ─────────────────────────────────────────────────────────

    def get_habits(self, active_only: bool = True) -> List[Dict]:
        q = "SELECT * FROM habits"
        q += " WHERE active = 1" if active_only else ""
        q += " ORDER BY priority, category, name"
        return [dict(r) for r in self.conn.execute(q).fetchall()]

    def get_habit(self, habit_id: int) -> Optional[Dict]:
        row = self.conn.execute("SELECT * FROM habits WHERE id = ?", (habit_id,)).fetchone()
        return dict(row) if row else None

    def add_habit(self, name: str, description: str, category: str, priority: int,
                  eightfold_aspect: str, time_of_day: str = "Anytime") -> int:
        c = self.conn.execute(
            "INSERT INTO habits (name, description, category, priority, eightfold_aspect, time_of_day) VALUES (?,?,?,?,?,?)",
            (name, description, category, priority, eightfold_aspect, time_of_day),
        )
        self.conn.commit()
        return c.lastrowid

    def update_habit(self, habit_id: int, name: str, description: str, category: str,
                     priority: int, eightfold_aspect: str, time_of_day: str = "Anytime"):
        self.conn.execute(
            "UPDATE habits SET name=?, description=?, category=?, priority=?, eightfold_aspect=?, time_of_day=? WHERE id=?",
            (name, description, category, priority, eightfold_aspect, time_of_day, habit_id),
        )
        self.conn.commit()

    def archive_habit(self, habit_id: int):
        self.conn.execute("UPDATE habits SET active = 0 WHERE id = ?", (habit_id,))
        self.conn.commit()

    def delete_habit(self, habit_id: int):
        self.conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        self.conn.commit()

    # ── Completions ────────────────────────────────────────────────────────

    def get_completion(self, habit_id: int, date_str: str) -> bool:
        row = self.conn.execute(
            "SELECT completed FROM daily_completions WHERE habit_id=? AND date=?",
            (habit_id, date_str),
        ).fetchone()
        return bool(row["completed"]) if row else False

    def set_completion(self, habit_id: int, date_str: str, completed: bool, note: str = None):
        self.conn.execute(
            """INSERT INTO daily_completions (habit_id, date, completed, completed_at, notes)
               VALUES (?, ?, ?, CASE WHEN ? THEN datetime('now') ELSE NULL END, ?)
               ON CONFLICT(habit_id, date) DO UPDATE SET
                 completed = excluded.completed,
                 completed_at = excluded.completed_at,
                 notes = COALESCE(excluded.notes, notes)""",
            (habit_id, date_str, int(completed), int(completed), note),
        )
        self.conn.commit()

    def get_completion_note(self, habit_id: int, date_str: str) -> str:
        row = self.conn.execute(
            "SELECT notes FROM daily_completions WHERE habit_id=? AND date=?",
            (habit_id, date_str),
        ).fetchone()
        return (row["notes"] or "") if row else ""

    def save_completion_note(self, habit_id: int, date_str: str, note: str):
        self.conn.execute(
            """INSERT INTO daily_completions (habit_id, date, completed, notes)
               VALUES (?, ?, 0, ?)
               ON CONFLICT(habit_id, date) DO UPDATE SET notes = excluded.notes""",
            (habit_id, date_str, note),
        )
        self.conn.commit()

    def get_today_completions(self, date_str: str) -> Dict[int, bool]:
        rows = self.conn.execute(
            "SELECT habit_id, completed FROM daily_completions WHERE date=?", (date_str,)
        ).fetchall()
        return {r["habit_id"]: bool(r["completed"]) for r in rows}

    def get_weekly_completions(self, habit_id: int) -> List[bool]:
        result = []
        for i in range(6, -1, -1):
            d = (date.today() - timedelta(days=i)).isoformat()
            result.append(self.get_completion(habit_id, d))
        return result

    # ── Streaks ────────────────────────────────────────────────────────────

    def get_streak(self, habit_id: int) -> int:
        today = date.today()
        yesterday = today - timedelta(days=1)
        rows = self.conn.execute(
            "SELECT date FROM daily_completions WHERE habit_id=? AND completed=1 ORDER BY date DESC",
            (habit_id,),
        ).fetchall()
        dates = [date.fromisoformat(r["date"]) for r in rows]
        if not dates:
            return 0
        if dates[0] not in (today, yesterday):
            return 0
        streak = 0
        current = dates[0]
        for d in dates:
            if d == current:
                streak += 1
                current -= timedelta(days=1)
            else:
                break
        return streak

    def get_longest_streak(self, habit_id: int) -> int:
        rows = self.conn.execute(
            "SELECT date FROM daily_completions WHERE habit_id=? AND completed=1 ORDER BY date ASC",
            (habit_id,),
        ).fetchall()
        dates = [date.fromisoformat(r["date"]) for r in rows]
        if not dates:
            return 0
        best = cur = 1
        for i in range(1, len(dates)):
            if dates[i] == dates[i - 1] + timedelta(days=1):
                cur += 1
                best = max(best, cur)
            else:
                cur = 1
        return best

    def get_completion_rate(self, habit_id: int, days: int = 30) -> float:
        row = self.conn.execute(
            """SELECT COUNT(*) as total, SUM(completed) as done
               FROM daily_completions
               WHERE habit_id=? AND date >= date('now', ?)""",
            (habit_id, f"-{days} days"),
        ).fetchone()
        if not row or not row["total"]:
            return 0.0
        return (row["done"] or 0) / row["total"]

    # ── Daily stats ────────────────────────────────────────────────────────

    def get_daily_totals(self, days: int = 30) -> Dict[str, int]:
        """Returns {date_str: completed_count} for last N days."""
        rows = self.conn.execute(
            """SELECT date, SUM(completed) as cnt
               FROM daily_completions
               WHERE date >= date('now', ?)
               GROUP BY date""",
            (f"-{days} days",),
        ).fetchall()
        return {r["date"]: r["cnt"] for r in rows}

    # ── Reflection ─────────────────────────────────────────────────────────

    def get_reflection(self, date_str: str) -> Optional[Dict]:
        row = self.conn.execute(
            "SELECT * FROM daily_reflections WHERE date=?", (date_str,)
        ).fetchone()
        return dict(row) if row else None

    def save_reflection(self, date_str: str, morning_intention: str,
                        evening_reflection: str, gratitude: str, mood: int):
        self.conn.execute(
            """INSERT INTO daily_reflections
                 (date, morning_intention, evening_reflection, gratitude, mood, updated_at)
               VALUES (?,?,?,?,?, datetime('now'))
               ON CONFLICT(date) DO UPDATE SET
                 morning_intention=excluded.morning_intention,
                 evening_reflection=excluded.evening_reflection,
                 gratitude=excluded.gratitude,
                 mood=excluded.mood,
                 updated_at=excluded.updated_at""",
            (date_str, morning_intention, evening_reflection, gratitude, mood),
        )
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
