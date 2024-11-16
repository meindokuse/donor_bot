from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types.text_quote import TextQuote
import constance
from api.network_worker import NetWorkWorker
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class DonationStates(StatesGroup):
    start = State()
    get_name = State()


get_info_donation_user_router = Router()
prom_mes = {}


@get_info_donation_user_router.callback_query(F.data == "get_users_donation")
async def get_info_users_donations(call: CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.delete()
    chat_id = call.message.chat.id
    last_mes = await bot.send_message(chat_id, "Введите имя пользователя")
    prom_mes[chat_id] = last_mes.message_id
    await state.set_state(DonationStates.get_name)


@get_info_donation_user_router.message(DonationStates.get_name)
async def get_name(message: types.Message, bot: Bot):
    await message.delete()
    chat_id = message.chat.id
    await bot.delete_message(chat_id=chat_id, message_id=prom_mes[chat_id])

    name = message.text
    params = {
        "name": name
    }

    result = await NetWorkWorker().get_model_by_params("user/check_exist", params)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="В меню", callback_data="main")],
    ])

    if result is not None and result.get('is_exist'):

        result_don = await NetWorkWorker().get_model_by_params("donation/admin/get_donations_info_from_user", params)

        message_text = await generate_message(result_don)

        await message.answer(text=message_text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    else:
        await bot.send_message(chat_id, "Пользователя с таким ФИО не существует, попробуйте еще раз",
                               reply_markup=keyboard)


async def format_donation_info(donation_info):
    # Асинхронное форматирование информации о донации
    formatted_info = ""
    for t, info in donation_info.items():
        last_donation = info["last_donation"]
        status = '✅' if info['status'] == 1 else '❌'
        text = (
            f"{t}:\n"
            f"  Количество донаций: {info['quantity_donation']}\n"
            f"  Последняя донация:\n"
            f"    - Дата: {last_donation.get('date')}\n"
            f"    - Организация: {last_donation.get('org')}\n"
            f"    - Безвозмездная: {'Да' if last_donation.get('is_free') else 'Нет'}\n"
            f"  Статус: {status}\n\n"
        )
        formatted_info += f"<blockquote>{text}</blockquote>"

    return formatted_info


async def generate_message(data: dict):
    user = data.get("user")
    donation_info = data.get("donation_info")

    kell = '+' if user.get('kell') == True else '-'
    rezus = '+' if user.get('rezus') == True else '-'

    user_info = (
        f"Информация о пользователе:\n"
        f"Имя: {user.get("name")}\n"
        f"Группа крови: {user.get("group")}\n"
        f"Резус-фактор: {rezus}\n"
        f"Kell: {kell}\n\n"
    )

    donation_details = await format_donation_info(donation_info)

    full_message = f"<blockquote>{user_info}</blockquote>" + donation_details
    return full_message
