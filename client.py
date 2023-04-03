from utils import init_socket_tcp, serialization_message, sys_param_reboot, deserialization_message_list
from decorators import log
import datetime, logging, sys, json, threading, time, socket
from log import client_log_config
from metaclasses import ClientVerifier

app_log_client = logging.getLogger('client')


class ClientSender(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def send_message(self):
        while True:
            message = input()
            msg = {
                "action": 'presence',
                'time': datetime.datetime.now().strftime('%d.%m.%Y'),
                'user': {
                    'account_name': self.account_name,
                },
                'mess_text': message
            }
            app_log_client.info('Сообщение создано')
            byte_msg = serialization_message(msg)
            app_log_client.info('Сообщение сериализовано')
            self.sock.send(byte_msg)
            time.sleep(1)

    def run(self):
        self.send_message()


class ClientRecipient(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, sock):
        self.sock = sock
        super().__init__()

    def get_message(self):
        while True:
            data = self.sock.recv(1024)
            list_message = deserialization_message_list(data)
            for i in list_message:
                app_log_client.info('Сообщение десериализовано')
                app_log_client.info('Ответ получен. %s %s', i['response'], i['alert'])
                print(f"{i['user_name']} >> {i['message']}")
            time.sleep(1)

    def run(self):
        self.get_message()


def install_param_in_socket_client():
    """Устанавливаем введенные пользователем параметры подключения к серверу/создания сервера"""
    param = sys.argv
    port = 10005
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


def main():
    # инициализируем сокет
    server = init_socket_tcp()
    print('Консольный мессенджер')
    app_log_client.info('Сокет инициализирован')

    # берем параметры для подключения к серверу, переданные при запуске сервера
    addr, port = install_param_in_socket_client()

    # подключаемся к серверу
    server.connect((addr, port))
    app_log_client.info(f'Установлено соединение с сервером. Ответ сервера: 200')

    # создаем имя пользователя
    name_accaunt = input('Введите имя пользователя: ')

    # создаем поток отправки сообщения от сервера
    client_sender = ClientSender(name_accaunt, server)
    client_sender.start()

    # создаем поток принятия сообщения от сервера
    client_recipient = ClientRecipient(server)
    client_recipient.start()


# вызываем функцию main() при запуске кода
if __name__ == '__main__':
    main()