import unittest
from client import create_message
from server import message_processing
import datetime


class ServerTest(unittest.TestCase):
    def test_message_processing_response_200(self):
        msg = create_message()
        result = message_processing(msg)
        self.assertEqual({'response': 200, 'alert': 'Сообщение принято'}, result)

    def test_message_processing_response_400(self):
        msg = {
            "action": '',
            'time': datetime.datetime.now().strftime('%d.%m.%Y'),
            'user': {
                'account_name': 'Michael',
            }
        }
        result = message_processing(msg)
        self.assertEqual({'response': 400, 'alert': 'Сообщение отклонено'}, result)


if __name__ == '__main__':
    unittest.main()