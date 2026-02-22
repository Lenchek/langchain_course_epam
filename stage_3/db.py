"""SQLite: dynamic parking data + reservation requests (Stage 2) + used by Stage 3."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from datetime import date, timedelta, datetime

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
        c.execute("""
            CREATE TABLE IF NOT EXISTS reservation_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                surname TEXT NOT NULL,
                car_number TEXT NOT NULL,
                period_start TEXT NOT NULL,
                period_end TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                admin_comment TEXT,
                created_at TEXT NOT NULL,
                decided_at TEXT
            )
        """)

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
    with db_session() as conn:
        c = conn.cursor()
        c.execute("SELECT day, open_time, close_time FROM working_hours ORDER BY id")
        return [{"day": r[0], "open": r[1], "close": r[2]} for r in c.fetchall()]


def get_prices():
    with db_session() as conn:
        c = conn.cursor()
        c.execute("SELECT space_type, first_hour, next_hours, day_max FROM prices")
        return [{"type": r[0], "first_hour": r[1], "next_hours": r[2], "day_max": r[3]} for r in c.fetchall()]


def get_availability_summary(date_str: str):
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


def create_reservation_request(name: str, surname: str, car_number: str, period_start: str, period_end: str) -> int:
    with db_session() as conn:
        c = conn.cursor()
        c.execute(
            """INSERT INTO reservation_requests
               (name, surname, car_number, period_start, period_end, status, created_at)
               VALUES (?, ?, ?, ?, ?, 'pending', ?)""",
            (name, surname, car_number, period_start, period_end, datetime.utcnow().isoformat()),
        )
        return c.lastrowid


def get_pending_reservation_requests():
    with db_session() as conn:
        c = conn.cursor()
        c.execute(
            """SELECT id, name, surname, car_number, period_start, period_end, created_at
               FROM reservation_requests WHERE status = 'pending' ORDER BY created_at"""
        )
        return [
            {"id": r[0], "name": r[1], "surname": r[2], "car_number": r[3],
             "period_start": r[4], "period_end": r[5], "created_at": r[6]}
            for r in c.fetchall()
        ]


def set_reservation_status(request_id: int, status: str, admin_comment: str = None):
    if status not in ("approved", "refused"):
        raise ValueError("status must be 'approved' or 'refused'")
    with db_session() as conn:
        c = conn.cursor()
        c.execute(
            """UPDATE reservation_requests SET status = ?, admin_comment = ?, decided_at = ?
               WHERE id = ?""",
            (status, admin_comment or "", datetime.utcnow().isoformat(), request_id),
        )


def get_reservation_status(request_id: int):
    with db_session() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT status, admin_comment, period_start, period_end FROM reservation_requests WHERE id = ?",
            (request_id,),
        )
        row = c.fetchone()
        if not row:
            return None
        return {"status": row[0], "admin_comment": row[1] or "", "period_start": row[2], "period_end": row[3]}


if __name__ == "__main__":
    init_db()
    print("DB initialized at", SQLITE_PATH)
