from aiogram import types
from loader import dp
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from repository import add_user_to_db, check_tgid_in_db, update_user_information, insert_order_to_db, get_order_status, \
    update_order_status, check_if_deliveryman, check_deliveryman_activity
from aiogram.types.web_app_info import WebAppInfo
import json
import logging


def json_contains_key(data, key) -> bool:
    try:  #
        if key in data:
            return True
        return False
    except json.JSONDecodeError:
        # Handle the case when the input is not a valid JSON string
        return False


def collect_information(json_string):
    try:
        data = json.loads(json_string)
        products_info = ""
        for product in data.get('products', []):
            products_info += f"Заказ из: {product['title']}\n"

        form_data = data.get('formData', {})
        if form_data.get('deliveryOption', '') == 'KPP':
            form_info = f"Куда доставить: КПП\n"
        elif form_data.get('deliveryOption', '') == 'CP':
            form_info = f"Куда доставить: ЦП\n"
        else:
            form_info = f"Общежитие: {form_data.get('dormOption', '')}\n"
            if form_data.get('floorOption', '') != 0:
                form_info += f"Этаж: {form_data.get('floorOption', '')}\n"
                if form_data.get('roomOption', '') != 0:
                    form_info += f"Комната: {form_data.get('roomOption', '')}\n"
        form_info += f"Крайний срок: {form_data.get('noLaterThan', '')}\n"
        form_info += f"Метод оплаты: {form_data.get('paymentMethod', '')}\n"
        form_info += f"Комментарий к заказу: {form_data.get('orderComment', '')}\n"

        return products_info, form_info  # Return both products_info and form_info as a tuple

    except json.JSONDecodeError:
        return "Invalid JSON format", ""


@dp.callback_query_handler(lambda query: query.data.startswith('cancel_order_'))
async def cancel_order_callback_handler(query: types.CallbackQuery, state: FSMContext):
    try:
        # Extract the order ID from the callback data
        order_id = query.data.split('_')[2]

        # Get the json_string from FSMContext
        data = await state.get_data()
        json_string = data.get('json_string', None)

        if json_string:
            # Trigger the cancel_order function with the json_string
            await cancel_order(query, order_id, json_string)
        else:
            logging.error("No json_string found in FSMContext.")
    except Exception as err:
        logging.exception(err)


async def cancel_order(query: types.CallbackQuery, order_id: str, json_string: str):
    try:
        # Update the order status to 'Отменен' in the database
        update_order_status(order_id, "Отменен")

        # Get the updated order status from the database
        order_status = get_order_status(order_id)

        # Call the collect_information function to get products_info and form_info
        products_info, form_info = collect_information(json_string)

        if order_status is not None:
            # Edit the sent message to display the updated status
            await query.message.edit_text(f"Order ID: {order_id}\nStatus: {order_status}\n" + products_info + form_info)
        else:
            await query.message.edit_text(
                f"Order ID: {order_id}\nStatus: Order not found\n" + products_info + form_info)

    except Exception as err:
        logging.exception(err)


@dp.message_handler(content_types=['web_app_data'])
async def web_app(message: types.Message, state: FSMContext) -> None:
    try:
        data_string = message.web_app_data.data
        data = json.loads(data_string)  # Parse the JSON string into a dictionary
        tg_id = message.from_user.id
        if json_contains_key(data, "name"):
            if check_tgid_in_db(tg_id):
                if check_if_deliveryman(tg_id) and check_deliveryman_activity(tg_id):
                    reply_markup = types.ReplyKeyboardMarkup(row_width=1).add(types.KeyboardButton(text='Сделать заказ',
                                                                                                   web_app=WebAppInfo(
                                                                                                       url='https://charming-cucurucho-1beba8.netlify.app')),
                                                                              types.KeyboardButton(
                                                                                  text='Заказы'))
                    is_updated = update_user_information(new_name=data["name"], tgid=tg_id, new_phone=data["phone"],
                                                         new_dorm=data["dorm"], new_floor=data["floor"],
                                                         new_room=data["room"])
                    if is_updated:
                        await message.answer(f"Информация обновлена! Можно возвращаться к заказам", reply_markup=reply_markup)
                    else:
                        await message.answer(
                            f'Инфрмация не обновлена. Если нуждаетесь в обновлении, оратитесь в техподдержку')
                else:
                    reply_markup = types.ReplyKeyboardMarkup(row_width=1).add(types.KeyboardButton(text='Сделать заказ',
                                                                                                   web_app=WebAppInfo(
                                                                                                       url='https://charming-cucurucho-1beba8.netlify.app')),
                                                                              types.KeyboardButton(
                                                                                  text='Стать доставщиком'))
                    is_updated = update_user_information(new_name=data["name"], tgid=tg_id, new_phone=data["phone"],
                                                         new_dorm=data["dorm"], new_floor=data["floor"],
                                                         new_room=data["room"])
                    if is_updated:
                        await message.answer(f"Информация обновлена", reply_markup=reply_markup)
                    else:
                        await message.answer(
                            f'Инфрмация не обновлена. Если нуждаетесь в обновлении, оратитесь в техподдержку')
            else:
                name = data["name"]
                dorm = data["dorm"]
                floor = data["floor"]
                room = data["room"]
                phone = data["phone"]
                reply_markup = types.ReplyKeyboardMarkup(row_width=1).add(types.KeyboardButton(text='Сделать заказ',
                                                                                               web_app=WebAppInfo(
                                                                                                   url='https://charming-cucurucho-1beba8.netlify.app')),
                                                                          types.KeyboardButton(
                                                                              text='Стать доставщиком'))
                await message.answer(
                    f'Приятно познакомиться!',
                    reply_markup=reply_markup)
                add_user_to_db(name=name, tgid=tg_id, phone=phone, dorm=dorm, floor=floor, room=room)
        else:
            data = json.loads(data_string)
            products_info = ""
            for product in data.get('products', []):
                products_info += f"Заказ из: {product['title']}\n"

            form_data = data.get('formData', {})
            delivery_option = form_data.get('deliveryOption', '')
            dorm_option = form_data.get('dormOption', '')
            floor_option = form_data.get('floorOption', '')
            room_option = form_data.get('roomOption', '')
            no_later_than = form_data.get('noLaterThan', '')
            payment_method = form_data.get('paymentMethod', '')
            order_comment = form_data.get('orderComment', '')

            if delivery_option == 'KPP':
                form_info = f"Куда доставить: КПП\n"
            elif delivery_option == 'CP':
                form_info = f"Куда доставить: ЦП\n"
            else:
                form_info = f"Общежитие: {dorm_option}\n"
                if floor_option != '0':
                    form_info += f"Этаж: {floor_option}\n"
                    if room_option != '0':
                        # Convert room_option to an integer before applying format
                        room_option_int = int(room_option)
                        form_info += f"Комната: {room_option_int:02d}\n"  # Formatting room_option_int with leading zero if < 10

            form_info += f"Крайний срок: {no_later_than}\n"
            form_info += f"Метод оплаты: {payment_method}\n"
            form_info += f"Комментарий к заказу: {order_comment}\n"

            # Call the insert_order_to_db function to insert data into the database
            order_id = insert_order_to_db(tg_id, delivery_option, dorm_option, floor_option, room_option, no_later_than,
                                          payment_method, order_comment, product['title'])
            order_status = get_order_status(order_id)

            if order_status is not None:
                # Combine the products_info, form_info, and order status
                order_info = f"Order ID: {order_id}\nStatus: {order_status}\n" + products_info + form_info
            else:
                order_info = f"Order ID: {order_id}\nStatus: Order not found\n" + products_info + form_info
            cancel_button = InlineKeyboardButton("Отменить заказ", callback_data=f"cancel_order_{order_id}")
            inline_keyboard = InlineKeyboardMarkup().add(cancel_button)

            # Send the order information along with the inline keyboard
            await message.answer(order_info, reply_markup=inline_keyboard)

            if product['title'] == "ПункВейп":
                await message.answer(text="Уточните ассортимент в личных сообщениях -> @VapePunk")

            # Save the json_string to the state
            async with state.proxy() as data:
                data['json_string'] = data_string

    except Exception as err:
        logging.exception(err)

