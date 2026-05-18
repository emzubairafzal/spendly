import os
import sqlite3

from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "expense_tracker.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    UNIQUE NOT NULL,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id),
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            description TEXT,
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()
    row = conn.execute("SELECT COUNT(*) FROM users").fetchone()
    if row[0] > 0:
        conn.close()
        return

    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
    )
    conn.commit()
    user_id = conn.execute(
        "SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)
    ).fetchone()["id"]

    expenses = [
        (user_id, 45.50, "Food",          "2026-05-01", "Grocery shopping"),
        (user_id, 12.00, "Transport",     "2026-05-03", "Bus pass"),
        (user_id, 85.00, "Bills",         "2026-05-05", "Electricity bill"),
        (user_id, 30.00, "Health",        "2026-05-08", "Pharmacy"),
        (user_id, 15.99, "Entertainment", "2026-05-10", "Netflix subscription"),
        (user_id, 60.00, "Shopping",      "2026-05-12", "New shirt"),
        (user_id, 25.00, "Other",         "2026-05-14", "Miscellaneous"),
        (user_id, 22.75, "Food",          "2026-05-16", "Restaurant lunch"),
    ]
    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        expenses,
    )
    conn.commit()
    conn.close()
