from utils import init_socket_tcp, serialization_message, sys_param_reboot, deserialization_message_list
import datetime, logging, sys, json, threading, time
from metaclasses import ClientVerifier
from client_database.crud import ClientStorage
from client_database.model import History, Contacts
from log.log_client import client_log_config

app_log_client = logging.getLogger('client')


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

    def send_message(self):
        self.print_help()
        while True:
            message = input()
            if message == '/quit':
                msg = create_message_logout(self.account_name, self.token)
                app_log_client.info('Сообщение создано')
                byte_msg = serialization_message(msg)
                app_log_client.info('Сообщение сериализовано')
                self.sock.send(byte_msg)
                self.stop()
            elif message == '/contacts':
                result = self.database.get_contacts()
                print(result)
            elif message == '/add_contact':
                nickname = input('Никнейм пользователя, который хотите добавить в список контактов >> ')
                msg = create_message_add_contact(nickname, self.account_name, self.token)
                app_log_client.info('Сообщение создано')
                byte_msg = serialization_message(msg)
                app_log_client.info('Сообщение сериализовано')
                self.sock.send(byte_msg)
            elif message == '/del_contact':
                nickname = input('Никнейм пользователя, который хотите удалить из контактов >> ')
                msg = create_message_del_contact(nickname, self.account_name, self.token)
                app_log_client.info('Сообщение создано')
                byte_msg = serialization_message(msg)
                app_log_client.info('Сообщение сериализовано')
                self.sock.send(byte_msg)
            elif message == '/help':
                self.print_help()
            elif message == '/message':
                to = input('Введите получателя >> ')
                mes = input('Введите сообщение >> ')
                msg = create_message_text(message=mes, account_name=self.account_name, token=self.token, to=to)
                app_log_client.info('Сообщение создано')
                byte_msg = serialization_message(msg)
                app_log_client.info('Сообщение сериализовано')
                self.sock.send(byte_msg)
            elif message == '/get_users':
                msg = create_message_get_users(self.account_name, token=self.token)
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
        self.send_message()

    def stop(self):
        self._stop_event.set()


class ClientRecipient(threading.Thread, metaclass=ClientVerifier):
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
                self.stop()
            elif 'user_name' in i and i['user_name'] != self.account_name:
                self.database.add_message(i['user_name'], i['from'], i['alert'])
                print(f"{i['user_name']} >> {i['alert']}")
                time.sleep(1)
            elif i['response'] == 200 and i['alert'] == 'Сообщение доставлено':
                self.database.add_message(i['user_name'], i['to'], i['message'])
                print(i['alert'])
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
        time.sleep(1)

    def run(self):
        while not self._stop_event.is_set():
            self.get_message()

    def stop(self):
        self._stop_event.set()


def authorization_user(server):
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


def install_param_in_socket_client():
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
    return 'Ok'


def main():
    # инициализируем сокет
    print('Консольный мессенджер')

    # берем параметры для подключения к серверу, переданные при запуске сервера
    addr, port = install_param_in_socket_client()

    # инициализируем сокет
    server = init_socket_tcp()
    app_log_client.info('Сокет инициализирован')

    # подключаемся к серверу
    app_log_client.info('Подключение к серверу...')
    server.connect((addr, port))

    # авторизация пользователя
    data = authorization_user(server)

    # инициализация базы данных
    database = ClientStorage(data['name_account'])
    database_load(server, database, data['name_account'], data['token'])

    # создаем поток отправки сообщения от сервера
    client_sender = ClientSender(server, data['name_account'], data['token'], database)
    client_sender.daemon = True
    client_sender.start()

    # создаем поток принятия сообщения от сервера
    client_recipient = ClientRecipient(server, data['name_account'], database)
    client_recipient.daemon = True
    client_recipient.start()
    app_log_client.debug('Запущены процессы')

    while True:
        time.sleep(1)
        if client_recipient.is_alive() and client_sender.is_alive():
            continue
        break


# вызываем функцию main() при запуске кода
if __name__ == '__main__':
    main()
