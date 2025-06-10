import telebot
import sqlite3
from database import db_operations

# Замените этот токен на свой реальный токен Telegram бота
TELEGRAM_BOT_TOKEN = "7846409638:AAHhGV3YdJk6PNUTUAjAaLVMwRdpRmqUm1c"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот транспортной службы. Чтобы обновить статус заказа, отправьте сообщение в формате: /update [ID_ЗАКАЗА] [НОВЫЙ_СТАТУС].\nДоступные статусы: В ожидании, В процессе, Доставлен, Отменен")

@bot.message_handler(commands=['update'])
def update_order_status_command(message):
    try:
        # Разделяем сообщение на части, максимум на 3: команда, ID, статус
        parts = message.text.split(' ', 2)
        
        if len(parts) != 3:
            bot.reply_to(message, "Неверный формат команды. Используйте: /update [ID_ЗАКАЗА] [НОВЫЙ_СТАТУС]")
            return
        
        order_id = int(parts[1])
        new_status_name = parts[2]

        valid_statuses = ["В ожидании", "В процессе", "Доставлен", "Отменен"]
        if new_status_name not in valid_statuses:
            bot.reply_to(message, f"Неверный статус. Доступные статусы: {', '.join(valid_statuses)}")
            return
        
        # Проверка существования заказа
        conn = sqlite3.connect(db_operations.DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT driver_id FROM orders WHERE id = ?", (order_id,))
        order_info = cursor.fetchone()
        conn.close()

        if not order_info:
            bot.reply_to(message, f"Заказ с ID {order_id} не найден.")
            return
        
        driver_id = order_info[0]

        db_operations.update_order_status(order_id, new_status_name)
        db_operations.update_driver_status(driver_id) # Обновить статус водителя после изменения статуса заказа
        bot.reply_to(message, f"Статус заказа {order_id} успешно обновлен на '{new_status_name}'.")

    except ValueError:
        bot.reply_to(message, "ID заказа должен быть числом.")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

def run_bot():
    print("Telegram бот запущен...")
    bot.polling()

if __name__ == '__main__':
    run_bot() 