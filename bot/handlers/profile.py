"""
User Profile Viewing and Editing Router.
"""

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.database.users import get_user_profile, update_user_field
from bot.keyboards.reply import get_main_keyboard
from bot.states.fsm import ProfileEditStates

profile_router = Router(name="profile")


def get_profile_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="✏️ Редактировать профиль")],
            [types.KeyboardButton(text="🔙 Главное меню")]
        ],
        resize_keyboard=True
    )


def get_edit_fields_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="✏️ Изменить имя"), types.KeyboardButton(text="✏️ Изменить фамилию")],
            [types.KeyboardButton(text="✏️ Изменить класс"), types.KeyboardButton(text="✏️ Изменить смену")],
            [types.KeyboardButton(text="✏️ Изменить телефон")],
            [types.KeyboardButton(text="🔙 Назад к профилю")]
        ],
        resize_keyboard=True
    )


@profile_router.message(F.text.in_(["👤 Профиль", "🔙 Назад к профилю"]))
async def process_profile(message: types.Message, state: FSMContext):
    await state.clear()
    user = get_user_profile(message.from_user.id)
    if not user:
        await message.reply("Вы еще не зарегистрированы. Используйте /start для регистрации.")
        return

    profile_text = (
        f"👤 <b>Профиль ученика:</b>\n\n"
        f"<b>Имя:</b> {user.get('name', '-')}\n"
        f"<b>Фамилия:</b> {user.get('surname', '-')}\n"
        f"<b>Отчество:</b> {user.get('patronymic', '-')}\n"
        f"<b>Класс:</b> {user.get('class', '-')}\n"
        f"<b>Смена:</b> {user.get('shift', '-')}\n"
        f"<b>Телефон:</b> {user.get('phone', '-')}"
    )
    await message.answer(profile_text, parse_mode="HTML", reply_markup=get_profile_keyboard())


@profile_router.message(F.text == "✏️ Редактировать профиль")
async def process_edit_profile(message: types.Message):
    await message.answer("Выберите поле для изменения:", reply_markup=get_edit_fields_keyboard())


@profile_router.message(F.text == "✏️ Изменить имя")
async def edit_name_start(message: types.Message, state: FSMContext):
    await message.answer("Введите новое имя:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ProfileEditStates.editing_name)


@profile_router.message(ProfileEditStates.editing_name)
async def edit_name_save(message: types.Message, state: FSMContext):
    update_user_field(message.from_user.id, "name", message.text.strip())
    await state.clear()
    await message.answer("✅ Имя успешно обновлено!", reply_markup=get_edit_fields_keyboard())


@profile_router.message(F.text == "✏️ Изменить фамилию")
async def edit_surname_start(message: types.Message, state: FSMContext):
    await message.answer("Введите новую фамилию:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ProfileEditStates.editing_surname)


@profile_router.message(ProfileEditStates.editing_surname)
async def edit_surname_save(message: types.Message, state: FSMContext):
    update_user_field(message.from_user.id, "surname", message.text.strip())
    await state.clear()
    await message.answer("✅ Фамилия успешно обновлена!", reply_markup=get_edit_fields_keyboard())


@profile_router.message(F.text == "✏️ Изменить класс")
async def edit_class_start(message: types.Message, state: FSMContext):
    await message.answer("Введите новый класс (например, 10А):", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ProfileEditStates.editing_class)


@profile_router.message(ProfileEditStates.editing_class)
async def edit_class_save(message: types.Message, state: FSMContext):
    update_user_field(message.from_user.id, "class", message.text.strip().upper())
    await state.clear()
    await message.answer("✅ Класс успешно обновлен!", reply_markup=get_edit_fields_keyboard())


@profile_router.message(F.text == "✏️ Изменить смену")
async def edit_shift_start(message: types.Message, state: FSMContext):
    kb = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="1"), types.KeyboardButton(text="2")]],
        resize_keyboard=True
    )
    await message.answer("Выберите номер новой смены:", reply_markup=kb)
    await state.set_state(ProfileEditStates.editing_shift)


@profile_router.message(ProfileEditStates.editing_shift)
async def edit_shift_save(message: types.Message, state: FSMContext):
    shift = message.text.strip()
    if shift in ["1", "2"]:
        update_user_field(message.from_user.id, "shift", shift)
        await state.clear()
        await message.answer("✅ Смена успешно обновлена!", reply_markup=get_edit_fields_keyboard())
    else:
        await message.answer("Пожалуйста, выберите 1 или 2.")


@profile_router.message(F.text == "✏️ Изменить телефон")
async def edit_phone_start(message: types.Message, state: FSMContext):
    await message.answer("Введите новый номер телефона:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ProfileEditStates.editing_phone)


@profile_router.message(ProfileEditStates.editing_phone)
async def edit_phone_save(message: types.Message, state: FSMContext):
    update_user_field(message.from_user.id, "phone", message.text.strip())
    await state.clear()
    await message.answer("✅ Телефон успешно обновлен!", reply_markup=get_edit_fields_keyboard())
