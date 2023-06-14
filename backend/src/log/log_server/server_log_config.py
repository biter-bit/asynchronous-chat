import logging
import sys
from logging import handlers
from variables import ROOT_DIR

# создаем обьект логгера с именем "server"
log_server = logging.getLogger('server')

# создаем обьект логгера для фиксации чата с именем "chat"
log_chat = logging.getLogger('chat')

# создаем формат сообщения для логгера
format_log = logging.Formatter("%(asctime)s %(levelname)s %(filename)s %(message)s")

# создаем обработчик для логгера (куда будут записываться логи)
fh = handlers.TimedRotatingFileHandler(f'{ROOT_DIR}/log/log_server/server.log', when='D', interval=1)

# создаем обработчик для логгера чата
fh_chat = handlers.TimedRotatingFileHandler(f'{ROOT_DIR}/log/log_server/server_chat.log', when='D', interval=1)

# добавляем в обрабочик наш формат сообщений
fh.setFormatter(format_log)

# добавляем в обработчик чата наш формат сообщений
fh_chat.setFormatter(format_log)

# добавляем уровень записи для нашего обработчика
fh.setLevel(logging.DEBUG)

# добавляем уровень записи для нашего обработчика чата
fh_chat.setLevel(logging.DEBUG)

# добавляем в наш логгер обрабочик
log_server.addHandler(fh)

# добавляем в наш логгер чата обработчик
log_chat.addHandler(fh_chat)

# добавляем уровень записи нашего логгера
log_server.setLevel(logging.DEBUG)

# добавляем уровень записи нашего логгера чата
log_chat.setLevel(logging.DEBUG)

if __name__ == '__main__':
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(format_log)
    log_server.addHandler(ch)
    log_server.info('Тестовый запуск логирования')