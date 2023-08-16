from loader import dp, bot
import logging
from aiogram.types.web_app_info import WebAppInfo
from repository import check_tgid_in_db, check_if_deliveryman, check_deliveryman_activity, get_deliveryman_username,\
    update_deliveryman_username
from aiogram import types
from app import db
import datetime
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def username_acceptance(message: types.Message) -> bool:
    try:
        current_username = message.from_user.username
        tg_id = message.from_user.id
        if current_username:
            if current_username != get_deliveryman_username(tg_id):
                update_deliveryman_username(tg_id, current_username)
            return True
        else:
            return False
    except Exception as err:
        logging.exception(err)


@dp.message_handler(text='Заказы')
async def command_help(message: types.Message) -> None:
    try:
        tgid = message.from_user.id
        if check_tgid_in_db(tgid):
            if check_if_deliveryman(tgid) and check_deliveryman_activity(tgid):
                if username_acceptance(message):
                    conn = db.connection
                    cursor = conn.cursor()

                    # Get orders with 'Создан' status
                    cursor.execute('''
                                    SELECT id, order_place, delivery_option, until_date, until_time, payment_method, comment, dorm, floor, room
                                    FROM "order"
                                    WHERE status = 'Создан'
                                ''')

                    orders = cursor.fetchall()

                    for order in orders:
                        order_id, order_place, delivery_option, until_date, until_time, payment_method, comment, dorm, floor, room = order

                        # Check if the order's until_date and until_time are not expired
                        current_datetime = datetime.datetime.now()
                        order_datetime = datetime.datetime.combine(until_date, until_time)
                        if order_datetime <= current_datetime:
                            # Update the status of the expired order to "Просрочен"
                            cursor.execute('''
                                            UPDATE "order"
                                            SET status = 'Просрочен'
                                            WHERE id = %s
                                        ''', (order_id,))
                            conn.commit()
                            continue  # Skip displaying this order as it's expired

                        # Format the order information
                        form_info = f"Order ID: {order_id}\n"
                        form_info += f"Status: Создан\n"
                        form_info += f"Заказ из: {order_place}\n"

                        if delivery_option == 'KPP':
                            form_info += f"Куда доставить: КПП\n"
                        elif delivery_option == 'CP':
                            form_info += f"Куда доставить: ЦП\n"
                        else:
                            form_info += f"Общежитие: {dorm}\n"
                            if floor != 0:
                                form_info += f"Этаж: {floor}\n"
                                if room != 0:
                                    form_info += f"Комната: {room:02d}\n"

                        form_info += f"Крайний срок: {until_date}, {until_time}\n"
                        form_info += f"Метод оплаты: {payment_method}\n"
                        form_info += f"Комментарий к заказу: {comment}\n"

                        keyboard = InlineKeyboardMarkup(row_width=1)
                        button = InlineKeyboardButton(text="Выполнять", callback_data=f"execute:{order_id}")
                        keyboard.add(button)

                        await message.answer(form_info, reply_markup=keyboard)
                else:
                    await message.answer(text='Установите Username!(В настройках Telegram)')
            else:
                reply_markup = types.ReplyKeyboardMarkup(row_width=1).add(types.KeyboardButton(text='Сделать заказ',
                                                                                               web_app=WebAppInfo(
                                                                                                   url='https://charming-cucurucho-1beba8.netlify.app')),
                                                                          types.KeyboardButton(
                                                                              text='Стать доставщиком'))
                await message.answer(text='На данный момент, Вы не являетесь доставщиком.\n\n'
                                          'Если Вы уже подали заявку на становление доставщиком'
                                          'то в скором времени вас внесут в список\n\n'
                                          'Если Вы являетесь доставщиком и видите это сообщение,'
                                          'то пишите в ЦПП(@OnDaWayHC)',
                                     reply_markup=reply_markup)
        else:
            await message.answer(f'Сначала надо зарегестрироваться!', reply_markup=types.ReplyKeyboardMarkup().add(
                types.KeyboardButton(text='Регистрация', web_app=WebAppInfo(url='https://charming-cucurucho-1beba8.netlify.app/form'))))
    except Exception as err:
        logging.exception(err)


# Handler for inline button clicks
@dp.callback_query_handler(lambda c: c.data.startswith('execute'))
async def start_order(callback_query: types.CallbackQuery):
    try:
        conn = db.connection
        cursor = conn.cursor()
        order_id = callback_query.data.split(':')[1]

        # Check if the order status is not 'Выполняется' or 'Отменен'
        cursor.execute('''
            SELECT status, order_place, delivery_option, until_date, until_time, payment_method, comment, dorm, floor, room, client_id
            FROM "order"
            WHERE id = %s
        ''', (order_id,))
        order_status, order_place, delivery_option, until_date, until_time, payment_method, comment, dorm, floor, room, client_id = cursor.fetchone()

        if order_status == 'Создан':
            # Check if the order's until_date and until_time are not expired
            current_datetime = datetime.datetime.now()  # Use the correct namespace
            order_datetime = datetime.datetime.combine(until_date, until_time)
            if order_datetime <= current_datetime:
                await bot.send_message(callback_query.from_user.id, f"Нельзя выполнить. Заказ №{order_id} просрочен")
                await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
                return

            # Update order status to 'Выполняется' and set deliveryman_id
            cursor.execute('''
                UPDATE "order"
                SET status = 'Выполняется', deliveryman_id = %s
                WHERE id = %s
            ''', (callback_query.from_user.id, order_id))
            conn.commit()

            # Format the order information
            form_info = f"Order ID: {order_id}\n"
            form_info += f"Status: Выполняется\n"
            form_info += f"Заказ из: {order_place}\n"

            if delivery_option == 'KPP':
                form_info += f"Куда доставить: КПП\n"
            elif delivery_option == 'CP':
                form_info += f"Куда доставить: ЦП\n"
            else:
                form_info += f"Общежитие: {dorm}\n"
                if floor != 0:
                    form_info += f"Этаж: {floor}\n"
                    if room != 0:
                        form_info += f"Комната: {room:02d}\n"

            form_info += f"Крайний срок: {until_date}, {until_time}\n"
            form_info += f"Метод оплаты: {payment_method}\n"
            form_info += f"Комментарий к заказу: {comment}\n"

            # Create inline keyboard with buttons
            inline_keyboard_user = types.InlineKeyboardMarkup(row_width=1)
            cancel_button = types.InlineKeyboardButton(text="Отменить заказ", callback_data=f"cancel_order:{order_id}")

            decline_button = types.InlineKeyboardButton(text="Отказаться от доставщика",
                                                        callback_data=f"decline_deliveryman:{order_id}")

            contact_button = types.InlineKeyboardButton(text="Связаться с доставщиком",
                                                        callback_data=f"contact_deliveryman:{order_id}")

            inline_keyboard_user.add(contact_button, decline_button, cancel_button)
            # Send the order details message with inline buttons
            client_message = await bot.send_message(client_id, form_info, reply_markup=inline_keyboard_user)
            client_message_id = client_message.message_id

            inline_keyboard_deliveryman = types.InlineKeyboardMarkup(row_width=1)
            cancel_execution = types.InlineKeyboardButton(text="Отказаться", callback_data=f"cancel_execution:{order_id}")
            take_pakage = types.InlineKeyboardButton(text="Забрал посылку", callback_data=f"package_taken:{order_id},{client_message_id}")
            inline_keyboard_deliveryman.add(take_pakage, cancel_execution)
            await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
            await bot.send_message(callback_query.from_user.id, form_info, reply_markup=inline_keyboard_deliveryman)

        elif order_status == 'Выполняется':
            await bot.send_message(callback_query.from_user.id, f"Нельзя выполнить. Заказ №{order_id} уже выполняется")
            await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)

        elif order_status == 'Отменен':
            await bot.send_message(callback_query.from_user.id, f"Нельзя выполнить. Заказ №{order_id} отменен")
            await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)

    except Exception as e:
        print("Error processing callback:", e)


# Handler for inline button "Отменить выполнение"
@dp.callback_query_handler(lambda c: c.data.startswith('cancel_execution'))
async def cancel_execution(callback_query: types.CallbackQuery):
    try:
        conn = db.connection
        cursor = conn.cursor()
        order_id = callback_query.data.split(':')[1]
        cursor.execute('''
                    SELECT status, deliveryman_id
                    FROM "order"
                    WHERE id = %s
                ''', (order_id,))
        order_status, deliveryman_id = cursor.fetchone()

        if order_status == 'Отменен' or deliveryman_id is None:
            await bot.send_message(callback_query.from_user.id, f"Нельзя выполнить. Заказ №{order_id} отменен")
            await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
        else:
            # Update order status to 'Создан' and set deliveryman_id to NULL
            cursor.execute('''
                UPDATE "order"
                SET status = 'Создан', deliveryman_id = NULL
                WHERE id = %s
            ''', (order_id,))
            conn.commit()

        # Delete the message with that order
            await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)

    except Exception as e:
        print("Error processing callback:", e)


@dp.callback_query_handler(lambda c: c.data.startswith('package_taken'))
async def cancel_execution(callback_query: types.CallbackQuery):
    try:
        conn = db.connection
        cursor = conn.cursor()
        string = callback_query.data.split(':')[1]
        order_id, client_message_id = string.split(',')[0], string.split(',')[1]

        cursor.execute('''
                            SELECT status, deliveryman_id
                            FROM "order"
                            WHERE id = %s
                        ''', (order_id,))
        order_status, deliveryman_id = cursor.fetchone()

        if order_status == 'Отменен' or deliveryman_id is None:
            await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
            await bot.send_message(callback_query.from_user.id, text=f"Заказ {order_id} был отменен")
        else:

            # Update order status to 'Создан' and set deliveryman_id to NULL
            cursor.execute('''
                            UPDATE "order"
                            SET status = 'Доставляется'
                            WHERE id = %s
                        ''', (order_id,))
            conn.commit()

            cursor.execute('''
                                    SELECT status, order_place, delivery_option, until_date, until_time, payment_method, comment, dorm, floor, room, client_id
                                    FROM "order"
                                    WHERE id = %s
                                ''', (order_id,))
            order_status, order_place, delivery_option, until_date, until_time, payment_method, comment, dorm, floor, room, client_id = cursor.fetchone()

            # Format the order information
            form_info = f"Order ID: {order_id}\n"
            form_info += f"Status: Доставляется\n"
            form_info += f"Заказ из: {order_place}\n"

            if delivery_option == 'KPP':
                form_info += f"Куда доставить: КПП\n"
            elif delivery_option == 'CP':
                form_info += f"Куда доставить: ЦП\n"
            else:
                form_info += f"Общежитие: {dorm}\n"
                if floor != 0:
                    form_info += f"Этаж: {floor}\n"
                    if room != 0:
                        form_info += f"Комната: {room:02d}\n"

            form_info += f"Крайний срок: {until_date}, {until_time}\n"
            form_info += f"Метод оплаты: {payment_method}\n"
            form_info += f"Комментарий к заказу: {comment}\n"
            inline_keyboard_user = types.InlineKeyboardMarkup(row_width=1)
            cancel_button = types.InlineKeyboardButton(text="Отменить заказ", callback_data=f"cancel_order:{order_id}")

            decline_button = types.InlineKeyboardButton(text="Отказаться от доставщика",
                                                        callback_data=f"decline_deliveryman:{order_id}")

            contact_button = types.InlineKeyboardButton(text="Связаться с доставщиком",
                                                        callback_data=f"contact_deliveryman:{order_id}")

            inline_keyboard_user.add(contact_button, decline_button, cancel_button)
            # Send the order details message with inline buttons
            await bot.edit_message_text(text=form_info, chat_id=client_id, message_id=client_message_id,
                                        reply_markup=inline_keyboard_user)

            inline_keyboard_deliveryman = types.InlineKeyboardMarkup(row_width=1)
            order_complete = types.InlineKeyboardButton(text="Завершить заказ",
                                                        callback_data=f"order_completed:{order_id},{client_message_id}")
            inline_keyboard_deliveryman.add(order_complete)
            await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
            await bot.send_message(callback_query.from_user.id, form_info, reply_markup=inline_keyboard_deliveryman)

            # Delete the message with that order
            await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)

    except Exception as e:
        print("Error processing callback:", e)


@dp.callback_query_handler(lambda c: c.data.startswith('order_completed'))
async def cancel_execution(callback_query: types.CallbackQuery):
    try:
        conn = db.connection
        cursor = conn.cursor()
        string = callback_query.data.split(':')[1]
        order_id, client_message_id = string.split(',')[0], string.split(',')[1]

        cursor.execute('''
                            SELECT status, deliveryman_id
                            FROM "order"
                            WHERE id = %s
                        ''', (order_id,))
        order_status, deliveryman_id = cursor.fetchone()
        if order_status == 'Отменен' or deliveryman_id is None:
            await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
            await bot.send_message(callback_query.from_user.id, text=f"Заказ {order_id} был отменен")
        else:
            # Update order status to 'Создан' and set deliveryman_id to NULL
            cursor.execute('''
                UPDATE "order"
                SET status = 'Доставлен'
                WHERE id = %s
            ''', (order_id,))
            conn.commit()

            # Increment the 'complete' field for the associated deliveryman
            cursor.execute('''
                            UPDATE "deliverymen"
                            SET complete = complete + 1
                            WHERE tg_id = %s
                        ''', (deliveryman_id,))
            conn.commit()

            cursor.execute('''
                        SELECT status, order_place, delivery_option, until_date, until_time, payment_method, comment, dorm, floor, room, client_id
                        FROM "order"
                        WHERE id = %s
                    ''', (order_id,))
            order_status, order_place, delivery_option, until_date, until_time, payment_method, comment, dorm, floor, room, client_id = cursor.fetchone()

            # Format the order information
            form_info = f"Order ID: {order_id}\n"
            form_info += f"Status: Доставлен\n"
            form_info += f"Заказ из: {order_place}\n"

            if delivery_option == 'KPP':
                form_info += f"Куда доставить: КПП\n"
            elif delivery_option == 'CP':
                form_info += f"Куда доставить: ЦП\n"
            else:
                form_info += f"Общежитие: {dorm}\n"
                if floor != 0:
                    form_info += f"Этаж: {floor}\n"
                    if room != 0:
                        form_info += f"Комната: {room:02d}\n"

            form_info += f"Крайний срок: {until_date}, {until_time}\n"
            form_info += f"Метод оплаты: {payment_method}\n"
            form_info += f"Комментарий к заказу: {comment}\n"

            await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
            await bot.send_message(callback_query.from_user.id, form_info)

            # Delete the message with that order
            await bot.edit_message_text(text=form_info, chat_id=client_id, message_id=client_message_id)

    except Exception as e:
        print("Error processing callback:", e)


@dp.callback_query_handler(lambda c: c.data.startswith('cancel_order'))
async def cancel_order_callback(callback_query: types.CallbackQuery):
    try:
        conn = db.connection
        cursor = conn.cursor()
        order_id = callback_query.data.split(':')[1]

        # Update order status to 'Отменен'
        cursor.execute('''
            UPDATE "order"
            SET status = 'Отменен'
            WHERE id = %s
        ''', (order_id,))
        conn.commit()

        await bot.send_message(callback_query.from_user.id, f"Заказ №{order_id} был успешно отменен.")
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)

    except Exception as e:
        print("Error processing cancel_order callback:", e)


@dp.callback_query_handler(lambda c: c.data.startswith('decline_deliveryman'))
async def decline_deliveryman_callback(callback_query: types.CallbackQuery):
    try:
        conn = db.connection
        cursor = conn.cursor()
        order_id = callback_query.data.split(':')[1]

        # Clear the deliveryman_id field and update order status to 'Создан'
        cursor.execute('''
            UPDATE "order"
            SET status = 'Создан', deliveryman_id = NULL
            WHERE id = %s
        ''', (order_id,))
        conn.commit()

        await bot.send_message(callback_query.from_user.id, f"Вы отказались от выполнения заказа №{order_id}")
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)

    except Exception as e:
        print("Error processing decline_deliveryman callback:", e)


@dp.callback_query_handler(lambda c: c.data.startswith('contact_deliveryman'))
async def contact_deliveryman_callback(callback_query: types.CallbackQuery):
    try:
        conn = db.connection
        cursor = conn.cursor()
        order_id = callback_query.data.split(':')[1]

        # Get the deliveryman_id from the order
        cursor.execute('''
            SELECT deliveryman_id FROM "order"
            WHERE id = %s
        ''', (order_id,))
        deliveryman_id = cursor.fetchone()[0]

        # Get the username of the deliveryman
        cursor.execute('''
            SELECT username FROM "deliverymen"
            WHERE tg_id = %s
        ''', (deliveryman_id,))
        deliveryman_username = cursor.fetchone()[0]

        message = f"Свяжитесь с Вашим доставщиком\n@{deliveryman_username}"
        await bot.send_message(callback_query.from_user.id, message)

    except Exception as e:
        print("Error processing contact_deliveryman callback:", e)

