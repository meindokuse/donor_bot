from aiogram import Router, F
from aiogram.types import CallbackQuery

from api.network_worker import NetWorkWorker
from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup

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
    print(user)
    if user:
        kell = '+' if user['kell'] == True else '-'
        rezus = '+' if user['rezus'] == True else '-'
        await call.answer(text=
                          f'ID:{user['id']}\n'
                          f'ФИО:{user['name']}\n'
                          f'Группа:{user['group']}\n'
                          f'Резус-Фактор:{rezus}'
                          f'Кель: {kell}'
                          f'Зарегистрован: {user['registered_on']}',
                          reply_markup=keyboard
                          )
    else:
        await call.answer(text='Что-то пошло не так!',reply_markup=keyboard)
