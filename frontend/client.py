from utils import init_socket_tcp, deserialization_message, serialization_message, sys_param_reboot, \
    deserialization_message_list
import datetime, logging, sys, json, threading, time
from metaclasses import ClientVerifier
from frontend.client_database.crud import ClientStorage
from PyQt5.QtCore import QObject, pyqtSignal, QThread

app_log_client = logging.getLogger('client')


def create_message_get_message_users(login, token):
    msg = {
        'action': 'get_messages_users',
        'time': datetime.datetime.now().strftime('%d.%m.%Y'),
        'user': {
            'user_login': login,
            'token': token
        }
    }
    return msg

def create_message_registration(login, password):
    msg = {
        'action': 'registration',
        'time': datetime.datetime.now().strftime('%d.%m.%Y'),
        'user': {
            'user_login': login,
            'user_password': password
        }
    }
    return msg


def create_message_get_statistics(account_name, token, stat):
    msg = {
        "action": 'get_statistics',
        'time': datetime.datetime.now().strftime('%d.%m.%Y'),
        'user': {
            'user_login': account_name,
            'token': token
        },
        'statistic': stat
    }
    return msg


def create_message_get_users(account_name, token):
    msg = {
        "action": 'get_users',
        'time': datetime.datetime.now().strftime('%d.%m.%Y'),
        'user': {
            'user_login': account_name,
            'token': token
        },
    }
    return msg


def create_message_text(account_name='', message='', token='', to=''):
    msg = {
        "action": 'presence',
        'time': datetime.datetime.now().strftime('%d.%m.%Y'),
        'user': {
            'user_login': account_name,
            'token': token
        },
        'mess_text': message,
        'to': to
    }
    return msg


def create_message_authorized(login, password):
    msg = {
        'action': 'authorization',
        'time': datetime.datetime.now().strftime('%d.%m.%Y'),
        'user': {
            'user_login': login,
            'user_password': password
        }
    }
    return msg


def create_message_logout(login, token):
    msg = {
        'action': 'quit',
        'time': datetime.datetime.now().strftime('%d.%m.%Y'),
        'user': {
            'user_login': login,
            'token': token
        }
    }
    return msg


def create_message_get_contacts(login, token):
    msg = {
        'action': 'get_contacts',
        'time': datetime.datetime.now().strftime('%d.%m.%Y'),
        'user': {
            'user_login': login,
            'token': token
        }
    }
    return msg


def create_message_add_contact(nickname, login, token):
    msg = {
        'action': 'add_contact',
        'user_id': nickname,
        'time': datetime.datetime.now().strftime('%d.%m.%Y'),
        'user': {
            'user_login': login,
            'token': token
        }
    }
    return msg


def create_message_del_contact(nickname, login, token):
    msg = {
        'action': 'del_contact',
        'user_id': nickname,
        'time': datetime.datetime.now().strftime('%d.%m.%Y'),
        'user': {
            'user_login': login,
            'token': token
        }
    }
    return msg


class ClientSender(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, sock, account_name, token, database):
        self.database = database
        self.sock = sock
        self.account_name = account_name
        self.token = token
        super().__init__()
        self._stop_event = threading.Event()

    def send_message(self, message):
        # self.print_help()
        if message['request'] == '/quit':
            msg = create_message_logout(self.account_name, self.token)
            app_log_client.info('Сообщение создано')
            byte_msg = serialization_message(msg)
            app_log_client.info('Сообщение сериализовано')
            self.sock.send(byte_msg)
            self.stop()
        elif message['request'] == '/registration':
            msg = create_message_registration(message['login'], message['password'])
            app_log_client.info('Сообщение создано')
            byte_msg = serialization_message(msg)
            app_log_client.info('Сообщение сериализовано')
            self.sock.send(byte_msg)
        # elif message == '/contacts':
        #     result = self.database.get_contacts()
        #     print(result)
        # elif message == '/add_contact':
        #     nickname = input('Никнейм пользователя, который хотите добавить в список контактов >> ')
        #     msg = create_message_add_contact(nickname, self.account_name, self.token)
        #     app_log_client.info('Сообщение создано')
        #     byte_msg = serialization_message(msg)
        #     app_log_client.info('Сообщение сериализовано')
        #     self.sock.send(byte_msg)
        # elif message == '/del_contact':
        #     nickname = input('Никнейм пользователя, который хотите удалить из контактов >> ')
        #     msg = create_message_del_contact(nickname, self.account_name, self.token)
        #     app_log_client.info('Сообщение создано')
        #     byte_msg = serialization_message(msg)
        #     app_log_client.info('Сообщение сериализовано')
        #     self.sock.send(byte_msg)
        # elif message == '/help':
        #     self.print_help()
        elif message['request'] == '/message':
            msg = create_message_text(message=message['message'], account_name=self.account_name, token=self.token, to=message['to'])
            app_log_client.info('Сообщение создано')
            byte_msg = serialization_message(msg)
            app_log_client.info('Сообщение сериализовано')
            self.sock.send(byte_msg)
        # elif message == '/get_users':
        #     msg = create_message_get_users(self.account_name, token=self.token)
        #     app_log_client.info('Сообщение создано')
        #     byte_msg = serialization_message(msg)
        #     app_log_client.info('Сообщение сериализовано')
        #     self.sock.send(byte_msg)
        elif message['request'] == '/get_statistics':
            msg = create_message_get_statistics(account_name=self.account_name, token=self.token, stat=message['args'].text())
            app_log_client.info('Сообщение создано')
            byte_msg = serialization_message(msg)
            app_log_client.info('Сообщение сериализовано')
            self.sock.send(byte_msg)
        else:
            self.print_help()

    def print_help(self):
        print('\n')
        print('Поддерживаемые команды:', end='\n\n')
        print('/message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('/add_contact - добавить пользователя в список контактов')
        print('/del_contact - удалить пользователя из списка контактов')
        print('/contacts - список контактов')
        print('/help - вывести подсказки по командам')
        print('/quit - выход из программы')

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
            app_log_client.info('Сообщение десериализовано')
            app_log_client.info('Ответ получен. %s %s', i['response'], i['alert'])
            if i['response'] == 200 and i['alert'] == 'Пользователь вышел':
                app_log_client.info(f'Пользователь {self.account_name} вышел')
                print('Пока!')
                self.message_received.emit('quit')
                self.stop()
            elif 'user_name' in i and i['user_name'] != self.account_name:
                self.database.add_message(i['user_name'], i['from'], i['alert'])
                self.message_user_received.emit('delivered')
            elif i['response'] == 200 and i['alert'] == 'Сообщение доставлено':
                self.database.add_message(i['user_name'], i['to'], i['message'])
                self.message_user_received.emit('delivered')
            elif i['response'] == 200 and i['alert'] == 'Пользователь добавлен в контакты':
                self.database.add_contact(i['to_user'])
                print(i['alert'])
            elif i['response'] == 200 and i['alert'] == 'Пользователь удален из контактов':
                self.database.del_contact(i['to_user'])
                print(i['alert'])
            elif i['response'] == 400 and i['alert'] == 'Для добавления пользователь должен быть в базе':
                print(i['alert'])
            elif i['response'] == 400 and i['alert'] == 'Для удаления пользователь должен быть в базе':
                print(i['alert'])
            elif i['response'] == 200 and i['alert'] == 'Список пользователей отправлен':
                print(str(i['users']))
                # self.message_received.emit('quit')
            elif i['response'] == 200 and i['alert'] == 'Статистика отправлена':
                print(str(i['user_history']))
                result = json.dumps(i['user_history'])
                self.create_users_signal.emit(result)
            elif i['response'] == 200 and i['alert'] == 'Успешная регистрация':
                print(i['alert'])
                self.register_signal.emit('Ok')
        time.sleep(1)

    def run(self):
        while not self._stop_event.is_set():
            self.get_message()

    def stop(self):
        self._stop_event.set()


def authorization_user_console(server):
    print('Авторизация аккаунта')
    response = 0
    addr, port = server.getsockname()
    result_data = {
        'name_account': '',
        'password': '',
        'token': ''
    }
    try:
        while response == 0:
            result_data['name_account'] = input('Введите имя пользователя: ')
            result_data['password'] = input('Введите пароль: ')

            # создаем сообщение и отправляем серверу
            msg = create_message_authorized(result_data['name_account'], result_data['password'])
            msg_json = serialization_message(msg)
            server.send(msg_json)

            # получаем сообщение сервера
            data = server.recv(1024)
            list_message = deserialization_message_list(data)
            for i in list_message:
                if i['response'] == 200:
                    app_log_client.info(f'Установлено соединение с сервером. Ответ сервера: {i["response"]}')
                    response = i['response']
                    result_data['token'] = i['token']
                    print('Установлено соединение с сервером.')
                    app_log_client.info(f'Запущен клиент с параметрами: адрес сервера: {addr}, порт: {port}, '
                                        f'имя пользователя: {result_data["name_account"]}')
                elif i['response'] == 401:
                    print('Неправильный логин или пароль. Попробуйте еще раз.')
                    app_log_client.info(f'Соединение с сервером не установлено. Ответ сервера: {response}')
        return result_data
    except json.JSONDecodeError:
        app_log_client.error('Не удалось декодировать полученную Json строку.')
        exit(1)
    except Exception as er:
        app_log_client.error('Не удалось подключиться к серверу')
        exit(1)


def registration_user_pyqt5(server, login, password):
    print('Регистрация аккаунта')
    addr, port = server.getsockname()
    msg = create_message_registration(login, password)
    msg_json = serialization_message(msg)
    server.send(msg_json)

    # получаем сообщение сервера
    data = server.recv(4096)

    message = deserialization_message(data)

    if message['response'] == 200:
        app_log_client.info(f'Установлено соединение с сервером. Ответ сервера: {message["response"]}')
        print('Регистрация прошла успешно')
        server.close()
        return 'Ok'

    else:
        server.close()
        return 'Error'


def authorization_user_pyqt5(server, login, password):
    print('Авторизация аккаунта')
    addr, port = server.getsockname()
    result_data = {
        'name_account': '',
        'password': '',
        'token': ''
    }
    try:
        result_data['name_account'] = login
        result_data['password'] = password

        # создаем сообщение и отправляем серверу
        msg = create_message_authorized(result_data['name_account'], result_data['password'])
        msg_json = serialization_message(msg)
        server.send(msg_json)

        # получаем сообщение сервера
        data = server.recv(4096)

        message = deserialization_message(data)
        if 'role' in message and message['role'] == 'Администратор' and message['response'] == 200:
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
        elif message['response'] == 401:
            print('Неправильный логин или пароль. Попробуйте еще раз.')
            app_log_client.info(f'Соединение с сервером не установлено. Ответ сервера: {message["response"]}')
            return result_data
    except json.JSONDecodeError:
        app_log_client.error('Не удалось декодировать полученную Json строку.')
        exit(1)
    except Exception as er:
        app_log_client.error('Не удалось подключиться к серверу')
        exit(1)


def install_param_in_socket_client():
    """Устанавливаем введенные пользователем параметры подключения к серверу/создания сервера"""
    param = sys.argv
    port = 10002
    addr = '10.0.2.15'
    try:
        for i in param:
            if i == '-p':
                port = int(param[param.index(i) + 1])
            if i == '-a':
                addr = param[param.index(i) + 1]
        sys_param_reboot()
        app_log_client.info('Параметры сокета успешно заданы')
        return addr, port
    except Exception as error:
        app_log_client.error('Параметр задан неверно')
        name_error = 'Ошибка'
        return error, name_error


def database_load(sock, database, user_login, token):
    # создаем сообщение запроса
    msg = create_message_get_contacts(user_login, token)
    app_log_client.info('Сообщение создано')

    # сериализуем сообщение для отправки и отправляем
    byte_msg = serialization_message(msg)
    app_log_client.info('Сообщение сериализовано')
    sock.send(byte_msg)

    # получаем сообщение от сервера и добавляем контакты в б.д.
    data = sock.recv(4096)
    list_message = deserialization_message_list(data)
    app_log_client.info('Сообщение десериализовано')
    for i in list_message:
        app_log_client.info('Ответ получен. %s %s', i['response'], i['alert'])
        if i['response'] == 202:
            database.add_contacts(i['alert'])

    # создаем сообщение запроса
    msg = create_message_get_message_users(user_login, token)
    app_log_client.info('Сообщение создано')

    # сериализуем сообщение для отправки и отправляем
    byte_msg = serialization_message(msg)
    app_log_client.info('Сообщение сериализовано')
    sock.send(byte_msg)

    # получаем сообщение от сервера и добавляем сообщения пользователя в б.д.
    data = sock.recv(4096)
    list_message = deserialization_message_list(data)
    app_log_client.info('Сообщение десериализовано')
    for i in list_message:
        app_log_client.info('Ответ получен. %s %s', i['response'], i['alert'])
        if i['response'] == 202:
            database.add_messages(i['alert'])

    return 'Ok'


def init_database(data, server):
    database = ClientStorage(data['name_account'])
    database_load(server, database, data['name_account'], data['token'])
    return database


def start_thread_client_send(data, server, database):
    client_sender = ClientSender(server, data['name_account'], data['token'], database)
    client_sender.daemon = True
    client_sender.start()
    return client_sender


def start_thread_client_recipient(data, server, database):
    client_recipient = ClientRecipient(server, data['name_account'], database)
    client_recipient.daemon = True
    client_recipient.start()
    app_log_client.debug('Запущены процессы')
    return client_recipient


def connect_server():
    addr, port = install_param_in_socket_client()

    # инициализируем сокет
    server = init_socket_tcp()
    app_log_client.info('Сокет инициализирован')

    # подключаемся к серверу
    app_log_client.info('Подключение к серверу...')
    server.connect((addr, port))
    return server


def main():
    # инициализируем сокет
    print('Консольный мессенджер')

    # подключаемся к серверу
    server = connect_server()

    # авторизация пользователя
    data = authorization_user_console(server)

    # инициализация базы данных
    database = init_database(data, server)

    # создаем поток отправки сообщения от сервера
    client_sender = start_thread_client_send(data, server, database)

    # создаем поток принятия сообщения от сервера
    client_recipient = start_thread_client_recipient(data, server, database)

    while True:
        time.sleep(1)
        if client_recipient.is_alive() and client_sender.is_alive():
            continue
        break


# вызываем функцию main() при запуске кода
if __name__ == '__main__':
    main()
