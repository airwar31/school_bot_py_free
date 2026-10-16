"""School events keyboards."""
from aiogram import types


def get_event_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🎉 Мероприятия"), types.KeyboardButton(text="📰 VK Новости")],
            [types.KeyboardButton(text="🔙 Главное меню")]
        ],
        resize_keyboard=True
    )


def get_admin_event_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="➕ Создать событие")],
            [types.KeyboardButton(text="❌ Удалить событие")],
            [types.KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )


def get_cancel_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="❌ Отменить создание")]],
        resize_keyboard=True
    )
