import logging
import select
import socket
import base64
import json
from descriptor import ServerCheckPort
from metaclasses import ServerVerifier
from utils import serialization_message
from utils import install_param_in_socket_server
from utils import check_user_is_online
from utils import deserialization_message
from utils import deserialization_message_list
from utils import login_required
from server_database.crud import ServerStorage
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from variables import ROOT_DIR
from log.log_server import server_log_config


app_log_chat = logging.getLogger('chat')
app_log_server = logging.getLogger('server')


class ServerClass(metaclass=ServerVerifier):
    port = ServerCheckPort()
    """
    Класс ServerClass принимает подключения от пользователей и обменивается с ними сообщениями

    Атрибуты:
        addr (str): Ip-адрес подключения
        port (str): Порт подключения
        wait (int): Ожидание подключения
        database (type): Обьект базы данных

    Методы:
        socket_init(): Инициализирует сокет сервера
        create_keys_for_encryption(): Создает или получает ключи шифрования для сервера (публичный, приватный)
        get_and_send_message(): Отправляет и получает сообщения от пользователя
        generic_privat_and_public_keys_server(): Создает ключи шифрования для сервера (публичный, приватный)
        generic_symmetric_key_server(): Создает симметричный ключ шифрования
        encrypted_message(msg_byte, public_key, symmetric_key): Шифрует сообщения гибридным шифрованием
        decrypted_message(data, privat_key): Расшифровывает сообщения
    """

    def __init__(self, addr, port, wait, database):
        self.SYMMETRIC_KEY = None
        self.PRIVAT_KEY_SERVER = None
        self.PUBLIC_KEY_SERVER = None
        self.socket_server = None
        self.addr = addr
        self.port = port
        self.database = database
        self.r = []
        self.w = []
        self.e = []
        self.wait = wait
        # создаем список клиентов, которые подключились
        self.sockets_of_clients = []
        # создаем обьект, который хранит все сообщения пользователей
        self.sockets_message_of_users = {}
        # создаем обьект, который хранит сокеты и логины пользователей, находящихся онлайн
        self.sockets_logins_of_online_users = {}

    def get_and_send_message(self):
        """
        Отправляет и получает сообщения от сервера

        :return: Ничего
        """
        self.socket_init()
        self.create_keys_for_encryption()

        while True:
            try:
                # получаем данные от клиента, который хочет к нам подключиться (клиентский сокет и адрес)
                client, client_addr = self.socket_server.accept()
            except OSError:
                pass
            else:
                # добавляем запись в логи
                app_log_server.info('Получен запрос на соединение от %s', client_addr)

                # добавляем нового клиента в список клиентов
                self.sockets_of_clients.append(client)
            finally:
                # создаем списки клиентов, которые нужно будет обрабатывать
                self.r = []
                self.w = []
                self.e = []
                try:
                    # проверяем есть ли у нас подключенные клиенты
                    if self.sockets_of_clients:
                        # выбираем из списка сокетов (клиентов) тех, которые доступны на чтение, запись, ошибка
                        self.r, self.w, self.e = select.select(self.sockets_of_clients, self.sockets_of_clients,
                                                               self.sockets_of_clients, self.wait)
                except:
                    pass
                # создаем словарь для хранения в нем сообщений клиентов
                self.sockets_message_of_users = {}

                # берем сокет каждого клиента и читаем сообщение, которые он отправил
                for i in self.r:
                    try:
                        # получаем сообщение от пользователя
                        data = i.recv(4096)
                        # проверяем зашифровано сообщение или нет (расшифровываем и декодируем)
                        decode_data = self.decrypted_message(data, self.PRIVAT_KEY_SERVER)
                        # добавляем сообщение пользователя
                        self.sockets_message_of_users[i] = decode_data
                        for el in decode_data:
                            # добавляем нового авторизированного пользователя, если он еще не онлайн
                            if not check_user_is_online(el['user']['user_login'], self.sockets_logins_of_online_users):
                                self.sockets_logins_of_online_users[i] = el['user']['user_login']
                    except Exception:
                        app_log_server.info(f'Клиент {i.fileno()} {i.getpeername()} отключился (отправка)')
                        for mes in self.sockets_message_of_users[i]:
                            self.logout_user(mes, i)

                for socket_of_user in self.sockets_message_of_users:
                    try:
                        for message_of_user in self.sockets_message_of_users[socket_of_user]:
                            # проверяем, онлайн ли пользователь, которому нужно отправить сообщение
                            if not check_user_is_online(message_of_user['user']['user_login'],
                                                        self.sockets_logins_of_online_users):
                                self.sockets_logins_of_online_users[socket_of_user] = message_of_user['user'][
                                    'user_login']
                            # выполняем определенные действия в зависимости от запроса и отправляем ответ пользователю
                            if message_of_user['action'] == 'authorization':
                                self.authorization_user_on_server(message_of_user, socket_of_user)
                            elif message_of_user['action'] == 'registration':
                                self.registration_user_on_server(message_of_user, socket_of_user)
                            elif message_of_user['action'] == 'presence':
                                self.send_message_user_to_user(message_of_user, socket_of_user)
                            elif message_of_user['action'] == 'presence_answer':
                                self.send_message_user_to_user(message_of_user, socket_of_user)
                            elif message_of_user['action'] == 'get_users':
                                self.get_all_registered_users(message_of_user, socket_of_user)
                            elif message_of_user['action'] == 'get_public_key':
                                self.send_and_get_public_key_server(message_of_user, socket_of_user)
                            elif message_of_user['action'] == 'get_public_key_user':
                                self.send_and_get_public_key_user(message_of_user, socket_of_user)
                            elif message_of_user['action'] == 'get_statistics':
                                self.get_statistic_all_users(message_of_user, socket_of_user)
                            elif message_of_user['action'] == 'get_target_contact':
                                self.get_target_users(message_of_user, socket_of_user)
                            elif message_of_user['action'] == 'get_contacts':
                                self.get_contacts_user(message_of_user, socket_of_user)
                            elif message_of_user['action'] == 'get_messages_users':
                                self.get_messages_target_user(message_of_user, socket_of_user)
                            elif message_of_user['action'] == 'add_contact':
                                self.add_contact_to_user(message_of_user, socket_of_user)
                            elif message_of_user['action'] == 'quit':
                                self.logout_user(message_of_user, socket_of_user)
                            elif message_of_user['action'] == 'symmetric_exchange':
                                self.exchange_symmetric_keys_users(message_of_user, socket_of_user)
                    except Exception:
                        app_log_server.info(f'Клиент {socket_of_user.fileno()} {socket_of_user.getpeername()} '
                                            f'отключился (отправка)')
                        for mes in self.sockets_message_of_users[socket_of_user]:
                            self.logout_user(mes, socket_of_user)

    def socket_init(self):
        """
        Инициализирует сокет сервера

        :return: Ничего
        """
        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        app_log_server.info('Сокет инициализирован')
        self.socket_server.bind((self.addr, self.port))
        self.socket_server.settimeout(1)
        self.socket_server.listen()

    def create_keys_for_encryption(self):
        """
        Создает или получает ключи сервера

        :return: Строку "Ok" или "Error"
        """
        try:
            with open(f'{ROOT_DIR}/secret/keys_server.json', 'w+', encoding='utf-8'):
                pass
            with open(f'{ROOT_DIR}/secret/keys_server.json', 'r+', encoding='utf-8') as file:
                file.seek(0)
                content = file.read()
                if content:
                    result = json.loads(content)
                    self.PRIVAT_KEY_SERVER = result['privat_key']
                    self.PUBLIC_KEY_SERVER = result['public_key']
                else:
                    data = {}
                    self.PRIVAT_KEY_SERVER, self.PUBLIC_KEY_SERVER = self.generic_privat_and_public_keys_server()
                    data['privat_key'] = self.PRIVAT_KEY_SERVER
                    data['public_key'] = self.PUBLIC_KEY_SERVER
                    file.seek(0)
                    json.dump(data, file)
                    file.truncate()
            return 'Ok'
        except FileNotFoundError:
            return 'Error'

    def generic_privat_and_public_keys_server(self):
        """
        Генерируем публичный и приватный ключи для шифровки сообщения и возвращаем их в строковом формате

        :return: Возвращает приватный и публичный ключ сервера. Тип str
        """
        key = RSA.generate(1024)
        PRIVAT_KEY = key.export_key().decode()
        PUBLIC_KEY = key.public_key().export_key().decode()
        return PRIVAT_KEY, PUBLIC_KEY

    def generic_symmetric_key_server(self):
        """
        Генерируем симметричный ключ и возвращаем его в строковом формате

        :return: Возвращает симметричный ключ. Тип bytes
        """
        SYMMETRIC_KEY = get_random_bytes(16)
        return SYMMETRIC_KEY

    def encrypted_message(self, msg_byte, public_key, symmetric_key):
        """
        Метод шифрует сообщение методом гибридного шифрования

        :param msg_byte: Кодированное сообщение. Тип binary
        :param public_key: Публичный ключ пользователя. Тип str
        :param symmetric_key: Симметричный ключ сообщения. Тип str
        :return: Зашифрованное и сериализованное сообщение. Тип binary
        """
        nonce = get_random_bytes(16)
        resipient_key = RSA.import_key(public_key)
        cipher = PKCS1_OAEP.new(resipient_key)
        encrypted_symmetric_key = cipher.encrypt(symmetric_key)
        cipher_aes = AES.new(symmetric_key, AES.MODE_EAX, nonce)

        crypt_mes, tag_mac = cipher_aes.encrypt_and_digest(msg_byte)
        encrypted_data = {
            'message': base64.b64encode(crypt_mes).decode('utf-8'),
            'symmetric_key': base64.b64encode(encrypted_symmetric_key).decode('utf-8'),
            'nonce': base64.b64encode(nonce).decode('utf-8')
        }
        encode_msg = 'ENCRYPTED:'.encode('utf-8') + serialization_message(encrypted_data)

        return encode_msg

    def decrypted_message(self, data, privat_key):
        """
        Метод расшифровывает и десериализует сообщения

        :param data: Кодированное сообщение. Тип binary
        :param privat_key: Приватный ключ сервера. Тип str
        :return: Расшифрованное и десериализованное сообщение. Тип dict
        """
        if data[:10] == b'ENCRYPTED:':
            decode_mes = deserialization_message(data[10:])
            if 'action' in decode_mes and decode_mes['action'] == 'send_message_user':
                return decode_mes
            resipient_key = RSA.import_key(privat_key)
            cipher = PKCS1_OAEP.new(resipient_key)
            decrypt_symmetric_key = cipher.decrypt(base64.b64decode(decode_mes['symmetric_key']))
            cipher_aes = AES.new(decrypt_symmetric_key, AES.MODE_EAX, base64.b64decode(decode_mes['nonce']))
            decrypt_mes = cipher_aes.decrypt(base64.b64decode(decode_mes['message']))
            decode_result_message = deserialization_message_list(decrypt_mes)
        else:
            decode_result_message = deserialization_message_list(data)
        return decode_result_message

    def exchange_symmetric_keys_users(self, message, socket_of_user):
        """
        Метод работает с сохранением, изменением и отправкой симметричного ключа для обмена сообщениями
        между пользователями

        :param message: Сообщение. Тип dict
        :param socket_of_user: Сокет пользователя. Тип obj
        :return: Строку "Ok"
        """
        if message['mess_text'] == 'update':
            self.database.update_contact_add_symmetric_key(
                message['user']['user_login'], message['to'], json.dumps(message['crypto_symmetric_key'])
            )
            return 'Ok'
        elif message['mess_text'] == 'check_sym_key':
            symmetric_key_check_to_user = self.database.get_symmetric_key_for_communicate_between_users(
                message['to'], message['user']['user_login']
            )
            symmetric_key_check_from_user = self.database.get_symmetric_key_for_communicate_between_users(
                message['user']['user_login'], message['to']
            )
            if symmetric_key_check_to_user:
                json_sym_key = json.loads(symmetric_key_check_to_user)
                msg = {
                    'response': 200,
                    'alert': 'Симметричный ключ получен',
                    'to': message['to'],
                    'symmetric_key': json_sym_key,
                    'action': 'old'
                }
                user_public_key = self.database.get_public_key_user(message['user']['user_login'])
                byte_message = serialization_message(msg)
                result = self.encrypted_message(byte_message, user_public_key, self.SYMMETRIC_KEY)
                socket_of_user.send(result)

            if not symmetric_key_check_to_user and not symmetric_key_check_from_user:
                msg = {
                    'response': 200,
                    'alert': 'Симметричный ключ получен',
                    'to': message['to'],
                    'action': 'new'
                }
                user_public_key = self.database.get_public_key_user(message['user']['user_login'])
                byte_message = serialization_message(msg)
                result = self.encrypted_message(byte_message, user_public_key, self.SYMMETRIC_KEY)
                socket_of_user.send(result)
            return 'Ok'

    def authorization_user_on_server(self, message, socket_of_user):
        """
        Функция принимает сообщение от пользователя на авторизацию, авторизирует его и отправляет ему ответ

        :param message: Сообщение. Тип dict
        :param socket_of_user: Сокет пользователя. Тип obj
        :return: Строку "Ok"
        """
        user_login = message['user']['user_login']
        role_user = self.database.get_user_role(user_login)
        if 'action' in message and message['action'] == 'authorization' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'user_password' in message['user'] and \
                self.database.check_authenticated(user_login, message['user']['user_password']) and not \
                check_user_is_online(user_login, self.sockets_logins_of_online_users):
            self.SYMMETRIC_KEY = self.generic_symmetric_key_server()
            if role_user == 'Администратор':
                history_obj = self.database.get_history_users()
                history_message = []
                token = self.database.login(user_login, socket_of_user)
                mes = {
                    'response': 200,
                    'user_name': user_login,
                    'token': token,
                    'alert': 'Успешная авторизация',
                    'role': 'Администратор',
                    'users': history_obj,
                    'users_message': history_message
                }
                byte_message = serialization_message(mes)
                result = self.encrypted_message(byte_message, message['public_key'], self.SYMMETRIC_KEY)
                app_log_server.info(f'Пользователь {user_login} авторизирован!')
                socket_of_user.send(result)

            elif role_user == 'Пользователь':
                history_obj = []
                token = self.database.login(user_login, socket_of_user)
                mes = {
                    'response': 200,
                    'user_name': user_login,
                    'token': token,
                    'alert': 'Успешная авторизация',
                    'role': 'Пользователь',
                    'users': history_obj,
                }
                byte_message = serialization_message(mes)
                result = self.encrypted_message(byte_message, message['public_key'], self.SYMMETRIC_KEY)
                app_log_server.info(f'Пользователь {user_login} авторизирован!')
                socket_of_user.send(result)

        elif 'action' in message and message['action'] == 'authorization' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'user_password' in message['user'] and not \
                self.database.check_authenticated(user_login, message['user']['user_password']):
            mes = {
                'role': 'Неверный логин или пароль',
                'response': 401
            }
            result = serialization_message(mes)
            app_log_server.info(f'Пользователь {user_login} не авторизирован!')
            socket_of_user.send(result)
            app_log_server.info(f'Клиент {socket_of_user.fileno()} {socket_of_user.getpeername()} '
                                f'отключился (отправка)')
            socket_of_user.close()
            self.sockets_of_clients.remove(socket_of_user)
            del self.sockets_logins_of_online_users[socket_of_user]

        elif 'action' in message and message['action'] == 'authorization' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'user_password' in message['user'] and \
                self.database.check_authenticated(user_login, message['user']['user_password']) and \
                check_user_is_online(user_login, self.sockets_logins_of_online_users):
            mes = {
                'role': 'Нет доступа',
                'response': 409
            }
            result = serialization_message(mes)
            app_log_server.info(f'Пользователь {user_login} уже есть в системе!')
            socket_of_user.send(result)
            app_log_server.info(f'Клиент {socket_of_user.fileno()} {socket_of_user.getpeername()} '
                                f'отключился (отправка)')
            socket_of_user.close()
            self.sockets_of_clients.remove(socket_of_user)
            del self.sockets_logins_of_online_users[socket_of_user]

        return 'Ok'

    def registration_user_on_server(self, message, socket_of_user):
        """
        Функция принимает сообщение от пользователя на регистрацию, регистрирует его и отправляет ему ответ

        :param message: Сообщение. Тип dict
        :param socket_of_user: Сокет пользователя. Тип obj
        :return: Строку "Ok"
        """
        user_login = message['user']['user_login']
        if 'action' in message and message['action'] == 'registration' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'user_password' in message['user']:
            self.SYMMETRIC_KEY = self.generic_symmetric_key_server()
            password_hash = self.database.hash_password(message['user']['user_password'])
            result = self.database.register(message['user']['user_login'], password_hash, message['public_key'])
            if result == 'Ok':
                msg = {
                    'response': 200,
                    'user_name': user_login,
                    'alert': 'Успешная регистрация'
                }
                byte_message = serialization_message(msg)
                result = self.encrypted_message(byte_message, message['public_key'], self.SYMMETRIC_KEY)
                app_log_server.info(f'Пользователь зарегестрирован!')
                socket_of_user.send(result)
                socket_of_user.close()
                self.sockets_of_clients.remove(socket_of_user)
                del self.sockets_logins_of_online_users[socket_of_user]
            else:
                msg = {
                    'response': 400,
                    'user_name': user_login,
                    'alert': 'Данные не валидны'
                }
                byte_message = serialization_message(msg)
                result = self.encrypted_message(byte_message, message['public_key'], self.SYMMETRIC_KEY)
                app_log_server.info(f'Пользователь не зарегестрирован!')
                socket_of_user.send(result)
                socket_of_user.close()
                self.sockets_of_clients.remove(socket_of_user)
                del self.sockets_logins_of_online_users[socket_of_user]

            return 'Ok'

    @login_required
    def send_message_user_to_user(self, message, socket_of_user):
        """
        Функция принимает сообщение от пользователя на отправку сообщения другому пользователю и отправляет
        его ему

        :param message: Сообщение. Тип dict
        :param socket_of_user: Сокет пользователя. Тип obj
        :return: Строку "Ok"
        """
        user_login = message['user']['user_login']
        if 'action' in message and message['action'] == 'presence' and 'time' in message and 'user' in message and \
                'user_login' in message['user'] and self.database.check_login(user_login) and 'token' in message['user'] and \
                self.database.check_authorized(user_login, message['user']['token']) and 'mess_text' in message and \
                'to' in message:
            self.database.add_history_message(user_login, message['to'], message['mess_text']['message'],
                                              message['hash_mes'], message['mess_text']['nonce'])
            msg_to = {
                "response": 200,
                'user_name': user_login,
                'alert': message['mess_text'],
                'to': message['to'],
                'hash_mes': message['hash_mes']
            }
            msg_from = {
                "response": 200,
                'user_name': user_login,
                'to': message['to'],
                'alert': 'Сообщение доставлено',
                'message': message['mess_text']
            }

            byte_message = serialization_message(msg_from)
            socket_of_user.send(byte_message)

            for key, value in self.sockets_logins_of_online_users.items():
                if value == message['to']:
                    byte_message = serialization_message(msg_to)
                    key.send(byte_message)

        if 'action' in message and message['action'] == 'presence_answer' and 'time' in message and 'user' in message and \
                'user_login' in message['user'] and self.database.check_login(user_login) and 'token' in message['user'] and \
                self.database.check_authorized(user_login, message['user']['token']) and 'mess_text' in message and \
                'to' in message:
            self.database.add_history_message(user_login, message['to'], message['message'], message['hash_mes'])
        return 'Ok'

    @login_required
    def get_all_registered_users(self, message, socket_of_user):
        """
        Функция принимает сообщение от пользователя на получение всех логинов пользователей,
        которые зарегестрирвоаны

        :param message: Сообщение. Тип dict
        :param socket_of_user: Сокет пользователя. Тип obj
        :return: Строку "Ok"
        """
        user_login = message['user']['user_login']
        if 'action' in message and message['action'] == 'get_users' and 'time' in message and 'user' in message and \
                'user_login' in message['user'] and self.database.check_login(user_login) and \
                'token' in message['user'] and self.database.check_admin(user_login):
            msg = {
                'response': 200,
                'user_name': user_login,
                'alert': 'Список пользователей отправлен',
                'users': self.database.get_users()
            }
            user = message['user']['user_login']
            byte_message = serialization_message(msg)
            socket_of_user.send(byte_message)
            app_log_server.info(f'Списко пользователей отправлен {user}')

        return 'Ok'

    def send_and_get_public_key_user(self, message, socket_of_user):
        """
        Берет публичный ключ пользователя из базы данных и отправляет его ему

        :param message: Сообщение от пользователя. Тип dict
        :param socket_of_user: Сокет пользователя. Тип obj
        :return: Строка "Ok"
        """
        if 'action' in message and message['action'] == 'get_public_key_user':
            key_user = self.database.get_public_key_user(message['to'])
            msg = {
                'response': 200,
                'alert': 'Публичный ключ пользователя отправлен',
                'public_key': key_user,
                'to': message['to']
            }
            byte_message = serialization_message(msg)
            app_log_server.info(f'Публичный ключ отправлен')
            socket_of_user.send(byte_message)

        return 'Ok'

    def send_and_get_public_key_server(self, message, socket_of_user):
        """
        Функция принимает сообщение от пользователя на отправку публичного ключа и отправляет в ответ ключ.
        Сообщение передается в незашифрованном виде

        :param message:
        :param socket_of_user:
        :return:
        """
        if 'action' in message and message['action'] == 'get_public_key':
            msg = {
                'response': 200,
                'alert': 'Публичный ключ отправлен',
                'public_key': self.PUBLIC_KEY_SERVER,
            }
            byte_message = serialization_message(msg)
            app_log_server.info(f'Публичный ключ отправлен')
            socket_of_user.send(byte_message)

        return 'Ok'

    def get_statistic_all_users(self, message, socket_of_user):
        """
        Функция принимает запрос на получение статистики зарегестрированных пользователей и отправляет ее

        :param message: Сообщение. Тип dict
        :param socket_of_user: Сокет пользователя. Тип obj
        :return: Строку "Ok"
        """
        user_login = message['user']['user_login']
        if 'action' in message and message['action'] == 'get_statistics' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'token' in message['user'] and \
                self.database.check_authorized(user_login, message['user']['token']) and \
                self.database.get_user_role(user_login) == 'Администратор':
            history_obj = self.database.get_history_user(message['statistic'])

            msg = {
                'response': 200,
                'user_name': user_login,
                'token': '',
                'alert': 'Статистика отправлена',
                'role': 'Администратор',
                'user_history': {
                    'create_at': history_obj.create_at.strftime("%Y-%m-%d %H:%M:%S"), 'login': history_obj.login,
                    'id': history_obj.id, 'ip': history_obj.ip_address
                }
            }

            byte_message = serialization_message(msg)
            socket_of_user.send(byte_message)
            app_log_server.info(f'Статистика отправлена')

        return 'Ok'

    def get_target_users(self, message, socket_of_user):
        """
        Функция принимает запрос на получение зарегестрированных пользователей, логин которых начинается на
        определенное значение и отправляет их

        :param message: Сообщение. Тип dict
        :param socket_of_user: Сокет пользователя. Тип obj
        :return: Строку "Ok"
        """
        user_login = message['user']['user_login']
        if 'action' in message and message['action'] == 'get_target_contact' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'token' in message['user'] and \
                self.database.check_authorized(user_login, message['user']['token']):
            msg = {
                'response': 202,
                'alert': self.database.get_target_contact(message['search_contact'], user_login),
                'action': 'get_target_contact',
                'user_name': user_login
            }
            byte_message = serialization_message(msg)
            app_log_server.info(f'Контакты готовы!')
            socket_of_user.send(byte_message)
        return 'Ok'

    def get_messages_target_user(self, message, socket_of_user):
        """
        Функция принимает запрос на получение всех сообщений определенного пользователя и отправляет их

        :param message: Сообщение. Тип dict
        :param socket_of_user: Сокет пользователя. Тип obj
        :return: Строку "Ok"
        """
        user_login = message['user']['user_login']
        if 'action' in message and message['action'] == 'get_messages_users' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'token' in message['user'] and \
                self.database.check_authorized(user_login, message['user']['token']):
            msg = {
                'response': 202,
                'alert': 'Сообщения отправлены',
                'message': self.database.get_history_message_user(user_login, message['to']),
                'to': message['to']
            }
            byte_message = serialization_message(msg)
            app_log_server.info(f'Сообщения пользователя {user_login} готовы!')
            socket_of_user.send(byte_message)

        return 'Ok'

    def get_contacts_user(self, message, socket_of_user):
        """
        Функция принимает запрос на получение всех контактов определенного пользователя и отправляет их

        :param message: Сообщение. Тип dict
        :param socket_of_user: Сокет пользователя. Тип obj
        :return: Строку "Ok"
        """
        user_login = message['user']['user_login']
        if 'action' in message and message['action'] == 'get_contacts' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'token' in message['user'] and \
                self.database.check_authorized(user_login, message['user']['token']):
            msg = {
                'response': 202,
                'alert': self.database.get_contacts(user_login)
            }
            byte_message = serialization_message(msg)
            app_log_server.info(f'Контакты пользователя {user_login} готовы!')
            socket_of_user.send(byte_message)

        return 'Ok'

    def add_contact_to_user(self, message, socket_of_user):
        """
        Функция принимает запрос на добавление контакта для пользователя и добавляет его ему в контакты

        :param message: Сообщение. Тип dict
        :param socket_of_user: Сокет пользователя. Тип obj
        :return: Строку "Ok"
        """
        # закончили на том, что добавили функционал с добавлением контакта сразу в обе стороны пользователей
        # + сделали отправку публичных ключей пользователям для общения друг с другом, нужно доработать !!!!!!!!Ё!
        user_login = message['user']['user_login']
        if 'action' in message and message['action'] == 'add_contact' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'token' in message['user'] and \
                self.database.check_authorized(user_login, message['user']['token']) and 'user_id' in message and \
                message['user_id']:
            # проверяем есть ли добавляемый контакт в базе
            if self.database.check_login(message['user_id']):
                # если да, то берем его публичный ключ
                public_key = self.database.get_public_key_user(message['user_id'])
                # создаем сообщение для ответа
                msg = {
                    'response': 200,
                    'user_name': user_login,
                    'to_user': message['user_id'],
                    'alert': f'Пользователь добавлен в контакты',
                    'public_key_recipient': public_key.replace('\n', '\\n'),
                    'sender': 'yes'
                }
                # переводим сообщение с обьекта в набор json и набор байт
                byte_message = serialization_message(msg)
                # добавляем контакт в базу данных (с обоих сторон)
                self.database.add_contact(user_login, message['user_id'])
                app_log_server.info(f'Добавлен новый контакт пользователю {user_login}')
                # отправляем ответ пользователю на добавление контакта
                socket_of_user.send(byte_message)
                # перебираем всех пользователей онлайн
                for key, value in self.sockets_logins_of_online_users.items():
                    # если пользователь, которого я добавляю в контакты есть в онлайн
                    if value == message['user_id']:
                        # отправляем ему сообщение
                        msg = {
                            'response': 200,
                            'user_name': message['user_id'],
                            'to_user': user_login,
                            'alert': f'Пользователь добавлен в контакты',
                            'public_key_recipient': message['public_key'].replace('\n', '\\n')
                        }
                        byte_message = serialization_message(msg)
                        result = self.encrypted_message(byte_message, public_key, self.SYMMETRIC_KEY)
                        key.send(result)
            else:
                msg = {
                    'response': 400,
                    'user_name': user_login,
                    'alert': 'Для добавления пользователь должен быть в базе'
                }
                byte_message = serialization_message(msg)
                socket_of_user.send(byte_message)

        return 'Ok'

    def logout_user(self, message, socket_of_user):
        """
        Функция принимает запрос на выход из аккаунта и выходит

        :param message: Сообщение. Тип dict
        :param socket_of_user: Сокет пользователя. Тип obj
        :return: Строку "Ok"
        """
        user_login = message['user']['user_login']
        if 'action' in message and 'time' in message and 'user' in message and 'user_login' in message['user'] and \
                'token' in message['user'] and self.database.check_authorized(user_login, message['user']['token']):
            msg = {
                'response': 200,
                'user_name': user_login,
                'alert': 'Пользователь вышел'
            }
            self.database.logout(user_login)
            byte_message = serialization_message(msg)
            app_log_server.info(f'Пользователь {user_login} вышел!')
            socket_of_user.send(byte_message)
            socket_of_user.close()
            self.sockets_of_clients.remove(socket_of_user)
            del self.sockets_logins_of_online_users[socket_of_user]

        return 'Ok'


def main():
    addr, port = install_param_in_socket_server()
    obj_server = ServerClass(addr, port, 10, ServerStorage())
    obj_server.get_and_send_message()


if __name__ == '__main__':
    main()
