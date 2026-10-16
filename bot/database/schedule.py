"""Schedule and timetable repository."""
import logging
from bot.core.database import get_db_connection


def save_schedule(date: str, first_shift: str, second_shift: str = None) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM schedule WHERE date = ?', (date,))
        exists = cursor.fetchone() is not None
        cursor.execute(
            'INSERT OR REPLACE INTO schedule (date, first_shift_photo, second_shift_photo) VALUES (?, ?, ?)',
            (date, first_shift, second_shift)
        )
        conn.commit()
        return exists


def get_schedule(date: str):
    with get_db_connection() as conn:
        cursor = conn.execute(
            'SELECT first_shift_photo, second_shift_photo FROM schedule WHERE date = ?',
            (date,)
        )
        result = cursor.fetchone()
        return result if result else (None, None)


def delete_schedule(date: str):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM schedule WHERE date = ?', (date,))
        conn.commit()
