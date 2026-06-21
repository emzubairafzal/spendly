import sqlite3

import pytest
from werkzeug.security import generate_password_hash

import database.db as db_module
from app import app as flask_app


@pytest.fixture
def patched_db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setattr(db_module, "DB_PATH", db_path)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def seed_user(patched_db):
    conn = sqlite3.connect(patched_db)
    conn.execute(
        "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
        ("Demo User", "demo@spendly.com",
         generate_password_hash("demo123"), "2026-01-15 10:00:00"),
    )
    conn.commit()
    uid = conn.execute(
        "SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)
    ).fetchone()[0]
    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        [
            (uid, 45.50, "Food",          "2026-05-01", "Grocery shopping"),
            (uid, 12.00, "Transport",     "2026-05-03", "Bus pass"),
            (uid, 85.00, "Bills",         "2026-05-05", "Electricity bill"),
            (uid, 30.00, "Health",        "2026-05-08", "Pharmacy"),
            (uid, 15.99, "Entertainment", "2026-05-10", "Netflix subscription"),
            (uid, 60.00, "Shopping",      "2026-05-12", "New shirt"),
            (uid, 25.00, "Other",         "2026-05-14", "Miscellaneous"),
            (uid, 22.75, "Food",          "2026-05-16", "Restaurant lunch"),
        ],
    )
    conn.commit()
    conn.close()
    return uid


@pytest.fixture
def no_expense_user(patched_db):
    conn = sqlite3.connect(patched_db)
    conn.execute(
        "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
        ("Empty User", "empty@spendly.com",
         generate_password_hash("pass1234"), "2026-03-01 08:00:00"),
    )
    conn.commit()
    uid = conn.execute(
        "SELECT id FROM users WHERE email = ?", ("empty@spendly.com",)
    ).fetchone()[0]
    conn.close()
    return uid


@pytest.fixture
def client(patched_db):
    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret"
    with flask_app.test_client() as c:
        yield c


@pytest.fixture
def logged_in_client(client, seed_user):
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
    return client
