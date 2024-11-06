from aiogram import types, Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from api.network_worker import NetWorkWorker
from aiogram.utils.keyboard import InlineKeyboardBuilder

pager = {}
get_all_my_donation = Router()


@get_all_my_donation.callback_query(F.data == 'get_all_my_donation')
async def get_donations_by_date(call: CallbackQuery):
    chat_id = call.message.chat.id
    tg_id = call.message.from_user.id

    pager[chat_id] = {'page': 1, 'limit': 4}

    params = {
        "page": pager[chat_id]['page'],
        "limit": pager[chat_id]['limit'],
        "telegram_id": tg_id,
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
        if len(data['donations']) < 4:
            builder.add(prev_p, to_start)
        else:
            builder.add(prev_p, to_start, next_p)

        don_message = await generate_message(data)

        await call.answer(text=don_message, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    else:
        await call.answer(text="Похоже произошла ошибка!")


@get_all_my_donation.callback_query(F.data == 'prev_don_list_1')
async def prev_p(query: CallbackQuery, state: FSMContext):
    chat_id = query.message.chat.id
    pager[chat_id]['page'] -= 1

    await query.message.delete()
    await send_paginated_donations(query.message, state, chat_id)


@get_all_my_donation.callback_query(F.data == 'next_don_list_1')
async def next_p(query: CallbackQuery, state: FSMContext):
    chat_id = query.message.chat.id
    pager[chat_id]['page'] += 1

    await query.message.delete()
    await send_paginated_donations(query.message, state, chat_id)


@get_all_my_donation.callback_query(F.data == 'to_start_1')
async def next_p(query: CallbackQuery, state: FSMContext):
    chat_id = query.message.chat.id
    pager[chat_id]['page'] = 1

    await query.message.delete()
    await send_paginated_donations(query.message, state, chat_id)


async def send_paginated_donations(message, state, chat_id):
    params = {
        "page": pager[chat_id]['page'],
        "limit": pager[chat_id]['limit'],

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
        if len(data['donations']) < 4:
            builder.add(prev_p, to_start)
        else:
            builder.add(prev_p, to_start, next_p)

        don_message = await generate_message(data)
        await message.answer(don_message, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    else:
        await message.answer("Похоже произошла ошибка!")


async def generate_message(data: dict):
    quantity = data.get('quantity_donation')
    donations = data.get('donations')

    if not donations:
        full_message = 'Донаций нету'
        return full_message
    donations_text = ''
    for donation in donations:
        is_free = 'Безвозмездная' if donation.get('is_free') else 'НЕбезвозмездная'
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
