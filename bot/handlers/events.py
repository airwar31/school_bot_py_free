"""
School Events Calendar and Management Router.
"""

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.core.config import FULL_ADMIN_ID
from bot.database.events import get_current_events, save_event, delete_event, get_event
from bot.keyboards.events import get_event_keyboard, get_admin_event_keyboard, get_cancel_keyboard
from bot.keyboards.reply import get_main_keyboard
from bot.states.fsm import EventStates

events_router = Router(name="events")


@events_router.message(F.text == "📋 Новости")
async def events_menu(message: types.Message):
    await message.answer("Выберите раздел:", reply_markup=get_event_keyboard())


@events_router.message(F.text == "🎉 Мероприятия")
async def current_events(message: types.Message):
    events = get_current_events()
    is_admin = message.from_user.id in FULL_ADMIN_ID

    if not events:
        await message.answer("🎉 На ближайшую неделю школьных мероприятий не запланировано.")
        if is_admin:
            await message.answer("Управление событиями:", reply_markup=get_admin_event_keyboard())
        return

    text = "🎉 <b>Ближайшие школьные мероприятия:</b>\n\n"
    for ev in events:
        text += (
            f"📌 <b>{ev['name']}</b> (ID: {ev['id']})\n"
            f"📝 {ev['description']}\n"
            f"📅 {ev['start_date']} {ev['start_time']} — {ev['end_date']} {ev['end_time']}\n\n"
        )

    await message.answer(text, parse_mode="HTML")
    if is_admin:
        await message.answer("Управление событиями:", reply_markup=get_admin_event_keyboard())


@events_router.message(F.text == "➕ Создать событие")
async def create_event_start(message: types.Message, state: FSMContext):
    if message.from_user.id not in FULL_ADMIN_ID:
        return
    await message.answer("Введите название мероприятия:", reply_markup=get_cancel_keyboard())
    await state.set_state(EventStates.waiting_for_name)


@events_router.message(EventStates.waiting_for_name)
async def event_name_step(message: types.Message, state: FSMContext):
    if message.text == "❌ Отменить создание":
        await state.clear()
        await message.answer("Создание отменено.", reply_markup=get_event_keyboard())
        return
    await state.update_data(name=message.text)
    await message.answer("Введите описание мероприятия:", reply_markup=get_cancel_keyboard())
    await state.set_state(EventStates.waiting_for_description)


@events_router.message(EventStates.waiting_for_description)
async def event_desc_step(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите дату начала (ГГГГ-ММ-ДД):", reply_markup=get_cancel_keyboard())
    await state.set_state(EventStates.waiting_for_start_date)


@events_router.message(EventStates.waiting_for_start_date)
async def event_start_date_step(message: types.Message, state: FSMContext):
    await state.update_data(start_date=message.text.strip())
    await message.answer("Введите дату окончания (ГГГГ-ММ-ДД):", reply_markup=get_cancel_keyboard())
    await state.set_state(EventStates.waiting_for_end_date)


@events_router.message(EventStates.waiting_for_end_date)
async def event_end_date_step(message: types.Message, state: FSMContext):
    await state.update_data(end_date=message.text.strip())
    await message.answer("Введите время начала (ЧЧ:ММ, например 14:00):", reply_markup=get_cancel_keyboard())
    await state.set_state(EventStates.waiting_for_start_time)


@events_router.message(EventStates.waiting_for_start_time)
async def event_start_time_step(message: types.Message, state: FSMContext):
    await state.update_data(start_time=message.text.strip())
    await message.answer("Введите время окончания (ЧЧ:ММ, например 16:00):", reply_markup=get_cancel_keyboard())
    await state.set_state(EventStates.waiting_for_end_time)


@events_router.message(EventStates.waiting_for_end_time)
async def event_end_time_step(message: types.Message, state: FSMContext):
    data = await state.get_data()
    end_time = message.text.strip()

    save_event(
        name=data['name'],
        description=data['description'],
        start_date=data['start_date'],
        end_date=data['end_date'],
        start_time=data['start_time'],
        end_time=end_time
    )
    await state.clear()
    await message.answer("✅ Мероприятие успешно создано!", reply_markup=get_event_keyboard())


@events_router.message(F.text == "❌ Удалить событие")
async def delete_event_start(message: types.Message, state: FSMContext):
    if message.from_user.id not in FULL_ADMIN_ID:
        return
    await message.answer("Введите ID события для удаления:", reply_markup=get_cancel_keyboard())
    await state.set_state(EventStates.waiting_for_event_id)


@events_router.message(EventStates.waiting_for_event_id)
async def delete_event_finish(message: types.Message, state: FSMContext):
    if message.text == "❌ Отменить создание" or message.text == "❌ Отменить":
        await state.clear()
        await message.answer("Удаление отменено.", reply_markup=get_event_keyboard())
        return

    try:
        ev_id = int(message.text.strip())
        delete_event(ev_id)
        await state.clear()
        await message.answer(f"✅ Событие #{ev_id} удалено.", reply_markup=get_event_keyboard())
    except ValueError:
        await message.answer("Пожалуйста, введите корректный числовой ID:")
