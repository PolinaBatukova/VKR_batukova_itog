import threading
from flask_app.main import create_app
from telegram_bot.bot import run_bot

def run_flask_app():
    app = create_app()
    app.run(debug=True, use_reloader=False) # use_reloader=False для предотвращения двойного запуска в режиме отладки

if __name__ == '__main__':
    # Запуск Flask-приложения в отдельном потоке
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True # Поток завершится, когда завершится основная программа
    flask_thread.start()

    # Запуск Telegram-бота в основном потоке
    run_bot() 