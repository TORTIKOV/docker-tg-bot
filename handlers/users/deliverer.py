from aiogram import types
from loader import dp
from repository import check_tgid_in_db, check_if_deliveryman, update_deliveryman_username
from aiogram.types.web_app_info import WebAppInfo
import logging
from config.config import admin_id
from aiogram.dispatcher import FSMContext


@dp.message_handler(text='Стать доставщиком')
async def command_deliverer(message: types.Message) -> None:
    try:
        tgid = message.from_user.id
        if check_tgid_in_db(tgid):
            await message.answer(f'Ты собираешься стать доставщиком!\nВвиду того, что ты будешь это делать не '
                                 f'бесплатно, '
                             f'тебе придется немного поделиться со мной.\nSber:')
            await message.answer(f'2202 2010 7411 2836')
            await message.answer(f'Подкинь сюда 100 шейкелей.\n'
                             f'Как шейкели придут, я лично добавлю тебя в список доставщиков и ты сможешь спокойно '
                             f'лутать свое золотишко.')
            await message.answer(f'Для связи с клиентами, тебе нужно скинуть в комментариях к платежу свой TG ID и username\n'
                             f'Ткни на кнопку ниже и я тебе их пришлю', reply_markup=types.ReplyKeyboardMarkup(row_width=1).add(types.KeyboardButton(text='Прислать'), types.KeyboardButton(text="Главное меню")))
        else:
            await message.answer(f'Сначала надо зарегестрироваться!', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton(text='Регистрация', web_app=WebAppInfo(url='https://charming-cucurucho-1beba8.netlify.app/form'))))
    except Exception as err:
        logging.exception(err)


@dp.message_handler(text='Прислать')
async def command_idGetter(message: types.Message) -> None:
    try:
        tg_id = message.from_user.id
        if check_tgid_in_db(tg_id):
            username = message.from_user.username

            if username:
                await message.answer(f'id: {tg_id}\nusername: {username}')
            else:
                await message.answer("Похоже, что username не установлен. Установи его в настройках и возвращайся.", reply_markup=types.ReplyKeyboardMarkup(row_width=1).add(types.KeyboardButton(text='Прислать'), types.KeyboardButton(text="Главное меню")))
                return

            await message.answer(f'Просто скопируй сообщение выше и скинь в комментарии к платежу.\n'
                                 f'Как закончишь, тыкай на кнопку ниже и я пойду проверять твой запрос.\n'
                                 f'Время на обработку до 24 часов\n'
                                 f'Тыкай "Готово" и админ пойдет проверять твой запрос,'
                                 f' а если еще не готов, то тыкай "Главное меню"',
                                 reply_markup=types.ReplyKeyboardMarkup(row_width=1).add(types.KeyboardButton(text='Готово!'), types.KeyboardButton(text="Главное меню")))
        else:
            await message.answer(f'Сначала надо зарегестрироваться!', reply_markup=types.ReplyKeyboardMarkup().add(
            types.KeyboardButton(text='Регистрация',
                                 web_app=WebAppInfo(url='https://charming-cucurucho-1beba8.netlify.app/form'))))
    except Exception as err:
        logging.exception(err)


@dp.message_handler(text='Готово!')
async def command_payment(message: types.Message) -> None:
    try:
        tgid = message.from_user.id
        if check_tgid_in_db(tgid):
            reply_markup = types.ReplyKeyboardMarkup(row_width=1).add(types.KeyboardButton(text='Сделать заказ',
                                                                                           web_app=WebAppInfo(
                                                                                           url='https://charming-cucurucho-1beba8.netlify.app')))
            await message.answer(f'Всё, ждем! А пока можешь сделать заказ', reply_markup=reply_markup)

            for admin in admin_id:
                try:
                    text = 'Шекель летит на карман'
                    await dp.bot.send_message(chat_id=admin, text=text)
                except Exception as err:
                    logging.exception(err)
        else:
            await message.answer(f'Сначала надо зарегестрироваться!', reply_markup=types.ReplyKeyboardMarkup().add(
            types.KeyboardButton(text='Регистрация',
                             web_app=WebAppInfo(url='https://charming-cucurucho-1beba8.netlify.app/form'))))
    except Exception as err:
        logging.exception(err)


@dp.message_handler(commands='update_username')
async def update_username(message: types.Message, state: FSMContext):
    try:
        tg_id = message.from_user.id
        if check_tgid_in_db(tg_id):
            if check_if_deliveryman(tg_id):
                await message.answer(f'Введите новое имя в формате:\nusername')
                await state.set_state("wait_username")
            else:
                await message.answer(f'Сначала надо стать доставщиком', reply_markup=types.ReplyKeyboardMarkup(row_width=1).add(
                    types.KeyboardButton(text='Стать доставщиком'), types.KeyboardButton(text='Главное меню')
                ))

        else:
            await message.answer(f'Сначала надо зарегестрироваться!', reply_markup=types.ReplyKeyboardMarkup().add(
                types.KeyboardButton(text='Регистрация',
                                     web_app=WebAppInfo(url='https://charming-cucurucho-1beba8.netlify.app/form'))))
    except Exception as err:
        logging.exception(err)


@dp.message_handler(state="wait_username")
async def update_username_tg_id(message: types.Message, state: FSMContext):
    try:

        # Get the entered Telegram ID and username from the message
        new_username = message.text
        tg_id = message.from_user.id
        # Check if the provided Telegram ID belongs to an existing deliveryman
        if not check_if_deliveryman(tg_id):
            await message.reply("Пользователь не найден в базе Deliverymen.")
            await state.reset_state()
            return

        if tg_id is None or new_username is None:
            await message.reply("Некорректный формат данных. Введите данные в формате:\n"
                                "id: {tg_id}\nusername: {username}")
            await state.reset_state()
            return

        # Update the deliveryman's username in the database
        if update_deliveryman_username(tg_id, new_username):
            await message.reply(f"Имя пользователя @{new_username} успешно обновлено.")
        else:
            await message.reply("Ошибка при обновлении имени пользователя Deliveryman.")

        # Reset the state to None to complete the flow
        await state.reset_state()

    except Exception as err:
        logging.exception(err)