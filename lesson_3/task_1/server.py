import socket
from utils import install_param_in_socket, message_processing, send_message
import json


def main():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    install_param_in_socket(server, 'bind')
    server.listen(5)

    while True:
        client, client_addr = server.accept()
        print(f'Получен запрос на соединение от {str(client_addr)}')

        data = client.recv(1024)
        decode_data = data.decode('utf-8')
        message = message_processing(json.loads(decode_data))

        send_message(message, client)
        client.close()


if __name__ == '__main__':
    main()