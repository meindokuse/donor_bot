from typing import Optional
from aiogram import Bot, Dispatcher, types, Router,F

from api.network_worker import NetWorkWorker
from models.user import UserRead

login_router = Router()


@login_router.message(F.data == 'login')
async def login_user(message: types.Message, bot: Bot):
    chat_id = message.chat.id
    params = {
        "telegram_id": message.from_user.id
    }
    try:
        json = await NetWorkWorker().get_model_by_params("user/login", params)
        if json:
            user: dict = await json.get("user")
            role = "Админ" if user.get("role_id") == 1 else "Донор"

            user_info = (
                f"Информация о вас:\n"
                f"Имя: {user.get("name")}\n"
                f"Группа крови: {user.get("group")}\n"
                f"Резус-фактор: {'+' if user.get("rezus") == 1 else '-'}\n"
                f"Kell: {user.get("kell")}\n"
                f"Роль: {role}"
            )

            await bot.send_message(chat_id, user_info)
    except Exception as e:
        print(e)
        await bot.send_message(message.chat.id, "Произошла ошибка")
