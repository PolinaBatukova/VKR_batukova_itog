import sqlite3
from datetime import datetime, timedelta
import hashlib

DATABASE_NAME = "courier_app.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            o.id,
            o.creation_date,
            os.status_name,
            o.delivery_address,
            c.fio AS client_fio,
            d.fio AS driver_fio,
            o.driver_id,
            o.product,
            o.quantity,
            o.comment,
            o.delivery_deadline,
            o.delay_reason
        FROM orders o
        JOIN order_statuses os ON o.status_id = os.id
        JOIN clients c ON o.client_id = c.id
        JOIN drivers d ON o.driver_id = d.id
    """)
    orders = cursor.fetchall()
    conn.close()
    return orders

def get_delivered_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            o.id,
            o.creation_date,
            os.status_name,
            o.delivery_address,
            c.fio AS client_fio,
            d.fio AS driver_fio,
            o.product,
            o.quantity,
            o.comment,
            o.delivery_deadline,
            o.delay_reason
        FROM orders o
        JOIN order_statuses os ON o.status_id = os.id
        JOIN clients c ON o.client_id = c.id
        JOIN drivers d ON o.driver_id = d.id
        WHERE os.status_name = 'Доставлен'
    """)
    orders = cursor.fetchall()
    conn.close()
    return orders

def update_order_delay_reason(order_id, reason):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET delay_reason = ? WHERE id = ?", (reason, order_id))
    conn.commit()
    conn.close()

def get_pending_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            o.id,
            o.creation_date,
            os.status_name,
            o.delivery_address,
            c.fio AS client_fio,
            d.fio AS driver_fio,
            o.product,
            o.quantity,
            o.comment,
            o.delivery_deadline,
            o.delay_reason
        FROM orders o
        JOIN order_statuses os ON o.status_id = os.id
        JOIN clients c ON o.client_id = c.id
        JOIN drivers d ON o.driver_id = d.id
        WHERE os.status_name = 'В ожидании'
    """)

    raw_orders = cursor.fetchall()
    orders = []
    current_time = datetime.now()
    for row in raw_orders:
        # Теперь row - это sqlite3.Row, можно обращаться по именам столбцов
        order_id = row['id']
        creation_date_str = row['creation_date']
        status_name = row['status_name']
        delivery_address = row['delivery_address']
        client_fio = row['client_fio']
        driver_fio = row['driver_fio']
        product = row['product']
        quantity = row['quantity']
        comment = row['comment']
        delivery_deadline = row['delivery_deadline']
        delay_reason = row['delay_reason']

        creation_date = datetime.strptime(creation_date_str, '%Y-%m-%d %H:%M:%S') # Assuming format
        
        # Check if overdue by 30 minutes
        if current_time - creation_date > timedelta(minutes=30):
            if not delay_reason or delay_reason == "": # Only update if not already set or empty
                delay_reason = "превышено, водитель не найден"
                update_order_delay_reason(order_id, delay_reason) # Update in DB
        
        # Возвращаем словарь для согласованности
        processed_order = {
            "id": order_id,
            "creation_date": creation_date_str,
            "status_name": status_name,
            "delivery_address": delivery_address,
            "client_fio": client_fio,
            "driver_fio": driver_fio,
            "product": product,
            "quantity": quantity,
            "comment": comment,
            "delivery_deadline": delivery_deadline,
            "delay_reason": delay_reason
        }
        orders.append(processed_order)
    
    conn.close()
    return orders

def get_in_progress_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            o.id,
            o.creation_date,
            os.status_name,
            o.delivery_address,
            c.fio AS client_fio,
            d.fio AS driver_fio,
            o.product,
            o.quantity,
            o.comment,
            o.delivery_deadline,
            o.delay_reason
        FROM orders o
        JOIN order_statuses os ON o.status_id = os.id
        JOIN clients c ON o.client_id = c.id
        JOIN drivers d ON o.driver_id = d.id
        WHERE os.status_name = 'В процессе'
    """)
    raw_orders = cursor.fetchall()
    orders = []
    current_time = datetime.now()
    for row in raw_orders:
        # Теперь row - это sqlite3.Row, можно обращаться по именам столбцов
        order_id = row['id']
        creation_date_str = row['creation_date']
        status_name = row['status_name']
        delivery_address = row['delivery_address']
        client_fio = row['client_fio']
        driver_fio = row['driver_fio']
        product = row['product']
        quantity = row['quantity']
        comment = row['comment']
        delivery_deadline = row['delivery_deadline']
        delay_reason = row['delay_reason']
        
        delivery_deadline_hours = 0
        if delivery_deadline and "час" in delivery_deadline:
            try:
                delivery_deadline_hours = int(delivery_deadline.split(" ")[0])
            except ValueError:
                pass 
        
        creation_date = datetime.strptime(creation_date_str, '%Y-%m-%d %H:%M:%S')
        
        if current_time - creation_date > timedelta(hours=delivery_deadline_hours):
            if not delay_reason or delay_reason == "":
                delay_reason = "водитель стоит в пробке"
                update_order_delay_reason(order_id, delay_reason) # Update in DB
        
        # Возвращаем словарь для согласованности
        processed_order = {
            "id": order_id,
            "creation_date": creation_date_str,
            "status_name": status_name,
            "delivery_address": delivery_address,
            "client_fio": client_fio,
            "driver_fio": driver_fio,
            "product": product,
            "quantity": quantity,
            "comment": comment,
            "delivery_deadline": delivery_deadline,
            "delay_reason": delay_reason
        }
        orders.append(processed_order)

    conn.close()
    return orders

def get_all_drivers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, fio, contact_info, telegram_id, status FROM drivers")
    drivers = cursor.fetchall()
    conn.close()
    return drivers

def update_driver_status(driver_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT os.status_name
        FROM orders o
        JOIN order_statuses os ON o.status_id = os.id
        WHERE o.driver_id = ? AND (os.status_name = 'В ожидании' OR os.status_name = 'В процессе')
    """, (driver_id,))
    
    active_orders = cursor.fetchall()
    
    if active_orders:
        cursor.execute("UPDATE drivers SET status = 'Занят' WHERE id = ?", (driver_id,))
    else:
        cursor.execute("UPDATE drivers SET status = 'Свободен' WHERE id = ?", (driver_id,))
    
    conn.commit()
    conn.close()

def get_all_clients():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, fio, contact_info, address FROM clients")
    clients = cursor.fetchall()
    conn.close()
    return clients

def add_client(fio, contact_info, address):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clients (fio, contact_info, address) VALUES (?, ?, ?)", (fio, contact_info, address))
    conn.commit()
    conn.close()

def update_client(client_id, fio, contact_info, address):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE clients SET fio = ?, contact_info = ?, address = ? WHERE id = ?", (fio, contact_info, address, client_id))
    conn.commit()
    conn.close()

def delete_client(client_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()

def add_driver(fio, contact_info, telegram_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO drivers (fio, contact_info, telegram_id) VALUES (?, ?, ?)", (fio, contact_info, telegram_id))
    conn.commit()
    conn.close()

def update_driver(driver_id, fio, contact_info, telegram_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE drivers SET fio = ?, contact_info = ?, telegram_id = ? WHERE id = ?", (fio, contact_info, telegram_id, driver_id))
    conn.commit()
    conn.close()

def delete_driver(driver_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM drivers WHERE id = ?", (driver_id,))
    conn.commit()
    conn.close()

def get_all_dispatchers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.username, r.role_name
        FROM users u
        JOIN roles r ON u.role_id = r.id
        WHERE r.role_name = 'Диспетчер'
    """)
    dispatchers = cursor.fetchall()
    conn.close()
    return dispatchers

def add_dispatcher(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    dispatcher_role_id = cursor.execute("SELECT id FROM roles WHERE role_name = 'Диспетчер'").fetchone()['id']
    cursor.execute("INSERT INTO users (username, password_hash, role_id) VALUES (?, ?, ?)", (username, password, dispatcher_role_id))
    conn.commit()
    conn.close()

def update_dispatcher(user_id, username, password=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if password:
        cursor.execute("UPDATE users SET username = ?, password_hash = ? WHERE id = ?", (username, password, user_id))
    else:
        cursor.execute("UPDATE users SET username = ? WHERE id = ?", (username, user_id))
    conn.commit()
    conn.close()

def delete_dispatcher(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def update_order_status(order_id, new_status_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    status_id = get_status_id(new_status_name)
    cursor.execute("UPDATE orders SET status_id = ? WHERE id = ?", (status_id, order_id))
    conn.commit()
    conn.close()

def create_order(creation_date, status_id, delivery_address, client_id, driver_id, product, quantity, comment, delivery_deadline, dispatcher_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO orders (creation_date, status_id, delivery_address, client_id, driver_id, product, quantity, comment, delivery_deadline, dispatcher_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (creation_date, status_id, delivery_address, client_id, driver_id, product, quantity, comment, delivery_deadline, dispatcher_id))
    conn.commit()
    conn.close()

def delete_order(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()

def get_status_id(status_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    print(f"[DEBUG_DB_OPERATIONS] Запрос статуса по имени: {status_name}")
    cursor.execute("SELECT id FROM order_statuses WHERE status_name = ?", (status_name,))
    result = cursor.fetchone()
    print(f"[DEBUG_DB_OPERATIONS] Результат запроса статуса: {result}")
    conn.close()
    return result['id'] if result else None

def get_client_id_by_fio(fio):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM clients WHERE fio = ?", (fio,))
    result = cursor.fetchone()
    conn.close()
    return result['id'] if result else None

def get_driver_id_by_fio(fio):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM drivers WHERE fio = ?", (fio,))
    result = cursor.fetchone()
    conn.close()
    return result['id'] if result else None

def get_user_id_and_role(username, password_hash):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, r.role_name
        FROM users u
        JOIN roles r ON u.role_id = r.id
        WHERE u.username = ? AND u.password_hash = ?
    """, (username, password_hash))
    print(f"[DEBUG_DB_OPERATIONS] Запрос к БД с: username={username}, password_hash={password_hash}")
    user = cursor.fetchone()
    conn.close()
    return user 