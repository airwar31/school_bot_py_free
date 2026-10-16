"""School events and calendar repository."""
import logging
import sqlite3
from bot.core.database import get_db_connection


def save_event(name: str, description: str, start_date: str, end_date: str, start_time: str, end_time: str) -> bool:
    try:
        with get_db_connection() as conn:
            conn.execute(
                'INSERT INTO events (name, description, start_date, end_date, start_time, end_time) VALUES (?, ?, ?, ?, ?, ?)',
                (name, description, start_date, end_date, start_time, end_time)
            )
            conn.commit()
        return True
    except sqlite3.Error as e:
        logging.error(f"Failed to save event: {e}")
        return False


def get_current_events():
    try:
        with get_db_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM events 
                WHERE 
                    datetime(end_date || ' ' || end_time) > datetime('now', 'localtime')
                    AND date(start_date) <= date('now', 'localtime', '+7 days')
                    AND date(start_date) >= date('now', 'localtime')
                ORDER BY date(start_date) ASC, time(start_time) ASC
            ''')
            return cursor.fetchall()
    except Exception as e:
        logging.error(f"Error getting current events: {e}")
        return []


def get_event(event_id: int):
    with get_db_connection() as conn:
        cursor = conn.execute('SELECT * FROM events WHERE id = ?', (event_id,))
        return cursor.fetchone()


def delete_event(event_id: int):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM events WHERE id = ?', (event_id,))
        conn.commit()
