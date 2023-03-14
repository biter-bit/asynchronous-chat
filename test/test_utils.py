import unittest
import socket
import sys
from utils import install_param_in_socket, serialization_message, deserialization_message, \
    init_socket_tcp, sys_param_reboot


class UnitClientServerTest(unittest.TestCase):

    def test_install_param_in_socket(self):
        param = sys.argv
        param.extend(['-p', 10003, '-a', 'localhost'])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr, port = install_param_in_socket()
        s.close()
        self.assertEqual(('localhost', 10003), (addr, port))

    def test_install_param_in_socket_error(self):
        param = sys.argv
        param.extend(['-p', 'dsf', '-a', 'localhost'])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        error, name_error = install_param_in_socket()
        s.close()
        self.assertEqual('Ошибка', name_error)

    def test_serialization_message(self):
        word = {'name': 'Sasha'}
        serial_word = serialization_message(word)
        result = '{"name": "Sasha"}'.encode('utf-8')
        self.assertEqual(result, serial_word)

    def test_deserialization_message(self):
        word = {'name': 'Sasha'}
        serial_word = serialization_message(word)
        deserial_word = deserialization_message(serial_word)
        result = {'name': 'Sasha'}
        self.assertEqual(result, deserial_word)

    def test_init_socket(self):
        s = init_socket_tcp()
        result = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.assertEqual(result.fileno()-1, s.fileno())

    def test_sys_param_reboot(self):
        param = sys.argv
        param.extend(['-p', 10003, '-a', 'localhost'])
        reboot_param = sys_param_reboot()
        result = ['test_utils.py']
        self.assertEqual(result, reboot_param)


if __name__ == '__main__':
    unittest.main()