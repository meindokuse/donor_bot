from typing import Optional
from aiogram import Bot, Dispatcher,F,Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.types import InlineKeyboardButton
from aiohttp import ClientResponse
from aiogram.utils.keyboard import InlineKeyboardBuilder
from api.network_worker import NetWorkWorker

class RegistrationStates(StatesGroup):
    username = State()
    email = State()
    password = State()

    cancel = State()

user_data = {}
reg_states_router = Router()


async def reg_add_request_handler(dp:Dispatcher, bot: Bot):
    @dp.callback_query(lambda call: call.data == "add_reg_request")
    @reg_states_router(RegistrationStates.name)
    async def handle_registration_start(call: CallbackQuery):
        user_data[chat_id] = {}
        chat_id = call.message.chat.id
        await call.message.answer("Введите ваше имя пользователя:")
        await RegistrationStates.username.set()

    # Сохранение имени пользователя
    @reg_states_router.message(RegistrationStates.username)
    async def get_username(message: Message, state: FSMContext):
        chat_id = message.chat.id
        username = message.text
        user_data[chat_id]['username'] = username

        await message.answer("Введите ваш email (или нажмите 'Пропустить'):")
        await state.set_state(RegistrationStates.email)  # Переход к следующему состоянию

    # Сохранение email или переход по умолчанию
    @reg_states_router.message(RegistrationStates.email)
    async def get_email(message: Message, state: FSMContext):
        chat_id = message.chat.id
        email = message.text if message.text.lower() != 'пропустить' else None
        user_data[chat_id]['email'] = email

        await message.answer("Введите ваш пароль:")
        await state.set_state(RegistrationStates.password)  # Переход к состоянию пароля

    # Сохранение пароля и завершение регистрации
    @reg_states_router.message(RegistrationStates.password)
    async def get_password(message: Message, state: FSMContext):
        chat_id = message.chat.id
        password = message.text

        user_data[chat_id]['password'] = password

        # Формируем запрос для регистрации
        
        builder = InlineKeyboardBuilder()

        button1 = InlineKeyboardButton("Готово",callback_data="send_model_to_server")
        button2 = InlineKeyboardButton("Начать заново",callback_data="add_reg_request")

        builder.add(button1,button2)

        await bot.send_message(
            f"Ваши данные:\n"
            f"Имя пользователя: {user_data[chat_id]['username']}\n"
            f"Email: {user_data[chat_id]['email']}\n"
            f"Telegram ID: {user_data[chat_id]['telegram_id']}",
            reply_markup = builder.as_markup()
        )

    @dp.callback_query(lambda call: call.data == "send_model_to_server")
    async def send_model_to_server(call: CallbackQuery, state:FSMContext):
        chat_id = call.message.from_user.id
        reg_request = {
            "username": user_data[chat_id]['username'],
            "telegram_id": chat_id,
            "email": user_data[chat_id]['email'],
            "password": user_data[chat_id]['password']
        }
        response: Optional[ClientResponse] = NetWorkWorker().send_model('user/add_reg_request',reg_request)
        if response:
            response_data = await response.json()
            if response_data.get('status') == 'success':
                await bot.send_message(chat_id,"Запрос на регистрацию отправлен, ожидайте одобрения\nМы сообщим вам вердикт")
        
        else:
            await bot.send_message(chat_id,"Похоже что то пошло не так, попробуйте позже")

        del user_data[chat_id]
        await state.clear()
    
    






        






