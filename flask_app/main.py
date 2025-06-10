from flask import Flask, request, jsonify
import sqlite3
from database import db_operations

def create_app():
    app = Flask(__name__)

    @app.route('/', endpoint='home_endpoint')
    def home():
        return "Flask сервер для транспортного приложения запущен."

    @app.route('/update_order_status', methods=['POST'], endpoint='update_order_status_endpoint')
    def update_order_status_api():
        data = request.get_json()
        order_id = data.get('order_id')
        new_status_name = data.get('new_status_name')

        if not order_id or not new_status_name:
            return jsonify({"error": "Отсутствуют order_id или new_status_name"}), 400

        try:
            db_operations.update_order_status(order_id, new_status_name)
            return jsonify({'message': 'Статус заказа успешно обновлен'}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # API для управления клиентами
    @app.route('/clients', methods=['GET'], endpoint='get_clients_endpoint')
    def get_clients_api():
        try:
            clients = db_operations.get_all_clients()
            # Преобразуем sqlite3.Row в обычные словари
            return jsonify([dict(client) for client in clients]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/clients', methods=['POST'], endpoint='add_client_endpoint')
    def add_client_api():
        data = request.get_json()
        fio = data.get('fio')
        contact_info = data.get('contact_info')
        address = data.get('address')

        if not all([fio, contact_info, address]):
            return jsonify({'error': 'Отсутствуют данные клиента'}), 400

        try:
            db_operations.add_client(fio, contact_info, address)
            return jsonify({'message': 'Клиент успешно добавлен'}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/clients/<int:client_id>', methods=['PUT'], endpoint='update_client_endpoint')
    def update_client_api(client_id):
        data = request.get_json()
        fio = data.get('fio')
        contact_info = data.get('contact_info')
        address = data.get('address')

        if not all([fio, contact_info, address]):
            return jsonify({'error': 'Отсутствуют данные клиента'}), 400

        try:
            db_operations.update_client(client_id, fio, contact_info, address)
            return jsonify({'message': 'Клиент успешно обновлен'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/clients/<int:client_id>', methods=['DELETE'], endpoint='delete_client_endpoint')
    def delete_client_api(client_id):
        try:
            db_operations.delete_client(client_id)
            return jsonify({'message': 'Клиент успешно удален'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # API для управления водителями
    @app.route('/drivers', methods=['GET'], endpoint='get_drivers_endpoint')
    def get_drivers_api():
        try:
            drivers = db_operations.get_all_drivers()
            # Преобразуем sqlite3.Row в обычные словари
            return jsonify([dict(driver) for driver in drivers]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/drivers', methods=['POST'], endpoint='add_driver_endpoint')
    def add_driver_api():
        data = request.get_json()
        fio = data.get('fio')
        contact_info = data.get('contact_info')
        telegram_id = data.get('telegram_id')

        if not all([fio, contact_info, telegram_id]):
            return jsonify({'error': 'Отсутствуют данные водителя'}), 400

        try:
            db_operations.add_driver(fio, contact_info, telegram_id)
            return jsonify({'message': 'Водитель успешно добавлен'}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/drivers/<int:driver_id>', methods=['PUT'], endpoint='update_driver_endpoint')
    def update_driver_api(driver_id):
        data = request.get_json()
        fio = data.get('fio')
        contact_info = data.get('contact_info')
        telegram_id = data.get('telegram_id')

        if not all([fio, contact_info, telegram_id]):
            return jsonify({'error': 'Отсутствуют данные водителя'}), 400

        try:
            db_operations.update_driver(driver_id, fio, contact_info, telegram_id)
            return jsonify({'message': 'Водитель успешно обновлен'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/drivers/<int:driver_id>', methods=['DELETE'], endpoint='delete_driver_endpoint')
    def delete_driver_api(driver_id):
        try:
            db_operations.delete_driver(driver_id)
            return jsonify({'message': 'Водитель успешно удален'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/drivers/update_status/<int:driver_id>', methods=['PUT'], endpoint='update_driver_status_endpoint')
    def update_driver_status_api(driver_id):
        try:
            db_operations.update_driver_status(driver_id)
            return jsonify({'message': 'Статус водителя успешно обновлен'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # API для управления диспетчерами
    @app.route('/dispatchers', methods=['GET'], endpoint='get_dispatchers_endpoint')
    def get_dispatchers_api():
        try:
            dispatchers = db_operations.get_all_dispatchers()
            # Преобразуем sqlite3.Row в обычные словари
            return jsonify([dict(dispatcher) for dispatcher in dispatchers]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/dispatchers', methods=['POST'], endpoint='add_dispatcher_endpoint')
    def add_dispatcher_api():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not all([username, password]):
            return jsonify({'error': 'Отсутствуют данные диспетчера'}), 400

        try:
            db_operations.add_dispatcher(username, password)
            return jsonify({'message': 'Диспетчер успешно добавлен'}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/dispatchers/<int:user_id>', methods=['PUT'], endpoint='update_dispatcher_endpoint')
    def update_dispatcher_api(user_id):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password') # Необязательно

        if not username:
            return jsonify({'error': 'Отсутствует имя пользователя'}), 400

        try:
            db_operations.update_dispatcher(user_id, username, password)
            return jsonify({'message': 'Диспетчер успешно обновлен'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/dispatchers/<int:user_id>', methods=['DELETE'], endpoint='delete_dispatcher_endpoint')
    def delete_dispatcher_api(user_id):
        try:
            db_operations.delete_dispatcher(user_id)
            return jsonify({'message': 'Диспетчер успешно удален'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # API для управления заказами
    @app.route('/orders', methods=['GET'], endpoint='get_all_orders_endpoint')
    def get_all_orders_api():
        try:
            orders = db_operations.get_all_orders()
            # Преобразуем sqlite3.Row в обычные словари
            return jsonify([dict(order) for order in orders]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/orders/delivered', methods=['GET'], endpoint='get_delivered_orders_endpoint')
    def get_delivered_orders_api():
        try:
            orders = db_operations.get_delivered_orders()
            # Преобразуем sqlite3.Row в обычные словари
            return jsonify([dict(order) for order in orders]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/orders/pending', methods=['GET'], endpoint='get_pending_orders_endpoint')
    def get_pending_orders_api():
        try:
            orders = db_operations.get_pending_orders()
            # db_operations.get_pending_orders() уже возвращает список словарей
            return jsonify(orders), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/orders/in_progress', methods=['GET'], endpoint='get_in_progress_orders_endpoint')
    def get_in_progress_orders_api():
        try:
            orders = db_operations.get_in_progress_orders()
            # db_operations.get_in_progress_orders() уже возвращает список словарей
            return jsonify(orders), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/orders', methods=['POST'], endpoint='create_order_endpoint')
    def create_order_api():
        data = request.get_json()
        creation_date = data.get('creation_date')
        status_id = data.get('status_id')
        delivery_address = data.get('delivery_address')
        client_id = data.get('client_id')
        driver_id = data.get('driver_id')
        product = data.get('product')
        quantity = data.get('quantity')
        comment = data.get('comment')
        delivery_deadline = data.get('delivery_deadline')
        dispatcher_id = data.get('dispatcher_id')

        if not all([creation_date, status_id, delivery_address, client_id, driver_id, product, quantity, delivery_deadline, dispatcher_id]):
            return jsonify({'error': 'Отсутствуют данные заказа'}), 400

        try:
            db_operations.create_order(creation_date, status_id, delivery_address, client_id, driver_id, product, quantity, comment, delivery_deadline, dispatcher_id)
            return jsonify({'message': 'Заказ успешно создан'}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/orders/<int:order_id>', methods=['DELETE'], endpoint='delete_order_endpoint')
    def delete_order_api(order_id):
        try:
            db_operations.delete_order(order_id)
            return jsonify({'message': 'Заказ успешно удален'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # API для вспомогательных функций
    @app.route('/status_id/<string:status_name>', methods=['GET'], endpoint='get_status_id_endpoint')
    def get_status_id_api(status_name):
        print(f"[DEBUG_FLASK_API] Получено запрос на status_id для: {status_name}")
        try:
            status_id_row = db_operations.get_status_id(status_name)
            if status_id_row is not None:
                print(f"[DEBUG_FLASK_API] status_id_row из DB: {status_id_row}")
                return jsonify({'status_id': status_id_row}), 200
            else:
                return jsonify({'error': 'Статус не найден'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/client_id/<string:fio>', methods=['GET'], endpoint='get_client_id_endpoint')
    def get_client_id_api(fio):
        try:
            client_id_row = db_operations.get_client_id_by_fio(fio)
            if client_id_row is not None:
                return jsonify({'client_id': client_id_row}), 200
            else:
                return jsonify({'error': 'Клиент не найден'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/driver_id/<string:fio>', methods=['GET'], endpoint='get_driver_id_endpoint')
    def get_driver_id_api(fio):
        try:
            driver_id_row = db_operations.get_driver_id_by_fio(fio)
            if driver_id_row is not None:
                return jsonify({'driver_id': driver_id_row}), 200
            else:
                return jsonify({'error': 'Водитель не найден'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/authenticate', methods=['POST'], endpoint='authenticate_endpoint')
    def authenticate_user_api():
        data = request.get_json()
        username = data.get('username')
        password_hash = data.get('password_hash')

        if not username or not password_hash:
            return jsonify({'error': 'Требуется имя пользователя и хэш пароля'}), 400

        print(f"[DEBUG_FLASK_API] Получено: username={username}, password_hash={password_hash}")
        try:
            user = db_operations.get_user_id_and_role(username, password_hash)
            if user:
                user_dict = dict(user)
                print(f"[DEBUG_FLASK_API] user_dict перед jsonify: {user_dict}")
                return jsonify({'user_id': user_dict['id'], 'role': user_dict['role_name']}), 200
            else:
                return jsonify({'error': 'Неверные учетные данные'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return app 