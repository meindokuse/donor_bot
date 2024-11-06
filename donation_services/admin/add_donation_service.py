from http.client import responses

from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

from api.network_worker import NetWorkWorker
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


class DonationStates(StatesGroup):
    start = State()
    type = State()
    owner = State()
    org = State()
    is_free = State()


donation_data = {}
add_donation_router = Router()


@add_donation_router.callback_query(F.data == "add_donation")
async def add_donation(call: CallbackQuery, state: FSMContext, bot: Bot):
    chat_id = call.message.chat.id
    donation_data[chat_id] = {}

    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text="Цельная кровь"))
    keyboard.add(KeyboardButton(text="Тромбоциты"))
    keyboard.add(KeyboardButton(text="Плазма"))

    await bot.send_message(chat_id, "Введите тип донации:", reply_markup=keyboard.as_markup())

    await state.set_state(DonationStates.type)


@add_donation_router.message(DonationStates.type)
async def get_name(message: types.Message, state: FSMContext, bot: Bot):
    chat_id = message.chat.id
    donation_data[chat_id]["type"] = message.text
    await bot.send_message(chat_id, "Введите имя владельца донации:", reply_markup=ReplyKeyboardRemove())

    await state.set_state(DonationStates.owner)


@add_donation_router.message(DonationStates.owner)
async def get_owner(message: types.Message, state: FSMContext, bot: Bot):
    chat_id = message.chat.id
    owner = message.text
    params = {
        "name": owner
    }
    result = await NetWorkWorker().get_model_by_params("user/check_exist", params)
    if result and result.get('is_exist'):
        donation_data[chat_id]['owner'] = owner

        await bot.send_message(chat_id, "Введите организацию принимающую донации:")
        await state.set_state(DonationStates.org)

    else:
        await bot.send_message(chat_id, "Пользователя с таким ФИО не существует, попробуйте еще раз")
        await state.set_state(DonationStates.owner)


@add_donation_router.message(DonationStates.org)
async def get_group(message: types.Message, state: FSMContext, bot: Bot):
    chat_id = message.chat.id
    org = message.text

    donation_data[chat_id]['org'] = org

    await bot.send_message(chat_id, "Является ли эта донация безвозмездной?\n(+) если да, (-) если нет")

    await state.set_state(DonationStates.is_free)


@add_donation_router.message(DonationStates.is_free)
async def get_is_free(message: types.Message, state: FSMContext, bot: Bot):
    chat_id = message.chat.id
    is_free = message.text

    if is_free not in "+-":
        await bot.send_message(chat_id, "Нужно ввести + или -")

    donation_data[chat_id]['is_free'] = True if is_free == "+" else False

    builder = InlineKeyboardBuilder()

    button1 = InlineKeyboardButton(text="Готово", callback_data="send_donation_to_server")
    button2 = InlineKeyboardButton(text="Начать заново", callback_data="add_donation")

    builder.add(button1, button2)

    # добавить код для сохранения данных в базе данных
    await bot.send_message(chat_id, (
        f"Данные о донации:\nТип:{donation_data[chat_id]["type"]}\nВладелец: {donation_data[chat_id]['owner']}\n"
        f"Организация: {donation_data[chat_id]['org']}\nБезвозмездная: {is_free}"
    ), reply_markup=builder.as_markup())


@add_donation_router.callback_query(F.data == "send_donation_to_server")
async def send_model(call: CallbackQuery, bot: Bot):
    chat_id = call.message.chat.id

    # Подготовка данных для отправки
    model_data = {
        "owner": donation_data[chat_id]['owner'],
        "type": donation_data[chat_id]["type"],
        "org": donation_data[chat_id]['org'],
        "is_free": donation_data[chat_id]['is_free'],
    }
    builder = InlineKeyboardBuilder()

    response = await NetWorkWorker().send_model("donation/admin/add_donation", model_data)
    if response:
        button1 = InlineKeyboardButton(text="В начало", callback_data="main")
        button2 = InlineKeyboardButton(text="Отправить еще", callback_data="reg_user")
        builder.add(button1, button2)
        await bot.send_message(chat_id,
                               "Данные по донации отправлены", reply_markup=builder.as_markup())
        del donation_data[chat_id]
    else:
        button3 = InlineKeyboardButton(text="Повторить отправку", callback_data="send_reg_request_to_server")
        button2 = InlineKeyboardButton(text="Начать заново", callback_data="reg_user")
        button1 = InlineKeyboardButton(text="В начало", callback_data="main")
        builder.add(button1, button2, button3)
        await bot.send_message(chat_id, "Похоже что то пошло не так, попробуйте позже",
                               reply_markup=builder.as_markup())
