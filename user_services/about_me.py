from aiogram import Router, F
from aiogram.types import CallbackQuery

from api.network_worker import NetWorkWorker
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

router_about_me = Router()


@router_about_me.callback_query(F.data == 'about_me')
async def router_about_me_handler(call: CallbackQuery):
    tg_id = call.message.from_user.id

    params = {
        'telegram_id': str(tg_id),
    }

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="В меню", callback_data="main")],
    ])

    user = await NetWorkWorker().get_model_by_params('/login', params)
    status = ""
    if user['status'] >= 8:
        status = "Почетный донор университета"
    if user['status'] >= 20:
        status = "Почетный донор Москвы"
    if user['status'] >= 40:
        status = "Почетный донор России"
    else:
        status = "Начинающий донор"

    print(user)
    if user:
        kell = '+' if user['kell'] == True else '-'
        rezus = '+' if user['rezus'] == True else '-'
        await call.answer(text=
                          f'ID:{user['id']}\n'
                          f'ФИО:{user['name']}\n'
                          f'Группа:{user['group']}\n'
                          f'Резус-Фактор:{rezus}\n'
                          f'Кель: {kell}\n'
                          f'Зарегистрован: {user['registered_on']}\n\n'
                          f'Статус: {status}',
                          reply_markup=keyboard
                          )
    else:
        await call.answer(text='Что-то пошло не так!', reply_markup=keyboard)
