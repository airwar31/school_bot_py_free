"""Keyboards Package."""
from .reply import (
    get_main_keyboard,
    get_registration_keyboard,
    get_date_selection_keyboard,
    get_announcement_keyboard,
    get_confirmation_keyboard,
    create_keyboard
)
from .events import get_event_keyboard, get_admin_event_keyboard, get_cancel_keyboard
from .schedule import get_schedule_upload_keyboard
from .vk import get_vk_news_keyboard
