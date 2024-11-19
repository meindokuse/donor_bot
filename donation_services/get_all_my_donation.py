from aiogram import types, Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from api.network_worker import NetWorkWorker
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

pager_user = {}
get_all_my_donation = Router()


@get_all_my_donation.callback_query(F.data == 'get_all_my_donation')
async def get_all_my_donation_fun(call: CallbackQuery):
    chat_id = call.message.chat.id

    pager_user[chat_id] = {'page': 1, 'limit': 4}

    await send_paginated_donations(call, chat_id)
    await call.message.delete()



@get_all_my_donation.callback_query(F.data == 'prev_don_list_1')
async def prev_p(query: CallbackQuery):
    chat_id = query.message.chat.id
    pager_user[chat_id]['page'] -= 1

    await send_paginated_donations(query, chat_id)
    await query.message.delete()



@get_all_my_donation.callback_query(F.data == 'next_don_list_1')
async def next_p(query: CallbackQuery):
    chat_id = query.message.chat.id
    pager_user[chat_id]['page'] += 1

    await send_paginated_donations(query, chat_id)
    await query.message.delete()



@get_all_my_donation.callback_query(F.data == 'to_start_1')
async def next_p(query: CallbackQuery):
    chat_id = query.message.chat.id
    pager_user[chat_id]['page'] = 1

    await send_paginated_donations(query, chat_id)
    await query.message.delete()



async def send_paginated_donations(call: CallbackQuery, chat_id):
    params = {
        "page": pager_user[chat_id]['page'],
        "limit": pager_user[chat_id]['limit'],
        "telegram_id": str(chat_id),
    }

    result = await NetWorkWorker().get_model_list(endpoint="donation/get_user_donations", params=params)

    if result:
        data = result.get('data')

        builder = InlineKeyboardBuilder()
        prev_p = InlineKeyboardButton(
            text="⬅️",
            callback_data="prev_don_list_1"
        )
        next_p = InlineKeyboardButton(
            text="➡️",
            callback_data="next_don_list_1"
        )
        to_start = InlineKeyboardButton(
            text="В начало",
            callback_data="to_start_1"
        )
        to_menu = InlineKeyboardButton(text="В меню", callback_data="main")
        if len(data['donations']) < 4 and pager_user[chat_id]['page'] == 1:
            builder.add(to_menu)
        elif len(data['donations']) < 4:
            builder.add(prev_p, to_start, to_menu)
            builder.adjust(2)
        elif pager_user[chat_id]['page'] == 1:
            builder.add(to_start, next_p, to_menu)
            builder.adjust(2)
        else:
            builder.add(to_start, prev_p, next_p, to_menu)
            builder.adjust(3)

        don_message = await generate_message(data)


        await call.message.answer(text=don_message, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="В меню", callback_data="main")],
        ])
        await call.message.answer(text="Похоже произошла ошибка!", reply_markup=keyboard)


async def generate_message(data: dict):
    quantity = data.get('quantity_donation')
    donations = data.get('donations')

    if not donations:
        full_message = 'Донаций нету'
        return full_message
    donations_text = ''
    for donation in donations:
        is_free = 'Да' if donation.get('is_free') else 'Нет'
        donation_info = (
            f"ID: {donation.get('id')}\n"
            f"Тип: {donation.get('type')}\n"
            f"Владелец: {donation.get("owner")}\n"
            f"Безвозмездная?: {is_free}\n"
            f"Когда: {donation.get('date')}\n"
            f"Где: {donation.get("org")}\n\n"
        )
        donations_text += f"<blockquote>{donation_info}</blockquote>"
    full_message = f'<blockquote>Кол-во донаций: {quantity}</blockquote>\n' + donations_text

    return full_message
