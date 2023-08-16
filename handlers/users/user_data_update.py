from aiogram import types
from aiogram.types.web_app_info import WebAppInfo
from loader import dp
from repository import check_tgid_in_db
import logging


@dp.message_handler(commands=['update_info'])
async def command_update_info(message: types.Message) -> None:
    try:
        tgid = message.from_user.id
        if check_tgid_in_db(tgid):
            await message.answer(f'Обновляем информацию?', reply_markup=types.ReplyKeyboardMarkup(row_width=1).add(
                types.KeyboardButton(text='Обновить информацию',
                                     web_app=WebAppInfo(url='https://charming-cucurucho-1beba8.netlify.app/form')),
                types.KeyboardButton(text="Главное меню")))
        else:
            await message.answer(
                f'А обновлять то и нечего... Регистрируемся по кнопке ниже',
                reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton(text='Регистрация',
                                                                                  web_app=WebAppInfo(
                                                                                      url='https://charming-cucurucho-1beba8.netlify.app/form'))))
    except Exception as err:
        logging.exception(err)
