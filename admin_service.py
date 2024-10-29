import requests
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

SERVER_URL = 'http://localhost:8000/items/'


def get_item_from_server(index):
    response = requests.get(SERVER_URL, params={"index": index})
    return response.json()


def admin_buttons(bot: TeleBot):
    @bot.callback_query_handler(func=lambda call: call.data == 'get_reg_requests')
    def start_get_reg_requests(call):
        chat_id = call.message.chat.id
        index = 0
        show_item(chat_id,index,bot)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('prev_') or call.data.startswith('next_'))
    def callback_pagination(call):
        current_index = int(call.data.split('_')[1])

        new_index = 0

        # Определяем направление: вперед или назад
        if call.data.startswith('prev_'):
            new_index = current_index - 1
        elif call.data.startswith('next_'):
            new_index = current_index + 1

        # Показываем новый элемент
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Загрузка...")
        show_item(call.message.chat.id, new_index, bot)


def show_item(chat_id, index, bot):
    item_data = get_item_from_server(index)

    if "error" in item_data:
        bot.send_message(chat_id, item_data["error"])
        return

    item = item_data["item"]
    total = item_data["total"]

    # Создаем inline-кнопки
    markup = InlineKeyboardMarkup()

    # Кнопка "Назад", если индекс больше 0
    if index > 0:
        markup.add(InlineKeyboardButton("⬅️ Назад", callback_data=f"prev_{index}"))

    # Кнопка "Вперед", если есть следующие элементы
    if index < total - 1:
        markup.add(InlineKeyboardButton("➡️ Вперед", callback_data=f"next_{index}"))

    bot.send_message(chat_id, f"{item}", reply_markup=markup)
