import sqlite3
import logging
from bot.core.database import get_db_connection

def create_feedback_table():
    """Создает таблицу для обратной связи"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    rating INTEGER,
                    status TEXT DEFAULT 'new',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            conn.commit()
            logging.info("Feedback table created successfully")
                
    except Exception as e:
        logging.error(f"Error creating feedback table: {e}")

if __name__ == "__main__":
    create_feedback_table()