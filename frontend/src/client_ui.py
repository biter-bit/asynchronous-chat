import time

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QWidget, QPushButton, QLineEdit, QLabel, QMessageBox
from PyQt5.QtCore import Qt
import sys
from client import authorization, connect_server, init_database, start_thread_client_send, \
    start_thread_client_recipient, registration
import json
from variables_client import ROOT_DIR


class SearchContactWidget(QWidget):
    """
    Класс SearchContactWidget является ui, который осуществляет поиск контактов в базе данных сервера и клиента
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(1052, 776)
        self.setMinimumSize(QtCore.QSize(0, 0))
        self.setMaximumSize(QtCore.QSize(1400, 1200))
        self.setStyleSheet('QWidget { background-color: rgb(24,25,29); }')
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)

        self.user_main = QtWidgets.QListWidget(self)
        self.user_main.setFocusPolicy(Qt.NoFocus)
        self.user_main.clearFocus()
        self.user_main.setMaximumSize(QtCore.QSize(150, 16777215))
        self.user_main.setStyleSheet("QListWidget {\n"
                                     "    background-color: rgb(40,46,51);\n"
                                     "    color: rgb(131,147,163);\n"
                                     "}"
                                     "QListWidget::item { padding: 10px }")

        self.item_my_page = QtWidgets.QListWidgetItem()
        self.item_my_page.setTextAlignment(Qt.AlignCenter)
        self.item_my_page.setText('Моя страница')
        self.user_main.addItem(self.item_my_page)

        self.item_search = QtWidgets.QListWidgetItem()
        self.item_search.setTextAlignment(Qt.AlignCenter)
        self.item_search.setText('Поиск')
        self.user_main.addItem(self.item_search)

        self.item_logout = QtWidgets.QListWidgetItem()
        self.item_logout.setTextAlignment(Qt.AlignCenter)
        self.item_logout.setText('Выход')
        self.user_main.addItem(self.item_logout)

        self.horizontalLayout.addWidget(self.user_main)

        self.search_widget = QWidget(self)

        self.verticalLayout = QtWidgets.QVBoxLayout(self.search_widget)
        self.list_contacts = QtWidgets.QListWidget(self)
        self.list_contacts.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.list_contacts.setStyleSheet("QListWidget {\n"
                                     "    background-color: rgb(40,46,51);\n"
                                     "    color: rgb(131,147,163);\n"
                                     "}"
                                     "QListWidget::item { padding: 10px } ")
        self.verticalLayout.addWidget(self.list_contacts)

        self.item_my_page = QtWidgets.QListWidgetItem()
        self.item_my_page.setTextAlignment(Qt.AlignCenter)
        self.user_main.addItem(self.item_my_page)

        self.send_line = QtWidgets.QLineEdit()
        self.send_line.setStyleSheet("background-color: rgb(40,46,51); color: white")
        self.send_line.setPlaceholderText('Имя пользователя')
        self.verticalLayout.addWidget(self.send_line)

        self.send_button = QtWidgets.QPushButton()
        self.send_button.setStyleSheet("QPushButton { background-color: rgb(40,46,51); color: rgb(255,255,255) }")
        self.send_button.setText("Найти")
        self.verticalLayout.addWidget(self.send_button)

        self.horizontalLayout.addWidget(self.search_widget)


class MessageUserWidget(QWidget):
    """
    Класс MessageUserWidget является ui, который отображает окно переписки с пользователем
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(1052, 776)
        self.setMinimumSize(QtCore.QSize(0, 0))
        self.setMaximumSize(QtCore.QSize(1400, 1200))
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)

        self.setStyleSheet('QWidget { background-color: rgb(24,25,29); }')

        self.user_main = QtWidgets.QListWidget(self)
        self.user_main.setFocusPolicy(Qt.NoFocus)
        self.user_main.clearFocus()
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
        self.scroll_area.setStyleSheet("border: 2px solid rgb(24,25,29); color: white")
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


class MessageWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(1052, 776)
        self.setMinimumSize(QtCore.QSize(0, 0))
        self.setMaximumSize(QtCore.QSize(1400, 1200))
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)

        self.setStyleSheet('QWidget { background-color: rgb(24,25,29); }')

        self.user_main = QtWidgets.QListWidget(self)
        self.user_main.setFocusPolicy(Qt.NoFocus)
        self.user_main.clearFocus()
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


class RegisterWidget(QWidget):
    """
    Класс RegisterWidget является ui, который отображает окно регистрации пользователя
    """
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
        self.lineEdit_password.setEchoMode(QLineEdit.Password)
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
    """
    Класс LoginWidget является ui, который отображает окно авторизации пользователя
    """
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


class AdminWidget(QWidget):
    """
    Класс AdminWidget является ui, который отображает панель администратора
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # создаем виджет, который будет расставлять другие обьекты по горизонтали и сразу добавляем его к центральному
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)

        self.user_main = QtWidgets.QListWidget(self)
        self.user_main.setFocusPolicy(Qt.NoFocus)
        self.user_main.clearFocus()
        self.user_main.setMaximumSize(QtCore.QSize(150, 16777215))
        self.user_main.setStyleSheet("QListWidget {\n"
                                     "    background-color: rgb(40,46,51);\n"
                                     "    color: rgb(131,147,163);\n"
                                     "}"
                                     "QListWidget::item { padding: 10px } ")

        self.item_logout = QtWidgets.QListWidgetItem()
        self.item_logout.setTextAlignment(Qt.AlignCenter)
        self.user_main.addItem(self.item_logout)
        item = self.user_main.item(0)
        item.setText("Выход")

        self.horizontalLayout.addWidget(self.user_main)

        # создаем текстовый виджет, который будет отображать статистику
        self.textEdit = QtWidgets.QLabel(self)
        self.horizontalLayout.addWidget(self.textEdit, 1)
        self.textEdit.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # создаем виджет со списком наших пользователей
        self.listWidget = QtWidgets.QListWidget(self)
        self.horizontalLayout.addWidget(self.listWidget, 0)
        self.listWidget.setStyleSheet("color: rgb(0, 0, 0);")


class ServerGUI(QMainWindow):
    """
    Класс ServerGUI является основным ui, который связывает весь функционал других модулей ui
    """
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
        self.setStyleSheet(f"QMainWindow {{ background-image: url({ROOT_DIR}/img/view.jpg); }}")

        # создаем основной виджет для наших 2 страниц: авторизация, приложение
        self.stack = QStackedWidget(self)
        # делаем этот виджет центральным
        self.setCentralWidget(self.stack)

        # создаем обьект виджета авторизации и добавляем его в основной виджет
        self.login_widget = LoginWidget(self.stack)
        self.stack.addWidget(self.login_widget)

        # создаем обьект виджета регистрации и добавляем его в основной виджет
        self.register_widget = RegisterWidget(self.stack)
        self.stack.addWidget(self.register_widget)

        # создаем обьект виджета отправки сообщений и добавляем его в основной виджет
        self.user_widget = MessageWidget(self.stack)
        self.stack.addWidget(self.user_widget)

        # создаем обьект виджета отправки конкретному пользователю и добавляем его в основной виджет
        self.user_target_widget = MessageUserWidget(self.stack)
        self.stack.addWidget(self.user_target_widget)

        # создаем обьект виджета поиска контактов и добавления их в список контактов
        self.search_contact_widget = SearchContactWidget(self.stack)
        self.stack.addWidget(self.search_contact_widget)

        # создаем обьект виджета админки и добавляем его в основной виджет
        self.admin_panel_widget = AdminWidget(self.stack)
        self.stack.addWidget(self.admin_panel_widget)

        # создаем сигналы и действия для них
        self.chat_signals()

    def login(self):
        self.server = connect_server()
        # запоминаем логин и пароль, который ввел пользователь
        login = self.login_widget.lineEdit.text()
        password = self.login_widget.lineEdit_2.text()
        # авторизируемся на сервере
        result = authorization(login, password, self.server)
        if 'role' in result and result['role'] == 'Нет доступа':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Данный пользователь уже в системе")
            msg.setWindowTitle("Ошибка")
            msg.exec_()
            # очищаем поля ввода и устанавливаем фокус на поле логина
            self.login_widget.lineEdit.setText("")
            self.login_widget.lineEdit_2.setText("")
            self.login_widget.lineEdit.setFocus()
        elif 'role' in result and result['role'] == 'Неверный логин или пароль':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Неверный логин или пароль")
            msg.setWindowTitle("Ошибка")
            msg.exec_()
            # очищаем поля ввода и устанавливаем фокус на поле логина
            self.login_widget.lineEdit.setText("")
            self.login_widget.lineEdit_2.setText("")
            self.login_widget.lineEdit.setFocus()
        elif 'role' in result and result['role'] == 'Администратор':
            self.database = init_database(result, self.server)
            self.stack.setCurrentWidget(self.admin_panel_widget)
            self.client_recipient = start_thread_client_recipient(result, self.server, self.database)
            self.client_sender = start_thread_client_send(result, self.server, self.database)
            self.client_recipient.message_received.connect(self.logout)
            self.client_recipient.create_users_signal.connect(self.handle_item_clicked)
            self.client_recipient.register_signal.connect(self.register)
            self.admin_panel_widget.listWidget.clear()
            for i in result['users']:
                item = QtWidgets.QListWidgetItem()
                item.setText(i)
                item.setTextAlignment(Qt.AlignCenter)
                self.admin_panel_widget.listWidget.addItem(item)
        elif 'role' in result and result['role'] == 'Пользователь':
            self.database = init_database(result, self.server)
            self.stack.setCurrentWidget(self.user_widget)
            self.user_widget.users_list.clear()
            self.search_contact_widget.list_contacts.clear()
            self.search_contact_widget.send_line.clear()
            for i in self.user_widget.message_widget.findChildren(QtWidgets.QLabel):
                i.deleteLater()
            self.client_recipient = start_thread_client_recipient(result, self.server, self.database)
            self.client_sender = start_thread_client_send(result, self.server, self.database)
            self.client_recipient.message_received.connect(self.logout)
            self.client_recipient.message_user_received.connect(lambda item: self.display_messages(item))
            self.client_recipient.search_contact_signal.connect(lambda item: self.output_found_contacts(item))
            for i in self.database.get_contacts():
                item = QtWidgets.QListWidgetItem()
                item.setText(str(i))
                item.setTextAlignment(Qt.AlignCenter)
                self.user_widget.users_list.addItem(item)

    def register(self):
        self.server = connect_server()

        login = self.register_widget.lineEdit_login.text()
        password = self.register_widget.lineEdit_password.text()

        result = registration(self.server, login, password)

        if result['response'] == 200:
            self.stack.setCurrentWidget(self.login_widget)
            self.login_widget.lineEdit.setText("")
            self.login_widget.lineEdit_2.setText("")
            self.login_widget.lineEdit.setFocus()
            self.server.close()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Данные не валидны")
            msg.setWindowTitle("Ошибка")
            msg.exec_()
            # очищаем поля ввода и устанавливаем фокус на поле логина
            self.register_widget.lineEdit_login.setText("")
            self.register_widget.lineEdit_password.setText("")
            self.register_widget.lineEdit_login.setFocus()
            self.server.close()

    def add_contact(self, item):
        msg = {
            'request': '/add_contact',
            'args': item
        }
        self.client_sender.send_message(msg)

    def get_public_key_user(self, item):
        mes = {
            'request': '/get_public_key',
            'contact': item
        }
        self.client_sender.send_message(mes)
        while True:
            public_key = self.database.get_public_key_user(item)
            if public_key:
                break
        return 'Ok'

    def send_message_user(self):
        self.get_public_key_user(self.to_user)
        mes = {
            'request': '/message',
            'message': self.user_target_widget.send_line.text(),
            'to': self.to_user

        }
        list_mes = self.database.get_messages(self.to_user)
        self.client_sender.send_message(mes)
        while True:
            if len(list_mes) < len(self.database.get_messages(self.to_user)):
                break
        self.user_target_widget.send_line.clear()
        return 'Ok'

    def get_symmetric_key(self, login):
        mes = {
            'request': '/get_symmetric_key',
            'contact': login,
        }
        self.client_sender.send_message(mes)
        while True:
            check_symmetric_key_client = self.database.get_symmetric_key_for_communicate_between_users(
                login
            )
            if check_symmetric_key_client:
                break
        return 'Ok'

    def get_messages_user(self, login):
        # создаем сообщение запроса
        msg = {
            'request': '/get_messages_users',
            'login': login
        }
        self.client_sender.send_message(msg)
        return 'Ok'

    # используется для преобразования обьекта пользователя в имя (str) и передается в качестве аргумента функции d_m
    def user_name_message_display_func(self, user_obj):
        self.to_user = user_obj.text()
        # получяаем публичный ключ пользователя
        self.get_public_key_user(self.to_user)
        time.sleep(2)
        # добавляем симметричный ключ для расшифровки сообщений (может возникнуть ошибка из-за того, что после
        # отправки второго запроса сервер не успевает ответить прежде, чем выполниться get_messages_user
        self.get_symmetric_key(self.to_user)
        time.sleep(2)
        # добавляем сообщения
        self.get_messages_user(self.to_user)
        time.sleep(1)
        # # отображаем переписку
        # self.display_messages(self.to_user)

    # отображает переписку с пользователем (удаляет все сообщения и добавляет имеющиеся)
    def display_messages(self, item):
        if self.to_user:
            # делаем виджет с перепиской центральным
            self.stack.setCurrentWidget(self.user_target_widget)

            # удаляем все отображаемые сообщения
            for i in self.user_target_widget.message_widget.findChildren(QtWidgets.QLabel):
                i.deleteLater()

            # получаем все сообщения с выбранным пользователем
            mes = self.database.get_messages(item)

            # добавляем имя пользователя на экран, с кем ведется переписка
            self.user_target_widget.label = QtWidgets.QLabel()
            self.user_target_widget.label.setText(item)
            self.user_target_widget.layout_scroll.addWidget(self.user_target_widget.label, 0, Qt.AlignCenter | Qt.AlignTop)
            self.user_target_widget.label.setStyleSheet("color: white")

            # если сообщения есть, то выводим их в нужном формате
            if mes:
                for i in mes:
                    text = i['message']
                    self.user_target_widget.label2 = {i['from_user']: QtWidgets.QLabel()}
                    self.user_target_widget.label2[i['from_user']].setText(i['from_user'] + ':<br>')
                    while True:
                        if len(text) // 30:
                            self.user_target_widget.label2[i['from_user']].setText(self.user_target_widget.label2[i['from_user']].text() + text[:30] + '<br>')
                            text = text[30:]
                        else:
                            self.user_target_widget.label2[i['from_user']].setText(self.user_target_widget.label2[i['from_user']].text() + text)
                            break

                    self.user_target_widget.label2[i['from_user']].setMargin(10)
                    self.user_target_widget.label2[i['from_user']].setMinimumSize(QtCore.QSize(100, 60))
                    if i['from_user'] == self.database.user_login:
                        self.user_target_widget.layout_scroll.addWidget(self.user_target_widget.label2[i['from_user']], 0, Qt.AlignRight | Qt.AlignTop)
                    else:
                        self.user_target_widget.layout_scroll.addWidget(self.user_target_widget.label2[i['from_user']], 0,
                                                                 Qt.AlignLeft | Qt.AlignTop)
                    self.user_target_widget.label2[i['from_user']].setStyleSheet("border-radius: 10px; background-color: #33393f; color: white")

            # отчищаем всех пользователей на экране справа
            self.user_target_widget.users_list.clear()

            # выводим всех пользователей на экран
            for i in self.database.get_contacts():
                item = QtWidgets.QListWidgetItem()
                item.setText(str(i))
                item.setTextAlignment(Qt.AlignCenter)
                self.user_target_widget.users_list.addItem(item)
            scroll_bar = self.user_target_widget.scroll_area.verticalScrollBar()
            scroll_bar.rangeChanged.connect(lambda: scroll_bar.setValue(scroll_bar.maximum()))

    # отображает контакты в нужном формате в графе "Поиск"
    def output_found_contacts(self, item):
        self.search_contact_widget.list_contacts.clear()
        for i in item:
            self.search_contact_widget.widget = QWidget()
            self.search_contact_widget.widget.setStyleSheet("background-color: transparent;")
            self.search_contact_widget.layout = QtWidgets.QHBoxLayout(self.search_contact_widget.widget)
            self.search_contact_widget.label = QLabel(i)
            self.search_contact_widget.label.setStyleSheet("background-color: rgb(40,46,51); color: white")
            self.search_contact_widget.layout.addWidget(self.search_contact_widget.label)
            self.search_contact_widget.button = QPushButton('Добавить')
            self.search_contact_widget.button.setStyleSheet("QPushButton { background-color: rgb(40,46,51); color: rgb(255,255,255) }")
            self.search_contact_widget.layout.addWidget(self.search_contact_widget.button)
            self.search_contact_widget.layout.setContentsMargins(0, 0, 0, 0)

            self.search_contact_widget.item = QtWidgets.QListWidgetItem()
            self.search_contact_widget.list_contacts.addItem(self.search_contact_widget.item)
            self.search_contact_widget.list_contacts.setItemWidget(self.search_contact_widget.item, self.search_contact_widget.widget)

            self.search_contact_widget.button.clicked.connect(lambda state, label=self.search_contact_widget.label.text(): self.add_contact(label))

    # отображает страницу авторизации
    def authorization(self):
        self.stack.setCurrentWidget(self.login_widget)

        self.login_widget.lineEdit.setText("")
        self.login_widget.lineEdit_2.setText("")
        self.login_widget.lineEdit.setFocus()

    # отображает страницу регистрации
    def registration(self):
        self.stack.setCurrentWidget(self.register_widget)
        self.register_widget.lineEdit_login.setText("")
        self.register_widget.lineEdit_password.setText("")
        self.register_widget.lineEdit_login.setFocus()

    # открывает страницу авторизации
    def logout(self):
        self.stack.setCurrentWidget(self.login_widget)
        self.login_widget.lineEdit.setText("")
        self.login_widget.lineEdit_2.setText("")
        self.login_widget.lineEdit.setFocus()

    # отображает одну из страниц: Моя страница, Поиск, Выход
    def main_menu_user(self, item):
        if item.text() == 'Моя страница':
            self.to_user = ''
            self.user_widget.users_list.clear()
            for i in self.user_widget.message_widget.findChildren(QtWidgets.QLabel):
                i.deleteLater()
            for i in self.database.get_contacts():
                item = QtWidgets.QListWidgetItem()
                item.setText(str(i))
                item.setTextAlignment(Qt.AlignCenter)
                self.user_widget.users_list.addItem(item)
            self.search_contact_widget.user_main.clearSelection()
            self.user_widget.user_main.clearSelection()
            self.user_target_widget.user_main.clearSelection()
            self.stack.setCurrentWidget(self.user_widget)
        elif item.text() == 'Поиск':
            self.to_user = ''
            self.search_contact_widget.list_contacts.clear()
            self.search_contact_widget.send_line.clear()
            self.search_contact_widget.user_main.clearSelection()
            self.user_widget.user_main.clearSelection()
            self.user_target_widget.user_main.clearSelection()
            self.stack.setCurrentWidget(self.search_contact_widget)
        elif item.text() == 'Выход':
            self.to_user = ''
            self.search_contact_widget.user_main.clearSelection()
            self.user_widget.user_main.clearSelection()
            self.user_target_widget.user_main.clearSelection()
            self.client_sender.send_message({'request': '/quit'})

    # отображает информацию о пользователе (для админки)
    def handle_item_clicked(self, item):
        result = json.loads(item)
        self.admin_panel_widget.textEdit.setText(
            f"Логин - {result['login']}\n"
            f"Дата создания - {result['create_at']}\n"
            f"Ip-адрес - {result['ip']}\n"
            f"Id пользователя - {result['id']}"
        )
        self.admin_panel_widget.textEdit.setStyleSheet("color: rgb(255, 255, 255);")
        self.admin_panel_widget.textEdit.setAlignment(Qt.AlignCenter)

    # все сигналы приложения
    def chat_signals(self):
        # вызываем метод, который будет авторизировать пользователя на сервере и заходить в приложение
        self.login_widget.pushButton.clicked.connect(self.login)

        # регистрируем пользователя при нажатии кнопки отправить
        self.register_widget.pushButton_send.clicked.connect(self.register)

        # добавляем возможность вернуться на страницу авторизации
        self.register_widget.pushButton_auth.clicked.connect(self.authorization)

        self.search_contact_widget.send_button.clicked.connect(lambda: self.client_sender.send_message({
            'request': '/get_target_contact',
            'args': self.search_contact_widget.send_line.text()
        }))

        # вызываем метод, который будет выводить статистику пользователя при клике на него
        self.admin_panel_widget.listWidget.itemClicked.connect(lambda item: self.client_sender.send_message({
            'request': '/get_statistics',
            'args': item
        }))

        # переключение вкладок в панели пользователя
        self.user_widget.user_main.itemClicked.connect(self.main_menu_user)

        # переключение вкладок в панели пользователя
        self.user_target_widget.user_main.itemClicked.connect(self.main_menu_user)

        # переключение вкладок в панели поиска контактов
        self.search_contact_widget.user_main.itemClicked.connect(self.main_menu_user)

        # переключение вкладок в панели администратора
        self.admin_panel_widget.user_main.itemClicked.connect(self.main_menu_user)

        # соединяем событие нажатия на кнопку регистрации и слот регистрации
        self.login_widget.pushButton_3.clicked.connect(self.registration)

        # выводим историю сообщений пользователя
        self.user_widget.users_list.itemDoubleClicked.connect(self.user_name_message_display_func)

        # выводим историю сообщений пользователя
        self.user_target_widget.users_list.itemDoubleClicked.connect(self.user_name_message_display_func)

        # отправляем сообщение пользователю
        self.user_target_widget.send_button.clicked.connect(self.send_message_user)


if __name__ == "__main__":
    # создаем приложение
    app = QtWidgets.QApplication(sys.argv)

    # создаем отображение нашего приложения
    ui = ServerGUI()
    ui.show()

    # создаем правильное закрытие программы
    sys.exit(app.exec_())
