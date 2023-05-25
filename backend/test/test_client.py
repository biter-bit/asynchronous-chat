import unittest
from frontend.client import create_message
import datetime


class ClientTest(unittest.TestCase):
    def test_create_message(self):
        result = create_message('привет', 'Michael')
        msg = {
            "action": 'presence',
            'time': datetime.datetime.now().strftime('%d.%m.%Y'),
            'user': {
                'account_name': 'Michael',
            },
            'mess_text': 'привет'
        }
        self.assertEqual(msg, result)

    # def test_get_response_server(self):
    #     server_main()
    #     message = create_message()
    #     response = client_main()
    #     self.assertEqual(message, response)


if __name__ == '__main__':
    unittest.main()