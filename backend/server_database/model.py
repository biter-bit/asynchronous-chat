import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    token = Column(String)
    info = Column(String)
    role = Column(String, nullable=False)
    authorized = Column(Boolean, default=False)
    salt = Column(String, nullable=False)
    public_key = Column(String)


class History(Base):
    __tablename__ = 'history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    create_at = Column(DateTime, default=datetime.datetime.utcnow)
    login = Column(String)
    ip_address = Column(String)


class Contacts(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    client_id = Column(Integer, ForeignKey('users.id'))
    symmetric_key = Column(String)


class HistoryMessageUsers(Base):
    __tablename__ = 'history_message'

    id = Column(Integer, primary_key=True, autoincrement=True)
    to_user_id = Column(String, ForeignKey('users.id'))
    from_user_id = Column(String, ForeignKey('users.id'))
    message = Column(String)
    create_at = Column(DateTime, default=datetime.datetime.now())
    hash_message = Column(String)
    nonce = Column(String)
