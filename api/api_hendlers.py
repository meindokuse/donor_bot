from aiogram import Bot, Dispatcher, types

async def reg_api_hendlers(dp:Dispatcher,bot:Dispatcher):
    @dp.message_handler(commands=['send_model'])
    async def send_model(message: types.Message):
        