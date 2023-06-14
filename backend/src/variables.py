import os

ROOT_DIR = os.getcwd()

SQLALCHEMY_SERVER_DATABASE_URL = f'sqlite:///{ROOT_DIR}/'