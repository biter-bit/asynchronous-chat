from utils import init_socket_tcp, serialization_message, deserialization_message, sys_param_reboot
from decorators import log
import datetime, logging, sys, json, threading, time
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
    port = 10003
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


def send_message(serv):
    user_name = input('Введите ваше имя >> ')
    while True:
        msg = create_message(input(''), user_name)
        byte_msg = serialization_message(msg)
        app_log_client.info('Сообщение сериализовано')
        serv.send(byte_msg)
        time.sleep(1)


def get_message(serv):
    while True:
        data = serv.recv(1024)
        list_message = deserialization_message_list(data)
        for i in list_message:
            app_log_client.info('Сообщение десериализовано')
            app_log_client.info('Ответ получен. %s %s', i['response'], i['alert'])
            print(f"{i['user_name']} >> {i['message']}")
        time.sleep(1)


def main():
    server = init_socket_tcp()
    app_log_client.info('Сокет инициализирован')
    addr, port = install_param_in_socket_client()
    server.connect((addr, port))

    t_send_message = threading.Thread(target=send_message, args=(server,), name='theard-1')
    t_send_message.start()

    t_get_message = threading.Thread(target=get_message, args=(server,), name='theard-2')
    t_get_message.start()


if __name__ == '__main__':
    main()