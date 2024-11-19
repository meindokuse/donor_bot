from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.enums import ParseMode

from api.network_worker import NetWorkWorker
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

login_router = Router()


@login_router.callback_query(F.data == 'login')
async def login_user(call: types.CallbackQuery, bot: Bot):
    chat_id = call.message.chat.id

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="В меню", callback_data="main")],
    ])
    params = {
        "telegram_id": str(chat_id)
    }
    try:

        json = await NetWorkWorker().get_model_by_params("user/login", params)
        print(json, params, call.message.from_user.id, chat_id)
        if json:
            user: dict = json.get("user")
            role = "Админ" if user.get("role_id") == 1 else "Донор"

            user_info = (
                f"Информация о вас:\n"
                f"Имя: {user.get("name")}\n"
                f"Группа крови: {user.get("group")}\n"
                f"Резус-фактор: {'+' if user.get("rezus") == 1 else '-'}\n"
                f"Kell: {user.get("kell")}\n"
                f"Роль: {role}"
            )

            formated = f'<blockquote>{user_info}</blockquote>'

            await bot.send_message(chat_id, formated, parse_mode=ParseMode.HTML,reply_markup=keyboard)
            await call.message.delete()

    except Exception as e:
        print(e)
        await bot.send_message(call.message.chat.id, "Произошла ошибка", reply_markup=keyboard)