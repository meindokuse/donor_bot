from http.client import responses

from aiogram import Bot, Dispatcher, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton

from api.network_worker import NetWorkWorker
from models.donation import DonationCreate
from aiogram.utils.keyboard import InlineKeyboardBuilder


class DonationStates(StatesGroup):
    owner = State()
    group = State()
    kell = State()
    tromb = State()
    plazma = State()
    rezus = State()
    org = State()


donation_data = {}
add_donation_states = Router()


async def add_donation_handler(dp: Dispatcher, bot: Bot):
    @dp.callback_query(func=lambda call: call.data == "add_donation")
    async def handle_donation_start(message: types.Message,state: FSMContext):
        chat_id = message.chat.id
        await bot.send_message(chat_id, "Введите имя владельца донации:")


        # Сохраняем состояние пользователя (ожидание ввода имени владельца)
        donation_data[chat_id] = {}
        await state.set_state(DonationStates.group)

    @add_donation_states.message(DonationStates.group)
    async def get_owner(message: types.Message,state: FSMContext):
        chat_id = message.chat.id
        owner = message.text
        params = {
            "name":owner
        }
        result = await NetWorkWorker().get_model_by_params("admin/get_user_by_name",params)
        if result:
            donation_data[chat_id]['owner'] = owner

            await bot.send_message(chat_id, "Введите группу донации:")
            await state.set_state(DonationStates.kell)

        else:
            await bot.send_message(chat_id,"Пользователя с таким ФИО не существует, попробуйте еще раз")


    @add_donation_states.message(DonationStates.kell)
    async def get_group(message: types.Message,state: FSMContext):
        chat_id = message.chat.id
        group = message.text

        donation_data[chat_id]['group'] = group

        await bot.send_message(chat_id, "Введите значение для kell:")
        await state.set_state(DonationStates.tromb)

    @add_donation_states.message(DonationStates.tromb)
    async def get_kell(message: types.Message,state: FSMContext):
        chat_id = message.chat.id
        kell = message.text

        donation_data[chat_id]['kell'] = kell

        await bot.send_message(chat_id, "Введите значение для tromb:")
        await state.set_state(DonationStates.plazma)

    @add_donation_states.message(DonationStates.plazma)
    async def get_tromb(message: types.Message,state: FSMContext):
        chat_id = message.chat.id
        tromb = message.text

        donation_data[chat_id]['tromb'] = tromb

        await bot.send_message(chat_id, "Введите значение для plazma:")
        await state.set_state(DonationStates.rezus)

    @add_donation_states.message(DonationStates.rezus)
    async def get_plazma(message: types.Message,state: FSMContext):
        chat_id = message.chat.id
        plazma = message.text

        donation_data[chat_id]['plazma'] = plazma

        await bot.send_message(chat_id, "Введите значение для rezus:")
        await state.set_state(DonationStates.org)


    @add_donation_states.message(DonationStates.org)
    async def get_org(message: types.Message):
        chat_id = message.chat.id
        org = message.text

        donation_data[chat_id]['org'] = org

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

        builder = InlineKeyboardBuilder()

        button1 = InlineKeyboardButton(text="Готово", callback_data="send_donation_to_server")
        button2 = InlineKeyboardButton(text="Начать заново", callback_data="add_donation")

        builder.add(button1, button2)

        # добавить код для сохранения данных в базе данных
        await bot.send_message(chat_id, (
            f"Данные о донации успешно сохранены!\nВаши данные:\nВладелец: {donation.owner}\n"
            f"Группа: {donation.group}\nKell: {donation.kell}\nTromb: {donation.tromb}\n"
            f"Plazma: {donation.plazma}\nRezus: {donation.rezus}\nДата: {donation.date}\nОрганизация: {donation.org}"
        ))

    @dp.callback_query(lambda call: call.data == "send_donation_to_server")
    async def send_model(message: types.Message,state: FSMContext):
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

        response = await NetWorkWorker().send_model("donation", model_data)
        if response:
            response_data = await response.json()
            if response_data.get('status') == 'success':
                await bot.send_message(chat_id,
                                       "Данные по донации отправлены")

        else:
            await bot.send_message(chat_id, "Похоже что то пошло не так, попробуйте позже")

        del donation_data[chat_id]
        await state.clear()


