"""
Class Timetable and Schedule Router.
"""

from datetime import datetime, timedelta
from aiogram import Router, F, types, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.core.config import ADMIN_ID, SCHEDULE_ADMIN_ID
from bot.database.schedule import get_schedule, save_schedule
from bot.database.users import get_user_profile
from bot.keyboards.reply import get_main_keyboard
from bot.keyboards.schedule import get_schedule_upload_keyboard
from bot.services.notifications import send_schedule_notification
from bot.states.fsm import ScheduleStates

schedule_router = Router(name="schedule")


def get_schedule_nav_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📅 Расписание на сегодня"), types.KeyboardButton(text="📅 Расписание на завтра")],
            [types.KeyboardButton(text="📅 Выбрать дату")],
            [types.KeyboardButton(text="🔙 Главное меню")]
        ],
        resize_keyboard=True
    )


async def send_schedule_for_date(message: types.Message, target_date_str: str, date_title: str):
    user = get_user_profile(message.from_user.id)
    user_shift = user.get('shift', '1') if user else '1'

    first_shift, second_shift = get_schedule(target_date_str)

    if not first_shift and not second_shift:
        await message.answer(f"📅 На {date_title} ({target_date_str}) расписание ещё не загружено.")
        return

    photo_id = first_shift if user_shift == '1' else second_shift
    caption = f"📅 Расписание на {date_title} ({target_date_str}) • Смена {user_shift}"

    if photo_id:
        await message.answer_photo(photo=photo_id, caption=caption)
    else:
        # Fallback to the other shift if specific one is empty
        alt_photo = second_shift if user_shift == '1' else first_shift
        if alt_photo:
            await message.answer_photo(photo=alt_photo, caption=caption)
        else:
            await message.answer(f"📅 Расписание на {date_title} отсутствует.")


@schedule_router.message(F.text == "📅 Расписание")
async def schedule_menu(message: types.Message):
    await message.answer("Выберите день для просмотра расписания:", reply_markup=get_schedule_nav_keyboard())


@schedule_router.message(F.text == "📅 Расписание на сегодня")
@schedule_router.message(Command("today"))
async def schedule_today(message: types.Message):
    today = datetime.now().strftime("%Y-%m-%d")
    await send_schedule_for_date(message, today, "сегодня")


@schedule_router.message(F.text == "📅 Расписание на завтра")
@schedule_router.message(Command("tomorrow"))
async def schedule_tomorrow(message: types.Message):
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    await send_schedule_for_date(message, tomorrow, "завтра")


@schedule_router.message(F.text == "📅 Выбрать дату")
async def schedule_choose_date(message: types.Message, state: FSMContext):
    cancel_kb = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="❌ Отменить")]],
        resize_keyboard=True
    )
    await message.answer(
        "Введите дату в формате ГГГГ-ММ-ДД (например, 2026-10-20):",
        reply_markup=cancel_kb
    )
    await state.set_state(ScheduleStates.waiting_for_date)


@schedule_router.message(ScheduleStates.waiting_for_date)
async def schedule_custom_date(message: types.Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("Выбор даты отменён.", reply_markup=get_schedule_nav_keyboard())
        return

    date_text = message.text.strip()
    try:
        dt = datetime.strptime(date_text, "%Y-%m-%d")
        await state.clear()
        await send_schedule_for_date(message, dt.strftime("%Y-%m-%d"), dt.strftime("%d.%m.%Y"))
    except ValueError:
        await message.answer("Неверный формат даты! Используйте ГГГГ-ММ-ДД (например, 2026-10-20):")


@schedule_router.message(Command("schedule"))
async def schedule_command(message: types.Message):
    parts = message.text.split()
    if len(parts) == 2:
        try:
            dt = datetime.strptime(parts[1], "%Y-%m-%d")
            await send_schedule_for_date(message, dt.strftime("%Y-%m-%d"), dt.strftime("%d.%m.%Y"))
        except ValueError:
            await message.reply("Неверный формат. Пример: /schedule 2026-10-20")
    else:
        await message.reply("Использование: /schedule ГГГГ-ММ-ДД")


# --- Admin Upload Schedule ---
@schedule_router.message(F.text == "📤 Загрузить расписание")
async def admin_upload_start(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_ID and message.from_user.id not in SCHEDULE_ADMIN_ID:
        await message.answer("❌ У вас нет прав для загрузки расписания.")
        return

    await message.answer(
        "Введите дату, для которой загружается расписание (ГГГГ-ММ-ДД):",
        reply_markup=get_schedule_upload_keyboard()
    )
    await state.set_state(ScheduleStates.date_input)


@schedule_router.message(ScheduleStates.date_input)
async def admin_date_input(message: types.Message, state: FSMContext):
    if message.text == "❌ Отменить загрузку":
        await state.clear()
        await message.answer("Загрузка отменена.", reply_markup=get_main_keyboard(message.from_user.id))
        return

    date_str = message.text.strip()
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        await state.update_data(schedule_date=date_str)
        await message.answer("Отправьте фото расписания для 1-й смены:", reply_markup=get_schedule_upload_keyboard())
        await state.set_state(ScheduleStates.uploading_first_shift)
    except ValueError:
        await message.answer("Неверный формат даты! Введите дату в виде ГГГГ-ММ-ДД:")


@schedule_router.message(ScheduleStates.uploading_first_shift, F.photo)
async def admin_first_shift_photo(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(first_shift=photo_id)
    await message.answer("Фото 1-й смены получено. Теперь отправьте фото для 2-й смены:", reply_markup=get_schedule_upload_keyboard())
    await state.set_state(ScheduleStates.uploading_second_shift)


@schedule_router.message(ScheduleStates.uploading_second_shift, F.photo)
async def admin_second_shift_photo(message: types.Message, state: FSMContext, bot: Bot):
    photo_id = message.photo[-1].file_id
    data = await state.get_data()
    schedule_date = data['schedule_date']
    first_shift = data['first_shift']

    is_update = save_schedule(schedule_date, first_shift, photo_id)
    await state.clear()

    await message.answer(
        f"✅ Расписание на {schedule_date} успешно сохранено!",
        reply_markup=get_main_keyboard(message.from_user.id)
    )
    # Broadcast alert
    await send_schedule_notification(bot, schedule_date, is_update)
