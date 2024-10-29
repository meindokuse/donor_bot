import requests
from telebot import TeleBot


def user_buttons(bot: TeleBot):
    @bot.callback_query_handler(func=lambda call: call.data == 'user_info')
    def user_info(call):
        tg_id = call.message.from_user.id
        chat_id = call.message.chat.id

        try:
            response = requests.get('http://localhost:8000/api/user', params=tg_id)
            status = response.json().get('status')
            user: dict = response.json().get('user_info')
            email = user.get('email') if user.get('email') else 'Не указан'
            if response.status_code == 200 and status == "success":
                bot.send_message(chat_id,
                                 f"Ваши данные:\nИмя пользователя: {user.get("name")}\nEmail: {email}\nTelegram ID: {user.get("telegram_id")}\n Зарегистрирован: {user.get('registered_on')}"
                                 )
            else:
                bot.send_message(chat_id, "Не нашли вас")
        except Exception as e:
            print(e)
            bot.send_message(chat_id, "Ой, произошла ошибка!")

    @bot.callback_query_handler(func=lambda call: call.data == 'user_donations')
    def user_donations(call):
        tg_id = call.message.from_user.id
        chat_id = call.message.chat.id
        index = 0
        response = requests.get('http://localhost:8000/api/user', params=tg_id)
