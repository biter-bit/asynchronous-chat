import unittest
from frontend.client import create_message
from backend.server import message_processing
import datetime


class ServerTest(unittest.TestCase):
    def test_message_processing_response_200(self):
        msg = create_message('привет', 'Michael')
        result = message_processing(msg)
        self.assertEqual({'response': 200, 'user_name': 'Michael', 'message': 'привет', 'alert': 'Сообщение принято'},
                         result)

    def test_message_processing_response_400(self):
        msg = {
            "action": '',
            'time': datetime.datetime.now().strftime('%d.%m.%Y'),
            'user': {
                'account_name': 'Michael',
            }
        }
        result = message_processing(msg)
        self.assertEqual({'response': 400, 'user_name': 'Michael', 'message': 'Неверный формат сообщения',
                          'alert': 'Сообщение отклонено'},
                         result)


if __name__ == '__main__':
    unittest.main()