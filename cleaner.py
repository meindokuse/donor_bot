from donation_services.admin.add_donation_service import donation_data
from donation_services.get_all_my_donation import pager_user
from user_services.admin.registration_service import user_data, last_mes_reg
from donation_services.admin.get_donations_by_date import pager
from donation_services.admin.add_donation_service import last_mes_id_don

from aiogram import BaseMiddleware
from aiogram.types import Update
from aiogram.fsm.context import FSMContext

# Пример словаря для временных данных (pager)
pager_1 = {}


class CleanUpMiddleware(BaseMiddleware):

    async def on_post_process_update(self, update: Update, result, data: dict):
        # Получаем состояние пользователя
        state: FSMContext = data.get('state')
        if state:
            # Очищаем состояние пользователя
            await state.clear()

        # Получаем chat_id пользователя
        if update.callback_query:
            chat_id = update.callback_query.message.chat.id
        elif update.message:
            chat_id = update.message.chat.id
        else:
            chat_id = None

        # Удаляем данные о пользователе из временного словаря, если он существует
        if chat_id and chat_id in pager:
            del pager[chat_id]


list_dicts = [user_data, donation_data, pager, last_mes_reg, last_mes_id_don, pager_user]
list_states = []


async def clear_all(chat_id):
    for d in list_dicts:
        if chat_id in d:
            del d[chat_id]

