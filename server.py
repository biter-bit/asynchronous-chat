import time, json

from utils import serialization_message, deserialization_message_list, sys_param_reboot, token_create
import sys
import logging, select, socket
from log import server_log_config
from metaclasses import ServerVerifier
from descriptor import ServerCheckPort
from database import Session
from model import User, Contacts

app_log_server = logging.getLogger('server')
app_log_chat = logging.getLogger('chat')


def message_processing(message):
    """Принимаем сообщение от клиента и обрабатываем его"""
    # создаем сессию для работы с б.д.
    session = Session()

    # берем все логины пользователей из б.д.
    users_login_password = [(i.login, i.password) for i in session.query(User).all()]

    # берем обьект пользователя
    user = session.query(User).filter(User.login == message['user']['user_login']).first()

    # если пользователь отправил обычное сообщение
    if 'action' in message and message['action'] == 'presence' and 'time' in message and 'user' in message and \
            message['user']['user_login'] and message['user']['token'] and \
            message['user']['token'] == user.token and message['mess_text']:
        app_log_server.info('Сообщение принято. Ответ 200')
        return {'response': 200, 'user_name': message['user']['user_login'], 'message': message['mess_text'],
                'alert': 'Сообщение принято'}

    # если пользователь отправил сообщения для авторизации, но пользователя нет в базе
    elif 'action' in message and message['action'] == 'presence' and 'time' in message and 'user' in message and \
            message['user']['account_name'] and message['user']['token'] and \
            message['user']['token'] != user.token and message['mess_text']:
        app_log_server.info('Сообщение отклонено. Ответ 400')
        return {'response': 302, 'user_name': message['user']['account_name'],
                'message': 'Пользователь не авторизирован',
                'alert': 'Сообщение отклонено'}

    # если пользователь отправил сообщения для авторизации
    elif 'action' in message and message['action'] == 'authorization' and 'time' in message and \
            'user' in message and message['user']['user_login'] and message['user']['user_password'] and \
            (message['user']['user_login'], message['user']['user_password']) in users_login_password:
        user.authorized = True
        user.token = token_create()
        session.commit()
        return {'response': 200, 'user_name': message['user']['user_login'], 'token': user.token,
                'alert': 'Успешная авторизация'}

    # если пользователь отправил сообщение для выхода из аккаунта
    elif 'action' in message and message['action'] == 'quit' and 'time' in message and \
            'user' in message and message['user']['user_login'] and \
            message['user']['user_login'] == user.login:
        user.authorized = False
        user.token = None
        session.commit()
        session.close()
        return {'response': 200, 'user_name': message['user']['user_login'], 'alert': 'Пользователь вышел'}

    # если пользователь отправил сообщение на получение контактов
    elif 'action' in message and message['action'] == 'get_contacts' and 'time' in message and \
            'user' in message and message['user']['user_login'] and message['user']['user_login'] == user.login:
        client_id_contact = session.query(Contacts.client_id).join(User, Contacts.owner_id == User.id).filter(
            User.login == message['user']['user_login']).all()
        id_list_client = [str(i[0]) for i in client_id_contact]
        contacts = session.query(User.login).join(Contacts, Contacts.client_id == User.id).filter(
            Contacts.client_id.in_(id_list_client)).all()
        id_list_contacts = [str(i[0]) for i in contacts]
        return {'response': 202, 'alert': str(id_list_contacts)}

    # если пользователь удалил сообщение на получение контактов
    elif 'action' in message and message['action'] == 'add_contact' and 'time' in message and \
            'user' in message and message['user']['user_login'] and \
            message['user']['user_login'] == user.login and 'user_id' in message and message['user_id']:
        new_user = session.query(User).filter(User.login == message['user_id']).first()
        if new_user is None:
            return {'response': 400, 'user_name': message['user']['account_name'],
                    'message': 'Данного пользователя нет в базе', 'alert': 'Сообщение отклонено'}
        return {'response': 200, 'user_name': message['user']['user_login'],
                'alert': f'Пользователь добавлен в контакты'}

    elif 'action' in message and message['action'] == 'del_contact' and 'time' in message and \
            'user' in message and message['user']['user_login'] and \
            message['user']['user_login'] == user.login and 'user_id' in message and message['user_id']:
        new_user = session.query(User).filter(User.login == message['user_id']).first()
        user = session.query(User).filter(User.login == message['user']['user_login']).first()
        result = session.query(Contacts).filter(Contacts.owner_id == user.id and
                                                Contacts.client_id == new_user.id).first()
        if result is None:
            return {'response': 400, 'user_name': message['user']['account_name'],
                    'message': 'Данного пользователя нет в базе', 'alert': 'Сообщение отклонено'}
        session.delete(result)
        session.commit()
        session.close()
        return {'response': 200, 'user_name': message['user']['user_login'],
                'alert': f'Пользователь удален из контактов'}

    # любое другое сообщение
    else:
        app_log_server.info('Сообщение отклонено. Ответ 400')
        return {'response': 400, 'user_name': message['user']['account_name'],
                'message': 'Неверный формат сообщения',
                'alert': 'Сообщение отклонено'}


class Server(metaclass=ServerVerifier):
    port = ServerCheckPort()

    def __init__(self, addr, port, wait):
        self.sock = None
        self.addr = addr
        self.port = port
        self.clients = []
        self.r = []
        self.w = []
        self.e = []
        self.message_client = {}
        self.wait = wait

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

        # создаем сессию для работы с б.д.
        session = Session()

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
                        self.message_client[i] = decode_data_dict
                    except Exception:
                        app_log_server.info(f'Клиент {i.fileno()} {i.getpeername()} отключился (чтение)')
                        i.close()
                        self.clients.remove(i)

                if self.message_client:
                    for i in self.w:
                        for el in self.message_client:
                            try:
                                for mes in self.message_client[el]:
                                    message = message_processing(mes)
                                    byte_message = serialization_message(message)
                                    if mes['action'] == 'authorization' and message['response'] == 200:
                                        app_log_server.info(f'Пользователь {mes["user"]["user_login"]} авторизирован!')
                                        el.send(byte_message)
                                    elif mes['action'] == 'quit' and message['response'] == 200:
                                        app_log_server.info(f'Пользователь {mes["user"]["user_login"]} вышел!')
                                        el.send(byte_message)
                                        el.close()
                                        self.clients.remove(el)
                                    elif mes['action'] == 'get_contacts' and message['response'] == 202:
                                        app_log_server.info(
                                            f'Контакты пользователя {mes["user"]["user_login"]} готовы!')
                                        el.send(byte_message)
                                    elif mes['action'] == 'add_contact' and message['response'] == 200:
                                        new_user = session.query(User).filter(User.login == mes['user_id']).first()
                                        user = session.query(User).filter(User.login == mes['user']['user_login']).first()
                                        result = Contacts(owner_id=user.id, client_id=new_user.id)
                                        session.add(result)
                                        session.commit()
                                        session.close()
                                        app_log_server.info(
                                            f'Добавлен новый контакт пользователю {mes["user"]["user_login"]}')
                                        el.send(byte_message)
                                    elif mes['action'] == 'del_contact' and message['response'] == 200:
                                        app_log_server.info(f'Удален контакт пользователю {mes["user"]["user_login"]}')
                                        el.send(byte_message)
                                    else:
                                        app_log_chat.info(f"{message['user_name']} >> {message['message']}")
                                        i.send(byte_message)
                                    time.sleep(1)
                            except Exception:
                                app_log_server.info(f'Клиент {i.fileno()} {i.getpeername()} отключился (отправка)')
                                i.close()
                                self.clients.remove(i)


def install_param_in_socket_server():
    """Устанавливаем введенные пользователем параметры подключения к серверу/создания сервера"""
    param = sys.argv
    port = 10001
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


def main():
    addr, port = install_param_in_socket_server()

    obj_server = Server(addr, port, 10)
    obj_server.get_and_send_message()


if __name__ == '__main__':
    main()
