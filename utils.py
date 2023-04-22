import sys, json, socket, hashlib, logging, inspect


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
    dec_mes = message.decode('unicode_escape')
    return dec_mes


def replace_data_message(decode_mes):
    replace_data = decode_mes.replace('}{', '} , {')
    return replace_data


def split_message(replace_mes):
    split_data = replace_mes.split(' , ')
    return split_data


def deserialization_message_list(message):
    deserialize_list = []
    d_mes = decode_message(message)
    d_rep = replace_data_message(d_mes)
    result = d_rep.split(' , ')
    for i in result:
        deserialize_list.append(json.loads(i))
    return deserialize_list


def hashing_password(password):
    hash_obj = hashlib.sha256()
    hash_obj.update(password.encode())
    hash_code = hash_obj.digest().hex()
    return hash_code


def log(func):
    def wrapper(*args, **kwargs):
        LOGGER = logging.getLogger('client_front')
        if 'client_front.py' in sys.argv[0].split('/'):
            LOGGER = logging.getLogger('client_front')
        if 'server_back.py' in sys.argv[0].split('/'):
            LOGGER = logging.getLogger('server_back')
        LOGGER.info(f'Используется функция {func.__name__} с параметрами {args}, {kwargs}. '
                    f'Вызвана из функции {inspect.stack()[1][3]}')
        result = func(*args, **kwargs)
        LOGGER.info(f'Функция {func.__name__} выполнилась')
        return result
    return wrapper