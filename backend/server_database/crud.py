import random

from faker import Faker
from server_database.model import User, History, Contacts, Base, HistoryMessageUsers
import sqlalchemy
from variables import SQLALCHEMY_SERVER_DATABASE_URL
from sqlalchemy.orm import sessionmaker, aliased
import secrets, hashlib
from sqlalchemy import or_, desc


class ServerStorage:
    def __init__(self):
        # создаем движок и сессию для работы с базой данных
        self.engine = sqlalchemy.create_engine(SQLALCHEMY_SERVER_DATABASE_URL + 'example.db')
        self.Session = sessionmaker(bind=self.engine)

        # создаем обьект, который позволяет генерировать случайные данные
        self.fake = Faker()

        # создаем базу данных со всеми таблицами
        Base.metadata.create_all(self.engine)

        # создаем тестовые данные
        # self.create_test_data()

    # метод создает тестовый данные для б.д.
    def create_test_data(self):
        with self.Session() as session:
            for i in range(10):
                session.add(User(login=self.fake.user_name() + str(i), info='today', password=self.fake.password(),
                                 role='Администратор'))
                session.add(History(ip_address=self.fake.ipv4(), login=self.fake.user_name()))
                session.add(Contacts(owner_id=self.fake.random_int(min=0, max=10),
                                     client_id=self.fake.random_int(min=0, max=10)))
                session.add(HistoryMessageUsers(from_user_id=1, to_user_id=1, message=self.fake.text(20), hash_message=str(random.getrandbits(128))))
                session.commit()
        return 'Ok'

    def login(self, user_login, sock):
        with self.Session() as session:
            user = session.query(User).filter(User.login == user_login).first()
            user.authorized = True
            token = secrets.token_hex(32)
            user.token = token
            result = History(ip_address=sock.getpeername()[0], login=user_login)
            session.add(result)
            session.commit()
        return token

    def logout(self, user_login):
        with self.Session() as session:
            user = session.query(User).filter(User.login == user_login).first()
            user.authorized = False
            user.token = None
            session.commit()
        return 'Ok'

    def register(self, login, password):
        with self.Session() as session:
            user = User(login=login, password=password, role='Пользователь')
            session.add(user)
            session.commit()
        return 'Ok'

    def hash_password(self, password):
        encode_password = password.encode('utf-8')
        result = hashlib.md5(encode_password).hexdigest()
        return result

    def get_target_contact(self, contact, login):
        with self.Session() as session:
            login_list = session.query(User.login).filter(User.login.like(contact + '%')).all()
            result = [i[0] for i in login_list if i[0] != login]
            session.commit()
        return result

    def get_contacts(self, user_login):
        with self.Session() as session:
            client_id_contact = session.query(Contacts).join(User, User.id == Contacts.owner_id).\
                filter(User.login == user_login).all()
            client_id_list = [i.client_id for i in client_id_contact]
            contacts = session.query(User).filter(User.id.in_(client_id_list)).all()
            id_list_contacts = [i.login for i in contacts]
            session.commit()
        return id_list_contacts

    def get_user_role(self, login):
        with self.Session() as session:
            user = session.query(User.role).filter(User.login == login).first()
            if user:
                user = user[0]
            session.commit()
        return user

    def get_users(self):
        with self.Session() as session:
            users = session.query(User).all()
            list_users = [i.login for i in users]
            session.commit()
        return list_users

    def get_history_users(self):
        with self.Session() as session:
            users = self.get_users()
            login_history = session.query(History.login).join(User, History.login == User.login).filter(History.login.in_(users))
            list_login_history = [i[0] for i in login_history]
            session.commit()
        return list_login_history

    def get_history_user(self, login):
        with self.Session() as session:
            obj_history = session.query(History).filter_by(login=login).first()
            session.expunge(obj_history)
            session.commit()
        return obj_history

    def add_history_message(self, from_user, to_user, message):
        with self.Session() as session:
            from_user_login = session.query(User).filter(User.login == from_user).first()
            to_user_login = session.query(User).filter(User.login == to_user).first()
            hash_message = str(random.getrandbits(128))
            new_message = HistoryMessageUsers(from_user_id=from_user_login.id, to_user_id=to_user_login.id, message=message, hash_message=hash_message)
            session.add(new_message)
            session.commit()
        return hash_message

    def get_history_message_user(self, login):
        with self.Session() as session:
            a = aliased(User)
            result = session.query(a.login, User.login, HistoryMessageUsers.message, HistoryMessageUsers.create_at, HistoryMessageUsers.hash_message).\
                join(a, a.id == HistoryMessageUsers.from_user_id).\
                join(User, User.id == HistoryMessageUsers.to_user_id).\
                filter(or_(User.login == login, a.login == login)).\
                order_by(desc(HistoryMessageUsers.create_at)).\
                all()
            list_result = []
            for i in result:
                result_dict = {
                    'message': i[2],
                    'from_user': i[0],
                    'to_user': i[1],
                    'date': i[3].strftime('%d-%m-%Y %H-%M-%S'),
                    'hash_message': i[4]
                }
                list_result.append(result_dict)
            session.commit()
        return list_result

    def add_contact(self, user_login, contact_login):
        with self.Session() as session:
            contact = session.query(User).filter(User.login == contact_login).first()
            user = session.query(User).filter(User.login == user_login).first()
            result = Contacts(owner_id=user.id, client_id=contact.id)
            session.add(result)
            session.commit()
        return 'Ok'

    def del_contact(self, user_login, contact_login):
        with self.Session() as session:
            contact = session.query(User).filter(User.login == contact_login).first()
            user = session.query(User).filter(User.login == user_login).first()
            result = session.query(Contacts).filter(Contacts.owner_id == user.id and Contacts.client_id == contact.id).first()
            session.delete(result)
            session.commit()
        return 'Ok'

    def check_authorized(self, user_login, token):
        with self.Session() as session:
            user = session.query(User).filter(User.login == user_login).first()
            if user and user.token == token and user.authorized:
                return True
            else:
                return False

    def check_authenticated(self, user_login, user_password):
        with self.Session() as session:
            password = self.hash_password(user_password)
            user = session.query(User).filter(User.login == user_login).first()
            if user and user.password == password:
                return True
            else:
                return False

    def check_login(self, user_login):
        with self.Session() as session:
            user = session.query(User).filter(User.login == user_login).first()
            if user is None:
                return False
            else:
                return True

    # def check_password(self, user_password):
    #     with self.Session() as session:
    #         password = self.hash_password(user_password)
    #         user = session.query(User).filter(User.password == user_password, User.login == ).first()
    #         if user is None:
    #             return False
    #         else:
    #             return True

    def check_admin(self, user_login):
        with self.Session() as session:
            user = session.query(User).filter(User.login == user_login).first()
            if user.role == 'Администратор':
                return True
            else:
                return False


if __name__ == '__main__':
    database = ServerStorage()
    database.create_test_data()