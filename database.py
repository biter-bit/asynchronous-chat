from sqlalchemy.orm import sessionmaker
import sqlalchemy
from model import Base

SQLALCHEMY_DATABASE_URL = 'sqlite:///example.db'
engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URL)
Session = sessionmaker(bind=engine)


def create_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return 'Ok'


if __name__ == '__main__':
    create_database()