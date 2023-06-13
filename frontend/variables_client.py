import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))

SQLALCHEMY_SERVER_DATABASE_URL = f'sqlite:///{ROOT_DIR}/'

SYMMETRIC_KEY = ''
