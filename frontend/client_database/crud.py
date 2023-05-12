import random

from faker import Faker
from client_database.model import History, Contacts, Base
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_
from variables import SQLALCHEMY_SERVER_DATABASE_URL


class ClientStorage:
    def __init__(self, user_login):
        # добавляем логин пользователя
        self.user_login = user_login

        # создаем движок и сессию для работы с базой данных
        url_database = SQLALCHEMY_SERVER_DATABASE_URL + f'user_{self.user_login}.db'
        self.engine = sqlalchemy.create_engine(url_database)
        self.Session = sessionmaker(bind=self.engine)


        # создаем обьект, который позволяет генерировать случайные данные
        self.fake = Faker()

        # создаем базу данных со всеми таблицами
        Base.metadata.create_all(self.engine)

        # очищаем контакты, так как при запуске они загружаются с сервера
        with self.Session() as session:
            session.query(Contacts).delete()
            session.commit()

    def get_contacts(self):
        with self.Session() as session:
            client_id_contact = session.query(Contacts.login).all()
            result = [i[0] for i in client_id_contact]
            session.commit()
        return result

    def add_contacts(self, list_contacts):
        with self.Session() as session:
            data_contact = session.query(Contacts).all()
            for i in list_contacts:
                if i not in data_contact:
                    result = Contacts(login=i)
                    session.add(result)
            session.commit()
        return 'Ok'

    def add_contact(self, contact):
        with self.Session() as session:
            data_contact = session.query(Contacts.login).all()
            if (contact,) not in data_contact:
                result = Contacts(login=contact)
                session.add(result)
            session.commit()
        return 'Ok'

    def del_contact(self, contact):
        with self.Session() as session:
            data_contact = session.query(Contacts.login).all()
            if (contact,) in data_contact:
                result = session.query(Contacts).filter(Contacts.login == contact).first()
                session.delete(result)
            session.commit()
        return 'Ok'

    def add_message(self, from_user, to_user, message):
        with self.Session() as session:
            result = History(to_user=to_user, from_user=from_user, message=message)
            session.add(result)
            session.commit()
        return 'Ok'

    def add_messages(self, list_messages):
        with self.Session() as session:
            list_messages_history = session.query(History.hash_message).all()
            list_message_history_finish = [i[0] for i in list_messages_history]
            for i in list_messages:
                if i['hash_message'] not in list_message_history_finish:
                    result = History(to_user=i['to_user'], from_user=i['from_user'],
                                     message=i['message'], hash_message=i['hash_message'])
                    session.add(result)
            session.commit()
        return 'Ok'

    def get_messages(self, from_user):
        with self.Session() as session:
            message = session.query(History.from_user, History.to_user, History.create_at, History.message).\
                filter(or_(History.from_user == from_user, History.to_user == from_user)).order_by(History.create_at).all()
            list_result = []
            if message:
                for i in message:
                    result_dict = {
                        'message': i[3],
                        'from_user': i[0],
                        'to_user': i[1],
                        'date': i[2].strftime('%d-%m-%Y %H-%M-%S')
                    }
                    list_result.append(result_dict)
            session.commit()
        return list_result


if __name__ == '__main__':
    database = ClientStorage('test_login')