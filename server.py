from utils import init_socket_tcp, serialization_message, deserialization_message, sys_param_reboot
import sys
import logging, select, socket
from log import server_log_config
from metaclasses import ServerVerifier
from descriptor import ServerCheckPort

app_log_server = logging.getLogger('server')
app_log_chat = logging.getLogger('chat')


class Server(metaclass=ServerVerifier):
    port = ServerCheckPort()

    def __init__(self, addr, port, wait):
        self.addr = addr
        self.port = port
        self.clients = []
        self.r = []
        self.w = []
        self.e = []
        self.message_client = {}
        self.wait = wait

    def socket_init(self):
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        app_log_server.info('Сокет инициализирован')
        transport.bind((self.addr, self.port))
        transport.settimeout(0.5)
        self.sock = transport
        self.sock.listen()

    def message_processing(self, message):
        """Принимаем сообщение от клиента и обрабатываем его"""
        if 'action' in message and message['action'] == 'presence' and 'time' in message and 'user' in message and \
                message['user']['account_name'] and message['mess_text']:
            app_log_server.info('Сообщение принято. Ответ 200')
            return {'response': 200, 'user_name': message['user']['account_name'], 'message': message['mess_text'],
                    'alert': 'Сообщение принято'}
        else:
            app_log_server.info('Сообщение отклонено. Ответ 400')
            return {'response': 400, 'user_name': message['user']['account_name'],
                    'message': 'Неверный формат сообщения',
                    'alert': 'Сообщение отклонено'}

    def get_and_send_message(self):
        self.socket_init()
        while True:
            try:
                client, client_addr = self.sock.accept()
            except OSError:
                pass
            else:
                app_log_server.info('Получен запрос на соединение от %s', client_addr)
                self.clients.append(client)
            finally:
                self.r = []
                self.w = []
                self.e = []
                try:
                    self.r, self.w, self.e = select.select(self.clients, self.clients, self.clients, self.wait)
                except:
                    pass
                self.message_client = {}
                for i in self.r:
                    try:
                        data = i.recv(1024)
                        decode_data_dict = deserialization_message(data)
                        app_log_server.info('Сообщение десериализовано')
                        self.message_client[i] = decode_data_dict
                        app_log_server.info(f'Сообщение пользователя {i.fileno()} {i.getpeername()} десериализовано')
                        message = self.message_processing(self.message_client[i])
                        app_log_chat.info(f"{message['user_name']} >> {message['message']}")
                    except Exception:
                        app_log_server.info(f'Клиент {i.fileno()} {i.getpeername()} отключился')
                        i.close()
                        self.clients.remove(i)

                if self.message_client:
                    for i in self.w:
                        for el in self.message_client.keys():
                            if el == i:
                                continue
                            try:
                                message = self.message_processing(self.message_client[el])
                                byte_message = serialization_message(message)
                                app_log_server.info('Сообщение сериализовано')
                                i.send(byte_message)
                            except Exception:
                                app_log_server.info(f'Клиент {i.fileno()} {i.getpeername()} отключился')
                                i.close()
                                self.clients.remove(i)


def install_param_in_socket_server():
    """Устанавливаем введенные пользователем параметры подключения к серверу/создания сервера"""
    param = sys.argv
    port = 10005
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
    addr, port = install_param_in_socket_server()

    obj_server = Server(addr, port, 10)
    obj_server.get_and_send_message()


if __name__ == '__main__':
    main()
