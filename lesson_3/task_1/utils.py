import sys, json, socket


def install_param_in_socket():
    """Устанавливаем введенные пользователем параметры подключения к серверу/создания сервера"""
    param = sys.argv
    port = 10002
    addr = 'localhost'
    try:
        for i in param:
            if i == '-p':
                port = int(param[param.index(i)+1])
            if i == '-a':
                addr = param[param.index(i)+1]
        sys_param_reboot()
        return addr, port
    except Exception as error:
        name_error = 'Ошибка'
        return error, name_error


def serialization_message(message):
    """Сериализуем сообщение"""
    js_msg = json.dumps(message)
    js_msg_encode = js_msg.encode('utf-8')
    return js_msg_encode


def deserialization_message(message):
    """Десериализация сообщения"""
    js_msg_decode = message.decode('utf-8')
    js_msg = json.loads(js_msg_decode)
    return js_msg


def init_socket_tcp():
    """Инициализация сокета"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return s


def sys_param_reboot():
    """Обновление параметров командной строки"""
    sys.argv = [sys.argv[0]]
    return sys.argv