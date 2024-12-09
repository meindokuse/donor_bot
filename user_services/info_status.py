from aiogram import types, Router, F

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

login_router = Router()


@login_router.callback_query(F.data == 'info_status')
async def login_user(call: types.CallbackQuery):
    await call.message.delete()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="В меню", callback_data="main")],
    ])


    await call.message.answer(text=
                      f"Почетный донор университета: любые 8 сдач на дне донора(Гаврилова) или в ГКБ52\n\n"
                      f"Почетный донор Москвы: сдача тромбоцитов и крови считаем за одно, сдача плазмы за половину сдачи в любой организации в размере 20 сдач\n\n"
                      f"Почетный донор России: также, но 40 сдач\n\n",
                      keyboard=keyboard,
                      )

    await call.answer()

