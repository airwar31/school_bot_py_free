import sqlite3
import logging
from bot.core.database import get_db_connection

def add_vk_notifications_column():
    """Добавляет колонку vk_notifications в таблицу users если её нет"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Проверяем, существует ли колонка
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'vk_notifications' not in columns:
                logging.info("Adding vk_notifications column to users table...")
                cursor.execute("ALTER TABLE users ADD COLUMN vk_notifications BOOLEAN DEFAULT 1")
                conn.commit()
                logging.info("vk_notifications column added successfully")
            else:
                logging.info("vk_notifications column already exists")
                
    except Exception as e:
        logging.error(f"Error adding vk_notifications column: {e}")

if __name__ == "__main__":
    add_vk_notifications_column()