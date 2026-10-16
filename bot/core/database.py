"""
Database Connection Manager and SQLite WAL Concurrency Guard.
"""

import os
import time
import sqlite3
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'bot.db')


class DatabaseLock:
    """Provides file-based concurrency locking for SQLite operations."""
    LOCK_FILE = os.path.join(BASE_DIR, "db.lock")

    @classmethod
    def is_locked(cls) -> bool:
        return os.path.exists(cls.LOCK_FILE)

    @classmethod
    def set_lock(cls):
        try:
            with open(cls.LOCK_FILE, "w") as f:
                f.write("locked")
        except Exception as e:
            logging.error(f"Failed to create lock file: {e}")

    @classmethod
    def clear_lock(cls):
        try:
            if os.path.exists(cls.LOCK_FILE):
                os.remove(cls.LOCK_FILE)
        except Exception as e:
            logging.error(f"Failed to remove lock file: {e}")

    @classmethod
    def mark_initialized(cls):
        cls.clear_lock()


def get_db_connection() -> sqlite3.Connection:
    """
    Returns a configured SQLite connection with WAL mode and exponential retry on lock.
    """
    max_retries = 5
    os.makedirs(DATA_DIR, exist_ok=True)

    for attempt in range(max_retries):
        try:
            conn = sqlite3.connect(DB_PATH, timeout=30)
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA busy_timeout = 30000")
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                time.sleep(0.1 * (2 ** attempt))
                continue
            logging.error(f"Database connection failed: {e}")
            raise
        except Exception as e:
            logging.error(f"Error connecting to database: {e}")
            raise
