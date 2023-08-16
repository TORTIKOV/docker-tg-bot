from aiogram import types
from aiogram.types.web_app_info import WebAppInfo
from loader import dp
from repository import check_tgid_in_db, check_if_deliveryman, check_deliveryman_activity
import logging


@dp.message_handler(text='Главное меню')
async def command_help(message: types.Message) -> None:
    try:
        tgid = message.from_user.id
        if check_tgid_in_db(tgid):
            if check_if_deliveryman(tgid) and check_deliveryman_activity(tgid):
                reply_markup = types.ReplyKeyboardMarkup(row_width=1).add(types.KeyboardButton(text='Сделать заказ',
                                                                                               web_app=WebAppInfo(
                                                                                                   url='https://charming-cucurucho-1beba8.netlify.app')),
                                                                          types.KeyboardButton(text='Заказы'))
                await message.answer(text='Мы в главном меню.\nТут ты можешь заказть что-нибудь или доставить и '
                                          'заработать', reply_markup=reply_markup)
            else:
                reply_markup = types.ReplyKeyboardMarkup(row_width=1).add(types.KeyboardButton(text='Сделать заказ',
                                                                                            web_app=WebAppInfo(
                                                                                            url='https://charming-cucurucho-1beba8.netlify.app')),
                                                                      types.KeyboardButton(text='Стать доставщиком'))
                await message.answer(text='Мы в главном меню.\nТут ты можешь заказать что-нибудь', reply_markup=reply_markup)
        else:
            await message.answer(f'Сначала надо зарегестрироваться!', reply_markup=types.ReplyKeyboardMarkup().add(
                types.KeyboardButton(text='Регистрация',
                                     web_app=WebAppInfo(url='https://charming-cucurucho-1beba8.netlify.app/form'))))
    except Exception as err:
        logging.exception(err)


@dp.message_handler(commands='main_menu')
async def command_help(message: types.Message) -> None:
    try:
        tgid = message.from_user.id
        if check_tgid_in_db(tgid):
            if check_if_deliveryman(tgid) and check_deliveryman_activity(tgid):
                reply_markup = types.ReplyKeyboardMarkup(row_width=1).add(types.KeyboardButton(text='Сделать заказ',
                                                                                               web_app=WebAppInfo(
                                                                                                   url='https://charming-cucurucho-1beba8.netlify.app')),
                                                                          types.KeyboardButton(text='Заказы'))
                await message.answer(text='Мы в главном меню.\nТут ты можешь заказть что-нибудь или доставить и '
                                          'заработать', reply_markup=reply_markup)
            else:
                reply_markup = types.ReplyKeyboardMarkup(row_width=1).add(types.KeyboardButton(text='Сделать заказ',
                                                                                            web_app=WebAppInfo(
                                                                                            url='https://charming-cucurucho-1beba8.netlify.app')),
                                                                      types.KeyboardButton(text='Стать доставщиком'))
                await message.answer(text='Мы в главном меню.\nТут ты можешь заказать что-нибудь', reply_markup=reply_markup)
        else:
            await message.answer(f'Сначала надо зарегестрироваться!', reply_markup=types.ReplyKeyboardMarkup().add(
                types.KeyboardButton(text='Регистрация',
                                     web_app=WebAppInfo(url='https://charming-cucurucho-1beba8.netlify.app/form'))))
    except Exception as err:
        logging.exception(err)