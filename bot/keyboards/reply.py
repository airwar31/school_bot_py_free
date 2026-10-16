"""Reply navigation keyboards."""
from aiogram import types
from bot.core.config import ADMIN_ID


def get_registration_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="❌ Отменить регистрацию")]],
        resize_keyboard=True
    )


def get_date_selection_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="❌ Отменить")]],
        resize_keyboard=True
    )


def get_announcement_keyboard(include_skip=False):
    buttons = []
    if include_skip:
        buttons.append([types.KeyboardButton(text="⏩ Пропустить")])
    buttons.append([types.KeyboardButton(text="❌ Отменить")])
    return types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_confirmation_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="✅ Подтвердить")],
            [types.KeyboardButton(text="❌ Отменить")]
        ],
        resize_keyboard=True
    )


def get_main_keyboard(user_id: int):
    buttons = [
        [types.KeyboardButton(text="🏫 ЦОП")],
        [types.KeyboardButton(text="📅 Расписание"), types.KeyboardButton(text="📋 Новости")],
        [types.KeyboardButton(text="👤 Профиль"), types.KeyboardButton(text="⚙️ Настройки")],
        [types.KeyboardButton(text="ℹ️ Информация")]
    ]
    if user_id in ADMIN_ID:
        buttons.append([types.KeyboardButton(text="⚙️ Панель администратора")])

    return types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def create_keyboard(buttons, row_width=2):
    keyboard_buttons = []
    for i in range(0, len(buttons), row_width):
        row_buttons = buttons[i:i + row_width]
        keyboard_buttons.append([types.KeyboardButton(text=btn) for btn in row_buttons])
    return types.ReplyKeyboardMarkup(keyboard=keyboard_buttons, resize_keyboard=True)
