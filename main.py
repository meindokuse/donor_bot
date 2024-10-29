from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import aiohttp

API_TOKEN = 'YOUR_BOT_API_TOKEN'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # Создаем клавиатуру для ответа
    inline_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    user_id = message.from_user.id
    name = message.from_user.first_name
    data = {
        "telegram_user_id": user_id,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/api/user', params=data) as response:
                response_data = await response.json()
                status = response_data.get('status')
                
                if response.status == 200 and status == "success":
                    user_info = response_data.get('user_info')
                    name_user = user_info.get('name')
                    role = user_info.get('role')
                    
                    if role == 1:
                        # Кнопки для администратора
                        button_list_requests = InlineKeyboardButton("📋Запросы на регистрацию",callback_data="get_reg_requests")
                        button_list_donation_all = InlineKeyboardButton("🩸Донации по дате",callback_data="get_donation_list")
                        button_list_donation_by_name = InlineKeyboardButton("🧾Донации пользователя",callback_data="get_users_donation")
                        
                        inline_keyboard.add(button_list_requests, button_list_donation_all, button_list_donation_by_name)
                        await message.reply(
                            f"Добро пожаловать в панель администратора {name}, у нас вы записаны как {name_user}", 
                            reply_markup=inline_keyboard
                        )
                    
                    else:
                        # Кнопки для обычного пользователя 
                        button_info = InlineKeyboardButton("ℹ️ Информация о пользователе",callback_data="get_user_info")
                        button_donations = InlineKeyboardButton("🩸Мой список донаций",callback_data="get")
                        button_achievement = InlineKeyboardButton("🏆 Мои достижения", callback_data="get_")
                        
                        inline_keyboard.add(button_info, button_donations, button_achievement)
                        await message.reply(f"Добро пожаловать, {name}!", reply_markup=inline_keyboard)
                
                else:
                    # Кнопка регистрации для незарегистрированных пользователей
                    button_reg = InlineKeyboardButton("📝 Зарегистрироваться")
                    inline_keyboard.add(button_reg)
                    await message.reply(
                        "Похоже, вы еще не зарегистрированы! Но мы можем это исправить)", 
                        reply_markup=inline_keyboard
                    )

    except Exception as e:
        print(e)
        await message.reply("Ой, произошла ошибка!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

