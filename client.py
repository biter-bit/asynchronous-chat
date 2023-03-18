from utils import init_socket_tcp, serialization_message, deserialization_message, sys_param_reboot
from decorators import log
import datetime, logging, sys, json
from log import client_log_config

app_log_client = logging.getLogger('client')


@log
def create_message(message, user_name):
    """Создаем сообщение для отправки на сервер."""
    msg = {
        "action": 'presence',
        'time': datetime.datetime.now().strftime('%d.%m.%Y'),
        'user': {
            'account_name': user_name,
        },
        'mess_text': message
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


def decode_message(message):
    dec_mes = message.decode('utf-8')
    return dec_mes


def replace_data_message(decode_mes):
    replace_data = decode_mes.replace('}{', '} , {')
    return replace_data


def split_message(replace_mes):
    split_data = replace_mes.split(' , ')
    return split_data


def deserialization_message_list(message):
    list_deserialization_message = []
    d_mes = decode_message(message)
    r_mes = replace_data_message(d_mes)
    s_mes = split_message(r_mes)
    for i in s_mes:
        list_deserialization_message.append(json.loads(i))
    return list_deserialization_message


def main():
    server = init_socket_tcp()
    app_log_client.info('Сокет инициализирован')
    addr, port = install_param_in_socket_client()
    server.connect((addr, port))

    while True:
        msg = input('Отправляем или принимаем сообщение? (w - отправляем, r - принимаем) >> ')
        if msg == 'exit':
            break
        if msg == 'r':
            data = server.recv(1024)
            list_message = deserialization_message_list(data)
            for i in list_message:
                app_log_client.info('Сообщение десериализовано')
                app_log_client.info('Ответ получен. %s %s', i['response'], i['alert'])
                print(f"{i['user_name']} >> {i['message']}")
        if msg == 'w':
            msg = create_message(input('>> '), 'Michael')
            byte_msg = serialization_message(msg)
            app_log_client.info('Сообщение сериализовано')
            server.send(byte_msg)


if __name__ == '__main__':
    main()