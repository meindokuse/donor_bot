import asyncio

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

from api.network_worker import NetWorkWorker
from cleaner import clear_all
from aiogram.fsm.context import FSMContext

from user_services.login_service import login_router
from user_services.admin.registration_service import reg_user_router
from donation_services.admin.add_donation_service import add_donation_router
from donation_services.admin.get_info_users_donations import get_info_donation_user_router
from donation_services.admin.get_donations_by_date import get_all_donations
from donation_services.get_all_my_donation import get_all_my_donation
from donation_services.admin.get_table_users import router as get_table_users_router

API_TOKEN = '7530930015:AAFJqvJUpaFUK93qZ73z-k01Y0KBtVIejyQ'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

dp.include_router(reg_user_router)
dp.include_router(add_donation_router)
dp.include_router(get_info_donation_user_router)
dp.include_router(login_router)
dp.include_router(get_all_donations)
dp.include_router(get_all_my_donation)
dp.include_router(get_table_users_router)


@dp.message(CommandStart())
async def main(message: types.Message, state: FSMContext):
    await main_fun(message)
    await state.clear()

@dp.callback_query(F.data == 'main')
async def main_call(call: types.CallbackQuery, state: FSMContext):
    await main_fun(call.message)
    await state.clear()


async def main_fun(message: types.Message):
    await message.delete()
    builder = InlineKeyboardBuilder()
    user_id = message.chat.id
    await clear_all(user_id)
    name = message.from_user.first_name
    data = {
        "telegram_id": str(user_id),
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

                button_get_table_users = InlineKeyboardButton(text="📋Таблица пользователей",
                                                              callback_data="get_user_table")

                builder.add(button_list_requests, button_list_donation_all, button_list_donation_by_name,
                            button_reg_user, button_get_table_users)
                builder.adjust(2)

                await message.answer(
                    f"Добро пожаловать в панель администратора {name}, у нас вы записаны как {name_user}",
                    reply_markup=builder.as_markup()
                )

            else:
                # Кнопки для обычного пользователя
                button_info = InlineKeyboardButton(text="ℹ️ Информация о пользователе", callback_data="login")
                button_donations = InlineKeyboardButton(text="🩸Мой список донаций",
                                                        callback_data="get_all_my_donation")
                button_achievement = InlineKeyboardButton(text="🏆 Мои достижения", callback_data="get_achievments")

                builder.add(button_info, button_donations, button_achievement)
                builder.adjust(1)
                await message.answer(f"Добро пожаловать, {name}!", reply_markup=builder.as_markup())

        else:
            await message.answer(
                "Похоже,что вы еще не зарегистрированы!",
            )

    except Exception as e:
        print(e)
        await message.answer("Ой, произошла ошибка!")


if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot, skip_updates=True))
