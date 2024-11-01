from typing import Optional
from aiogram import Bot, Dispatcher, types

from api.network_worker import NetWorkWorker
from models.user import UserRead

async def reg_handler_users_login(dp:Dispatcher,bot:Bot):
    @dp.message(commands=['login'])
    async def login_user(message : types.Message):
        chat_id = message.chat.id
        params ={
            "telegram_id":message.chat.id
        }
        try:
            json = await NetWorkWorker().get_model_by_params("user/",params)
            status = await json.get("status")
            if status == "success":
                user_info: UserRead = await json.get("user")
                
                email = user_info.email if user_info.email else "Не указан" 
                role = "Админ" if user_info.role_id == 1 else "Донор"
                await bot.send_message(chat_id, (
                    f"Ваши данные:\n"
                    f"ID: {user_info.id}\Имя: {user_info.name}\nEmail: {email}\n"
                    f"Роль: {role}\nЗарегистрирован: {user_info.registered_on}"
                ))
        except Exception as e:
           await bot.send_message(message.chat.id, "Произошла ошибка")

    
    

