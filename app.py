import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import hashlib
import os
import pandas as pd
import openpyxl
# from database import db_operations # Удаляем прямой импорт db_operations
from datetime import datetime
from PIL import Image, ImageTk # Импорт для работы с изображениями
import requests
from tkcalendar import Calendar # Импорт для календаря

DATABASE_NAME = "courier_app.db"
FLASK_API_BASE_URL = "http://127.0.0.1:5000" # Базовый URL для Flask API

def hash_password(password):
    print(f"[DEBUG_APP_HASH] Пароль до хеширования: '{password}'")
    hashed_pass = hashlib.sha256(password.encode()).hexdigest()
    print(f"[DEBUG_APP_HASH] Пароль после хеширования: '{hashed_pass}'")
    return hashed_pass

class CourierApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Транспортная служба")
        self.geometry("1200x800")
        self.configure(bg="#ADD8E6") # Бледно-голубой фон
        self.logo_image = None # Для хранения ссылки на изображение
        self.load_logo()
        self.create_login_widgets()

    def load_logo(self):
        try:
            original_image = Image.open("logo.png")
            resized_image = original_image.resize((100, 100), Image.Resampling.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(resized_image)
        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Файл logo.png не найден. Пожалуйста, убедитесь, что он находится в корневой папке проекта.")
            self.logo_image = None # Очищаем, если не найдено
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить logo.png: {e}")
            self.logo_image = None

    def create_login_widgets(self):
        # Очищаем все существующие виджеты
        for widget in self.winfo_children():
            if widget.winfo_class() != 'Menu': # Пропускаем меню, если оно есть
                widget.destroy()

        self.login_frame = ttk.Frame(self, padding="20", style="LightBlue.TFrame")
        self.login_frame.pack(expand=True, fill="both", anchor="center")
        
        # Стиль для фреймов
        self.style = ttk.Style()
        self.style.configure("LightBlue.TFrame", background="#ADD8E6")

        # Размещаем логотип
        if self.logo_image:
            self.logo_label = ttk.Label(self.login_frame, image=self.logo_image, background="#ADD8E6")
        else:
            self.logo_label = ttk.Label(self.login_frame, text="[ЛОГОТИП НЕ ЗАГРУЖЕН]", background="#ADD8E6")
        self.logo_label.place(relx=0.98, rely=0.02, anchor='ne') # Правый верхний угол

        ttk.Label(self.login_frame, text="Логин:", background="#ADD8E6").pack(pady=5)
        self.username_entry = ttk.Entry(self.login_frame, width=30)
        self.username_entry.pack(pady=5)

        ttk.Label(self.login_frame, text="Пароль:", background="#ADD8E6").pack(pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*", width=30)
        self.password_entry.pack(pady=5)

        ttk.Button(self.login_frame, text="Войти", command=self.authenticate_user).pack(pady=10)
        ttk.Button(self.login_frame, text="Зарегистрироваться", command=self.show_registration_panel).pack(pady=5)

    def show_registration_panel(self):
        self.clear_all_frames()

        self.registration_frame = ttk.Frame(self, padding="20", style="LightBlue.TFrame")
        self.registration_frame.pack(expand=True, fill="both", anchor="center")

        # Размещаем логотип
        if self.logo_image:
            self.logo_label = ttk.Label(self.registration_frame, image=self.logo_image, background="#ADD8E6")
        else:
            self.logo_label = ttk.Label(self.registration_frame, text="[ЛОГОТИП НЕ ЗАГРУЖЕН]", background="#ADD8E6")
        self.logo_label.place(relx=0.98, rely=0.02, anchor='ne')

        ttk.Label(self.registration_frame, text="Регистрация нового пользователя", font=("Arial", 20), background="#ADD8E6").pack(pady=15)

        ttk.Label(self.registration_frame, text="Имя пользователя:", background="#ADD8E6").pack(pady=5)
        self.reg_username_entry = ttk.Entry(self.registration_frame, width=30)
        self.reg_username_entry.pack(pady=5)

        ttk.Label(self.registration_frame, text="Пароль:", background="#ADD8E6").pack(pady=5)
        self.reg_password_entry = ttk.Entry(self.registration_frame, show="*", width=30)
        self.reg_password_entry.pack(pady=5)

        ttk.Label(self.registration_frame, text="Выберите роль:", background="#ADD8E6").pack(pady=5)
        self.role_options = ["Админ", "Диспетчер"]
        self.reg_role_combobox = ttk.Combobox(self.registration_frame, values=self.role_options, width=28)
        self.reg_role_combobox.pack(pady=5)
        self.reg_role_combobox.set("Диспетчер")

        ttk.Label(self.registration_frame, text="Ключ администратора:", background="#ADD8E6").pack(pady=5)
        self.admin_key_entry = ttk.Entry(self.registration_frame, show="*", width=30)
        self.admin_key_entry.pack(pady=5)

        ttk.Button(self.registration_frame, text="Зарегистрировать", command=self.register_new_user).pack(pady=10)
        ttk.Button(self.registration_frame, text="Назад к входу", command=self.create_login_widgets).pack(pady=5)

    def register_new_user(self):
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()
        selected_role = self.reg_role_combobox.get()
        admin_key = self.admin_key_entry.get()

        ADMIN_REGISTRATION_KEY = "admin_key123"
        if admin_key != ADMIN_REGISTRATION_KEY:
            messagebox.showerror("Ошибка регистрации", "Неверный ключ администратора.", parent=self.registration_frame)
            return

        if not username or not password or not selected_role:
            messagebox.showerror("Ошибка регистрации", "Пожалуйста, заполните все поля.", parent=self.registration_frame)
            return

        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM roles WHERE role_name = ?", (selected_role,))
            role_id_result = cursor.fetchone()
            if not role_id_result:
                messagebox.showerror("Ошибка", "Выбранная роль не найдена.", parent=self.registration_frame)
                conn.close()
                return
            role_id = role_id_result[0]

            hashed_password = hash_password(password)

            cursor.execute("INSERT INTO users (username, password_hash, role_id) VALUES (?, ?, ?)", (username, hashed_password, role_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Успех", f"Пользователь {username} ({selected_role}) успешно зарегистрирован!", parent=self.registration_frame)
            self.create_login_widgets() # Возвращаемся к экрану входа
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка регистрации", "Пользователь с таким именем уже существует.", parent=self.registration_frame)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при регистрации: {e}", parent=self.registration_frame)

    def authenticate_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Ошибка", "Пожалуйста, введите логин и пароль.")
            return

        hashed_password = hash_password(password) # Пароль все еще хешируется на клиенте перед отправкой

        try:
            response = requests.post(f"{FLASK_API_BASE_URL}/authenticate", json={
                "username": username,
                "password_hash": hashed_password
            })
            response.raise_for_status() # Вызовет исключение для HTTP ошибок (4xx или 5xx)
            print(response.json())
            user_data = response.json()
            if user_data and "user_id" in user_data and "role" in user_data:
                user_id = user_data["user_id"]
                role = user_data["role"]
                self.current_user_id = user_id # Сохраняем ID текущего пользователя
                self.current_user_role = role # Сохраняем роль текущего пользователя
                messagebox.showinfo("Успех", f"Добро пожаловать, {username}! Ваша роль: {role}")
                if role == "Админ":
                    self.show_admin_panel(user_id)
                elif role == "Диспетчер":
                    self.show_dispatcher_panel(user_id)
            else:
                messagebox.showerror("Ошибка", "Неверный логин или пароль.")

        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.")
        except requests.exceptions.HTTPError as e:
            error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
            messagebox.showerror("Ошибка", f"Ошибка аутентификации: {error_message}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")

    def show_admin_panel(self, user_id):
        self.clear_all_frames()

        self.admin_frame = ttk.Frame(self, padding="20", style="LightBlue.TFrame")
        self.admin_frame.pack(expand=True, fill="both")

        # Размещаем логотип
        if self.logo_image:
            self.logo_label = ttk.Label(self.admin_frame, image=self.logo_image, background="#ADD8E6")
        else:
            self.logo_label = ttk.Label(self.admin_frame, text="[ЛОГОТИП НЕ ЗАГРУЖЕН]", background="#ADD8E6")
        self.logo_label.place(relx=0.98, rely=0.02, anchor='ne')

        ttk.Label(self.admin_frame, text="Панель Админа", font=("Arial", 24), background="#ADD8E6").pack(pady=20, anchor='n')

        # Кнопки для управления данными
        button_frame = ttk.Frame(self.admin_frame, style="LightBlue.TFrame")
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Показать клиентов", command=self.show_clients).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="Добавить/Изменить/Удалить клиента", command=self.manage_clients).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text="Показать водителей", command=self.show_drivers).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(button_frame, text="Добавить/Изменить/Удалить водителя", command=self.manage_drivers).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(button_frame, text="Показать диспетчеров", command=self.show_dispatchers).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(button_frame, text="Добавить/Изменить/Удалить диспетчера", command=self.manage_dispatchers).grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(self.admin_frame, text="Выйти", command=self.logout).pack(pady=20, side="bottom")

        self.admin_content_frame = ttk.Frame(self.admin_frame, padding="10", style="LightBlue.TFrame")
        self.admin_content_frame.pack(expand=True, fill="both")

    def show_dispatcher_panel(self, user_id):
        self.clear_all_frames()

        self.dispatcher_frame = ttk.Frame(self, padding="20", style="LightBlue.TFrame")
        self.dispatcher_frame.pack(expand=True, fill="both")

        # Размещаем логотип
        if self.logo_image:
            self.logo_label = ttk.Label(self.dispatcher_frame, image=self.logo_image, background="#ADD8E6")
        else:
            self.logo_label = ttk.Label(self.dispatcher_frame, text="[ЛОГОТИП НЕ ЗАГРУЖЕН]", background="#ADD8E6")
        self.logo_label.place(relx=0.98, rely=0.02, anchor='ne')

        ttk.Label(self.dispatcher_frame, text="Панель Диспетчера", font=("Arial", 24), background="#ADD8E6").pack(pady=20, anchor='n')

        # Кнопки для управления заказами и водителями
        button_frame = ttk.Frame(self.dispatcher_frame, style="LightBlue.TFrame")
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Показать все заказы", command=self.show_orders_dispatcher).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="Выполненные заказы", command=self.show_completed_orders_dispatcher).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text="Заказы в ожидании", command=self.show_pending_orders_dispatcher).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(button_frame, text="Заказы в процессе", command=self.show_in_progress_orders_dispatcher).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(button_frame, text="Показать всех водителей", command=self.show_drivers_dispatcher).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(button_frame, text="Обновить статус заказа", command=self.update_order_status_dialog).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="Создать заказ", command=self.create_order_dialog).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text="Удалить заказ", command=self.delete_order_dialog).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(button_frame, text="Создать отчет о курьерах", command=self.create_driver_report).grid(row=1, column=3, padx=5, pady=5)

        ttk.Button(self.dispatcher_frame, text="Выйти", command=self.logout).pack(pady=20, side="bottom")

        self.dispatcher_content_frame = ttk.Frame(self.dispatcher_frame, padding="10", style="LightBlue.TFrame")
        self.dispatcher_content_frame.pack(expand=True, fill="both")

    def logout(self):
        self.clear_all_frames()
        self.create_login_widgets()
    
    def clear_all_frames(self):
        for widget in self.winfo_children():
            if widget.winfo_class() != 'Menu':
                widget.destroy()

    def clear_main_display(self):
        if hasattr(self, 'admin_content_frame') and self.admin_content_frame.winfo_exists():
            for widget in self.admin_content_frame.winfo_children():
                widget.destroy()
        if hasattr(self, 'dispatcher_content_frame') and self.dispatcher_content_frame.winfo_exists():
            for widget in self.dispatcher_content_frame.winfo_children():
                widget.destroy()

    # Функции для панели Администратора
    def show_clients(self):
        self.clear_main_display()
        try:
            response = requests.get(f"{FLASK_API_BASE_URL}/clients")
            response.raise_for_status()
            clients = response.json()

            columns = ("ID", "ФИО", "Контактная информация", "Адрес")
            self.tree_clients = ttk.Treeview(self.admin_content_frame, columns=columns, show="headings")
            for col in columns:
                self.tree_clients.heading(col, text=col)
                self.tree_clients.column(col, width=150)
            self.tree_clients.pack(expand=True, fill="both", padx=10, pady=10)

            for client in clients:
                self.tree_clients.insert("", "end", values=(client['id'], client['fio'], client['contact_info'], client['address']))
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.")
        except requests.exceptions.HTTPError as e:
            error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
            messagebox.showerror("Ошибка", f"Ошибка получения клиентов: {error_message}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")

    def manage_clients(self):
        self.clear_main_display()

        manage_frame = ttk.Frame(self.admin_content_frame, padding="10", style="LightBlue.TFrame")
        manage_frame.pack(pady=10)

        ttk.Label(manage_frame, text="ID клиента (для изменения/удаления):", background="#ADD8E6").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.client_id_entry = ttk.Entry(manage_frame, width=30)
        self.client_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(manage_frame, text="ФИО:", background="#ADD8E6").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.client_fio_entry = ttk.Entry(manage_frame, width=30)
        self.client_fio_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(manage_frame, text="Контактная информация:", background="#ADD8E6").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.client_contact_entry = ttk.Entry(manage_frame, width=30)
        self.client_contact_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(manage_frame, text="Адрес:", background="#ADD8E6").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.client_address_entry = ttk.Entry(manage_frame, width=30)
        self.client_address_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        ttk.Button(manage_frame, text="Добавить", command=self.add_client).grid(row=4, column=0, padx=5, pady=10)
        ttk.Button(manage_frame, text="Изменить", command=self.update_client).grid(row=4, column=1, padx=5, pady=10)
        ttk.Button(manage_frame, text="Удалить", command=self.delete_client).grid(row=4, column=2, padx=5, pady=10)
        
        # self.show_clients()

    def add_client(self):
        fio = self.client_fio_entry.get()
        contact = self.client_contact_entry.get()
        address = self.client_address_entry.get()
        if fio and contact and address:
            try:
                response = requests.post(f"{FLASK_API_BASE_URL}/clients", json={
                    "fio": fio,
                    "contact_info": contact,
                    "address": address
                })
                response.raise_for_status()
                messagebox.showinfo("Успех", "Клиент успешно добавлен.")
                self.clear_client_entries()
                self.show_clients()
            except requests.exceptions.ConnectionError:
                messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.")
            except requests.exceptions.HTTPError as e:
                error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
                messagebox.showerror("Ошибка", f"Ошибка добавления клиента: {error_message}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля для добавления клиента.")

    def update_client(self):
        client_id_str = self.client_id_entry.get()
        fio = self.client_fio_entry.get()
        contact = self.client_contact_entry.get()
        address = self.client_address_entry.get()
        if client_id_str and fio and contact and address:
            try:
                client_id = int(client_id_str)
                response = requests.put(f"{FLASK_API_BASE_URL}/clients/{client_id}", json={
                    "fio": fio,
                    "contact_info": contact,
                    "address": address
                })
                response.raise_for_status()
                messagebox.showinfo("Успех", "Данные клиента успешно обновлены.")
                self.clear_client_entries()
                self.show_clients()
            except ValueError:
                messagebox.showerror("Ошибка", "ID клиента должен быть числом.")
            except requests.exceptions.ConnectionError:
                messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.")
            except requests.exceptions.HTTPError as e:
                error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
                messagebox.showerror("Ошибка", f"Ошибка обновления клиента: {error_message}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните ID и все поля для изменения клиента.")

    def delete_client(self):
        client_id_str = self.client_id_entry.get()
        if client_id_str:
            try:
                client_id = int(client_id_str)
                if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить клиента с ID {client_id}?", parent=self):
                    response = requests.delete(f"{FLASK_API_BASE_URL}/clients/{client_id}")
                    response.raise_for_status()
                    messagebox.showinfo("Успех", "Клиент успешно удален.")
                    self.clear_client_entries()
                    self.show_clients()
            except ValueError:
                messagebox.showerror("Ошибка", "ID клиента должен быть числом.")
            except requests.exceptions.ConnectionError:
                messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.")
            except requests.exceptions.HTTPError as e:
                error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
                messagebox.showerror("Ошибка", f"Ошибка удаления клиента: {error_message}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, введите ID клиента для удаления.")

    def clear_client_entries(self):
        self.client_id_entry.delete(0, tk.END)
        self.client_fio_entry.delete(0, tk.END)
        self.client_contact_entry.delete(0, tk.END)
        self.client_address_entry.delete(0, tk.END)

    # Функции для панели Администратора - Водители
    def show_drivers(self):
        self.clear_main_display()
        try:
            response = requests.get(f"{FLASK_API_BASE_URL}/drivers")
            response.raise_for_status()
            drivers = response.json()
            print(f"[DEBUG_APP_DRIVERS] Полученные данные водителей от API: {drivers}")
            columns = ("ID", "ФИО", "Контактная информация", "Telegram ID", "Статус")
            self.tree_drivers = ttk.Treeview(self.admin_content_frame, columns=columns, show="headings")
            for col in columns:
                self.tree_drivers.heading(col, text=col)
                self.tree_drivers.column(col, width=150)
            self.tree_drivers.pack(expand=True, fill="both", padx=10, pady=10)

            for driver in drivers:
                self.tree_drivers.insert("", "end", values=(driver['id'], driver['fio'], driver['contact_info'], driver['telegram_id'], driver['status']))
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.")
        except requests.exceptions.HTTPError as e:
            error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
            messagebox.showerror("Ошибка", f"Ошибка получения водителей: {error_message}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")

    def manage_drivers(self):
        self.clear_main_display()

        manage_frame = ttk.Frame(self.admin_content_frame, padding="10", style="LightBlue.TFrame")
        manage_frame.pack(pady=10)

        ttk.Label(manage_frame, text="ID водителя (для изменения/удаления/статуса):", background="#ADD8E6").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.driver_id_entry = ttk.Entry(manage_frame, width=30)
        self.driver_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(manage_frame, text="ФИО:", background="#ADD8E6").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.driver_fio_entry = ttk.Entry(manage_frame, width=30)
        self.driver_fio_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(manage_frame, text="Контактная информация:", background="#ADD8E6").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.driver_contact_entry = ttk.Entry(manage_frame, width=30)
        self.driver_contact_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(manage_frame, text="Telegram ID:", background="#ADD8E6").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.driver_telegram_id_entry = ttk.Entry(manage_frame, width=30)
        self.driver_telegram_id_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(manage_frame, text="Статус:", background="#ADD8E6").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.driver_status_combobox = ttk.Combobox(manage_frame, values=["Активен", "Неактивен", "На смене", "Не на смене"], state="readonly", width=27)
        self.driver_status_combobox.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        self.driver_status_combobox.set("Активен")

        ttk.Button(manage_frame, text="Добавить", command=self.add_driver).grid(row=5, column=0, padx=5, pady=10)
        ttk.Button(manage_frame, text="Изменить", command=self.update_driver).grid(row=5, column=1, padx=5, pady=10)
        ttk.Button(manage_frame, text="Удалить", command=self.delete_driver).grid(row=5, column=2, padx=5, pady=10)
        ttk.Button(manage_frame, text="Изменить статус", command=self.update_driver_status).grid(row=6, column=0, columnspan=3, padx=5, pady=10)

        # self.show_drivers()

    def add_driver(self):
        fio = self.driver_fio_entry.get()
        contact = self.driver_contact_entry.get()
        telegram_id = self.driver_telegram_id_entry.get()
        status = self.driver_status_combobox.get()

        if fio and contact and telegram_id and status:
            try:
                response = requests.post(f"{FLASK_API_BASE_URL}/drivers", json={
                    "fio": fio,
                    "contact_info": contact,
                    "telegram_id": telegram_id,
                    "status": status
                })
                response.raise_for_status()
                messagebox.showinfo("Успех", "Водитель успешно добавлен.")
                self.clear_driver_entries()
                self.show_drivers()
            except requests.exceptions.ConnectionError:
                messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.")
            except requests.exceptions.HTTPError as e:
                error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
                messagebox.showerror("Ошибка", f"Ошибка добавления водителя: {error_message}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля для добавления водителя.")

    def update_driver(self):
        driver_id_str = self.driver_id_entry.get()
        fio = self.driver_fio_entry.get()
        contact = self.driver_contact_entry.get()
        telegram_id = self.driver_telegram_id_entry.get()
        status = self.driver_status_combobox.get()

        if driver_id_str and fio and contact and telegram_id and status:
            try:
                driver_id = int(driver_id_str)
                response = requests.put(f"{FLASK_API_BASE_URL}/drivers/{driver_id}", json={
                    "fio": fio,
                    "contact_info": contact,
                    "telegram_id": telegram_id,
                    "status": status
                })
                response.raise_for_status()
                messagebox.showinfo("Успех", "Данные водителя успешно обновлены.")
                self.clear_driver_entries()
                self.show_drivers()
            except ValueError:
                messagebox.showerror("Ошибка", "ID водителя должен быть числом.")
            except requests.exceptions.ConnectionError:
                messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.")
            except requests.exceptions.HTTPError as e:
                error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
                messagebox.showerror("Ошибка", f"Ошибка обновления водителя: {error_message}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните ID и все поля для изменения водителя.")

    def delete_driver(self):
        driver_id_str = self.driver_id_entry.get()
        if driver_id_str:
            try:
                driver_id = int(driver_id_str)
                if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить водителя с ID {driver_id}?", parent=self):
                    response = requests.delete(f"{FLASK_API_BASE_URL}/drivers/{driver_id}")
                    response.raise_for_status()
                    messagebox.showinfo("Успех", "Водитель успешно удален.")
                    self.clear_driver_entries()
                    self.show_drivers()
            except ValueError:
                messagebox.showerror("Ошибка", "ID водителя должен быть числом.")
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, введите ID водителя для удаления.")

    def update_driver_status(self):
        driver_id_str = self.driver_id_entry.get()
        new_status = self.driver_status_combobox.get()
        if driver_id_str and new_status:
            try:
                driver_id = int(driver_id_str)
                response = requests.put(f"{FLASK_API_BASE_URL}/drivers/update_status/{driver_id}", json={
                    "status": new_status
                })
                response.raise_for_status()
                messagebox.showinfo("Успех", "Статус водителя успешно обновлен.")
                self.clear_driver_entries()
                self.show_drivers()
            except ValueError:
                messagebox.showerror("Ошибка", "ID водителя должен быть числом.")
            except requests.exceptions.ConnectionError:
                messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.")
            except requests.exceptions.HTTPError as e:
                error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
                messagebox.showerror("Ошибка", f"Ошибка обновления статуса водителя: {error_message}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, введите ID водителя и выберите новый статус.")

    def clear_driver_entries(self):
        self.driver_id_entry.delete(0, tk.END)
        self.driver_fio_entry.delete(0, tk.END)
        self.driver_contact_entry.delete(0, tk.END)
        self.driver_telegram_id_entry.delete(0, tk.END)

    # Функции для панели Администратора - Диспетчеры
    def show_dispatchers(self):
        self.clear_main_display()
        try:
            response = requests.get(f"{FLASK_API_BASE_URL}/dispatchers")
            response.raise_for_status()
            dispatchers = response.json()

            columns = ("ID", "Имя пользователя", "Роль")
            self.tree_dispatchers = ttk.Treeview(self.admin_content_frame, columns=columns, show="headings")
            for col in columns:
                self.tree_dispatchers.heading(col, text=col)
                self.tree_dispatchers.column(col, width=150)
            self.tree_dispatchers.pack(expand=True, fill="both", padx=10, pady=10)

            for dispatcher in dispatchers:
                self.tree_dispatchers.insert("", "end", values=(dispatcher['id'], dispatcher['username'], dispatcher['role_name']))
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.")
        except requests.exceptions.HTTPError as e:
            error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
            messagebox.showerror("Ошибка", f"Ошибка получения диспетчеров: {error_message}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")

    def manage_dispatchers(self):
        self.clear_main_display()

        manage_frame = ttk.Frame(self.admin_content_frame, padding="10", style="LightBlue.TFrame")
        manage_frame.pack(pady=10)

        ttk.Label(manage_frame, text="ID пользователя (для изменения/удаления):", background="#ADD8E6").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.dispatcher_user_id_entry = ttk.Entry(manage_frame, width=30)
        self.dispatcher_user_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(manage_frame, text="Имя пользователя:", background="#ADD8E6").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.dispatcher_username_entry = ttk.Entry(manage_frame, width=30)
        self.dispatcher_username_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(manage_frame, text="Пароль:", background="#ADD8E6").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.dispatcher_password_entry = ttk.Entry(manage_frame, show="*", width=30)
        self.dispatcher_password_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Button(manage_frame, text="Добавить", command=self.add_dispatcher).grid(row=3, column=0, padx=5, pady=10)
        ttk.Button(manage_frame, text="Изменить", command=self.update_dispatcher).grid(row=3, column=1, padx=5, pady=10)
        ttk.Button(manage_frame, text="Удалить", command=self.delete_dispatcher).grid(row=3, column=2, padx=5, pady=10)

        # self.show_dispatchers()

    def add_dispatcher(self):
        username = self.dispatcher_username_entry.get()
        password = self.dispatcher_password_entry.get()
        if username and password:
            try:
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                response = requests.post(f"{FLASK_API_BASE_URL}/dispatchers", json={
                    "username": username,
                    "password": hashed_password
                })
                response.raise_for_status()
                messagebox.showinfo("Успех", "Диспетчер успешно добавлен.")
                self.clear_dispatcher_entries()
                self.show_dispatchers()
            except requests.exceptions.ConnectionError:
                messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.")
            except requests.exceptions.HTTPError as e:
                error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
                messagebox.showerror("Ошибка", f"Ошибка добавления диспетчера: {error_message}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля для добавления диспетчера.")

    def update_dispatcher(self):
        user_id_str = self.dispatcher_user_id_entry.get()
        username = self.dispatcher_username_entry.get()
        password = self.dispatcher_password_entry.get()
        if user_id_str and username and password:
            try:
                user_id = int(user_id_str)
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                response = requests.put(f"{FLASK_API_BASE_URL}/dispatchers/{user_id}", json={
                    "username": username,
                    "password": hashed_password
                })
                response.raise_for_status()
                messagebox.showinfo("Успех", "Данные диспетчера успешно обновлены.")
                self.clear_dispatcher_entries()
                self.show_dispatchers()
            except ValueError:
                messagebox.showerror("Ошибка", "ID пользователя должен быть числом.")
            except requests.exceptions.ConnectionError:
                messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.")
            except requests.exceptions.HTTPError as e:
                error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
                messagebox.showerror("Ошибка", f"Ошибка обновления диспетчера: {error_message}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните ID и все поля для изменения диспетчера.")

    def delete_dispatcher(self):
        user_id_str = self.dispatcher_user_id_entry.get()
        if user_id_str:
            try:
                user_id = int(user_id_str)
                if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить диспетчера с ID {user_id}?", parent=self):
                    response = requests.delete(f"{FLASK_API_BASE_URL}/dispatchers/{user_id}")
                    response.raise_for_status()
                    messagebox.showinfo("Успех", "Диспетчер успешно удален.")
                    self.clear_dispatcher_entries()
                    self.show_dispatchers()
            except ValueError:
                messagebox.showerror("Ошибка", "ID пользователя должен быть числом.")
            except requests.exceptions.ConnectionError:
                messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.")
            except requests.exceptions.HTTPError as e:
                error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
                messagebox.showerror("Ошибка", f"Ошибка удаления диспетчера: {error_message}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, введите ID пользователя для удаления.")

    def clear_dispatcher_entries(self):
        self.dispatcher_user_id_entry.delete(0, tk.END)
        self.dispatcher_username_entry.delete(0, tk.END)
        self.dispatcher_password_entry.delete(0, tk.END)

    def setup_dispatcher_order_tree(self):
        columns = (
            "ID", "Дата создания", "Статус", "Адрес доставки",
            "Клиент", "Водитель", "Продукт", "Количество",
            "Комментарий", "Срок доставки"
        )
        self.tree_orders = ttk.Treeview(self.dispatcher_content_frame, columns=columns, show="headings")
        for col in columns:
            self.tree_orders.heading(col, text=col)
            self.tree_orders.column(col, width=100)
        self.tree_orders.pack(expand=True, fill="both", padx=10, pady=10)

    # Функции для панели Диспетчера
    def show_orders_dispatcher(self):
        self.clear_main_display()
        self.setup_dispatcher_order_tree()
        try:
            response = requests.get(f"{FLASK_API_BASE_URL}/orders")
            response.raise_for_status()
            orders = response.json()
            for order in orders:
                self.tree_orders.insert("", "end", values=(
                    order['id'],
                    order['creation_date'],
                    order['status_name'],
                    order['delivery_address'],
                    order['client_fio'],
                    order['driver_fio'],
                    order['product'],
                    order['quantity'],
                    order['comment'],
                    order['delivery_deadline']
                ))
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.")
        except requests.exceptions.HTTPError as e:
            error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
            messagebox.showerror("Ошибка", f"Ошибка получения заказов: {error_message}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")

    def show_completed_orders_dispatcher(self):
        self.clear_main_display()
        self.setup_dispatcher_order_tree()
        try:
            response = requests.get(f"{FLASK_API_BASE_URL}/orders/delivered")
            response.raise_for_status()
            orders = response.json()
            for order in orders:
                self.tree_orders.insert("", "end", values=(
                    order['id'],
                    order['creation_date'],
                    order['status_name'],
                    order['delivery_address'],
                    order['client_fio'],
                    order['driver_fio'],
                    order['product'],
                    order['quantity'],
                    order['comment'],
                    order['delivery_deadline']
                ))
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.")
        except requests.exceptions.HTTPError as e:
            error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
            messagebox.showerror("Ошибка", f"Ошибка получения доставленных заказов: {error_message}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")

    def show_pending_orders_dispatcher(self):
        self.clear_main_display()
        self.setup_dispatcher_order_tree()
        try:
            response = requests.get(f"{FLASK_API_BASE_URL}/orders/pending")
            response.raise_for_status()
            orders = response.json()
            for order in orders:
                self.tree_orders.insert("", "end", values=(
                    order['id'],
                    order['creation_date'],
                    order['status_name'],
                    order['delivery_address'],
                    order['client_fio'],
                    order['driver_fio'],
                    order['product'],
                    order['quantity'],
                    order['comment'],
                    order['delivery_deadline']
                ))
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.")
        except requests.exceptions.HTTPError as e:
            error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
            messagebox.showerror("Ошибка", f"Ошибка получения ожидающих заказов: {error_message}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")

    def show_in_progress_orders_dispatcher(self):
        self.clear_main_display()
        self.setup_dispatcher_order_tree()
        try:
            response = requests.get(f"{FLASK_API_BASE_URL}/orders/in_progress")
            response.raise_for_status()
            orders = response.json()
            for order in orders:
                self.tree_orders.insert("", "end", values=(
                    order['id'],
                    order['creation_date'],
                    order['status_name'],
                    order['delivery_address'],
                    order['client_fio'],
                    order['driver_fio'],
                    order['product'],
                    order['quantity'],
                    order['comment'],
                    order['delivery_deadline']
                ))
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.")
        except requests.exceptions.HTTPError as e:
            error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
            messagebox.showerror("Ошибка", f"Ошибка получения заказов в процессе: {error_message}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")

    def show_drivers_dispatcher(self):
        self.clear_main_display()
        columns = ("ID", "ФИО", "Контактная информация", "Telegram ID", "Статус")
        self.tree_drivers_dispatcher = ttk.Treeview(self.dispatcher_content_frame, columns=columns, show="headings")
        for col in columns:
            self.tree_drivers_dispatcher.heading(col, text=col)
            self.tree_drivers_dispatcher.column(col, width=150)
        self.tree_drivers_dispatcher.pack(expand=True, fill="both", padx=10, pady=10)

        try:
            response = requests.get(f"{FLASK_API_BASE_URL}/drivers")
            response.raise_for_status()
            drivers = response.json()
            print(f"[DEBUG_APP_DRIVERS] Полученные данные водителей от API: {drivers}")
            for driver in drivers:
                self.tree_drivers_dispatcher.insert("", "end", values=(driver['id'], driver['fio'], driver['contact_info'], driver['telegram_id'], driver['status']))
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.")
        except requests.exceptions.HTTPError as e:
            error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
            messagebox.showerror("Ошибка", f"Ошибка получения водителей: {error_message}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")

    def update_order_status_dialog(self):
        update_window = tk.Toplevel(self)
        update_window.title("Обновить статус заказа")
        update_window.transient(self)
        update_window.grab_set()

        ttk.Label(update_window, text="ID заказа:").grid(row=0, column=0, padx=5, pady=5)
        order_id_entry = ttk.Entry(update_window)
        order_id_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(update_window, text="Новый статус:").grid(row=1, column=0, padx=5, pady=5)
        status_combobox = ttk.Combobox(update_window, values=["В ожидании", "В процессе", "Доставлен", "Отменен"], state="readonly")
        status_combobox.grid(row=1, column=1, padx=5, pady=5)
        status_combobox.set("В ожидании")

        def perform_update():
            order_id_str = order_id_entry.get()
            new_status_name = status_combobox.get()
            if order_id_str and new_status_name:
                try:
                    order_id = int(order_id_str)
                    response = requests.put(f"{FLASK_API_BASE_URL}/orders/update_status", json={
                        "order_id": order_id,
                        "new_status_name": new_status_name
                    })
                    print(f"[DEBUG_APP_UPDATE_STATUS] Отправленный запрос: {response}")
                    response.raise_for_status()
                    messagebox.showinfo("Успех", f"Статус заказа {order_id} успешно обновлен на \'{new_status_name}\'", parent=update_window)
                    update_window.destroy()
                    self.show_orders_dispatcher() # Обновить список заказов
                except ValueError:
                    messagebox.showerror("Ошибка", "ID заказа должен быть числом.", parent=update_window)
                except requests.exceptions.ConnectionError:
                    messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.", parent=update_window)
                except requests.exceptions.HTTPError as e:
                    error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
                    messagebox.showerror("Ошибка", f"Ошибка обновления статуса заказа: {error_message}", parent=update_window)
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}", parent=update_window)
            else:
                messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.", parent=update_window)

        ttk.Button(update_window, text="Обновить", command=perform_update).grid(row=2, column=0, columnspan=2, pady=10)

    def _bind_suggestions(self, entry_widget, entity_type):
        def _callback(event):
            self._update_suggestions(entry_widget, entity_type)
        return _callback

    def _update_suggestions(self, entry_widget, entity_type):
        query = entry_widget.get()
        if not query:
            if entity_type == 'client' and hasattr(self, 'client_suggestions'):
                self.client_suggestions.destroy()
            elif entity_type == 'driver' and hasattr(self, 'driver_suggestions'):
                self.driver_suggestions.destroy()
            return

        try:
            response = requests.get(f"{FLASK_API_BASE_URL}/{entity_type}s")
            response.raise_for_status()
            entities = response.json()
            suggestions = [entity['fio'] for entity in entities if query.lower() in entity['fio'].lower()]

            if entity_type == 'client':
                if hasattr(self, 'client_suggestions'):
                    self.client_suggestions.destroy()
                self.client_suggestions = tk.Listbox(entry_widget.master, height=min(len(suggestions), 5))
                self.client_suggestions.place(x=entry_widget.winfo_x(), y=entry_widget.winfo_y() + entry_widget.winfo_height(), relwidth=entry_widget.winfo_reqwidth() / entry_widget.winfo_width())
                for s in suggestions:
                    self.client_suggestions.insert(tk.END, s)
                self.client_suggestions.bind("<<ListboxSelect>>", lambda event: entry_widget.delete(0, tk.END) or entry_widget.insert(0, self.client_suggestions.get(self.client_suggestions.curselection())) or self.client_suggestions.destroy())
            elif entity_type == 'driver':
                if hasattr(self, 'driver_suggestions'):
                    self.driver_suggestions.destroy()
                self.driver_suggestions = tk.Listbox(entry_widget.master, height=min(len(suggestions), 5))
                self.driver_suggestions.place(x=entry_widget.winfo_x(), y=entry_widget.winfo_y() + entry_widget.winfo_height(), relwidth=entry_widget.winfo_reqwidth() / entry_widget.winfo_width())
                for s in suggestions:
                    self.driver_suggestions.insert(tk.END, s)
                self.driver_suggestions.bind("<<ListboxSelect>>", lambda event: entry_widget.delete(0, tk.END) or entry_widget.insert(0, self.driver_suggestions.get(self.driver_suggestions.curselection())) or self.driver_suggestions.destroy())
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.", parent=entry_widget.winfo_toplevel())
        except requests.exceptions.HTTPError as e:
            error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
            messagebox.showerror("Ошибка", f"Ошибка получения предложений: {error_message}", parent=entry_widget.winfo_toplevel())
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}", parent=entry_widget.winfo_toplevel())

    def create_order_dialog(self):
        create_window = tk.Toplevel(self)
        create_window.title("Создать новый заказ")
        create_window.transient(self)
        create_window.grab_set()

        form_frame = ttk.Frame(create_window, padding="10")
        form_frame.pack(fill="both", expand=True)

        labels = [
            "Дата создания:", "Статус:", "Адрес доставки:",
            "ФИО Клиента:", "ФИО Водителя:", "Продукт:", "Количество:",
            "Комментарий:", "Срок доставки:"
        ]
        entries = {}
        
        # Специальная обработка для полей даты с кнопками календаря
        current_row = 0

        ttk.Label(form_frame, text=labels[0]).grid(row=current_row, column=0, padx=5, pady=2, sticky="w")
        creation_date_entry = ttk.Entry(form_frame, width=30)
        creation_date_entry.grid(row=current_row, column=1, padx=5, pady=2, sticky="ew")
        creation_date_button = ttk.Button(form_frame, text="Выбрать дату", command=lambda: self._open_calendar(creation_date_entry))
        creation_date_button.grid(row=current_row, column=2, padx=5, pady=2)
        entries[labels[0]] = creation_date_entry
        current_row += 1

        # Остальные поля
        for i in range(1, len(labels)):
            text = labels[i]
            ttk.Label(form_frame, text=text).grid(row=current_row, column=0, padx=5, pady=2, sticky="w")
            if text == "Статус:":
                status_options = ["В ожидании", "В процессе", "Доставлен", "Отменен"]
                entry = ttk.Combobox(form_frame, values=status_options, state="readonly")
                entry.set("В ожидании")
            elif text == "ФИО Клиента:":
                entry = ttk.Entry(form_frame, width=30)
                entry.bind("<KeyRelease>", self._bind_suggestions(entry, 'client'))
                self.client_suggestions = tk.Listbox(form_frame, height=5)
            elif text == "ФИО Водителя:":
                entry = ttk.Entry(form_frame, width=30)
                entry.bind("<KeyRelease>", self._bind_suggestions(entry, 'driver'))
                self.driver_suggestions = tk.Listbox(form_frame, height=5)
            elif text == "Срок доставки:":
                delivery_deadline_entry = ttk.Entry(form_frame, width=30)
                delivery_deadline_entry.grid(row=current_row, column=1, padx=5, pady=2, sticky="ew")
                delivery_deadline_button = ttk.Button(form_frame, text="Выбрать дату", command=lambda: self._open_calendar(delivery_deadline_entry))
                delivery_deadline_button.grid(row=current_row, column=2, padx=5, pady=2)
                entry = delivery_deadline_entry
            else:
                entry = ttk.Entry(form_frame, width=30)
            
            if text != "Срок доставки:": # Если это не поле срока доставки, размещаем его здесь
                entry.grid(row=current_row, column=1, padx=5, pady=2, sticky="ew")
            entries[text] = entry
            current_row += 1

        def perform_create():
            # Получаем даты из полей ввода
            creation_date_str = entries["Дата создания:"].get()
            delivery_deadline_str = entries["Срок доставки:"].get()

            # Получаем текущее время
            current_time = datetime.now().strftime('%H:%M:%S')

            # Формируем полные даты со временем
            creation_date_full = f"{creation_date_str} {current_time}"
            delivery_deadline_full = f"{delivery_deadline_str} {current_time}"

            status_name = entries["Статус:"].get()
            delivery_address = entries["Адрес доставки:"].get()
            client_fio = entries["ФИО Клиента:"].get()
            driver_fio = entries["ФИО Водителя:"].get()
            product = entries["Продукт:"].get()
            quantity = entries["Количество:"].get()
            
            comment_entry = entries.get("Комментарий:")
            comment = comment_entry.get() if comment_entry else ""

            if not all([creation_date_str, delivery_deadline_str, status_name, delivery_address, client_fio, driver_fio, product, quantity]):
                messagebox.showerror("Ошибка", "Пожалуйста, заполните все обязательные поля.", parent=create_window)
                return

            try:
                status_id_response = requests.get(f"{FLASK_API_BASE_URL}/status_id/{status_name}")
                status_id_response.raise_for_status()
                status_id = status_id_response.json()["status_id"]

                client_id_response = requests.get(f"{FLASK_API_BASE_URL}/client_id/{client_fio}")
                client_id_response.raise_for_status()
                client_id = client_id_response.json()["client_id"]

                driver_id_response = requests.get(f"{FLASK_API_BASE_URL}/driver_id/{driver_fio}")
                driver_id_response.raise_for_status()
                driver_id = driver_id_response.json()["driver_id"]

                order_data = {
                    "creation_date": creation_date_full,
                    "status_id": status_id,
                    "delivery_address": delivery_address,
                    "client_id": client_id,
                    "driver_id": driver_id,
                    "product": product,
                    "quantity": int(quantity),
                    "comment": comment,
                    "delivery_deadline": delivery_deadline_full,
                    "dispatcher_id": self.current_user_id
                }
                print(f"[DEBUG_APP_CREATE_ORDER] order_data перед отправкой: {order_data}")

                response = requests.post(f"{FLASK_API_BASE_URL}/orders", json=order_data)
                response.raise_for_status()
                messagebox.showinfo("Успех", "Заказ успешно создан.", parent=create_window)
                create_window.destroy()
                self.show_orders_dispatcher()
            except ValueError:
                messagebox.showerror("Ошибка", "Количество должно быть числом.", parent=create_window)
            except requests.exceptions.ConnectionError:
                messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.", parent=create_window)
            except requests.exceptions.HTTPError as e:
                error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
                messagebox.showerror("Ошибка", f"Ошибка создания заказа: {error_message}", parent=create_window)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}", parent=create_window)

        ttk.Button(form_frame, text="Создать заказ", command=perform_create).grid(row=len(labels), column=0, columnspan=2, pady=10)

    def _open_calendar(self, entry_widget):
        def _set_date():
            selected_date = cal.selection_get()
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, selected_date.strftime('%Y-%m-%d'))
            top.destroy()

        top = tk.Toplevel(self)
        top.title("Выбрать дату")
        top.transient(self)
        top.grab_set()

        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(pady=10)

        ttk.Button(top, text="Выбрать", command=_set_date).pack(pady=5)

    def delete_order_dialog(self):
        delete_window = tk.Toplevel(self)
        delete_window.title("Удалить заказ")
        delete_window.transient(self)
        delete_window.grab_set()

        ttk.Label(delete_window, text="ID заказа:").grid(row=0, column=0, padx=5, pady=5)
        order_id_entry = ttk.Entry(delete_window)
        order_id_entry.grid(row=0, column=1, padx=5, pady=5)

        def perform_delete():
            order_id_str = order_id_entry.get()
            if order_id_str:
                try:
                    order_id = int(order_id_str)
                    if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить заказ с ID {order_id}?", parent=delete_window):
                        response = requests.delete(f"{FLASK_API_BASE_URL}/orders/{order_id}")
                        response.raise_for_status()
                        messagebox.showinfo("Успех", "Заказ успешно удален.", parent=delete_window)
                        delete_window.destroy()
                        self.show_orders_dispatcher() # Обновить список заказов
                except ValueError:
                    messagebox.showerror("Ошибка", "ID заказа должен быть числом.", parent=delete_window)
                except requests.exceptions.ConnectionError:
                    messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.", parent=delete_window)
                except requests.exceptions.HTTPError as e:
                    error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
                    messagebox.showerror("Ошибка", f"Ошибка удаления заказа: {error_message}", parent=delete_window)
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}", parent=delete_window)
            else:
                messagebox.showerror("Ошибка", "Пожалуйста, введите ID заказа для удаления.", parent=delete_window)

        ttk.Button(delete_window, text="Удалить", command=perform_delete).grid(row=1, column=0, columnspan=2, pady=10)

    def create_driver_report(self):
        self.clear_main_display()

        report_control_frame = ttk.Frame(self.dispatcher_content_frame, padding="10", style="LightBlue.TFrame")
        report_control_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(report_control_frame, text="Выберите водителя для отчета:", background="#ADD8E6").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.driver_selection_combobox = ttk.Combobox(report_control_frame, state="readonly", width=40)
        self.driver_selection_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(report_control_frame, text="Сгенерировать отчет", command=self._generate_driver_report_content).grid(row=0, column=2, padx=10, pady=5)

        # Загружаем водителей для выпадающего списка
        try:
            drivers_response = requests.get(f"{FLASK_API_BASE_URL}/drivers")
            drivers_response.raise_for_status()
            drivers_data = drivers_response.json()
            self.all_drivers = drivers_data # Сохраняем всех водителей для дальнейшего использования

            driver_names = [driver['fio'] for driver in drivers_data]
            self.driver_selection_combobox['values'] = ["Все водители"] + driver_names
            self.driver_selection_combobox.set("Все водители") # Устанавливаем значение по умолчанию

        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.", parent=report_control_frame)
        except requests.exceptions.HTTPError as e:
            error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
            messagebox.showerror("Ошибка", f"Ошибка получения списка водителей: {error_message}", parent=report_control_frame)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}", parent=report_control_frame)

        self.report_display_frame = ttk.Frame(self.dispatcher_content_frame, padding="10", style="LightBlue.TFrame")
        self.report_display_frame.pack(expand=True, fill="both", padx=10, pady=10)

    def _generate_driver_report_content(self):
        selected_driver_fio = self.driver_selection_combobox.get()

        try:
            drivers_to_report = []
            if selected_driver_fio == "Все водители":
                drivers_to_report = self.all_drivers
            else:
                # Находим выбранного водителя по ФИО
                for driver in self.all_drivers:
                    if driver['fio'] == selected_driver_fio:
                        drivers_to_report.append(driver)
                        break
                if not drivers_to_report:
                    messagebox.showerror("Ошибка", "Выбранный водитель не найден.")
                    return

            # Получаем данные обо всех заказах
            orders_response = requests.get(f"{FLASK_API_BASE_URL}/orders")
            orders_response.raise_for_status()
            all_orders = orders_response.json()

            report_frame = self.report_display_frame # Используем созданную рамку для отображения отчета
            for widget in report_frame.winfo_children(): # Очищаем старый отчет
                widget.destroy()

            if not drivers_to_report:
                ttk.Label(report_frame, text="Нет зарегистрированных водителей для отображения отчета.", background="#ADD8E6").pack(pady=10)
                return

            for driver in drivers_to_report:
                driver_name = driver['fio']
                driver_id = driver['id']
                # Фильтруем заказы по текущему водителю
                driver_orders = [order for order in all_orders if order['driver_id'] == driver_id]

                ttk.Label(report_frame, text=f"Отчет для водителя: {driver_name}", font=("Arial", 12, "bold"), background="#ADD8E6").pack(anchor="w", pady=(10, 0))

                if driver_orders:
                    columns = (
                        "ID", "Дата создания", "Статус", "Адрес доставки",
                        "Клиент", "Продукт", "Количество", "Комментарий", "Срок доставки"
                    )
                    tree = ttk.Treeview(report_frame, columns=columns, show="headings")
                    for col in columns:
                        tree.heading(col, text=col)
                        tree.column(col, width=100)
                    tree.pack(expand=True, fill="both", padx=5, pady=5)

                    for order in driver_orders:
                        tree.insert("", "end", values=(
                            order['id'],
                            order['creation_date'],
                            order['status_name'],
                            order['delivery_address'],
                            order['client_fio'],
                            order['product'],
                            order['quantity'],
                            order['comment'],
                            order['delivery_deadline']
                        ))
                else:
                    ttk.Label(report_frame, text="Нет заказов для этого водителя.", background="#ADD8E6").pack(anchor="w")
                ttk.Separator(report_frame, orient="horizontal").pack(fill="x", pady=10)

            # Добавляем кнопку для сохранения в Excel
            ttk.Button(report_frame, text="Сохранить отчет в Excel", command=lambda: self.export_driver_report_to_excel(drivers_to_report, all_orders)).pack(pady=10)

        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к Flask серверу. Убедитесь, что сервер запущен.")
        except requests.exceptions.HTTPError as e:
            error_message = e.response.json().get("error", "Неизвестная ошибка сервера")
            messagebox.showerror("Ошибка", f"Ошибка получения данных для отчета: {error_message}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")

    def export_driver_report_to_excel(self, drivers, all_orders):
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Сохранить отчет курьеров как"
            )
            if not filepath:
                return

            writer = pd.ExcelWriter(filepath, engine='openpyxl')

            for driver in drivers:
                driver_name = driver['fio']
                driver_id = driver['id']
                driver_orders = [order for order in all_orders if order['driver_id'] == driver_id]

                if driver_orders:
                    # Преобразуем список словарей в DataFrame
                    df = pd.DataFrame(driver_orders)
                    
                    # Выбираем и переименовываем столбцы для отчета
                    df_report = df[[
                        'id', 'creation_date', 'status_name', 'delivery_address',
                        'client_fio', 'product', 'quantity', 'comment', 'delivery_deadline'
                    ]].rename(columns={
                        'id': 'ID',
                        'creation_date': 'Дата создания',
                        'status_name': 'Статус',
                        'delivery_address': 'Адрес доставки',
                        'client_fio': 'Клиент',
                        'product': 'Продукт',
                        'quantity': 'Количество',
                        'comment': 'Комментарий',
                        'delivery_deadline': 'Срок доставки'
                    })
                    
                    # Записываем данные в лист Excel
                    sheet_name = f"Отчет_{driver_name[:25]}" # Обрезаем имя листа, если слишком длинное
                    df_report.to_excel(writer, sheet_name=sheet_name, index=False)
                else:
                    # Если нет заказов, создаем пустой лист или записываем сообщение
                    sheet_name = f"Отчет_{driver_name[:25]}"
                    pd.DataFrame([{"Сообщение": "Нет заказов для этого водителя."}]).to_excel(writer, sheet_name=sheet_name, index=False)

            writer._save()
            messagebox.showinfo("Успех", f"Отчет успешно сохранен в {filepath}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить отчет в Excel: {e}")

if __name__ == "__main__":
    app = CourierApp()
    app.mainloop() 