"""User accounts repository."""
import logging
from bot.core.database import get_db_connection


def register_user(user_id: int, user_data: dict):
    try:
        with get_db_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO users (
                    user_id, name, surname, patronymic, class, shift, phone, username
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                user_data['name'],
                user_data['surname'],
                user_data['patronymic'],
                user_data['class'],
                user_data['shift'],
                user_data['phone'],
                user_data.get('username')
            ))
            conn.commit()
    except Exception as e:
        logging.error(f"Failed to register user {user_id}: {e}")
        raise


def get_user_profile(user_id: int):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except Exception as e:
        logging.error(f"Failed to fetch user {user_id}: {e}")
        return None


def update_user_field(user_id: int, field: str, value):
    try:
        with get_db_connection() as conn:
            conn.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (value, user_id))
            conn.commit()
    except Exception as e:
        logging.error(f"Failed to update user field {field}: {e}")
        raise


def get_all_users():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logging.error(f"Failed to fetch users: {e}")
        return []
