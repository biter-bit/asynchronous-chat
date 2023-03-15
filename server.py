from utils import init_socket_tcp, serialization_message, deserialization_message, sys_param_reboot
import sys
import logging
from log import server_log_config


app_log_server = logging.getLogger('server')


def message_processing(message):
    """Принимаем сообщение от клиента и обрабатываем его"""
    if 'action' in message and message['action'] == 'presence' and 'time' in message and 'user' in message and \
            message['user']['account_name'] == 'Michael':
        app_log_server.info('Сообщение принято. Ответ 200')
        return {'response': 200, 'alert': 'Сообщение принято'}
    else:
        app_log_server.info('Сообщение отклонено. Ответ 400')
        return {'response': 400, 'alert': 'Сообщение отклонено'}


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


def main():

    server = init_socket_tcp()
    app_log_server.info('Сокет инициализирован')
    addr, port = install_param_in_socket_server()
    server.bind((addr, port))
    server.listen(5)

    while True:
        client, client_addr = server.accept()
        app_log_server.info('Получен запрос на соединение от %s', client_addr)
        # app_log_server.info(f'Получен запрос на соединение от {str(client_addr)}')

        data = client.recv(1024)
        decode_data_dict = deserialization_message(data)
        app_log_server.info('Сообщение десериализовано')

        message = message_processing(decode_data_dict)
        byte_message = serialization_message(message)
        app_log_server.info('Сообщение сериализовано')
        client.send(byte_message)
        client.close()


if __name__ == '__main__':
    main()