import socket
from lesson_3.task_1.utils import install_param_in_socket, init_socket_tcp, serialization_message, deserialization_message
import json


def message_processing(message):
    """Принимаем сообщение от клиента и обрабатываем его"""
    if 'action' in message and message['action'] == 'presence' and 'time' in message and 'user' in message and \
            message['user']['account_name'] == 'Michael':
        return {'response': 200, 'alert': 'Сообщение принято'}
    else:
        return {'response': 400, 'alert': 'Сообщение отклонено'}


def main():

    server = init_socket_tcp()
    addr, port = install_param_in_socket()
    server.bind((addr, port))
    server.listen(5)

    while True:
        client, client_addr = server.accept()
        print(f'Получен запрос на соединение от {str(client_addr)}')

        data = client.recv(1024)
        decode_data_dict = deserialization_message(data)

        message = message_processing(decode_data_dict)
        byte_message = serialization_message(message)
        client.send(byte_message)
        client.close()


if __name__ == '__main__':
    main()