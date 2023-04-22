from faker import Faker
from client_database.model import History, Contacts, Base
import sqlalchemy
from sqlalchemy.orm import sessionmaker


class ClientStorage:
    def __init__(self, user_login):
        # добавляем логин пользователя
        self.user_login = user_login

        # создаем движок и сессию для работы с базой данных
        url_database = f'sqlite:///user_{self.user_login}.db'
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
            client_id_contact = session.query(Contacts).all()
            session.commit()
        return client_id_contact

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


if __name__ == '__main__':
    database = ClientStorage('test_login')