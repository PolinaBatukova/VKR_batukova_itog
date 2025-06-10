import sqlite3
import hashlib

DATABASE_NAME = "courier_app.db"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_tables():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_name TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role_id INTEGER,
            FOREIGN KEY (role_id) REFERENCES roles(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fio TEXT NOT NULL,
            contact_info TEXT,
            address TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fio TEXT NOT NULL,
            contact_info TEXT,
            telegram_id TEXT UNIQUE,
            status TEXT DEFAULT 'Свободен' -- Занят/Свободен
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_statuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status_name TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creation_date TEXT NOT NULL,
            status_id INTEGER,
            delivery_address TEXT,
            client_id INTEGER,
            driver_id INTEGER,
            product TEXT,
            quantity TEXT,
            comment TEXT,
            delivery_deadline TEXT, -- Срок доставки (например, 3 часа)
            delay_reason TEXT, -- Причина задержки
            FOREIGN KEY (status_id) REFERENCES order_statuses(id),
            FOREIGN KEY (client_id) REFERENCES clients(id),
            FOREIGN KEY (driver_id) REFERENCES drivers(id)
        )
    """)

    # Добавление начальных данных для статусов и ролей
    cursor.execute("INSERT OR IGNORE INTO order_statuses (status_name) VALUES (?)", ('В ожидании',))
    cursor.execute("INSERT OR IGNORE INTO order_statuses (status_name) VALUES (?)", ('В процессе',))
    cursor.execute("INSERT OR IGNORE INTO order_statuses (status_name) VALUES (?)", ('Доставлен',))
    cursor.execute("INSERT OR IGNORE INTO order_statuses (status_name) VALUES (?)", ('Отменен',))

    cursor.execute("INSERT OR IGNORE INTO roles (role_name) VALUES (?)", ('Админ',))
    cursor.execute("INSERT OR IGNORE INTO roles (role_name) VALUES (?)", ('Диспетчер',))

    # Добавление пользователей по умолчанию
    admin_role_id = cursor.execute("SELECT id FROM roles WHERE role_name = 'Админ'").fetchone()[0]
    dispatcher_role_id = cursor.execute("SELECT id FROM roles WHERE role_name = 'Диспетчер'").fetchone()[0]

    admin_password_hash = hash_password("admin_pass")
    dispatcher_password_hash = hash_password("dispatcher_pass")

    cursor.execute("INSERT OR IGNORE INTO users (username, password_hash, role_id) VALUES (?, ?, ?)", ('admin', admin_password_hash, admin_role_id))
    cursor.execute("INSERT OR IGNORE INTO users (username, password_hash, role_id) VALUES (?, ?, ?)", ('dispatcher', dispatcher_password_hash, dispatcher_role_id))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("База данных и таблицы успешно созданы.") 