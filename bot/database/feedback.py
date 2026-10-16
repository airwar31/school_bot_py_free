"""Feedback and support ticket repository."""
import logging
from bot.core.database import get_db_connection


def create_feedback(user_id: int, feedback_type: str, message: str = None, rating: int = None) -> int:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO feedback (user_id, feedback_type, message, rating)
                VALUES (?, ?, ?, ?)
            """, (user_id, feedback_type, message, rating))
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        logging.error(f"Failed to create feedback: {e}")
        raise


def get_feedback_list(feedback_type: str = None, limit: int = 10) -> list:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if feedback_type:
                cursor.execute("""
                    SELECT f.*, u.name, u.surname, u.class
                    FROM feedback f
                    LEFT JOIN users u ON f.user_id = u.user_id
                    WHERE f.feedback_type = ? AND f.status = 'pending'
                    ORDER BY f.created_at DESC
                    LIMIT ?
                """, (feedback_type, limit))
            else:
                cursor.execute("""
                    SELECT f.*, u.name, u.surname, u.class
                    FROM feedback f
                    LEFT JOIN users u ON f.user_id = u.user_id
                    WHERE f.status = 'pending'
                    ORDER BY f.created_at DESC
                    LIMIT ?
                """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logging.error(f"Failed to get feedback list: {e}")
        return []


def get_feedback_by_id(feedback_id: int):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT f.*, u.name, u.surname, u.class
                FROM feedback f
                LEFT JOIN users u ON f.user_id = u.user_id
                WHERE f.id = ?
            """, (feedback_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except Exception as e:
        logging.error(f"Failed to get feedback by ID: {e}")
        return None


def update_feedback_status(feedback_id: int, status: str, admin_reply: str = None) -> bool:
    try:
        with get_db_connection() as conn:
            conn.execute("""
                UPDATE feedback
                SET status = ?, admin_reply = ?
                WHERE id = ?
            """, (status, admin_reply, feedback_id))
            conn.commit()
            return True
    except Exception as e:
        logging.error(f"Failed to update feedback status: {e}")
        return False
