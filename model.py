import sqlite3

# создаем базу данных и устанавливаем соединение
conn = sqlite3.connect('chat.sqlite3')

# создаем обьект, благодаря которому будем делать запросы в б.д.
cursor = conn.cursor()

# sql запросы б.д.
cursor.execute("""CREATE TABLE client (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login VARCHAR(255),
        info TEXT)
""")
cursor.execute("""
        CREATE TABLE history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        ip_address VARCHAR(255))
""")
cursor.execute("""
        CREATE TABLE contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER,
        client_id INTEGER,
        FOREIGN KEY(owner_id, client_id) REFERENCES client(id, id))
""")

cursor.execute("INSERT INTO client (login, info) VALUES (?, ?)", ('michael', 'info'))

cursor.execute("INSERT INTO client (login, info) VALUES (?, ?)", ('vasy', 'info'))

cursor.execute("INSERT INTO history (ip_address) VALUES (?)", ('128.11.22.55',))

cursor.execute("INSERT INTO contacts (owner_id, client_id) VALUES (?, ?)", (1, 2))

# сохраняем результаты запросов в бд
conn.commit()

# закрываем соединение с б.д.
cursor.close()
conn.close()