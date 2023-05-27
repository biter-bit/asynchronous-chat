import logging
import select
import socket
import base64
from descriptor import ServerCheckPort
from metaclasses import ServerVerifier
from utils import serialization_message
from utils import install_param_in_socket_server
from utils import check_user_is_online
from utils import deserialization_message
from utils import deserialization_message_list
from utils import login_required
from server_database.crud import ServerStorage
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes


app_log_chat = logging.getLogger('chat')
app_log_server = logging.getLogger('server')


class Server(metaclass=ServerVerifier):
    port = ServerCheckPort()

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

    def socket_init(self):
        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        app_log_server.info('Сокет инициализирован')
        self.socket_server.bind((self.addr, self.port))
        self.socket_server.settimeout(1)
        self.socket_server.listen()

    def create_keys_for_encryption(self):
        self.PRIVAT_KEY_SERVER, self.PUBLIC_KEY_SERVER, self.SYMMETRIC_KEY = self.generic_key_server()
        return 'Ok'

    def get_and_send_message(self):
        # инициализируем сокет
        self.socket_init()

        # генерируем ключи для сервера
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
                        decode_data = self.decrypted_message(data, self.PRIVAT_KEY_SERVER.decode())
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
                            elif message_of_user['action'] == 'get_users':
                                self.get_all_registered_users(message_of_user, socket_of_user)
                            elif message_of_user['action'] == 'get_public_key':
                                self.send_and_get_public_key_server(message_of_user, socket_of_user)
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
                    except Exception:
                        app_log_server.info(f'Клиент {socket_of_user.fileno()} {socket_of_user.getpeername()} '
                                            f'отключился (отправка)')
                        for mes in self.sockets_message_of_users[socket_of_user]:
                            self.logout_user(mes, socket_of_user)

    def generic_key_server(self):
        """Генерируем публичный и приватный ключи для шифровки сообщения и возвращаем их в бинарном формате"""
        key = RSA.generate(1024)
        PRIVAT_KEY = key.export_key()
        PUBLIC_KEY = key.public_key().export_key()
        SYMMETRIC_KEY = get_random_bytes(16)
        return PRIVAT_KEY, PUBLIC_KEY, SYMMETRIC_KEY

    def encrypted_message(self, msg, public_key, symmetric_key):
        nonce = get_random_bytes(16)
        resipient_key = RSA.import_key(public_key)
        cipher = PKCS1_OAEP.new(resipient_key)
        encrypted_symmetric_key = cipher.encrypt(symmetric_key)
        cipher_aes = AES.new(symmetric_key, AES.MODE_EAX, nonce)

        crypt_mes, tag_mac = cipher_aes.encrypt_and_digest(msg)
        encrypted_data = {
            'message': base64.b64encode(crypt_mes).decode('utf-8'),
            'symmetric_key': base64.b64encode(encrypted_symmetric_key).decode('utf-8'),
            'nonce': base64.b64encode(nonce).decode('utf-8')
        }
        encode_msg = 'ENCRYPTED:'.encode('utf-8') + serialization_message(encrypted_data)

        return encode_msg

    def decrypted_message(self, data, privat_key):
        if data[:10] == b'ENCRYPTED:':
            decode_mes = deserialization_message(data[10:])
            resipient_key = RSA.import_key(privat_key)
            cipher = PKCS1_OAEP.new(resipient_key)
            decrypt_symmetric_key = cipher.decrypt(base64.b64decode(decode_mes['symmetric_key']))
            cipher_aes = AES.new(decrypt_symmetric_key, AES.MODE_EAX, base64.b64decode(decode_mes['nonce']))
            decrypt_mes = cipher_aes.decrypt(base64.b64decode(decode_mes['message']))
            decode_result_message = deserialization_message_list(decrypt_mes)
        else:
            decode_result_message = deserialization_message_list(data)
        return decode_result_message

    def authorization_user_on_server(self, message, socket_of_user):
        """Функция принимает сообщение от пользователя на авторизацию, авторизирует его и отправляет ему ответ"""
        user_login = message['user']['user_login']
        role_user = self.database.get_user_role(user_login)
        if 'action' in message and message['action'] == 'authorization' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'user_password' in message['user'] and \
                self.database.check_authenticated(user_login, message['user']['user_password']):
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
                history_message = self.database.get_history_message_user(user_login)
                token = self.database.login(user_login, socket_of_user)
                mes = {
                    'response': 200,
                    'user_name': user_login,
                    'token': token,
                    'alert': 'Успешная авторизация',
                    'role': 'Пользователь',
                    'users': history_obj,
                    'users_message': history_message
                }
                byte_message = serialization_message(mes)
                result = self.encrypted_message(byte_message, message['public_key'], self.SYMMETRIC_KEY)
                app_log_server.info(f'Пользователь {user_login} авторизирован!')
                socket_of_user.send(result)

            elif not self.database.check_authenticated(message['user']['user_login'], message['user']['user_password']):
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

            elif check_user_is_online(message['user']['user_login'], self.sockets_logins_of_online_users):
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
        """Функция принимает сообщение от пользователя на регистрацию, регистрирует его и отправляет ему ответ"""
        user_login = message['user']['user_login']
        if 'action' in message and message['action'] == 'registration' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'user_password' in message['user']:
            password_hash = self.database.hash_password(message['user']['user_password'])
            result = self.database.register(message['user']['user_login'], password_hash)
            if result == 'Ok':
                msg = {
                    'response': 200,
                    'user_name': user_login,
                    'alert': 'Успешная регистрация'
                }
                byte_message = serialization_message(msg)
                app_log_server.info(f'Пользователь зарегестрирован!')
                socket_of_user.send(byte_message)
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
                app_log_server.info(f'Пользователь не зарегестрирован!')
                socket_of_user.send(byte_message)
                socket_of_user.close()
                self.sockets_of_clients.remove(socket_of_user)
                del self.sockets_logins_of_online_users[socket_of_user]

            return 'Ok'


    @login_required
    def send_message_user_to_user(self, message, socket_of_user):
        """Функция принимает сообщение от пользователя на отправку сообщения другому пользователю и отправляет
        его ему"""
        user_login = message['user']['user_login']
        if 'action' in message and message['action'] == 'presence' and 'time' in message and 'user' in message and \
                'user_login' in message['user'] and self.database.check_login(user_login) and 'token' in message['user'] and \
                self.database.check_authorized(user_login, message['user']['token']) and 'mess_text' in message and \
                'to' in message:

            msg_to = {
                "response": 200,
                'user_name': user_login,
                'alert': message['mess_text'],
                'from': message['to']
            }
            msg_from = {
                "response": 200,
                'user_name': user_login,
                'to': message['to'],
                'alert': 'Сообщение доставлено',
                'message': message['mess_text']
            }

            hash_mes = self.database.add_history_message(user_login, message['to'], message['mess_text'])
            msg_from['hash_message'] = hash_mes
            byte_message = serialization_message(msg_from)
            socket_of_user.send(byte_message)

            for key, value in self.sockets_logins_of_online_users.items():
                if value == message['to']:
                    msg_to['hash_message'] = hash_mes
                    byte_message = serialization_message(msg_to)
                    key.send(byte_message)

        return 'Ok'

    @login_required
    def get_all_registered_users(self, message, socket_of_user):
        """Функция принимает сообщение от пользователя на получение всех логинов пользователей,
        которые зарегестрирвоаны"""
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

    def send_and_get_public_key_server(self, message, socket_of_user):
        """Функция принимает сообщение от пользователя на отправку и получение публичного ключа и отправляет ответ"""
        if 'action' in message and message['action'] == 'get_public_key':
            msg = {
                'response': 200,
                'alert': 'Публичный ключ отправлен',
                'public_key': self.PUBLIC_KEY_SERVER.decode(),
            }
            byte_message = serialization_message(msg)
            app_log_server.info(f'Публичный ключ отправлен')
            socket_of_user.send(byte_message)

        return 'Ok'

    def get_statistic_all_users(self, message, socket_of_user):
        """Функция принимает запрос на получение статистики зарегестрированных пользователей и отправляет ее"""
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
        """Функция принимает запрос на получение зарегестрированных пользователей, логин которых начинается на
        определенное значение и отправляет их"""
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
        """Функция принимает запрос на получение всех сообщений определенного пользователя и отправляет их"""
        user_login = message['user']['user_login']
        if 'action' in message and message['action'] == 'get_messages_users' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'token' in message['user'] and \
                self.database.check_authorized(user_login, message['user']['token']):
            msg = {
                'response': 202,
                'alert': 'Сообщения отправлены',
                'message': self.database.get_history_message_user(user_login)
            }
            byte_message = serialization_message(msg)
            app_log_server.info(f'Сообщения пользователя {user_login} готовы!')
            socket_of_user.send(byte_message)

        return 'Ok'

    def get_contacts_user(self, message, socket_of_user):
        """Функция принимает запрос на получение всех контактов определенного пользователя и отправляет их"""
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
        """Функция принимает запрос на добавление контакта для пользователя и добавляет его ему в контакты"""
        user_login = message['user']['user_login']
        if 'action' in message and message['action'] == 'add_contact' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'token' in message['user'] and \
                self.database.check_authorized(user_login, message['user']['token']) and 'user_id' in message and \
                message['user_id']:
            if self.database.check_login(message['user_id']):
                msg = {
                    'response': 200,
                    'user_name': user_login,
                    'to_user': message['user_id'],
                    'alert': f'Пользователь добавлен в контакты'
                }
                byte_message = serialization_message(msg)
                self.database.add_contact(user_login, message['user_id'])
                app_log_server.info(f'Добавлен новый контакт пользователю {user_login}')
                socket_of_user.send(byte_message)
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
        """Функция принимает запрос на выход из аккаунта и выходит"""
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

    def delete_contact_to_user(self):
        # # если пользователь отправил сообщение на удаление контакта
        # elif 'action' in message and message['action'] == 'del_contact' and 'time' in message and \
        #         'user' in message and 'user_login' in message['user'] and 'token' in message['user'] and \
        #         database.check_authorized(user_login, message['user']['token']) and 'user_id' in message and \
        #         message['user_id'] and database.check_login(message['user_id']):
        #     return {'response': 200, 'user_name': user_login, 'to_user': message['user_id'],
        #             'alert': f'Пользователь удален из контактов'}

        # # если пользователь отправил сообщение на удаление контакта, но контакта в базе нет
        # elif 'action' in message and message['action'] == 'del_contact' and 'time' in message and \
        #         'user' in message and 'user_login' in message['user'] and 'token' in message['user'] and \
        #         database.check_authorized(user_login, message['user']['token']) and 'user_id' in message and \
        #         message['user_id'] and not database.check_login(message['user_id']):
        #     return {'response': 400, 'user_name': user_login, 'alert': 'Для удаления пользователь должен быть в базе'}
        # elif message_of_user['action'] == 'del_contact' \
        #         and message_response['response'] == 200:
        #     user = message_of_user['user']['user_login']
        #     contact = message_of_user['user_id']
        #     self.database.del_contact(user, contact)
        #     byte_message = serialization_message(message_response)
        #     app_log_server.info(f'Удален контакт пользователю {user}')
        #     socket_of_user.send(byte_message)
        # elif message_of_user['action'] == 'del_contact' \
        #         and message_response['response'] == 400:
        #     byte_message = serialization_message(message_response)
        #     socket_of_user.send(byte_message)
        pass


def main():
    addr, port = install_param_in_socket_server()
    obj_server = Server(addr, port, 10, ServerStorage())
    obj_server.get_and_send_message()


if __name__ == '__main__':
    main()
