import db
from datetime import datetime, timedelta
from config.config import deliverymen_id


def update_start_date_for_user(tgid):
    conn = db.connection
    cursor = conn.cursor()

    # Get the current date
    current_date = datetime.now().date()

    cursor.execute('''
        UPDATE "user" 
        SET start_date = %s
        WHERE tgid = %s
    ''', (current_date, tgid))

    conn.commit()
    cursor.close()


def add_user_to_db(name, tgid, phone, dorm, floor, room):
    conn = db.connection
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO "user" (name, tgid, phone, dorm, floor, room)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (name, tgid, phone, dorm, floor, room))
    conn.commit()
    cursor.close()
    update_start_date_for_user(tgid)


def check_tgid_in_db(tgid):
    conn = db.connection
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM \"user\" WHERE tgid = %s", (tgid,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] > 0


def update_user_information(tgid, new_name, new_dorm, new_floor, new_room, new_phone):
    conn = db.connection
    cursor = conn.cursor()

    # Check if the user exists in the database
    existing_user = check_tgid_in_db(tgid)
    if existing_user:
        # Update the user information
        cursor.execute('''
            UPDATE "user"
            SET name = %s, dorm = %s, floor = %s, room = %s, phone = %s
            WHERE tgid = %s
        ''', (new_name, new_dorm, new_floor, new_room, new_phone, tgid))
        conn.commit()
        cursor.close()
        return True  # Return True to indicate the update was successful
    else:
        cursor.close()
        return False  # Return False to indicate that the user does not exist


def insert_order_to_db(tg_id, delivery_option, dorm, floor, room, no_later_than, payment_method, order_comment,
                       products):
    conn = db.connection
    cursor = conn.cursor()

    # Parse the 'no_later_than' string to get the date and time
    until_date, until_time = no_later_than.split("T")

    # Convert the date and time strings to Python datetime objects
    until_date = datetime.strptime(until_date, "%Y-%m-%d").date()
    until_time = datetime.strptime(until_time, "%H:%M").time()

    # Set the status and creation date/time
    status = "Создан"
    creation_date = datetime.now().date()
    creation_time = datetime.now().time()

    try:
        # Insert the data into the database and use the RETURNING clause to get the order ID
        cursor.execute('''
            INSERT INTO "order" 
            (client_id, status, creation_date, creation_time, order_place, until_date, until_time, payment_method, comment, delivery_option, dorm, floor, room)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
        tg_id, status, creation_date, creation_time, products, until_date, until_time, payment_method, order_comment,
        delivery_option, dorm, floor, room))

        # Fetch the order ID from the returned row
        order_id = cursor.fetchone()[0]

        # Commit the changes to the database
        conn.commit()
        print("Data inserted successfully.")
        return order_id  # Return the order ID
    except Exception as e:
        # If there's an error, rollback the transaction
        conn.rollback()
        print("Error inserting data:", e)
    finally:
        # Close the cursor and release the connection
        cursor.close()


def get_order_status(order_id):
    conn = db.connection
    cursor = conn.cursor()

    try:
        # Execute the query to get the status of the order with the given ID
        cursor.execute('''
            SELECT status
            FROM "order"
            WHERE id = %s
        ''', (order_id,))

        # Fetch the status from the result
        status = cursor.fetchone()
        if status:
            return status[0]
        else:
            return None  # Order with the provided ID not found
    except Exception as e:
        print("Error fetching order status:", e)
    finally:
        cursor.close()


def update_order_status(order_id, status):
    conn = db.connection
    cursor = conn.cursor()

    try:
        # Check if the current status is 'Доставлен', and if so, do nothing
        cursor.execute('''
                        SELECT status FROM "order"
                        WHERE id = %s
                    ''', (order_id,))
        current_status = cursor.fetchone()[0]

        if current_status != 'Доставлен':
            # Update the status of the order with the provided ID
            cursor.execute('''
                            UPDATE "order"
                            SET status = %s
                            WHERE id = %s
                        ''', (status, order_id))

            # Commit the changes to the database
            conn.commit()
            print("Order status updated successfully.")
            return True
        else:
            print("Order is already delivered. Status unchanged.")
            return False
    except Exception as e:
        # If there's an error, rollback the transaction
        conn.rollback()
        print("Error updating order status:", e)
        return False
    finally:
        # Close the cursor and release the connection
        cursor.close()


def add_deliveryman_to_db(deliveryman_tg_id, username, date):
    try:
        conn = db.connection
        cursor = conn.cursor()

        # Parse the provided date string in DD.MM.YYYY format
        work_until_date = datetime.strptime(date, '%d.%m.%Y').date()

        # Insert the deliveryman data into the database
        cursor.execute('''
            INSERT INTO "deliverymen" (tg_id, career_start, work_until, experience_month, complete, status, username)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (deliveryman_tg_id, datetime.now().date(), work_until_date, 0, 0, True, username))

        # Commit the changes to the database
        conn.commit()

        # Close the cursor
        cursor.close()

        return True

    except Exception as e:
        # If there's an error, rollback the transaction
        conn.rollback()
        print("Error inserting deliveryman data:", e)
        return False


def update_deliveryman(tg_id, date):
    try:
        conn = db.connection
        cursor = conn.cursor()

        # Check if the Telegram ID exists in the `deliverymen` table
        if not check_if_deliveryman(tg_id):
            return False

        # Increment the `experience_month` field by 1
        cursor.execute('''
            UPDATE "deliverymen"
            SET experience_month = experience_month + 1
            WHERE tg_id = %s
        ''', (tg_id,))

        # Parse the provided date string in DD.MM.YYYY format
        new_work_until = datetime.strptime(date, '%d.%m.%Y').date()

        # Set the `work_until` and `status` fields
        cursor.execute('''
            UPDATE "deliverymen"
            SET work_until = %s, status = %s
            WHERE tg_id = %s
        ''', (new_work_until, True, tg_id))  # Use True for boolean value

        # Commit the changes to the database
        conn.commit()

        # Close the cursor
        cursor.close()

        return True

    except Exception as e:
        print("Error updating deliveryman:", e)
        return False


def check_if_deliveryman(tg_id):
    try:
        conn = db.connection
        cursor = conn.cursor()

        # Execute the query to check if the Telegram ID is in the `deliverymen` table
        cursor.execute('''
            SELECT COUNT(*) FROM "deliverymen" WHERE tg_id = %s
        ''', (tg_id,))

        # Fetch the result from the query
        result = cursor.fetchone()

        # Close the cursor
        cursor.close()

        # Return 1 if the Telegram ID is found, otherwise return 0
        return 1 if result[0] > 0 else 0

    except Exception as e:
        print("Error checking if deliveryman:", e)
        return 0


def ban_deliveryman(deliveryman_tg_id):
    try:
        conn = db.connection
        cursor = conn.cursor()

        # Update the deliveryman's status to False
        cursor.execute('''
            UPDATE "deliverymen"
            SET status = false
            WHERE tg_id = %s
        ''', (deliveryman_tg_id,))

        # Commit the changes to the database
        conn.commit()

        # Close the cursor
        cursor.close()

        return True

    except Exception as e:
        # If there's an error, rollback the transaction
        conn.rollback()
        print("Error banning deliveryman:", e)
        return False


def unban_deliveryman(deliveryman_tg_id):
    try:
        conn = db.connection
        cursor = conn.cursor()

        # Update the deliveryman's status to False
        cursor.execute('''
            UPDATE "deliverymen"
            SET status = true
            WHERE tg_id = %s
        ''', (deliveryman_tg_id,))

        # Commit the changes to the database
        conn.commit()

        # Close the cursor
        cursor.close()

        return True

    except Exception as e:
        # If there's an error, rollback the transaction
        conn.rollback()
        print("Error unbanning deliveryman:", e)
        return False


async def import_deliverymen():
    try:
        conn = db.connection
        cursor = conn.cursor()

        # Get the current date
        current_date = datetime.now().date()

        # Select the deliverymen IDs with status == true and work_until != current date
        cursor.execute('''
            SELECT tg_id FROM "deliverymen"
            WHERE status = true AND work_until != %s
        ''', (current_date,))

        # Fetch the deliverymen IDs from the result
        updated_deliverymen = cursor.fetchall()

        # Append the fetched deliverymen IDs to the deliverymen_id list
        for row in updated_deliverymen:
            if row[0] not in deliverymen_id:
                deliverymen_id.append(row[0])

        # Commit the changes to the database
        conn.commit()

        # Close the cursor
        cursor.close()

        return True

    except Exception as e:
        # If there's an error, rollback the transaction
        conn.rollback()
        print("Error importing deliverymen:", e)
        return False


def get_client_id_by_order_id(order_id):
    conn = db.connection
    cursor = conn.cursor()

    try:
        # Execute the query to retrieve the client_id for the given order_id
        cursor.execute('''
            SELECT client_id
            FROM "order"
            WHERE id = %s
        ''', (order_id,))

        # Fetch the client_id from the result
        result = cursor.fetchone()

        if result:
            return result[0]  # Return the client_id
        else:
            return None  # Return None if order with the provided order_id not found

    except Exception as e:
        print("Error fetching client_id by order_id:", e)
        return None
    finally:
        cursor.close()


def update_deliveryman_username(tg_id, new_username):
    try:
        conn = db.connection
        cursor = conn.cursor()

        # Update the username of the deliveryman with the provided ID
        cursor.execute('''
            UPDATE "deliverymen"
            SET username = %s
            WHERE tg_id = %s
        ''', (new_username, tg_id))

        # Commit the changes to the database
        conn.commit()

        # Close the cursor
        cursor.close()

        return True

    except Exception as e:
        # If there's an error, rollback the transaction
        conn.rollback()
        print("Error updating deliveryman username:", e)
        return False


def add_admin_to_db(tg_id):
    conn = db.connection
    cursor = conn.cursor()

    try:
        # Insert a new admin into the "moderator" table
        cursor.execute('''
            INSERT INTO "moderator" (tg_id, status)
            VALUES (%s, %s)
        ''', (tg_id, True))

        # Commit the changes to the database
        conn.commit()
        print("Admin added successfully.")
        return True
    except Exception as e:
        # If there's an error, rollback the transaction
        conn.rollback()
        print("Error adding admin:", e)
        return False
    finally:
        # Close the cursor and release the connection
        cursor.close()


def check_if_admin(tg_id):
    conn = db.connection
    cursor = conn.cursor()

    try:
        # Check if the admin with the provided tg_id and status=True exists
        cursor.execute('''
            SELECT COUNT(*) FROM "moderator"
            WHERE tg_id = %s AND status = TRUE
        ''', (tg_id,))
        admin_count = cursor.fetchone()[0]

        if admin_count > 0:
            print("Admin exists and is active.")
            return True
        else:
            print("Admin does not exist or is not active.")
            return False
    except Exception as e:
        print("Error checking admin:", e)
        return False
    finally:
        # Close the cursor and release the connection
        cursor.close()


def get_active_admins():
    conn = db.connection
    cursor = conn.cursor()

    try:
        # Retrieve all admins with active status
        cursor.execute('''
            SELECT tg_id FROM "moderator"
            WHERE status = TRUE
        ''')
        admins = [row[0] for row in cursor.fetchall()]
        return admins
    except Exception as e:
        print("Error retrieving active admins:", e)
        return []
    finally:
        # Close the cursor and release the connection
        cursor.close()


def deactivate_admin(tg_id):
    conn = db.connection
    cursor = conn.cursor()

    try:
        # Update admin status to False
        cursor.execute('''
            UPDATE "moderator"
            SET status = FALSE
            WHERE tg_id = %s
        ''', (tg_id,))
        conn.commit()
        print(f"Admin with tg_id {tg_id} status deactivated.")
        return True
    except Exception as e:
        # If there's an error, rollback the transaction
        conn.rollback()
        print("Error deactivating admin:", e)
        return False
    finally:
        # Close the cursor and release the connection
        cursor.close()


# Assuming you have a function check_if_deliveryman defined in your repository
# Update it to include status check
def check_deliveryman_activity(tg_id) -> bool:
    try:
        conn = db.connection
        cursor = conn.cursor()

        # Check if the user is a deliveryman and has status set to True
        cursor.execute('''
            SELECT status, work_until FROM "deliverymen"
            WHERE tg_id = %s AND status = True
        ''', (tg_id,))
        result = cursor.fetchone()

        if result:
            status, work_until = result
            current_date = datetime.now().date()

            # If work_until is less than or equal to the current date, ban the deliveryman and update status
            if work_until <= current_date:
                cursor.execute('''
                    UPDATE "deliverymen"
                    SET status = False
                    WHERE tg_id = %s
                ''', (tg_id,))
                conn.commit()
                return False
            else:
                return True
        else:
            return False

    except Exception as e:
        print("Error checking if deliveryman:", e)
        return False


def get_deliveryman_username(tg_id):
    try:
        conn = db.connection
        cursor = conn.cursor()

        # Retrieve the username of the deliveryman with the given tg_id
        cursor.execute('''
            SELECT username FROM "deliverymen"
            WHERE tg_id = %s
        ''', (tg_id,))
        result = cursor.fetchone()

        if result:
            return result[0]  # Return the username
        else:
            return None  # No deliveryman with the given tg_id found

    except Exception as e:
        print("Error retrieving deliveryman username:", e)
        return None


