from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

from api.network_worker import NetWorkWorker

API_TOKEN = 'YOUR_BOT_API_TOKEN'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def main(message: types.Message):
    # Создаем клавиатуру для ответа
    builder = InlineKeyboardBuilder()
    user_id = message.from_user.id
    name = message.from_user.first_name
    data = {
        "telegram_user_id": user_id,
    }

    try:
        response = await NetWorkWorker().get_model_by_params('user/login', data)
        if response and response.get('status') == "success":
            user_info = response.get('user_info')
            name_user = user_info.get('name')
            role = user_info.get('role')

            if role == 1:
                # Кнопки для администратора
                button_list_requests = InlineKeyboardButton(text="📋Запросы на регистрацию",
                                                            callback_data="get_reg_requests")
                button_list_donation_all = InlineKeyboardButton(text="🩸Донации по дате",
                                                                callback_data="get_donation_list")
                button_list_donation_by_name = InlineKeyboardButton(text="🧾Донации пользователя",
                                                                    callback_data="get_users_donation")

                builder.add(button_list_requests, button_list_donation_all, button_list_donation_by_name)
                await message.reply(
                    f"Добро пожаловать в панель администратора {name}, у нас вы записаны как {name_user}",
                    reply_markup=builder.as_markup()
                )

            else:
                # Кнопки для обычного пользователя
                button_info = InlineKeyboardButton(text="ℹ️ Информация о пользователе", callback_data="get_user_info")
                button_donations = InlineKeyboardButton(text="🩸Мой список донаций", callback_data="get")
                button_achievement = InlineKeyboardButton(text="🏆 Мои достижения", callback_data="get_")

                builder.add(button_info, button_donations, button_achievement)
                await message.reply(f"Добро пожаловать, {name}!", reply_markup=builder.as_markup())

        else:
            # Кнопка регистрации для незарегистрированных пользователей
            button_reg = InlineKeyboardButton(text="📝 Зарегистрироваться")
            builder.add(button_reg)
            await message.reply(
                "Похоже, вы еще не зарегистрированы! Но мы можем это исправить)",
                reply_markup=builder.as_markup()
            )

    except Exception as e:
        print(e)
        await message.reply("Ой, произошла ошибка!")


if __name__ == '__main__':
    dp.start_polling(bot, skip_updates=True)
