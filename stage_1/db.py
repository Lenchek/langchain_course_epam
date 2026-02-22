"""SQLite database for dynamic parking data (hours, prices, availability)."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from datetime import date, timedelta

from config import SQLITE_PATH, DATA_DIR
from data_gen import get_dynamic_fixture


def _ensure_data_dir():
    Path(SQLITE_PATH).parent.mkdir(parents=True, exist_ok=True)


def get_connection():
    _ensure_data_dir()
    return sqlite3.connect(SQLITE_PATH)


@contextmanager
def db_session():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create tables and seed with generated dynamic data."""
    with db_session() as conn:
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS working_hours (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day TEXT NOT NULL,
                open_time TEXT NOT NULL,
                close_time TEXT NOT NULL
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                space_type TEXT NOT NULL,
                first_hour REAL NOT NULL,
                next_hours REAL NOT NULL,
                day_max REAL NOT NULL
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS availability (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                space_id INTEGER NOT NULL,
                slot_date TEXT NOT NULL,
                hour_slot INTEGER NOT NULL,
                available INTEGER NOT NULL DEFAULT 1
            )
        """)

        # Seed if empty
        c.execute("SELECT COUNT(*) FROM working_hours")
        if c.fetchone()[0] == 0:
            fixture = get_dynamic_fixture()
            for row in fixture["working_hours"]:
                c.execute(
                    "INSERT INTO working_hours (day, open_time, close_time) VALUES (?, ?, ?)",
                    (row["day"], row["open"], row["close"]),
                )
            for row in fixture["prices"]:
                c.execute(
                    "INSERT INTO prices (space_type, first_hour, next_hours, day_max) VALUES (?, ?, ?, ?)",
                    (row["type"], row["first_hour"], row["next_hours"], row["day_max"]),
                )
            # Seed some availability for next 7 days, 24 hours each, sample spaces
            today = date.today()
            for space_id in range(1, 11):
                for d in range(7):
                    slot_date = (today + timedelta(days=d)).isoformat()
                    for hour in range(24):
                        c.execute(
                            "INSERT INTO availability (space_id, slot_date, hour_slot, available) VALUES (?, ?, ?, ?)",
                            (space_id, slot_date, hour, 1),
                        )


def get_working_hours():
    """Return list of dicts: day, open_time, close_time."""
    with db_session() as conn:
        c = conn.cursor()
        c.execute("SELECT day, open_time, close_time FROM working_hours ORDER BY id")
        return [{"day": r[0], "open": r[1], "close": r[2]} for r in c.fetchall()]


def get_prices():
    """Return list of dicts: space_type, first_hour, next_hours, day_max."""
    with db_session() as conn:
        c = conn.cursor()
        c.execute("SELECT space_type, first_hour, next_hours, day_max FROM prices")
        return [
            {"type": r[0], "first_hour": r[1], "next_hours": r[2], "day_max": r[3]}
            for r in c.fetchall()
        ]


def get_availability_summary(date_str: str):
    """Return counts of available vs total slots for a given date (YYYY-MM-DD)."""
    with db_session() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT COUNT(*) FROM availability WHERE slot_date = ? AND available = 1",
            (date_str,),
        )
        available = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM availability WHERE slot_date = ?", (date_str,))
        total = c.fetchone()[0]
        return {"available": available, "total": total, "date": date_str}


if __name__ == "__main__":
    init_db()
    print("SQLite DB initialized at", SQLITE_PATH)
    print("Working hours:", get_working_hours())
    print("Prices:", get_prices())
    print("Availability sample (today):", get_availability_summary(date.today().isoformat()))
