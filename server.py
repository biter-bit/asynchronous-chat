import logging
import select
import socket
import sys
import time

from descriptor import ServerCheckPort
from metaclasses import ServerVerifier
from utils import serialization_message, deserialization_message_list, sys_param_reboot
from log.log_server import server_log_config
from server_database.crud import ServerStorage
from server_database.model import User

app_log_server = logging.getLogger('server')
app_log_chat = logging.getLogger('chat')


def install_param_in_socket_server():
    """Устанавливаем введенные пользователем параметры подключения к серверу/создания сервера"""
    param = sys.argv
    port = 10002
    addr = 'localhost'
    try:
        for i in param:
            if i == '-p':
                port = int(param[param.index(i) + 1])
            if i == '-a':
                addr = param[param.index(i) + 1]
        sys_param_reboot()
        app_log_server.info('Параметры сокета успешно заданы')
        return addr, port
    except Exception as error:
        app_log_server.error('Параметр задан неверно')
        name_error = 'Ошибка'
        return error, name_error


class Server(metaclass=ServerVerifier):
    port = ServerCheckPort()

    def __init__(self, addr, port, wait, database):
        self.sock = None
        self.addr = addr
        self.port = port
        self.clients = []

        # создаем обьект для работы с б.д.
        self.database = database

        self.r = []
        self.w = []
        self.e = []
        self.message_client = {}
        self.wait = wait

        # создаем обьект, который будет ассоциировать логины с сокетами
        self.name = {}

    def socket_init(self):
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        app_log_server.info('Сокет инициализирован')
        transport.bind((self.addr, self.port))
        transport.settimeout(1)
        self.sock = transport
        self.sock.listen()

    def get_and_send_message(self):
        # инициализируем сокет
        self.socket_init()

        while True:
            try:
                # получаем данные от клиента, который хочет к нам подключиться (клиентский сокет и адрес)
                client, client_addr = self.sock.accept()
            except OSError:
                pass
            else:
                # добавляем запись в логи
                app_log_server.info('Получен запрос на соединение от %s', client_addr)

                # добавляем нового клиента в список клиентов
                self.clients.append(client)
            finally:
                # создаем списки клиентов, которые нужно будет обрабатывать
                self.r = []
                self.w = []
                self.e = []
                try:
                    # проверяем есть ли у нас подключенные клиенты
                    if self.clients:
                        # выбираем из списка сокетов (клиентов) тех, которые доступны на чтение, запись, ошибка
                        self.r, self.w, self.e = select.select(self.clients, self.clients, self.clients, self.wait)
                except:
                    pass
                # создаем словарь для хранения в нем сообщений клиентов
                self.message_client = {}

                # берем сокет каждого клиента и читаем сообщение, которые он отправил
                for i in self.r:
                    try:
                        data = i.recv(4096)
                        decode_data_dict = deserialization_message_list(data)
                        # if i in self.name:
                        #     raise Exception
                        for el in decode_data_dict:
                            for sock_name in self.name:
                                if self.name[sock_name] == el['user']['user_login'] and el['action'] == 'authorization':
                                    raise Exception
                            if el['user']['user_login'] not in self.name.values():
                                self.name[i] = el['user']['user_login']
                        self.message_client[i] = decode_data_dict
                    except Exception:
                        app_log_server.info(f'Клиент {i.fileno()} {i.getpeername()} отключился (чтение)')
                        i.close()
                        self.clients.remove(i)

                if self.message_client:
                    for socket_client_mes_name in self.message_client:
                        try:
                            for socket_client_message in self.message_client[socket_client_mes_name]:
                                # проверяем, онлайн ли пользователь, которому нужно отправить сообщение
                                if socket_client_message['user']['user_login'] not in self.name.values():
                                    # если нет, то делаем его онлайн
                                    self.name[socket_client_mes_name] = socket_client_message['user']['user_login']
                                message_response = self.message_processing(socket_client_message, self.database,
                                                                           socket_client_mes_name)
                                if socket_client_message['action'] == 'authorization' \
                                        and message_response['response'] == 200:
                                    user = socket_client_message['user']['user_login']
                                    token = self.database.login(user, socket_client_mes_name)
                                    message_response['token'] = token
                                    if user not in self.name:
                                        self.name[socket_client_mes_name] = user
                                    byte_message = serialization_message(message_response)
                                    app_log_server.info(f'Пользователь {user} авторизирован!')
                                    socket_client_mes_name.send(byte_message)
                                elif socket_client_message['action'] == 'registration' \
                                        and message_response['response'] == 200:
                                    byte_message = serialization_message(message_response)
                                    app_log_server.info(f'Пользователь зарегестрирован!')
                                    socket_client_mes_name.send(byte_message)
                                    socket_client_mes_name.close()
                                    self.clients.remove(socket_client_mes_name)
                                    del self.name[socket_client_mes_name]
                                elif socket_client_message['action'] == 'registration' \
                                        and message_response['response'] == 400:
                                    byte_message = serialization_message(message_response)
                                    app_log_server.info(f'Пользователь не зарегестрирован!')
                                    socket_client_mes_name.send(byte_message)
                                elif socket_client_message['action'] == 'get_users' \
                                        and message_response['response'] == 200:
                                    user = socket_client_message['user']['user_login']
                                    message_response['users'] = self.database.get_users()
                                    byte_message = serialization_message(message_response)
                                    socket_client_mes_name.send(byte_message)
                                    app_log_server.info(f'Списко пользователей отправлен {user}')
                                elif socket_client_message['action'] == 'get_statistics' \
                                        and message_response['response'] == 200:
                                    byte_message = serialization_message(message_response)
                                    socket_client_mes_name.send(byte_message)
                                    app_log_server.info(f'Статистика отправлена')
                                elif socket_client_message['action'] == 'authorization' \
                                        and message_response['response'] == 401:
                                    user = socket_client_message['user']['user_login']
                                    byte_message = serialization_message(message_response)
                                    app_log_server.info(f'Пользователь {user} не авторизирован!')
                                    socket_client_mes_name.send(byte_message)
                                elif socket_client_message['action'] == 'quit' \
                                        and message_response['response'] == 200:
                                    user = socket_client_message['user']['user_login']
                                    self.database.logout(user)
                                    byte_message = serialization_message(message_response)
                                    app_log_server.info(f'Пользователь {user} вышел!')
                                    socket_client_mes_name.send(byte_message)
                                    socket_client_mes_name.close()
                                    self.clients.remove(socket_client_mes_name)
                                    del self.name[socket_client_mes_name]
                                elif socket_client_message['action'] == 'get_contacts' \
                                        and message_response['response'] == 202:
                                    user = socket_client_message['user']['user_login']
                                    id_list_contacts = self.database.get_contacts(user)
                                    message_response['alert'] = id_list_contacts
                                    byte_message = serialization_message(message_response)
                                    app_log_server.info(
                                        f'Контакты пользователя {user} готовы!')
                                    socket_client_mes_name.send(byte_message)
                                elif socket_client_message['action'] == 'get_messages_users' \
                                        and message_response['response'] == 202:
                                    user = socket_client_message['user']['user_login']
                                    list_messages_user = self.database.get_history_message_user(user)
                                    message_response['alert'] = list_messages_user
                                    byte_message = serialization_message(message_response)
                                    app_log_server.info(
                                        f'Сообщения пользователя {user} готовы!')
                                    socket_client_mes_name.send(byte_message)
                                elif socket_client_message['action'] == 'add_contact' \
                                        and message_response['response'] == 200:
                                    byte_message = serialization_message(message_response)
                                    user = socket_client_message['user']['user_login']
                                    contact = socket_client_message['user_id']
                                    self.database.add_contact(user, contact)
                                    app_log_server.info(
                                        f'Добавлен новый контакт пользователю {user}')
                                    socket_client_mes_name.send(byte_message)
                                elif socket_client_message['action'] == 'del_contact' \
                                        and message_response['response'] == 200:
                                    user = socket_client_message['user']['user_login']
                                    contact = socket_client_message['user_id']
                                    self.database.del_contact(user, contact)
                                    byte_message = serialization_message(message_response)
                                    app_log_server.info(f'Удален контакт пользователю {user}')
                                    socket_client_mes_name.send(byte_message)
                                elif socket_client_message['action'] == 'add_contact' \
                                        and message_response['response'] == 400:
                                    byte_message = serialization_message(message_response)
                                    socket_client_mes_name.send(byte_message)
                                elif socket_client_message['action'] == 'del_contact' \
                                        and message_response['response'] == 400:
                                    byte_message = serialization_message(message_response)
                                    socket_client_mes_name.send(byte_message)
                                elif message_response == 'Error':
                                    msg = {
                                        "response": 200,
                                        'user_name': socket_client_message['user']['user_login'],
                                        'alert': 'Сообщение доставлено',
                                        'to': socket_client_message['to'],
                                        'message': socket_client_message['mess_text']
                                    }
                                    byte_message = serialization_message(msg)
                                    socket_client_mes_name.send(byte_message)
                                    self.database.add_history_message(socket_client_message['user']['user_login'],
                                                                      socket_client_message['to'],
                                                                      socket_client_message['mess_text'])
                                time.sleep(1)
                        except Exception:
                            app_log_server.info(f'Клиент {socket_client_mes_name.fileno()} {socket_client_mes_name.getpeername()} '
                                                f'отключился (отправка)')
                            socket_client_mes_name.close()
                            self.clients.remove(socket_client_mes_name)
                            del self.name[socket_client_mes_name]

    def message_processing(self, message, database, sock):
        """Принимаем сообщение от клиента и обрабатываем его"""

        user_login = message['user']['user_login']

        # если пользователь отправил обычное сообщение
        if 'action' in message and message['action'] == 'presence' and 'time' in message and 'user' in message and \
                'user_login' in message['user'] and database.check_login(user_login) and 'token' in message['user'] and \
                database.check_authorized(user_login, message['user']['token']) and 'mess_text' in message and \
                'to' in message:

            for key, value in self.name.items():
                if value == message['to'] and database.check_login(message['to']):
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
                    byte_message = serialization_message(msg_to)
                    key.send(byte_message)
                    byte_message = serialization_message(msg_from)
                    sock.send(byte_message)
                    app_log_server.info('Сообщение принято. Ответ 200')
                    database.add_history_message(user_login, message['to'], message['mess_text'])
                    return 'Ok'
            return 'Error'

        # если администратор хочет получить информацию о пользователях
        elif 'action' in message and message['action'] == 'get_users' and 'time' in message and 'user' in message and \
                'user_login' in message['user'] and database.check_login(user_login) and 'token' in message['user'] and \
                database.check_authorized(user_login, message['user']['token']) and database.check_admin(user_login):
            return {'response': 200, 'user_name': user_login, 'alert': 'Список пользователей отправлен'}

        # если пользователь хочет получить сообщения пользователя
        elif 'action' in message and message['action'] == 'get_messages_users' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'token' in message['user'] and \
                database.check_authorized(user_login, message['user']['token']):
            return {'response': 202, 'alert': None}

        # если пользователь отправил сообщение, но пользователь не авторизован
        elif 'action' in message and message['action'] == 'presence' and 'time' in message and 'user' in message and \
                'user_login' in message['user'] and 'token' in message['user'] and not \
                database.check_authorized(user_login, message['user']['token']) and message['mess_text']:
            app_log_server.info('Сообщение отклонено. Ответ 400')
            return {'response': 302, 'user_name': user_login, 'message': 'Пользователь не авторизирован',
                    'alert': 'Сообщение отклонено'}

        # если пользователь отправил сообщения для авторизации
        elif 'action' in message and message['action'] == 'authorization' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'user_password' in message['user'] and \
                database.check_authenticated(user_login, message['user']['user_password']):
            user_role = database.get_user_role(user_login)
            if user_role == 'Администратор':
                history_obj = database.get_history_users()
                history_message = []
            else:
                history_obj = []
                history_message = database.get_history_message_user(user_login)
            return {'response': 200, 'user_name': user_login, 'token': '', 'alert': 'Успешная авторизация',
                    'role': user_role, 'users': history_obj, 'users_message': history_message}

        # если пользователь отправил сообщение для регистрации
        elif 'action' in message and message['action'] == 'registration' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'user_password' in message['user']:
            password_hash = database.hash_password(message['user']['user_password'])
            database.register(message['user']['user_login'], password_hash)
            return {'response': 200, 'user_name': user_login, 'alert': 'Успешная регистрация'}

        # если пользователь отправил сообщение для регистрации, но данные не валидны
        # elif 'action' in message and message['action'] == 'registration' and 'time' in message and \
        #         'user' in message and 'user_login' in message['user'] and 'user_password' in message['user']:
        #     password_hash = database.hash_password(message['user']['password'])
        #     database.register(message['user']['user_login'], password_hash)
        #     return {'response': 400, 'user_name': user_login, 'alert': 'Регистрация не удалась'}

        # если пользователь отправил сообщение на получение статистики определенного пользователя
        elif 'action' in message and message['action'] == 'get_statistics' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'token' in message['user'] and \
                database.check_authorized(user_login, message['user']['token']):
            user_role = database.get_user_role(user_login)
            if user_role == 'Администратор':
                history_obj = database.get_history_user(message['statistic'])
            else:
                history_obj = ''
            return {'response': 200, 'user_name': user_login, 'token': '', 'alert': 'Статистика отправлена',
                    'role': user_role,
                    'user_history': {
                        'create_at': history_obj.create_at.strftime("%Y-%m-%d %H:%M:%S"), 'login': history_obj.login, 'id': history_obj.id, 'ip': history_obj.ip_address
                    }
                }

        # если пользователь отправил сообщения для авторизации, но данные неверные
        elif 'action' in message and message['action'] == 'authorization' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'user_password' in message['user'] and not \
                database.check_authenticated(user_login, message['user']['user_password']):
            return {'response': 401, 'user_name': user_login, 'alert': 'Авторизация не удалась'}

        # если пользователь отправил сообщение для выхода из аккаунта
        elif 'action' in message and message['action'] == 'quit' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'token' in message['user'] and \
                database.check_authorized(user_login, message['user']['token']):
            return {'response': 200, 'user_name': user_login, 'alert': 'Пользователь вышел'}

        # если пользователь отправил сообщение для выхода из аккаунта, но пользователь итак не авторизирован
        elif 'action' in message and message['action'] == 'quit' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'token' in message['user'] and not \
                database.check_authorized(user_login, message['user']['token']):
            return {'response': 302, 'user_name': user_login, 'alert': 'Пользователь не авторизован'}

        # если пользователь отправил сообщение на получение контактов
        elif 'action' in message and message['action'] == 'get_contacts' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'token' in message['user'] and \
                database.check_authorized(user_login, message['user']['token']):
            return {'response': 202, 'alert': None}

        # если пользователь отправил сообщение на получение контактов, но пользователь не авторизирован
        elif 'action' in message and message['action'] == 'get_contacts' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'token' in message['user'] and not \
                database.check_authorized(user_login, message['user']['token']):
            return {'response': 302, 'alert': None}

        # если пользователь отправил сообщение на добавление контакта
        elif 'action' in message and message['action'] == 'add_contact' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and \
                database.check_authorized(user_login, message['user']['token']) and 'user_id' in message and \
                message['user_id'] and database.check_login(message['user_id']):
            return {'response': 200, 'user_name': user_login, 'to_user': message['user_id'],
                    'alert': f'Пользователь добавлен в контакты'}

        # если пользователь отправил сообщение на добваление контакта, но контакта в базе нет
        elif 'action' in message and message['action'] == 'add_contact' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'token' in message['user'] and \
                database.check_authorized(user_login, message['user']['token']) and 'user_id' in message and \
                message['user_id'] and not database.check_login(message['user_id']):
            return {'response': 400, 'user_name': user_login, 'alert': 'Для добавления пользователь должен быть в базе'}

        # если пользователь отправил сообщение на удаление контакта
        elif 'action' in message and message['action'] == 'del_contact' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'token' in message['user'] and \
                database.check_authorized(user_login, message['user']['token']) and 'user_id' in message and \
                message['user_id'] and database.check_login(message['user_id']):
            return {'response': 200, 'user_name': user_login, 'to_user': message['user_id'],
                    'alert': f'Пользователь удален из контактов'}

        # если пользователь отправил сообщение на удаление контакта, но контакта в базе нет
        elif 'action' in message and message['action'] == 'del_contact' and 'time' in message and \
                'user' in message and 'user_login' in message['user'] and 'token' in message['user'] and \
                database.check_authorized(user_login, message['user']['token']) and 'user_id' in message and \
                message['user_id'] and not database.check_login(message['user_id']):
            return {'response': 400, 'user_name': user_login, 'alert': 'Для удаления пользователь должен быть в базе'}

        # любое другое сообщение
        else:
            app_log_server.info('Сообщение отклонено. Ответ 400')
            return {'response': 400, 'user_name': user_login, 'message': 'Неверный формат сообщения',
                    'alert': 'Сообщение отклонено'}


def main():
    addr, port = install_param_in_socket_server()

    obj_server = Server(addr, port, 10, ServerStorage())
    obj_server.get_and_send_message()


if __name__ == '__main__':
    main()
