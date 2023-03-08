import socket
from lesson_3.task_1.utils import install_param_in_socket, init_socket_tcp, serialization_message, deserialization_message
import datetime
import json


def create_message():
    """Создаем сообщение для отправки на сервер."""
    msg = {
        "action": 'presence',
        'time': datetime.datetime.now().strftime('%d.%m.%Y'),
        'user': {
            'account_name': 'Michael',
        }
    }
    return msg


def main():
    server = init_socket_tcp()
    addr, port = install_param_in_socket()
    server.connect((addr, port))

    msg = create_message()
    byte_msg = serialization_message(msg)
    server.send(byte_msg)

    data = server.recv(1024)
    message = deserialization_message(data)
    print(message['response'], message['alert'])


if __name__ == '__main__':
    main()