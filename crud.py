from faker import Faker
from database import Session
from model import User, History, Contacts


def create_data():
    fake = Faker()
    session = Session()
    for i in range(10):
        session.add(User(login=fake.user_name() + str(i), info='today', password=fake.password()))
        session.add(History(ip_address=fake.ipv4()))
        session.add(Contacts(owner_id=fake.random_int(min=0, max=10), client_id=fake.random_int(min=0, max=10)))
    session.commit()
    return 'Ok'


if __name__ == '__main__':
    create_data()