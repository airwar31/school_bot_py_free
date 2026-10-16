"""
School Announcements Broadcast Router.
"""

from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext

from bot.core.config import FULL_ADMIN_ID
from bot.keyboards.reply import get_announcement_keyboard, get_confirmation_keyboard, get_main_keyboard
from bot.services.notifications import send_announcement
from bot.states.fsm import AnnouncementStates

announcements_router = Router(name="announcements")


@announcements_router.message(F.text == "📢 Создать объявление")
async def start_announcement(message: types.Message, state: FSMContext):
    if message.from_user.id not in FULL_ADMIN_ID:
        await message.answer("❌ У вас нет прав для создания объявлений.")
        return

    await message.answer(
        "Введите текст объявления:",
        reply_markup=get_announcement_keyboard(include_skip=False)
    )
    await state.set_state(AnnouncementStates.waiting_for_text)


@announcements_router.message(AnnouncementStates.waiting_for_text)
async def process_text(message: types.Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("Создание объявления отменено.", reply_markup=get_main_keyboard(message.from_user.id))
        return

    await state.update_data(text=message.text)
    await message.answer(
        "Прикрепите фото или видео к объявлению (или нажмите '⏩ Пропустить'):",
        reply_markup=get_announcement_keyboard(include_skip=True)
    )
    await state.set_state(AnnouncementStates.waiting_for_media)


@announcements_router.message(AnnouncementStates.waiting_for_media)
async def process_media(message: types.Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("Объявление отменено.", reply_markup=get_main_keyboard(message.from_user.id))
        return

    media = None
    if message.photo:
        media = {'type': 'photo', 'file_id': message.photo[-1].file_id}
    elif message.video:
        media = {'type': 'video', 'file_id': message.video.file_id}

    await state.update_data(media=media)
    data = await state.get_data()

    await message.answer("Предпросмотр объявления:")
    if media:
        if media['type'] == 'photo':
            await message.answer_photo(media['file_id'], caption=f"📢 ОБЪЯВЛЕНИЕ:\n\n{data['text']}")
        elif media['type'] == 'video':
            await message.answer_video(media['file_id'], caption=f"📢 ОБЪЯВЛЕНИЕ:\n\n{data['text']}")
    else:
        await message.answer(f"📢 ОБЪЯВЛЕНИЕ:\n\n{data['text']}")

    await message.answer("Подтвердить отправку объявления?", reply_markup=get_confirmation_keyboard())
    await state.set_state(AnnouncementStates.confirm_announcement)


@announcements_router.message(AnnouncementStates.confirm_announcement)
async def confirm_announcement(message: types.Message, state: FSMContext, bot: Bot):
    if message.text == "✅ Подтвердить":
        data = await state.get_data()
        await state.clear()
        await message.answer("🚀 Отправка объявления запущена...", reply_markup=get_main_keyboard(message.from_user.id))
        await send_announcement(bot, data['text'], data.get('media'))
        await message.answer("✅ Объявление успешно разослано!")
    else:
        await state.clear()
        await message.answer("Рассылка отменена.", reply_markup=get_main_keyboard(message.from_user.id))
