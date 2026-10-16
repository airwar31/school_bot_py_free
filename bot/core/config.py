"""
School LMS Telegram Bot Configuration Module
Loads credentials and permissions safely from environment variables.
"""

import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Telegram Bot Token (Required)
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

def parse_id_list(env_var_name: str, default: list) -> list:
    """Safely parse comma-separated list of Telegram user IDs."""
    raw = os.getenv(env_var_name, "").strip()
    if not raw:
        return default
    try:
        return [int(x.strip()) for x in raw.split(",") if x.strip()]
    except ValueError:
        return default

# Role-Based Access Control (RBAC) IDs
# Super Administrators (full privileges: announcements, events, feedback, user management)
FULL_ADMIN_ID = parse_id_list("FULL_ADMIN_IDS", [8391219214])

# Schedule Administrators (schedule upload and editing only)
SCHEDULE_ADMIN_ID = parse_id_list("SCHEDULE_ADMIN_IDS", [1124990195])

# Combined list for general admin checks
ADMIN_ID = list(set(FULL_ADMIN_ID + SCHEDULE_ADMIN_ID))

# VKontakte Community Integration
VK_TOKEN = os.getenv("VK_TOKEN", "").strip()
try:
    VK_GROUP_ID = int(os.getenv("VK_GROUP_ID", "171068837"))
except ValueError:
    VK_GROUP_ID = 171068837

# SQLite Database Location
DATABASE = os.getenv("DATABASE_PATH", "data/bot.db").strip()
