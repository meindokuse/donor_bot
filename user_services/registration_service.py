from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from models import DonationCreate
import aiohttp
import asyncio
from api.network_worker import NetWorkWorker
from models.user import RegRequestCreate
user_data = {}


from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor

bot = Bot(token='YOUR_BOT_TOKEN')
dp = Dispatcher(bot)

# Состояния для регистрации
class RegistrationStates(StatesGroup):
    username = State()
    email = State()
    password = State()

# Хранилище данных о пользователях
user_data = {}

# Старт регистрации по кнопке callback
@dp.callback_query_handler(lambda call: call.data == "add_reg_request")
async def handle_registration_start(call: CallbackQuery):
    chat_id = call.message.chat.id
    await call.message.answer("Введите ваше имя пользователя:")
    await RegistrationStates.username.set()
    user_data[chat_id] = {}  # Начало сбора данных для пользователя

# Сохранение имени пользователя
@dp.message_handler(state=RegistrationStates.username)
async def get_username(message: Message, state: FSMContext):
    chat_id = message.chat.id
    username = message.text
    user_data[chat_id]['username'] = username

    await message.answer("Введите ваш email (или нажмите 'Пропустить'):")
    await RegistrationStates.email.set()  # Переход к следующему состоянию

# Сохранение email или переход по умолчанию
@dp.message_handler(state=RegistrationStates.email)
async def get_email(message: Message, state: FSMContext):
    chat_id = message.chat.id
    email = message.text if message.text.lower() != 'пропустить' else None
    user_data[chat_id]['email'] = email

    await message.answer("Введите ваш пароль:")
    await RegistrationStates.password.set()  # Переход к состоянию пароля

# Сохранение пароля и завершение регистрации
@dp.message_handler(state=RegistrationStates.password)
async def get_password(message: Message, state: FSMContext):
    chat_id = message.chat.id
    password = message.text
    telegram_id = str(chat_id)

    user_data[chat_id]['password'] = password

    # Формируем запрос для регистрации
    reg_request = {
        "username": user_data[chat_id]['username'],
        "telegram_id": telegram_id,
        "email": user_data[chat_id]['email'],
        "password": user_data[chat_id]['password']
    }

    await message.answer(
        f"Регистрация завершена!\nВаши данные:\n"
        f"Имя пользователя: {reg_request['username']}\n"
        f"Email: {reg_request['email']}\n"
        f"Telegram ID: {reg_request['telegram_id']}"
    )

    # Завершаем состояние и очищаем данные
    await state.finish()
    del user_data[chat_id]





