import sqlite3
from pathlib import Path
from backend.config import config

DB_PATH = Path(config.DB_PATH)


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    UNIQUE NOT NULL,
            password_hash TEXT    NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER,
            user_name  TEXT NOT NULL,
            user_email TEXT,
            date       TEXT NOT NULL,
            time       TEXT NOT NULL,
            reason     TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Safe migrations for existing databases ────────────────────────────────
    user_cols  = [r[1] for r in cur.execute("PRAGMA table_info(users)").fetchall()]
    appt_cols  = [r[1] for r in cur.execute("PRAGMA table_info(appointments)").fetchall()]

    if "password_hash" not in user_cols:
        cur.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
    if "user_id" not in appt_cols:
        cur.execute("ALTER TABLE appointments ADD COLUMN user_id INTEGER")

    conn.commit()
    conn.close()
