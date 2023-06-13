import logging
from variables_client import ROOT_DIR

# создаем обьект логгера с именем "client_front"
log_server = logging.getLogger('client')

# создаем формат сообщения для логгера
format_log = logging.Formatter("%(asctime)s %(levelname)s %(filename)s %(message)s")

# создаем обработчик для логгера (куда будут записываться логи)
fh = logging.FileHandler(f'{ROOT_DIR}/log/log_client/client.log', encoding='utf-8')

# добавляем уровень записи для нашего обработчика
fh.setLevel(logging.DEBUG)

# добавляем в обрабочик наш формат сообщений
fh.setFormatter(format_log)

# добавляем в наш логгер обрабочик
log_server.addHandler(fh)

# добавляем уровень записи нашего логгера
log_server.setLevel(logging.DEBUG)

if __name__ == '__main__':
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(format_log)
    log_server.addHandler(ch)
    log_server.info('Тестовый запуск логирования')