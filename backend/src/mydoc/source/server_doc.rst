Server Module
===============

Серверный модуль мессенджера. Обрабатывает словари - сообщения, хранит публичные ключи клиентов и симметричные для
обмена сообщениями. Публичный и приватный ключ сервера хранится в папке secret

Использование

Модуль поддерживает аргументы командной строки:

    1. -p - Порт, на котором принимаются соединения
    2. -a - Адрес, с которого принимаются соединения

Примеры использования:

Запуск сервера на порту 8000 с адресом "localhost":

.. code-block:: bash

   python server.py

Запуск сервера на выбранном порту и адресе:

.. code-block:: bash

   python server.py -p 8080 -a 172.107.198.234

server.py
-------------

Запускаемы модуль содержит парсер аргументов командной строки и функционал инициализации приложения

.. automodule:: backend.server
   :members:

descriptor.py
---------------

.. automodule:: backend.descriptor
   :members:

metaclasses.py
----------------

.. automodule:: backend.metaclasses
   :members:

utils.py
----------

.. automodule:: backend.utils
   :members:

variables.py
--------------

.. automodule:: backend.variables
   :members:

crud.py
--------

.. automodule:: backend.server_database.crud
   :members:

model.py
----------

.. automodule:: backend.server_database.model
   :members:

server_log_config.py
----------------------

.. automodule:: backend.log.log_server.server_log_config
   :members:
