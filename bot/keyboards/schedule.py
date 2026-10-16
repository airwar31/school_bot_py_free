"""Schedule keyboards."""
from aiogram import types


def get_schedule_upload_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="❌ Отменить загрузку")]],
        resize_keyboard=True
    )
