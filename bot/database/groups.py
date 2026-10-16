"""Group chat settings repository."""
import logging
from bot.core.database import get_db_connection


def add_group(chat_id: int, chat_type: str, chat_title: str = None):
    try:
        with get_db_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO groups (chat_id, chat_type, chat_title)
                VALUES (?, ?, ?)
            """, (chat_id, chat_type, chat_title))
            conn.commit()
    except Exception as e:
        logging.error(f"Failed to add group: {e}")


def remove_group(chat_id: int):
    try:
        with get_db_connection() as conn:
            conn.execute("DELETE FROM groups WHERE chat_id = ?", (chat_id,))
            conn.commit()
    except Exception as e:
        logging.error(f"Failed to remove group: {e}")


def get_all_groups():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM groups")
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logging.error(f"Failed to get groups: {e}")
        return []


def get_groups_with_vk_notifications():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT chat_id FROM groups WHERE vk_notifications = 1")
            return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        logging.error(f"Failed to get groups with VK notifications: {e}")
        return []


def get_groups_with_schedule_notifications():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT chat_id FROM groups WHERE schedule_notifications = 1")
            return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        logging.error(f"Failed to get groups with schedule notifications: {e}")
        return []


def toggle_group_vk_notifications(chat_id: int, enabled: bool):
    try:
        with get_db_connection() as conn:
            conn.execute("UPDATE groups SET vk_notifications = ? WHERE chat_id = ?", (enabled, chat_id))
            conn.commit()
            return True
    except Exception as e:
        logging.error(f"Failed to toggle VK notifications: {e}")
        return False


def get_group_settings(chat_id: int):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM groups WHERE chat_id = ?", (chat_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except Exception as e:
        logging.error(f"Failed to get group settings: {e}")
        return None
