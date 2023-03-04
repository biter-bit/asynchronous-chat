import sys, datetime, json


def install_param_in_socket(socket_create, way):
    """Устанавливаем введенные пользователем параметры подключения к серверу/создания сервера"""
    param = sys.argv
    port = 10001
    addr = 'localhost'
    try:
        for i in param:
            if i == '-p':
                port = int(param[param.index(i)+1])
            if i == '-a':
                addr = param[param.index(i)+1]
        if way == 'connect':
            socket_create.connect((addr, port))
        elif way == 'bind':
            socket_create.bind((addr, port))
        return 'OK'
    except Exception as error:
        return error


def message_processing(message):
    """Принимаем сообщение от клиента и обрабатываем его"""
    if 'action' in message and message['action'] == 'presence' and 'time' in message and 'user' in message and \
            message['user']['account_name'] == 'Michael':
        return {'response': 200, 'alert': 'Сообщение принято'}
    else:
        return {'response': 400, 'alert': 'Сообщение отклонено'}


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


def send_message(message, client_obj):
    """Сериализуем и отправляем сообщение на сервер."""
    js_msg = json.dumps(message)
    js_msg_encode = js_msg.encode('utf-8')
    client_obj.send(js_msg_encode)
    return 'OK'