import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class History(Base):
    __tablename__ = 'history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    to_user = Column(String)
    from_user = Column(String)
    message = Column(String)
    create_at = Column(DateTime, default=datetime.datetime.now())
    hash_message = Column(String)


class Contacts(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String, unique=True, nullable=False)