import logging
from logging import handlers

# создаем обьект логгера с именем "server"
log_server = logging.getLogger('server')

# создаем формат сообщения для логгера
format_log = logging.Formatter("%(asctime)s %(levelname)s %(filename)s %(message)s")

# создаем обработчик для логгера (куда будут записываться логи)
fh = handlers.TimedRotatingFileHandler('log/log_server/server.log', when='D', interval=1)

# добавляем в обрабочик наш формат сообщений
fh.setFormatter(format_log)

# добавляем уровень записи для нашего обработчика
fh.setLevel(logging.DEBUG)

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


# после можно приступать к заданию 3