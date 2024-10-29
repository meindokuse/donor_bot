from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from models import DonationCreate
import aiohttp
import asyncio
from api.network_worker import NetWorkWorker

donation_data = {}

async def donation_handler(dp:Dispatcher,bot:Bot):
    @dp.message_handler(func=lambda call: call.data == "add_donation")
    async def handle_donation_start(message: types.Message):
        chat_id = message.chat.id
        await bot.send_message(chat_id, "Введите имя владельца донации:")

        # Сохраняем состояние пользователя (ожидание ввода имени владельца)
        donation_data[chat_id] = {'step': 'owner'}

    @dp.message_handler(lambda message: message.chat.id in donation_data and donation_data[message.chat.id]['step'] == 'owner')
    async def get_owner(message: types.Message):
        chat_id = message.chat.id
        owner = message.text

        donation_data[chat_id]['owner'] = owner
        donation_data[chat_id]['step'] = 'group'

        await bot.send_message(chat_id, "Введите группу донации:")

    @dp.message_handler(lambda message: message.chat.id in donation_data and donation_data[message.chat.id]['step'] == 'group')
    async def get_group(message: types.Message):
        chat_id = message.chat.id
        group = message.text

        donation_data[chat_id]['group'] = group
        donation_data[chat_id]['step'] = 'kell'

        await bot.send_message(chat_id, "Введите значение для kell:")

    @dp.message_handler(lambda message: message.chat.id in donation_data and donation_data[message.chat.id]['step'] == 'kell')
    async def get_kell(message: types.Message):
        chat_id = message.chat.id
        kell = message.text

        donation_data[chat_id]['kell'] = kell
        donation_data[chat_id]['step'] = 'tromb'

        await bot.send_message(chat_id, "Введите значение для tromb:")

    @dp.message_handler(lambda message: message.chat.id in donation_data and donation_data[message.chat.id]['step'] == 'tromb')
    async def get_tromb(message: types.Message):
        chat_id = message.chat.id
        tromb = message.text

        donation_data[chat_id]['tromb'] = tromb
        donation_data[chat_id]['step'] = 'plazma'

        await bot.send_message(chat_id, "Введите значение для plazma:")

    @dp.message_handler(lambda message: message.chat.id in donation_data and donation_data[message.chat.id]['step'] == 'plazma')
    async def get_plazma(message: types.Message):
        chat_id = message.chat.id
        plazma = message.text

        donation_data[chat_id]['plazma'] = plazma
        donation_data[chat_id]['step'] = 'rezus'

        await bot.send_message(chat_id, "Введите значение для rezus:")

    @dp.message_handler(lambda message: message.chat.id in donation_data and donation_data[message.chat.id]['step'] == 'rezus')
    async def get_rezus(message: types.Message):
        chat_id = message.chat.id
        rezus = message.text

        donation_data[chat_id]['rezus'] = rezus
        donation_data[chat_id]['step'] = 'date'

        await bot.send_message(chat_id, "Введите дату донации (в формате YYYY-MM-DD):")

    @dp.message_handler(lambda message: message.chat.id in donation_data and donation_data[message.chat.id]['step'] == 'date')
    async def get_date(message: types.Message):
        chat_id = message.chat.id
        date = message.text

        donation_data[chat_id]['date'] = date
        donation_data[chat_id]['step'] = 'org'

        await bot.send_message(chat_id, "Введите организацию донации:")

    @dp.message_handler(lambda message: message.chat.id in donation_data and donation_data[message.chat.id]['step'] == 'org')
    async def get_org(message: types.Message):
        chat_id = message.chat.id
        org = message.text

        donation_data[chat_id]['org'] = org

        # Создаем объект донации и отправляем его в базу данных
        donation = DonationCreate(
            owner=donation_data[chat_id]['owner'],
            group=donation_data[chat_id]['group'],
            kell=donation_data[chat_id]['kell'],
            tromb=donation_data[chat_id]['tromb'],
            plazma=donation_data[chat_id]['plazma'],
            rezus=donation_data[chat_id]['rezus'],
            date=donation_data[chat_id]['date'],
            org=donation_data[chat_id]['org']
        )
         # Создание кнопки "Отправить"
        inline_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,)
        send_button = types.ReplyKeyboardButton("Отправить")
        send_button = types.ReplyKeyboardButton("Начать заново")

        inline_keyboard.add(send_button)

        # добавить код для сохранения данных в базе данных
        await bot.send_message(chat_id, (
            f"Данные о донации успешно сохранены!\nВаши данные:\nВладелец: {donation.owner}\n"
            f"Группа: {donation.group}\nKell: {donation.kell}\nTromb: {donation.tromb}\n"
            f"Plazma: {donation.plazma}\nRezus: {donation.rezus}\nДата: {donation.date}\nОрганизация: {donation.org}"
        ))
    @dp.message_handler(lambda message: message.text == "Отправить" and message.chat.id in donation_data)
    async def send_model(message: types.Message):
        chat_id = message.chat.id

        # Подготовка данных для отправки
        model_data = {
            "owner": donation_data[chat_id]['owner'],
            "group": donation_data[chat_id]['group'],
            "kell": donation_data[chat_id]['kell'],
            "tromb": donation_data[chat_id]['tromb'],
            "plazma": donation_data[chat_id]['plazma'],
            "rezus": donation_data[chat_id]['rezus'],
            "date": donation_data[chat_id]['date'],
            "org": donation_data[chat_id]['org'],
        }

        result = await NetWorkWorker().send_model("donation", model_data)
        if result:
            await bot.send_message(chat_id, "Данные о донации успешно отправлены!")
        else:
            await bot.send_message(chat_id, "Ошибка при отправке данных о донации.")

        # Удаляем данные после завершения
        del donation_data[chat_id]

    @dp.message_handler(lambda message: message.text == "Начать заново" and message.chat.id in donation_data)
    async def cancel_send_donation(message: types.Message):
        chat_id = message.chat.id

        del donation_data[chat_id]

        bot.send_message(chat_id,"/new_donation")

        
