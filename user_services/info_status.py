from aiogram import types, Router, F

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

get_status = Router()


@get_status.callback_query(F.data == 'get_info_status')
async def login_user(call: types.CallbackQuery):
    await call.message.delete()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="В меню", callback_data="main")],
    ])

    await call.answer()

    await call.message.answer(text=
                      f"Почетный донор университета: любые 8 сдач на дне донора(Гаврилова) или в ГКБ52\n\n"
                      f"Почетный донор Москвы: сдача тромбоцитов и крови считаем за одно, сдача плазмы за половину сдачи в любой организации в размере 20 сдач\n\n"
                      f"Почетный донор России: также, но 40 сдач\n\n",
                      reply_markup=keyboard,
                      )
