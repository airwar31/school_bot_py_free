"""
Student Registration FSM Router.
"""

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.database.users import register_user
from bot.keyboards.reply import get_main_keyboard, get_registration_keyboard
from bot.states.fsm import RegistrationStates

registration_router = Router(name="registration")


@registration_router.message(F.text == "❌ Отменить регистрацию")
async def cancel_registration(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Регистрация отменена. Используйте /start чтобы начать заново.")


@registration_router.message(RegistrationStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Введите вашу фамилию:", reply_markup=get_registration_keyboard())
    await state.set_state(RegistrationStates.waiting_for_surname)


@registration_router.message(RegistrationStates.waiting_for_surname)
async def process_surname(message: types.Message, state: FSMContext):
    await state.update_data(surname=message.text.strip())
    await message.answer("Введите ваше отчество:", reply_markup=get_registration_keyboard())
    await state.set_state(RegistrationStates.waiting_for_patronymic)


@registration_router.message(RegistrationStates.waiting_for_patronymic)
async def process_patronymic(message: types.Message, state: FSMContext):
    await state.update_data(patronymic=message.text.strip())
    await message.answer("Введите ваш класс (например, 10А или 11Б):", reply_markup=get_registration_keyboard())
    await state.set_state(RegistrationStates.waiting_for_class)


@registration_router.message(RegistrationStates.waiting_for_class)
async def process_class(message: types.Message, state: FSMContext):
    await state.update_data(user_class=message.text.strip().upper())
    shift_kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="1"), types.KeyboardButton(text="2")],
            [types.KeyboardButton(text="❌ Отменить регистрацию")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите номер вашей смены (1 или 2):", reply_markup=shift_kb)
    await state.set_state(RegistrationStates.waiting_for_shift)


@registration_router.message(RegistrationStates.waiting_for_shift)
async def process_shift(message: types.Message, state: FSMContext):
    shift = message.text.strip()
    if shift not in ["1", "2"]:
        await message.answer("Пожалуйста, выберите смену: 1 или 2.")
        return

    await state.update_data(shift=shift)
    await message.answer(
        "Введите номер вашего телефона (например, +79991234567):",
        reply_markup=get_registration_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_phone)


@registration_router.message(RegistrationStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    phone = message.text.strip()

    user_data = {
        'name': data.get('name', ''),
        'surname': data.get('surname', ''),
        'patronymic': data.get('patronymic', ''),
        'class': data.get('user_class', ''),
        'shift': data.get('shift', '1'),
        'phone': phone,
        'username': message.from_user.username
    }
    register_user(message.from_user.id, user_data)
    await state.clear()

    await message.answer(
        "✅ Регистрация успешно завершена! Добро пожаловать!",
        reply_markup=get_main_keyboard(message.from_user.id)
    )
