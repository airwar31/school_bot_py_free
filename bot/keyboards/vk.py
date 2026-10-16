"""VK Post Pagination Inline Keyboards."""
from aiogram import types


def get_vk_news_keyboard(has_prev=False, has_next=False):
    buttons = []
    nav_row = []
    if has_prev:
        nav_row.append(types.InlineKeyboardButton(text="◀️ Назад", callback_data="vk_news_prev"))
    if has_next:
        nav_row.append(types.InlineKeyboardButton(text="Вперед ▶️", callback_data="vk_news_next"))

    if nav_row:
        buttons.append(nav_row)

    buttons.append([types.InlineKeyboardButton(text="❌ Закрыть", callback_data="vk_news_exit")])
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)
