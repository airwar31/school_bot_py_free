"""Core infrastructure: Configuration and Database Engine."""
from .config import BOT_TOKEN, FULL_ADMIN_ID, SCHEDULE_ADMIN_ID, ADMIN_ID, VK_TOKEN, VK_GROUP_ID, DATABASE
from .database import get_db_connection, DB_PATH, DatabaseLock
