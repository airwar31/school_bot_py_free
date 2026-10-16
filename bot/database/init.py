"""
Centralized Database Schema Initialization and Migrations.
"""

import logging
from bot.core.database import get_db_connection


def init_all_databases():
    """Initializes all SQLite tables in a unified safe transaction."""
    logging.info("Initializing complete database schema...")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                surname TEXT NOT NULL,
                patronymic TEXT NOT NULL,
                class TEXT NOT NULL,
                shift TEXT NOT NULL,
                phone TEXT NOT NULL,
                username TEXT,
                vk_notifications BOOLEAN DEFAULT 1,
                schedule_notifications BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Schedule Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedule (
                date TEXT PRIMARY KEY,
                first_shift_photo TEXT,
                second_shift_photo TEXT
            )
        """)

        # 3. Events Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 4. Feedback Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                feedback_type TEXT NOT NULL,
                message TEXT,
                rating INTEGER,
                status TEXT DEFAULT 'pending',
                admin_reply TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)

        # 5. Groups Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                chat_id INTEGER PRIMARY KEY,
                chat_type TEXT NOT NULL,
                chat_title TEXT,
                vk_notifications BOOLEAN DEFAULT 1,
                schedule_notifications BOOLEAN DEFAULT 1,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 6. Sent VK Posts Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sent_vk_posts (
                post_id INTEGER PRIMARY KEY,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Indexes for fast querying
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_dates ON events(start_date, end_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_class ON users(class, shift)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_status ON feedback(status)")

        conn.commit()

    logging.info("Database schema initialized successfully.")
