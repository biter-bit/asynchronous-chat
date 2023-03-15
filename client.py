from utils import init_socket_tcp, serialization_message, deserialization_message, sys_param_reboot
from decorators import log
import datetime, logging, sys
from log import client_log_config

app_log_client = logging.getLogger('client')


@log
def create_message():
    """Создаем сообщение для отправки на сервер."""
    msg = {
        "action": 'presence',
        'time': datetime.datetime.now().strftime('%d.%m.%Y'),
        'user': {
            'account_name': 'Michael',
        }
    }
    app_log_client.info('Сообщение создано')
    return msg


def install_param_in_socket_client():
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
        app_log_client.info('Параметры сокета успешно заданы')
        return addr, port
    except Exception as error:
        app_log_client.error('Параметр задан неверно')
        name_error = 'Ошибка'
        return error, name_error


def main():
    server = init_socket_tcp()
    app_log_client.info('Сокет инициализирован')
    addr, port = install_param_in_socket_client()
    server.connect((addr, port))

    msg = create_message()
    byte_msg = serialization_message(msg)
    app_log_client.info('Сообщение сериализовано')
    server.send(byte_msg)

    data = server.recv(1024)
    message = deserialization_message(data)
    app_log_client.info('Сообщение десериализовано')
    app_log_client.info('Ответ получен. %s %s', message['response'], message['alert'])


if __name__ == '__main__':
    main()