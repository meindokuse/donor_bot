from typing import Optional
from aiogram import Router, Bot, F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton
from aiohttp import ClientResponse
from aiogram.utils.keyboard import InlineKeyboardBuilder
from api.network_worker import NetWorkWorker


class RegistrationStates(StatesGroup):
    name = State()
    telegram_id = State()
    group = State()
    rezus = State()
    kell = State()


user_data = {}
reg_user_router = Router()


@reg_user_router.callback_query(F.data == 'reg_user')
async def handle_registration_start(call: CallbackQuery, state: FSMContext):
    chat_id = call.from_user.id
    user_data[chat_id] = {}
    await call.message.answer("Введите ФИО пользователя:")
    await state.set_state(RegistrationStates.name)


@reg_user_router.message(RegistrationStates.name)
async def get_name(message: Message, state: FSMContext):
    chat_id = message.chat.id
    user_data[chat_id]['name'] = message.text
    await message.answer("Введите Telegram ID\nБудущий пользователь может узнать его через @getmyid_bot:")
    await state.set_state(RegistrationStates.telegram_id)


@reg_user_router.message(RegistrationStates.telegram_id)
async def get_telegram_id(message: Message, state: FSMContext):
    chat_id = message.chat.id
    user_data[chat_id]['telegram_id'] = message.text
    await message.answer("Введите номер группы:")
    await state.set_state(RegistrationStates.group)


@reg_user_router.message(RegistrationStates.group)
async def get_group(message: Message, state: FSMContext):
    chat_id = message.chat.id
    user_data[chat_id]['group'] = message.text
    await message.answer("Введите резус (+/-):")
    await state.set_state(RegistrationStates.rezus)


@reg_user_router.message(RegistrationStates.rezus)
async def get_rezus(message: Message, state: FSMContext):
    chat_id = message.chat.id
    user_data[chat_id]['rezus'] = message.text
    await message.answer("Введите келл:")
    await state.set_state(RegistrationStates.kell)


@reg_user_router.message(RegistrationStates.kell)
async def get_kell(message: Message):
    chat_id = message.chat.id
    user_data[chat_id]['kell'] = message.text

    builder = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Готово", callback_data="send_reg_request_to_server")],
        [InlineKeyboardButton(text="Начать заново", callback_data="reg_user")]
    ])

    await message.answer(
        f"Введенные данные:\n"
        f"ФИО: {user_data[chat_id]['name']}\n"
        f"Telegram ID: {user_data[chat_id]['telegram_id']}\n"
        f"Группа: {user_data[chat_id]['group']}\n"
        f"Резус: {user_data[chat_id]['rezus']}\n"
        f"Келл: {user_data[chat_id]['kell']}",
        reply_markup=builder
    )


@reg_user_router.callback_query(F.data == "send_reg_request_to_server")
async def send_model_to_server(call: CallbackQuery, bot: Bot):
    chat_id = call.from_user.id
    rezus = 1 if user_data[chat_id]['rezus'] == '+' else 0
    try:
        reg_request = {
            "name": user_data[chat_id]['name'],
            "telegram_id": user_data[chat_id]['telegram_id'],
            "group": int(user_data[chat_id]['group']),
            "rezus": rezus,
            "kell": int(user_data[chat_id]['kell'])
        }
        response: Optional[ClientResponse] = await NetWorkWorker().send_model(endpoint="user/register",
                                                                              model_data=reg_request)

        if response:
            builder = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="В начало", callback_data="main")],
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
            [InlineKeyboardButton(text="В начало", callback_data="main")]
        ])
        print(e)
        await bot.send_message(chat_id, "Похоже, что-то пошло не так, попробуйте позже", reply_markup=builder)
