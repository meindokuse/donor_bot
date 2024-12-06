from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from api.network_worker import NetWorkWorker
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder, InlineKeyboardMarkup


class DonationStates(StatesGroup):
    type = State()
    owner = State()
    org = State()
    is_free = State()


donation_data = {}
add_donation_router = Router()
last_mes_id_don = {}


@add_donation_router.callback_query(F.data == "add_donation")
async def add_donation(call: CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.delete()
    chat_id = call.message.chat.id
    donation_data[chat_id] = {}

    # Инлайн-клавиатура с типами донации и кнопкой "Назад"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Цельная кровь", callback_data="Цельная кровь")],
        [InlineKeyboardButton(text="Тромбоциты", callback_data="Тромбоциты")],
        [InlineKeyboardButton(text="Плазма", callback_data="Плазма")],
        [InlineKeyboardButton(text="В меню", callback_data="main")]
    ])

    last_mes = await bot.send_message(chat_id, "Выберите тип донации:", reply_markup=keyboard)
    last_mes_id_don[chat_id] = last_mes.message_id

    await state.set_state(DonationStates.type)


@add_donation_router.callback_query(F.data == "don_state_type")
@add_donation_router.callback_query(F.data.in_(["Цельная кровь", "Тромбоциты", "Плазма"]))
async def get_name(event, state: FSMContext, bot: Bot):
    global chat_id

    if isinstance(event, CallbackQuery):
        chat_id = event.message.chat.id
        await bot.delete_message(chat_id, last_mes_id_don[chat_id])
        donation_data[chat_id]["type"] = event.data

    elif isinstance(event, Message):
        chat_id = event.chat.id
        await bot.delete_message(chat_id, event.message_id)
        await bot.delete_message(chat_id, last_mes_id_don[chat_id])
        donation_data[chat_id]["type"] = event.text

    builder = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="add_donation")],
    ])

    last_mes = await bot.send_message(
        chat_id, "Введите ФИО владельца донации:",
        reply_markup=builder)
    last_mes_id_don[chat_id] = last_mes.message_id
    await state.set_state(DonationStates.owner)


@add_donation_router.callback_query(F.data == "don_state_owner")
@add_donation_router.message(DonationStates.owner)
async def get_owner(event, state: FSMContext, bot: Bot):
    global chat_id
    global owner

    builder = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="don_state_type")],
    ])

    if isinstance(event, CallbackQuery):
        chat_id = event.message.chat.id
        await bot.delete_message(chat_id, last_mes_id_don[chat_id])
        owner = event.message.text

        last_mes = await bot.send_message(
            chat_id=chat_id,
            text="Введите организацию принимающую донации:",
            reply_markup=builder
        )
        last_mes_id_don[chat_id] = last_mes.message_id
        await state.set_state(DonationStates.org)

    elif isinstance(event, Message):
        chat_id = event.chat.id
        owner = event.text
        await bot.delete_message(chat_id, event.message_id)
        await bot.delete_message(chat_id, last_mes_id_don[chat_id])
        donation_data[chat_id]["owner"] = event.text

        params = {
            "name": owner
        }

        result = await NetWorkWorker().get_model_by_params("user/check_exist", params)
        if result and result.get('is_exist'):
            print(result.get('is_exist'))
            donation_data[chat_id]['owner'] = owner
            last_mes = await bot.send_message(
                chat_id=chat_id,
                text="Введите организацию принимающую донации:",
                reply_markup=builder
            )
            last_mes_id_don[chat_id] = last_mes.message_id
            await state.set_state(DonationStates.org)

        else:
            last_mes = await bot.send_message(chat_id, "Пользователя с таким ФИО не существует, попробуйте еще раз")
            last_mes_id_don[chat_id] = last_mes.message_id
            await state.set_state(DonationStates.owner)


@add_donation_router.callback_query(F.data == "don_state_group")
@add_donation_router.message(DonationStates.org)
async def get_group(event, state: FSMContext, bot: Bot):
    global chat_id

    if isinstance(event, CallbackQuery):
        chat_id = event.message.chat.id
        await bot.delete_message(chat_id, last_mes_id_don[chat_id])
        donation_data[chat_id]['org'] = event.message.text

    elif isinstance(event, Message):
        chat_id = event.chat.id
        await bot.delete_message(chat_id, event.message_id)
        await bot.delete_message(chat_id, last_mes_id_don[chat_id])
        donation_data[chat_id]['org'] = event.text

    builder = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="+", callback_data="+_is_free")],
        [InlineKeyboardButton(text="-", callback_data="-_if_free")],
        [InlineKeyboardButton(text="Назад", callback_data="don_state_owner")],
    ])

    last_mes = await bot.send_message(
        chat_id=chat_id,
        text="Является ли эта донация безвозмездной?\n(+) если да, (-) если нет",
        reply_markup=builder
    )
    last_mes_id_don[chat_id] = last_mes.message_id


@add_donation_router.callback_query(F.data.in_(["+_is_free", "-_if_free"]))
async def get_is_free(event: CallbackQuery, bot: Bot):

    chat_id = event.message.chat.id
    await bot.delete_message(chat_id, last_mes_id_don[chat_id])
    is_free = event.data[0]

    donation_data[chat_id]['is_free'] = True if is_free == "+" else False

    builder = InlineKeyboardBuilder()

    button1 = InlineKeyboardButton(text="Готово", callback_data="send_donation_to_server")
    button2 = InlineKeyboardButton(text="Начать заново", callback_data="add_donation")
    button3 = InlineKeyboardButton(text="Назад", callback_data="don_state_group")

    builder.add(button1, button2, button3)

    last_mes_id = await bot.send_message(chat_id, (
        f"Данные о донации:\nТип:{donation_data[chat_id]["type"]}\nВладелец: {donation_data[chat_id]['owner']}\n"
        f"Организация: {donation_data[chat_id]['org']}\nБезвозмездная: {is_free}"
    ), reply_markup=builder.as_markup())

    last_mes_id_don[chat_id] = last_mes_id.message_id


@add_donation_router.callback_query(F.data == "send_donation_to_server")
async def send_model(call: CallbackQuery, bot: Bot):
    await call.message.delete()

    chat_id = call.message.chat.id

    # Подготовка данных для отправки
    model_data = {
        "owner": donation_data[chat_id]['owner'],
        "type": donation_data[chat_id]["type"],
        "org": donation_data[chat_id]['org'],
        "is_free": donation_data[chat_id]['is_free'],
    }
    builder = InlineKeyboardBuilder()

    response = await NetWorkWorker().send_model("donation/admin/add_donation", model_data)
    if response:
        button1 = InlineKeyboardButton(text="В меню", callback_data="main")
        button2 = InlineKeyboardButton(text="Отправить еще", callback_data="add_donation")
        builder.add(button1, button2)
        await bot.send_message(chat_id,
                               "Данные по донации отправлены", reply_markup=builder.as_markup())
        del donation_data[chat_id]
    else:
        button3 = InlineKeyboardButton(text="Повторить отправку", callback_data="send_reg_request_to_server")
        button2 = InlineKeyboardButton(text="Начать заново", callback_data="reg_user")
        button1 = InlineKeyboardButton(text="В меню", callback_data="main")
        builder.add(button1, button2, button3)
        await bot.send_message(chat_id, "Похоже что то пошло не так, попробуйте позже",
                               reply_markup=builder.as_markup())

    del last_mes_id_don[chat_id]
