import sys, json, socket, hashlib, logging, inspect
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import base64

app_log_client = logging.getLogger('client')


def encrypted_message_for_send_user(msg, public_key):
    resipient_key = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(resipient_key)
    encrypted_mes = cipher.encrypt(msg)
    return encrypted_mes

def generic_public_and_privat_key_client():
    """Генерируем публичный и приватный ключи для шифровки сообщения и возвращаем их в строковом формате"""
    key = RSA.generate(1024)
    PRIVAT_KEY = key.export_key().decode()
    PUBLIC_KEY = key.public_key().export_key().decode()
    return PRIVAT_KEY, PUBLIC_KEY

def generic_symmetric_key_client():
    """Фукнция генерирует симметричный ключ для шифровки сообщения. Возвращает его в строковом формате"""
    SYMMETRIC_KEY = get_random_bytes(16)
    return SYMMETRIC_KEY

def get_public_key(server, msg):
    """Сериализуем сообщение и отправляем запрос на получение публичного ключа сервера.
    Получаем и возвращаем публичный ключ сервера в строковом формате"""
    msg_json = serialization_message(msg)
    server.send(msg_json)
    data = server.recv(4096)
    message = deserialization_message(data)
    return message['public_key']

def encrypted_symmetric_key(message, sym_key):
    """
    Функция шифрует сообщение. Принимает сообщение и симметричный ключ в строковом виде. Возвращает шифрованное
    сообщение в бинарном виде
    :param message:
    :param sym_key:
    :return:
    """
    nonce = get_random_bytes(16)
    # создаем обьект с нашим симметричным ключом, который позволит зашифровать сообщение
    cipher_aes = AES.new(sym_key, AES.MODE_EAX, nonce)
    # шифруем наше сообщение, с помощью симметричного ключа
    crypt_mes, tag_mac = cipher_aes.encrypt_and_digest(message.encode())
    return crypt_mes

def encrypted_message(msg, public_key, symmetric_key, encrypted=1):
    # создаем обьект асимметричного ключа
    resipient_key = RSA.import_key(public_key)
    # создаем обьект с нашим асимметричным ключом, который позволит зашифровать симметричный ключ
    cipher = PKCS1_OAEP.new(resipient_key)
    # шифруем симметричный ключ алгоритмом PKCS1_OAEP
    encrypted_symmetric_key = cipher.encrypt(symmetric_key)

    # создаем контрольную сумму для нашего симметричного алгоритма шифрования
    nonce = get_random_bytes(16)
    # создаем обьект с нашим симметричным ключом, который позволит зашифровать сообщение
    cipher_aes = AES.new(symmetric_key, AES.MODE_EAX, nonce)
    # шифруем наше сообщение, с помощью симметричного ключа
    crypt_mes, tag_mac = cipher_aes.encrypt_and_digest(msg)
    # собираем наше сообщение для отправки
    encrypted_data = {
        'message': base64.b64encode(crypt_mes).decode('utf-8'),
        'symmetric_key': base64.b64encode(encrypted_symmetric_key).decode('utf-8'),
        'nonce': base64.b64encode(nonce).decode('utf-8')
    }
    # добавляем к нему тег, который позволит понять зашифровано сообщение или нет + сериализуем сообщение
    if encrypted == 1:
        encode_msg = 'ENCRYPTED:'.encode('utf-8') + serialization_message(encrypted_data)
    else:
        encode_msg = serialization_message(encrypted_data)

    return encode_msg

def decrypted_message(msg, privat_key, decrypt=1):
    if decrypt:
        des_mes = deserialization_message(msg)
    else:
        des_mes = msg
    resipient_key = RSA.import_key(privat_key)
    cipher = PKCS1_OAEP.new(resipient_key)
    decrypt_symmetric_key = cipher.decrypt(base64.b64decode(des_mes['symmetric_key']))
    cipher_aes = AES.new(decrypt_symmetric_key, AES.MODE_EAX, base64.b64decode(des_mes['nonce']))
    decrypt_mes = cipher_aes.decrypt(base64.b64decode(des_mes['message']))

    return decrypt_mes, decrypt_symmetric_key

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


def install_param_in_socket_client():
    """Устанавливаем введенные пользователем параметры подключения к серверу/создания сервера"""
    param = sys.argv
    port = 8002
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