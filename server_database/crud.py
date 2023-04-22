from faker import Faker
from server_database.model import User, History, Contacts, Base
import sqlalchemy
from variables import SQLALCHEMY_SERVER_DATABASE_URL
from sqlalchemy.orm import sessionmaker
import secrets


class ServerStorage:
    def __init__(self):
        # создаем движок и сессию для работы с базой данных
        self.engine = sqlalchemy.create_engine(SQLALCHEMY_SERVER_DATABASE_URL)
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

    def get_contacts(self, user_login):
        with self.Session() as session:
            client_id_contact = session.query(Contacts).join(User, User.id == Contacts.owner_id).\
                filter(User.login == user_login).all()
            client_id_list = [i.client_id for i in client_id_contact]
            contacts = session.query(User).filter(User.id.in_(client_id_list)).all()
            id_list_contacts = [i.login for i in contacts]
            session.commit()
        return id_list_contacts

    def get_users(self):
        with self.Session() as session:
            users = session.query(User).all()
            list_users = [i.login for i in users]
            session.commit()
        return list_users

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
            result = session.query(Contacts).filter(Contacts.owner_id == user.id and
                                                    Contacts.client_id == contact.id).first()
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
            user = session.query(User).filter(User.login == user_login).first()
            if user and user.password == user_password:
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