from aiogram import types, Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from api.network_worker import NetWorkWorker
from aiogram.utils.keyboard import InlineKeyboardBuilder


class GetDonationDate(StatesGroup):
    start = State()
    get_date = State()


get_all_donations = Router()

pager = {}


@get_all_donations.callback_query(F.data == 'get_donation_list')
async def get_donations_by_date(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.clear()
    message = query.message
    pager[message.chat.id] = {'page': 1, 'limit': 4}

    last_mes = await message.answer("Введите дату в формате\n YYYY-MM-DD-YYYY-MM-DD\n(Т.е начало - конец)")
    await state.set_state(GetDonationDate.get_date)
    await state.update_data(last_mes_id=last_mes.message_id)


@get_all_donations.message(GetDonationDate.get_date)
async def get_donations_by_date(message: types.Message, state: FSMContext, bot: Bot):
    state_data = await state.get_data()
    if state_data.get('get_date') is not None:
        dates = state_data['get_date']
    else:
        dates = message.text.split()
        await state.update_data(get_date=dates)

    await message.delete()
    await bot.delete_message(chat_id=message.chat.id, message_id=state_data['last_mes_id'])

    date_start = dates[0]
    date_end = dates[1]
    chat_id = message.chat.id

    params = {
        "page": pager[chat_id]['page'],
        "limit": pager[chat_id]['limit'],
        "start_date": date_start,
        "end_date": date_end
    }

    result = await NetWorkWorker().get_model_list(endpoint="donation/admin/get_all_donations", params=params)

    if result:
        data = result.get('data')

        builder = InlineKeyboardBuilder()
        prev_p = InlineKeyboardButton(
            text="⬅️",
            callback_data="prev_don_list"
        )
        next_p = InlineKeyboardButton(
            text="➡️",
            callback_data="next_don_list"
        )
        to_start = InlineKeyboardButton(
            text="В начало",
            callback_data="to_start"
        )
        if len(data['donations']) < 4 and pager[chat_id]['page'] == 1:
            builder.add()
        elif len(data['donations']) < 4:
            builder.add(prev_p, to_start)
        elif pager[chat_id]['page'] == 1:
            builder.add(to_start, next_p)
        else:
            builder.add(prev_p, to_start, next_p)

        don_message = await generate_message(data)

        await message.answer(don_message, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    else:
        await message.answer("Похоже произошла ошибка!")


@get_all_donations.callback_query(F.data == 'prev_don_list')
async def prev_p(query: CallbackQuery, state: FSMContext):
    chat_id = query.message.chat.id
    pager[chat_id]['page'] -= 1

    await query.message.delete()
    await send_paginated_donations(query, state, chat_id)


@get_all_donations.callback_query(F.data == 'next_don_list')
async def next_p(query: CallbackQuery, state: FSMContext):
    chat_id = query.message.chat.id
    pager[chat_id]['page'] += 1

    await query.message.delete()
    await send_paginated_donations(query, state, chat_id)


@get_all_donations.callback_query(F.data == 'to_start')
async def next_p(query: CallbackQuery, state: FSMContext):
    chat_id = query.message.chat.id
    pager[chat_id]['page'] = 1

    await query.message.delete()
    await send_paginated_donations(query, state, chat_id)


async def send_paginated_donations(call: CallbackQuery, state, chat_id):
    dates = await state.get_data()
    date_start, date_end = dates['get_date']

    params = {
        "page": pager[chat_id]['page'],
        "limit": pager[chat_id]['limit'],
        "start_date": date_start,
        "end_date": date_end
    }

    result = await NetWorkWorker().get_model_list(endpoint="donation/admin/get_all_donations", params=params)

    if result:
        data = result.get('data')

        builder = InlineKeyboardBuilder()
        prev_p = InlineKeyboardButton(
            text="⬅️",
            callback_data="prev_don_list"
        )
        next_p = InlineKeyboardButton(
            text="➡️",
            callback_data="next_don_list"
        )
        to_start = InlineKeyboardButton(
            text="В начало",
            callback_data="to_start"
        )
        to_main = InlineKeyboardButton(
            text="В меню",
            callback_data="main"
        )
        if len(data['donations']) < 4 and pager[chat_id]['page'] == 1:
            builder.add(to_main)
        elif len(data['donations']) < 4:
            builder.add(prev_p, to_start, to_main)
            builder.adjust(2)
        elif pager[chat_id]['page'] == 1:
            builder.add(to_start, next_p, to_main)
            builder.adjust(2)
        else:
            builder.add(prev_p, to_start, next_p, to_main)
            builder.adjust(3)

        don_message = await generate_message(data)
        print(don_message)
        await call.message.answer(don_message, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    else:
        builder = InlineKeyboardBuilder()

        to_main = InlineKeyboardButton(
            text="В меню",
            callback_data="main"
        )
        builder.add(to_main)
        await call.message.answer("Похоже произошла ошибка!", reply_markup=builder.as_markup())


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
