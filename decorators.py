import sys, logging, inspect
from log import client_log_config, server_log_config

if 'client.py' in sys.argv[0].split('/'):
    LOGGER = logging.getLogger('client')
if 'server.py' in sys.argv[0].split('/'):
    LOGGER = logging.getLogger('server')


def log(func):
    def wrapper(*args, **kwargs):
        LOGGER.info(f'Используется функция {func.__name__} с параметрами {args}, {kwargs}. '
                    f'Вызвана из функции {inspect.stack()[1][3]}')
        result = func(*args, **kwargs)
        LOGGER.info(f'Функция {func.__name__} выполнилась')
        return result
    return wrapper
