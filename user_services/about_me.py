from aiogram import Router, F
from aiogram.types import CallbackQuery

from api.network_worker import NetWorkWorker

router_about_me = Router()


@router_about_me.callback_query(F.data == 'about_me')
async def router_about_me_handler(call: CallbackQuery):
    tg_id = call.message.from_user.id

    params = {
        'telegram_id': tg_id,
    }

    user = await NetWorkWorker().get_model_by_params('/login', params)
    if user:
        await call.answer(text=
                          f'ID:{user['id']}\n'
                          f'ФИО:{user['name']}\n'
                          f'Группа:{user['group']}\n'
                          f'Резус-Фактор:{user['rezus']}'
                          f'Кель: {user['kell']}'
                          f'Зарегистрован: {user['registered_on']}'
                          )
    else:
        await call.answer(text='Что-то пошло не так!')
