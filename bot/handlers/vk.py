"""
VK News Browser & Pagination Router.
"""

from aiogram import Router, F, types
from bot.database.users import update_user_field, get_user_profile
from bot.keyboards.vk import get_vk_news_keyboard
from bot.keyboards.reply import get_main_keyboard
from bot.services.vk_service import get_vk_news

vk_router = Router(name="vk")


@vk_router.message(F.text == "📰 VK Новости")
async def vk_news_menu(message: types.Message):
    posts = await get_vk_news()
    if not posts:
        await message.answer("Новостей из сообщества ВКонтакте пока нет или интеграция не настроена.")
        return

    p = posts[0]
    text = f"📰 <b>VK Новости школы:</b>\n\n{p.get('text', '')[:900]}"
    await message.answer(text, parse_mode="HTML", reply_markup=get_vk_news_keyboard(has_prev=False, has_next=len(posts) > 1))


@vk_router.callback_query(F.data == "vk_news_exit")
async def vk_news_exit(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer()


@vk_router.message(F.text == "⚙️ Настройки")
async def vk_settings(message: types.Message):
    user = get_user_profile(message.from_user.id)
    is_enabled = user.get('vk_notifications', 1) if user else 1

    btn_text = "🔕 Отключить VK уведомления" if is_enabled else "🔔 Включить VK уведомления"
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=btn_text)],
            [types.KeyboardButton(text="🔙 Главное меню")]
        ],
        resize_keyboard=True
    )
    status_label = "включены" if is_enabled else "отключены"
    await message.answer(f"⚙️ Ваши персональные VK уведомления: {status_label}", reply_markup=kb)


@vk_router.message(F.text.in_(["🔔 Включить VK уведомления", "🔕 Отключить VK уведомления"]))
async def toggle_vk_user(message: types.Message):
    user = get_user_profile(message.from_user.id)
    cur = user.get('vk_notifications', 1) if user else 1
    new_val = 0 if cur else 1

    update_user_field(message.from_user.id, "vk_notifications", new_val)
    status_str = "включены" if new_val else "отключены"
    await message.answer(f"✅ VK уведомления {status_str}!", reply_markup=get_main_keyboard(message.from_user.id))
