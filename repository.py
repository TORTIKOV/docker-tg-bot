import db
from datetime import datetime
from config.config import deliverymen_id


def update_start_date_for_user(tgid):
    conn = db.connection
    cursor = conn.cursor()

    current_date = datetime.now().date()

    cursor.execute('''
        UPDATE "user" 
        SET start_date = %s
        WHERE tg_id = %s
    ''', (current_date, tgid))

    conn.commit()
    cursor.close()


def add_user_to_db(name, tgid, phone, dorm, floor, room):
    conn = db.connection
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO "user" (name, tg_id, phone, dorm, floor, room)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (name, tgid, phone, dorm, floor, room))
    conn.commit()
    cursor.close()
    update_start_date_for_user(tgid)


def check_tgid_in_db(tgid):
    conn = db.connection
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM \"user\" WHERE tg_id = %s", (tgid,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] > 0


def update_user_information(tgid, new_name, new_dorm, new_floor, new_room, new_phone):
    conn = db.connection
    cursor = conn.cursor()

    existing_user = check_tgid_in_db(tgid)
    if existing_user:
        cursor.execute('''
            UPDATE "user"
            SET name = %s, dorm = %s, floor = %s, room = %s, phone = %s
            WHERE tg_id = %s
        ''', (new_name, new_dorm, new_floor, new_room, new_phone, tgid))
        conn.commit()
        cursor.close()
        return True
    else:
        cursor.close()
        return False


def insert_order_to_db(tg_id, delivery_option, dorm, floor, room, no_later_than, payment_method, order_comment,
                       products):
    conn = db.connection
    cursor = conn.cursor()

    until_date, until_time = no_later_than.split("T")

    until_date = datetime.strptime(until_date, "%Y-%m-%d").date()
    until_time = datetime.strptime(until_time, "%H:%M").time()

    status = "Создан"
    creation_date = datetime.now().date()
    creation_time = datetime.now().time()

    try:
        cursor.execute('''
            INSERT INTO "order" 
            (client_id, status, creation_date, creation_time, order_place, until_date, until_time, payment_method, comment, delivery_option, dorm, floor, room)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
        tg_id, status, creation_date, creation_time, products, until_date, until_time, payment_method, order_comment,
        delivery_option, dorm, floor, room))

        order_id = cursor.fetchone()[0]

        conn.commit()
        print("Data inserted successfully.")
        return order_id
    except Exception as e:
        conn.rollback()
        print("Error inserting data:", e)
    finally:
        cursor.close()


def get_order_status(order_id):
    conn = db.connection
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT status
            FROM "order"
            WHERE id = %s
        ''', (order_id,))

        status = cursor.fetchone()
        if status:
            return status[0]
        else:
            return None
    except Exception as e:
        print("Error fetching order status:", e)
    finally:
        cursor.close()


def update_order_status(order_id, status):
    conn = db.connection
    cursor = conn.cursor()

    try:
        cursor.execute('''
                        SELECT status FROM "order"
                        WHERE id = %s
                    ''', (order_id,))
        current_status = cursor.fetchone()[0]

        if current_status != 'Доставлен':
            cursor.execute('''
                            UPDATE "order"
                            SET status = %s
                            WHERE id = %s
                        ''', (status, order_id))

            conn.commit()
            print("Order status updated successfully.")
            return True
        else:
            print("Order is already delivered. Status unchanged.")
            return False
    except Exception as e:
        conn.rollback()
        print("Error updating order status:", e)
        return False
    finally:
        cursor.close()


def add_deliveryman_to_db(deliveryman_tg_id, username, date):
    try:
        conn = db.connection
        cursor = conn.cursor()

        work_until_date = datetime.strptime(date, '%d.%m.%Y').date()

        cursor.execute('''
            INSERT INTO "deliverymen" (tg_id, career_start, work_until, experience_month, complete, status, username)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (deliveryman_tg_id, datetime.now().date(), work_until_date, 0, 0, True, username))

        conn.commit()

        cursor.close()

        return True

    except Exception as e:
        conn.rollback()
        print("Error inserting deliveryman data:", e)
        return False


def update_deliveryman(tg_id, date):
    try:
        conn = db.connection
        cursor = conn.cursor()

        if not check_if_deliveryman(tg_id):
            return False

        cursor.execute('''
            UPDATE "deliverymen"
            SET experience_month = experience_month + 1
            WHERE tg_id = %s
        ''', (tg_id,))

        new_work_until = datetime.strptime(date, '%d.%m.%Y').date()

        cursor.execute('''
            UPDATE "deliverymen"
            SET work_until = %s, status = %s
            WHERE tg_id = %s
        ''', (new_work_until, True, tg_id))

        conn.commit()

        cursor.close()

        return True

    except Exception as e:
        print("Error updating deliveryman:", e)
        return False


def check_if_deliveryman(tg_id):
    try:
        conn = db.connection
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT(*) FROM "deliverymen" WHERE tg_id = %s
        ''', (tg_id,))

        result = cursor.fetchone()

        cursor.close()

        return 1 if result[0] > 0 else 0

    except Exception as e:
        print("Error checking if deliveryman:", e)
        return 0


def ban_deliveryman(deliveryman_tg_id):
    try:
        conn = db.connection
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE "deliverymen"
            SET status = false
            WHERE tg_id = %s
        ''', (deliveryman_tg_id,))

        conn.commit()

        cursor.close()

        return True

    except Exception as e:
        conn.rollback()
        print("Error banning deliveryman:", e)
        return False


def unban_deliveryman(deliveryman_tg_id):
    try:
        conn = db.connection
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE "deliverymen"
            SET status = true
            WHERE tg_id = %s
        ''', (deliveryman_tg_id,))

        conn.commit()

        cursor.close()

        return True

    except Exception as e:
        conn.rollback()
        print("Error unbanning deliveryman:", e)
        return False


async def import_deliverymen():
    try:
        conn = db.connection
        cursor = conn.cursor()

        current_date = datetime.now().date()

        cursor.execute('''
            SELECT tg_id FROM "deliverymen"
            WHERE status = true AND work_until != %s
        ''', (current_date,))

        updated_deliverymen = cursor.fetchall()

        for row in updated_deliverymen:
            if row[0] not in deliverymen_id:
                deliverymen_id.append(row[0])

        conn.commit()

        cursor.close()

        return True

    except Exception as e:
        conn.rollback()
        print("Error importing deliverymen:", e)
        return False


def get_client_id_by_order_id(order_id):
    conn = db.connection
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT client_id
            FROM "order"
            WHERE id = %s
        ''', (order_id,))

        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    except Exception as e:
        print("Error fetching client_id by order_id:", e)
        return None
    finally:
        cursor.close()


def update_deliveryman_username(tg_id, new_username):
    try:
        conn = db.connection
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE "deliverymen"
            SET username = %s
            WHERE tg_id = %s
        ''', (new_username, tg_id))

        conn.commit()

        cursor.close()

        return True

    except Exception as e:
        conn.rollback()
        print("Error updating deliveryman username:", e)
        return False


def add_admin_to_db(tg_id):
    conn = db.connection
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO "moderator" (tg_id, status)
            VALUES (%s, %s)
        ''', (tg_id, True))

        conn.commit()
        print("Admin added successfully.")
        return True
    except Exception as e:
        conn.rollback()
        print("Error adding admin:", e)
        return False
    finally:
        cursor.close()


def check_if_admin(tg_id):
    conn = db.connection
    cursor = conn.cursor()

    try:
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
        cursor.close()


def get_active_admins():
    conn = db.connection
    cursor = conn.cursor()

    try:
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
        cursor.close()


def deactivate_admin(tg_id):
    conn = db.connection
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE "moderator"
            SET status = FALSE
            WHERE tg_id = %s
        ''', (tg_id,))
        conn.commit()
        print(f"Admin with tg_id {tg_id} status deactivated.")
        return True
    except Exception as e:
        conn.rollback()
        print("Error deactivating admin:", e)
        return False
    finally:
        cursor.close()


def check_deliveryman_activity(tg_id) -> bool:
    try:
        conn = db.connection
        cursor = conn.cursor()

        cursor.execute('''
            SELECT status, work_until FROM "deliverymen"
            WHERE tg_id = %s AND status = True
        ''', (tg_id,))
        result = cursor.fetchone()

        if result:
            status, work_until = result
            current_date = datetime.now().date()

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

        cursor.execute('''
            SELECT username FROM "deliverymen"
            WHERE tg_id = %s
        ''', (tg_id,))
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    except Exception as e:
        print("Error retrieving deliveryman username:", e)
        return None


