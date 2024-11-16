import asyncio
import os

import aiohttp
from aiogram import types, Router, F
from aiogram.types import CallbackQuery

from api.network_worker import NetWorkWorker
from aiohttp import ClientError
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

router = Router()


@router.callback_query(F.data == 'get_user_table')
async def get_user_table(call: CallbackQuery):
    await call.message.delete()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="В меню", callback_data="main")],
    ])

    try:

        async with aiohttp.ClientSession() as session:
            async with session.get('http://192.168.1.66:8000/user/get_table') as response:
                if response.status == 200:
                    # Save the file locally before sending it
                    file_path = 'temp_donations.xlsx'
                    with open(file_path, 'wb') as f:
                        f.write(await response.read())

                    # Send the file to the user
                    file = types.FSInputFile(file_path)
                    await call.message.answer_document(file, caption="Ваша таблица", reply_markup=keyboard)

                    os.remove(file_path)
                else:
                    await call.message.reply("Failed to fetch the file.")

    except ClientError as e:
        await call.message.answer(f"Сетевая ошибка: {e}", reply_markup=keyboard)

    except asyncio.TimeoutError:
        await call.message.answer("Ошибка: время ожидания запроса истекло.", reply_markup=keyboard)

    except Exception as e:
        await call.message.answer(f"Произошла неизвестная ошибка: {e}", reply_markup=keyboard)
