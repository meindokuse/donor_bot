import asyncio

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

from api.network_worker import NetWorkWorker

from user_services.login_service import login_router
from user_services.admin.registration_service import reg_user_router
from donation_services.admin.add_donation_service import add_donation_router
from donation_services.admin.get_info_users_donations import get_info_donation_user_router
from donation_services.admin.get_donations_by_date import get_all_donations

API_TOKEN = '7530930015:AAFJqvJUpaFUK93qZ73z-k01Y0KBtVIejyQ'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

dp.include_router(reg_user_router)
dp.include_router(add_donation_router)
dp.include_router(get_info_donation_user_router)
dp.include_router(login_router)
dp.include_router(get_all_donations)


@dp.message(CommandStart())
async def main(message: types.Message):
    builder = InlineKeyboardBuilder()
    user_id = message.from_user.id
    name = message.from_user.first_name
    data = {
        "telegram_id": user_id,
    }

    try:
        response = await NetWorkWorker().get_model_by_params('user/login', data)
        if response:
            user_info = response.get('user')
            name_user = user_info.get('name')
            role = user_info.get('role_id')

            if role == 1:
                # Кнопки для администратора
                button_list_requests = InlineKeyboardButton(text="📋Добавить донацию",
                                                            callback_data="add_donation")
                button_list_donation_all = InlineKeyboardButton(text="🩸Все донации по дате",
                                                                callback_data="get_donation_list")
                button_list_donation_by_name = InlineKeyboardButton(text="🧾Донации пользователя",
                                                                    callback_data="get_users_donation")
                button_reg_user = InlineKeyboardButton(text="📋Регистрация пользователя",
                                                       callback_data="reg_user")

                builder.add(button_list_requests, button_list_donation_all, button_list_donation_by_name,
                            button_reg_user)
                builder.adjust(2)

                await message.reply(
                    f"Добро пожаловать в панель администратора {name}, у нас вы записаны как {name_user}",
                    reply_markup=builder.as_markup()
                )

            else:
                # Кнопки для обычного пользователя
                button_info = InlineKeyboardButton(text="ℹ️ Информация о пользователе", callback_data="about_me")
                button_donations = InlineKeyboardButton(text="🩸Мой список донаций",
                                                        callback_data="get_all_my_donation")
                button_achievement = InlineKeyboardButton(text="🏆 Мои достижения", callback_data="get_achievments")

                builder.add(button_info, button_donations, button_achievement)
                await message.reply(f"Добро пожаловать, {name}!", reply_markup=builder.as_markup())

        else:

            await message.reply(
                "Похоже,что вы еще не зарегистрированы!",
            )

    except Exception as e:
        print(e)
        await message.reply("Ой, произошла ошибка!")

# @dp.callback_query(F.data == 'main_after_back')
# async def main_back(call: types.CallbackQuery):

if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot, skip_updates=True))
