from typing import Optional
from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton
from aiohttp import ClientResponse
from api.network_worker import NetWorkWorker
from donation_services.admin.add_donation_service import last_mes_id_don


class RegistrationStates(StatesGroup):
    name = State()
    telegram_id = State()
    group = State()
    rezus = State()
    kell = State()


user_data = {}
reg_user_router = Router()
last_mes_reg = {}


@reg_user_router.callback_query(F.data == 'reg_user')
async def handle_registration_start(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    chat_id = call.from_user.id
    user_data[chat_id] = {}

    builder = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="В меню", callback_data="main")],
    ])
    last_mes = await call.message.answer("Введите ФИО пользователя:\n (лучше перепроверьте несколько раз 😉)",
                                         reply_markup=builder)
    last_mes_reg[chat_id] = last_mes.message_id
    await state.set_state(RegistrationStates.name)


@reg_user_router.callback_query(F.data == 'reg_state_name')
@reg_user_router.message(RegistrationStates.name)
async def get_name(event, state: FSMContext, bot: Bot):
    global chat_id

    if isinstance(event, CallbackQuery):
        chat_id = event.message.chat.id
        await bot.delete_message(chat_id, last_mes_reg[chat_id])

    elif isinstance(event, Message):
        chat_id = event.chat.id
        await bot.delete_message(chat_id, event.message_id)
        await bot.delete_message(chat_id, last_mes_reg[chat_id])

        params = {
            "name": event.text
        }

        result = await NetWorkWorker().get_model_by_params("user/check_exist", params)
        if result and (result.get('is_exist') == False):
            user_data[chat_id]['name'] = event.text.strip()

            builder = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Назад", callback_data="reg_user")],
            ])

            last_mes = await bot.send_message(chat_id=chat_id,
                                              text="Введите Telegram ID\nБудущий пользователь может узнать его через @getmyid_bot:",
                                              reply_markup=builder)
            last_mes_reg[chat_id] = last_mes.message_id

            await state.set_state(RegistrationStates.telegram_id)

        else:
            builder = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Назад", callback_data="reg_user")],
            ])

            last_mes = await bot.send_message(chat_id=chat_id,
                                              text="Пользователь с таким ФИО уже существует",
                                              reply_markup=builder)
            last_mes_reg[chat_id] = last_mes.message_id


@reg_user_router.callback_query(F.data == 'reg_state_telegram_id')
@reg_user_router.message(RegistrationStates.telegram_id)
async def get_telegram_id(event, state: FSMContext, bot: Bot):
    global chat_id

    if isinstance(event, Message):
        chat_id = event.chat.id
        user_data[chat_id]['telegram_id'] = event.text.strip()
        await bot.delete_message(chat_id, event.message_id)
        await bot.delete_message(chat_id, last_mes_reg[chat_id])
    if isinstance(event, CallbackQuery):
        chat_id = event.message.chat.id
        await bot.delete_message(chat_id, last_mes_reg[chat_id])

    builder = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="reg_state_name")],
    ])

    last_mes = await bot.send_message(chat_id=chat_id, text="Введите номер группы:\n Только число!!!",
                                      reply_markup=builder)
    last_mes_reg[chat_id] = last_mes.message_id
    await state.set_state(RegistrationStates.group)


@reg_user_router.callback_query(F.data == 'reg_state_group')
@reg_user_router.message(RegistrationStates.group)
async def get_group(event, state: FSMContext, bot: Bot):
    global chat_id

    builder = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="reg_state_telegram_id")],
    ])

    if isinstance(event, Message):
        chat_id = event.chat.id
        if event.text.strip() not in '0123456789':
            last_mes_id = await bot.send_message(chat_id=chat_id, text="Некоректный номер группы", reply_markup=builder)
            last_mes_id[chat_id] = last_mes_id.message_id
        user_data[chat_id]['group'] = event.text.strip()
        await bot.delete_message(chat_id, event.message_id)
        await bot.delete_message(chat_id, last_mes_id[chat_id])
    if isinstance(event, CallbackQuery):
        chat_id = event.message.chat.id
        await bot.delete_message(chat_id, last_mes_id[chat_id])

    last_mes = await bot.send_message(chat_id, "Введите резус (+/-):", reply_markup=builder)
    last_mes_id[chat_id] = last_mes.message_id
    await state.set_state(RegistrationStates.rezus)


@reg_user_router.callback_query(F.data == 'reg_state_rezus')
@reg_user_router.message(RegistrationStates.rezus)
async def get_rezus(event, state: FSMContext, bot: Bot):
    global chat_id

    if isinstance(event, Message):
        chat_id = event.chat.id
        user_data[chat_id]['rezus'] = event.text
        await bot.delete_message(chat_id, event.message_id)
        await bot.delete_message(chat_id, last_mes_reg[chat_id])
    if isinstance(event, CallbackQuery):
        chat_id = event.message.chat.id
        user_data[chat_id]['rezus'] = event.message.text
        await bot.delete_message(chat_id, last_mes_reg[chat_id])

    builder = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="reg_state_group")],
    ])
    last_mes = await bot.send_message(chat_id, "Введите келл (+/-):", reply_markup=builder)
    last_mes_reg[chat_id] = last_mes.message_id
    await state.set_state(RegistrationStates.kell)


@reg_user_router.callback_query(F.data == 'reg_state_kell')
@reg_user_router.message(RegistrationStates.kell)
async def get_kell(event, bot: Bot):
    global chat_id

    if isinstance(event, Message):
        chat_id = event.chat.id
        user_data[chat_id]['kell'] = event.text
        await bot.delete_message(chat_id, event.message_id)
        await bot.delete_message(chat_id, last_mes_reg[chat_id])
    if isinstance(event, CallbackQuery):
        chat_id = event.chat.id
        user_data[chat_id]['kell'] = event.message.text
        await bot.delete_message(chat_id, last_mes_reg[chat_id])

    builder = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Готово", callback_data="send_reg_request_to_server")],
        [InlineKeyboardButton(text="Начать заново", callback_data="reg_user")],
        [InlineKeyboardButton(text="Назад", callback_data="reg_state_rezus")]
    ])

    last_mes = await bot.send_message(chat_id,
                                      f"Введенные данные:\n"
                                      f"ФИО: {user_data[chat_id]['name']}\n"
                                      f"Telegram ID: {user_data[chat_id]['telegram_id']}\n"
                                      f"Группа: {user_data[chat_id]['group']}\n"
                                      f"Резус: {user_data[chat_id]['rezus']}\n"
                                      f"Келл: {user_data[chat_id]['kell']}",
                                      reply_markup=builder
                                      )

    last_mes_reg[chat_id] = last_mes.message_id


@reg_user_router.callback_query(F.data == "send_reg_request_to_server")
async def send_model_to_server(call: CallbackQuery, bot: Bot):
    await call.message.delete()
    chat_id = call.from_user.id
    rezus = True if user_data[chat_id]['rezus'] == '+' else False
    kell = True if user_data[chat_id]['kell'] == '+' else False
    try:
        reg_request = {
            "name": user_data[chat_id]['name'],
            "telegram_id": user_data[chat_id]['telegram_id'],
            "group": int(user_data[chat_id]['group']),
            "rezus": rezus,
            "kell": kell
        }
        response: Optional[ClientResponse] = await NetWorkWorker().send_model(endpoint="user/register",
                                                                              model_data=reg_request)

        if response:
            builder = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="В меню", callback_data="main")],
                [InlineKeyboardButton(text="Отправить еще один", callback_data="reg_user")]
            ])
            await bot.send_message(chat_id, "Пользователь успешно зарегистрирован", reply_markup=builder)
            del user_data[chat_id]
        else:
            raise Exception("Ошибка при регистрации")

    except Exception as e:
        builder = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Повторить отправку", callback_data="send_reg_request_to_server")],
            [InlineKeyboardButton(text="Начать заново", callback_data="reg_user")],
            [InlineKeyboardButton(text="В меню", callback_data="main")]
        ])
        print(e)
        await bot.send_message(chat_id, "Похоже, что-то пошло не так, попробуйте позже", reply_markup=builder)
