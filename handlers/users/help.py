from aiogram import types
from loader import dp
import logging
from repository import check_tgid_in_db, check_if_deliveryman, check_deliveryman_activity
from aiogram.types.web_app_info import WebAppInfo


@dp.message_handler(commands=['help'])
async def command_help(message: types.Message) -> None:
    try:
        tg_id = message.from_user.id
        if check_tgid_in_db(tg_id):
            await message.answer('Если возникнут вопросы, то можешь писать сюда -> @OnDaWayHC\n')
            await message.answer('Главное меню - место, в котором ты можешь заказывать или становиться доставщиком\n'
                                 'Как работают заказы?\n'
                                 'Чтобы сделать заказ, в главном меню ты должен нажать на "Сделать заказ"\n'
                                 'Далее ты должен выбрать откуда доставлять, ввести время, '
                                 'до которого твое предложение будет актуальным, '
                                 'а так же место в которое надо доставить\n\n'
                                 'Метод оплаты. Так как мы студенты, денег у нас не много, а вот шоколада... '
                                 'Пиши в метод оплаты то, чем тебе удобно платить(Деньги/Сигареты/Бананы/Шоколад...).'
                                 'У нас ты сам формируешь предложение!\n\n'
                                 'Комментарий к заказу писать не обязательно, поэтому можешь тыкать "-". '
                                 'Всё равно потом с доставщиком в ЛС все вопросы решаются',
                                 reply_markup=types.ReplyKeyboardMarkup(row_width=1).add(
                                     types.KeyboardButton(text='Главное меню')))
            if check_if_deliveryman(tg_id) and check_deliveryman_activity(tg_id):
                await message.answer('Как доставлять?\n'
                                     'В главном меню есть копка "Заказы". Если туда нажать, '
                                     'то тебе начнут показываться актуальные заказы пользователей. '
                                     'Если считаешь, что тебе по пути и ты хочешь помочь,'
                                     ' а так же залутать чего-нибудь кошерного, то смело тыкай "Выполнять".\n\n',
                                     reply_markup=types.ReplyKeyboardMarkup(row_width=1).add(types.KeyboardButton(text='Главное меню')))
        else:
            await message.answer('Если возникнут вопросы, то можешь писать сюда -> @OnDaWayHC\n')
            await message.answer('Как работают заказы?\n'
                                 'Чтобы сделать заказ, в главном меню ты должен нажать на "Сделать заказ"\n'
                                 'Далее ты должен выбрать откуда доставлять, ввести время, '
                                 'до которого твое предложение будет актуальным, '
                                 'а так же место в которое надо доставить\n\n'
                                 'Метод оплаты\nТак как мы студенты, денег у нас не много, а вот шоколада... '
                                 'Пиши в "метод оплаты" то, чем тебе удобно платить(Деньги/Сигареты/Бананы/Шоколад...).'
                                 'У нас ты сам формируешь предложение!\n\n'
                                 'В комментарии к заказу лучше написать размер посылки, но много писать смысла нет. '
                                 'Всё равно потом с доставщиком в ЛС все вопросы решаются\n\n'
                                 'Давайте регистрироваться!',
                                 reply_markup=types.ReplyKeyboardMarkup(row_width=1).add(
                                     types.KeyboardButton(text='Регистрация', web_app=WebAppInfo(url='https://charming-cucurucho-1beba8.netlify.app/form'))))

    except Exception as err:
        logging.exception(err)
