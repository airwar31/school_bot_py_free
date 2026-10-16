"""
Common commands and navigation router (/start, /help, info, main menu).
"""

import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.core.config import ADMIN_ID
from bot.database.users import get_user_profile
from bot.keyboards.reply import get_main_keyboard
from bot.states.fsm import RegistrationStates

common_router = Router(name="common")


@common_router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Handles /start command, registers new students or shows main menu."""
    try:
        user = get_user_profile(message.from_user.id)
        keyboard = get_main_keyboard(message.from_user.id)

        if user:
            await message.answer("С возвращением!\nГлавное меню:", reply_markup=keyboard)
        else:
            await message.answer(
                "Добро пожаловать в Школьный бот! Давайте зарегистрируемся.\nВведите ваше имя:",
                reply_markup=types.ReplyKeyboardRemove()
            )
            await state.set_state(RegistrationStates.waiting_for_name)
    except Exception as e:
        logging.error(f"Error in cmd_start: {e}")
        await message.reply("Произошла ошибка при обращении к базе данных. Попробуйте позже.")


@common_router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Detailed help message."""
    is_group = message.chat.type in ['group', 'supergroup']

    help_text = """📚 <b>Справка по командам бота</b>

<b>📅 Расписание:</b>
/today - Расписание на сегодня
/tomorrow - Расписание на завтра
/schedule ГГГГ-ММ-ДД - Расписание на дату
  <i>Пример: /schedule 2026-10-17</i>

<b>🔧 Основные команды:</b>
/start - Начать работу с ботом
/help - Показать эту справку
"""
    if is_group:
        help_text += """
<b>⚙️ Управление группой (только для админов):</b>
/settings - Посмотреть настройки группы
/toggle_vk - Включить/отключить VK уведомления
"""
    else:
        help_text += """
<b>📱 В личных сообщениях доступно:</b>
• Регистрация и управление профилем
• Просмотр расписания и мероприятий
• VK новости школы
• Обратная связь с администрацией
• Доступ к ЦОП

Используйте кнопки меню для быстрой навигации! 👇
"""
    await message.answer(help_text, parse_mode="HTML")


@common_router.message(F.text == "ℹ️ Информация")
async def bot_info(message: types.Message):
    """About bot information."""
    bot_info_text = (
        "🤖 *О боте*\n\n"
        "Этот бот поможет вам:\n"
        "📅 Просматривать расписание занятий\n"
        "📋 Получать важные новости и объявления\n"
        "Разработан для удобства учащихся и преподавателей.\n"
        "По вопросам и предложениям: @airwar31."
    )
    await message.answer(
        bot_info_text,
        parse_mode="Markdown",
        reply_markup=get_main_keyboard(message.from_user.id)
    )


@common_router.message(F.text == "🔙 Главное меню")
async def process_main_menu(message: types.Message, state: FSMContext):
    """Return to main menu."""
    await state.clear()
    await message.answer(
        "Вы вернулись в главное меню:",
        reply_markup=get_main_keyboard(message.from_user.id)
    )


@common_router.message(F.text == "⚙️ Панель администратора")
async def process_admin_panel(message: types.Message):
    """Admin dashboard menu."""
    if message.from_user.id not in ADMIN_ID:
        await message.answer("❌ У вас нет прав доступа к панели администратора.")
        return

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📢 Создать объявление")],
            [types.KeyboardButton(text="📤 Загрузить расписание")],
            [types.KeyboardButton(text="🎉 Мероприятия")],
            [types.KeyboardButton(text="📞 Обратная связь")],
            [types.KeyboardButton(text="🔙 Главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer("⚙️ Панель администратора:", reply_markup=keyboard)
