from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QWidget, QPushButton, QToolBar, QMessageBox, QLineEdit
from PyQt5.QtCore import Qt
import sys
from frontend.client import authorization_user_pyqt5, connect_server, init_database, start_thread_client_send, \
    start_thread_client_recipient, registration_user_pyqt5
import json


class MessageWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(1052, 776)
        self.setMinimumSize(QtCore.QSize(0, 0))
        self.setMaximumSize(QtCore.QSize(1400, 1200))
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)

        self.setStyleSheet('QWidget { background-color: rgb(24,25,29); }')

        self.user_main = QtWidgets.QListWidget(self)
        self.user_main.setMaximumSize(QtCore.QSize(150, 16777215))
        self.user_main.setStyleSheet("QListWidget {\n"
                                     "    background-color: rgb(40,46,51);\n"
                                     "    color: rgb(131,147,163);\n"
                                     "}"
                                     "QListWidget::item { padding: 10px } ")

        self.item_my_page = QtWidgets.QListWidgetItem()
        self.item_my_page.setTextAlignment(Qt.AlignCenter)
        self.user_main.addItem(self.item_my_page)

        self.item_search = QtWidgets.QListWidgetItem()
        self.item_search.setTextAlignment(Qt.AlignCenter)
        self.user_main.addItem(self.item_search)

        self.item_logout = QtWidgets.QListWidgetItem()
        self.item_logout.setTextAlignment(Qt.AlignCenter)
        self.user_main.addItem(self.item_logout)

        self.horizontalLayout.addWidget(self.user_main)

        self.message_widget = QtWidgets.QWidget(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.message_widget.sizePolicy().hasHeightForWidth())
        self.message_widget.setSizePolicy(sizePolicy)
        self.message_widget.setMinimumSize(QtCore.QSize(0, 0))
        self.message_widget.setSizeIncrement(QtCore.QSize(0, 0))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.message_widget)

        self.scroll_area = QtWidgets.QScrollArea(self.message_widget)
        self.scroll_widget = QWidget(self.scroll_area)
        self.layout_scroll = QtWidgets.QVBoxLayout(self.scroll_widget)

        self.scroll_area.setWidgetResizable(True)
        self.layout_scroll.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.scroll_widget)
        self.verticalLayout_2.addWidget(self.scroll_area)

        self.send_line = QtWidgets.QLineEdit(self.message_widget)
        self.send_line.setStyleSheet("background-color: rgb(40,46,51); color: white")
        self.verticalLayout_2.addWidget(self.send_line)

        self.send_button = QtWidgets.QPushButton(self.message_widget)
        self.send_button.setStyleSheet("QPushButton { background-color: rgb(40,46,51); color: rgb(255,255,255) }")
        self.verticalLayout_2.addWidget(self.send_button)

        self.horizontalLayout.addWidget(self.message_widget)

        self.users_list = QtWidgets.QListWidget(self)
        self.users_list.setMaximumSize(QtCore.QSize(150, 16777215))
        self.users_list.setStyleSheet("QListWidget {\n"
                                      "    background-color: rgb(40,46,51);\n"
                                      "    color: rgb(131,147,163);\n"
                                      "}")
        self.horizontalLayout.addWidget(self.users_list)

        self.setWindowTitle("Form")
        item = self.user_main.item(0)
        item.setText("Моя страница")
        item.setTextAlignment(Qt.AlignCenter)
        item = self.user_main.item(1)
        item.setText("Поиск")
        item = self.user_main.item(2)
        item.setText("Выход")
        self.send_button.setText("Отправить")


class RegisterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.verticalLayout = QtWidgets.QVBoxLayout(self)

        self.label = QtWidgets.QLabel(self)
        self.label.setMaximumSize(QtCore.QSize(16777215, 100))
        font = QtGui.QFont()
        font.setFamily("PT Mono")
        font.setPointSize(35)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setStyleSheet("background-color: rgb(255, 255, 255);\n"
                                    "font: 35pt \"PT Mono\";\n"
                                    "border-radius: 30px;\n"
                                    "border-color: rgb(224, 27, 36);"
                                 )
        self.label.setAlignment(Qt.AlignCenter)
        self.verticalLayout.addWidget(self.label)

        self.widget_form = QtWidgets.QWidget(self)
        self.widget_form.setMinimumSize(QtCore.QSize(500, 0))
        self.widget_form.setMaximumSize(QtCore.QSize(16777215, 200))
        self.widget_form.setObjectName("widget")

        self.verticalLayout_form = QtWidgets.QVBoxLayout(self.widget_form)

        self.lineEdit_login = QtWidgets.QLineEdit(self.widget_form)
        self.lineEdit_login.setMaximumSize(QtCore.QSize(500, 35))
        self.lineEdit_login.setAlignment(Qt.AlignCenter)
        self.verticalLayout_form.addWidget(self.lineEdit_login)

        self.lineEdit_password = QtWidgets.QLineEdit(self.widget_form)
        self.lineEdit_password.setMaximumSize(QtCore.QSize(500, 35))
        self.lineEdit_password.setAlignment(Qt.AlignCenter)
        self.verticalLayout_form.addWidget(self.lineEdit_password)

        self.pushButton_send = QtWidgets.QPushButton(self.widget_form)
        self.pushButton_send.setMaximumSize(QtCore.QSize(500, 35))
        self.verticalLayout_form.addWidget(self.pushButton_send)

        self.pushButton_auth = QtWidgets.QPushButton(self.widget_form)
        self.pushButton_auth.setMaximumSize(QtCore.QSize(500, 35))
        self.verticalLayout_form.addWidget(self.pushButton_auth)

        self.verticalLayout.addWidget(self.widget_form, 0, Qt.AlignHCenter)
        self.label.setText("РЕГИСТРАЦИЯ")
        self.lineEdit_login.setPlaceholderText("Login")
        self.lineEdit_password.setPlaceholderText("Password")
        self.pushButton_send.setText("ОТПРАВИТЬ")
        self.pushButton_auth.setText("АВТОРИЗАЦИЯ")


class LoginWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

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
        self.lineEdit_2.setEchoMode(QLineEdit.Password)
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

        self.pushButton_3 = QtWidgets.QPushButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy)
        self.pushButton_3.setMaximumSize(QtCore.QSize(16777215, 35))
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout.addWidget(self.pushButton_3)
        self.pushButton_3.setText("РЕГИСТРАЦИЯ")


class ServerGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.client_sender = None
        self.client_recipient = None
        self.server = None
        self.database = None
        self.to_user = ''

        # создаем окно и настройки для него
        self.resize(1227, 987)
        self.setMaximumSize(QtCore.QSize(1400, 1100))
        self.setWindowTitle("Асинхронный чат")
        self.setStyleSheet("QMainWindow { background-image: url(/home/michael/python_work/asynchronous_chat_gb/frontend/img/view.jpg); }")

        # создаем основной виджет для наших 2 страниц: авторизация, приложение
        self.stack = QStackedWidget(self)
        # делаем этот виджет центральным
        self.setCentralWidget(self.stack)

        # создаем обьект виджета логина и добавляем его в основной виджет
        self.login_widget = LoginWidget(self.stack)
        self.stack.addWidget(self.login_widget)

        # создаем обьект виджета регистрации и добавляем его в основной виджет
        self.register_widget = RegisterWidget(self.stack)
        self.stack.addWidget(self.register_widget)

        # создаем обьект виджета отправки сообщений и добавляем его в основной виджет
        self.user_widget = MessageWidget(self.stack)
        self.stack.addWidget(self.user_widget)

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

        # создаем кнопку выхода
        self.tool_button = QToolBar(self.centralwidget)
        self.button_logout = QPushButton('logout')
        self.tool_button.addWidget(self.button_logout)

        # вызываем метод, который будет выводить статистику пользователя при клике на него
        self.listWidget.itemClicked.connect(lambda item: self.send_message({'request': '/get_statistics', 'args': item}))

        # вызываем метод, который будет авторизировать пользователя на сервере и заходить в приложение
        self.login_widget.pushButton.clicked.connect(self.login_successful)

        # добавляем возможность вернуться на страницу авторизации
        self.register_widget.pushButton_auth.clicked.connect(self.authorization)

        # вызываем метод, который будет выходить из сервера на страницу авторизации
        self.button_logout.clicked.connect(lambda: self.send_message({'request': '/quit'}))

        self.user_widget.user_main.itemClicked.connect(self.main_menu_user)

        # соединяем событие нажатия на кнопку регистрации и слот регистрации
        self.login_widget.pushButton_3.clicked.connect(self.registration)

        self.register_widget.pushButton_send.clicked.connect(self.register_success)

        # выводим историю сообщений пользователя
        self.user_widget.users_list.itemClicked.connect(self.display_messages)

        # отправляем сообщение пользователю
        self.user_widget.send_button.clicked.connect(self.send_message_user)

    def display_messages(self, item):
        self.to_user = item
        for i in self.user_widget.message_widget.findChildren(QtWidgets.QLabel):
            i.deleteLater()
        mes = self.database.get_messages(item.text())
        if mes:
            for i in mes:
                text = i['message']
                self.user_widget.label2 = {i['from_user']: QtWidgets.QLabel()}
                # self.user_widget.label2[i['from_user']].installEventFilter(self.del_message_user)
                self.user_widget.label2[i['from_user']].setText(i['from_user'] + ':<br>')
                while True:
                    if len(text) // 30:
                        self.user_widget.label2[i['from_user']].setText(self.user_widget.label2[i['from_user']].text() + text[:30] + '<br>')
                        text = text[30:]
                    else:
                        self.user_widget.label2[i['from_user']].setText(self.user_widget.label2[i['from_user']].text() + text)
                        break
                self.user_widget.label2[i['from_user']].setMargin(10)
                self.user_widget.label2[i['from_user']].setMinimumSize(QtCore.QSize(100, 60))
                # self.user_widget.label2[i['from_user']].setAlignment(Qt.AlignRight)
                if i['from_user'] == self.database.user_login:
                    self.user_widget.layout_scroll.addWidget(self.user_widget.label2[i['from_user']], 0, Qt.AlignRight | Qt.AlignTop)
                else:
                    self.user_widget.layout_scroll.addWidget(self.user_widget.label2[i['from_user']], 0,
                                                             Qt.AlignLeft | Qt.AlignTop)
                self.user_widget.label2[i['from_user']].setStyleSheet("border-radius: 10px; background-color: #33393f; color: white")
        scroll_bar = self.user_widget.scroll_area.verticalScrollBar()
        scroll_bar.rangeChanged.connect(lambda: scroll_bar.setValue(scroll_bar.maximum()))

    def send_message_user(self):
        mes = {
            'request': '/message',
            'message': self.user_widget.send_line.text(),
            'to': self.to_user.text()

        }
        self.send_message(mes)
        self.user_widget.send_line.clear()

    def del_message_user(self, widget, event):
        # menu = QMenu(self.user_widget.label2[i['from_user']].cli)
        pass


    def authorization(self):
        self.stack.setCurrentWidget(self.login_widget)
        self.login_widget.lineEdit.setText("")
        self.login_widget.lineEdit_2.setText("")
        self.login_widget.lineEdit.setFocus()

    def registration(self):
        self.stack.setCurrentWidget(self.register_widget)
        self.register_widget.lineEdit_login.setText("")
        self.register_widget.lineEdit_password.setText("")
        self.register_widget.lineEdit_login.setFocus()

    def main_menu_user(self, item):
        if item.text() == 'Моя страница':
            pass
        elif item.text() == 'Поиск':
            pass
        elif item.text() == 'Выход':
            self.send_message({'request': '/quit'})

    def handle_item_clicked(self, item):
        result = json.loads(item)
        self.textEdit.setText(
            f"Логин - {result['login']}\n"
            f"Дата создания - {result['create_at']}\n"
            f"Ip-адрес - {result['ip']}\n"
            f"Id пользователя - {result['id']}"
        )
        self.textEdit.setStyleSheet("color: rgb(255, 255, 255);")
        self.textEdit.setAlignment(Qt.AlignCenter)

    def login_successful(self):
        # подключаемся к серверу
        self.server = connect_server()

        # запоминаем логин и пароль, который ввел пользователь
        login = self.login_widget.lineEdit.text()
        password = self.login_widget.lineEdit_2.text()

        # авторизируемся на сервере
        result = authorization_user_pyqt5(self.server, login, password)

        if 'role' in result and result['role'] == 'Администратор':
            self.database = init_database(result, self.server)
            self.stack.setCurrentWidget(self.centralwidget)
            self.client_recipient = start_thread_client_recipient(result, self.server, self.database)
            self.client_sender = start_thread_client_send(result, self.server, self.database)
            self.client_recipient.message_received.connect(self.logout)
            self.client_recipient.create_users_signal.connect(self.handle_item_clicked)
            self.client_recipient.register_signal.connect(self.register_success)
            self.listWidget.clear()
            for i in result['users']:
                item = QtWidgets.QListWidgetItem()
                item.setText(i)
                item.setTextAlignment(Qt.AlignCenter)
                self.listWidget.addItem(item)
        elif 'role' in result and result['role'] == 'Пользователь':
            self.database = init_database(result, self.server)
            self.stack.setCurrentWidget(self.user_widget)
            self.user_widget.users_list.clear()
            for i in self.user_widget.message_widget.findChildren(QtWidgets.QLabel):
                i.deleteLater()
            self.client_recipient = start_thread_client_recipient(result, self.server, self.database)
            self.client_sender = start_thread_client_send(result, self.server, self.database)
            self.client_recipient.message_received.connect(self.logout)
            self.client_recipient.message_user_received.connect(lambda: self.display_messages(self.to_user))
            for i in self.database.get_contacts():
                item = QtWidgets.QListWidgetItem()
                item.setText(str(i))
                item.setTextAlignment(Qt.AlignCenter)
                self.user_widget.users_list.addItem(item)
        elif 'role' not in result:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Неправильный логин или пароль")
            msg.setWindowTitle("Ошибка")
            msg.exec_()
            # очищаем поля ввода и устанавливаем фокус на поле логина
            self.login_widget.lineEdit.setText("")
            self.login_widget.lineEdit_2.setText("")
            self.login_widget.lineEdit.setFocus()

    def send_message(self, message):
        self.client_sender.send_message(message)

    def logout(self, mes):
        if mes == 'quit':
            self.stack.setCurrentWidget(self.login_widget)
            self.login_widget.lineEdit.setText("")
            self.login_widget.lineEdit_2.setText("")
            self.login_widget.lineEdit.setFocus()
        elif mes == 'statistics':
            pass

    def register_success(self):
        self.server = connect_server()

        login = self.register_widget.lineEdit_login.text()
        password = self.register_widget.lineEdit_password.text()

        result = registration_user_pyqt5(self.server, login, password)

        if result == 'Ok':
            self.stack.setCurrentWidget(self.login_widget)
            self.login_widget.lineEdit.setText("")
            self.login_widget.lineEdit_2.setText("")
            self.login_widget.lineEdit.setFocus()
            self.server.close()
        else:
            pass


if __name__ == "__main__":

    # создаем приложение
    app = QtWidgets.QApplication(sys.argv)

    # создаем отображение нашего приложения
    ui = ServerGUI()
    ui.show()

    # создаем правильное закрытие программы
    sys.exit(app.exec_())
