from utils import init_socket_tcp, deserialization_message, serialization_message, deserialization_message_list, \
    install_param_in_socket_client, get_public_key, encrypted_message, generic_key_client, decrypted_message, \
    encrypted_message_for_send_user
import datetime, logging, json, threading
from metaclasses import ClientVerifier
from client_database.crud import ClientStorage
from PyQt5.QtCore import QObject, pyqtSignal
from Crypto.Cipher import PKCS1_OAEP

app_log_client = logging.getLogger('client')


def message_template(login='', password='', token='', action='', message='', to='', add_contact='',
                     statistic='', search_contact='', public_key='', crypto_symmetric_key=''):
    msg = {
        'action': action,
        'time': datetime.datetime.now().strftime('%d.%m.%Y'),
        'user': {
            'user_login': login,
            'user_password': password,
            'token': token
        },
        'mess_text': message,
        'to': to,
        'user_id': add_contact,
        'statistic': statistic,
        'search_contact': search_contact,
        'public_key': public_key,
        'crypto_symmetric_key': crypto_symmetric_key
    }
    return msg


class ClientSender(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, sock, account_name, token, database):
        self.database = database
        self.sock = sock
        self.account_name = account_name
        self.token = token
        self.msg = ''
        super().__init__()
        self._stop_event = threading.Event()
        self.private_key, self.public_key, self.symmetric = generic_key_client()

    def send_message(self, message):
        if message['request'] == '/quit':
            msg = message_template(action='quit', login=self.account_name, token=self.token)
            app_log_client.info('Сообщение создано')
            byte_msg = serialization_message(msg)
            self.sock.send(byte_msg)
            self.stop()
        # elif message['request'] == '/get_send_public_key':
        #     msg = message_template(action='get_send_public_key', public_key=self.public_key)
        elif message['request'] == '/get_target_contact':
            msg = message_template(action='get_target_contact', login=self.account_name, token=self.token,
                                   search_contact=message['args'])
            app_log_client.info('Сообщение создано')
            byte_msg = serialization_message(msg)
            self.sock.send(byte_msg)
        elif message['request'] == '/add_contact':
            msg = message_template(action='add_contact', add_contact=message['args'], login=self.account_name,
                                   token=self.token)
            app_log_client.info('Сообщение создано')
            byte_msg = serialization_message(msg)
            self.sock.send(byte_msg)
        elif message['request'] == '/message':
            msg = message_template(action='presence', message=message['message'], login=self.account_name,
                                   token=self.token, to=message['to'])
            app_log_client.info('Сообщение создано')
            byte_msg = serialization_message(msg)
            self.sock.send(byte_msg)
        elif message['request'] == '/get_statistics':
            msg = message_template(action='get_statistics', login=self.account_name, token=self.token,
                                   statistic=message['args'].text())
            app_log_client.info('Сообщение создано')
            byte_msg = serialization_message(msg)
            self.sock.send(byte_msg)
        elif message['request'] == '/get_messages_users':
            msg = message_template(action='get_messages_users', login=self.account_name, token=self.token)
            byte_msg = serialization_message(msg)
            app_log_client.info('Сообщение создано')
            self.sock.send(byte_msg)
        # elif message == '/del_contact':
        #     nickname = input('Никнейм пользователя, который хотите удалить из контактов >> ')
        #     msg = message_template(action='del_contact', add_contact=nickname, login=self.account_name, token=self.token)
        #     app_log_client.info('Сообщение создано')
        #     byte_msg = serialization_message(msg)
        #     app_log_client.info('Сообщение сериализовано')
        #     self.sock.send(byte_msg)
        # elif message == '/get_users':
        #     msg = message_template(action='get_users', login=self.account_name, token=self.token)
        #     app_log_client.info('Сообщение создано')
        #     byte_msg = serialization_message(msg)
        #     app_log_client.info('Сообщение сериализовано')
        #     self.sock.send(byte_msg)

    def run(self):
        while not self._stop_event.is_set():
            self._stop_event.wait(1)

    def stop(self):
        self._stop_event.set()


class ClientRecipient(QObject, threading.Thread):
    message_received = pyqtSignal(str)
    create_users_signal = pyqtSignal(str)
    register_signal = pyqtSignal(str)
    message_user_received = pyqtSignal(str)
    search_contact_signal = pyqtSignal(list)

    def __init__(self, sock, account_name, database):
        self.database = database
        self.sock = sock
        self.account_name = account_name
        super().__init__()
        self._stop_event = threading.Event()

    def get_message(self):
        data = self.sock.recv(4096)
        list_message = deserialization_message_list(data)
        for i in list_message:
            app_log_client.info('Ответ получен. %s %s', i['response'], i['alert'])
            if i['response'] == 200 and i['alert'] == 'Пользователь вышел':
                app_log_client.info(f'Пользователь {self.account_name} вышел')
                self.message_received.emit('quit')
                self.stop()
            elif 'user_name' in i and i['user_name'] != self.account_name:
                self.database.add_message(i['user_name'], i['from'], i['alert'], i['hash_message'])
                self.message_user_received.emit(i['user_name'])
            elif i['response'] == 200 and i['alert'] == 'Сообщение доставлено':
                self.database.add_message(i['user_name'], i['to'], i['message'], i['hash_message'])
                self.message_user_received.emit(i['to'])
            elif i['response'] == 200 and i['alert'] == 'Пользователь добавлен в контакты':
                self.database.add_contact(i['to_user'])
                print(i['alert'])
            elif i['response'] == 200 and i['alert'] == 'Статистика отправлена':
                print(str(i['user_history']))
                result = json.dumps(i['user_history'])
                self.create_users_signal.emit(result)
            elif i['response'] == 200 and i['alert'] == 'Успешная регистрация':
                print(i['alert'])
                self.register_signal.emit('Ok')
            elif i['response'] == 202 and i['alert'] == 'Сообщения отправлены':
                app_log_client.info('Ответ получен. %s %s', i['response'], i['message'])
                self.database.add_messages(i['message'])
            elif i['response'] == 202 and i['action'] == 'get_target_contact':
                self.search_contact_signal.emit(i['alert'])
            # elif i['response'] == 400 and i['alert'] == 'Для добавления пользователь должен быть в базе':
            #     print(i['alert'])
            # elif i['response'] == 400 and i['alert'] == 'Для удаления пользователь должен быть в базе':
            #     print(i['alert'])
            # elif i['response'] == 200 and i['alert'] == 'Пользователь удален из контактов':
            #     self.database.del_contact(i['to_user'])
            #     print(i['alert'])

    def run(self):
        while not self._stop_event.is_set():
            self.get_message()

    def stop(self):
        self._stop_event.set()


def connect_server():
    addr, port = install_param_in_socket_client()

    # инициализируем сокет
    server = init_socket_tcp()
    app_log_client.info('Сокет инициализирован')

    # подключаемся к серверу
    app_log_client.info('Подключение к серверу...')
    server.connect((addr, port))
    return server


def authorization(server, login, password):
    addr, port = server.getsockname()
    result_data = {
        'name_account': '',
        'password': '',
        'token': ''
    }
    try:
        # сгенерировал приватный и публичный ключ клиента
        PRIVAT_KEY_CLIENT, PUBLIC_KEY_CLIENT, SYMMETRIC_KEY = generic_key_client()
        # создаем сообщение для получения публичного ключа сервера
        mes = message_template(action='get_public_key', public_key=PUBLIC_KEY_CLIENT.decode())
        # отправляем запрос на получение публичного ключа сервера и отправляем ему публичный ключ клиента
        PUBLIC_KEY_SERVER = get_public_key(server, mes)

        result_data['name_account'] = login
        result_data['password'] = password

        # создаем сообщение на авторизацию
        msg = message_template(action='authorization', login=result_data['name_account'],
                               password=result_data['password'], public_key=PUBLIC_KEY_CLIENT.decode())
        # приводим json обьект к строке и переводим строку в байты
        encode_msg = serialization_message(msg)
        # шифруем сообщение с помощью публичного ключа сервера
        encrypted_mes = encrypted_message(encode_msg, PUBLIC_KEY_SERVER, SYMMETRIC_KEY)
        # отправляем сообщение серверу на авторизацию
        server.send(encrypted_mes)

        # получаем сообщение сервера
        data_res = b''
        while True:
            data = server.recv(4096)
            if not data:
                break
            data_res = data_res + data
            if len(data) < 4096:
                break
        if data_res[:10] == b'ENCRYPTED:':
            decrypt_data = decrypted_message(data_res[10:], PRIVAT_KEY_CLIENT)
            message = deserialization_message(decrypt_data)
        else:
            message = deserialization_message(data_res)
        if message['response'] == 409 and message['role'] == 'Нет доступа':
            result_data['role'] = 'Нет доступа'
            print('Этот пользователь уже в системе.')
            app_log_client.info(f'Соединение с сервером не установлено. Ответ сервера: {message["response"]}')
            return result_data
        elif message['response'] == 401 and message['role'] == 'Неверный логин или пароль':
            result_data['role'] = 'Неверный логин или пароль'
            print('Неправильный логин или пароль. Попробуйте еще раз.')
            app_log_client.info(f'Соединение с сервером не установлено. Ответ сервера: {message["response"]}')
            return result_data
        elif 'role' in message and message['role'] == 'Администратор' and message['response'] == 200:
            app_log_client.info(f'Установлено соединение с сервером. Ответ сервера: {message["response"]}')
            result_data['token'] = message['token']
            result_data['role'] = message['role']
            result_data['users'] = message['users']
            print('Установлено соединение с сервером.')
            app_log_client.info(f'Запущен клиент с параметрами: адрес сервера: {addr}, порт: {port}, '
                                f'имя пользователя: {result_data["name_account"]}')
            return result_data
        elif 'role' in message and message['role'] == 'Пользователь' and message['response'] == 200:
            app_log_client.info(f'Установлено соединение с сервером. Ответ сервера: {message["response"]}')
            result_data['token'] = message['token']
            result_data['role'] = message['role']
            print('Установлено соединение с сервером.')
            app_log_client.info(f'Запущен клиент с параметрами: адрес сервера: {addr}, порт: {port}, '
                                f'имя пользователя: {result_data["name_account"]}')
            return result_data
    except json.JSONDecodeError:
        app_log_client.error('Не удалось декодировать полученную Json строку.')
        exit(1)
    except Exception as er:
        app_log_client.error('Не удалось подключиться к серверу')
        exit(1)


def registration(server, login, password):
    # addr, port = server.getsockname()
    msg = message_template(action='registration', login=login, password=password)
    msg_json = serialization_message(msg)
    server.send(msg_json)

    # получаем сообщение сервера
    data = server.recv(4096)

    message = deserialization_message(data)

    if message['response'] == 200:
        app_log_client.info(f'Установлено соединение с сервером. Ответ сервера: {message["response"]}')
        server.close()
        return 'Ok'

    server.close()
    return 'Error'


def init_database(data, server):
    database = ClientStorage(data['name_account'])

    msg = message_template(action='get_contacts', login=data['name_account'], token=data['token'])

    # сериализуем сообщение для отправки и отправляем
    byte_msg = serialization_message(msg)
    app_log_client.info('Сообщение создано')
    server.send(byte_msg)

    # получаем сообщение от сервера и добавляем контакты в б.д.
    server_data_res = b''
    while True:
        server_data = server.recv(4096)
        if not server_data:
            break
        server_data_res = server_data_res + server_data
        if len(server_data) < 4096:
            break
    list_message = deserialization_message_list(server_data_res)
    for i in list_message:
        app_log_client.info('Ответ получен. %s %s', i['response'], i['alert'])
        if i['response'] == 202:
            database.add_contacts(i['alert'])

    # создаем сообщение запроса
    msg = message_template(action='get_messages_users', login=data['name_account'], token=data['token'])

    # сериализуем сообщение для отправки и отправляем
    byte_msg = serialization_message(msg)
    app_log_client.info('Сообщение создано')
    server.send(byte_msg)

    # получаем сообщение от сервера и добавляем сообщения пользователя в б.д.
    server_data_res = b''
    while True:
        server_data = server.recv(4096)
        if not server_data:
            break
        server_data_res = server_data_res + server_data
        if len(server_data) < 4096:
            break
    list_message = deserialization_message_list(server_data_res)
    for i in list_message:
        app_log_client.info('Ответ получен. %s %s', i['response'], i['message'])
        if i['response'] == 202:
            database.add_messages(i['message'])

    return database


def check_database(data, server, database):
    msg = message_template(action='get_messages_users', login=data['name_account'], token=data['token'])

    # сериализуем сообщение для отправки и отправляем
    byte_msg = serialization_message(msg)
    app_log_client.info('Сообщение создано')
    server.send(byte_msg)

    # получаем сообщение от сервера и добавляем сообщения пользователя в б.д.
    server_data = server.recv(4096)
    list_message = deserialization_message_list(server_data)
    for i in list_message:
        app_log_client.info('Ответ получен. %s %s', i['response'], i['alert'])
        if i['response'] == 202:
            database.add_messages(i['alert'])


def start_thread_client_send(data, server, database):
    client_sender = ClientSender(server, data['name_account'], data['token'], database)
    client_sender.daemon = True
    client_sender.start()
    app_log_client.debug('Запущен процесс')
    return client_sender


def start_thread_client_recipient(data, server, database):
    client_recipient = ClientRecipient(server, data['name_account'], database)
    client_recipient.daemon = True
    client_recipient.start()
    app_log_client.debug('Запущен процесс')
    return client_recipient
