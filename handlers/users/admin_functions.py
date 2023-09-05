from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import dp
import db
from repository import check_tgid_in_db, add_deliveryman_to_db, check_if_deliveryman, update_deliveryman, \
    ban_deliveryman, unban_deliveryman, import_deliverymen, update_order_status, get_client_id_by_order_id,\
    update_deliveryman_username, add_admin_to_db, get_active_admins, check_if_admin, deactivate_admin, check_deliveryman_activity
import logging
from config.config import admin_id, deliverymen_id
from loader import bot


# Handler to add a deliveryman
@dp.message_handler(commands=['add_deliveryman'])
async def command_add_deliveryman(message: types.Message, state: FSMContext) -> None:
    try:
        tg_id = message.from_user.id
        moderator_id = get_active_admins()
        print(moderator_id)
        # Check if the user is an admin
        if tg_id not in moderator_id:
            await message.reply("Недостаточно авторитета для использования данной команды.")
            return

        # Ask the admin to enter the deliveryman info
        await message.reply("Введите данные о доставщике в формате:\n"
                            "id: {tg_id}\nusername: {username}\ndate: {date}\n\nТут дата - день когда пользователь"
                            " заблокируется, поэтому надоо ввести именно этот день")

        # Set the state to `wait_deliveryman_info` to handle the next message
        await state.set_state("wait_deliveryman_info")

    except Exception as err:
        logging.exception(err)


# Handler to process the deliveryman info
@dp.message_handler(state="wait_deliveryman_info", content_types=types.ContentTypes.TEXT)
async def add_deliveryman_info(message: types.Message, state: FSMContext) -> None:
    try:
        # Extract Telegram ID, username, and date from the message text
        message_text = message.text.strip()
        tg_id = None
        username = None
        date = None

        for line in message_text.split('\n'):
            key, value = line.split(':')
            if key.strip() == 'id':
                tg_id = int(value.strip())
            elif key.strip() == 'username':
                username = value.strip()
            elif key.strip() == 'date':
                date = value.strip()

        if tg_id is None or username is None or date is None:
            await message.reply("Некорректный формат данных. Введите данные в формате:\n"
                                "id: {tg_id}\nusername: {username}\ndate: {date}")
            await state.reset_state()
            return

        if not check_tgid_in_db(tg_id):
            await message.reply("Такого пользователя нет в БД. Сначала регистрация, потом доставки")
            await state.reset_state()
            return

        if check_if_deliveryman(tg_id):
            await message.reply("Уже доставщик")
            await state.reset_state()
            return

        # Add the deliveryman to the database
        success = add_deliveryman_to_db(tg_id, username, date)

        if success:
            await message.reply(f"Доставщик с Telegram ID {tg_id}, username {username} добавлен в базу данных. Будет работать до: {date}")
            await bot.send_message(text=f'Вам одобрен статус доставщика до {date}(не включительно)! Пропишите "/main_menu" и можете приступать к работе', chat_id=tg_id)
        else:
            await message.reply("Не удалось добавить доставщика. Проверьте правильность введенных данных.")

        # Reset the state after processing the message
        await state.reset_state()

    except Exception as err:
        logging.exception(err)


@dp.message_handler(commands=['update_deliveryman'])
async def command_update_deliveryman(message: types.Message, state: FSMContext) -> None:
    try:
        tg_id = message.from_user.id
        moderator_id = get_active_admins()

        # Check if the user is an admin
        if tg_id not in moderator_id:
            await message.reply("Недостаточно авторитета для использования данной команды.")
            return

        # Ask the admin to enter the Telegram ID and date of the deliveryman
        await message.reply("Введите данные для обновления Deliveryman в формате:\n"
                            "id: {tg_id}\ndate: {date}.\n\nТут дата - день когда пользователь заблокируется,"
                            " поэтому надоо ввести именно этот день")

        # Set the state to `wait_deliveryman_info_update` to handle the next message
        await state.set_state("wait_deliveryman_info_update")

    except Exception as err:
        logging.exception(err)


# Handler to process the deliveryman info for updating
@dp.message_handler(state="wait_deliveryman_info_update", content_types=types.ContentTypes.TEXT)
async def update_deliveryman_info(message: types.Message, state: FSMContext) -> None:
    try:
        # Extract Telegram ID and date from the message text
        message_text = message.text.strip()
        deliveryman_tg_id = None
        date = None

        for line in message_text.split('\n'):
            key, value = line.split(':')
            if key.strip() == 'id':
                deliveryman_tg_id = int(value.strip())
            elif key.strip() == 'date':
                date = value.strip()

        if deliveryman_tg_id is None or date is None:
            await message.reply("Некорректный формат данных. Введите данные в формате:\n"
                                "id: {tg_id}\ndate: {date}")
            await state.reset_state()
            return

        # Update the deliveryman's information in the database using the update_deliveryman function
        if update_deliveryman(deliveryman_tg_id, date):
            await message.reply("Информация о Deliveryman успешно обновлена.")
            await bot.send_message(text=f'Вам одобрен статус доставщика до {date}(не включительно)! Пропишите "/main_menu" и можете приступать к работе', chat_id=deliveryman_tg_id)
        else:
            await message.reply("Ошибка при обновлении информации Deliveryman.")

        # Reset the state after processing the message
        await state.reset_state()

    except Exception as err:
        logging.exception(err)


@dp.message_handler(commands=['update_username'])
async def command_update_deliveryman(message: types.Message, state: FSMContext) -> None:
    try:
        tg_id = message.from_user.id
        moderator_id = get_active_admins()
        # Check if the user is an admin
        if tg_id not in moderator_id:
            await message.reply("Недостаточно авторитета для использования данной команды.")
            return

        # Ask the admin to enter the Telegram ID of the deliveryman
        await message.reply("Введите данные в формате:\n"
                                "id: {tg_id}\nusername: {username}")

        # Set the state to `wait_deliveryman_tg_id` to handle the next message
        await state.set_state("wait_username_update")

    except Exception as err:
        logging.exception(err)


@dp.message_handler(state="wait_username_update")
async def update_deliveryman_tg_id(message: types.Message, state: FSMContext) -> None:
    try:
        # Get the entered Telegram ID and username from the message
        message_text = message.text.strip()
        for line in message_text.split('\n'):
            key, value = line.split(':')
            if key.strip() == 'id':
                tg_id = int(value.strip())
            elif key.strip() == 'username':
                new_username = value.strip()

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


@dp.message_handler(commands=['ban'])
async def command_update_deliveryman(message: types.Message, state: FSMContext) -> None:
    try:
        tg_id = message.from_user.id
        moderator_id = get_active_admins()
        # Check if the user is an admin
        if tg_id not in moderator_id:
            await message.reply("Недостаточно авторитета для использования данной команды.")
            return

        # Ask the admin to enter the Telegram ID of the deliveryman
        await message.reply("Введите Telegram ID пользователя:")

        # Set the state to `wait_deliveryman_tg_id` to handle the next message
        await state.set_state("wait_ban_tg_id")

    except Exception as err:
        logging.exception(err)


@dp.message_handler(state="wait_ban_tg_id")
async def update_deliveryman_tg_id(message: types.Message, state: FSMContext) -> None:
    try:
        # Get the entered Telegram ID from the message
        deliveryman_tg_id = message.text.strip()

        # Check if the provided Telegram ID belongs to an existing deliveryman
        if not check_if_deliveryman(deliveryman_tg_id):
            await message.reply("Пользователь не найден в базе Deliverymen.")
            await state.reset_state()
            return

        # Update the deliveryman's information in the database
        if ban_deliveryman(deliveryman_tg_id):
            await message.reply(f"Пользователь {deliveryman_tg_id} забанен")
            await bot.send_message(deliveryman_tg_id, "Возможность доставлять заказы прекращена.\n"
                                                      "Для выяснения обстоятельств пишите -> @OnDaWayHC")
            await state.reset_state()
            for admin_tg_id in admin_id:
                await bot.send_message(admin_tg_id, f"Пользователь {deliveryman_tg_id} заблокирован.")
        else:
            await message.reply("Ошибка при бане.")

        # Reset the state to None to complete the flow
        await state.reset_state()

    except Exception as err:
        logging.exception(err)


@dp.message_handler(commands=['unban'])
async def command_update_deliveryman(message: types.Message, state: FSMContext) -> None:
    try:
        tg_id = message.from_user.id
        moderator_id = get_active_admins()
        # Check if the user is an admin
        if tg_id not in moderator_id:
            await message.reply("Недостаточно авторитета для использования данной команды.")
            return

        # Ask the admin to enter the Telegram ID of the deliveryman
        await message.reply("Введите Telegram ID пользователя:")

        # Set the state to `wait_deliveryman_tg_id` to handle the next message
        await state.set_state("wait_unban_tg_id")

    except Exception as err:
        logging.exception(err)


@dp.message_handler(state="wait_unban_tg_id")
async def update_deliveryman_tg_id(message: types.Message, state: FSMContext) -> None:
    try:
        # Get the entered Telegram ID from the message
        deliveryman_tg_id = message.text.strip()

        # Check if the provided Telegram ID belongs to an existing deliveryman
        if not check_if_deliveryman(deliveryman_tg_id):
            await message.reply("Пользователь не найден в базе Deliverymen.")
            await state.reset_state()
            return

        # Update the deliveryman's information in the database
        if unban_deliveryman(deliveryman_tg_id):
            await message.reply(f"Пользователь {deliveryman_tg_id} разблокирован")
            await bot.send_message(deliveryman_tg_id, "Вы разблокированы")
            await state.reset_state()

            for admin_tg_id in admin_id:
                await bot.send_message(admin_tg_id, f"\t{deliveryman_tg_id} разблокирован")
        else:
            await message.reply("Ошибка при разбане.")

        # Reset the state to None to complete the flow
        await state.reset_state()

    except Exception as err:
        logging.exception(err)


@dp.message_handler(commands=['import'])
async def command_add_deliveryman(message: types.Message) -> None:
    try:
        tg_id = message.from_user.id
        id_string = ""
        counter = 0
        moderator_id = get_active_admins()
        # Check if the user is an admin
        if tg_id not in moderator_id:
            await message.reply("Недостаточно авторитета для использования данной команды.")
            return

        if await import_deliverymen():
            for id in deliverymen_id:
                if counter % 3 == 0:
                    id_string += '\n'
                id_string += f"{str(id)},\t"
                counter += 1

            await message.answer("Список доставщиков обновлен:" + id_string)
        else:
            await message.answer("Ошибка импорта:" + id_string)

    except Exception as err:
        logging.exception(err)


@dp.message_handler(commands=['delete_order'])
async def command_add_deliveryman(message: types.Message, state: FSMContext) -> None:
    try:
        tg_id = message.from_user.id
        moderator_id = get_active_admins()
        # Check if the user is an admin
        if tg_id not in admin_id and tg_id not in moderator_id:
            await message.reply("Недостаточно авторитета для использования данной команды.")
            return

        await message.reply("Введите ID Заказа:")
        await state.set_state("wait_delete_order")

    except Exception as err:
        logging.exception(err)


@dp.message_handler(state="wait_delete_order")
async def update_deliveryman_tg_id(message: types.Message, state: FSMContext) -> None:
    try:
        order_id = message.text.strip()

        if update_order_status(order_id, "Отменен"):
            await message.reply(f"Статус заказа {order_id} изменен на 'Отменен'")
            await bot.send_message(get_client_id_by_order_id(order_id), f"Статус заказа {order_id} изменен на 'Отменен")
        else:
            await message.reply("Ошибка отмены заказа.")

        # Reset the state to None to complete the flow
        await state.reset_state()

    except Exception as err:
        logging.exception(err)


@dp.message_handler(commands=['get_username'])
async def get_username(message: types.Message, state: FSMContext):
    try:
        # Get the username of the user who sent the message
        username = message.from_user.username

        if username:
            await message.answer(username)
        else:
            await message.answer("You don't have a username set.")

    except Exception as err:
        logging.exception(err)


@dp.message_handler(commands=['add_admin'])
async def add_admin(message: types.Message, state: FSMContext):
    try:
        tg_id = message.from_user.id
        if tg_id not in admin_id:
            await message.reply("Недостаточно авторитета для использования данной команды.")
            return

        await message.reply("Введите ID нового админа:")
        await state.set_state("wait_admin_id")

    except Exception as err:
        logging.exception(err)


@dp.message_handler(state='wait_admin_id')
async def wait_admin_id(message: types.Message, state: FSMContext):
    try:
        admin_tg_id = message.text.strip()

        # Check if the entered ID is valid
        if not admin_tg_id.isdigit():
            await message.reply("Некорректный ID админа. Пожалуйста, введите корректный ID.")
            return

        admin_tg_id = int(admin_tg_id)

        # Check if the admin is already in the database
        if check_if_admin(admin_tg_id):
            await message.reply("Этот админ уже есть в базе.")
            await state.reset_state()
            return

        # Add the new admin to the "moderator" table with status set to True
        if add_admin_to_db(admin_tg_id):
            await message.reply(f"Админ с ID {admin_tg_id} успешно добавлен.")
        else:
            await message.reply("Ошибка при добавлении админа.")

        # Reset the state to None to complete the flow
        await state.reset_state()

    except Exception as err:
        logging.exception(err)


@dp.message_handler(commands=['deactivate_admin'])
async def deactivate_admin(message: types.Message, state: FSMContext):
    try:
        tg_id = message.from_user.id
        if tg_id not in admin_id:
            await message.reply("Недостаточно авторитета для использования данной команды.")
            return

        await message.reply("Введите ID админа, которого вы хотите деактивировать:")
        await state.set_state("wait_deactivate_admin_id")

    except Exception as err:
        logging.exception(err)


@dp.message_handler(state='wait_deactivate_admin_id')
async def wait_deactivate_admin_id(message: types.Message, state: FSMContext):
    try:
        admin_tg_id = message.text.strip()

        # Check if the entered ID is valid
        if not admin_tg_id.isdigit():
            await message.reply("Некорректный ID админа. Пожалуйста, введите корректный ID.")
            return

        admin_tg_id = int(admin_tg_id)

        # Check if the admin is in the database and has status True
        if not check_if_admin(admin_tg_id):
            await message.reply("Админ с таким ID не найден.")
            await state.reset_state()
            return

        # Deactivate the admin by setting their status to False
        if deactivate_admin(admin_tg_id):
            await message.reply(f"Админ с ID {admin_tg_id} успешно деактивирован.")
        else:
            await message.reply("Ошибка при деактивации админа.")

        # Reset the state to None to complete the flow
        await state.reset_state()

    except Exception as err:
        logging.exception(err)


@dp.message_handler(commands=['ping'])
async def ping_deliverymen(message: types.Message) -> None:
    try:
        # Check if the user is an admin or has the authority to send this command
        tg_id = message.from_user.id

        # Check if the user is an admin
        if not check_if_admin(tg_id):
            await message.reply("Недостаточно авторитета для использования данной команды.")
            return

        conn = db.connection
        cursor = conn.cursor()

        # Count the number of orders with 'Создан' status
        cursor.execute('''
            SELECT COUNT(*) FROM "order"
            WHERE status = 'Создан'
        ''')
        order_count = cursor.fetchone()[0]

        # Get the list of active deliverymen
        cursor.execute('''
            SELECT tg_id FROM "deliverymen"
            WHERE status = True
        ''')
        deliverymen = cursor.fetchall()
        counter = 0
        # Send a message to each active deliveryman with the order count
        for deliveryman in deliverymen:
            deliveryman_tg_id = deliveryman[0]
            try:
                await bot.send_message(deliveryman_tg_id, f"Количество активных заказов: {order_count}!\nМожно залутать чего-нибудь")
                counter +=1
            except Exception as err:
                print(deliveryman_tg_id)
                logging.exception(err)
        print(f"pinged {counter} users")
    except Exception as err:
        logging.exception(err)