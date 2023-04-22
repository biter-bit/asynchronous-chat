from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QPushButton, QToolBar
from PyQt5.QtCore import Qt
import sys
from client import install_param_in_socket_client, app_log_client, authorization_user
from utils import init_socket_tcp


class LoginWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.result = 0
        # self.layout = QVBoxLayout(self)
        # self.text_login = QtWidgets.QLabel('Dasdafasfasdf')
        # self.button = QPushButton('start')
        # self.layout.addWidget(self.button)
        # self.layout.addWidget(self.text_login)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(500, 0))
        self.setObjectName("page")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QtWidgets.QLabel(self)
        self.label.setMaximumSize(QtCore.QSize(16777215, 100))
        font = QtGui.QFont()
        font.setFamily("PT Mono")
        font.setPointSize(35)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setStyleSheet("font: 35pt \"PT Mono\";\n"
                                 "background-color: rgba(255, 255, 255, 100%);\n"
                                 "border-radius: 30px;\n"
                                 "border-color: rgb(224, 27, 36);")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setIndent(4)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.widget = QtWidgets.QWidget(self)
        self.widget.setMinimumSize(QtCore.QSize(500, 0))
        self.widget.setMaximumSize(QtCore.QSize(16777215, 200))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(-1, 0, -1, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lineEdit = QtWidgets.QLineEdit(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setMaximumSize(QtCore.QSize(500, 35))
        self.lineEdit.setText("")
        self.lineEdit.setAlignment(Qt.AlignCenter)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_2.sizePolicy().hasHeightForWidth())
        self.lineEdit_2.setSizePolicy(sizePolicy)
        self.lineEdit_2.setMaximumSize(QtCore.QSize(16777215, 35))
        self.lineEdit_2.setAlignment(Qt.AlignCenter)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.verticalLayout.addWidget(self.lineEdit_2)
        self.pushButton = QtWidgets.QPushButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setMaximumSize(QtCore.QSize(16777215, 35))
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        self.verticalLayout_3.addWidget(self.widget, 0, Qt.AlignHCenter)
        self.label.setText("<html><head/><body><p align=\"center\">АВТОРИЗАЦИЯ</p></body></html>")
        self.lineEdit.setPlaceholderText("Login")
        self.lineEdit_2.setPlaceholderText("Password")
        self.pushButton.setText("ВХОД")

class ServerGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # создаем окно и настройки для него
        self.resize(1227, 987)
        self.setMaximumSize(QtCore.QSize(1400, 1100))
        self.setWindowTitle("Асинхронный чат")
        self.setStyleSheet("QMainWindow { background-image: url(/home/michael/python_work/asynchronous_chat_gb/img/view.jpg); }")

        # создаем основной виджет для наших 2 страниц: авторизация, приложение
        self.stack = QStackedWidget(self)
        # делаем этот виджет центральным
        self.setCentralWidget(self.stack)

        # создаем обьект виджета логина и добавляем его в основной виджет
        self.login_widget = LoginWidget(self.stack)
        self.stack.addWidget(self.login_widget)

        # создаем центральный виджет, в котором будут располагаться все остальные виджиты
        self.centralwidget = QtWidgets.QWidget(self.stack)
        # создаем виджет, который будет расставлять другие обьекты по горизонтали и сразу добавляем его к центральному
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        # добавляем этот виджет в основной
        self.stack.addWidget(self.centralwidget)

        # создаем текстовый виджет, который будет отображать статистику
        self.textEdit = QtWidgets.QLabel(self.centralwidget)
        self.horizontalLayout.addWidget(self.textEdit, 1)
        self.textEdit.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # создаем виджет со списком наших пользователей
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.horizontalLayout.addWidget(self.listWidget, 0)
        self.listWidget.setStyleSheet("color: rgb(0, 0, 0);")
        for i in range(100):
            item = QtWidgets.QListWidgetItem()
            item.setText(str(i))
            item.setTextAlignment(Qt.AlignCenter)
            self.listWidget.addItem(item)

        self.tool_button = QToolBar(self.centralwidget)
        self.button_logout = QPushButton('logout')
        self.tool_button.addWidget(self.button_logout)

        # вызываем метод, который будет выводить статистику пользователя при клике на него
        self.listWidget.itemClicked.connect(self.handle_item_clicked)

        self.login_widget.pushButton.clicked.connect(self.login_successful)

        self.button_logout.clicked.connect(self.logout)

    def handle_item_clicked(self, item):
        self.textEdit.setText(item.text())
        self.textEdit.setStyleSheet("color: rgb(255, 255, 255);")
        self.textEdit.setAlignment(Qt.AlignCenter)

    def login_successful(self):
        addr, port = install_param_in_socket_client()

        # инициализируем сокет
        server = init_socket_tcp()
        app_log_client.info('Сокет инициализирован')

        # подключаемся к серверу
        app_log_client.info('Подключение к серверу...')
        server.connect((addr, port))

        print(self.login_widget.lineEdit.text())
        self.stack.setCurrentWidget(self.centralwidget)

    def logout(self):
        self.stack.setCurrentWidget(self.login_widget)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = ServerGUI()
    ui.show()
    sys.exit(app.exec_())
