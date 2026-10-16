"""
Student Feedback and Admin Ticket Reply Router.
"""

from aiogram import Router, F, types, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.core.config import FULL_ADMIN_ID
from bot.database.feedback import create_feedback, get_feedback_list, get_feedback_by_id, update_feedback_status
from bot.keyboards.reply import get_main_keyboard
from bot.states.fsm import FeedbackStates, AdminFeedbackStates

feedback_router = Router(name="feedback")


def get_feedback_menu_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="❓ Задать вопрос"), types.KeyboardButton(text="😡 Жалоба")],
            [types.KeyboardButton(text="💡 Предложение"), types.KeyboardButton(text="⭐ Оценить бота")],
            [types.KeyboardButton(text="🔙 Главное меню")]
        ],
        resize_keyboard=True
    )


@feedback_router.message(F.text == "📞 Обратная связь")
async def feedback_menu(message: types.Message):
    await message.answer("Выберите тип обращения к администрации школы:", reply_markup=get_feedback_menu_keyboard())


@feedback_router.message(F.text == "❓ Задать вопрос")
async def question_start(message: types.Message, state: FSMContext):
    await message.answer("Напишите ваш вопрос. Администрация ответит вам в личных сообщениях:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(FeedbackStates.waiting_for_question)


@feedback_router.message(FeedbackStates.waiting_for_question)
async def question_save(message: types.Message, state: FSMContext, bot: Bot):
    ticket_id = create_feedback(message.from_user.id, "question", message.text)
    await state.clear()
    await message.answer("✅ Ваш вопрос передан администрации! Мы ответим в ближайшее время.", reply_markup=get_main_keyboard(message.from_user.id))

    for admin_id in FULL_ADMIN_ID:
        try:
            await bot.send_message(
                admin_id,
                f"❓ <b>Новый вопрос от ученика (Тикет #{ticket_id})</b>\n"
                f"От: @{message.from_user.username or message.from_user.id}\n\n"
                f"{message.text}\n\n"
                f"<i>Для ответа используйте: /reply {ticket_id}</i>",
                parse_mode="HTML"
            )
        except Exception:
            pass


@feedback_router.message(F.text == "😡 Жалоба")
async def complaint_start(message: types.Message, state: FSMContext):
    await message.answer("Опишите возникшую проблему или жалобу:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(FeedbackStates.waiting_for_complaint)


@feedback_router.message(FeedbackStates.waiting_for_complaint)
async def complaint_save(message: types.Message, state: FSMContext):
    create_feedback(message.from_user.id, "complaint", message.text)
    await state.clear()
    await message.answer("✅ Ваша жалоба зафиксирована и передана на рассмотрение.", reply_markup=get_main_keyboard(message.from_user.id))


@feedback_router.message(F.text == "💡 Предложение")
async def suggestion_start(message: types.Message, state: FSMContext):
    await message.answer("Поделитесь вашей идеей или предложением по улучшению школы/бота:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(FeedbackStates.waiting_for_suggestion)


@feedback_router.message(FeedbackStates.waiting_for_suggestion)
async def suggestion_save(message: types.Message, state: FSMContext):
    create_feedback(message.from_user.id, "suggestion", message.text)
    await state.clear()
    await message.answer("✅ Спасибо за ваше предложение!", reply_markup=get_main_keyboard(message.from_user.id))


@feedback_router.message(F.text == "⭐ Оценить бота")
async def rating_start(message: types.Message, state: FSMContext):
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="1"), types.KeyboardButton(text="2"), types.KeyboardButton(text="3"),
             types.KeyboardButton(text="4"), types.KeyboardButton(text="5")]
        ],
        resize_keyboard=True
    )
    await message.answer("Оцените работу школьного бота от 1 до 5:", reply_markup=kb)
    await state.set_state(FeedbackStates.waiting_for_rating)


@feedback_router.message(FeedbackStates.waiting_for_rating)
async def rating_save(message: types.Message, state: FSMContext):
    try:
        val = int(message.text.strip())
        create_feedback(message.from_user.id, "rating", rating=val)
        await state.clear()
        await message.answer("⭐ Спасибо за вашу оценку!", reply_markup=get_main_keyboard(message.from_user.id))
    except ValueError:
        await message.answer("Пожалуйста, нажмите оценку от 1 до 5:")


# --- Admin Ticket Replies ---
@feedback_router.message(Command("reply"))
async def admin_reply_cmd(message: types.Message, state: FSMContext):
    if message.from_user.id not in FULL_ADMIN_ID:
        return

    parts = message.text.split(maxsplit=2)
    if len(parts) >= 3:
        try:
            ticket_id = int(parts[1])
            reply_text = parts[2]
            fb = get_feedback_by_id(ticket_id)
            if not fb:
                await message.reply(f"Тикет #{ticket_id} не найден.")
                return

            update_feedback_status(ticket_id, "resolved", reply_text)
            bot = message.bot
            await bot.send_message(
                fb['user_id'],
                f"💬 <b>Ответ администрации на ваше обращение #{ticket_id}:</b>\n\n{reply_text}",
                parse_mode="HTML"
            )
            await message.reply(f"✅ Ответ успешно доставлен ученику по тикету #{ticket_id}!")
        except Exception as e:
            await message.reply(f"Ошибка при отправке: {e}")
    else:
        await message.reply("Использование: /reply <ID_ТИКЕТА> <ТЕКСТ_ОТВЕТА>\nПример: /reply 5 Здравствуйте! Расписание обновлено.")
