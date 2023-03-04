import socket
from utils import install_param_in_socket, create_message, send_message
import datetime
import json


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    install_param_in_socket(server, 'connect')

    msg = create_message()
    send_message(msg, server)

    data = server.recv(1024)
    decode_data = data.decode('utf-8')
    message = json.loads(decode_data)
    print(message['response'], message['alert'])


if __name__ == '__main__':
    main()