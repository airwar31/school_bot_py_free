"""
COP (Digital Educational Platform) Mini-App Router.
"""

from aiogram import Router, F, types

cop_router = Router(name="cop")


@cop_router.message(F.text == "🏫 ЦОП")
async def open_cop(message: types.Message):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(
            text="🚀 Открыть платформу ЦОП",
            web_app=types.WebAppInfo(url="https://cop.admhmao.ru")
        )]
    ])
    await message.answer(
        "Нажмите кнопку ниже, чтобы перейти в Цифровую образовательную платформу (ЦОП):",
        reply_markup=kb
    )
