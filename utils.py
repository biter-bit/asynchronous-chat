import sys, json, socket


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