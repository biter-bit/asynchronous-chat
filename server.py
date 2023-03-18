from utils import init_socket_tcp, serialization_message, deserialization_message, sys_param_reboot
import sys
import logging, select
from log import server_log_config


app_log_server = logging.getLogger('server')
app_log_chat = logging.getLogger('chat')


def message_processing(message):
    """Принимаем сообщение от клиента и обрабатываем его"""
    if 'action' in message and message['action'] == 'presence' and 'time' in message and 'user' in message and \
            message['user']['account_name'] and message['mess_text']:
        app_log_server.info('Сообщение принято. Ответ 200')
        return {'response': 200, 'user_name': message['user']['account_name'], 'message': message['mess_text'],
                'alert': 'Сообщение принято'}
    else:
        app_log_server.info('Сообщение отклонено. Ответ 400')
        return {'response': 400, 'user_name': message['user']['account_name'], 'message': 'Неверный формат сообщения',
                'alert': 'Сообщение отклонено'}


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
    server.settimeout(0.2)
    clients = []

    while True:
        try:
            client, client_addr = server.accept()
        except OSError as e:
            pass
        else:
            app_log_server.info('Получен запрос на соединение от %s', client_addr)
            clients.append(client)
        finally:
            wait = 10
            r = []
            w = []
            e = []
            try:
                r, w, e = select.select(clients, clients, clients, wait)
            except:
                pass

            message_client = {}

            for i in r:
                try:
                    data = i.recv(1024)
                    decode_data_dict = deserialization_message(data)
                    app_log_server.info('Сообщение десериализовано')
                    message_client[i] = decode_data_dict
                    app_log_server.info(f'Сообщение пользователя {i.fileno()} {i.getpeername()} десериализовано')
                    message = message_processing(message_client[i])
                    app_log_chat.info(f"{message['user_name']} >> {message['message']}")
                except Exception as e:
                    app_log_server.info(f'Клиент {i.fileno()} {i.getpeername()} отключился')
                    i.close()
                    clients.remove(i)

            if message_client:
                for i in w:
                    for el in message_client.keys():
                        if el == i:
                            continue
                        try:
                            message = message_processing(message_client[el])
                            byte_message = serialization_message(message)
                            app_log_server.info('Сообщение сериализовано')
                            i.send(byte_message)
                        except Exception:
                            app_log_server.info(f'Клиент {i.fileno()} {i.getpeername()} отключился')
                            i.close()
                            clients.remove(i)


if __name__ == '__main__':
    main()