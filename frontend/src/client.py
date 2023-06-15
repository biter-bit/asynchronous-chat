import os.path
import sys

from utils_client import init_socket_tcp
from utils_client import deserialization_message
from utils_client import serialization_message
from utils_client import deserialization_message_list
from utils_client import install_param_in_socket_client
from utils_client import get_public_key
from utils_client import encrypted_message
from utils_client import generic_public_and_privat_key_client
from utils_client import generic_symmetric_key_client
from utils_client import decrypted_message
import datetime, logging, json, threading, random
from threading import Thread
from metaclasses import ClientVerifier
from client_database.crud import ClientStorage
from PyQt5.QtCore import QObject, pyqtSignal
from variables_client import ROOT_DIR
from log.log_client import client_log_config

app_log_client = logging.getLogger('client')


def message_template(login='', password='', token='', action='', message='', to='', add_contact='',
                     statistic='', search_contact='', public_key='', crypto_symmetric_key='', hash_mes=''):
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
        'crypto_symmetric_key': crypto_symmetric_key,
        'hash_mes': hash_mes
    }
    return msg


class ClientSender(Thread, metaclass=ClientVerifier):
    def __init__(self, sock, account_name, token, database):
        super().__init__()
        self.database = database
        self.sock = sock
        self.account_name = account_name
        self.token = token
        self.msg = ''
        self._stop_event = threading.Event()
        self.public_key_user = ''
        self.symmetric_key_mes = ''

    def send_message(self, message):
        if message['request'] == '/quit':
            msg = message_template(action='quit', login=self.account_name, token=self.token)
            app_log_client.info('Сообщение создано')
            byte_msg = serialization_message(msg)
            self.sock.send(byte_msg)
            self.stop()
        elif message['request'] == '/get_public_key':
            public_key_user = self.database.get_public_key_user(message['contact'])
            if not public_key_user:
                msg = message_template(action='get_public_key_user', to=message['contact'])
                msg_json = serialization_message(msg)
                self.sock.send(msg_json)
        elif message['request'] == '/get_symmetric_key':
            self.get_symmetric_key(message)
        elif message['request'] == '/get_target_contact':
            msg = message_template(action='get_target_contact', login=self.account_name, token=self.token,
                                   search_contact=message['args'])
            app_log_client.info('Сообщение создано')
            byte_msg = serialization_message(msg)
            self.sock.send(byte_msg)
        elif message['request'] == '/add_contact':
            public_key_server = self.database.get_public_key_server_or_user('server')
            symmetric_key = generic_symmetric_key_client()
            # !!!!!!!!!!!!!!!!!!!
            with open(f'{ROOT_DIR}/secret/key_user_{self.account_name}.json', 'r', encoding='utf-8') as file:
                read_file = file.read()
                privat_key_dict = json.loads(read_file)
                public_key_user = privat_key_dict['public_key']
            msg = message_template(action='add_contact', add_contact=message['args'], login=self.account_name,
                                   token=self.token, public_key=public_key_user)
            app_log_client.info('Сообщение создано')
            byte_msg = serialization_message(msg)
            encrypted_mes = encrypted_message(byte_msg, public_key_server, symmetric_key)
            self.sock.send(encrypted_mes)
        elif message['request'] == '/message':
            self.send_message_user(message)
        elif message['request'] == '/get_statistics':
            msg = message_template(action='get_statistics', login=self.account_name, token=self.token,
                                   statistic=message['args'].text())
            app_log_client.info('Сообщение создано')
            byte_msg = serialization_message(msg)
            self.sock.send(byte_msg)
        elif message['request'] == '/get_messages_users':
            msg = message_template(action='get_messages_users', login=self.account_name, to=message['login'],
                                   token=self.token)
            byte_msg = serialization_message(msg)
            app_log_client.info('Сообщение создано')
            self.sock.send(byte_msg)
        # elif message['request'] == '/get_send_public_key':
        #     msg = message_template(action='get_send_public_key', public_key=self.public_key)
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

    def get_symmetric_key(self, message):
        # получаем публичный ключ сервера и генерируем симметричный ключ для шифрования сообщения
        public_key_server = self.database.get_public_key_server_or_user('server')
        symmetric_key_for_message_by_server = generic_symmetric_key_client()

        # отправляем запрос на проверку симметричного ключа
        mes = message_template(action='symmetric_exchange', to=message['contact'], login=self.account_name,
                               message='check_sym_key')
        encode_mes_server = serialization_message(mes)
        encrypted_mes = encrypted_message(encode_mes_server, public_key_server,
                                          symmetric_key_for_message_by_server)

        # отправляем сообщение
        self.sock.send(encrypted_mes)
        return 'Ok'

    def send_message_user(self, message):
        # берем публичный ключ пользователя, которому хотим написать
        self.public_key_user = self.database.get_public_key_user(message['to'])

        # создаем симметричный ключ
        self.symmetric_key_mes = self.database.get_symmetric_key_for_communicate_between_users(message['to'])

        # создаем хеш для сообщения
        hash_message = str(random.getrandbits(128))

        # создаем сообщение и шифруем его публичным ключом пользователя
        msg_user = message_template(message=message['message'])
        encode_msg_user = serialization_message(msg_user)
        encrypted_mes_user = encrypted_message(encode_msg_user, self.public_key_user, self.symmetric_key_mes,
                                               encrypted=0)

        # создаем сообщение и шифруем его публичным ключом сервера
        public_key_server = self.database.get_public_key_server_or_user('server')
        msg_server = message_template(action='presence', message=json.loads(encrypted_mes_user.decode()),
                                      login=self.account_name, token=self.token, to=message['to'],
                                      hash_mes=hash_message)
        encode_msg_server = serialization_message(msg_server)
        encrypted_mes_server = encrypted_message(encode_msg_server, public_key_server, self.symmetric_key_mes)
        app_log_client.info('Сообщение создано')

        # добавляем сообщение в базу данных в незашифрованном виде
        self.database.add_message(self.account_name, message['to'], message['message'], hash_message)

        # отправляем сообщение
        self.sock.send(encrypted_mes_server)
        return 'Ok'

class ClientRecipient(QObject, Thread):
    message_received = pyqtSignal(str)
    create_users_signal = pyqtSignal(str)
    register_signal = pyqtSignal(str)
    message_user_received = pyqtSignal(str)
    search_contact_signal = pyqtSignal(list)

    def __init__(self, sock, account_name, database):
        super().__init__()
        self.database = database
        self.sock = sock
        self.account_name = account_name
        self._stop_event = threading.Event()

    def get_message(self):
        global encrypted_mes_symmetric_key
        with open(f'{ROOT_DIR}/secret/key_user_{self.account_name}.json', 'r', encoding='utf-8') as file:
            read_file = file.read()
            privat_key_dict = json.loads(read_file)
            PRIVAT_KEY_CLIENT = privat_key_dict['privat_key']
        data_res = b''
        while True:
            data = self.sock.recv(4096)
            if not data:
                break
            data_res = data_res + data
            if len(data) < 4096:
                break
        if data_res[:10] == b'ENCRYPTED:':
            decrypt_data, sym_key_one = decrypted_message(data_res[10:], PRIVAT_KEY_CLIENT)
            list_message = deserialization_message_list(decrypt_data)
        else:
            list_message = deserialization_message_list(data_res)
        for i in list_message:
            app_log_client.info('Ответ получен. %s %s', i['response'], i['alert'])
            if i['response'] == 200 and i['alert'] == 'Пользователь вышел':
                app_log_client.info(f'Пользователь {self.account_name} вышел')
                self.message_received.emit('quit')
                self.stop()
            elif 'user_name' in i and i['user_name'] != self.account_name:
                # получение сообщения от пользователя
                decrypt_data, sym_key = decrypted_message(i['alert'], PRIVAT_KEY_CLIENT, 0)
                message = deserialization_message(decrypt_data)
                self.database.add_message(i['user_name'], i['to'], message['mess_text'], i['hash_mes'])
                self.message_user_received.emit(i['user_name'])
            elif i['response'] == 200 and i['alert'] == 'Симметричный ключ получен':
                public_key_server = self.database.get_public_key_server_or_user('server')
                public_key_user = self.database.get_public_key_user(i['to'])
                symmetric_key_for_encrypted_symmetric_key = generic_symmetric_key_client()
                if i['action'] == 'old':
                    # расшифровываем ключ
                    decrypt_symmetric_key, sym_key_mes = decrypted_message(i['symmetric_key'], PRIVAT_KEY_CLIENT, 0)
                    # обновляем симметричный ключ в базе данных
                    self.database.update_contact_add_symmetric_key(i['to'], decrypt_symmetric_key)
                    # шифруем наш симметричный ключ
                    encrypted_mes_symmetric_key = encrypted_message(decrypt_symmetric_key,
                                                                    public_key_user,
                                                                    symmetric_key_for_encrypted_symmetric_key, 0)
                elif i['action'] == 'new':
                    symmetric_key_exchanging_messages_between_users = generic_symmetric_key_client()

                    # добавляем новый симметричный ключ в бд пользователя
                    self.database.update_contact_add_symmetric_key(i['to'],
                                                                   symmetric_key_exchanging_messages_between_users)

                    # шифруем наш симметричный ключ
                    encrypted_mes_symmetric_key = encrypted_message(symmetric_key_exchanging_messages_between_users,
                                                                    public_key_user,
                                                                    symmetric_key_for_encrypted_symmetric_key, 0)

                symmetric_key_for_message_by_server = generic_symmetric_key_client()
                # создаем сообщение, шифруем его и отправляем
                mes = message_template(action='symmetric_exchange', to=i['to'], login=self.account_name,
                                       crypto_symmetric_key=json.loads(encrypted_mes_symmetric_key.decode()),
                                       message='update')

                encode_mes_server = serialization_message(mes)
                encrypted_mes = encrypted_message(encode_mes_server, public_key_server,
                                                  symmetric_key_for_message_by_server)
                self.sock.send(encrypted_mes)

                print(i['alert'])
            elif i['response'] == 200 and i['alert'] == 'Сообщение доставлено':
                # ответ от сервера, что сообщение доставлено пользователю
                self.message_user_received.emit(i['to'])
            elif i['response'] == 200 and i['alert'] == 'Пользователь добавлен в контакты':
                public_key_user = i['public_key_recipient'].replace('\\n', '\n')
                self.database.add_contact(i['to_user'], public_key_user)
                print(i['alert'])
                # получаем публичный ключ сервера и генерируем симметричный ключ для шифрования сообщения
                public_key_server = self.database.get_public_key_server_or_user('server')
                symmetric_key_for_message_by_server = generic_symmetric_key_client()

                # отправляем запрос на проверку симметричного ключа
                mes = message_template(action='symmetric_exchange', to=i['to_user'], login=self.account_name,
                                       message='check_sym_key')
                encode_mes_server = serialization_message(mes)
                encrypted_mes = encrypted_message(encode_mes_server, public_key_server,
                                                  symmetric_key_for_message_by_server)

                # отправляем сообщение
                self.sock.send(encrypted_mes)
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
                self.message_user_received.emit(i['to'])
            elif i['response'] == 202 and i['action'] == 'get_target_contact':
                self.search_contact_signal.emit(i['alert'])
            elif i['response'] == 200 and i['alert'] == 'Публичный ключ пользователя отправлен':
                self.database.update_contact_add_public_key(i['to'], i['public_key'])
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


def authorization(login, password, server):
    """
    Фукнция авторизирует пользователя на сервере. Создается приватный и публичный ключ пользователя. Приватный ключ
    сохраняется в файл. Публичный сохраняется в базу данных клиента. Также функция отправляет запрос на получение
    публичного ключа сервера и сохраняет его в базу данных.
    :param login:
    :param password:
    :param server:
    :return:
    """
    addr, port = server.getsockname()
    result_data = {
        'name_account': '',
        'password': '',
        'token': ''
    }
    try:
        try:
            with open(f'{ROOT_DIR}/secret/key_user_{login}.json', 'r', encoding='utf-8') as file:
                read_file = file.read()
                privat_key_dict = json.loads(read_file)
                PRIVAT_KEY_CLIENT = privat_key_dict['privat_key']
                PUBLIC_KEY_CLIENT = privat_key_dict['public_key']
                SYMMETRIC_KEY = generic_symmetric_key_client()
        except Exception:
            PRIVAT_KEY_CLIENT = ''
            PUBLIC_KEY_CLIENT = ''
            SYMMETRIC_KEY = generic_symmetric_key_client()
        # сохранить приватный ключ клиента в отдельный файл
        result_data['name_account'] = login
        result_data['password'] = password

        # создаем сообщение для получения публичного ключа сервера
        mes = message_template(action='get_public_key', public_key=PUBLIC_KEY_CLIENT)
        # отправляем запрос на получение публичного ключа сервера и отправляем ему публичный ключ клиента
        PUBLIC_KEY_SERVER = get_public_key(server, mes)

        # создаем сообщение на авторизацию
        msg = message_template(action='authorization', login=result_data['name_account'],
                               password=result_data['password'], public_key=PUBLIC_KEY_CLIENT)
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
            decrypt_data, sym_key = decrypted_message(data_res[10:], PRIVAT_KEY_CLIENT)
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
            result_data['public_key_server'] = PUBLIC_KEY_SERVER
            result_data['public_key_user'] = PUBLIC_KEY_CLIENT
            print('Установлено соединение с сервером.')
            app_log_client.info(f'Запущен клиент с параметрами: адрес сервера: {addr}, порт: {port}, '
                                f'имя пользователя: {result_data["name_account"]}')
            return result_data
        elif 'role' in message and message['role'] == 'Пользователь' and message['response'] == 200:
            app_log_client.info(f'Установлено соединение с сервером. Ответ сервера: {message["response"]}')
            result_data['token'] = message['token']
            result_data['role'] = message['role']
            result_data['public_key_server'] = PUBLIC_KEY_SERVER
            result_data['public_key_user'] = PUBLIC_KEY_CLIENT
            print('Установлено соединение с сервером.')
            app_log_client.info(f'Запущен клиент с параметрами: адрес сервера: {addr}, порт: {port}, '
                                f'имя пользователя: {result_data["name_account"]}')
            return result_data
    except json.JSONDecodeError:
        app_log_client.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except Exception as er:
        app_log_client.error('Не удалось подключиться к серверу')
        sys.exit(1)


def registration(server, login, password):
    """
    Функция регистрирует новый аккаунт для пользователя. Генерируется приватный, публичный и симметричный ключ
    пользователя для шифрования данных и дальнейшей их передачи. Данные пока никуда не сохраняются.
    :param server:
    :param login:
    :param password:
    :return:
    """
    try:
        if not os.path.isfile(f'{ROOT_DIR}/secret/key_user_{login}.json'):
            with open(f'{ROOT_DIR}/secret/key_user_{login}.json', 'w+', encoding='utf-8'):
                pass
        with open(f'{ROOT_DIR}/secret/key_user_{login}.json', 'r+', encoding='utf-8') as file:
            file.seek(0)
            content = file.read()
            if content:
                data = json.loads(content)
            else:
                data = {}
            if login not in data:
                # сгенерировал приватный и публичный ключ клиента
                PRIVAT_KEY_CLIENT, PUBLIC_KEY_CLIENT = generic_public_and_privat_key_client()
                SYMMETRIC_KEY = generic_symmetric_key_client()
                data['privat_key'] = PRIVAT_KEY_CLIENT
                data['public_key'] = PUBLIC_KEY_CLIENT
                file.seek(0)
                json.dump(data, file)
                file.truncate()
            else:
                database = ClientStorage(login)
                PUBLIC_KEY_CLIENT = database.get_public_key_server_or_user('user')
                PRIVAT_KEY_CLIENT = data[login]
                SYMMETRIC_KEY = generic_symmetric_key_client()
    except FileNotFoundError:
        pass

    # создаем сообщение для получения публичного ключа сервера
    mes = message_template(action='get_public_key', public_key=PUBLIC_KEY_CLIENT)
    # отправляем запрос на получение публичного ключа сервера и отправляем ему публичный ключ клиента
    PUBLIC_KEY_SERVER = get_public_key(server, mes)

    # addr, port = server.getsockname()
    msg = message_template(action='registration', login=login, password=password, public_key=PUBLIC_KEY_CLIENT)
    msg_json = serialization_message(msg)
    # шифруем сообщение с помощью публичного ключа сервера
    encrypted_mes = encrypted_message(msg_json, PUBLIC_KEY_SERVER, SYMMETRIC_KEY)
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
        decrypt_data, sym_key = decrypted_message(data_res[10:], PRIVAT_KEY_CLIENT)
        message = deserialization_message(decrypt_data)
    else:
        message = deserialization_message(data_res)

    if message['response'] == 200:
        app_log_client.info(f'Установлено соединение с сервером. Ответ сервера: {message["response"]}')
        server.close()
    else:
        os.remove(f'{ROOT_DIR}/secret/key_user_{login}.json')
    server.close()
    return message


def init_database(data, server):
    database = ClientStorage(data['name_account'])
    database.add_public_key_server_or_user('server', data['public_key_server'])
    database.add_public_key_server_or_user('user', data['public_key_user'])
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
