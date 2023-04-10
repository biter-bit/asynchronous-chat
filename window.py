import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QMainWindow, QTextEdit, \
    QLineEdit, QVBoxLayout
from PyQt5.QtNetwork import QTcpSocket


class ClientGUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # создание ввода текста
        self.chat = QTextEdit()
        self.input_chat = QLineEdit()
        self.button_chat = QPushButton('Send')

        # создаем layout
        layout = QVBoxLayout()
        layout.addWidget(self.chat)
        layout.addWidget(self.input_chat)
        layout.addWidget(self.button_chat)
        self.setLayout(layout)

        # создание сокета
        self.socket = QTcpSocket()
        self.socket.readyRead.connect(self.receive_message)

        # Установка соединения с сервером
        self.socket.connectToHost('localhost', 10001)

        # устанавливаем сигнал на кнопку
        self.button_chat.clicked.connect(self.send_message)

    def send_message(self):
        # Отправка сообщения на сервер
        message = self.input_chat.text()
        self.socket.write(message.encode())
        self.input_chat.setText('')

    def receive_message(self):
        # Получение сообщение от сервера
        message = self.socket.readAll().data().decode()
        self.chat.append(message)


if __name__ == '__main__':
    # создаем экземпляр нашего приложения
    app = QApplication(sys.argv)
    client = ClientGUI()

    # отобразить приложение
    client.show()
    sys.exit(app.exec_())

# создаем главное окно и указываем ему размеры
# w = QWidget()
# w.resize(1280, 720)
# w.move(300, 300)

# называем окно приложения
# w.setWindowTitle('Messanger')


# label = QLabel('hello', parent=w)
# button = QPushButton('Click me!', parent=w)
# # button.move(50, 50)
# button.clicked.connect(lambda: print('hello'))