import sqlite3
from datetime import datetime
from pathlib import Path

DATABASE_NAME = Path(__file__).resolve().with_name("waste.db")

def _connect():
    connection = sqlite3.connect(DATABASE_NAME, timeout=10)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS waste (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            waste_text TEXT NOT NULL,
            category TEXT NOT NULL,
            confidence REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    return connection

def create_database():
    with _connect():
        pass

def add_waste(waste_text, category, confidence):
    with _connect() as connection:
        connection.execute(
            "INSERT INTO waste (waste_text, category, confidence, created_at) VALUES (?, ?, ?, ?)",
            (waste_text, category, float(confidence), datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S"))
        )

def get_statistics():
    with _connect() as connection:
        return connection.execute(
            "SELECT category, COUNT(*) FROM waste GROUP BY category ORDER BY COUNT(*) DESC"
        ).fetchall()

def get_history(limit=10):
    with _connect() as connection:
        return connection.execute(
            "SELECT waste_text, category, confidence, created_at FROM waste ORDER BY id DESC LIMIT ?",
            (int(limit),)
        ).fetchall()
