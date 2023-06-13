Client Module
===============

Клиентское приложение для обмена сообщениями. Поддерживает отправку сообщений пользователям. Использует механизм
сквозного шифрования, с помощью алгоритма шифрования RSA для публичных и приватных ключей и с помощью алгоритма AES
для симметричных ключей. В папке "secret" хранятся публичные и приватные ключи пользователей

Использование

Модуль поддерживает аргументы командной строки:

    1. -p - Порт, к которому будет подключаться клиент
    2. -a - Адрес, к которому будет подключаться клиент

Примеры использования:

Запуск клиента к серверу на порту 8000 с адресом "localhost":

.. code-block:: bash

   python client.py

Запуск клиента к серверу на выбранном порту и адресе:

.. code-block:: bash

   python client.py -p 8080 -a 172.107.198.234

client_ui.py
-------------

.. automodule:: frontend.client_ui
   :members:

client.py
----------

.. automodule:: frontend.client
   :members:

metaclasses.py
---------------

.. automodule:: frontend.metaclasses
   :members:

utils_client.py
----------------

.. automodule:: frontend.utils_client
   :members:

variables_client.py
--------------------

.. automodule:: frontend.variables_client
   :members:

crud.py
--------

.. automodule:: frontend.client_database.crud
   :members:

model.py
----------

.. automodule:: frontend.client_database.model
   :members:

client_log_config.py
----------------------

.. automodule:: frontend.log.log_client.client_log_config
   :members: