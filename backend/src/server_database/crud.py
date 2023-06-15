import random
import secrets
import hashlib
import uuid
import sqlalchemy

from faker import Faker
from server_database.model import User, History, Contacts, Base, HistoryMessageUsers
from variables import SQLALCHEMY_SERVER_DATABASE_URL
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy import or_, desc
from sqlalchemy.sql import default_comparator


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

    def get_public_key_user(self, login):
        with self.Session() as session:
            result = session.query(User.public_key).filter(User.login == login).first()
            session.commit()
        return result[0]

    def logout(self, user_login):
        with self.Session() as session:
            user = session.query(User).filter(User.login == user_login).first()
            user.authorized = False
            user.token = None
            session.commit()
        return 'Ok'

    def register(self, login, password, public_key):
        with self.Session() as session:
            if self.validator_unique_user(login) and self.validator_mail(login):
                salt = uuid.uuid4().hex
                hash_password = self.hash_password(salt) + password
                user = User(login=login, password=hash_password, role='Пользователь', salt=salt, public_key=public_key)
                session.add(user)
                session.commit()
                return 'Ok'
        return 'Not valid'

    def validator_unique_user(self, login):
        with self.Session() as session:
            login_list = session.query(User.login).filter(User.login == login).all()
            result = [i[0] for i in login_list if i[0] == login]
            if result:
                return False
        return True

    def validator_mail(self, login):
        # сделать с помощью регулярок
        if '@' in login and 5 < len(login) < 40:
            return True
        return False

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

    def get_symmetric_key_for_communicate_between_users(self, login_owner, login_client):
        with self.Session() as session:
            owner_alias = aliased(User)
            client_alias = aliased(User)
            data_contact = session.query(Contacts.symmetric_key).\
                join(owner_alias, Contacts.owner_id == owner_alias.id).\
                join(client_alias, Contacts.client_id == client_alias.id).\
                filter(owner_alias.login == login_owner, client_alias.login == login_client).first()
            if data_contact[0] is not None:
                return data_contact[0]
            session.commit()
        return None

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

    def add_history_message(self, from_user, to_user, message, hash_mes='', nonce=''):
        with self.Session() as session:
            from_user_login = session.query(User).filter(User.login == from_user).first()
            to_user_login = session.query(User).filter(User.login == to_user).first()
            new_message = HistoryMessageUsers(from_user_id=from_user_login.id, to_user_id=to_user_login.id,
                                              message=message, hash_message=hash_mes, nonce=nonce)
            session.add(new_message)
            session.commit()
        return 'Ok'

    def get_history_message_user(self, login, contact):
        with self.Session() as session:
            a = aliased(User)
            result = session.query(a.login, User.login, HistoryMessageUsers.message, HistoryMessageUsers.create_at, HistoryMessageUsers.hash_message, HistoryMessageUsers.nonce).\
                join(a, a.id == HistoryMessageUsers.from_user_id).\
                join(User, User.id == HistoryMessageUsers.to_user_id).\
                filter(or_(User.login == login, a.login == login)).\
                filter(or_(User.login == contact, a.login == contact)).\
                order_by(desc(HistoryMessageUsers.create_at)).\
                all()
            list_result = []
            for i in result:
                result_dict = {
                    'message': i[2],
                    'from_user': i[0],
                    'to_user': i[1],
                    'date': i[3].strftime('%d-%m-%Y %H-%M-%S'),
                    'hash_message': i[4],
                    'nonce': i[5]
                }
                list_result.append(result_dict)
            session.commit()
        return list_result

    def add_contact(self, user_login, contact_login):
        with self.Session() as session:
            contact = session.query(User).filter(User.login == contact_login).first()
            user = session.query(User).filter(User.login == user_login).first()
            owner_alias = aliased(User)
            client_alias = aliased(User)
            check_contact = session.query(Contacts). \
                join(owner_alias, Contacts.owner_id == owner_alias.id). \
                join(client_alias, Contacts.client_id == client_alias.id). \
                filter(owner_alias.login == user_login, client_alias.login == contact_login).first()
            if not check_contact:
                result = Contacts(owner_id=user.id, client_id=contact.id)
                session.add(result)
            check_contact = session.query(Contacts). \
                join(owner_alias, Contacts.owner_id == owner_alias.id). \
                join(client_alias, Contacts.client_id == client_alias.id). \
                filter(owner_alias.login == contact_login, client_alias.login == user_login).first()
            if not check_contact:
                result = Contacts(owner_id=contact.id, client_id=user.id)
                session.add(result)
            session.commit()
        return 'Ok'

    def update_contact_add_symmetric_key(self, login_owner, login_client, symmetric_key):
        with self.Session() as session:
            owner_alias = aliased(User)
            client_alias = aliased(User)
            data_contact = session.query(Contacts).\
                join(owner_alias, Contacts.owner_id == owner_alias.id).\
                join(client_alias, Contacts.client_id == client_alias.id).\
                filter(owner_alias.login == login_owner, client_alias.login == login_client).first()
            data_contact.symmetric_key = symmetric_key
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
            user = session.query(User).filter(User.login == user_login).first()
            if not user:
                return False
            password = self.hash_password(user.salt) + self.hash_password(user_password)
            if user.password == password:
                return True
            else:
                return False

    def check_online(self, user_login):
        with self.Session() as session:
            user = session.query(User).filter(User.login == user_login).first()
            if user and user.authorized:
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